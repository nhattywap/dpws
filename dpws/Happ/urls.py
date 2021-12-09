from django.urls import path, re_path, include
from .views import get_request_class

app_name = 'Happ'

patient_patterns = [
	path('patient-index/', get_request_class(), name='patientIndex'),
	path('make-appointment/', get_request_class(), name='Mappoint'),
	path('view-appointment/', get_request_class(), name='Vappoint'),
	path('emergency/', get_request_class(), name='emergency'),
	path('search/', get_request_class(), name='search'),
	path('<int:doctor_id>/doctor-detail/', get_request_class(), name='doctorDetail'),
	path('info/', get_request_class(), name='info'),
	path('news/', get_request_class(), name='news'),
	path('<int:news_id>/news-detail/', get_request_class(), name='newsdetail'),
	path('online/', get_request_class(), name='online'),
	path('patient-profile/', get_request_class(), name='Pprofile'),
	path('<int:news_id>/news-comments/', get_request_class(), name='newscomm'),
	path('<int:com_id>/edit-comment/', get_request_class(), name='editcom'),
	path('choose-lang/', get_request_class(), name='clang'),
	path('redirect-user/', get_request_class(), name='rediuser'),
	path('pre-appoint/', get_request_class(), name='preappoint'),
	path('<int:apont_id>/try-again', get_request_class(), name='tryagain'),
]

doctor_patterns = [
	path('doctor-index/', get_request_class(), name='doctorIndex'),
	path('add-news/', get_request_class(), name='addnews'),
	path('d-v-appoint/', get_request_class(), name='dvappoint'),
	path('<int:patient_id>/patient-detail/', get_request_class(), name='pdetail'),
	path('notification/', get_request_class(), name='notify'),
	path('view-emergency/', get_request_class(), name='Vemerg'),
	path('dis-list/', get_request_class(), name='dislist'),
	path('<int:dis_id>/discussion/', get_request_class(), name='discussion'),
	path('pnt-online', get_request_class(), name='pntonline'),
	path('doctor-profile/', get_request_class(), name='Dprofile'),
	path('pnt-search/', get_request_class(), name='pntsearch'),
	path('dis-vote/', get_request_class(), name='disvote'),
	path('<int:dis_id>/dis-voted/', get_request_class(), name='voteddis'),
	path('down-qust/', get_request_class(), name='downquest'),
	path('<int:apt_id>/apt-decision/', get_request_class(), name='sdecision'),
]

both_patterns = [
	path('<int:d_id>/<int:p_id>/chat/', get_request_class(), name='dpchat'),
	path('change-pass/', get_request_class(), name='changep'),
	path('survey/', get_request_class(), name='survey'),
	path('profile-pic/', get_request_class(), name='profilepic'),
	path('req-survey/', get_request_class(), name='reqsurv'),
	path('<int:surv_id>/vote-surv', get_request_class(), name='votesurv'),
]

urlpatterns = [
	path('', get_request_class(), name='allindex'),
	path('login/', get_request_class(), name='login'),
	path('forget/', get_request_class(), name='forget'),
	path('sendcode/', get_request_class(), name='sendcode'),
	path('auth-code/', get_request_class(), name='authcode'),
	path('reset-pass/', get_request_class(), name='resetpass'),
	path('logout/', get_request_class(), name='logout'),
	path('signup/', get_request_class(), name='signup'),
	path('unauth/', get_request_class(), name='unauth'),
	path('patient/', include(patient_patterns)),
	path('doctor/', include(doctor_patterns)),
	path('both/', include(both_patterns)),
]