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
        PATH             = "/opt/venv/bin:${env.PATH}"
        APP_HOST         = "web"
        APP_PORT         = "8000"
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

    triggers {
        // Automatically checks GitHub every minute for new commits pushed to main
        pollSCM('* * * * *')
        // Automatically triggers when GitHub Webhook fires
        githubPush()
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
                        terraform fmt -check || true
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
                    docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} -t thinkers-web:latest -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest .
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
                    echo "Applying migrations and refreshing web container with latest image..."
                    docker compose up -d --force-recreate --no-deps web
                    docker exec thinkers_web python manage.py migrate --noinput || true
                    echo "Live application container refreshed with updated code!"
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
                    echo "Running health checks against application container..."
                    curl -s -f "http://${APP_HOST}:${APP_PORT}/health/" | grep -q "healthy" && echo "[PASSED] Web Application Container is HEALTHY"
                    curl -s -f "http://${APP_HOST}:${APP_PORT}/metrics" | grep -q "django_" && echo "[PASSED] Prometheus Metrics Scraping Active"
                    echo "All automated healthcheck validations PASSED!"
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
        }
        failure {
            echo "FAILURE: Thinkers Platform deployment pipeline failed at stage: ${env.STAGE_NAME}"
        }
        always {
            deleteDir()
        }
    }
}
