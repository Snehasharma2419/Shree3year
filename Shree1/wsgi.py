import os
from django.core.wsgi import get_wsgi_application

# Tells Django where your project settings are located [cite: 212]
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Shree1.settings')

application = get_wsgi_application()