release: python manage.py migrate
web: cd chatup && python manage.py compilemessages && python manage.py collectstatic --noinput && daphne config.asgi:application --port $PORT --bind 0.0.0.0 -v2