FROM python:3.9-slim-bookworm
WORKDIR /app
COPY requirements.txt .

# Install build dependencies
RUN apt-get update && apt-get install -y default-libmysqlclient-dev gcc pkg-config \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- THIS IS THE CHANGE ---
# Copy the app code AND the new templates folder
COPY app.py .
COPY templates/ ./templates/
# --- END OF CHANGE ---

EXPOSE 8082
CMD ["python", "app.py"]