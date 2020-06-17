SECRET_KEY = '^ueo-4=t96eio5zjege^ae!0g15^tf2=yey5(360^^=jwl)m*d'

DEBUG = True
# False # python ./src/manage.py runserver --insecure
CELERY_ALWAYS_EAGER = CELERY_TASK_ALWAYS_EAGER = True

ALLOWED_HOSTS = ['*']

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'devs.ops.tests@gmail.com'
EMAIL_HOST_PASSWORD = 'brainfuck436'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


