import os
from django.core.asgi import get_asgi_application

# Standard setup for a Django 3-tier architecture 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Shree1.settings')

application = get_asgi_application()