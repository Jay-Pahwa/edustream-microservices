pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "570716071075"
        AWS_REGION     = "ap-south-1"
        AWS_CLI_PATH   = "/usr/bin/aws"

        // --- DB & S3 Secrets ---
        // We pass these to the 'docker run' command
        DB_HOST        = "edustream-database.c9kgo4igkbet.ap-south-1.rds.amazonaws.com"
        DB_NAME        = "edustream_db"
        DB_USER        = "admin"
        DB_PASSWORD    = "As3jayaws" // <-- CRITICAL: PUT YOUR NEW, SECURE PASSWORD HERE
        S3_BUCKET_NAME = "edustream-videos-jayal-1029"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        // --- BUILD USER-SERVICE ---
        stage('Build User-Service') {
            steps {
                script {
                    def imageName = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/user-service:latest"
                    dir('user-service') {
                        sh "docker build -t ${imageName} ."
                    }
                }
            }
        }

        // --- BUILD UPLOADER-SERVICE ---
        stage('Build Uploader-Service') {
            steps {
                script {
                    def imageName = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/uploader-service:latest"
                    dir('uploader-service') {
                        sh "docker build -t ${imageName} ."
                    }
                }
            }
        }

        // --- LOGIN & PUSH ALL IMAGES ---
        stage('Login & Push to ECR') {
            steps {
                echo "--- Logging into AWS ECR ---"
                sh "${AWS_CLI_PATH} ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

                echo "--- Pushing User-Service ---"
                sh "docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/user-service:latest"

                echo "--- Pushing Uploader-Service ---"
                sh "docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/uploader-service:latest"
            }
        }

        // --- DEPLOY! ---
        stage('Deploy Services') {
            steps {
                echo "--- Deploying User-Service on port 8082 ---"
                // 1. Stop the old container (if it exists)
                sh "docker stop user-service || true"
                sh "docker rm user-service || true"

                // 2. Run the new container
                sh """
                docker run -d --name user-service -p 8082:8082 \
                  -e DB_HOST="${DB_HOST}" \
                  -e DB_NAME="${DB_NAME}" \
                  -e DB_USER="${DB_USER}" \
                  -e DB_PASSWORD="${DB_PASSWORD}" \
                  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/user-service:latest
                """

                echo "--- Deploying Uploader-Service on port 8081 ---"
                // 1. Stop the old container
                sh "docker stop uploader-service || true"
                sh "docker rm uploader-service || true"

                // 2. Run the new container
                sh """
                docker run -d --name uploader-service -p 8081:8081 \
                  -e S3_BUCKET_NAME="${S3_BUCKET_NAME}" \
                  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/uploader-service:latest
                """
            }
        }
    }
}