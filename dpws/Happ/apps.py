from django.apps import AppConfig


class HappConfig(AppConfig):
    name = 'Happ'

    def ready(self):
    	import Happ.signals