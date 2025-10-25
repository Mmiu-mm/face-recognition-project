#!/bin/bash

echo "创建项目目录结构..."

# 创建主要目录
mkdir -p .github/workflows
mkdir -p backend/models backend/tests
mkdir -p frontend
mkdir -p data/known_faces data/unknown_faces
mkdir -p mlflow/tracking

# 创建后端文件
touch backend/app.py backend/face_recognition.py backend/utils.py
touch backend/requirements.txt backend/Dockerfile
touch backend/tests/test_app.py backend/tests/test_face_recognition.py

# 创建前端文件
touch frontend/index.html frontend/style.css frontend/script.js frontend/Dockerfile

# 创建配置和文档文件
touch .env.example .gitignore docker-compose.yml requirements.txt
touch linting.py mlflow_tracking.py README.md

# 创建CI/CD工作流文件
touch .github/workflows/ci-cd.yml

# 创建空文件保持目录结构
touch data/known_faces/.gitkeep
touch data/unknown_faces/.gitkeep

echo "项目结构创建完成!"
