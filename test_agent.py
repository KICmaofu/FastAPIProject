"""
智能体模块测试脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.agent_service import agent_service
from app.config.database import get_db

def test_agent_service():
    """测试智能体服务"""
    print("=" * 60)
    print("  智能体模块测试")
    print("=" * 60)
    
    # 获取数据库会话
    db = next(get_db())
    
    # 测试 1: 获取智能体状态
    print("\n[1] 测试智能体综合状态...")
    try:
        status = agent_service.get_agent_status()
        print(f"✓ 状态获取成功")
        print(f"  数据库状态: {status['database']['status']}")
        print(f"  待处理告警数: {status['alarmCount']}")
    except Exception as e:
        print(f"✗ 状态获取失败: {e}")
    
    # 测试 2: 获取数据库连接状态
    print("\n[2] 测试数据库连接状态...")
    try:
        db_status = agent_service.get_database_connection_status()
        print(f"✓ 数据库状态获取成功")
        print(f"  连接状态: {db_status['status']}")
        print(f"  数据库: {db_status.get('database', 'N/A')}")
    except Exception as e:
        print(f"✗ 数据库状态获取失败: {e}")
    
    # 测试 3: 获取系统资源指标
    print("\n[3] 测试系统资源指标...")
    try:
        metrics = agent_service.get_system_metrics()
        print(f"✓ 系统指标获取成功")
        print(f"  CPU使用率: {metrics['cpu']['usagePercent']}%")
        print(f"  内存使用率: {metrics['memory']['usagePercent']}%")
        print(f"  磁盘使用率: {metrics['disk']['usagePercent']}%")
    except Exception as e:
        print(f"✗ 系统指标获取失败: {e}")
    
    # 测试 4: 获取业务指标
    print("\n[4] 测试业务指标...")
    try:
        business_metrics = agent_service.get_business_metrics(db)
        print(f"✓ 业务指标获取成功")
        print(f"  设备总数: {business_metrics.get('deviceCount', 0)}")
        print(f"  告警总数: {business_metrics.get('alertCount', 0)}")
        print(f"  传感器数据量: {business_metrics.get('sensorDataCount', 0)}")
    except Exception as e:
        print(f"✗ 业务指标获取失败: {e}")
    
    # 测试 5: 执行数据库查询
    print("\n[5] 测试数据库查询...")
    try:
        result = agent_service.execute_query_analysis(db, {"query": "SELECT COUNT(*) as count FROM users"})
        print(f"✓ 查询执行成功")
        print(f"  查询结果: {result}")
    except Exception as e:
        print(f"✗ 查询执行失败: {e}")
    
    # 测试 6: 自然语言查询
    print("\n[6] 测试自然语言查询...")
    try:
        result = agent_service.natural_language_query("有多少个设备", db)
        print(f"✓ 自然语言查询成功")
        print(f"  用户查询: {result['originalQuery']}")
        print(f"  识别意图: {result['intent']}")
        print(f"  自然语言回复: {result['naturalResponse'][:100]}...")
    except Exception as e:
        print(f"✗ 自然语言查询失败: {e}")
    
    # 测试 7: 生成AI分析洞察
    print("\n[7] 测试AI分析洞察...")
    try:
        result = agent_service.generate_ai_insights(db, {})
        print(f"✓ AI分析完成")
        print(f"  业务指标: 设备数={result['businessMetrics'].get('deviceCount', 0)}, 告警数={result['businessMetrics'].get('alertCount', 0)}")
        print(f"  AI建议: {result['aiInsights'][:200]}...")
    except Exception as e:
        print(f"✗ AI分析失败: {e}")
    
    # 测试 8: 任务队列管理
    print("\n[8] 测试任务队列...")
    try:
        task_id = agent_service.add_task("business_metrics", {})
        print(f"✓ 任务创建成功: {task_id}")
        
        queue = agent_service.get_task_queue()
        print(f"✓ 任务队列获取成功")
        print(f"  待处理任务: {len(queue['pending'])}")
        print(f"  处理中任务: {len(queue['processing'])}")
        print(f"  已完成任务: {len(queue['completed'])}")
    except Exception as e:
        print(f"✗ 任务队列测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("  智能体模块测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_agent_service()