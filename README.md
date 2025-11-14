# UH Care (United Home Care) — Local dev and infra notes

This repository contains the Django-based UH Care web application.

Quick start (using Docker Compose)

1) Build and start services (Postgres, Redis, Web):

```bash
docker compose up -d --build
```

2) Run migrations and create a superuser:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

3) Start a Celery worker (in a separate terminal):

```bash
docker compose exec web celery -A config worker --loglevel=info
```

Notes
- Configuration is read from environment variables (see `config/settings.py`).
- For production: set `USE_S3=True` and the AWS_* environment variables, set `DATABASE_URL` to a Postgres instance, and secure `DJANGO_SECRET_KEY`.

Local dev without Docker
- Install dependencies into your virtualenv:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
