# ChatUP

[![Tests Status](https://github.com/AverHLV/chatup/workflows/Tests/badge.svg)](https://github.com/AverHLV/chatup/actions?query=workflow%3ATests)

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
python manage.py compilemessages
```

Run development server:
```
python manage.py runserver
```

Set needed environment variables (see definition below), 
for a basic setup no environment variables are needed.

Log in with credentials `admin / admin` or `streamer / streamer`.

## Environment variables

- `CH_SECRET_KEY`, `default=secret` - project`s secret key, default value allowed only in DEBUG mode;
- `CH_DEBUG`, `default=true` - whether DEBUG mode should be enabled;
- `CH_ALLOWED_HOSTS`, `default=*` - allowed hosts list, separated by a comma;
- `DATABASE_URL`, `default=postgres://postgres:postgres@localhost:5432/chatup` - database url;
- `REDIS_URL`, `default=redis://localhost:6379` - redis url;
- `CH_HOST`, `default=http://127.0.0.1:8000` - hostname with a schema;
- `CH_DEFAULT_LANG`, `default=en` - api default language;

## Documentation

Swagger UI available on `/api/docs`. All dev-needed links available on `/dev`.

## Important CLI commands

Run tests in parallel with preserving testing database:

```
python manage.py test --keepdb --parallel
```

Populate database with generated objects (broadcasts and messages):

```
python manage.py create
```

Drop schema for default database (PostgreSQL only):

```
python manage.py reset-db
```

Drop schema without confirmation (Heroku case):

```
python manage.py reset-db -nc True
```
