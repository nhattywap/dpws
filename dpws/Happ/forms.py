from django import forms
from .models import Question

class UserSignupFrom(forms.Form):
	MARIAL_STAUS = [('Merried','Merried'),('Devorsed', 'Devorsed'), ('Widow', 'Widow'), ('Single','Single')]
	GENDER_CHOICE = [('M', 'Male'), ('F', 'Fimale')]

	first_name = forms.CharField(label='first name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'first name'}))
	last_name = forms.CharField(label='last name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'last name'}))
	age = forms.IntegerField(label='age', widget=forms.NumberInput(attrs={'placeholder': 'your age'}))
	email = forms.EmailField(label='email', max_length=100, widget=forms.EmailInput(attrs={'placeholder': 'you email'}))
	phone = forms.IntegerField(label='phone', widget=forms.NumberInput(attrs={'placeholder': 'phone number'}))
	address = forms.CharField(label='address', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'your address'}))
	username = forms.CharField(label='username', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'username'}))
	gender = forms.CharField(label='gender', max_length=10, widget=forms.Select(choices=GENDER_CHOICE))
	blood_type = forms.CharField(label='blood type', max_length=3, widget=forms.TextInput(attrs={'placeholder': 'blood type'}))
	marial_status = forms.CharField(label='marial status', max_length=100, widget=forms.Select(choices=MARIAL_STAUS))
	password = forms.CharField(label='password', max_length=9, widget=forms.PasswordInput(attrs={'placeholder': 'password'}))
	confirm = forms.CharField(label='confirm', max_length=9, widget=forms.PasswordInput(attrs={'placeholder': 'confirm password'}))
	description = forms.CharField(label='status', max_length=400, widget=forms.Textarea(attrs={'placeholder': 'put your health status here'}))

class ChangePassWordForm(forms.Form):
	password = forms.CharField(label='password', max_length=9, widget=forms.PasswordInput(attrs={'placeholder': 'password'}))
	confirm = forms.CharField(label='confirm', max_length=9, widget=forms.PasswordInput(attrs={'placeholder': 'confirm'}))

class SurveryForm(forms.Form):
	question = forms.ModelChoiceField(queryset=Question.objects.all(), empty_label='Choose Question Here')
	answer = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'your answer'}))

