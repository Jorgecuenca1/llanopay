FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /code-backend

# Install system dependencies for psycopg2 and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc libjpeg62-turbo-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code-backend/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /code-backend/
