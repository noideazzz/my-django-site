#!/usr/bin/env python
import os
import sys
import subprocess

# 设置Django环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject2.settings')

# 启动服务器的命令
command = [sys.executable, 'manage.py', 'runserver', '8080']

# 执行命令并捕获输出
try:
    print("Starting Django server...")
    process = subprocess.Popen(
        command,
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 读取输出
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    
    # 读取错误输出
    error_output = process.stderr.read()
    if error_output:
        print("Error output:")
        print(error_output)
        
except Exception as e:
    print(f"Error starting server: {e}")
