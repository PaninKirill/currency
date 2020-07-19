#!/bin/bash

rm /srv/project/tmp/celerybeat-schedule /srv/project/tmp/celerybeat.pid
celery -A settings beat --loglevel=info --workdir=/srv/project/src --schedule=/srv/project/tmp/celerybeat-schedule --pidfile=/srv/project/tmp/celerybeat.pid