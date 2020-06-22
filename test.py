def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b"Hello World"]

# /Documents/currency/src$ uwsgi --http :8000 --module settings.wsgi --processes 4 --threads 2
