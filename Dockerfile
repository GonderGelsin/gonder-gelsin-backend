FROM python:3.11-slim

# Sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && apt-get clean

# Çalışma dizinini ayarla
WORKDIR /app

# Python bağımlılıklarını yükle
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . /app/

# Static dizini oluştur
RUN mkdir -p /app/static

# Django ayarlarını belirle
ENV DJANGO_SETTINGS_MODULE=backend.settings

# Uygulama portunu aç
EXPOSE 8000

# Migration ve sunucu başlatma komutlarını birleştir
CMD bash -c "python manage.py migrate && python manage.py collectstatic --noinput && uvicorn backend.asgi:application --host 0.0.0.0 --port 8000"
