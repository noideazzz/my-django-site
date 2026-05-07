#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试日历API接口
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
def test_calendar_api():
    """测试日历相关API"""
    client = Client()
    
    print("=" * 80)
    print("日历API测试")
    print("=" * 80)
    
    # 1. 测试未登录状态
    print("\n1. 测试未登录状态 - 创建事件")
    response = client.post('/api/calendar/events/create/',
                          data=json.dumps({'title': '测试', 'date': '2024-01-01'}),
                          content_type='application/json')
    print(f"   状态码: {response.status_code}")
    # 未登录应该返回302重定向或403
    assert response.status_code in [302, 403], f"未登录应该返回302或403，实际返回{response.status_code}"
    print("   验证通过：未登录状态检查正确")
    
    # 创建测试用户
    print("\n2. 创建测试用户...")
    try:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print("   用户创建成功")
    except Exception as e:
        # 如果用户已存在，尝试获取
        try:
            user = User.objects.get(username='testuser')
            user.set_password('testpass123')
            user.save()
            print("   用户已存在，重置密码")
        except Exception:
            print(f"   创建用户失败: {e}")
            raise
    
    # 登录
    print("\n3. 用户登录...")
    login_result = client.login(username='testuser', password='testpass123')
    if login_result:
        print("   登录成功")
    else:
        print("   登录失败，尝试直接使用测试客户端强制认证")
        # 强制设置用户
        client.force_login(user)
        print("   已强制登录")
    
    # 4. 测试检查认证状态
    print("\n4. 测试检查认证状态")
    response = client.get('/api/calendar/auth/')
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"   响应: {data}")
        assert data.get('is_authenticated') == True, "应该返回已认证状态"
        print("   验证通过：认证状态正确")
    else:
        print(f"   警告: 认证检查返回 {response.status_code}")
    
    # 5. 测试创建事件 - 空标题
    print("\n5. 测试创建事件 - 空标题（表单验证）")
    response = client.post('/api/calendar/events/create/',
                          data=json.dumps({'title': '', 'date': '2024-01-01'}),
                          content_type='application/json')
    print(f"   状态码: {response.status_code}")
    data = json.loads(response.content)
    print(f"   响应: {data}")
    assert data.get('success') == False, "应该返回失败状态"
    assert 'error' in data, "应该返回错误信息"
    assert data.get('field') == 'title', "应该指示title字段错误"
    print("   验证通过：正确返回表单验证错误")
    
    # 6. 测试创建事件 - 空日期
    print("\n6. 测试创建事件 - 空日期（表单验证）")
    response = client.post('/api/calendar/events/create/',
                          data=json.dumps({'title': '测试课程', 'date': ''}),
                          content_type='application/json')
    print(f"   状态码: {response.status_code}")
    data = json.loads(response.content)
    print(f"   响应: {data}")
    assert data.get('success') == False, "应该返回失败状态"
    assert data.get('field') == 'date', "应该指示date字段错误"
    print("   验证通过：正确返回表单验证错误")
    
    # 7. 测试创建事件 - 无效日期格式
    print("\n7. 测试创建事件 - 无效日期格式")
    response = client.post('/api/calendar/events/create/',
                          data=json.dumps({'title': '测试课程', 'date': '2024/01/01'}),
                          content_type='application/json')
    print(f"   状态码: {response.status_code}")
    data = json.loads(response.content)
    print(f"   响应: {data}")
    assert data.get('success') == False, "应该返回失败状态"
    print("   验证通过：正确返回日期格式错误")
    
    # 8. 测试创建事件 - 成功
    print("\n8. 测试创建事件 - 成功场景")
    response = client.post('/api/calendar/events/create/',
                          data=json.dumps({
                              'title': '电磁场理论课',
                              'date': '2024-12-25',
                              'time': '08:00',
                              'location': '教学楼A301',
                              'type': 'theory',
                              'description': '第4章内容讲解'
                          }),
                          content_type='application/json')
    print(f"   状态码: {response.status_code}")
    data = json.loads(response.content)
    print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert data.get('success') == True, f"应该返回成功状态，实际: {data}"
    event_id = data.get('event_id')
    assert event_id is not None, "应该返回事件ID"
    assert 'event' in data, "应该返回完整事件数据"
    print(f"   验证通过：事件创建成功，ID={event_id}")
    
    # 9. 测试获取事件列表（使用年份-月份格式）
    print("\n9. 测试获取事件列表")
    response = client.get('/api/calendar/events/?year=2024&month=2024-12')
    print(f"   状态码: {response.status_code}")
    data = json.loads(response.content)
    print(f"   事件数量: {len(data.get('events', []))}")
    assert data.get('success') == True, "应该返回成功状态"
    # 注意：后端可能使用year和month参数组合查询，这里只检查成功响应
    print("   验证通过：成功获取事件列表")
    
    # 10. 测试更新事件 - 使用POST方法
    print(f"\n10. 测试更新事件 - 使用POST方法 (ID={event_id})")
    response = client.post(f'/api/calendar/events/{event_id}/update/',
                          data=json.dumps({
                              'title': '电磁场理论课（已修改）',
                              'date': '2024-12-25',
                              'time': '10:00',
                              'location': '教学楼B205',
                              'type': 'lab',
                              'description': '实验课'
                          }),
                          content_type='application/json')
    print(f"   状态码: {response.status_code}")
    data = json.loads(response.content)
    print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert data.get('success') == True, f"应该返回成功状态，实际: {data}"
    assert 'event' in data, "应该返回更新后的事件数据"
    assert data.get('event', {}).get('title') == '电磁场理论课（已修改）', "标题应该已更新"
    print("   验证通过：使用POST方法成功更新事件")
    
    # 11. 测试更新事件 - 空标题验证
    print(f"\n11. 测试更新事件 - 空标题验证 (ID={event_id})")
    response = client.post(f'/api/calendar/events/{event_id}/update/',
                          data=json.dumps({
                              'title': '',
                              'date': '2024-12-25'
                          }),
                          content_type='application/json')
    print(f"   状态码: {response.status_code}")
    data = json.loads(response.content)
    print(f"   响应: {data}")
    assert data.get('success') == False, "应该返回失败状态"
    assert data.get('field') == 'title', "应该指示title字段错误"
    print("   验证通过：更新时正确验证必填字段")
    
    # 12. 测试删除事件 - 使用POST方法
    print(f"\n12. 测试删除事件 - 使用POST方法 (ID={event_id})")
    response = client.post(f'/api/calendar/events/{event_id}/delete/',
                          content_type='application/json')
    print(f"   状态码: {response.status_code}")
    data = json.loads(response.content)
    print(f"   响应: {data}")
    assert data.get('success') == True, "应该返回成功状态"
    assert data.get('deleted_id') == event_id, "应该返回被删除的事件ID"
    print("   验证通过：使用POST方法成功删除事件")
    
    # 13. 测试删除不存在的事件
    print(f"\n13. 测试删除不存在的事件 (ID=99999)")
    response = client.post('/api/calendar/events/99999/delete/',
                          content_type='application/json')
    print(f"   状态码: {response.status_code}")
    data = json.loads(response.content)
    print(f"   响应: {data}")
    assert data.get('success') == False, "应该返回失败状态"
    assert 'error' in data, "应该返回错误信息"
    assert '不存在' in data.get('error', '') or '权限' in data.get('error', ''), "错误信息应该指示事件不存在"
    print("   验证通过：正确返回错误信息")
    
    # 14. 测试特殊字符和XSS防护
    print("\n14. 测试特殊字符标题")
    response = client.post('/api/calendar/events/create/',
                          data=json.dumps({
                              'title': '课程<>&"\'测试',
                              'date': '2024-12-25',
                              'description': '描述<script>alert(1)</script>'
                          }),
                          content_type='application/json')
    print(f"   状态码: {response.status_code}")
    data = json.loads(response.content)
    print(f"   响应: {data}")
    if data.get('success'):
        special_event_id = data.get('event_id')
        print("   验证通过：正确处理特殊字符")
        # 清理
        client.post(f'/api/calendar/events/{special_event_id}/delete/',
                   content_type='application/json')
    else:
        print(f"   错误: {data.get('error')}")
    
    # 15. 测试无效JSON数据
    print("\n15. 测试无效JSON数据")
    response = client.post('/api/calendar/events/create/',
                          data='这不是有效的JSON',
                          content_type='application/json')
    print(f"   状态码: {response.status_code}")
    data = json.loads(response.content)
    print(f"   响应: {data}")
    assert data.get('success') == False, "应该返回失败状态"
    assert '格式' in data.get('error', '') or '格式' in data.get('message', ''), "应该返回格式错误提示"
    print("   验证通过：正确处理无效JSON")
    
    # 清理测试数据
    print("\n16. 清理测试数据...")
    CalendarEvent.objects.filter(user=user).delete()
    print("   清理完成")
    
    print("\n" + "=" * 80)
    print("所有测试通过！")
    print("=" * 80)


if __name__ == '__main__':
    try:
        test_calendar_api()
    except AssertionError as e:
        print(f"\n测试断言失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
