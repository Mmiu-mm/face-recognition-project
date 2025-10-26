import pytest
import sys
import os
import json

# 添加backend目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    """测试首页"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert data['status'] == 'running'

def test_status(client):
    """测试状态端点"""
    response = client.get('/status')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'known_faces' in data
    assert 'face_names' in data

def test_health_check(client):
    """测试健康检查"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data

def test_recognize_no_data(client):
    """测试无数据的人脸识别"""
    response = client.post('/recognize', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_register_no_data(client):
    """测试无数据的人脸注册"""
    response = client.post('/register', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_register_missing_name(client):
    """测试缺少姓名的注册"""
    response = client.post('/register', json={'image': 'test'})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_register_missing_image(client):
    """测试缺少图像的注册"""
    response = client.post('/register', json={'name': 'test'})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data