class FaceRecognitionApp {
    constructor() {
        this.video = document.getElementById('video');
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.isRecognizing = false;
        this.recognitionInterval = null;
        this.currentName = '';
        this.backendUrl = 'http://localhost:5000';
        
        this.initializeElements();
        this.initializeCamera();
        this.loadSystemInfo();
        
        // 定期更新系统信息
        setInterval(() => this.loadSystemInfo(), 10000);
    }

    initializeElements() {
        // 按钮事件监听
        document.getElementById('startBtn').addEventListener('click', () => this.startRecognition());
        document.getElementById('stopBtn').addEventListener('click', () => this.stopRecognition());
        document.getElementById('captureBtn').addEventListener('click', () => this.prepareRegistration());
        document.getElementById('registerBtn').addEventListener('click', () => this.registerFace());

        // 姓名输入
        document.getElementById('nameInput').addEventListener('input', (e) => {
            this.currentName = e.target.value.trim();
        });
        
        // 初始按钮状态
        document.getElementById('stopBtn').disabled = true;
    }

    async initializeCamera() {
        try {
            const constraints = { 
                video: { 
                    width: { ideal: 640 }, 
                    height: { ideal: 480 },
                    facingMode: "user"
                } 
            };
            
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = stream;
            
            // 等待视频加载
            this.video.onloadedmetadata = () => {
                this.updateStatus('摄像头已启动', 'success');
            };
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            this.updateStatus('无法访问摄像头: ' + error.message, 'error');
        }
    }

    updateStatus(message, type = 'info') {
        const statusElement = document.getElementById('status');
        statusElement.textContent = message;
        
        // 移除所有状态类
        statusElement.classList.remove('status-info', 'status-success', 'status-error');
        
        // 添加新状态类
        if (type === 'success') {
            statusElement.style.background = '#27ae60';
        } else if (type === 'error') {
            statusElement.style.background = '#e74c3c';
        } else {
            statusElement.style.background = '#3498db';
        }
    }

    async startRecognition() {
        if (this.isRecognizing) return;
        
        this.isRecognizing = true;
        this.updateStatus('人脸识别中...', 'success');
        
        // 更新按钮状态
        document.getElementById('startBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;
        document.getElementById('captureBtn').disabled = true;
        
        this.recognitionInterval = setInterval(() => {
            this.processFrame();
        }, 1000); // 每秒处理一帧
    }

    stopRecognition() {
        if (!this.isRecognizing) return;
        
        this.isRecognizing = false;
        clearInterval(this.recognitionInterval);
        this.updateStatus('识别已停止', 'info');
        
        // 更新按钮状态
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        document.getElementById('captureBtn').disabled = false;
        
        // 清空画布
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        document.getElementById('resultsContainer').innerHTML = '<div class="result-item">识别已停止</div>';
    }

    processFrame() {
        if (this.video.readyState !== this.video.HAVE_ENOUGH_DATA) {
            return;
        }
        
        // 绘制视频帧到canvas
        this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
        
        // 获取base64图像数据
        const imageData = this.canvas.toDataURL('image/jpeg', 0.8);
        
        // 发送识别请求
        this.sendRecognitionRequest(imageData);
    }

    async sendRecognitionRequest(imageData) {
        try {
            const response = await fetch(`${this.backendUrl}/recognize`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: imageData })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.displayResults(data.results);
                this.drawFaceBoxes(data.results);
            } else {
                this.updateStatus('识别失败: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Recognition error:', error);
            this.updateStatus('识别请求失败: ' + error.message, 'error');
        }
    }

    displayResults(results) {
        const container = document.getElementById('resultsContainer');
        container.innerHTML = '';

        if (results.length === 0) {
            container.innerHTML = '<div class="result-item">未检测到人脸</div>';
            return;
        }

        results.forEach(result => {
            const resultElement = document.createElement('div');
            const isUnknown = result.name === 'Unknown';
            resultElement.className = `result-item ${isUnknown ? 'unknown-face' : 'known-face'}`;
            
            const confidencePercent = (result.confidence * 100).toFixed(1);
            
            resultElement.innerHTML = `
                <strong>${result.name}</strong>
                <br>置信度: ${confidencePercent}%
                <br>位置: [${result.location[0]}, ${result.location[1]}, ${result.location[2]}, ${result.location[3]}]
            `;
            
            container.appendChild(resultElement);
        });
    }

    drawFaceBoxes(results) {
        // 清空上一帧的绘制
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
        
        results.forEach(result => {
            const [top, right, bottom, left] = result.location;
            const isUnknown = result.name === 'Unknown';
            
            // 绘制人脸框
            this.ctx.strokeStyle = isUnknown ? '#e74c3c' : '#27ae60';
            this.ctx.lineWidth = 3;
            this.ctx.strokeRect(left, top, right - left, bottom - top);
            
            // 绘制姓名标签背景
            this.ctx.fillStyle = isUnknown ? '#e74c3c' : '#27ae60';
            this.ctx.fillRect(left, top - 25, right - left, 25);
            
            // 绘制姓名和置信度
            this.ctx.fillStyle = 'white';
            this.ctx.font = '16px Arial';
            const confidencePercent = (result.confidence * 100).toFixed(1);
            this.ctx.fillText(
                `${result.name} (${confidencePercent}%)`, 
                left + 5, 
                top - 8
            );
        });
    }

    prepareRegistration() {
        if (this.isRecognizing) {
            this.updateStatus('请先停止识别再进行注册', 'error');
            return;
        }
        
        // 捕获当前帧用于注册
        this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
        
        const nameInput = document.getElementById('nameInput');
        nameInput.value = '';
        nameInput.focus();
        
        this.updateStatus('请输入姓名并点击确认注册', 'info');
    }

    async registerFace() {
        if (!this.currentName) {
            this.updateStatus('请输入姓名', 'error');
            return;
        }

        const imageData = this.canvas.toDataURL('image/jpeg', 0.8);
        
        try {
            this.updateStatus('注册中...', 'info');
            
            const response = await fetch(`${this.backendUrl}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: imageData,
                    name: this.currentName
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.updateStatus(`成功注册: ${this.currentName}`, 'success');
                this.loadSystemInfo(); // 更新系统信息
                document.getElementById('nameInput').value = '';
                this.currentName = '';
            } else {
                this.updateStatus('注册失败: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.updateStatus('注册请求失败: ' + error.message, 'error');
        }
    }

    async loadSystemInfo() {
        try {
            const response = await fetch(`${this.backendUrl}/status`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            document.getElementById('systemInfo').innerHTML = `
                已知人脸数量: ${data.known_faces}<br>
                已注册姓名: ${data.face_names.join(', ') || '无'}
            `;
        } catch (error) {
            console.error('Error loading system info:', error);
            document.getElementById('systemInfo').innerHTML = '无法连接到后端服务';
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new FaceRecognitionApp();
});