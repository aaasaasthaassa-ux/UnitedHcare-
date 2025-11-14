# UH Care (United Home Care) — Local dev and infra notes

This repository contains the Django-based UH Care web application.

## Quick start (using Docker Compose)

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

## Notes

- Configuration is read from environment variables (see `config/settings.py`).
- For production: set `USE_S3=True` and the `AWS_*` environment variables, set `DATABASE_URL` to a Postgres instance, and secure `DJANGO_SECRET_KEY`.

## Local dev without Docker

Install dependencies into your virtualenv and run locally:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Troubleshooting

- If you run into static file problems in production, confirm `STATIC_ROOT` and `STATICFILES_STORAGE` are configured and collect static files with `python manage.py collectstatic`.
- If using a remote database, set `DATABASE_URL` and remove or adjust any local `sqlite3` references in `config/settings.py`.

If you want, I can add a CONTRIBUTING section, a minimal development checklist, or a GitHub Actions CI workflow next.
