import pymysql
pymysql.install_as_MySQLdb()

import os
import boto3
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

# --- 1. App Initialization ---
app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Redirect to /login if user is not logged in

# --- 2. Configuration (Uses your Jenkins Env Vars) ---
DB_HOST = os.environ.get("DB_HOST", "edustream-database.c9kgo4igkbet.ap-south-1.rds.amazonaws.com")
DB_NAME = os.environ.get("DB_NAME", "edustream_db")
DB_USER = os.environ.get("DB_USER", "admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "As3jayaws")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "edustream-videos-jayal-1029")

# Generate a secret key (required for login sessions)
app.config['SECRET_KEY'] = 'a_very_secret_key_that_should_be_changed'
# Create the full database connection URI - CHANGED TO PYMYSQL
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

db = SQLAlchemy(app)
s3_client = boto3.client('s3', region_name='ap-south-1')


# --- 3. Database Models ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    image_url = db.Column(db.String(200))
    videos = db.relationship('Video', backref='subject', lazy=True)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    s3_key = db.Column(db.String(200), nullable=False) # The filename in S3
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- 4. Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'warning')
            return redirect(url_for('signup'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    """Renders the main homepage (index.html) with subjects."""
    subjects = Subject.query.all()
    return render_template('index.html', subjects=subjects)

@app.route('/subject/<int:subject_id>')
@login_required
def subject_page(subject_id):
    """Shows all videos for a specific subject."""
    subject = db.session.get(Subject, subject_id)
    return render_template('subject_page.html', subject=subject)

@app.route('/video/<int:video_id>')
@login_required
def video_player(video_id):
    """Shows the video player for a single video."""
    video = db.session.get(Video, video_id)
    
    # Generate a temporary, secure URL to stream the video from S3
    video_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': S3_BUCKET_NAME, 'Key': video.s3_key},
        ExpiresIn=3600  # URL is valid for 1 hour
    )
    
    return render_template('video_player.html', video=video, video_url=video_url)

@app.route('/api/status')
def status():
    """This is the ALB Health Check. Must return 200 OK."""
    return jsonify({"status": "UP", "service": "User/Metadata Service"}), 200

# --- 5. Create Database & Run App ---
if __name__ == '__main__':
    with app.app_context():
        # This creates all the tables (User, Subject, Video)
        db.create_all()
        
        # --- Add Sample Data (Only if it doesn't exist) ---
        if not Subject.query.first():
            print("Adding sample data...")
            # Create Subjects
            subject1 = Subject(name="Cloud Computing", description="Learn the fundamentals of AWS and cloud infrastructure.", image_url="https://placehold.co/600x400/007bff/white?text=Cloud")
            subject2 = Subject(name="DevOps", description="Explore CI/CD, Docker, and automation.", image_url="https://placehold.co/600x400/6f42c1/white?text=DevOps")
            db.session.add(subject1)
            db.session.add(subject2)
            db.session.commit() # Commit subjects so they get IDs

            # Create Videos
            video1 = Video(title="What is EC2?", s3_key="sample-video.mp4", subject_id=subject1.id)
            video2 = Video(title="What is S3?", s3_key="sample-video.mp4", subject_id=subject1.id)
            video3 = Video(title="What is Jenkins?", s3_key="sample-video.mp4", subject_id=subject2.id)
            video4 = Video(title="What is Docker?", s3_key="sample-video.mp4", subject_id=subject2.id)
            db.session.add(video1)
            db.session.add(video2)
            db.session.add(video3)
            db.session.add(video4)
            db.session.commit()
            
    app.run(host='0.0.0.0', port=8082)
```

## Key changes made:
1. **Line 1-2**: Added pymysql import and setup at the very top
2. **Line 27**: Changed `mysql+mysqlclient://` to `mysql+pymysql://`

Now also make sure your **requirements.txt** looks like this:
```
Flask
pymysql
cryptography
boto3
Flask-SQLAlchemy
Flask-Login
Flask-Bcrypt