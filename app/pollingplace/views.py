from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from datetime import date, datetime, timedelta
from rest_framework.response import Response
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.core.cache import cache
from rest_framework import status
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
import redis
from django.views.decorators.cache import cache_page
from mongoengine import *
from helper.base_db import ConnectionPool


from .models import Polls, PollOptions, Users, PollResponses, Categories, Music, PollViewModel

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

#RAW SQL
def polls_grid(request):
    """
    Returns all active and non-expired polls for the main dashboard card grid
    """
    db_conn = None
    result = []

    try:
        db_conn = ConnectionPool.get_conn()
        mycursor = db_conn.cursor()

        sql = "SELECT polls.pid, polls.topic, categories.name, count(poll_responses.oid) as num_votes, "\
                "CONCAT(FLOOR(HOUR(timediff(ADDTIME(cast(polls.end_date as datetime), STR_TO_DATE( polls.end_time, '%l:%i %p' )),now()))/24), ' days ', "\
                "MOD(HOUR(timediff(ADDTIME(cast(polls.end_date as datetime), STR_TO_DATE( polls.end_time, '%l:%i %p' )),now())), 24), ' hours ' , "\
                "MINUTE(timediff(ADDTIME(cast(polls.end_date as datetime), STR_TO_DATE( polls.end_time, '%l:%i %p' )),now())), ' minutes') as time_remaining "\
                "FROM polls "\
                "INNER JOIN categories "\
                "ON polls.cid = categories.cid "\
                "LEFT JOIN poll_responses "\
                "ON polls.pid = poll_responses.pid "\
                "WHERE polls.active AND (ADDTIME(cast(polls.end_date as datetime), STR_TO_DATE( polls.end_time, '%l:%i %p' )) - now()) > 0 "\
                "GROUP BY polls.pid "\
                "ORDER BY polls.pid DESC "\
                "LIMIT 10"
        
        mycursor.execute(sql)
        myresult = mycursor.fetchall()

        for x in myresult:
            row_data = {}
            row_data["pid"] = x[0]
            row_data["topic"] = x[1]
            row_data["category_name"] = x[2]
            row_data["num_votes"] = x[3]
            row_data["time_remaining"] = x[4]
            result.append(row_data)
        return render(request, 'polls/polls.html',{'results' : result})

    except Exception as ex:
        logging.error(str(ex))

    finally:
        if mycursor:
            mycursor.close()
        if db_conn:
            db_conn.close()


#ORM
@cache_page(CACHE_TTL, cache='default', key_prefix='')
def index(request):
    result = []
    today = date.today()
    polls = Polls.objects.filter(active__exact=1, flag__lt=46, end_date__gte=today).order_by('-pid')[:10]
    categories = dict ((c.pk, c.name) for c in Categories.objects.all())
    votes = dict ((int(v['pid']), v['total_votes']) for v in PollResponses.objects.all().values('pid').annotate(total_votes=Count('oid')))

    for p in polls:
        row_data = {}
        row_data["pid"] = p.pid
        row_data["topic"] = p.topic
        if int(p.cid.cid) in categories:
            row_data["category_name"] = categories[int(p.cid.cid)]
        else:
            row_data["category_name"] = "misc"
        if p.pid in votes:
            row_data["num_votes"] = votes[p.pid]
        else:
            row_data["num_votes"] = 0
        if p.end_date == today:
            row_data["time_remaining"] = "Poll ends today!"
        else:
            row_data["time_remaining"] = "Polls end in " + str((p.end_date - today).days) + " days!"
        result.append(row_data)
    
    return render(request, 'polls/polls.html', {'results' : result})


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request, format=None):
 
        data = {}
        today = date.today()
        polls = dict((p['pid'],0) for p in Polls.objects.filter(active__exact=1, flag__lt=46, end_date__gte=today).values('pid'))
        votes = dict((int(v['oid']),v['responses']) for v in PollResponses.objects.all().values('oid').annotate(responses=Count('uid')))
        all_options = dict((int(o['oid']),[o['optiontext'],o['pid_id']]) for o in PollOptions.objects.all().values())

        
        for oid, values in all_options.items():
            pid = int(values[1])
            label = values[0]
            if pid in polls:
                if pid in data:
                    data[pid]["labels"].append(label)
                    if oid in votes:
                        data[pid]["results"].append(votes[oid])
                    else:
                        data[pid]["results"].append(0)
                else:
                    if oid in votes:
                        data[pid] = {"labels":[label], "results": [votes[oid]]}
                    else:
                        data[pid] = {"labels":[label], "results": [0]}

        
        return Response(data)


class PollUpdate(UpdateView):
    #Change halppend and we would like to clear the chache
    model = Polls
    fields = ['creation_date','end_date','topic', 'url','active','public','state','zipcode']
    template_name = 'polls/pollmod.html'
    cache.clear()
    success_url = reverse_lazy('mypolls')

class PollDelete(DeleteView):
    #Change halppend and we would like to clear the chache
    model = Polls
    template_name = 'polls/polldel.html'
    cache.clear()
    success_url = reverse_lazy('mypolls')



def create(request):

    if request.method == 'POST':
        topic = request.POST['topic']
        enddate = request.POST['enddate']

        active = public = False
        if 'active' in request.POST:
            active = request.POST['active']
            
        if 'public' in request.POST:    
            public = request.POST['public']

        state = request.POST['state']
        zipcode = request.POST['zip']
        
        userid = 1
        if 'userid' in request.session:
            userid = request.session['userid']

        o1 = request.POST['o1']
        o2 = request.POST['o2']
        o3 = request.POST['o3']

        user_id = Users.objects.get(uid=userid)
        cid = Categories.objects.get(cid=1)

        today = date.today()
        objDate = datetime.strptime(enddate, '%m/%d/%Y %I:%M %p')
        endd = datetime.strftime(objDate, '%Y-%m-%d')
        
        poll = Polls.objects.create(creation_date=today,end_date=endd,topic=topic,active=1,public=1,flag=0,state=state,zipcode=zipcode,cid=cid,uid=user_id)
        pollo1 = PollOptions.objects.create(optiontext=o1,pid=poll)
        pollo2 = PollOptions.objects.create(optiontext=o2,pid=poll)
        pollo3 = PollOptions.objects.create(optiontext=o3,pid=poll)

        #Change halppend and we would like to clear the chache
        cache.clear()

        return redirect('mypolls')  
    
    else:
        return render(request, 'polls/create.html')

#ORM VOTE IMPLEMENTATION
def vote(request, poll_id):

    polltext = Polls.objects.get(pid=poll_id)
    
    if request.method == 'POST':
        choice = request.POST["choice"]
        userid = request.session['userid']

        option_id = PollOptions.objects.get(oid=choice)
        user_id = Users.objects.get(uid=userid)
        pollid = Polls.objects.get(pid=poll_id)

        PollResponses.objects.create(oid=option_id,pid=pollid,uid=user_id)

        #Change halppend and we would like to clear the chache
        cache.clear()

        return redirect('mypolls')  

    else:
        vote = PollOptions.objects.filter(pid=poll_id)
        return render(request, 'polls/vote.html', {'poll': vote, 'polltxt': polltext})

#RAW SQL VOTE IMPLEMENTATION
def polls_vote(request, poll_id):
    if request.method == 'POST':
            pid = request.POST.get('pid')
            poll_topic = request.POST.get('poll_topic')
            poll_url = request.POST.get('poll_url')
            field_name = request.POST.getlist('field_name[]')
            selected_choice = request.POST['choice']
            uid = 200

            db_conn = None
            result = []
         
            try:
                db_conn = ConnectionPool.get_conn()
                mycursor = db_conn.cursor()
         
                date = datetime.date.today()

                sql = 'INSERT INTO poll_responses (uid,pid,oid) '\
                'VALUES (%s, %s, %s)'
                args = (uid,pid, selected_choice)
                mycursor.execute(sql, args)  
                db_conn.commit()
                messages.success(request, "Thank  you for Voting", 
                                 extra_tags='alert alert-success alert-dismissible fade show')

#                 return render(request, 'polls/polls_list.html', context)
            except Exception as ex:
                logging.error(str(ex))
                messages.error(request, "Faild to update Poll or Poll Options " + str(ex),  extra_tags='alert alert-warning alert-dismissible fade show')

            finally:
                if mycursor:
                    mycursor.close()
                if db_conn:
                    db_conn.close()

            return redirect('polls:list')

    else:
        try: 
            sql = "SELECT polls.topic, polls.URL FROM polls WHERE pid = {}".format(poll_id)
    
            db_conn = ConnectionPool.get_conn()
            mycursor = db_conn.cursor()
    
            mycursor.execute(sql)
            poll = mycursor.fetchone()
    
            poll_data = {}
            poll_data["pid"] = poll_id
            poll_data["topic"] = poll[0]
            poll_data["url"] = poll[1]
    
            sql_option = "SELECT poll_options.oid, poll_options.optiontext FROM poll_options WHERE poll_options.pid = {}".format(poll_id)
                    
            mycursor.execute(sql_option)
            poll_options = mycursor.fetchall()
    
            poll_options_data = []
            
            index = 1
            for x in poll_options:
                row_data = {}
                row_data["index"] = index
                row_data["oid"] = x[0]
                row_data["polloption"] = x[1]
                poll_options_data.append(row_data)
                index +=1
                
        except Exception as ex:
            logging.error(str(ex))
            messages.error(request, "Faild to list Poll or Poll Options " + str(ex),  extra_tags='alert alert-warning alert-dismissible fade show')

        finally:
            if mycursor:
                mycursor.close()
            if db_conn:
                db_conn.close()

        return render(request, 'polls/poll_vote.html',{'poll' : poll_data, 'poll_options' : poll_options_data})



def login(request):
    if request.method == 'POST':
        uname = request.POST['username']
        passw =  request.POST['password']
        post = Users.objects.filter(username=uname, password=passw).count()
        if post > 0:
            userid = Users.objects.values_list('uid', flat=True).get(username=uname)
            request.session['userid'] = userid
            return redirect('index')
        else:
            return render(request, 'polls/login.html', {})
    return render(request, 'polls/login.html', {})

def mypolls(request):
    userid = request.session['userid']
    mypolls = Polls.objects.filter(uid=userid).order_by('-pid')
    return render(request, 'polls/mypolls.html', {'mypolls' : mypolls})

@cache_page(CACHE_TTL, cache='default', key_prefix='')
def viewpolls(request):
    polls = PollViewModel.objects.all().order_by('-num_votes')
    return render(request, 'polls/viewpolls.html', {'polls' : polls})


def autopoll(request):

    if request.method == 'POST': 
        bandtext = request.POST['band']
        alist = []
        bands = Music.objects(Artist__contains = bandtext)[:3].order_by('Rating')
        for artist in bands:
            alist.append(artist.Album) 
        
        topic = ("What is the best %s album?" % bandtext)
        today = date.today()
        enddate = today + timedelta(days=7)
       
        userid = request.session['userid']
        user_id = Users.objects.get(uid=userid)
        cid = Categories.objects.get(cid=1)
    
        poll = Polls.objects.create(creation_date=today,end_date=enddate,topic=topic,active=1,public=1,flag=0,cid=cid,uid=user_id)

        for artist in bands:
            PollOptions.objects.create(optiontext=artist.Album,pid=poll)

        #Change halppend and we would like to clear the chache
        cache.clear()
        return redirect('vote', poll.pid)  
          

    # return render(request, 'polls/autopoll.html', {'artist':  alist})
    return render(request, 'polls/autopoll.html')
    


