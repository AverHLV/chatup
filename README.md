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

Use `CUP_CONF` environment variable for custom config from `.ini` file in the `config` folder,
otherwise `config.ini` will be used.

Custom Swagger UI url can be specified with `CUP_API_DOCS_URL` environment variable.

Log in with credentials `admin / admin` or `streamer / streamer`.

## Documentation

Swagger UI available on `/api/docs`.

## Important CLI commands

Run tests in parallel with preserving testing database:

```
python manage.py test --keepdb --parallel
```
