"""
DeepSeek API 测试脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.deepseek_service import deepseek_service

def test_deepseek_api():
    """测试 DeepSeek API"""
    print("=" * 60)
    print("  DeepSeek API 测试")
    print("=" * 60)
    
    # 测试 1: 简单对话
    print("\n[1] 测试简单对话...")
    try:
        response = deepseek_service.simple_chat("你好，请介绍一下智能巡检系统")
        print(f"✓ 对话成功")
        print(f"  回复: {response[:200]}...")
    except Exception as e:
        print(f"✗ 对话失败: {e}")
    
    # 测试 2: 环境数据分析
    print("\n[2] 测试环境数据分析...")
    try:
        result = deepseek_service.analyze_environment(25.5, 60.0, 30.0)
        print(f"✓ 分析成功")
        print(f"  状态: {result['status']}")
        print(f"  分析: {result['analysis'][:200]}...")
    except Exception as e:
        print(f"✗ 分析失败: {e}")
    
    # 测试 3: 自然语言查询
    print("\n[3] 测试自然语言查询...")
    try:
        result = deepseek_service.natural_language_query("如何提高巡检效率？")
        print(f"✓ 查询成功")
        print(f"  回答: {result['answer'][:200]}...")
    except Exception as e:
        print(f"✗ 查询失败: {e}")
    
    print("\n" + "=" * 60)
    print(" 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_deepseek_api()