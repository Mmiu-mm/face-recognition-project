#!/usr/bin/env python3
"""
MLflow实验跟踪示例
运行: python mlflow_tracking.py
"""

import mlflow
import mlflow.sklearn
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import os
from dotenv import load_dotenv

load_dotenv()

def create_sample_data():
    """创建示例人脸识别数据"""
    np.random.seed(42)
    # 模拟人脸特征数据（128维，类似于FaceNet输出）
    n_samples = 1000
    n_features = 128
    
    X = np.random.randn(n_samples, n_features)
    # 创建简单的分类任务：基于前两个特征的组合
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    return X, y

def main():
    """主函数"""
    # 设置MLflow
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
    mlflow.set_experiment("face_recognition_demo")
    
    print("生成示例数据...")
    X, y = create_sample_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"训练数据: {X_train.shape}, 测试数据: {X_test.shape}")
    
    # 定义不同的参数进行实验
    param_combinations = [
        {'n_estimators': 50, 'max_depth': 5, 'criterion': 'gini'},
        {'n_estimators': 100, 'max_depth': 10, 'criterion': 'gini'},
        {'n_estimators': 200, 'max_depth': 15, 'criterion': 'entropy'},
        {'n_estimators': 150, 'max_depth': 8, 'criterion': 'gini'}
    ]
    
    best_accuracy = 0
    best_params = None
    
    for i, params in enumerate(param_combinations):
        run_name = f"rf_experiment_{i+1}"
        print(f"\n开始实验 {i+1}: {params}")
        
        with mlflow.start_run(run_name=run_name):
            # 记录参数
            mlflow.log_params(params)
            
            # 训练模型
            model = RandomForestClassifier(**params, random_state=42)
            model.fit(X_train, y_train)
            
            # 预测和评估
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # 记录指标
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("train_samples", len(X_train))
            mlflow.log_metric("test_samples", len(X_test))
            
            # 记录模型
            mlflow.sklearn.log_model(model, "random_forest_model")
            
            # 记录分类报告
            report = classification_report(y_test, y_pred, output_dict=True)
            for label, metrics in report.items():
                if isinstance(metrics, dict):
                    for metric, value in metrics.items():
                        mlflow.log_metric(f"{label}_{metric}", value)
            
            print(f"实验 {i+1} 完成 - 准确率: {accuracy:.4f}")
            
            # 更新最佳结果
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_params = params
    
    print(f"\n{'='*50}")
    print("所有实验完成!")
    print(f"最佳准确率: {best_accuracy:.4f}")
    print(f"最佳参数: {best_params}")
    print(f"MLflow跟踪URI: {os.getenv('MLFLOW_TRACKING_URI')}")
    print("="*50)

if __name__ == "__main__":
    main()