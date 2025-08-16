FROM python:3.12-slim

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Proje dosyaları
COPY . /app

# collectstatic için env okunmalı
ENV DJANGO_ENV=prod
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Gunicorn kurulumu (yoksa)
RUN pip install --no-cache-dir gunicorn

# entrypoint script executable
RUN chmod +x /app/deploy/backend/entrypoint.sh
