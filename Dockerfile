# 1) Base image
FROM python:3.11-slim

# 2) System deps (psycopg2/compilers etc.)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential libpq-dev bash \
  && rm -rf /var/lib/apt/lists/*

# 3) Python settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 4) Workdir
WORKDIR /app

# 5) Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6) Copy project
COPY . .

# 7) Django env that matches your project package
ENV DJANGO_SETTINGS_MODULE=whatsapp_bulk.settings
ENV DEBUG=false

# 8) Collect static (but don't fail build if not configured yet)
RUN bash -lc 'python manage.py collectstatic --noinput || true'

# 9) Expose & run
ENV PORT=8080

# (Optional) Auto‑migrate on start (useful for SQLite / quick demo)
# If you don't want this, switch CMD to the single gunicorn line below.
CMD bash -lc 'python manage.py migrate --noinput || true && \
  exec gunicorn whatsapp_bulk.wsgi:application --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 120'

# If you prefer not to run migrations on container start, use:
# CMD ["gunicorn", "whatsapp_bulk.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "120"]
