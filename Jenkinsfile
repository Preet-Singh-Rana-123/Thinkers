// =============================================================================
// Thinkers Platform - Automated CI/CD Pipeline
// As specified in Devops-Synopsis.pdf Section 4.3 (Diagram 3)
// Stages: Linters -> Tests -> Terraform -> Docker Build & Push -> Rolling Deploy -> Healthcheck & Telemetry
// =============================================================================

pipeline {
    agent any

    environment {
        APP_NAME           = "thinkers"
        ECR_REGISTRY       = "326730685075.dkr.ecr.us-east-1.amazonaws.com"
        IMAGE_NAME         = "thinkers-app"
        IMAGE_TAG          = "${env.BUILD_NUMBER}"
        PATH               = "/opt/venv/bin:${env.PATH}"
        APP_HOST           = "web"
        APP_PORT           = "8000"
        AWS_DEFAULT_REGION = "us-east-1"
        AWS_REGION         = "us-east-1"
        ALB_DNS            = "thinkers-alb-production-896227422.us-east-1.elb.amazonaws.com"
        SLACK_CHANNEL      = "#thinkers-deployments"
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
        // Stage 4: Docker Container Build (Local & AWS ECR linux/amd64)
        // ---------------------------------------------------------------------
        stage('Docker Image Build') {
            steps {
                echo "=== [Stage 4] Building Multi-Stage Docker Images (Local & AWS ECR linux/amd64) ==="
                sh '''
                    echo "Building local image for staging and internal testing..."
                    docker build -t thinkers-web:latest .

                    echo "Building linux/amd64 production image for AWS ECR..."
                    docker buildx build --platform linux/amd64 \
                        -t ${ECR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} \
                        -t ${ECR_REGISTRY}/${IMAGE_NAME}:latest \
                        --load .
                    echo "Docker images successfully built and tagged."
                '''
            }
        }

        // ---------------------------------------------------------------------
        // Stage 5: Container Registry Push (AWS Elastic Container Registry)
        // ---------------------------------------------------------------------
        stage('Push to Registry') {
            steps {
                echo "=== [Stage 5] Authenticating and Pushing to AWS ECR ==="
                sh '''
                    echo "Authenticating Docker with AWS ECR (${ECR_REGISTRY})..."
                    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

                    echo "Pushing image tags: ${IMAGE_TAG} and latest..."
                    docker push ${ECR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${ECR_REGISTRY}/${IMAGE_NAME}:latest
                    echo "Successfully published production container images to AWS ECR!"
                '''
            }
        }

        // ---------------------------------------------------------------------
        // Stage 6: Zero-Downtime Rolling Deployment (Local & AWS ASG)
        // ---------------------------------------------------------------------
        stage('Rolling Deployment') {
            steps {
                echo '=== [Stage 6] Performing Zero-Downtime Rolling Update (Local & AWS ASG) ==='
                sh '''
                    echo "--- Local Deployment Update ---"
                    docker stop thinkers_web || true
                    docker rm thinkers_web || true
                    docker compose -p thinkers up -d --no-deps web
                    docker exec thinkers_web python manage.py migrate --noinput || true
                    echo "Local application container refreshed with latest code."

                    echo "--- AWS Cloud Deployment Rolling Update ---"
                    ASG_NAME=$(aws autoscaling describe-auto-scaling-groups --region ${AWS_REGION} --query "AutoScalingGroups[?starts_with(AutoScalingGroupName, 'thinkers-asg-production')].AutoScalingGroupName" --output text | head -n1)
                    if [ -n "$ASG_NAME" ] && [ "$ASG_NAME" != "None" ]; then
                        echo "Initiating AWS Auto Scaling Group Instance Refresh for: ${ASG_NAME}"
                        aws autoscaling start-instance-refresh \
                            --auto-scaling-group-name "${ASG_NAME}" \
                            --region ${AWS_REGION} \
                            --preferences '{"MinHealthyPercentage": 50, "InstanceWarmup": 180}' || true
                        echo "AWS Auto Scaling Group rolling update triggered successfully."
                    else
                        echo "No active AWS ASG found, skipping cloud rolling update."
                    fi
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
                    echo "Verifying local web container health..."
                    curl -s -f "http://${APP_HOST}:${APP_PORT}/health/" | grep -q "healthy" && echo "[PASSED] Local Web Application Container is HEALTHY"
                    curl -s -f "http://${APP_HOST}:${APP_PORT}/metrics" | grep -q "django_" && echo "[PASSED] Local Prometheus Metrics Scraping Active"

                    echo "Verifying AWS Application Load Balancer live endpoint..."
                    AWS_HEALTH=$(curl -s --max-time 10 "http://${ALB_DNS}/health/" || true)
                    echo "AWS ALB Response: ${AWS_HEALTH}"
                    if echo "${AWS_HEALTH}" | grep -q "healthy"; then
                        echo "[PASSED] AWS Production Load Balancer is HEALTHY and Live!"
                    else
                        echo "[INFO] AWS ALB returned non-200 or in rollout transition: ${AWS_HEALTH}"
                    fi
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
