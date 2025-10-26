import face_recognition
import cv2
import numpy as np
import os
from cryptography.fernet import Fernet
import pickle
from dotenv import load_dotenv
import base64

load_dotenv()

class FaceRecognitionSystem:
    def __init__(self):
        self.known_faces_dir = os.getenv('KNOWN_FACES_DIR', './data/known_faces')
        self.unknown_faces_dir = os.getenv('UNKNOWN_FACES_DIR', './data/unknown_faces')
        
        # 加密配置
        encryption_key = os.getenv('ENCRYPTION_KEY')
        if not encryption_key or encryption_key == 'your-32-character-encryption-key-here':
            # 生成一个临时密钥用于开发
            encryption_key = Fernet.generate_key().decode()
        self.encryption_key = encryption_key.encode()
        self.cipher = Fernet(self.encryption_key)
        
        self.known_face_encodings = []
        self.known_face_names = []
        
        self.load_known_faces()
    
    def encrypt_data(self, data):
        """加密数据"""
        if isinstance(data, np.ndarray):
            data = data.tobytes()
        elif isinstance(data, str):
            data = data.encode()
        return self.cipher.encrypt(data)
    
    def decrypt_data(self, encrypted_data):
        """解密数据"""
        decrypted = self.cipher.decrypt(encrypted_data)
        return decrypted
    
    def load_known_faces(self):
        """加载已知人脸"""
        if not os.path.exists(self.known_faces_dir):
            os.makedirs(self.known_faces_dir)
        
        for filename in os.listdir(self.known_faces_dir):
            if filename.endswith('.encrypted'):
                try:
                    # 解密文件
                    with open(os.path.join(self.known_faces_dir, filename), 'rb') as f:
                        encrypted_data = f.read()
                    
                    decrypted_data = self.decrypt_data(encrypted_data)
                    face_data = pickle.loads(decrypted_data)
                    
                    self.known_face_encodings.append(face_data['encoding'])
                    self.known_face_names.append(face_data['name'])
                    
                    print(f"Loaded face: {face_data['name']}")
                    
                except Exception as e:
                    print(f"Error loading face {filename}: {e}")
    
    def save_face(self, face_encoding, name):
        """保存人脸数据（加密）"""
        face_data = {
            'encoding': face_encoding,
            'name': name
        }
        
        # 序列化并加密数据
        serialized_data = pickle.dumps(face_data)
        encrypted_data = self.encrypt_data(serialized_data)
        
        # 保存加密文件
        filename = f"{name}_{len(self.known_face_names)}.encrypted"
        filepath = os.path.join(self.known_faces_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(encrypted_data)
        
        # 更新内存中的数据
        self.known_face_encodings.append(face_encoding)
        self.known_face_names.append(name)
        
        print(f"Saved face: {name}")
    
    def recognize_face(self, image):
        """识别人脸"""
        # 转换图像格式
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 检测人脸
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        results = []
        
        for face_encoding, face_location in zip(face_encodings, face_locations):
            # 比较人脸
            matches = face_recognition.compare_faces(
                self.known_face_encodings, 
                face_encoding,
                tolerance=float(os.getenv('DISTANCE_THRESHOLD', 0.6))
            )
            
            name = "Unknown"
            confidence = 0
            
            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_face_names[first_match_index]
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings, 
                    face_encoding
                )
                best_match_index = np.argmin(face_distances)
                confidence = 1 - face_distances[best_match_index]
            else:
                # 如果没有匹配，计算与最近人脸的置信度
                if len(self.known_face_encodings) > 0:
                    face_distances = face_recognition.face_distance(
                        self.known_face_encodings, 
                        face_encoding
                    )
                    confidence = 1 - np.min(face_distances)
            
            results.append({
                'name': name,
                'confidence': float(confidence),
                'location': face_location
            })
        
        return results
    
    def add_new_face(self, image, name):
        """添加新人脸"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(rgb_image)
        
        if len(face_encodings) > 0:
            self.save_face(face_encodings[0], name)
            return True
        return False