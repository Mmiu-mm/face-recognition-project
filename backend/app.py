from flask import Flask, request, jsonify
from flask_cors import CORS
from face_recognition import FaceRecognitionSystem
from utils import base64_to_image
import os
from dotenv import load_dotenv
import mlflow
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
CORS(app)

# 初始化MLflow
mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
mlflow.set_experiment(os.getenv('MLFLOW_EXPERIMENT_NAME'))

# 初始化人脸识别系统
try:
    face_system = FaceRecognitionSystem()
    logger.info("Face recognition system initialized successfully")
    logger.info(f"Loaded {len(face_system.known_face_names)} known faces")
except Exception as e:
    logger.error(f"Failed to initialize face recognition system: {e}")
    face_system = None

@app.route('/')
def index():
    return jsonify({
        "message": "Face Recognition API", 
        "status": "running",
        "known_faces_count": len(face_system.known_face_names) if face_system else 0
    })

@app.route('/recognize', methods=['POST'])
def recognize_face():
    if not face_system:
        return jsonify({"error": "Face recognition system not initialized"}), 500
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({"error": "No image data provided"}), 400
        
        # 转换图像
        image = base64_to_image(image_data)
        if image is None:
            return jsonify({"error": "Invalid image data"}), 400
        
        # 记录到MLflow
        with mlflow.start_run(run_name="face_recognition"):
            mlflow.log_param("image_size", f"{image.shape[1]}x{image.shape[0]}")
            
            # 识别人脸
            results = face_system.recognize_face(image)
            
            mlflow.log_metric("faces_detected", len(results))
            known_faces_matched = len([r for r in results if r['name'] != 'Unknown'])
            mlflow.log_metric("known_faces_matched", known_faces_matched)
        
        return jsonify({
            "success": True,
            "results": results,
            "faces_detected": len(results)
        })
    
    except Exception as e:
        logger.error(f"Recognition error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/register', methods=['POST'])
def register_face():
    if not face_system:
        return jsonify({"error": "Face recognition system not initialized"}), 500
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        image_data = data.get('image')
        name = data.get('name')
        
        if not image_data or not name:
            return jsonify({"error": "Image data and name are required"}), 400
        
        # 转换图像
        image = base64_to_image(image_data)
        if image is None:
            return jsonify({"error": "Invalid image data"}), 400
        
        # 记录到MLflow
        with mlflow.start_run(run_name="face_registration"):
            mlflow.log_param("person_name", name)
            mlflow.log_param("image_size", f"{image.shape[1]}x{image.shape[0]}")
            
            # 注册人脸
            success = face_system.add_new_face(image, name)
            
            mlflow.log_metric("registration_success", int(success))
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Face registered successfully for {name}",
                "total_faces": len(face_system.known_face_names)
            })
        else:
            return jsonify({"error": "No face detected in the image"}), 400
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/status')
def status():
    if not face_system:
        return jsonify({"error": "Face recognition system not initialized"}), 500
        
    return jsonify({
        "known_faces": len(face_system.known_face_names),
        "face_names": face_system.known_face_names
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "face_system_ready": face_system is not None})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)