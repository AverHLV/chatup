release: cd chatup && python manage.py migrate
celery-beat: cd chatup && celery -A config beat -l INFO
celery-worker: cd chatup && celery -A config worker -l INFO --concurrency 2
web: cd chatup && python manage.py compilemessages && python manage.py collectstatic --noinput && daphne config.asgi:application --port $PORT --bind 0.0.0.0 -v2