Deploying to Render (recommended, free Git-based deploy)

This project is configured to deploy on Render or any Git-based PaaS that exposes $PORT.
Here's a minimal set of steps to get the app running on Render using your GitHub repo.

1) Push your code to GitHub
   - Ensure your project root contains `Procfile` and `requirements.txt`.

2) Create a Render account and connect your GitHub repo
   - Go to https://dashboard.render.com/new and create a Web Service.
   - Select your repository and branch (e.g., `main`).

3) Build & Start commands
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3

4) Environment variables (add these to Render's dashboard -> Environment)
   - DJANGO_SECRET_KEY: <your secret>
   - DJANGO_DEBUG: False
   - DJANGO_ALLOWED_HOSTS: yourdomain.com,127.0.0.1
   - DATABASE_URL: postgres://user:password@host:5432/dbname (use a managed DB or Render Postgres)
   - (Optional) AWS / EMAIL variables if you use S3 or SMTP for outgoing email.

5) Static files
   - `whitenoise` is configured and `STATICFILES_STORAGE` is set for production.
   - On first deploy, ensure `collectstatic` runs. Render runs your build command; it will collect static files if you run `python manage.py collectstatic --noinput` as part of a build hook or in the build command.

6) Database
   - After service is live, open Render's shell or use `render` CLI and run migrations:
     python manage.py migrate --noinput

7) Domain & TLS
   - Configure custom domain in Render (if you have one). Render will provision TLS automatically.

Notes
- For quick demos you can use SQLite, but for production use Postgres via Render's managed DB or Railway.
- If browser autoplay is blocked for hero videos, users will see the poster image and a play button (already implemented).

If you want, I can also:
- Add a small GitHub Actions workflow to run tests on push (I added one by default in `.github/workflows/ci.yml`).
- Help you connect the repo in the Render UI step-by-step.
