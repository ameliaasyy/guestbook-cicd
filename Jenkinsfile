pipeline {
    agent any
    triggers { githubPush() }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Syntax Check') {
            steps { sh 'python3 -m py_compile backend/app.py' }
        }
        stage('Build Image') {
            steps { sh 'docker compose build' }
        }
        stage('Automated Deployment') {
            steps { sh 'docker compose up -d --remove-orphans' }
        }
        stage('Health Check') {
            steps {
                sh '''
                for i in $(seq 1 10); do
                  curl -sf http://localhost:5001/messages && exit 0
                  sleep 3
                done
                exit 1
                '''
            }
        }
    }
    post {
        failure { sh 'docker compose logs --tail=50 || true' }
    }
}
