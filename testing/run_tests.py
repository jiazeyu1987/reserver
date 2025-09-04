#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试运行器
用于运行所有API接口测试
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 发现并运行所有测试
if __name__ == '__main__':
    # 创建测试套件
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 根据测试结果设置退出码
    sys.exit(0 if result.wasSuccessful() else 1)