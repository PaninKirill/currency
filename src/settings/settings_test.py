from settings.settings import *

SECRET_KEY = 'esfnsjkfbrdjgbdrkjgbdrkgjd'
DEBUG = False
ALLOWED_HOSTS = ['*']

CELERY_ALWAYS_EAGER = CELERY_TASK_ALWAYS_EAGER = True  # run celery tasks as functions

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db-test.sqlite3'),
    }
}

EMAIL_BACKEND = 'django.core.mail.outbox'
