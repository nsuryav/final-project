pipeline {
    agent any

    tools {
        python 'Python3'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/nsuryav/final-project.git'
            }
        }

        stage('Install dependencies') {
            steps {
                sh 'python -m venv venv'
                sh '. venv/bin/activate && pip install --upgrade pip'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh '. venv/bin/activate && pytest --maxfail=1 --disable-warnings -q --junitxml=test-results/results.xml'
            }
        }
    }

    post {
        always {
            junit '**/test-results/*.xml'
            archiveArtifacts artifacts: '**/reports/**', fingerprint: true
        }
        cleanup {
            echo 'Cleaning workspace...'
            cleanWs()   // Jenkins built-in step to wipe out workspace
            sh 'rm -rf venv __pycache__ .pytest_cache test-results reports || true'
        }
    }
}

