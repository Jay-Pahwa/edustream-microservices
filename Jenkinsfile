pipeline {
    // 1. AGENT
    agent any

    // 2. ENVIRONMENT
    environment {
        AWS_ACCOUNT_ID = "570716071075"
        AWS_REGION     = "ap-south-1"
        
        // --- THIS IS THE FIX ---
        // Explicitly adding the path for the AWS CLI v2
        AWS_CLI_PATH   = "/usr/local/bin/aws"
    }

    // 3. STAGES
    stages {

        // --- STAGE 1: CHECKOUT ---
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        // --- STAGE 2: BUILD & PUSH USER-SERVICE ---
        stage('Build & Push User-Service') {
            steps {
                script {
                    def imageName = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/user-service:latest"
                    
                    dir('user-service') {
                        
                        echo "--- 1. Building Docker image: ${imageName} ---"
                        sh "docker build -t ${imageName} ."
                        
                        echo "--- 2. Logging into AWS ECR ---"
                        // We now use the $AWS_CLI_PATH variable
                        sh "${AWS_CLI_PATH} ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
                        
                        echo "--- 3. Pushing image to ECR ---"
                        sh "docker push ${imageName}"
                    }
                }
            }
        }

        // --- STAGE 3: BUILD & PUSH UPLOADER-SERVICE ---
        stage('Build & Push Uploader-Service') {
            steps {
                script {
                    def imageName = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/uploader-service:latest"
                    
                    dir('uploader-service') {
                        
                        echo "--- 1. Building Docker image: ${imageName} ---"
                        sh "docker build -t ${imageName} ."
                        
                        echo "--- 2. Logging into AWS ECR ---"
                        sh "${AWS_CLI_PATH} ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
                        
                        echo "--- 3. Pushing image to ECR ---"
                        sh "docker push ${imageName}"
                    }
                }
            }
        }

    }
}