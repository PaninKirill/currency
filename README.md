[![Build Status](https://travis-ci.org/simkimsia/UtilityBehaviors.png)](https://travis-ci.com/PaninKirill/currency.svg?branch=master)

### Currency-exchange

> STACK: 
* Django
* Postgres 
* Memcached
* Celery
* Celery-beat
* RabbitMQ
* REST API with token auth
* Flower 
* Portainer
* Nginx
* Postgres
* Gunicorn 
* Beautiful-soup
* Pytest
* Regex
* Web-parsers

>CI/CD:
* Codecov
* Travis

### Quick Start

`Install docker and docker-compose`

```bash
# In root directory
cp .env.example .env
```

```bash
# Build with Docker-compose
docker-compose up -d --build
```
### Setup project and run tests
```bash
# In root directory
bash backend/commands/setup.sh
bash backend/commands/check.sh
```

### Nginx serves application on:

* http://localhost:8000/

Documentation API:
* http://localhost/api/v1/swagger/
* http://localhost/api/v1/redoc/

Logs / Docker-compose containers watch:
* http://localhost:9000/
