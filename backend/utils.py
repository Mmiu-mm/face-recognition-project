import cv2
import base64
import numpy as np
from PIL import Image
import io

def base64_to_image(base64_string):
    """将base64字符串转换为OpenCV图像"""
    try:
        # 移除数据URL前缀（如果存在）
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # 解码base64
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        
        # 转换为OpenCV格式
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        return opencv_image
    except Exception as e:
        print(f"Error converting base64 to image: {e}")
        return None

def image_to_base64(image):
    """将OpenCV图像转换为base64字符串"""
    try:
        # 转换颜色空间
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # 转换为base64
        buffered = io.BytesIO()
        pil_image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/jpeg;base64,{img_str}"
    except Exception as e:
        print(f"Error converting image to base64: {e}")
        return None

def generate_encryption_key():
    """生成加密密钥"""
    from cryptography.fernet import Fernet
    return Fernet.generate_key().decode()

if __name__ == "__main__":
    # 生成加密密钥
    key = generate_encryption_key()
    print(f"Generated encryption key: {key}")
    print("请将此密钥复制到.env文件的ENCRYPTION_KEY中")