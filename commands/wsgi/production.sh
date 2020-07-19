#!/bin/bash

uwsgi --processes 4 --threads 2 --http :8000 --chdir /srv/project/src --module settings.wsgi