# MlBackendFfej

## Requirements

* [Docker](https://www.docker.com/) (compose).

## Local Development

* Start the stack with Docker Compose:
> Add the `openssl rand -hex 32` result to SECRET_KEY before run docker compose up -d
> Also u can start with more than one celery worker: `--scale worker=2` 

```bash
cp example.env .env
docker compose up -d
```

## ...

...

