# ChatUP

ChatUP - it`s an interactive platform with chat and related mechanisms for simple and reliable
streaming without dependency on popular platforms.

## Setup

Use external services or start via Docker:
```
docker-compose up -d
```

Migrate database:
```
python manage.py migrate
```

Install fixtures:
```
python manage.py loaddata init
```

Compile translations:
```
django-admin compilemessages
```

Run development server:
```
python manage.py runserver
```

Use `CUP_CONF` environment variable for custom config from `.ini` file in the `config` folder,
otherwise `config.ini` will be used.

Log in with credentials `admin / admin` or `streamer / streamer`.
