release: cd chatup && echo $CONFIG | base64 -d > ./config/config_deploy.ini && python manage.py migrate && python manage.py compilemessages && python manage.py collectstatic --noinput
web: daphne --root-path=/chatup config.asgi:application --port $PORT --bind 0.0.0.0 -v2