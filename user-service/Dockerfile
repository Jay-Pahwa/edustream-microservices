FROM python:3.9-slim-bookworm
WORKDIR /app
COPY requirements.txt .
# Need to install MySQL client development headers
RUN apt-get update && apt-get install -y default-libmysqlclient-dev gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY app.py .
EXPOSE 8080
CMD ["python", "app.py"]