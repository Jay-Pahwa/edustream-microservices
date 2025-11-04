FROM python:3.9-slim-bookworm
WORKDIR /app
COPY requirements.txt .

# Install build dependencies
RUN apt-get update && apt-get install -y default-libmysqlclient-dev gcc pkg-config \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- THIS IS THE CHANGE ---
# Copy the entire application, including templates/ and static/
COPY . .
# --- END OF CHANGE ---

EXPOSE 8082
CMD ["python", "app.py"]
