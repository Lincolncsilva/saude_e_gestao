FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# Instalamos as deps e garantimos o uvicorn explicitamente
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uvicorn

COPY . .

ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]