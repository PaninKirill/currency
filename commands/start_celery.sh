#!/bin/bash

rm /srv/project/tmp/celery.pid
celery -A settings worker -E --loglevel=info --workdir=/srv/project/src --pidfile=/srv/project/tmp/celery.pid