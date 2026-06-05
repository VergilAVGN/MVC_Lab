FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# system deps for Pillow and general builds
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libjpeg-dev \
       zlib1g-dev \
       gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# create directories for media/static when container runs (mounted in compose)
RUN mkdir -p /app/media /app/static

EXPOSE 8000

# Development entrypoint: run migrations then dev server
CMD ["bash", "-lc", "python manage.py migrate --noinput  && python manage.py runserver 0.0.0.0:8000"]
