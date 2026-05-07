#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试日历显示功能 - 验证添加课程后是否正确显示
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject2.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client, override_settings
from django.contrib.auth import get_user_model
from blog.models import CalendarEvent
import json

User = get_user_model()


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_calendar_display():
    """测试日历显示功能"""
    client = Client()
    
    print("=" * 80)
    print("日历显示功能测试")
    print("=" * 80)
    
    # 创建测试用户并登录
    print("\n1. 准备测试环境...")
    try:
        user = User.objects.create_user(
            username='calendartest',
            email='calendar@test.com',
            password='testpass123'
        )
    except:
        user = User.objects.get(username='calendartest')
    
    client.login(username='calendartest', password='testpass123')
    print("   测试用户准备完成")
    
    # 清理旧数据
    CalendarEvent.objects.filter(user=user).delete()
    
    # 2. 测试参数格式 - 新格式 year=2024&month=12
    print("\n2. 测试参数格式 - 新格式 (year=2024&month=12)")
    
    # 添加2024年12月的课程
    event_dec = CalendarEvent.objects.create(
        user=user,
        title='12月电磁场课',
        date='2024-12-15',
        time='08:00',
        location='A301',
        event_type='theory'
    )
    
    # 使用新格式获取
    response = client.get('/api/calendar/events/?year=2024&month=12')
    data = json.loads(response.content)
    print(f"   请求: year=2024&month=12")
    print(f"   状态码: {response.status_code}")
    print(f"   返回事件数: {len(data.get('events', []))}")
    
    assert response.status_code == 200
    assert data.get('success') == True
    assert len(data.get('events', [])) == 1
    assert data['events'][0]['title'] == '12月电磁场课'
    print("   [OK] 新格式参数测试通过")
    
    # 3. 测试参数格式 - 旧格式 month=2024-12
    print("\n3. 测试参数格式 - 旧格式 (month=2024-12)")
    response = client.get('/api/calendar/events/?month=2024-12')
    data = json.loads(response.content)
    print(f"   请求: month=2024-12")
    print(f"   状态码: {response.status_code}")
    print(f"   返回事件数: {len(data.get('events', []))}")
    
    assert len(data.get('events', [])) == 1
    print("   [OK] 旧格式参数测试通过（向后兼容）")
    
    # 4. 测试跨年份过滤
    print("\n4. 测试跨年份过滤")
    
    # 添加2025年1月的课程
    event_jan = CalendarEvent.objects.create(
        user=user,
        title='1月微波工程课',
        date='2025-01-20',
        time='10:00',
        location='B205',
        event_type='lab'
    )
    
    # 查询2024年12月
    response = client.get('/api/calendar/events/?year=2024&month=12')
    data = json.loads(response.content)
    print(f"   查询2024年12月，返回事件数: {len(data.get('events', []))}")
    assert len(data.get('events', [])) == 1
    assert data['events'][0]['title'] == '12月电磁场课'
    
    # 查询2025年1月
    response = client.get('/api/calendar/events/?year=2025&month=1')
    data = json.loads(response.content)
    print(f"   查询2025年1月，返回事件数: {len(data.get('events', []))}")
    assert len(data.get('events', [])) == 1
    assert data['events'][0]['title'] == '1月微波工程课'
    
    # 查询2024年1月（应该没有）
    response = client.get('/api/calendar/events/?year=2024&month=1')
    data = json.loads(response.content)
    print(f"   查询2024年1月，返回事件数: {len(data.get('events', []))}")
    assert len(data.get('events', [])) == 0
    
    print("   [OK] 跨年份过滤测试通过")
    
    # 5. 测试数据字段完整性
    print("\n5. 测试数据字段完整性")
    response = client.get('/api/calendar/events/?year=2024&month=12')
    data = json.loads(response.content)
    event = data['events'][0]
    
    required_fields = ['id', 'title', 'date', 'time', 'location', 'type', 'description']
    for field in required_fields:
        assert field in event, f"缺少字段: {field}"
        print(f"   [OK] 字段 '{field}': {event.get(field)}")
    
    print("   [OK] 所有必需字段都存在")
    
    # 6. 测试权限隔离
    print("\n6. 测试权限隔离")
    
    # 创建另一个用户
    try:
        user2 = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='testpass123'
        )
    except:
        user2 = User.objects.get(username='otheruser')
    
    # 为用户2添加课程
    CalendarEvent.objects.create(
        user=user2,
        title='其他用户的课程',
        date='2024-12-25',
        event_type='theory'
    )
    
    # 用户1查询，应该看不到用户2的课程
    response = client.get('/api/calendar/events/?year=2024&month=12')
    data = json.loads(response.content)
    
    titles = [e['title'] for e in data.get('events', [])]
    print(f"   用户1看到的事件: {titles}")
    assert '其他用户的课程' not in titles
    print("   [OK] 权限隔离测试通过")
    
    # 7. 测试无效参数处理
    print("\n7. 测试无效参数处理")
    
    # 无效月份
    response = client.get('/api/calendar/events/?year=2024&month=13')
    data = json.loads(response.content)
    print(f"   月份=13，返回事件数: {len(data.get('events', []))}")
    assert data.get('success') == True  # 应该返回成功，只是没有数据
    
    # 无效年份
    response = client.get('/api/calendar/events/?year=abc&month=12')
    data = json.loads(response.content)
    print(f"   年份=abc，返回事件数: {len(data.get('events', []))}")
    
    print("   [OK] 无效参数处理测试通过")
    
    # 8. 测试边界条件 - 月份补零
    print("\n8. 测试月份补零")
    
    # 添加2月的课程
    CalendarEvent.objects.create(
        user=user,
        title='2月课程',
        date='2024-02-15',
        event_type='theory'
    )
    
    # 查询2月（month=2）
    response = client.get('/api/calendar/events/?year=2024&month=2')
    data = json.loads(response.content)
    print(f"   查询2024年2月，返回事件数: {len(data.get('events', []))}")
    assert len(data.get('events', [])) == 1
    assert data['events'][0]['title'] == '2月课程'
    
    print("   [OK] 月份补零测试通过")
    
    # 清理测试数据
    print("\n9. 清理测试数据...")
    CalendarEvent.objects.filter(user=user).delete()
    CalendarEvent.objects.filter(user=user2).delete()
    User.objects.filter(username__in=['calendartest', 'otheruser']).delete()
    print("   清理完成")
    
    print("\n" + "=" * 80)
    print("所有测试通过！")
    print("=" * 80)
    print("\n修复总结：")
    print("1. [OK] 后端API正确处理 year=YYYY&month=M 格式参数")
    print("2. [OK] 向后兼容旧格式 month=YYYY-MM")
    print("3. [OK] 年份和月份正确组合过滤")
    print("4. [OK] 月份自动补零（1月->01）")
    print("5. [OK] 权限隔离正常工作")
    print("6. [OK] 数据字段完整性保证")


if __name__ == '__main__':
    try:
        test_calendar_display()
    except AssertionError as e:
        print(f"\n[X] 测试断言失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n[X] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
