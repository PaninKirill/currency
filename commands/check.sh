#!/usr/bin/env bash

docker exec backend flake8 ./src &&
docker exec backend flake8 ./parse_workua &&
docker exec backend pip check &&
docker exec backend python ./src/manage.py validate_templates &&
docker exec backend python src/manage.py check &&
docker exec backend python src/manage.py makemigrations --check --dry-run &&
docker exec backend python src/manage.py collectstatic --noinput --dry-run &&
docker exec backend python src/manage.py validate_templates &&
docker exec backend pytest ./src/tests -s -x --cov-config=.coveragerc --cov=src --cov-report html --cov-fail-under=100 &&
docker-compose -f docker-compose.yml config --quiet &&
docker exec nginx nginx -t
