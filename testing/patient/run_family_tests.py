#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
家庭档案管理API测试套件运行器
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_family_tests():
    """运行家庭档案相关的所有测试"""
    
    # 导入测试模块
    from test_family_crud import FamilyTestCase
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加家庭CRUD测试
    suite.addTest(unittest.makeSuite(FamilyTestCase))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果统计
    print("\n" + "="*50)
    print("测试结果统计:")
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    print("="*50)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_family_tests()
    sys.exit(0 if success else 1)