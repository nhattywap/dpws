from django.shortcuts import render
from .forms import *
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse, Http404, HttpRequest
from django.urls import reverse
from django.contrib.auth.models import User
from .models import *
from .make_forms import *
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm, TextInput, DateTimeInput, HiddenInput, Textarea, DateInput, TimeInput, Select
from django.core.mail import send_mail
from django.db.models import Q
import re
import time
import datetime
# Create your views here.
doctor_list = []
patient_list = []

time_holder = 0
count_request = 1
count_dict = {}

a_group = ['A', 'A+', 'A-']
b_group = ['B', 'B+', 'B-']
ab_group = ['AB', 'AB+', 'AB-']
o_group = ['O', 'O+', 'O-']

def get_template(classname):

	return TemplateManager(classname)()

def inc_time():
	global time_holder
	time_holder += 1
	return time_holder

def get_request_(class_):

	_, name_set = TemplateManager(class_).get_name()
	name = name_set[0]
	if name:
		if len(count_dict) <= 0:
			count_dict.update({name: count_request})
		else:
			if name in count_dict:
				num = count_dict[name]
				count_dict.update({name: num+1})
			else:
				count_dict.update({name: count_request})

		return name, count_dict
	else:
		return

def backup_data(d_base_name, to_path):
	import os
	import platform
	for r, d, f, in os.walk(os.getcwd()):
		if d_base_name in f:
			act = None
			if platform.system() == 'Windows':
				act = 'copy'
			if platform.system() == 'Linux':
				act = 'cp'
			os.system('%s %s\\%s %s' %(act, os.getcwd(), d_base_name, to_path))
			print('Performed: [action: copy] %s %s\\%s %s' %(act, os.getcwd(), d_base_name, to_path))
	del os, platform

def is_string(_str):

	if _str.isalpha():

		return True
	else:
		return False

def is_valid_blood(_str):
	bg = _str.upper()
	if bg in a_group or bg in b_group:
		return True
	elif bg in ab_group or bg in o_group:
		return True
	else:
		return False

def is_valid_phone(_str):
	print(len(str(_str)))
	print(str(_str))
	_str = str(_str)
	if _str.startswith('9') and len(_str) == 9:
		return True
	elif _str.startswith('251') and len(_str) == 12:
		return True
	else:
		return False

def make_form(class_name, attrs):
	
	try:
		fo = Global_Dict_Obj[class_name]
		return fo
	except Exception as e:
		mf = Fill_Form_Field(class_name, attrs)
		exec_obj_as_global(mf.fill())
		fo = Global_Dict_Obj[class_name]
		return fo

class ViewClass(View):

	def _view_class_(self, request):
		url_name = request.resolver_match.url_name
		_, cls_set = TemplateManager.parse_list(url_name)
		view_class = cls_set[-1]()
		
		return view_class

	def get(self, request, *args, **kwargs):
		view_class = self._view_class_(request)
		print('[-X-][requested class view] %s' %(view_class.__class__.__name__))
		
		get = getattr(view_class, 'get')
		try:
			return get(request, *args, **kwargs)
		except Exception as e:
			return HttpResponse('<h1>-- NaN -- </h1>')

	def post(self, request, *args, **kwargs):
		view_class = self._view_class_(request)
		print('[-X-][requested class view] %s' %(view_class.__class__.__name__))

		post = getattr(view_class, 'post')
		try:
			return post(request, *args, **kwargs)
		except Exception as e:
			return HttpResponse('<h1>-- NaN -- </h1>')

class IndexView(View):

	def get(self, request, *args, **kwargs):
		#backup_data('db.sqlite3', 'E:\\Django')
		return render(request, get_template(self), {'login': 'Log In'})

class UserLogin(View):
	passd = Char_Field('password', max_length=9, widget='PasswordInput')
	form = make_form('UserLoginForm', ('username', passd))

	def get(self, request, *args, **kwargs):
		login_form = self.form()
		
		return render(request, get_template(self), {'login_form': login_form})

	def post(self, request, *args, **kwargs):
		login_form = self.form(request.POST)

		if login_form.is_valid():
			
			username = login_form.cleaned_data.get('username')
			password = login_form.cleaned_data.get('password')

			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				try:
					global time_holder

					doctor_username = Doctor.objects.filter(username=username)
					patient_username = Patient.objects.filter(username=username)
					if doctor_username.exists():

						doctor_list.append(username)
						print('[-X-]',datetime.datetime.now(),': Action[login]: user:', username)
						time_holder -= time_holder
						return HttpResponseRedirect(reverse('Happ:doctorIndex'))
					elif patient_username.exists():
						patient_list.append(username)
						print('[-X-]',datetime.datetime.now(),': Action[login]: user:', username)
						time_holder -= time_holder
						return HttpResponseRedirect(reverse('Happ:patientIndex'))
					else:
						return HttpResponseForbidden(HttpResponse('you are not authorized here'))
				except Exception as e:
					pass
			else:
				tryed = inc_time()

				if tryed >= 2:
					time.sleep(tryed)
				if tryed >= 5:
					#global time_holder
					time_holder -= tryed
					return HttpResponseForbidden(HttpResponse('<center><h1>Too many trial</h1> \
						<p>if you forget your password try reseting <a href="/Happ/forget/">here</a> \
						or contact the adminstrator </p></center>'))

				cls_name, di = get_request_(self)
				num = di[cls_name]
				if num >= 4:
					count_dict[cls_name] = 0
					return render(request, get_template(self), {'login_form': login_form, 'forget': 'forget password ?'})
				return render(request, get_template(self), {'login_form': login_form, 'wrong_user': 'Wrong username or password'})
		else:
			return render(request, get_template(self), {'login_form': login_form, 'invalid': 'Invalid input'})

class ForgetPassword(View):
	mf = Email_Field('email', placeholder='email')
	form = make_form('ForgetPasswordForm', (mf,))

	def get(self, request, *args, **kwargs):
		forget_form = self.form()
		return render(request, get_template(self), {'forget_form': forget_form})

	def post(self, request, *args, **kwargs):
		forget_form = self.form(request.POST)

		if forget_form.is_valid():
			email = forget_form.cleaned_data.get('email')

			try:
				patient_obj = Patient.objects.get(email=email)
				request.session['email'] = email
				return render(request, get_template(self), {'forget_form': forget_form, 'patient_obj': patient_obj})
			except Exception as e:
				try:
					doctor_obj = Doctor.objects.get(email=email)
					request.session['email'] = email
					return render(request, get_template(self), {'forget_form': forget_form, 'doctor_obj': doctor_obj})
				except Exception as e:
					return render(request, get_template(self), {'forget_form': forget_form, 'user_not_found': 'There is no user registered with this number'})

class SendCode(View):

	def get(self, request, *args, **kwargs):
		return HttpResponseRedirect(reverse('Happ:login'))
		
	def post(self, request, *args, **kwargs):
		yes_it_is_me = request.POST['yes_it_is_me']
		email = request.session['email']
		code = random_vari_num(5)
		try:
			pnt_obj = Patient.objects.get(email=email)
			send_mail('test mail', str(code), 'nhattywap123@gmail.com', [pnt_obj.email], fail_silently=False)
			del request.session['email']
			request.session['_code_'] = code
			request.session['_username_'] = pnt_obj.username
			return HttpResponseRedirect(reverse('Happ:authcode'))
		except Exception as e:
			try:
				doc_obj = Doctor.objects.get(email=email)
				send_mail('Happ mail', str(code), 'nhattywap123@gmail.com', [doc_obj.email], fail_silently=False)
				del request.session['email']
				request.session['_code_'] = code
				request.session['_username_'] = doc_obj.username
				return HttpResponseRedirect(reverse('Happ:authcode'))
			except Exception as e:
				return render(request, get_template(self), {'unknown_user': 'you are not authorized idividual'})

class AuthenCode(View):
	i_field = Integer_Field('code', placeholder='enter the code')
	form = make_form('ResetForm', (i_field,))

	def get(self, request, *args, **kwargs):
		reset_form = self.form()
		if not request.session.get('_code_'):
			return HttpResponseRedirect(reverse('Happ:login'))

		return render(request, get_template(self), {'reset_form': reset_form})

	def post(self, request, *args, **kwargs):
		reset_form = self.form(request.POST)

		if reset_form.is_valid():
			code = reset_form.cleaned_data.get('code')
			_code_ = request.session['_code_']

			if int(code) == int(_code_):
				del request.session['_code_']
				return HttpResponseRedirect(reverse('Happ:resetpass'))
			else:
				return render(request, get_template(self), {'reset_form': reset_form, 'invalid_code': 'the code you entered is invalid'})


class ResetPassword(View):
	form = ChangePassWordForm

	def get(self, request, *args, **kwargs):
		reset_pass_form = self.form()

		if not request.session.get('_username_'):
			return HttpResponseRedirect(reverse('Happ:login'))

		return render(request, get_template(self), {'reset_pass_form': reset_pass_form})

	def post(self, request, *args, **kwargs):
		reset_pass_form = self.form(request.POST)
		_username_ = request.session['_username_']
		user = User.objects.get(username=_username_)

		if reset_pass_form.is_valid():
			new_pass = reset_pass_form.cleaned_data.get('password')
			conf_new = reset_pass_form.cleaned_data.get('confirm')

			if new_pass == conf_new:
				if len(new_pass) >= 8:
					match_1 = re.findall((r"\D\w+\d+"), new_pass)
					match_2 = re.findall((r"\d+\w+\D"), new_pass)
					if match_1 or match_2:
						same_pass = user.check_password(new_pass)
						
						if same_pass:
							return render(request, get_template(self), {'reset_pass_form': reset_pass_form, 'old_pass': 'The new password is the same as the old'})

						user.set_password(new_pass)
						user.save()
						del request.session['_username_']
						return HttpResponseRedirect(reverse('Happ:login'))
					else:
						return render(request, get_template(self), {'reset_pass_form': reset_pass_form, 'must_be': 'password must contain aleast one character or number'})
				else:
					return render(request, get_template(self), {'reset_pass_form': reset_pass_form, 'too_short': 'The password is too short'})
			else:
				return render(request, get_template(self), {'reset_pass_form': reset_pass_form, 'p_no_match': 'password do not match'})
		else:
			return render(request, get_template(self), {'reset_pass_form': reset_pass_form, 'invalid': 'invalid input'})

class UserSignup(View):
	form = UserSignupFrom

	def get(self, request, *args, **kwargs):
		signup_form = self.form()
		return render(request, get_template(self), {'signup_form': signup_form})

	def post(self, request, *args, **kwargs):
		signup_form = self.form(request.POST)

		if signup_form.is_valid():
			first_name = signup_form.cleaned_data.get('first_name')
			last_name = signup_form.cleaned_data.get('last_name')
			
			if not is_string(first_name) or not is_string(last_name):
				return render(request, get_template(self), {'char_not_valied': 'number not allowed in first name or last name', 'signup_form': signup_form})

			age = signup_form.cleaned_data.get('age')
			if not age >= 18:
				return render(request, get_template(self), {'invalid_age': 'your age must be atleast 18 or greater', 'signup_form': signup_form})

			if age > 100:
				return render(request, get_template(self), {'not_valid_a':'please enter a valid age', 'signup_form': signup_form})
			email = signup_form.cleaned_data.get('email')
			phone = signup_form.cleaned_data.get('phone')

			if not is_valid_phone(phone):

				return render(request, get_template(self), {'not_valid_phone':'please enter a valid phone number', 'signup_form': signup_form})

			address = signup_form.cleaned_data.get('address')
			description = signup_form.cleaned_data.get('description')
			username = signup_form.cleaned_data.get('username')
			password = signup_form.cleaned_data.get('password')
			confirm = signup_form.cleaned_data.get('confirm')
			gender = signup_form.cleaned_data.get('gender')
			blood_type = signup_form.cleaned_data.get('blood_type')

			if not is_valid_blood(blood_type):
				return render(request, get_template(self), {'not_valid_bg': 'please enter a valid blood type', 'signup_form': signup_form})

			marial_status = signup_form.cleaned_data.get('marial_status')

			check_username = User.objects.filter(username=username)
			check_username_2 = Patient.objects.filter(username=username)

			if check_username.exists() or check_username_2.exists():
				return render(request, get_template(self), {'signup_form': signup_form, 'olready_taken': 'the username is olredy taken choose another one'})
			else:
				if len(password) < 8:
					return render(request, self.template_name, {'signup_form': signup_form, 'too_short': 'password is to short'})
				if password == confirm:
					match_1 = re.findall((r"\D\w+\d+"), password)
					match_2 = re.findall((r"\d+\w+\D"), password)
					if match_1 or match_2:
						user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, password=password)
						user.save()
						Patient.objects.create(
							username=username,
							first_name=first_name,
							last_name=last_name,
							age=age,
							email=email,
							phone=phone,
							address=address,
							gender=gender,
							blood_type=blood_type,
							marial_status=marial_status,
							description=description,
							)
						login(request, user)
						patient_list.append(username)
						return HttpResponseRedirect(reverse('Happ:patientIndex'))
					else:
						return render(request, get_template(self), {'signup_form': signup_form, 'patt_match': 'password must contain aleast one character or number'})
				else:
					return render(request, get_template(self), {'signup_form': signup_form, 'p_no_match': 'password do not match'})

		else:
			return render(request, get_template(self), {'signup_form': signup_form})

def getPatient(request):
	name = request.user.username
	try:
		user = Patient.objects.get(username=name)
		'''if user.exists():
			return user
		else:
			return'''
		return user
	except Exception as e:
		return False

def _get_pic(name):

	if isinstance(name, str):
		try:
			pic_data = ProfilePicture.objects.get(username=name)
			pic_ = pic_data.photo
			pic_split = str(pic_).split('/')
			pic_path = pic_split[-3:]
			joined_pic = '/'.join(pic_path)
			#img = pic_split[-1]
			#img_link = 'Happ/file/'+img
			pic = joined_pic
		except Exception as e:
			pic = 'Happ/file/avatar.png'

	else:
		pic = 'Happ/file/avatar.png'

	return pic

def _add_pic(di, request, key, /):

	if _add_pic.__defaults__ is not None:
		if request is not None:
			name = request.user.username
		else:
			name = None

		pic = _get_pic(name)

		di.update({key: pic})
		return di

def add_pic_dict(*args, func=_add_pic):
	dict_data = None
	str_data = 'pic'
	req_data = None

	for arg in args:
		if isinstance(arg, dict):
			dict_data = arg
		if isinstance(arg, str):
			str_data = arg
		if isinstance(arg, HttpRequest):
			req_data = arg

	if dict_data is None:
		dict_data = {}

	ordered_tuple_args = (dict_data, req_data, str_data,)

	func.__defaults__ = ordered_tuple_args
	return func()

class PatientIndexView(View):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getPatient(request)
		if get_user:

			name = get_user.username
			user_profile = Patient.objects.get(username=name)
			return render(request, get_template(self), add_pic_dict('p_pic', request, {'patient_name': name, 'p_profile': user_profile}))
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

class UnAuthorizedAccess(View):

	def get(self, request, *args, **kwargs):
		title = "Unauthorized"
		desc = "You are unauthorized to access this source please \
					contact the adminstrator"

		return render(request, 'Happ/unauth.html', {'title': title, 'desc': desc})

class PatientProfileForm(ModelForm):
	
	class Meta:
		MARIAL_STAUS = [('Merried','Merried'),('Devorsed', 'Devorsed'), ('Widow', 'Widow'), ('Single','Single')]
		GENDER_CHOICE = [('M', 'Male'), ('F', 'Fimale')]

		model = Patient
		exclude = ['date']

		widgets = {
			'gender': Select(choices=GENDER_CHOICE),
			'marial_status': Select(choices=MARIAL_STAUS),
		}

class PatientProfile(View):
	form = PatientProfileForm

	def initials(self, _req):
		name = _req.user.username
		user = Patient.objects.get(username=name)

		initial = {'username': user.username, 'first_name': user.first_name,
		'last_name': user.last_name, 'age': user.age, 'email': user.email,
		'phone': user.phone, 'address': user.address, 'gender': user.gender,
		'blood_type': user.blood_type, 'marial_status': user.marial_status, 'description': user.description}

		return user, self.form(initial=initial)

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getPatient(request)
		if get_user:
			user, p_profile_form = self.initials(request)
			return render(request, get_template(self), add_pic_dict({'p_profile_form': p_profile_form, 'user_profile': user}, request, 'p_pic'))
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

	def post(self, request, *args, **kwargs):
		p_profile_form = self.form(request.POST)
		name = request.user.username
		if p_profile_form.is_valid():

			change = 0
			username = p_profile_form.cleaned_data.get('username')
			first_name = p_profile_form.cleaned_data.get('first_name')
			last_name = p_profile_form.cleaned_data.get('last_name')

			if not is_string(first_name) or not is_string(last_name):
				user, p_profile_form = self.initials(request)
				return render(request, get_template(self), add_pic_dict({'ch_not_valid': 'number not allowed in name','p_profile_form': p_profile_form, 'user_profile': user}, request, 'p_pic'))

			age = p_profile_form.cleaned_data.get('age')

			if not age >= 18:
				user, p_profile_form = self.initials(request)
				return render(request, get_template(self), add_pic_dict({'invalid_age':'your age must be atleast 18 or greater','p_profile_form': p_profile_form, 'user_profile': user}, request, 'p_pic'))
			email = p_profile_form.cleaned_data.get('email')
			phone = p_profile_form.cleaned_data.get('phone')

			if not is_valid_phone(phone):
				user, p_profile_form = self.initials(request)
				return render(request, get_template(self), add_pic_dict({'not_valid_phone':'please enter a valid phone number', 'p_profile_form': p_profile_form, 'user_profile': user}, request, 'p_pic'))

			address = p_profile_form.cleaned_data.get('address')
			gender = p_profile_form.cleaned_data.get('gender')
			blood_type = p_profile_form.cleaned_data.get('blood_type')

			if not is_valid_blood(blood_type):
				user, p_profile_form = self.initials(request)
				return render(request, get_template(self), add_pic_dict({'not_valid_bg': 'please enter a valid blood type', 'p_profile_form': p_profile_form, 'user_profile': user}, request, 'p_pic'))

			marial_status = p_profile_form.cleaned_data.get('marial_status')
			description = p_profile_form.cleaned_data.get('description')

			patient = Patient.objects.get(username=name)
			user = User.objects.get(username=name)

			if username != patient.username:
				if patient.username in patient_list:
					patient_list.remove(patient.username)
					patient_list.append(username)

				patient.username = username
				user.username = username

				auths = Authors.objects.filter(patient=name)
				for a in auths:
					ac = a.consulte_set.filter(someone=name)
					for n in ac:
						n.someone=username
						n.save()
				for auth in auths:
					auth.patient = username
					auth.save()
				change += 1

			if first_name != patient.first_name:
				patient.first_name = first_name
				user.first_name = first_name
				change += 1

			if last_name != patient.last_name:
				patient.last_name = last_name
				user.last_name = last_name
				change += 1

			if age != patient.age:
				patient.age = age
				change += 1

			if email != patient.email:
				patient.email = email
				user.email = email
				change += 1

			if phone != patient.phone:
				patient.phone = phone
				change += 1

			if address != patient.address:
				patient.address = address
				change += 1

			if gender != patient.gender:
				patient.gender = gender
				change += 1

			if blood_type != patient.blood_type:
				patient.blood_type = blood_type
				change += 1

			if marial_status != patient.marial_status:
				patient.marial_status = marial_status
				change += 1

			if description != patient.description:
				patient.description = description
				change += 1
			
			#patient.date = datetime.datetime.now()
			if change <= 0:
				user, p_profile_form = self.initials(request)
				return render(request, get_template(self), add_pic_dict({'no_change': 'you have made no change','p_profile_form': p_profile_form, 'user_profile': user}, request, 'p_pic'))
			patient.save()
			user.save()
			return HttpResponseRedirect(reverse('Happ:patientIndex'))
		else:
			return render(request, get_template(self), add_pic_dict({'p_profile_form': p_profile_form, 'invalid': 'invalid input'}, request, 'p_pic'))

class OnlineDocUsers(View):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getPatient(request)
		if get_user:
			languages = ['English', 'Amaharic', 'Oromic']
			online_docs = doctor_list
			name = get_user.username
			pnt = Patient.objects.get(username=name)
			p_id = pnt.id
			all_docs = Doctor.objects.all()
			return render(request, get_template(self), {'p_id': p_id, 'all_docs': all_docs, 'online_docs': online_docs, 'lang': languages})
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

class PreAppointView(View):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		ava_professions = Profession.objects.all()
		req_time_stamp = ['Now', 'Anytime']

		return render(request, get_template(self), {'ava_professions': ava_professions, 'req_time_stamp': req_time_stamp})

	def post(self, request, *args, **kwargs):
		ava_professions = Profession.objects.all()
		req_time_stamp = ['Now', 'Anytime']

		_calender = None
		check_docs = {}
		ava_docs = []

		print(len(ava_docs))
		try:
			profession = request.POST['profession']
			time_stamp = request.POST['timestamp']
			if not profession.isdigit() or time_stamp not in req_time_stamp:
				return render(request, get_template(self), {'invalid_value': 'Values must be choosen please choose value', 'ava_professions': ava_professions, 'req_time_stamp': req_time_stamp})
		except Exception as e:
			return render(request, get_template(self), {'invalid_value': 'Values must be choosen please choose value', 'ava_professions': ava_professions, 'req_time_stamp': req_time_stamp})
		docs_with_this_pro = Doctor.objects.filter(profession=profession)

		def doc_lookup(name, value):
			if name in check_docs:
				list_val = check_docs[name]
				list_val.append(value)
				check_docs.update({name:list_val})
			else:
				check_docs[name] = [value]

		def get_strftime(time):
			_time_ = time.strftime('%I:%M %p')
			f_time, f_lol = _time_.split(' ')
			hour, minute = f_time.split(':')

			return hour, minute, f_lol

		if time_stamp in req_time_stamp:
			if time_stamp == 'Now':
				_calender = datetime.datetime.now()
				formated_time = _calender.strftime(format="%I:%M %p")
				_hour, _minute, _lol = get_strftime(_calender)
				
				for docs_appoint in docs_with_this_pro:
					for appoint in docs_appoint.appointment_set.all():
						date = appoint.date
						time = appoint.time
						if _calender.year == date.year and _calender.month == date.month:

							if _calender.day == date.day:
								apt_hour, apt_minute, apt_lol = get_strftime(time)

								if int(apt_hour) == int(_hour) and apt_lol == _lol:
									if int(apt_minute) != int(_minute):
										if int(_minute) > int(apt_minute) and int(_minute)-30 < int(apt_minute):
											doc_lookup(appoint.doctor, False)

										elif int(_minute) < int(apt_minute) and int(_minute)+30 > int(apt_minute):
											doc_lookup(appoint.doctor, False)
										else:
											pass
									else:
										doc_lookup(appoint.doctor, False)
								elif int(apt_hour) != int(_hour) and apt_lol == _lol:
									pass
							elif _calender.day > date.day:
								pass
							else:
								pass
						else:
							pass

					if docs_appoint not in check_docs.keys():
						ava_docs.append(docs_appoint)
						
						check_docs = {}
					else:
						print('c',check_docs)
						continue
				no_res = ''

				if len(ava_docs) == 0:
					no_res = 'no result'
				
				print(ava_docs)
				return render(request, get_template(self), {'ava_docs': ava_docs, 'ava_professions': ava_professions, 'req_time_stamp': req_time_stamp, 'no_res': no_res})
			if time_stamp == 'Anytime':
				return render(request, get_template(self), {'docs_with_this_pro': docs_with_this_pro, 'ava_professions': ava_professions, 'req_time_stamp': req_time_stamp})


class widDateInput(DateInput):
	input_type = 'date'

class widTimeInput(TimeInput):
	input_type = 'time'
	input_formats = ('%I:%M %p', '%H:%M:%S.%f', '%H:%M')


class TextWidget(TextInput): 
	class Media:
		css = { 
		'all': ('pretty.css',) 
		} 
		js = ('animations.js', 'actions.js')

class MakeAppointmentForm(ModelForm):
	class Meta:
		model = Appointment
		exclude = ['confirm']
		labels = {
			'subject': ('subject'),
			'doctor': ('doctor name'),
			'patient': ('your name'),
			'date': ('Appointment date'),
			'time': ('Appointment time'),
		}
		widgets = {
			'subject': TextInput(attrs={'placeholder': 'subject'}),
			'patient': TextInput(),
			'date': widDateInput(),
			'time': widTimeInput(),
			'pin': TextWidget(),
		}

def twilio_send_sms(doc_obj, patient, date, time):
	from twilio.rest import Client

	phone = '%s%s' %('+', doc_obj.phone)
	mess = 'you have appointment with %s date: %s time: %s' %(patient, date, time)

	account = "ACa568af9537e79fb47881503217b73b44"
	token = "5cfccec4133372fa350b7327603b02fb"
	client = Client(account, token)

	message = client.messages.create(to=phone, from_="+14133279164",
                                 body=mess)
	print(message.json)
	del Client

def bulk_send_sms(doc_obj, patient, date, time):
	import requests
	phone = '%s%s' %('+', doc_obj.phone)
	message = 'you have appointment with %s date: %s time: %s' %(patient, date, time)

	resp = requests.post('https://textbelt.com/text', {
	'phone': phone,
	'message': message,
	'key': 'textbelt',
	})

	del requests

def random_vari_num(num_len):
		from random import randint
		num_list = []
		for i in range(num_len):
			num_list.append(str(randint(0,9)))

		joined_num = ''.join(num_list)

		del randint
		return joined_num

class MakeAppointment(View):
	
	form = MakeAppointmentForm

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getPatient(request)
		if get_user:
			sub_ject = ''
			doct = request.session['doc_for_appoint']
			sub_j = request.session.get('appoint_subject', None)

			if sub_j is not None:
				sub_ject = sub_j
				del request.session['appoint_subject']

			doctor = Doctor.objects.get(username=doct)
			random_pin = random_vari_num(5)
			name = get_user.username
			pin = random_pin
			initial = {'subject': sub_ject, 'patient': name, 'doctor': doctor, 'pin': pin, 'time': datetime.datetime.now()}
			appoint_form = self.form(initial=initial)
			#del request.session['doc_for_appoint']
			return render(request, get_template(self), {'appoint_form': appoint_form})
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

	def time_span(self, date, time, patient, doctor):
		p = True
		d = True
		time_for = time.strftime(format='%I:%M %p')
		_time_, locale = time_for.split(' ')
		_hour_, _minute_ = _time_.split(':')
		hour = int(_hour_)
		minute = int(_minute_)
		minute_span = minute + 30
		day = date.day
		month = date.month
		year = date.year

		def filter_ap(appoint):
			truth_lith = []

			for ava in appoint:
				if ava.date.year == year:
					if ava.date.month == month:
						if ava.date.day == day:
							_time_for = ava.time.strftime(format='%I:%M %p')
							__time_, _locale = _time_for.split(' ')
							__hour_, __minute_ = __time_.split(':')
							ava_hour = int(__hour_)
							ava_minute = int(__minute_)
							#print(locale, _locale)
							if ava_hour == hour and locale == _locale:
								
								if ava_minute == minute or ava_minute+30 > minute:
									truth_lith.append('false')

								elif ava_minute > minute and minute+30 > ava_minute:
									
									truth_lith.append('false')
								elif ava_minute < minute and ava_minute+30 > minute:
									
									truth_lith.append('false')
								else: pass
							elif ava_hour == hour and locale != _locale:
								
								pass
							elif ava_hour < hour and locale == _locale:
								
								_min = ava_minute
								add_min = _min+30
								if add_min >= 60:
									left_min = add_min - 60
									_hour = ava_hour+1
									if _hour == hour:
										if left_min > minute:
											truth_lith.append('false')
										else:
											pass
									if _hour < hour:
										pass
								else: pass
							elif ava_hour < hour and locale != _locale:
								
								if ava_hour == 11 and ava_minute > 30:
									truth_lith.append('false')
								else: pass
							else:
								if ava_hour > hour and locale == _locale:
									
									_add_min = minute+30
									if _add_min > 60:
										_left_min = _add_min - 60
										hour_ = hour + 1
										if hour_ == ava_hour:
											if _left_min > ava_minute:
												truth_lith.append('false')
											else: pass
										if hour_ < ava_hour:
											pass
									else: pass
								elif ava_hour > hour and locale != _locale:
									pass
						else: pass
					else:
						pass
				else: pass

			if len(truth_lith) > 0:
				if 'false' in truth_lith:
					truth_lith = []
					return False
				else:
					truth_lith = []
					return True
			else:
				truth_lith = []
				return True

		p_ava_appoint = Appointment.objects.filter(patient=patient)
		d_ava_appoint = Appointment.objects.filter(doctor=doctor)
		if p_ava_appoint.exists():
			p = filter_ap(p_ava_appoint)
		if d_ava_appoint.exists():
			d = filter_ap(d_ava_appoint)

		if p and d:
			return True
		else:
			return False

	def post(self, request, *args, **kwargs):
		appoint_form = self.form(request.POST)

		if appoint_form.is_valid():
			subject = appoint_form.cleaned_data.get('subject')
			doctor = appoint_form.cleaned_data.get('doctor')
			patient = appoint_form.cleaned_data.get('patient')
			date = appoint_form.cleaned_data.get('date')
			time = appoint_form.cleaned_data.get('time')
			pin = appoint_form.cleaned_data.get('pin')
			_str_time = time.strftime(format='%I:%M %p')
			_time, _locale = _str_time.split(' ')
			t_hour, t_min = _time.split(':')
			#try:
			ava_doc = Doctor.objects.filter(username=doctor)
			#patient_time = Appointment.objects.filter(Q(patient=patient) & Q(time__hour=time.hour) & Q(time__minute=time.minute) & Q(date__day=date.day) & Q(date__month=date.month))
			#ava_time = Appointment.objects.filter(Q(doctor=doctor) & Q(time__hour=time.hour) & Q(time__minute=time.minute) & Q(date__day=date.day) & Q(date__month=date.month))
			exist_patient = Patient.objects.filter(username=patient)

			time_year = datetime.datetime.now()
			time_str = time_year.strftime(format='%I:%M %p')
			ft_time, locale = time_str.split(' ')
			str_hour, str_min = ft_time.split(':')

			current_year = time_year.year
			current_day = time_year.day
			current_month = time_year.month
			current_hour = int(str_hour)
			current_min = int(str_min)
			
			print(time.strftime(format='%I:%M %p'), time_year.strftime(format='%I:%M %p'))
			if int(date.year) < int(current_year):
				return render(request, get_template(self), {'appoint_form': appoint_form, 'invalid_date': 'invalid year'})

			elif int(date.year) == int(current_year):
				if int(date.month) < int(current_month):
					return render(request, get_template(self), {'appoint_form': appoint_form, 'invalid_date': 'invalid month'})
				elif int(date.month) == int(current_month):
					if int(date.day) < int(current_day):
						return render(request, get_template(self), {'appoint_form': appoint_form, 'invalid_date': 'invalid day'})
					elif int(date.day) == int(current_day):
						if int(current_hour) == 12 and int(t_hour) < int(current_hour) and locale == _locale:
							pass
						elif int(t_hour) < int(current_hour) and locale == _locale:
							return render(request, get_template(self), {'appoint_form': appoint_form, 'invalid_date': 'invalid hour'})
						elif int(t_hour) == int(current_hour) and locale == _locale:

							if int(t_min) < int(current_min):
								return render(request, get_template(self), {'appoint_form': appoint_form, 'invalid_date': 'invalid minute'})
						else: pass
					else: pass
				else: pass
			else: pass

			_id = request.session.get('appoint_id', None)
			if _id is not None:
				exes_appoint = Appointment.objects.get(pk=_id)
				exes_appoint.subject = subject
				exes_appoint.doctor = doctor
				exes_appoint.patient = patient
				exes_appoint.date = date
				exes_appoint.time = time
				exes_appoint.pin = pin
				exes_appoint.confirm = 'none'
				exes_appoint.save()
				del request.session['appoint_id']
				try:
					twilio_send_sms(doctor, patient, date, time)
				except Exception as e:
					try:
						bulk_send_sms(doctor, patient, date, time)
					except Exception as e:
						pass
				
				return HttpResponseRedirect(reverse('Happ:Vappoint'))

			if ava_doc.exists() and exist_patient.exists():
				if not self.time_span(date, time, patient, doctor):
					return render(request, get_template(self), {'appoint_form': appoint_form, 't_taken': 'the time is taken'})
				else:
					Appointment.objects.create(
					subject=subject,
					doctor=doctor,
					patient=patient,
					date=date,
					time=time,
					pin=pin,
					)
					try:
						twilio_send_sms(doctor, patient, date, time)
					except Exception as e:
						try:
							bulk_send_sms(doctor, patient, date, time)
						except Exception as e:
							pass
					
					return HttpResponseRedirect(reverse('Happ:Vappoint'))
			else:
				return render(request, get_template(self), {'appoint_form': appoint_form, 'd_n_exist': 'the docter or patient username do not exist'})
			#except Exception as e:
				#pass
		else:
			return render(request, get_template(self), {'appoint_form': appoint_form, 'invalid': 'Invalid input'})

class TryAgainView(View):

	@method_decorator(login_required)
	def post(self, request, apont_id, *args, **kwargs):
		
		try:
			again = request.POST['again']
			appoint = Appointment.objects.get(pk=apont_id)
			doc = appoint.doctor
			request.session['doc_for_appoint'] = doc.username
			request.session['appoint_subject'] = appoint.subject
			request.session['appoint_id'] = apont_id

			return HttpResponseRedirect(reverse('Happ:Mappoint'))
		except Exception as e:
			raise e

class ViewAppointment(View):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getPatient(request)
		if get_user:
			all_appoint = Appointment.objects.filter(patient=get_user.username).order_by("date__year").order_by("date__month").order_by("date__day")
			if all_appoint.exists():

				return render(request, get_template(self), {'all_appoint': all_appoint.reverse()})
			else:
				return render(request, get_template(self), {'no_appoint': 'there is no appointment'})
		else:
			return HttpResponseRedirect(reverse('Happ:login'))


class EmergencyCallForm(ModelForm):
	class Meta:
		model = Emergency
		fields = ['status']
		labels = {
			'status': ('description'),
		}
		widgets = {
			'status': Textarea(attrs={'placeholder': 'Describe what happend or happening here'})
		}

class EmergencyCall(View):
	form = EmergencyCallForm

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getPatient(request)
		if get_user:
			emerg_form = self.form()
			
			return render(request, get_template(self), {'emerg_form': emerg_form})
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

	def post(self, request, *args, **kwargs):
		emerg_form = self.form(request.POST)

		if emerg_form.is_valid():
			status = emerg_form.cleaned_data.get('status')

			Emergency.objects.create(status=status, patient=request.user.username, date=timezone.now())
			return HttpResponseRedirect(reverse('Happ:patientIndex'))
		else:
			return render(request, get_template(self), {'emerg_form': emerg_form, 'invalid': 'Invalid input'})

class SearchDoctorView(View):
	form = make_form('SearchForm', ('search',))
	#form = SearchForm

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getPatient(request)
		if get_user:
			all_pros = Profession.objects.all()

			search_form = self.form()
			doctors_list = Doctor.objects.all()
			return render(request, get_template(self), {'search_form': search_form, 'doctors_list': doctors_list, 'all_pros': all_pros})
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

	def post(self, request, *args, **kwargs):
		search_form = self.form(request.POST)
		doctors_list = Doctor.objects.all()
		all_pros = Profession.objects.all()

		if search_form.is_valid():
			search_name = search_form.cleaned_data.get('search')
			try:
				search_type = request.POST.get('pro_type', None)

				if search_type is not None:
					if search_type == 'profession':
						try:
							_pro = Profession.objects.get(profession=search_name)
						except Exception as e:
							return render(request, get_template(self), {'search_form': search_form, 'doctors_list': doctors_list,
								'all_pros': all_pros, 'noresult': 'there is no doctor with the profession %s please try again' %(search_name)})
						
						_type_doctors = Doctor.objects.filter(profession=_pro)
						
						if _type_doctors:
							return render(request, get_template(self), {'search_form': search_form, 'd_name': _type_doctors, 'doctors_list': doctors_list, 'all_pros': all_pros})
						else:
							return render(request, get_template(self), {'search_form': search_form, 'doctors_list': doctors_list,
								'all_pros': all_pros, 'noresult': 'there is no doctor with the profession %s please try again' %(search_name)})
					if search_type == 'name':
						d_name = Doctor.objects.filter(username__contains=search_name).order_by("username")
						if d_name:
							return render(request, get_template(self), {'search_form': search_form, 'd_name': d_name, 'doctors_list': doctors_list, 'all_pros': all_pros})
						else:
							return render(request, get_template(self), {'search_form': search_form, 'doctors_list': doctors_list,
								'all_pros': all_pros, 'noresult': 'there is no doctor with the name %s please try again' %(search_name)})

				else:
					d_name = Doctor.objects.filter(username__contains=search_name).order_by("username")
					if d_name:
						return render(request, get_template(self), {'search_form': search_form, 'd_name': d_name, 'doctors_list': doctors_list, 'all_pros': all_pros})
					else:
						return render(request, get_template(self), {'search_form': search_form, 'doctors_list': doctors_list,
							'all_pros': all_pros, 'noresult': 'there is no doctor with the name %s please try again' %(search_name)})
			except Exception as e:
				pass
		else:
			return render(request, get_template(self), {'search_form': search_form, 'doctors_list': doctors_list})

class DoctorDetailView(View):

	@method_decorator(login_required)
	def get(self, request, doctor_id, *args, **kwargs):
		get_user = getPatient(request)
		if get_user:
			try:
				doctor_detail = Doctor.objects.get(pk=doctor_id)
				doc_pic = _get_pic(doctor_detail.username)

				request.session['doc_for_appoint'] = doctor_detail.username
				return render(request, get_template(self), {'doctor_detail': doctor_detail, 'doc_pic': doc_pic})
			except Exception as e:
				return HttpResponseRedirect(reverse('Happ:search'))
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

class InfoView(View):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getPatient(request)
		if get_user:
			info_list = KnowladgeBase.objects.all()
			return render(request, get_template(self), {'info_list': info_list})
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

class NewsView(View):
	
	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getPatient(request)
		get_user_d = getDoctor(request)

		if get_user or get_user_d:
			lateast_news = News.objects.all()
			return render(request, get_template(self), {'lateast_news': lateast_news})
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

class NewsDetailView(View):

	@method_decorator(login_required)
	def get(self, request, news_id, *args, **kwargs):
		get_user = getPatient(request)
		get_user_d = getDoctor(request)

		if get_user or get_user_d:
			request.session['_news_id'] = news_id

			try:
				news_detail = News.objects.get(pk=news_id)
				news_comment_form = NewsCommentsForm
				all_comments = news_detail.newscomment_set.all()
				curr_user = request.user.username

				return render(request, get_template(self), {'news_detail': news_detail, 'news_comment_form': news_comment_form, 'all_comments': all_comments, 'curr_user': curr_user})
			except Exception as e:
				return HttpResponseRedirect(reverse('Happ:news'))
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

class NewsCommentsForm(ModelForm):
	class Meta:
		model = NewsComment
		fields = ['comment']

class NewsComments(View):
	form = NewsCommentsForm

	@method_decorator(login_required)
	def get(self, request, news_id, *args, **kwargs):
		get_user = getPatient(request)
		get_user_d = getDoctor(request)

		if get_user or get_user_d:
			news_comment_form = self.form()
			news_det = News.objects.get(pk=news_id)
			all_comments = news_det.newscomment_set.all()

			return render(request, get_template(self), {'news_comment_form': news_comment_form, 'all_comments': all_comments})

	def post(self, request, news_id, *args, **kwargs):
		news_comment_form = self.form(request.POST)

		if news_comment_form.is_valid():
			comment = news_comment_form.cleaned_data.get('comment')

			_news_ = News.objects.get(pk=news_id)

			news_com = NewsComment.objects.create(news=_news_, author=request.user.username, comment=comment)
			return HttpResponseRedirect(reverse('Happ:newsdetail', args=(news_id,)))
			

class EditComment(View):
	form = NewsCommentsForm

	@method_decorator(login_required)
	def get(self, request, com_id, *args, **kwargs):
		_comment_val = NewsComment.objects.get(pk=com_id)
		if request.user.username != _comment_val.author:
			news_id = request.session['_news_id']
			return HttpResponseRedirect(reverse('Happ:newsdetail', args=(news_id,)))
		initial = {'comment': _comment_val.comment}
		comment_form = self.form(initial=initial)
		return render(request, get_template(self), {'comment_form': comment_form, 'com_id': com_id})

	def post(self, request, com_id, *args, **kwargs):
		comment_form = self.form(request.POST)

		if comment_form.is_valid():
			comment = comment_form.cleaned_data.get('comment')

			news_com = NewsComment.objects.get(pk=com_id)
			if request.user.username == news_com.author:
				news_com.comment = comment
				news_com.save()
				news_id = request.session['_news_id']
				return HttpResponseRedirect(reverse('Happ:newsdetail', args=(news_id,)))

class ChoosenLauguage(View):

	@method_decorator(login_required)
	def post(self, request, *arg, **kwargs):
		name = request.user.username
		lang = request.POST['lang']
		lan = Language.objects.filter(username=name)
		if lan.exists():
			for lango in lan:
				lango.language = lang
				lango.save()
		else:
			Language.objects.create(username=name, language=lang)

		return HttpResponseRedirect(reverse('Happ:online'))

#--------------------------------middle---------------------------------------------

class DPChatForm(ModelForm):
	class Meta:
		model = Consulte
		fields = ['message']
		labels = {
			'message': ('message'),
		}
		widgets = {
			'message': TextInput(attrs={'placeholder': 'your text'})
		}

class DPChatView(View):
	form = DPChatForm

	@method_decorator(login_required)
	def get(self, request, d_id, p_id ,*args, **kwargs):
		lang = 'none'
		username = request.user.username
		chat_form = self.form()
		try:
			doctor_obj = Doctor.objects.get(pk=d_id)
			patient_obj = Patient.objects.get(pk=p_id)
			
			if username == doctor_obj.username or username == patient_obj.username:
				doctor = doctor_obj.username
				patient = patient_obj.username
				language = Language.objects.filter(username=patient)
				if language.exists():
					for lan in language:
						lang = lan.language

				try:

					auth = Authors.objects.get(doctor=doctor, patient=patient)
					if auth:
						all_chats = auth.consulte_set.all()
						return render(request, get_template(self), {'chat_form': chat_form, 'all_chats': all_chats, 'd_id': d_id, 'p_id': p_id, 'ch_lang': lang})
				except Exception as e:
					return render(request, get_template(self), {'chat_form': chat_form, 'd_id': d_id, 'p_id': p_id, 'ch_lang': lang})
			else:
				return HttpResponseRedirect(reverse('Happ:unauth'))
		except Exception as e:
			return HttpResponseRedirect(reverse('Happ:unauth'))

	def post(self, request, d_id, p_id, *args, **kwargs):
		chat_form = self.form(request.POST)
		doctor_obj = Doctor.objects.get(pk=d_id)
		patient_obj = Patient.objects.get(pk=p_id)

		doctor = doctor_obj.username
		patient = patient_obj.username

		username = request.user.username

		if username == doctor or username == patient:
			if chat_form.is_valid():
				message = chat_form.cleaned_data.get('message')
				auths = Authors.objects.filter(doctor=doctor, patient=patient)
				if auths.exists():
					authors = Authors.objects.get(doctor=doctor, patient=patient)

					self.create_message(authors, username, message)

					return HttpResponseRedirect(reverse('Happ:dpchat', args=(d_id, p_id,)))
				else:
					auths = Authors.objects.create(doctor=doctor, patient=patient)
					
					self.create_message(auths, username, message)

					return HttpResponseRedirect(reverse('Happ:dpchat', args=(d_id, p_id,)))
			else:
				return render(request, get_template(self), {'chat_form': chat_form, 'd_id': d_id, 'p_id': p_id})
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

	def create_message(self, auth, someone, message):

		Consulte.objects.create(authors=auth,
					 someone=someone,
					  message=message,
					  date=timezone.now())

class ChangePassword(View):
	form = ChangePassWordForm

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user_d = getDoctor(request)
		get_user_p = getPatient(request)
		if get_user_p or get_user_d:
			ch_p_form = self.form()
			return render(request, get_template(self), {'ch_p_form': ch_p_form})
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

	def post(self, request, *args, **kwargs):
		ch_p_form = self.form(request.POST)

		if ch_p_form.is_valid():
			user = request.user
			username = user.username
			new_pass = ch_p_form.cleaned_data.get('password')
			conf_new = ch_p_form.cleaned_data.get('confirm')

			if new_pass == conf_new:
				if len(new_pass) >= 8:
					match_1 = re.findall((r"\D\w+\d+"), new_pass)
					match_2 = re.findall((r"\d+\w+\D"), new_pass)
					if match_1 or match_2:
						same_pass = user.check_password(new_pass)
						
						if same_pass:
							return render(request, get_template(self), {'ch_p_form': ch_p_form, 'old_pass': 'The new password is the same as the old'})

						user.set_password(new_pass)
						user.save()
						
						return HttpResponseRedirect(reverse('Happ:login'))
					else:
						return render(request, get_template(self), {'ch_p_form': ch_p_form, 'must_be': 'password must contain aleast one character or number'})
				else:
					return render(request, get_template(self), {'ch_p_form': ch_p_form, 'too_short': 'The password is too short'})
			else:
				return render(request, get_template(self), {'ch_p_form': ch_p_form, 'p_no_match': 'password do not match'})
		else:
			return render(request, get_template(self), {'ch_p_form': ch_p_form, 'invalid': 'invalid input'})

class SurveyView(View):
	form = SurveryForm

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		survey_form = self.form()
		user = request.user.username

		try:
			_doc_ = Doctor.objects.get(username=user)
		except Exception as e:
			return render(request, get_template(self), {'survey_form': survey_form})

		down_form = DownSeruveyForm
		return render(request, get_template(self), {'survey_form': survey_form, 'down_form': down_form})

	def post(self, request, *args, **kwargs):
		survey_form = self.form(request.POST)
		author = request.user.username
		current = timezone.now()
		year = str(current.year)
		if survey_form.is_valid():
			question = survey_form.cleaned_data.get('question')
			answer = survey_form.cleaned_data.get('answer')

			try:
				surv = Survey.objects.filter(Q(question=question) & Q(author=author))
				if surv.exists():
					return render(request, get_template(self), {'survey_form': survey_form, 'already': 'you alreadey answerd this question choice another one'})
				else:
					Survey.objects.create(question=question, author=author, answer=answer)
					with open('survey/%s_data.txt' %(year), 'a') as f:
						f.write('Question: '+str(question)+'\n')
						f.write('Author: '+str(author)+'\n')
						f.write('Answer: '+str(answer)+'\n')
						f.write('---------------------------------------------------------------------'+'\n')
					return HttpResponseRedirect(reverse('Happ:survey'))
			except Exception as e:
				return HttpResponseRedirect(reverse('Happ:survey'))

class SurveyRequestForm(ModelForm):
	class Meta:
		model = SurveyVote
		fields = ['surv_title']

		labels = {
			'surv_title': ('survey title')
		}

class SurveyRequest(View):
	form = SurveyRequestForm

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getDoctor(request)

		if get_user:
			surv_req_form = self.form()
			reque_surv_list = SurveyWithVote.objects.all()
			high_sur_title = HighSurTitle.objects.all()

			return render(request, get_template(self), {'surv_req_form': surv_req_form, 'reque_surv_list': reque_surv_list, 'high_sur_title': high_sur_title})
		else:
			return HttpResponseRedirect(reverse('Happ:survey'))

	def post(self, request, *args, **kwargs):
		surv_req_form = self.form(request.POST)

		if surv_req_form.is_valid():
			_title_s = HighSurTitle.objects.all()
			_list_s = SurveyWithVote.objects.all()

			_title = surv_req_form.cleaned_data.get('surv_title')

			check_title = SurveyVote.objects.filter(surv_title=_title)
			if check_title:
				return render(request, get_template(self), {'surv_req_form': surv_req_form, 'high_sur_title': _title_s, 'reque_surv_list': _list_s,'alreadey_token_surv': 'the title is onlready token'})

			user = request.user.username
			_surv_ = SurveyVote.objects.create(surv_title=_title, author=user)
			SurveyWithVote.objects.create(surv_title=_surv_)

			return HttpResponseRedirect(reverse('Happ:reqsurv'))

class VoteForSurvey(View):
	form = SurveyRequestForm

	@method_decorator(login_required)
	def post(self, request, surv_id, *args, **kwargs):
		_surv_ = SurveyWithVote.objects.all()
		_surv_update = SurveyWithVote.objects.get(pk=surv_id)
		high_sur_title = HighSurTitle.objects.all()

		user_s = request.user.username
		list_of_docs = _surv_update.voters.all()

		_doc_ = Doctor.objects.get(username=user_s)
		vote_val = _surv_update.vote

		try:
			voted = request.POST['voted']
			if voted:
				if _doc_ in list_of_docs:
					return render(request, get_template(self), {'surv_req_form': self.form(), 'reque_surv_list': _surv_, 'high_sur_title': high_sur_title, 'alreadey_voted_s': 'alreadey voted this title'})

				_surv_update.vote = vote_val+1
				_surv_update.voters.add(_doc_)
		except Exception as e:
			try:
				unvoted = request.POST['unvoted']
				if unvoted:
					if _doc_ not in list_of_docs:
						return render(request, get_template(self), {'surv_req_form': self.form(), 'reque_surv_list': _surv_, 'high_sur_title': high_sur_title, 'alreadey_unvoted_s': 'alreadey unvoted this title'})

					_surv_update.vote = vote_val-1
					_surv_update.voters.remove(_doc_)
			except Exception as e:
				pass #return HttpResponseRedirect(reverse('Happ:reqsurv')

		finally:
			_surv_update.save()
			_surv_ = SurveyWithVote.objects.all()
			if len(_surv_) > 0:
				_surv_list = []
				for _surv in _surv_:
					_surv_list.append((_surv.surv_title, _surv.vote))

				create_high_title(_surv_list, 'Survey')

		return HttpResponseRedirect(reverse('Happ:reqsurv'))

class DownSeruveyForm(ModelForm):
	class Meta:
		model = Survey
		fields = ['question']

class DownSurvey(View):
	form = DownSeruveyForm

	@method_decorator(login_required)
	def post(self, request, *args, **kwargs):
		surv_form = self.form(request.POST)

		if surv_form.is_valid():
			choosen_quest = surv_form.cleaned_data.get('question')

			surv_qest = Question.objects.get(question=choosen_quest.question)
			_ques_date = surv_qest.date
			_ques_id = surv_qest.id

			q_year = _ques_date.year
			q_month = _ques_date.month
			q_day = _ques_date.day
			full_date = '%s-%s-%s' %(q_year, q_month, q_day)

			try:
				user_path = request.META['USERPROFILE']
			except Exception as e:
				user_path = '/storage/sdcard0/'

			down_folder = 'Downloads\\%s.txt' %('%s_survey_data_%s' %(full_date, _ques_id))

			full_path = '%s\\%s' %(user_path, down_folder)

			with open(full_path, 'w') as f:
				f.write(surv_qest.question+'\n###############################\n')
				for quest_ in surv_qest.survey_set.all():
					f.write('Author: '+quest_.author+'\n')
					f.write('Answer: '+quest_.answer+'\n')
					f.write('-------------------------------------\n')

		return HttpResponseRedirect(reverse('Happ:survey'))

class ProfilePicForm(ModelForm):
	class Meta:
		model = ProfilePicture
		fields = ['photo']

class ProfilePic(View):
	form = ProfilePicForm

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		pic_form = self.form()

		return render(request, get_template(self), {'pic_form': pic_form})

	def post(self, request, *args, **kwargs):
		pic_form = self.form(request.POST, request.FILES)

		if pic_form.is_valid():
			name = request.user.username

			pic = pic_form.cleaned_data.get('photo')
			import os
			try:
				pro = ProfilePicture.objects.get(username=name)
				static_pic = str(pro.photo)
				split_str = static_pic.split('/')
				last_e = split_str[-1]

				path = 'Happ\\static\\Happ\\file\\'
				
				for r, d, f in os.walk(path):
					if last_e in f:
						os.system('del %s%s' % (path, last_e))
						break

				pic.name = name+pic.name[-4:]
				pro.photo = pic
				pro.save()
			except Exception as e:
				pic.name = name+pic.name[-4:]
				ProfilePicture.objects.create(username=request.user.username, photo=pic)

			del os
			return HttpResponseRedirect(reverse('Happ:profilepic'))
		else:
			return render(request, get_template(self), {'pic_form': pic_form, 'invalid': 'invalid input'})

#----------------------------------Now Doctor Views----------------------------------

def getDoctor(request):
	name = request.user.username
	try:
		user = Doctor.objects.get(username=name)
		'''if user.exists():
			return user
		else:
			return'''
		return user
	except Exception as e:
		return False

class DoctorIndexView(View):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getDoctor(request)
		if get_user:
			name = get_user.username
			user_profile = Doctor.objects.get(username=name)

			return render(request, get_template(self), add_pic_dict({'name': name, 'd_profile': user_profile}, request, 'd_pic'))
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

class DocotorProfileForm(ModelForm):
	class Meta:
		model = Doctor
		exclude = ['date']

class DoctorProfile(View):
	form = DocotorProfileForm

	def initials(self, _req):
		name = _req.user.username
		user = Doctor.objects.get(username=name)

		initial = {'username': user.username, 'first_name': user.first_name,
		'last_name': user.last_name, 'age': user.age, 'email': user.email,
		'profession': user.profession, 'phone': user.phone}

		return user, self.form(initial=initial)

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getDoctor(request)
		if get_user:
			
			user, d_profile_form = self.initials(request)
			return render(request, get_template(self), add_pic_dict({'d_profile_form': d_profile_form, 'user_profile': user}, request, 'd_pic'))
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

	def post(self, request, *args, **kwargs):
		d_profile_form = self.form(request.POST)
		name = request.user.username

		if d_profile_form.is_valid():
			change = 0

			username = d_profile_form.cleaned_data.get('username')
			first_name = d_profile_form.cleaned_data.get('first_name')
			last_name = d_profile_form.cleaned_data.get('last_name')

			if not is_string(first_name) or not is_string(last_name):
				user, d_profile_form = self.initials(request)
				return render(request, get_template(self), add_pic_dict({'not_valid_ch': 'number is not allowed in name','d_profile_form': d_profile_form, 'user_profile': user}, request, 'd_pic'))

			age = d_profile_form.cleaned_data.get('age')

			if not age >= 18:
				user, d_profile_form = self.initials(request)
				return render(request, get_template(self), add_pic_dict({'invalid_age':'your age must be atleast 18 or greater', 'd_profile_form': d_profile_form, 'user_profile': user}, request, 'd_pic'))

			email = d_profile_form.cleaned_data.get('email')
			profession = d_profile_form.cleaned_data.get('profession')
			phone = d_profile_form.cleaned_data.get('phone')

			if not is_valid_phone(phone):
				user, d_profile_form = self.initials(request)
				return render(request, get_template(self), add_pic_dict({'not_valid_phone':'please enter a valid phone number', 'd_profile_form': d_profile_form, 'user_profile': user}, request, 'd_pic'))

			doctor = Doctor.objects.get(username=name)
			user = User.objects.get(username=name)

			if username != doctor.username:
				if doctor.username in doctor_list:
					doctor_list.remove(doctor.username)
					doctor_list.append(username)

				doctor.username = username
				user.username = username
				auths = Authors.objects.filter(doctor=name)
				discussion_name = Chat.objects.filter(doctor=name)
				for a in auths:
					ac = a.consulte_set.filter(someone=name)
					for n in ac:
						n.someone = username
						n.save()
				for auth in auths:
					auth.doctor = username
					auth.save()
				for dis_name in discussion_name:
					dis_name.doctor = username
					dis_name.save()
				change += 1

			if first_name != doctor.username:
				doctor.first_name = first_name
				user.first_name = first_name
				change +=1

			if last_name != doctor.last_name:
				doctor.last_name = last_name
				user.last_name = last_name
				change += 1

			if age != doctor.age:
				doctor.age = age
				change += 1

			if email != doctor.email:
				doctor.email = email
				user.email = email
				change += 1

			if profession != doctor.profession:
				doctor.profession = profession
				change += 1

			if phone != doctor.phone:
				doctor.phone = phone
				change += 1
			#date = datetime.datetime.now()
			if change <= 0:
				user, d_profile_form = self.initials(request)
				return render(request, get_template(self), add_pic_dict({'no_change': 'you have made no change', 'd_profile_form': d_profile_form, 'user_profile': user}, request, 'pic'))

			doctor.save()
			user.save()
			return HttpResponseRedirect(reverse('Happ:doctorIndex'))
		else:
			return render(request, get_template(self), add_pic_dict({'d_profile_form': d_profile_form, 'invalid': 'invalid input'}, request, 'pic'))

class OnlinePntUser(View):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getDoctor(request)
		if get_user:
			online_pnt = patient_list
			all_pnt = Patient.objects.all()
			d_id = get_user.id
			'''for user in get_user:
				#name = user.username
				d_id = user.id'''
			return render(request, get_template(self), {'all_pnt': all_pnt, 'd_id': d_id, 'online_pnt': online_pnt})
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

class AddNewForm(ModelForm):
	class Meta:
		model = News
		fields = ['title', 'content']
		labels = {
			'title': ('News title'),
			'content': ('News content'),
		}
		widgets = {
			'title': TextInput(attrs={'placeholder': 'title here'}),
			'content': Textarea(attrs={'placeholder': 'content here'}),
		}

class AddNewsView(View):
	form = AddNewForm

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getDoctor(request)
		if get_user:
			news_form = self.form()
			return render(request, get_template(self), {'news_form': news_form})
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

	def post(self, request, *args, **kwargs):
		news_form = self.form(request.POST)

		if news_form.is_valid():
			title = news_form.cleaned_data.get('title')
			content = news_form.cleaned_data.get('content')

			News.objects.create(title=title, content=content, date=timezone.now(), doctor=request.user.username)
			return HttpResponseRedirect(reverse('Happ:doctorIndex'))


class StatusDecisionView(View):

	@method_decorator(login_required)
	def post(self, request, apt_id, *args, **kwargs):
		
		try:
			accept = request.POST['accept']
			apt = Appointment.objects.get(pk=apt_id)
			apt.confirm = 'accepted'
			apt.save()
			return HttpResponseRedirect(reverse('Happ:dvappoint'))
		except Exception as e:
			try:
				reject = request.POST['reject']
				apt = Appointment.objects.get(pk=apt_id)
				apt.confirm = 'rejected'
				apt.save()
				return HttpResponseRedirect(reverse('Happ:dvappoint'))
			except Exception as e:
				raise e


class DVAppointment(View):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getDoctor(request)
		if get_user:
			d_username = get_user.username
			doctor = Doctor.objects.get(username=d_username)
			current_time = timezone.now()
			d_appoint = Appointment.objects.filter(doctor=doctor).order_by("date__year").order_by("date__month").order_by("date__day")
			if d_appoint.exists():
				return render(request, get_template(self), {'d_appoint': d_appoint.reverse()})
			else:
				return render(request, get_template(self), {'no_appoint': 'there is no appointment'})
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

class SearchPnt(View):
	form = make_form('SearchForm', ('search',))

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getDoctor(request)
		if get_user:
			pnt_search_form = self.form()
			all_pnts = Patient.objects.all()

			return render(request, get_template(self), {'pnt_search_form': pnt_search_form, 'all_pnts': all_pnts})
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

	def post(self, request, *args, **kwargs):
		pnt_search_form = self.form(request.POST)
		all_pnts = Patient.objects.all()

		if pnt_search_form.is_valid():
			search = pnt_search_form.cleaned_data.get('search')
			
			try:
				p_name = Patient.objects.filter(username__contains=search).order_by("username")
				if p_name:
					return render(request, get_template(self), {'pnt_search_form': pnt_search_form, 'p_name': p_name, 'all_pnts': all_pnts})
				else:
					return render(request, get_template(self), {'pnt_search_form': pnt_search_form, 'all_pnts': all_pnts, 'noresult': 'no result found for %s search' %(search)})
			except Exception as e:
				pass
		else:
			return render(request, get_template(self), {'pnt_search_form': pnt_search_form})

class PatientDetail(View):

	@method_decorator(login_required)
	def get(self, request, patient_id, *args, **kwargs):
		get_user = getDoctor(request)
		if get_user:
			try:
				patient = Patient.objects.get(pk=patient_id)
				pnt_pic = _get_pic(patient.username)

				return render(request, get_template(self), {'patient': patient, 'pnt_pic': pnt_pic})
			except Exception as e:
				return HttpResponseRedirect(reverse('Happ:pntsearch'))
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

class NotificationView(View):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getDoctor(request)
		if get_user:
			current_time = datetime.datetime.now()
			current_hour = current_time.hour
			current_min = current_time.minute
			current_user = get_user.username
			doctor = Doctor.objects.get(username=current_user)

			appoint_time = Appointment.objects.filter(Q(doctor=doctor) & Q(time__hour=current_hour)
			 & Q(date__day=current_time.day) & Q(date__month=current_time.month) & Q(date__year=current_time.year))

			emergency_req = Emergency.objects.filter(Q(date__hour=current_hour))
			if appoint_time.exists() and emergency_req.exists():
				'''for p in appoint_time:
					p_name = p.patient
					patient = Patient.objects.get(username=p_name)
					patient_id = patient.id'''
				return render(request, get_template(self), {'appoint_time': appoint_time,'emerg_req': emergency_req})
			
			elif emergency_req.exists():
				return render(request, get_template(self), {'emerg_req': emergency_req})
			
			elif appoint_time.exists():
				return render(request, get_template(self), {'appoint_time': appoint_time})
			
			else:
				return render(request, get_template(self), {'empty_not': 'you have no notification in this time'})
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

class VEmergency(View):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getDoctor(request)
		if get_user:
			current_time = datetime.datetime.now()
			current_hour = current_time.hour
			past_emerg = Emergency.objects.all()

			curr_emerg = Emergency.objects.filter(date__hour=current_hour)
			if curr_emerg.exists():
				
				return render(request, get_template(self), {'curr_emerg': curr_emerg, 'past_emerg': past_emerg})
			else:
				return render(request, get_template(self), {'past_emerg': past_emerg, 'empty_notify': 'there is no emergency calls now.'})
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

class DiscussionList(View):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getDoctor(request)
		if get_user:
			dis_list = Discussion.objects.all()
			return render(request, get_template(self), {'dis_list': dis_list, 'for_link': 'here'})
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

class DiscussionForm(ModelForm):
	class Meta:
		model = Chat
		fields = ['message']
		labels = {
			'message': ('message'),
		}
		widgets = {
			'message': TextInput(attrs={'placeholder': 'your message'}),
		}

class DiscussionView(View):
	form = DiscussionForm

	@method_decorator(login_required)
	def get(self, request, dis_id, *args, **kwargs):
		get_user = getDoctor(request)
		if get_user:
			try:
				dis_form = self.form()
				all_chats = Discussion.objects.get(pk=dis_id)
				return render(request, get_template(self), {'dis_form': dis_form, 'all_chats': all_chats, 'dis_id': dis_id})
			except Exception as e:
				return HttpResponseRedirect(reverse('Happ:dislist'))
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

	def post(self, request, dis_id, *args, **kwargs):
		dis_form = self.form(request.POST)
		dis_sub = Discussion.objects.get(pk=dis_id)

		if dis_form.is_valid():
			message = dis_form.cleaned_data.get('message')

			mes = Chat.objects.create(doctor=request.user.username, message=message)
			dis_sub.chat.add(mes)
			return HttpResponseRedirect(reverse('Happ:discussion', args=(dis_id,)))
		else:
			return render(request, get_template(self), {'dis_form': dis_form, 'invalid': 'invalid input'})

class DiscusionVoteForm(ModelForm):
	class Meta:
		model = DiscussionVote
		fields = ['dis_title']

		labels = {
			'dis_title': ('discussion title')
		}

class DiscussionListAndVote(View):
	form = DiscusionVoteForm 

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		get_user = getDoctor(request)
		if get_user:
			dis_vote_form = self.form()
			all_dis_vote = DiscussionWithVote.objects.all()
			high_title = HighDisTitle.objects.all()

			return render(request, get_template(self), {'dis_vote_form': dis_vote_form, 'all_dis_vote': all_dis_vote, 'high_title': high_title})

	def post(self, request, *args, **kwargs):
		dis_vote_form = self.form(request.POST)

		if dis_vote_form.is_valid():
			_list_d = DiscussionWithVote.objects.all()
			_title_d = HighDisTitle.objects.all()

			title = dis_vote_form.cleaned_data.get('dis_title')
			username = request.user.username

			check_title = DiscussionVote.objects.filter(dis_title=title)
			if check_title:
				return render(request, get_template(self), {'dis_vote_form': dis_vote_form, 'all_dis_vote': _list_d, 'high_title': _title_d,'title_token': 'the title is onlready token'})

			_dis_ = DiscussionVote.objects.create(dis_title=title, author=username)
			DiscussionWithVote.objects.create(dis_title = _dis_)

			return HttpResponseRedirect(reverse('Happ:disvote'))

class VoteForDiscussion(View):
	form = DiscusionVoteForm
	
	@method_decorator(login_required)
	def post(self, request, dis_id, *args, **kwargs):
		dis = DiscussionWithVote.objects.all()
		_dis_update = DiscussionWithVote.objects.get(pk=dis_id)
		_title_d = HighDisTitle.objects.all()

		user_n = request.user.username
		list_of_docs = _dis_update.voters.all()

		user = Doctor.objects.get(username=user_n)
		vote_val = _dis_update.vote

		try:

			voted = request.POST['voted']
			if voted:
				if user in list_of_docs:
					return render(request, get_template(self), {'dis_vote_form': self.form(), 'all_dis_vote': dis, 'high_title': _title_d,'alreadey_voted': 'you alreadey voted this title'})

				_dis_update.vote = vote_val+1
				_dis_update.voters.add(user)

		except Exception as e:

			try:
				unvoted = request.POST['unvoted']
				if unvoted:
					if user not in list_of_docs:
						return render(request, get_template(self), {'dis_vote_form': self.form(), 'all_dis_vote': dis, 'high_title': _title_d,'alreadey_unvoted': 'you alreadey unvoted this title'})
					
					_dis_update.vote = vote_val-1
					_dis_update.voters.remove(user)

			except Exception as e:
				pass #return HttpResponseRedirect(reverse('Happ:disvote')

		finally:
			_dis_update.save()
			dis = DiscussionWithVote.objects.all()
			if len(dis) > 0:
				_dis_list = []
				for dis_val in dis:
					_dis_list.append((dis_val.dis_title, dis_val.vote))

				create_high_title(_dis_list, 'Discussion')

		return HttpResponseRedirect(reverse('Happ:disvote'))

def create_high_title(_list_, model_name):
	from collections import OrderedDict

	dis_dict = OrderedDict(_list_)

	def this_model(model_name):
		if model_name == 'Discussion':
			model_obj = HighDisTitle.objects
		if model_name == 'Survey':
			model_obj = HighSurTitle.objects

		return model_obj

	for key,value in dis_dict.items():

		exs_title = this_model(model_name).filter(title=key)
		if exs_title.exists():

			for _title in exs_title:
				_title.vote = value
				_title.save()
		else:
			this_model(model_name).create(title=key, vote=value)

	hi_tit = this_model(model_name).all()

	if len(hi_tit) > 0:
		high_list = []

		for high in hi_tit:
			high_list.append((high.title, high.vote))
		
		high_dict = OrderedDict(high_list)
		max_high_val = max(high_dict.values())

		for h_key, h_value in high_dict.items():
			if h_value == max_high_val:
				continue
			else:
				del_h = this_model(model_name).get(title=h_key)
				del_h.delete()

class RedirectUserToHome(View):

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		_username = request.user.username

		try:
			_user_p = Patient.objects.filter(username=_username)
			_user_d = Doctor.objects.filter(username=_username)
			if _user_p.exists():
				return HttpResponseRedirect(reverse('Happ:patientIndex'))
			elif _user_d.exists():
				return HttpResponseRedirect(reverse('Happ:doctorIndex'))
			else:
				return HttpResponseRedirect(reverse('Happ:login'))
		except Exception as e:
			return HttpResponseRedirect(reverse('Happ:login'))

class LogoutUser(View):

	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			name = request.user.username
			if name in doctor_list:
				doctor_list.remove(name)
			elif name in patient_list:
				patient_list.remove(name)
			else:
				pass
			logout(request)
			return HttpResponseRedirect(reverse('Happ:login'))
		else:
			return HttpResponseRedirect(reverse('Happ:login'))

public_class = (
				('IndexView', 'allindex', IndexView),
				('UserLogin', 'login', UserLogin), 
				('UserSignup', 'signup', UserSignup),
				('ForgetPassword', 'forget', ForgetPassword), 
				('SendCode', 'sendcode', SendCode),
				('AuthenCode', 'authcode', AuthenCode),
				('ResetPassword', 'resetpass', ResetPassword),
			   )

patient_class = (
				('PatientIndexView', 'patientIndex', PatientIndexView),
				('PatientProfile', 'Pprofile', PatientProfile), 
				('OnlineDocUsers', 'online', OnlineDocUsers),
				('PreAppointView', 'preappoint', PreAppointView),
				('MakeAppointment', 'Mappoint', MakeAppointment), 
				('ViewAppointment', 'Vappoint', ViewAppointment),
				('EmergencyCall', 'emergency', EmergencyCall), 
				('SearchDoctorView', 'search', SearchDoctorView),
				('DoctorDetailView', 'doctorDetail', DoctorDetailView), 
				('InfoView', 'info', InfoView),
				('NewsView', 'news', NewsView),
				('NewsDetailView', 'newsdetail', NewsDetailView),
				('NewsComments', 'newscomm', NewsComments),
				('EditComment', 'editcom', EditComment),
				('ChoosenLauguage', 'clang', ChoosenLauguage),
				('RedirectUserToHome', 'rediuser', RedirectUserToHome),
				('TryAgainView', 'tryagain', TryAgainView),
				)

doctor_class = (
				('DoctorIndexView', 'doctorIndex', DoctorIndexView),
				('DoctorProfile', 'Dprofile', DoctorProfile), 
				('OnlinePntUser', 'pntonline', OnlinePntUser),
				('AddNewsView', 'addnews', AddNewsView), 
				('DVAppointment', 'dvappoint', DVAppointment),
				('SearchPnt', 'pntsearch', SearchPnt), 
				('PatientDetail', 'pdetail', PatientDetail),
				('NotificationView', 'notify', NotificationView), 
				('VEmergency', 'Vemerg', VEmergency),
				('DiscussionList', 'dislist', DiscussionList), 
				('DiscussionView', 'discussion', DiscussionView),
				('DiscussionListAndVote', 'disvote', DiscussionListAndVote),
				('VoteForDiscussion', 'voteddis', VoteForDiscussion),
				('DownSurvey', 'downquest', DownSurvey),
				('StatusDecisionView', 'sdecision', StatusDecisionView),
			   )
			
both_class = (
			  ('DPChatView', 'dpchat', DPChatView),
			  ('ChangePassword', 'changep', ChangePassword), 
			  ('SurveyView', 'survey', SurveyView),
			  ('ProfilePic', 'profilepic', ProfilePic),
			  ('SurveyRequest', 'reqsurv', SurveyRequest),
			  ('VoteForSurvey', 'votesurv', VoteForSurvey),
			 )

lonely_class_name = {'logout': LogoutUser, 'unauth': UnAuthorizedAccess}

class TemplateManager(object):

	_template_name = 'Happ/public.html'
	_patient_template_name = 'Happ/patient_view.html'
	_both_template_name = 'Happ/both_view.html'
	_doctor_template_name = 'Happ/doctor_view.html'


	def __init__(self, class_):

		if type(class_).__name__ == 'function':
			_class = class_.__name__
		else:
			_class =  class_.__class__.__name__

		self.classname = _class

	def __call__(self):
		template_name = self.set_name()
		return template_name

	def get_name(self):
		prefix, name_set = self.parse_list(self.classname)
	
		return prefix, name_set
		

	def set_name(self):
		name = self.this_class_name
		if name:
			if name.startswith('public'):
				return self._template_name
			if name.startswith('patient'):
				return self._patient_template_name
			if 	name.startswith('doctor'):
				return self._doctor_template_name
			if name.startswith('both'):
				return self._both_template_name
		else:
			return

	@property
	def this_class_name(self):
		prefix, name_set = self.get_name()
		pre_and_name = '%s%s' %(prefix, name_set[0])
		
		return pre_and_name

	@staticmethod
	def parse_list(name):
		if name in lonely_class_name:
			class_name = lonely_class_name[name]
			return None, (None, None, class_name)

		for i in range(len(public_class)):
			if name in public_class[i]:
				return 'public_', public_class[i]

		for i in range(len(patient_class)):
			if name in patient_class[i]:
				return 'patient_', patient_class[i]

		for i in range(len(doctor_class)):
			if name in doctor_class[i]:
				return 'doctor_', doctor_class[i]

		for i in range(len(both_class)):
			if name in both_class[i]:
				return 'both_', both_class[i]


def get_request_class():
	
	return ViewClass.as_view()