import pytest
import sys
import os
import numpy as np

# 添加backend目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from face_recognition import FaceRecognitionSystem

def test_encryption_decryption():
    """测试加密解密功能"""
    system = FaceRecognitionSystem()
    test_data = b"test data for encryption"
    
    encrypted = system.encrypt_data(test_data)
    decrypted = system.decrypt_data(encrypted)
    
    assert decrypted == test_data
    assert encrypted != test_data  # 确保数据确实被加密

def test_string_encryption():
    """测试字符串加密"""
    system = FaceRecognitionSystem()
    test_string = "test string"
    
    encrypted = system.encrypt_data(test_string)
    decrypted = system.decrypt_data(encrypted)
    
    assert decrypted.decode() == test_string

def test_numpy_encryption():
    """测试numpy数组加密"""
    system = FaceRecognitionSystem()
    test_array = np.array([1.0, 2.0, 3.0, 4.0])
    
    encrypted = system.encrypt_data(test_array)
    decrypted_bytes = system.decrypt_data(encrypted)
    decrypted_array = np.frombuffer(decrypted_bytes, dtype=test_array.dtype)
    
    assert np.array_equal(test_array, decrypted_array)

def test_system_initialization():
    """测试系统初始化"""
    system = FaceRecognitionSystem()
    assert system.known_faces_dir is not None
    assert system.unknown_faces_dir is not None
    assert hasattr(system, 'known_face_encodings')
    assert hasattr(system, 'known_face_names')