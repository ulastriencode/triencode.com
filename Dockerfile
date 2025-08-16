FROM python:3.12-slim

# Sistem paketleri
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    libjpeg62-turbo-dev zlib1g-dev libpng-dev libfreetype6-dev \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# Gereken dosyaları kopyala (önce requirements hızlı cache için)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Proje
COPY . /app

# Django runserver 0.0.0.0 dinlesin
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# İsteğe bağlı: statik topla klasörü
RUN mkdir -p /app/staticfiles /app/media

EXPOSE 8000
