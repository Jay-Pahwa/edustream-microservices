FROM python:3.9-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application, including templates/ and static/
COPY . .

EXPOSE 8082

CMD ["python", "app.py"]
```

### Step 2: Update requirements.txt

Replace `mysqlclient` with `pymysql`:
```
Flask
pymysql
cryptography
boto3
Flask-SQLAlchemy
Flask-Login
Flask-Bcrypt