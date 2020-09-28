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

Run development server:
```
python manage.py runserver
```

Use `CUP_CONF` environment variable for custom config from `.ini` file in the `config` folder,
otherwise `config.ini` will be used.
