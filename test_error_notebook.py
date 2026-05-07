#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试错题本功能 - 验证错题显示和解析展示
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject2.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client, override_settings
from django.contrib.auth import get_user_model
from blog.models import Course, Chapter, Question, ErrorNotebook
import json

User = get_user_model()


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def test_error_notebook():
    """测试错题本功能"""
    client = Client()
    
    print("=" * 80)
    print("错题本功能测试")
    print("=" * 80)
    
    # 1. 准备测试环境
    print("\n1. 准备测试环境...")
    
    # 创建测试用户
    try:
        user = User.objects.create_user(
            username='errornbtest',
            email='errornb@test.com',
            password='testpass123'
        )
    except:
        user = User.objects.get(username='errornbtest')
    
    client.login(username='errornbtest', password='testpass123')
    
    # 创建测试课程
    try:
        course = Course.objects.create(
            code='test-course',
            name='测试课程',
            description='用于测试的课程'
        )
    except:
        course = Course.objects.get(code='test-course')
    
    # 创建测试章节
    try:
        chapter = Chapter.objects.create(
            code='ch1',
            name='第一章 测试章节',
            course=course
        )
    except:
        chapter = Chapter.objects.filter(code='ch1', course=course).first()
    
    print("   测试环境准备完成")
    
    # 清理旧数据
    ErrorNotebook.objects.filter(user=user).delete()
    
    # 2. 创建测试题目
    print("\n2. 创建测试题目...")
    
    # 创建包含完整信息的题目
    question = Question.objects.create(
        course=course,
        chapter=chapter,
        question_type='single',
        difficulty=2,
        content='测试题目的具体内容：电磁波在真空中的传播速度是多少？',
        options=['3x10^8 m/s', '3x10^6 m/s', '3x10^4 m/s', '3x10^2 m/s'],
        correct_answer='A',
        explanation='电磁波在真空中的传播速度是光速，约为3x10^8米/秒。这是电磁场理论的基本知识。'
    )
    print(f"   创建题目: {question.content[:30]}...")
    
    # 3. 创建错题记录
    print("\n3. 创建错题记录...")
    
    error_record = ErrorNotebook.objects.create(
        user=user,
        course=course,
        question=question,
        error_count=3,
        is_mastered=False
    )
    print(f"   创建错题记录 ID: {error_record.id}")
    
    # 4. 测试API返回数据完整性
    print("\n4. 测试API返回数据完整性...")
    
    response = client.get(f'/api/error-notebook/?course={course.code}')
    data = json.loads(response.content)
    
    print(f"   状态码: {response.status_code}")
    print(f"   返回错题数: {len(data.get('errors', []))}")
    
    assert response.status_code == 200
    assert 'errors' in data
    assert len(data['errors']) == 1
    
    # 5. 检查必需字段
    print("\n5. 检查必需字段...")
    
    error = data['errors'][0]
    required_fields = [
        'id', 'course', 'course_code', 'chapter', 'content', 
        'type', 'difficulty', 'error_count', 'last_error_time',
        'options', 'correct_answer', 'explanation'
    ]
    
    for field in required_fields:
        assert field in error, f"缺少字段: {field}"
        print(f"   [OK] 字段 '{field}': {type(error[field]).__name__}")
    
    # 6. 验证数据内容
    print("\n6. 验证数据内容...")
    
    assert error['content'] == question.content
    print(f"   [OK] 题目内容: {error['content'][:50]}...")
    
    assert error['correct_answer'] == 'A'
    print(f"   [OK] 正确答案: {error['correct_answer']}")
    
    assert len(error['options']) == 4
    print(f"   [OK] 选项数量: {len(error['options'])}")
    
    assert '光速' in error['explanation'] or '3x10^8' in error['explanation']
    print(f"   [OK] 解析内容: {error['explanation'][:50]}...")
    
    assert error['chapter'] == '第一章 测试章节'
    print(f"   [OK] 章节: {error['chapter']}")
    
    # 7. 检查统计数据
    print("\n7. 检查统计数据...")
    
    assert 'total' in data
    assert 'unmastered' in data
    assert 'mastered' in data
    
    assert data['total'] == 1
    assert data['unmastered'] == 1
    assert data['mastered'] == 0
    
    print(f"   [OK] total: {data['total']}")
    print(f"   [OK] unmastered: {data['unmastered']}")
    print(f"   [OK] mastered: {data['mastered']}")
    
    # 8. 测试标记已掌握功能
    print("\n8. 测试标记已掌握功能...")
    
    response = client.post(
        '/api/mark-mastered/',
        json.dumps({'error_id': error_record.id}),
        content_type='application/json'
    )
    data = json.loads(response.content)
    
    assert response.status_code == 200
    assert data.get('success') == True
    print("   [OK] 标记已掌握成功")
    
    # 验证统计数据更新
    response = client.get(f'/api/error-notebook/?course={course.code}')
    data = json.loads(response.content)
    
    assert data['total'] == 1
    assert data['unmastered'] == 0  # 未掌握变为0
    assert data['mastered'] == 1    # 已掌握变为1
    print(f"   [OK] 统计数据已更新")
    
    # 9. 测试不同题型
    print("\n9. 测试不同题型...")
    
    # 判断题
    judge_question = Question.objects.create(
        course=course,
        chapter=chapter,
        question_type='judge',
        difficulty=1,
        content='测试判断题',
        options=['正确', '错误'],
        correct_answer='T',
        explanation='判断题解析'
    )
    
    ErrorNotebook.objects.create(
        user=user,
        course=course,
        question=judge_question,
        error_count=1,
        is_mastered=False
    )
    
    response = client.get(f'/api/error-notebook/?course={course.code}')
    data = json.loads(response.content)
    
    assert data['unmastered'] == 1  # 未掌握的判断题
    print(f"   [OK] 判断题数据正确")
    
    # 10. 测试权限隔离
    print("\n10. 测试权限隔离...")
    
    # 创建另一个用户和错题
    user2 = User.objects.create_user(
        username='otherusertest',
        email='other@test.com',
        password='testpass123'
    )
    
    ErrorNotebook.objects.create(
        user=user2,
        course=course,
        question=question,
        error_count=5,
        is_mastered=False
    )
    
    # 用户1查看，应该只看到自己的错题
    response = client.get(f'/api/error-notebook/?course={course.code}')
    data = json.loads(response.content)
    
    assert data['total'] == 2  # 用户1有2道错题（已掌握的+判断题）
    print(f"   [OK] 用户1只能看到自己的错题: {data['total']}道")
    
    # 清理测试数据
    print("\n11. 清理测试数据...")
    ErrorNotebook.objects.filter(user__in=[user, user2]).delete()
    Question.objects.filter(course=course).delete()
    Chapter.objects.filter(code='ch1', course=course).delete()
    Course.objects.filter(code='test-course').delete()
    User.objects.filter(username__in=['errornbtest', 'otherusertest']).delete()
    print("   清理完成")
    
    print("\n" + "=" * 80)
    print("所有测试通过！")
    print("=" * 80)
    print("\n修复总结：")
    print("1. [OK] 后端API返回完整的题目内容")
    print("2. [OK] 返回正确答案 (correct_answer)")
    print("3. [OK] 返回答案解析 (explanation)")
    print("4. [OK] 返回选项列表 (options)")
    print("5. [OK] 返回完整统计数据 (total/unmastered/mastered)")
    print("6. [OK] 权限隔离正常工作")


if __name__ == '__main__':
    try:
        test_error_notebook()
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
