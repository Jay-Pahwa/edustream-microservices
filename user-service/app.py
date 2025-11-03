import os
from flask import Flask, jsonify, render_template
import MySQLdb

app = Flask(__name__)

# --- Configuration (Pulled from deployment environment) ---
DB_HOST = os.environ.get("DB_HOST", "edustream-database.c9kgo4igkbet.ap-south-1.rds.amazonaws.com")
DB_NAME = os.environ.get("DB_NAME", "edustream_db")
DB_USER = os.environ.get("DB_USER", "admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "As3jayaws")

def get_db_status():
    """Checks DB connection and returns a status string."""
    try:
        conn = MySQLdb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
        conn.close()
        return "UP"
    except Exception:
        return "DOWN"

@app.route('/')
def home():
    """Renders the main homepage (index.html)."""
    
    # We will simulate the video list for now
    # In a real app, you would fetch this from the database
    video_list = [
        {"title": "DevOps Overview", "description": "A quick intro to the principles of DevOps.", "id": 1},
        {"title": "Terraform in 5 Minutes", "description": "Learn the basics of Infrastructure as Code.", "id": 2}
    ]
    
    # Pass data to the HTML template
    return render_template('index.html', 
                           videos=video_list, 
                           db_host=DB_HOST)

@app.route('/api/status')
def status():
    """This is the ALB Health Check. Must return 200 OK."""
    return jsonify({"status": "UP", "service": "User/Metadata Service"}), 200

@app.route('/api/videos')
def get_videos():
    """This is the API endpoint to get video data."""
    # This simulates fetching from the DB
    video_list = [
        {"title": "DevOps Overview", "id": 1},
        {"title": "Terraform in 5 Minutes", "id": 2}
    ]
    return jsonify(video_list)

if __name__ == '__main__':
    # Runs on port 8082
    app.run(host='0.0.0.0', port=8082)