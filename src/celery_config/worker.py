import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from celery import Celery

from core.configuration import settings


celery = Celery(__name__)
celery.conf.broker_url = str(settings.CELERY_BROKER_URL)
celery.conf.result_backend = str(settings.CELERY_RESULT_BACKEND)
celery.autodiscover_tasks(["app.tasks.publickml"])
