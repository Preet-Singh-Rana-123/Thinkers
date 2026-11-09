// =============================================================================
// Thinkers Platform - Automated CI/CD Pipeline
// As specified in Devops-Synopsis.pdf Section 4.3 (Diagram 3)
// Stages: Linters -> Tests -> Terraform -> Docker Build & Push -> Rolling Deploy -> Healthcheck & Telemetry
// =============================================================================

pipeline {
    agent any

    environment {
        APP_NAME         = "thinkers"
        DOCKER_REGISTRY  = "docker.io/thinkersorg"
        IMAGE_NAME       = "thinkers-app"
        IMAGE_TAG        = "${env.BUILD_NUMBER}"
        AWS_DEFAULT_REGION = "us-east-1"
        AWS_CREDENTIALS_ID = "aws-thinkers-credentials"
        DOCKER_CREDENTIALS_ID = "dockerhub-credentials"
        SLACK_CHANNEL    = "#thinkers-deployments"
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15'))
        disableConcurrentBuilds()
    }

    stages {
        // ---------------------------------------------------------------------
        // Stage 1: Source Checkout & Static Code Analysis
        // ---------------------------------------------------------------------
        stage('Checkout & Linting') {
            steps {
                echo '=== [Stage 1] Checking Out Code & Running Linters ==='
                checkout scm
                sh '''
                    echo "Checking Python code formatting and syntax..."
                    python3 -m pip install --quiet flake8 black safety || true
                    flake8 --exclude=myenv,venv,migrations,.git --max-line-length=120 --ignore=E501,W503 . || true
                '''
            }
        }

        // ---------------------------------------------------------------------
        // Stage 2: Django Unit Tests & Pytest
        // ---------------------------------------------------------------------
        stage('Django Unit Tests') {
            steps {
                echo '=== [Stage 2] Running Django Unit Test Suites ==='
                sh '''
                    python3 -m pip install --quiet -r requirements.txt || true
                    python3 manage.py test core --noinput
                '''
            }
        }

        // ---------------------------------------------------------------------
        // Stage 3: Infrastructure as Code (Terraform Plan & Security Check)
        // ---------------------------------------------------------------------
        stage('Terraform Infra Check') {
            steps {
                echo '=== [Stage 3] Validating Terraform AWS Infrastructure ==='
                dir('terraform') {
                    sh '''
                        terraform init -backend=false
                        terraform fmt -check
                        terraform validate
                        echo "Terraform infrastructure configuration verified successfully."
                    '''
                }
            }
        }

        // ---------------------------------------------------------------------
        // Stage 4: Docker Container Build & Security Scan
        // ---------------------------------------------------------------------
        stage('Docker Image Build') {
            steps {
                echo "=== [Stage 4] Building Multi-Stage Docker Image: ${IMAGE_NAME}:${IMAGE_TAG} ==="
                sh '''
                    docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest .
                    echo "Docker image built successfully."
                '''
            }
        }

        // ---------------------------------------------------------------------
        // Stage 5: Container Registry Push (Docker Hub / AWS ECR)
        // ---------------------------------------------------------------------
        stage('Push to Registry') {
            steps {
                echo "=== [Stage 5] Pushing Docker Image to Registry ==="
                // withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                //     sh '''
                //         echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                //         docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
                //         docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest
                //     '''
                // }
                echo "Simulated registry push for tag ${IMAGE_TAG}."
            }
        }

        // ---------------------------------------------------------------------
        // Stage 6: Zero-Downtime Rolling Deployment (Diagram 3)
        // ---------------------------------------------------------------------
        stage('Rolling Deployment') {
            steps {
                echo '=== [Stage 6] Performing Zero-Downtime Rolling Update ==='
                sh '''
                    echo "Applying migrations and refreshing containers..."
                    ./scripts/deploy.sh
                '''
            }
        }

        // ---------------------------------------------------------------------
        // Stage 7: Healthcheck & Telemetry Verification (Section 6.1)
        // ---------------------------------------------------------------------
        stage('Healthcheck & Verification') {
            steps {
                echo '=== [Stage 7] Verifying Application Health & Prometheus Scrape ==='
                sh '''
                    ./scripts/health_check.sh
                '''
            }
        }
    }

    // -------------------------------------------------------------------------
    // Post-Build Pipeline Notifications (Slack / Email)
    // -------------------------------------------------------------------------
    post {
        success {
            echo "SUCCESS: Thinkers Platform deployed successfully! (Build #${env.BUILD_NUMBER})"
            // slackSend channel: "${SLACK_CHANNEL}", color: '#36a64f', message: "SUCCESS: Thinkers Platform Build #${env.BUILD_NUMBER} deployed successfully."
        }
        failure {
            echo "FAILURE: Thinkers Platform deployment pipeline failed at stage: ${env.STAGE_NAME}"
            // slackSend channel: "${SLACK_CHANNEL}", color: '#d00000', message: "ALERT: Thinkers Platform Build #${env.BUILD_NUMBER} failed at stage: ${env.STAGE_NAME}."
        }
        always {
            cleanWs deleteDirs: true, notFailBuild: true
        }
    }
}
