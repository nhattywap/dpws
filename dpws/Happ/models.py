from django.db import models
from django.utils import timezone
import datetime
# Create your models here.
class Profession(models.Model):
	profession = models.CharField(max_length=100)
	description = models.TextField(null=True, blank=True)

	def __str__(self):
		return self.profession

class Doctor(models.Model):
	username = models.CharField(max_length=100)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	age = models.PositiveIntegerField()
	email = models.EmailField()
	profession = models.ForeignKey(Profession, on_delete=models.CASCADE)
	phone = models.PositiveIntegerField()
	date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.username

	class Meta:
		ordering = ["username"]

class Patient(models.Model):
	username = models.CharField(max_length=100)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	age = models.PositiveIntegerField()
	email = models.EmailField()
	phone = models.PositiveIntegerField()
	address = models.CharField(max_length=100)
	gender = models.CharField(max_length=10, null=True, blank=True)
	blood_type = models.CharField(max_length=4, null=True, blank=True)
	marial_status = models.CharField(max_length=100, null=True, blank=True)
	description = models.TextField()
	date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.username

	class Meta:
		ordering = ["username"]

class ProfilePicture(models.Model):
	username = models.CharField(max_length=100)
	photo = models.ImageField(upload_to='Happ/static/Happ/file')

	def __str__(self):
		return self.username

class Appointment(models.Model):
	subject = models.CharField(max_length=200)
	doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
	patient = models.CharField(max_length=100)
	date = models.DateField(default=datetime.datetime.now)
	time = models.TimeField()
	pin = models.CharField(max_length=6, default='_none_')
	confirm = models.CharField(max_length=10, default='none')
	def __str__(self):
		return self.subject

	class Meta:
		ordering = ["time"]

class Emergency(models.Model):
	status = models.TextField()
	patient = models.CharField(max_length=100)
	date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.patient

	class Meta:
		ordering = ["date"]

class Question(models.Model):
	question = models.CharField(max_length=400)
	date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.question

class SurveyVote(models.Model):
	surv_title = models.CharField(max_length=200)
	author = models.CharField(max_length=100)

	def __str__(self):
		return self.surv_title

class SurveyWithVote(models.Model):
	surv_title = models.ForeignKey(SurveyVote, on_delete=models.CASCADE)
	vote = models.PositiveIntegerField(default=0, blank=True)
	voters = models.ManyToManyField(Doctor)

	def __str__(self):
		return self.surv_title.surv_title+':  votes: '+str(self.vote)

class HighSurTitle(models.Model):
	title = models.ForeignKey(SurveyVote, on_delete=models.CASCADE)
	vote = models.PositiveIntegerField(default=0)

	def __str__(self):
		return self.title.surv_title

class Survey(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE, default=None)
	author = models.CharField(max_length=200, default=None)
	answer = models.CharField(max_length=200, default=None, blank=True, null=True)

	def __str__(self):
		return self.question.question

class KnowladgeBase(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField()
	date = models.DateTimeField(default=timezone.now)
	
	def __str__(self):
		return self.title

	class Meta:
		ordering = ["title"]

class Chat(models.Model):
	doctor = models.CharField(max_length=200, blank=True)
	message = models.CharField(max_length=400, blank=True)
	date = models.DateTimeField(default=timezone.now)
	
	def __str__(self):
		return self.doctor

class DiscussionVote(models.Model):
	dis_title = models.CharField(max_length=200)
	author = models.CharField(max_length=100, default='username')

	def __str__(self):
		return self.dis_title

class DiscussionWithVote(models.Model):
	dis_title = models.ForeignKey(DiscussionVote, on_delete=models.CASCADE)
	vote = models.PositiveIntegerField(default=0, blank=True)
	voters = models.ManyToManyField(Doctor)

	def __str__(self):
		return self.dis_title.dis_title+':  votes: '+str(self.vote)

class Discussion(models.Model):
	subject = models.CharField(max_length=200)
	chat = models.ManyToManyField(Chat, blank=True, default=None)

	def __str__(self):
		return self.subject

class HighDisTitle(models.Model):
	title = models.ForeignKey(DiscussionVote, on_delete=models.CASCADE)
	vote = models.PositiveIntegerField(default=0)

	def __str__(self):
		return self.title.dis_title

class News(models.Model):
	title = models.CharField(max_length=200)
	content = models.TextField()
	date = models.DateTimeField(default=timezone.now)
	doctor = models.CharField(max_length=200, default=None)
	
	def __str__(self):
		return self.title

	class Meta:
		ordering = ["date"]

class NewsComment(models.Model):
	news = models.ForeignKey(News, on_delete=models.CASCADE)
	author = models.CharField(max_length=100)
	comment = models.TextField()

class Authors(models.Model):
	doctor = models.CharField(max_length=200)
	patient = models.CharField(max_length=200)

	def __str__(self):
		return self.doctor+" "+"and"+" "+self.patient

class Consulte(models.Model):
	authors = models.ForeignKey(Authors, on_delete=models.CASCADE)
	someone = models.CharField(max_length=200, blank=True)
	message = models.CharField(max_length=400)
	date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.message

class Language(models.Model):
	username = models.CharField(max_length=100)
	language = models.CharField(max_length=100)

	def __str__(self):
		return self.username
