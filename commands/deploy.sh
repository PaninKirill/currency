#!/usr/bin/env bash

docker exec backend python ./src/manage.py makemigrations &&
docker exec backend python ./src/manage.py migrate &&
docker exec backend python ./src/manage.py collectstatic --noinput &&
docker exec -it backend pytest ./src/tests -s -x --cov=src --cov-report html &&
docker-compose restart && \
docker-compose restart nginx
