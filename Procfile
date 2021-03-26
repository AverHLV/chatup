release: cd chatup && python manage.py migrate
celery: cd chatup && (celery -A config worker -l INFO --concurrency 2 & celery -A config beat -l INFO)
web: cd chatup && python manage.py compilemessages && python manage.py collectstatic --noinput && ((cd .. && bin/start-nginx) & daphne config.asgi:application -p 8000 -b 0.0.0.0 -v2)