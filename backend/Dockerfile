FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update --allow-insecure-repositories --allow-unauthenticated 2>/dev/null || true \
    && apt-get install -y --no-install-recommends --allow-unauthenticated \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* || true

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]