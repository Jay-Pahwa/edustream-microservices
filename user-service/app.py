import os
from flask import Flask, jsonify, render_template
import MySQLdb # Using MySQL client

app = Flask(__name__)

# --- Configuration (Pulled from deployment environment) ---

# 1. Look for an env variable named "DB_HOST".
# 2. If it's not found, use your RDS endpoint string as the default.
DB_HOST = os.environ.get("DB_HOST", "edustream-database.c9kgo4igkbet.ap-south-1.rds.amazonaws.com")

# 1. Look for "DB_NAME".
# 2. If not found, use "edustream_db" as the default.
DB_NAME = os.environ.get("DB_NAME", "edustream_db")

# 1. Look for "DB_USER".
# 2. If not found, use "admin" as the default.
DB_USER = os.environ.get("DB_USER", "admin")

# 1. Look for "DB_PASSWORD".
# 2. If not found, use your REAL password as the default.
DB_PASSWORD = os.environ.get("DB_PASSWORD", "As3jayaws")
@app.route('/')
def home():
    # This simulates fetching the video list from the database
    videos = [
        {"title": "DevOps Overview", "id": 1},
        {"title": "Terraform in 5 Minutes", "id": 2}
    ]
    
    # *** DEMO ONLY: You'd render a real HTML template here ***
    return f"""
    <html>
    <head><title>EduStream Lite</title></head>
    <body>
        <h1>Welcome to EduStream Lite</h1>
        <h2>Database Host: {DB_HOST}</h2>
        <p>This service retrieves video metadata (Title, ID) from the RDS database.</p>
        <p>Videos Loaded: {len(videos)}</p>
        <hr>
        <p>Try visiting: /api/status or /api/videos</p>
    </body>
    </html>
    """

@app.route('/api/status')
def status():
    # This is the dedicated health check endpoint.
    # It MUST return 200 OK to pass the ALB health check.
    return jsonify({"status": "UP", "service": "User/Metadata Service"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)