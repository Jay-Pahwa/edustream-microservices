pipeline {
    // 1. AGENT
    // Run this pipeline on any available agent
    agent any

    // 2. ENVIRONMENT
    // Set global variables for our pipeline
    environment {
        AWS_ACCOUNT_ID = "570716071075"
        AWS_REGION     = "ap-south-1"
    }

    // 3. STAGES
    // Define the sequence of steps
    stages {

        // --- STAGE 1: CHECKOUT ---
        stage('Checkout Code') {
            steps {
                // This command pulls the code from the Git repository
                // that this Jenkins job is linked to.
                checkout scm
            }
        }

        // --- STAGE 2: BUILD & PUSH USER-SERVICE ---
        stage('Build & Push User-Service') {
            steps {
                script {
                    // Define the full name for our ECR image
                    def imageName = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/user-service:latest"
                    
                    // 'dir' changes directory into our microservice folder
                    dir('user-service') {
                        
                        echo "--- 1. Building Docker image: ${imageName} ---"
                        sh "docker build -t ${imageName} ."
                        
                        echo "--- 2. Logging into AWS ECR ---"
                        // This command uses the EC2's IAM Role automatically!
                        sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
                        
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
                    // Define the full name for our ECR image
                    def imageName = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/uploader-service:latest"
                    
                    dir('uploader-service') {
                        
                        echo "--- 1. Building Docker image: ${imageName} ---"
                        sh "docker build -t ${imageName} ."
                        
                        echo "--- 2. Logging into AWS ECR ---"
                        // We log in again, just to be safe
                        sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
                        
                        echo "--- 3. Pushing image to ECR ---"
                        sh "docker push ${imageName}"
                    }
                }
            }
        }

    }
}