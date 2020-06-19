SECRET_KEY = '^ueo-4=t96eio5zjege^ae!0g15^tf2=yey5(360^^=jwl)m*d'

CELERY_ALWAYS_EAGER = CELERY_TASK_ALWAYS_EAGER = True

DEBUG = True
ALLOWED_HOSTS = ['*']

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'dev.ops.tests@gmail.com'
EMAIL_HOST_PASSWORD = 'brainfuck436'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
