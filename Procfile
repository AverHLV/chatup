release: cd chatup &&
         echo $CONFIG > ./config/config_deploy.ini
         python manage.py migrate &&
         python manage.py compilemessages &&
         python manage.py collectstatic --noinput

web: daphne config.asgi:application --port $PORT --bind 0.0.0.0 -v2