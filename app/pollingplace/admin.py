from django.contrib import admin
from .models import Categories, PollOptions, PollResponses, Polls, Users

admin.site.register(Categories)
admin.site.register(PollOptions)
admin.site.register(PollResponses)
admin.site.register(Polls)
admin.site.register(Users)
