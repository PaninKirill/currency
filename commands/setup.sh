#!/usr/bin/env bash

docker exec -it backend python ./src/manage.py collectstatic --noinput &&
docker exec -it backend python ./src/manage.py migrate
