from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([Doctor, Discussion, KnowladgeBase, Question, DiscussionWithVote, HighDisTitle,Profession])
admin.site.site_header = "Happ"
