#!/usr/bin/env python3
"""
代码质量检查脚本
运行: python linting.py
"""

import subprocess
import sys
import os

def run_command(command, description):
    """运行命令并处理结果"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*60)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            if result.stdout:
                print("Output:", result.stdout)
        else:
            print("❌ FAILED")
            if result.stderr:
                print("Error:", result.stderr)
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False
        
    return True

def main():
    """主函数"""
    print("开始代码质量检查...")
    
    # 检查Python文件
    python_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py") and not any(x in root for x in ['.git', '__pycache__', 'venv', '.pytest_cache']):
                python_files.append(os.path.join(root, file))
    
    all_passed = True
    
    if python_files:
        print(f"找到 {len(python_files)} 个Python文件进行检查")
        
        # 1. Black代码格式化检查
        black_check = f"python -m black --check {' '.join(python_files)}"
        if not run_command(black_check, "Black代码格式化检查"):
            print("💡 建议运行: black [文件] 来自动格式化代码")
            all_passed = False
        
        # 2. Flake8代码风格检查
        flake8_cmd = f"python -m flake8 {' '.join(python_files)} --max-line-length=88 --ignore=E203,W503,E501"
        if not run_command(flake8_cmd, "Flake8代码风格检查"):
            all_passed = False
        
        # 3. 简单的语法检查
        for py_file in python_files[:5]:  # 限制检查文件数量
            syntax_cmd = f"python -m py_compile {py_file}"
            if not run_command(syntax_cmd, f"语法检查: {py_file}"):
                all_passed = False
    
    # 4. 运行测试
    test_cmd = "cd backend && python -m pytest tests/ -v"
    if not run_command(test_cmd, "运行单元测试"):
        all_passed = False
    
    # 5. 安全检查（如果安装了safety）
    try:
        safety_cmd = "python -m safety check --json"
        run_command(safety_cmd, "依赖包安全检查")
    except:
        print("⚠️  Skipping safety check (safety not installed)")
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 所有代码质量检查通过!")
    else:
        print("❌ 部分检查未通过，请查看上面的输出")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())