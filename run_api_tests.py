#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的测试运行脚本
用于快速运行API接口测试
"""

import subprocess
import sys
import os

def run_tests():
    """运行所有API测试"""
    print("开始运行API接口测试...")
    
    # 获取testing目录的绝对路径
    testing_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testing')
    
    # 运行测试
    try:
        result = subprocess.run([
            sys.executable, 
            os.path.join(testing_dir, 'run_tests.py')
        ], cwd=testing_dir, capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"运行测试时出错: {e}")
        return False

def run_single_test(test_name):
    """运行单个测试文件"""
    print(f"开始运行 {test_name} 测试...")
    
    # 获取testing目录的绝对路径
    testing_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testing')
    
    # 检查测试文件是否存在
    test_file = os.path.join(testing_dir, test_name)
    if not os.path.exists(test_file):
        print(f"测试文件 {test_name} 不存在")
        return False
    
    # 运行单个测试
    try:
        result = subprocess.run([
            sys.executable, 
            test_file
        ], cwd=testing_dir, capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"运行测试时出错: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 运行指定的测试文件
        test_name = sys.argv[1]
        success = run_single_test(test_name)
    else:
        # 运行所有测试
        success = run_tests()
    
    if success:
        print("所有测试运行完成!")
        sys.exit(0)
    else:
        print("测试运行失败!")
        sys.exit(1)