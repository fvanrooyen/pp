-- Polls view
CREATE OR REPLACE VIEW polls_view AS
SELECT polls.pid, 
       polls.topic, 
       categories.name, 
       Count(poll_responses.id) AS num_votes, 
       Concat(Floor (Hour(Timediff(Cast(polls.end_date AS datetime), Now())) / 
                     24), 
       ' days ', MOD(Hour(Timediff(Cast(polls.end_date AS datetime), Now())), 24 
                 ), 
       ' hours ', Minute(Timediff(Cast(polls.end_date AS datetime), Now())), 
       ' minutes' 
       )                        AS time_remaining 
FROM   polls, 
       categories, 
       poll_responses 
WHERE  polls.cid_id = categories.cid 
       AND polls.pid = poll_responses.pid_id 
       AND polls.active 
       AND ( Cast(polls. end_date AS datetime) ) - Now() > 0 
GROUP  BY polls.pid 
ORDER  BY polls.pid DESC