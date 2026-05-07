# 日历课程显示问题诊断报告

## 问题概述

用户添加新课程后，日历模块未能准确显示所添加的课程内容。

## 问题定位

### 1. 参数格式不匹配（主要问题）

**前端代码**（calendar.html:749）：
```javascript
const year = currentYear.value;  // 2024
const month = currentMonth.value + 1;  // 12
const response = await fetch(`${API_BASE}/events/?year=${year}&month=${month}`);
// 发送: year=2024&month=12
```

**后端代码**（views.py:839-841）：
```python
month = request.GET.get('month')  # 获取到 "12"
if month:
    events = events.filter(date__startswith=month)  # 匹配所有包含"12"的日期
```

**问题分析**：
- 后端只使用了 `month` 参数（值为"12"）
- `date__startswith="12"` 会匹配所有以"12"开头的日期
- 这包括："2024-12-15"、"2023-12-01"，甚至 "12-25-2024"（如果存在）
- **年份过滤失效！**

### 2. 添加课程后日历不显示（跨月份问题）

**场景**：
1. 用户当前查看的是2024年1月的日历
2. 用户选择1月15日并添加课程
3. 课程成功保存到数据库（日期：2024-01-15）
4. 日历立即刷新，但**月份参数仍然是当前显示的月份**
5. 如果当前显示的就是1月，应该能看到；但如果用户快速切换月份，可能看不到

**实际代码分析**：
- 添加课程后调用 `await loadEventsFromServer()`
- 该函数使用 `currentYear` 和 `currentMonth` 获取事件
- **问题**：如果添加的课程日期不在当前显示的月份，添加后不会自动跳转到那个月份

### 3. 日期格式转换问题

**后端返回**（views.py:844-853）：
```python
event_list.append({
    'id': event.id,
    'title': event.title,
    'date': event.date.strftime('%Y-%m-%d'),  # 格式：2024-12-25
    'time': event.time.strftime('%H:%M') if event.time else None,
    'location': event.location,
    'type': event.event_type,  # 注意：字段名是type
    'description': event.description,
})
```

**前端匹配**（calendar.html:628-636）：
```javascript
days.push({
    date: dateStr,  // 格式：2024-12-25
    ...
    events: events.value.filter(event => event.date === dateStr)
});
```

**分析**：日期格式一致（都是YYYY-MM-DD），这部分没有问题。

### 4. 权限控制分析

**后端过滤**（views.py:835）：
```python
events = CalendarEvent.objects.filter(user=user)
```

**分析**：
- ✅ 正确实现了用户数据隔离
- ✅ 用户只能看到自己的课程

## 修复方案

### 方案1：修复参数格式（推荐）

修改后端API，正确处理 `year` 和 `month` 参数：

```python
@login_required
@require_http_methods(["GET"])
def get_calendar_events(request):
    """获取用户的日历事件"""
    user = request.user
    events = CalendarEvent.objects.filter(user=user)
    
    # 支持两种参数格式：
    # 1. year=2024&month=12（前端当前使用的格式）
    # 2. month=2024-12（旧格式，向后兼容）
    
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    if year and month:
        # 新格式：year=2024&month=12
        try:
            year = int(year)
            month = int(month)
            if 1 <= month <= 12:
                month_str = f"{year}-{month:02d}"
                events = events.filter(date__startswith=month_str)
        except (ValueError, TypeError):
            pass
    elif month and '-' in month:
        # 旧格式：month=2024-12（向后兼容）
        events = events.filter(date__startswith=month)
    
    event_list = []
    for event in events:
        event_list.append({
            'id': event.id,
            'title': event.title,
            'date': event.date.strftime('%Y-%m-%d'),
            'time': event.time.strftime('%H:%M') if event.time else None,
            'location': event.location,
            'type': event.event_type,
            'description': event.description,
        })
    
    return JsonResponse({
        'success': True,
        'events': event_list
    })
```

### 方案2：优化添加课程后的用户体验

添加课程后，如果添加的日期不在当前显示的月份，提示用户：

```javascript
async function saveEvent() {
    // ... 保存逻辑 ...
    
    if (response.ok) {
        const data = await response.json();
        if (data.success) {
            ElMessage.success(data.message || '添加成功');
            
            // 检查添加的日期是否在当前显示的月份
            const eventDate = new Date(selectedDate.value);
            const eventYear = eventDate.getFullYear();
            const eventMonth = eventDate.getMonth();
            
            if (eventYear !== currentYear.value || eventMonth !== currentMonth.value) {
                // 自动跳转到添加课程的月份
                currentDate.value = new Date(eventYear, eventMonth, 1);
                ElMessage.info(`已自动跳转到 ${eventYear}年${eventMonth + 1}月`);
            }
            
            await loadEventsFromServer();
            showEventModal.value = false;
        }
    }
}
```

### 方案3：添加调试日志

在前后端添加调试日志，方便问题排查：

**前端**：
```javascript
async function loadEventsFromServer() {
    console.log(`[Calendar Debug] 加载事件: year=${currentYear.value}, month=${currentMonth.value + 1}`);
    // ...
    if (response.ok) {
        const data = await response.json();
        console.log(`[Calendar Debug] 获取到 ${data.events.length} 个事件`);
        events.value = data.events;
    }
}
```

**后端**：
```python
import logging
logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["GET"])
def get_calendar_events(request):
    user = request.user
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    logger.info(f"[Calendar API] 用户 {user.username} 请求事件: year={year}, month={month}")
    # ...
```

## 测试验证计划

### 测试场景1：基本功能
1. 在2024年1月添加课程，检查是否正常显示
2. 切换到2024年2月，确认1月的课程不显示
3. 切换回2024年1月，确认课程仍然显示

### 测试场景2：跨月份添加
1. 当前显示2024年1月
2. 选择2024年2月15日添加课程
3. 验证自动跳转到2月并显示新课程

### 测试场景3：年份边界
1. 当前显示2024年12月
2. 添加2025年1月的课程
3. 验证年份切换正确

### 测试场景4：权限隔离
1. 用户A添加课程
