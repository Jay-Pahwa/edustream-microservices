import os
import boto3
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Configuration (Pulled from deployment environment) ---
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "edustream-videos-jayal-1029")

@app.route('/')
def health_check():
    # This endpoint is just for the ALB health check
    return jsonify({"status": "UP", "service": "Uploader Service"}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    video_file = request.files['file']
    filename = video_file.filename
    
    # Simulate the S3 Upload
    s3_client = boto3.client('s3')
    
    try:
        # In a real app, you would stream the file, but here we simulate success
        # s3_client.upload_fileobj(video_file, S3_BUCKET_NAME, filename)
        
        # --- Simulate Triggering Thumbnail Generation ---
        # (This will be the Lambda function in the final deployment)
        
        return jsonify({
            "message": f"File '{filename}' simulated upload success.",
            "storage_location": f"s3://{S3_BUCKET_NAME}/{filename}"
        }), 200

    except Exception as e:
        return jsonify({"message": f"Upload failed: {str(e)}"}), 500


if __name__ == '__main__':
    # Run on a different port than the User Service
    app.run(host='0.0.0.0', port=8081)