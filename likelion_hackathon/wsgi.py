"""
WSGI config for likelion_hackathon project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from rentalhistories.tasks import scheduler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'likelion_hackathon.settings')

application = get_wsgi_application()

scheduler.start()