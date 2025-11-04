import pymysql
pymysql.install_as_MySQLdb()

import os
import boto3
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Environment variables
DB_HOST = os.environ.get("DB_HOST", "edustream-database.c9kgo4igkbet.ap-south-1.rds.amazonaws.com")
DB_NAME = os.environ.get("DB_NAME", "edustream_db")
DB_USER = os.environ.get("DB_USER", "admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "As3jayaws")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "edustream-videos-jayal-1029")

app.config['SECRET_KEY'] = 'edustream_secret_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Initialize AWS S3 client
try:
    s3_client = boto3.client('s3', region_name='ap-south-1')
    print("✅ S3 client initialized successfully")
except Exception as e:
    print(f"❌ S3 Client Error: {e}")
    s3_client = None

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
    s3_key = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
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
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    subjects = Subject.query.all()
    return render_template('index.html', subjects=subjects)

@app.route('/subject/<int:subject_id>')
@login_required
def subject_page(subject_id):
    subject = db.session.get(Subject, subject_id)
    if not subject:
        flash('Subject not found', 'danger')
        return redirect(url_for('home'))
    return render_template('subject_page.html', subject=subject)

@app.route('/video/<int:video_id>')
@login_required
def video_player(video_id):
    video = db.session.get(Video, video_id)
    if not video:
        flash('Video not found', 'danger')
        return redirect(url_for('home'))
    
    # Generate S3 presigned URL for the video
    try:
        video_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET_NAME, 
                'Key': video.s3_key,
                'ResponseContentType': 'video/mp4'
            },
            ExpiresIn=7200  # 2 hours
        )
        print(f"✅ Generated S3 URL for: {video.s3_key}")
        print(f"🔗 Video URL: {video_url}")
    except Exception as e:
        print(f"❌ Error generating video URL: {e}")
        flash('Error loading video. Please try again.', 'danger')
        video_url = None
    
    return render_template('video_player.html', video=video, video_url=video_url)

@app.route('/api/status')
def status():
    return jsonify({
        "status": "UP", 
        "service": "EduStream Video Service",
        "s3_bucket": S3_BUCKET_NAME
    }), 200

def create_sample_data():
    """Create sample subjects and videos that point to your S3 files"""
    try:
        # Only create if no subjects exist
        if not Subject.query.first():
            print("📦 Creating sample data...")
            
            # Create subjects
            cloud_subject = Subject(
                name="Cloud Computing", 
                description="Master AWS services, cloud architecture, and deployment strategies.", 
                image_url="https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&h=400&fit=crop"
            )
            
            devops_subject = Subject(
                name="DevOps", 
                description="Learn CI/CD pipelines, containerization, and infrastructure automation.", 
                image_url="https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=600&h=400&fit=crop"
            )
            
            db.session.add(cloud_subject)
            db.session.add(devops_subject)
            db.session.commit()
            
            # Create videos - USING YOUR EC2 VIDEO FOR ALL
            videos_data = [
                # Cloud Computing videos
                {"title": "AWS EC2 Tutorial", "s3_key": "aws-ec2-tutorial.mp4", "subject": cloud_subject},
                {"title": "Amazon S3 Deep Dive", "s3_key": "amazon-s3-deepdive.mp4", "subject": cloud_subject},
                
                # DevOps videos  
                {"title": "Jenkins CI/CD Pipeline", "s3_key": "jenkins-cicd-pipeline.mp4", "subject": devops_subject},
                {"title": "Docker Containerization", "s3_key": "docker-containerization.mp4", "subject": devops_subject}
            ]
            
            for video_data in videos_data:
                video = Video(
                    title=video_data["title"],
                    s3_key=video_data["s3_key"], 
                    subject_id=video_data["subject"].id
                )
                db.session.add(video)
            
            db.session.commit()
            print("✅ Sample data created successfully!")
            
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.session.rollback()

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            create_sample_data()
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            
    print("🚀 Starting EduStream server on port 8082...")
    app.run(host='0.0.0.0', port=8082, debug=True)