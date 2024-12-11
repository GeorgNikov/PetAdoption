import os

from django.core.wsgi import get_wsgi_application

settings_module = 'PetAdoption.deployment' if 'WEBSITE_HOSTNAME' else 'PetAdoption.settings'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()
