"""
个人工作计划API
提供快速捕获、四象限视图、日历规划、番茄钟、复盘统计、习惯追踪等功能
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import logging
import re

personal_plan_bp = Blueprint('personal_plan', __name__, url_prefix='/personal-plan')
logger = logging.getLogger(__name__)

def get_models():
    """延迟获取模型，避免循环导入"""
    from enhanced_app import (
        db, User
    )
    return {
        'db': db,
        'User': User
    }

class PersonalTaskStatus:
    INBOX = "inbox"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"

class TaskQuadrant:
    IMPORTANT_URGENT = 1
    IMPORTANT_NOT_URGENT = 2
    NOT_IMPORTANT_URGENT = 3
    NOT_IMPORTANT_NOT_URGENT = 4

@personal_plan_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """获取用户的个人任务列表"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask
        status = request.args.get('status')
        quadrant = request.args.get('quadrant')
        tag = request.args.get('tag')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        is_habit = request.args.get('is_habit')

        query = PersonalTask.query.filter(PersonalTask.user_id == current_user_id)

        if status:
            if status == 'inbox':
                query = query.filter(PersonalTask.status == PersonalTaskStatus.INBOX)
            elif status == 'active':
                query = query.filter(PersonalTask.status.in_([PersonalTaskStatus.TODO, PersonalTaskStatus.IN_PROGRESS]))
            elif status == 'done':
                query = query.filter(PersonalTask.status == PersonalTaskStatus.DONE)
            else:
                query = query.filter(PersonalTask.status == status)

        if quadrant:
            query = query.filter(PersonalTask.quadrant == int(quadrant))

        if tag:
            query = query.filter(PersonalTask.tags.contains(tag))

        if is_habit is not None:
            query = query.filter(PersonalTask.is_habit == (is_habit.lower() == 'true'))

        if date_from:
            query = query.filter(PersonalTask.scheduled_date >= date_from)
        if date_to:
            query = query.filter(PersonalTask.scheduled_date <= date_to)

        tasks = query.order_by(PersonalTask.created_at.desc()).all()

        return jsonify({
            'success': True,
            'data': {
                'tasks': [task.to_dict() for task in tasks],
                'total': len(tasks)
            }
        })

    except Exception as e:
        logger.error(f"获取个人任务失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取个人任务失败: {str(e)}'}), 500

@personal_plan_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    """创建新任务 - 支持智能解析"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask

        data = request.get_json()
        content = data.get('content', '').strip()

        if not content:
            return jsonify({'success': False, 'message': '任务内容不能为空'}), 400

        parsed = parse_task_content(content)

        task = PersonalTask(
            user_id=current_user_id,
            title=parsed['title'],
            description=data.get('description', parsed.get('description', '')),
            status=PersonalTaskStatus.INBOX if not data.get('scheduled_date') else PersonalTaskStatus.TODO,
            priority=data.get('priority', parsed.get('priority', 'medium')),
            quadrant=parsed.get('quadrant'),
            scheduled_date=parsed.get('scheduled_date') or data.get('scheduled_date'),
            scheduled_time=parsed.get('scheduled_time'),
            estimated_minutes=parsed.get('estimated_minutes') or data.get('estimated_minutes'),
            tags=','.join(parsed.get('tags', [])) if parsed.get('tags') else (data.get('tags', '')),
            is_habit=data.get('is_habit', False),
            habit_frequency=data.get('habit_frequency'),
            source=data.get('source', 'manual')
        )

        db.session.add(task)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': task.to_dict(),
            'message': '任务创建成功'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"创建任务失败: {str(e)}")
        return jsonify({'success': False, 'message': f'创建任务失败: {str(e)}'}), 500

@personal_plan_bp.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """获取单个任务详情"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask

        task = PersonalTask.query.filter(
            PersonalTask.id == task_id,
            PersonalTask.user_id == current_user_id
        ).first()

        if not task:
            return jsonify({'success': False, 'message': '任务不存在'}), 404

        return jsonify({
            'success': True,
            'data': task.to_dict()
        })

    except Exception as e:
        logger.error(f"获取任务详情失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取任务详情失败: {str(e)}'}), 500

@personal_plan_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """更新任务"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask

        task = PersonalTask.query.filter(
            PersonalTask.id == task_id,
            PersonalTask.user_id == current_user_id
        ).first()

        if not task:
            return jsonify({'success': False, 'message': '任务不存在'}), 404

        data = request.get_json()

        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            task.status = data['status']
            if data['status'] == PersonalTaskStatus.DONE and not task.completed_at:
                task.completed_at = datetime.utcnow()
        if 'priority' in data:
            task.priority = data['priority']
        if 'quadrant' in data:
            task.quadrant = data['quadrant']
        if 'scheduled_date' in data:
            task.scheduled_date = data['scheduled_date']
        if 'scheduled_time' in data:
            task.scheduled_time = data['scheduled_time']
        if 'estimated_minutes' in data:
            task.estimated_minutes = data['estimated_minutes']
        if 'actual_minutes' in data:
            task.actual_minutes = data['actual_minutes']
        if 'tags' in data:
            task.tags = data['tags'] if isinstance(data['tags'], str) else ','.join(data['tags'])
        if 'is_habit' in data:
            task.is_habit = data['is_habit']
        if 'habit_frequency' in data:
            task.habit_frequency = data['habit_frequency']

        db.session.commit()

        return jsonify({
            'success': True,
            'data': task.to_dict(),
            'message': '任务更新成功'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"更新任务失败: {str(e)}")
        return jsonify({'success': False, 'message': f'更新任务失败: {str(e)}'}), 500

@personal_plan_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """删除任务"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask

        task = PersonalTask.query.filter(
            PersonalTask.id == task_id,
            PersonalTask.user_id == current_user_id
        ).first()

        if not task:
            return jsonify({'success': False, 'message': '任务不存在'}), 404

        db.session.delete(task)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '任务删除成功'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除任务失败: {str(e)}")
        return jsonify({'success': False, 'message': f'删除任务失败: {str(e)}'}), 500

@personal_plan_bp.route('/tasks/inbox', methods=['GET'])
@jwt_required()
def get_inbox_tasks():
    """获取收件箱中的任务"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask

        tasks = PersonalTask.query.filter(
            PersonalTask.user_id == current_user_id,
            PersonalTask.status == PersonalTaskStatus.INBOX
        ).order_by(PersonalTask.created_at.desc()).all()

        return jsonify({
            'success': True,
            'data': {
                'tasks': [task.to_dict() for task in tasks],
                'total': len(tasks)
            }
        })

    except Exception as e:
        logger.error(f"获取收件箱任务失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取收件箱任务失败: {str(e)}'}), 500

@personal_plan_bp.route('/tasks/inbox/process', methods=['POST'])
@jwt_required()
def process_inbox():
    """处理收件箱任务"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask

        data = request.get_json()
        task_ids = data.get('task_ids', [])
        action = data.get('action', 'organize')
        target_status = data.get('status', PersonalTaskStatus.TODO)

        if action == 'delete':
            PersonalTask.query.filter(
                PersonalTask.id.in_(task_ids),
                PersonalTask.user_id == current_user_id
            ).delete(synchronize_session=False)
        else:
            PersonalTask.query.filter(
                PersonalTask.id.in_(task_ids),
                PersonalTask.user_id == current_user_id
            ).update({PersonalTask.status: target_status}, synchronize_session=False)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'已处理 {len(task_ids)} 个任务'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"处理收件箱失败: {str(e)}")
        return jsonify({'success': False, 'message': f'处理收件箱失败: {str(e)}'}), 500

@personal_plan_bp.route('/tasks/quadrant', methods=['GET'])
@jwt_required()
def get_quadrant_tasks():
    """获取四象限任务"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask

        tasks = PersonalTask.query.filter(
            PersonalTask.user_id == current_user_id,
            PersonalTask.status.in_([PersonalTaskStatus.TODO, PersonalTaskStatus.IN_PROGRESS])
        ).all()

        quadrant_tasks = {1: [], 2: [], 3: [], 4: []}

        for task in tasks:
            if task.quadrant and task.quadrant in quadrant_tasks:
                quadrant_tasks[task.quadrant].append(task.to_dict())

        for q in quadrant_tasks:
            quadrant_tasks[q].sort(key=lambda x: (
                0 if x['priority'] == 'urgent' else 1 if x['priority'] == 'high' else 2,
                x.get('scheduled_date') or ''
            ))

        return jsonify({
            'success': True,
            'data': quadrant_tasks
        })

    except Exception as e:
        logger.error(f"获取四象限任务失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取四象限任务失败: {str(e)}'}), 500

@personal_plan_bp.route('/tasks/start', methods=['POST'])
@jwt_required()
def start_task():
    """开始执行任务"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask

        data = request.get_json()
        task_id = data.get('task_id')

        task = PersonalTask.query.filter(
            PersonalTask.id == task_id,
            PersonalTask.user_id == current_user_id
        ).first()

        if not task:
            return jsonify({'success': False, 'message': '任务不存在'}), 404

        task.status = PersonalTaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'data': task.to_dict(),
            'message': '任务已开始'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"开始任务失败: {str(e)}")
        return jsonify({'success': False, 'message': f'开始任务失败: {str(e)}'}), 500

@personal_plan_bp.route('/tasks/complete', methods=['POST'])
@jwt_required()
def complete_task():
    """完成任务"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask

        data = request.get_json()
        task_id = data.get('task_id')
        actual_minutes = data.get('actual_minutes')

        task = PersonalTask.query.filter(
            PersonalTask.id == task_id,
            PersonalTask.user_id == current_user_id
        ).first()

        if not task:
            return jsonify({'success': False, 'message': '任务不存在'}), 404

        task.status = PersonalTaskStatus.DONE
        task.completed_at = datetime.utcnow()

        if actual_minutes:
            task.actual_minutes = actual_minutes

        if task.is_habit and task.habit_frequency:
            from enhanced_app import HabitRecord
            record = HabitRecord(
                user_id=current_user_id,
                task_id=task.id,
                completed_date=datetime.utcnow().date(),
                duration_minutes=actual_minutes or task.estimated_minutes
            )
            db.session.add(record)

        db.session.commit()

        return jsonify({
            'success': True,
            'data': task.to_dict(),
            'message': '任务已完成'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"完成任务失败: {str(e)}")
        return jsonify({'success': False, 'message': f'完成任务失败: {str(e)}'}), 500

@personal_plan_bp.route('/calendar/events', methods=['GET'])
@jwt_required()
def get_calendar_events():
    """获取日历事件"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask

        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        query = PersonalTask.query.filter(
            PersonalTask.user_id == current_user_id,
            PersonalTask.scheduled_date.isnot(None),
            PersonalTask.status != PersonalTaskStatus.CANCELLED
        )

        if date_from:
            query = query.filter(PersonalTask.scheduled_date >= date_from)
        if date_to:
            query = query.filter(PersonalTask.scheduled_date <= date_to)

        tasks = query.all()

        events = []
        for task in tasks:
            event = {
                'id': task.id,
                'title': task.title,
                'date': task.scheduled_date,
                'time': task.scheduled_time,
                'duration': task.estimated_minutes,
                'type': 'habit' if task.is_habit else 'task',
                'priority': task.priority,
                'quadrant': task.quadrant,
                'status': task.status,
                'color': get_priority_color(task.priority)
            }
            events.append(event)

        return jsonify({
            'success': True,
            'data': events
        })

    except Exception as e:
        logger.error(f"获取日历事件失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取日历事件失败: {str(e)}'}), 500

@personal_plan_bp.route('/time-blocks', methods=['GET'])
@jwt_required()
def get_time_blocks():
    """获取日程时间块"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask

        date = request.args.get('date')

        query = PersonalTask.query.filter(
            PersonalTask.user_id == current_user_id,
            PersonalTask.scheduled_date == date,
            PersonalTask.status != PersonalTaskStatus.CANCELLED
        )

        tasks = query.order_by(PersonalTask.scheduled_time.asc()).all()

        blocks = []
        current_time = 8 * 60
        for task in tasks:
            if task.scheduled_time:
                parts = task.scheduled_time.split(':')
                task_minutes = int(parts[0]) * 60 + int(parts[1])
            else:
                task_minutes = current_time

            duration = task.estimated_minutes or 30

            blocks.append({
                'id': task.id,
                'title': task.title,
                'start_time': f"{task_minutes // 60:02d}:{task_minutes % 60:02d}",
                'end_time': f"{(task_minutes + duration) // 60:02d}:{(task_minutes + duration) % 60:02d}",
                'duration': duration,
                'priority': task.priority,
                'status': task.status,
                'is_habit': task.is_habit
            })

            current_time = task_minutes + duration + 15

        return jsonify({
            'success': True,
            'data': blocks
        })

    except Exception as e:
        logger.error(f"获取时间块失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取时间块失败: {str(e)}'}), 500

@personal_plan_bp.route('/time-blocks', methods=['POST'])
@jwt_required()
def create_time_block():
    """创建时间块"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask

        data = request.get_json()

        task = PersonalTask(
            user_id=current_user_id,
            title=data.get('title', ''),
            status=PersonalTaskStatus.TODO,
            priority=data.get('priority', 'medium'),
            scheduled_date=data.get('date'),
            scheduled_time=data.get('start_time'),
            estimated_minutes=data.get('duration', 30)
        )

        db.session.add(task)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': task.to_dict(),
            'message': '时间块创建成功'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"创建时间块失败: {str(e)}")
        return jsonify({'success': False, 'message': f'创建时间块失败: {str(e)}'}), 500

@personal_plan_bp.route('/focus/start', methods=['POST'])
@jwt_required()
def start_focus():
    """开始专注模式"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import FocusSession

        data = request.get_json()
        task_id = data.get('task_id')
        focus_type = data.get('focus_type', 'pomodoro')
        duration = 25 if focus_type == 'pomodoro' else data.get('duration', 25)

        session = FocusSession(
            user_id=current_user_id,
            task_id=task_id,
            focus_type=focus_type,
            planned_duration=duration,
            started_at=datetime.utcnow()
        )

        db.session.add(session)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': session.to_dict(),
            'message': '专注模式已启动'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"启动专注失败: {str(e)}")
        return jsonify({'success': False, 'message': f'启动专注失败: {str(e)}'}), 500

@personal_plan_bp.route('/focus/end', methods=['POST'])
@jwt_required()
def end_focus():
    """结束专注模式"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import FocusSession

        data = request.get_json()
        session_id = data.get('session_id')
        completed = data.get('completed', True)

        session = FocusSession.query.filter(
            FocusSession.id == session_id,
            FocusSession.user_id == current_user_id
        ).first()

        if not session:
            return jsonify({'success': False, 'message': '专注会话不存在'}), 404

        session.ended_at = datetime.utcnow()
        session.actual_duration = int((session.ended_at - session.started_at).total_seconds() / 60)
        session.completed = completed

        if session.task_id and completed:
            from enhanced_app import PersonalTask
            task = PersonalTask.query.get(session.task_id)
            if task and task.status != PersonalTaskStatus.DONE:
                if session.actual_duration >= session.planned_duration * 0.5:
                    task.status = PersonalTaskStatus.DONE
                    task.completed_at = datetime.utcnow()
                    task.actual_minutes = (task.actual_minutes or 0) + session.actual_duration

        db.session.commit()

        return jsonify({
            'success': True,
            'data': session.to_dict(),
            'message': '专注模式已结束'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"结束专注失败: {str(e)}")
        return jsonify({'success': False, 'message': f'结束专注失败: {str(e)}'}), 500

@personal_plan_bp.route('/focus/stats', methods=['GET'])
@jwt_required()
def get_focus_stats():
    """获取专注统计"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import FocusSession

        days = int(request.args.get('days', 7))
        start_date = datetime.utcnow() - timedelta(days=days)

        sessions = FocusSession.query.filter(
            FocusSession.user_id == current_user_id,
            FocusSession.started_at >= start_date
        ).all()

        total_minutes = sum(s.actual_duration or 0 for s in sessions)
        completed_count = sum(1 for s in sessions if s.completed)
        pomodoro_count = sum(1 for s in sessions if s.focus_type == 'pomodoro')

        daily_stats = {}
        for s in sessions:
            date_key = s.started_at.strftime('%Y-%m-%d')
            if date_key not in daily_stats:
                daily_stats[date_key] = {'minutes': 0, 'sessions': 0}
            daily_stats[date_key]['minutes'] += s.actual_duration or 0
            daily_stats[date_key]['sessions'] += 1

        return jsonify({
            'success': True,
            'data': {
                'total_minutes': total_minutes,
                'completed_sessions': completed_count,
                'pomodoro_count': pomodoro_count,
                'total_sessions': len(sessions),
                'daily_stats': daily_stats
            }
        })

    except Exception as e:
        logger.error(f"获取专注统计失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取专注统计失败: {str(e)}'}), 500

@personal_plan_bp.route('/habits', methods=['GET'])
@jwt_required()
def get_habits():
    """获取习惯列表"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask, HabitRecord

        habits = PersonalTask.query.filter(
            PersonalTask.user_id == current_user_id,
            PersonalTask.is_habit == True
        ).all()

        habit_data = []
        for habit in habits:
            records = HabitRecord.query.filter(
                HabitRecord.user_id == current_user_id,
                HabitRecord.task_id == habit.id
            ).order_by(HabitRecord.completed_date.desc()).limit(30).all()

            habit_data.append({
                'task': habit.to_dict(),
                'records': [r.to_dict() for r in records],
                'streak': calculate_streak(records),
                'total_completions': len(records)
            })

        return jsonify({
            'success': True,
            'data': habit_data
        })

    except Exception as e:
        logger.error(f"获取习惯失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取习惯失败: {str(e)}'}), 500

@personal_plan_bp.route('/habits/check-in', methods=['POST'])
@jwt_required()
def check_in_habit():
    """打卡习惯"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import HabitRecord

        data = request.get_json()
        task_id = data.get('task_id')
        duration = data.get('duration')

        record = HabitRecord(
            user_id=current_user_id,
            task_id=task_id,
            completed_date=datetime.utcnow().date(),
            duration_minutes=duration
        )

        db.session.add(record)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': record.to_dict(),
            'message': '打卡成功'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"打卡失败: {str(e)}")
        return jsonify({'success': False, 'message': f'打卡失败: {str(e)}'}), 500

@personal_plan_bp.route('/stats/daily', methods=['GET'])
@jwt_required()
def get_daily_stats():
    """获取每日统计"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask, FocusSession

        date = request.args.get('date', datetime.utcnow().strftime('%Y-%m-%d'))

        tasks = PersonalTask.query.filter(
            PersonalTask.user_id == current_user_id,
            PersonalTask.scheduled_date == date
        ).all()

        completed = sum(1 for t in tasks if t.status == PersonalTaskStatus.DONE)
        total = len(tasks)
        completion_rate = (completed / total * 100) if total > 0 else 0

        focus_sessions = FocusSession.query.filter(
            FocusSession.user_id == current_user_id,
            FocusSession.started_at >= datetime.strptime(date, '%Y-%m-%d'),
            FocusSession.started_at < datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)
        ).all()

        focus_minutes = sum(s.actual_duration or 0 for s in focus_sessions)

        time_by_quadrant = {1: 0, 2: 0, 3: 0, 4: 0}
        for task in tasks:
            if task.quadrant and task.status == PersonalTaskStatus.DONE:
                time_by_quadrant[task.quadrant] += task.actual_minutes or task.estimated_minutes or 0

        return jsonify({
            'success': True,
            'data': {
                'date': date,
                'tasks_total': total,
                'tasks_completed': completed,
                'completion_rate': round(completion_rate, 1),
                'focus_minutes': focus_minutes,
                'time_by_quadrant': time_by_quadrant
            }
        })

    except Exception as e:
        logger.error(f"获取每日统计失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取每日统计失败: {str(e)}'}), 500

@personal_plan_bp.route('/stats/weekly', methods=['GET'])
@jwt_required()
def get_weekly_stats():
    """获取每周统计"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask, FocusSession

        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        tasks = PersonalTask.query.filter(
            PersonalTask.user_id == current_user_id,
            PersonalTask.scheduled_date >= week_start.strftime('%Y-%m-%d'),
            PersonalTask.scheduled_date <= week_end.strftime('%Y-%m-%d')
        ).all()

        completed = sum(1 for t in tasks if t.status == PersonalTaskStatus.DONE)
        total = len(tasks)
        completion_rate = (completed / total * 100) if total > 0 else 0

        overdue = sum(1 for t in tasks if t.status != PersonalTaskStatus.DONE and t.scheduled_date and datetime.strptime(t.scheduled_date, '%Y-%m-%d').date() < today)

        by_type = {}
        for task in tasks:
            tag = task.tags.split(',')[0] if task.tags else 'other'
            if tag not in by_type:
                by_type[tag] = {'total': 0, 'completed': 0, 'minutes': 0}
            by_type[tag]['total'] += 1
            if task.status == PersonalTaskStatus.DONE:
                by_type[tag]['completed'] += 1
            by_type[tag]['minutes'] += task.actual_minutes or task.estimated_minutes or 0

        focus_sessions = FocusSession.query.filter(
            FocusSession.user_id == current_user_id,
            FocusSession.started_at >= datetime.combine(week_start, datetime.min.time()),
            FocusSession.started_at < datetime.combine(week_end + timedelta(days=1), datetime.min.time())
        ).all()

        total_focus_minutes = sum(s.actual_duration or 0 for s in focus_sessions)

        achievement = generate_achievement_message(completed, total, total_focus_minutes)

        return jsonify({
            'success': True,
            'data': {
                'week_start': week_start.strftime('%Y-%m-%d'),
                'week_end': week_end.strftime('%Y-%m-%d'),
                'tasks_total': total,
                'tasks_completed': completed,
                'tasks_overdue': overdue,
                'completion_rate': round(completion_rate, 1),
                'total_focus_minutes': total_focus_minutes,
                'by_type': by_type,
                'achievement': achievement
            }
        })

    except Exception as e:
        logger.error(f"获取每周统计失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取每周统计失败: {str(e)}'}), 500

@personal_plan_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_settings():
    """获取用户设置"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalSettings

        settings = PersonalSettings.query.filter(
            PersonalSettings.user_id == current_user_id
        ).first()

        if not settings:
            settings = PersonalSettings(user_id=current_user_id)
            db.session.add(settings)
            db.session.commit()

        return jsonify({
            'success': True,
            'data': settings.to_dict()
        })

    except Exception as e:
        logger.error(f"获取设置失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取设置失败: {str(e)}'}), 500

@personal_plan_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    """更新用户设置"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalSettings

        data = request.get_json()

        settings = PersonalSettings.query.filter(
            PersonalSettings.user_id == current_user_id
        ).first()

        if not settings:
            settings = PersonalSettings(user_id=current_user_id)
            db.session.add(settings)

        if 'default_view' in data:
            settings.default_view = data['default_view']
        if 'pomodoro_duration' in data:
            settings.pomodoro_duration = data['pomodoro_duration']
        if 'break_duration' in data:
            settings.break_duration = data['break_duration']
        if 'long_break_duration' in data:
            settings.long_break_duration = data['long_break_duration']
        if 'work_streak_alert' in data:
            settings.work_streak_alert = data['work_streak_alert']
        if 'custom_tags' in data:
            settings.custom_tags = ','.join(data['custom_tags']) if isinstance(data['custom_tags'], list) else data['custom_tags']
        if 'tag_colors' in data:
            import json
            settings.tag_colors = json.dumps(data['tag_colors'])

        db.session.commit()

        return jsonify({
            'success': True,
            'data': settings.to_dict(),
            'message': '设置已更新'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"更新设置失败: {str(e)}")
        return jsonify({'success': False, 'message': f'更新设置失败: {str(e)}'}), 500

def parse_task_content(content):
    """智能解析任务内容"""
    result = {
        'title': content,
        'priority': 'medium',
        'quadrant': None,
        'tags': [],
        'scheduled_date': None,
        'scheduled_time': None,
        'estimated_minutes': None
    }

    priority_patterns = [
        (r'!{3,}', 'urgent'),
        (r'!!', 'high'),
        (r'!', 'medium')
    ]
    for pattern, priority in priority_patterns:
        if re.search(pattern, content):
            result['priority'] = priority
            content = re.sub(pattern, '', content)
            break

    if '明天下午' in content or '明天上午' in content or '明天' in content:
        tomorrow = datetime.utcnow().date() + timedelta(days=1)
        result['scheduled_date'] = tomorrow.strftime('%Y-%m-%d')
        if '下午' in content:
            result['scheduled_time'] = '14:00'
        elif '上午' in content:
            result['scheduled_time'] = '09:00'

    if '@' in content:
        tag_match = re.findall(r'@(\w+)', content)
        result['tags'] = tag_match
        content = re.sub(r'@\w+', '', content)

    time_pattern = r'(\d{1,2}):(\d{2})'
    time_match = re.search(time_pattern, content)
    if time_match:
        hour, minute = int(time_match.group(1)), int(time_match.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            result['scheduled_time'] = f"{hour:02d}:{minute:02d}"

    date_pattern = r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})'
    date_match = re.search(date_pattern, content)
    if date_match:
        result['scheduled_date'] = date_match.group(1).replace('/', '-')

    duration_pattern = r'(\d+)(?:分钟|min)'
    duration_match = re.search(duration_pattern, content)
    if duration_match:
        result['estimated_minutes'] = int(duration_match.group(1))

    result['title'] = content.strip()

    if result['priority'] == 'urgent':
        result['quadrant'] = 1
    elif result['priority'] == 'high':
        result['quadrant'] = 2

    return result

def get_priority_color(priority):
    """获取优先级对应的颜色"""
    colors = {
        'urgent': '#F56C6C',
        'high': '#E6A23C',
        'medium': '#409EFF',
        'low': '#909399'
    }
    return colors.get(priority, '#409EFF')

def calculate_streak(records):
    """计算连续打卡天数"""
    if not records:
        return 0

    sorted_records = sorted(records, key=lambda x: x.completed_date, reverse=True)
    streak = 0
    expected_date = datetime.utcnow().date()

    for record in sorted_records:
        record_date = record.completed_date if isinstance(record.completed_date, datetime) else record.completed_date
        if isinstance(record_date, datetime):
            record_date = record_date.date()

        if record_date == expected_date:
            streak += 1
            expected_date -= timedelta(days=1)
        elif record_date == expected_date + timedelta(days=1):
            expected_date = record_date - timedelta(days=1)
            streak += 1
            expected_date -= timedelta(days=1)
        else:
            break

    return streak

def generate_achievement_message(completed, total, focus_minutes):
    """生成成就总结"""
    if total == 0:
        return "还没有设置任务，明天加油哦！"

    rate = completed / total * 100

    if rate >= 100 and focus_minutes >= 120:
        return f"太棒了！本周完成全部{total}项任务，专注{focus_minutes}分钟，超越95%的用户！"
    elif rate >= 90:
        return f"优秀！本周完成{total}项任务中的{completed}项，超越85%的用户！"
    elif rate >= 70:
        return f"不错！本周完成{completed}项任务，继续保持！"
    elif rate >= 50:
        return f"本周完成{completed}项任务，完成率{rate:.0f}%，还有提升空间！"
    else:
        return f"本周完成了{completed}项任务，记得抽时间补上未完成的事项哦！"


# ==================== 增强功能 API ====================

@personal_plan_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    """获取工作台Dashboard数据"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask
        from datetime import date

        today = date.today().strftime('%Y-%m-%d')

        # 今日三件事（置顶任务或高优先级任务）
        top_tasks_query = PersonalTask.query.filter(
            PersonalTask.user_id == current_user_id,
            PersonalTask.status.in_(['todo', 'in_progress']),
            (PersonalTask.scheduled_date == today) | (PersonalTask.is_pinned == True)
        ).order_by(
            PersonalTask.is_pinned.desc(),
            db.case(
                (PersonalTask.priority == 'urgent', 1),
                (PersonalTask.priority == 'high', 2),
                (PersonalTask.priority == 'medium', 3),
                else_=4
            ),
            PersonalTask.order_index.asc()
        ).limit(3)

        top_tasks = [task.to_dict() for task in top_tasks_query.all()]

        # 超时任务
        overdue_tasks = PersonalTask.query.filter(
            PersonalTask.user_id == current_user_id,
            PersonalTask.status.in_(['todo', 'in_progress']),
            PersonalTask.due_date < today,
            PersonalTask.completed == False
        ).all()

        # 风险任务（今日截止且进度<50%）
        at_risk_tasks = PersonalTask.query.filter(
            PersonalTask.user_id == current_user_id,
            PersonalTask.status.in_(['todo', 'in_progress']),
            PersonalTask.due_date == today,
            (PersonalTask.progress < 50) | (PersonalTask.progress == None)
        ).all()

        # 今日统计
        today_tasks = PersonalTask.query.filter(
            PersonalTask.user_id == current_user_id,
            PersonalTask.scheduled_date == today
        ).all()

        today_completed = sum(1 for t in today_tasks if t.completed or t.status == 'done')
        today_total = len(today_tasks)

        return jsonify({
            'success': True,
            'data': {
                'top_three_tasks': top_tasks,
                'overdue_count': len(overdue_tasks),
                'overdue_tasks': [t.to_dict() for t in overdue_tasks[:5]],
                'at_risk_count': len(at_risk_tasks),
                'at_risk_tasks': [t.to_dict() for t in at_risk_tasks[:5]],
                'today_stats': {
                    'total': today_total,
                    'completed': today_completed,
                    'completion_rate': round((today_completed / today_total * 100) if today_total > 0 else 0, 1)
                }
            }
        })

    except Exception as e:
        logger.error(f"获取Dashboard数据失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取Dashboard数据失败: {str(e)}'}), 500


@personal_plan_bp.route('/tasks/<int:task_id>/subtasks', methods=['POST'])
@jwt_required()
def create_subtask(task_id):
    """为指定任务创建子任务"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask
        import json

        parent_task = PersonalTask.query.filter(
            PersonalTask.id == task_id,
            PersonalTask.user_id == current_user_id
        ).first()

        if not parent_task:
            return jsonify({'success': False, 'message': '父任务不存在'}), 404

        data = request.get_json()

        subtask = PersonalTask(
            user_id=current_user_id,
            parent_id=task_id,
            title=data.get('title'),
            description=data.get('description', ''),
            status='todo',
            priority=data.get('priority', 'medium'),
            estimated_minutes=data.get('estimated_minutes'),
            due_date=data.get('due_date'),
            tags=parent_task.tags
        )

        db.session.add(subtask)
        db.session.commit()

        # 更新父任务的进度
        update_parent_progress(parent_task)

        return jsonify({
            'success': True,
            'data': subtask.to_dict(),
            'message': '子任务创建成功'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"创建子任务失败: {str(e)}")
        return jsonify({'success': False, 'message': f'创建子任务失败: {str(e)}'}), 500


@personal_plan_bp.route('/tasks/<int:task_id>/subtasks', methods=['GET'])
@jwt_required()
def get_subtasks(task_id):
    """获取任务的所有子任务"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask

        task = PersonalTask.query.filter(
            PersonalTask.id == task_id,
            PersonalTask.user_id == current_user_id
        ).first()

        if not task:
            return jsonify({'success': False, 'message': '任务不存在'}), 404

        subtasks = PersonalTask.query.filter(
            PersonalTask.parent_id == task_id
        ).order_by(PersonalTask.order_index.asc()).all()

        return jsonify({
            'success': True,
            'data': {
                'subtasks': [s.to_dict() for s in subtasks],
                'total': len(subtasks)
            }
        })

    except Exception as e:
        logger.error(f"获取子任务失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取子任务失败: {str(e)}'}), 500


@personal_plan_bp.route('/tasks/batch', methods=['PUT'])
@jwt_required()
def batch_update_tasks():
    """批量更新任务"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask
        import json

        data = request.get_json()
        task_ids = data.get('task_ids', [])
        action = data.get('action')
        updates = data.get('updates', {})

        if not task_ids:
            return jsonify({'success': False, 'message': '请选择要操作的任务'}), 400

        tasks = PersonalTask.query.filter(
            PersonalTask.id.in_(task_ids),
            PersonalTask.user_id == current_user_id
        ).all()

        if not tasks:
            return jsonify({'success': False, 'message': '未找到指定的任务'}), 404

        updated_count = 0
        for task in tasks:
            if action == 'complete':
                task.status = 'done'
                task.completed = True
                task.completed_at = datetime.utcnow()
                task.progress = 100
            elif action == 'start':
                task.status = 'in_progress'
                task.started_at = datetime.utcnow()
            elif action == 'cancel':
                task.status = 'cancelled'
            elif action == 'update':
                if 'tags' in updates:
                    task.tags = updates['tags']
                if 'priority' in updates:
                    task.priority = updates['priority']
                if 'due_date' in updates:
                    task.due_date = updates['due_date']
                if 'status' in updates:
                    task.status = updates['status']

            updated_count += 1

            # 如果有子任务，递归更新
            if action == 'complete':
                subtasks = PersonalTask.query.filter(PersonalTask.parent_id == task.id).all()
                for subtask in subtasks:
                    subtask.status = 'done'
                    subtask.completed = True
                    subtask.progress = 100

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'已成功更新 {updated_count} 个任务',
            'data': {'updated_count': updated_count}
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"批量更新任务失败: {str(e)}")
        return jsonify({'success': False, 'message': f'批量更新任务失败: {str(e)}'}), 500


@personal_plan_bp.route('/tasks/<int:task_id>/toggle-complete', methods=['POST'])
@jwt_required()
def toggle_task_complete(task_id):
    """切换任务完成状态"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask

        task = PersonalTask.query.filter(
            PersonalTask.id == task_id,
            PersonalTask.user_id == current_user_id
        ).first()

        if not task:
            return jsonify({'success': False, 'message': '任务不存在'}), 404

        task.completed = not task.completed

        if task.completed:
            task.status = 'done'
            task.progress = 100
            task.completed_at = datetime.utcnow()
        else:
            task.status = 'todo'
            task.progress = 0
            task.completed_at = None

        # 更新父任务进度
        if task.parent_id:
            parent_task = PersonalTask.query.get(task.parent_id)
            if parent_task:
                update_parent_progress(parent_task)

        db.session.commit()

        return jsonify({
            'success': True,
            'data': task.to_dict(),
            'message': f'任务已{"完成" if task.completed else "重新打开"}'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"切换任务状态失败: {str(e)}")
        return jsonify({'success': False, 'message': f'切换任务状态失败: {str(e)}'}), 500


@personal_plan_bp.route('/tasks/<int:task_id>/progress', methods=['PUT'])
@jwt_required()
def update_task_progress(task_id):
    """更新任务进度"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PersonalTask

        data = request.get_json()
        progress = data.get('progress')

        if progress is None or not (0 <= progress <= 100):
            return jsonify({'success': False, 'message': '进度值必须在0-100之间'}), 400

        task = PersonalTask.query.filter(
            PersonalTask.id == task_id,
            PersonalTask.user_id == current_user_id
        ).first()

        if not task:
            return jsonify({'success': False, 'message': '任务不存在'}), 404

        task.progress = progress

        # 自动更新状态
        if progress >= 100:
            task.status = 'done'
            task.completed = True
            task.completed_at = datetime.utcnow()
        elif progress > 0 and task.status == 'todo':
            task.status = 'in_progress'

        # 更新父任务进度
        if task.parent_id:
            parent_task = PersonalTask.query.get(task.parent_id)
            if parent_task:
                update_parent_progress(parent_task)

        db.session.commit()

        return jsonify({
            'success': True,
            'data': task.to_dict(),
            'message': f'进度已更新至 {progress}%'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"更新进度失败: {str(e)}")
        return jsonify({'success': False, 'message': f'更新进度失败: {str(e)}'}), 500


@personal_plan_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_templates():
    """获取计划模板列表"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PlanTemplate

        templates = PlanTemplate.query.filter(
            PlanTemplate.user_id == current_user_id
        ).order_by(PlanTemplate.created_at.desc()).all()

        return jsonify({
            'success': True,
            'data': {
                'templates': [t.to_dict() for t in templates],
                'total': len(templates)
            }
        })

    except Exception as e:
        logger.error(f"获取模板列表失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取模板列表失败: {str(e)}'}), 500


@personal_plan_bp.route('/templates', methods=['POST'])
@jwt_required()
def create_template():
    """创建计划模板"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PlanTemplate
        import json

        data = request.get_json()

        template = PlanTemplate(
            user_id=current_user_id,
            name=data.get('name'),
            description=data.get('description', ''),
            template_type=data.get('template_type', 'daily'),
            tasks_template=json.dumps(data.get('tasks_template', []), ensure_ascii=False),
            is_default=data.get('is_default', False)
        )

        # 如果设为默认，取消其他默认模板
        if template.is_default:
            PlanTemplate.query.filter(
                PlanTemplate.user_id == current_user_id,
                PlanTemplate.id != template.id
            ).update({'is_default': False})

        db.session.add(template)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': template.to_dict(),
            'message': '模板创建成功'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"创建模板失败: {str(e)}")
        return jsonify({'success': False, 'message': f'创建模板失败: {str(e)}'}), 500


@personal_plan_bp.route('/templates/<int:template_id>', methods=['PUT'])
@jwt_required()
def update_template(template_id):
    """更新计划模板"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PlanTemplate
        import json

        template = PlanTemplate.query.filter(
            PlanTemplate.id == template_id,
            PlanTemplate.user_id == current_user_id
        ).first()

        if not template:
            return jsonify({'success': False, 'message': '模板不存在'}), 404

        data = request.get_json()

        if 'name' in data:
            template.name = data['name']
        if 'description' in data:
            template.description = data['description']
        if 'template_type' in data:
            template.template_type = data['template_type']
        if 'tasks_template' in data:
            template.tasks_template = json.dumps(data['tasks_template'], ensure_ascii=False)
        if 'is_default' in data and data['is_default']:
            PlanTemplate.query.filter(
                PlanTemplate.user_id == current_user_id,
                PlanTemplate.id != template_id
            ).update({'is_default': False})
            template.is_default = True

        db.session.commit()

        return jsonify({
            'success': True,
            'data': template.to_dict(),
            'message': '模板更新成功'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"更新模板失败: {str(e)}")
        return jsonify({'success': False, 'message': f'更新模板失败: {str(e)}'}), 500


@personal_plan_bp.route('/templates/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_template(template_id):
    """删除计划模板"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PlanTemplate

        template = PlanTemplate.query.filter(
            PlanTemplate.id == template_id,
            PlanTemplate.user_id == current_user_id
        ).first()

        if not template:
            return jsonify({'success': False, 'message': '模板不存在'}), 404

        db.session.delete(template)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '模板删除成功'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"删除模板失败: {str(e)}")
        return jsonify({'success': False, 'message': f'删除模板失败: {str(e)}'}), 500


@personal_plan_bp.route('/templates/<int:template_id>/apply', methods=['POST'])
@jwt_required()
def apply_template(template_id):
    """应用模板创建任务"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import PlanTemplate, PersonalTask
        import json

        template = PlanTemplate.query.filter(
            PlanTemplate.id == template_id,
            PlanTemplate.user_id == current_user_id
        ).first()

        if not template:
            return jsonify({'success': False, 'message': '模板不存在'}), 404

        data = request.get_json()
        base_date = data.get('date', datetime.utcnow().strftime('%Y-%m-%d'))

        tasks_template = json.loads(template.tasks_template)
        created_tasks = []

        for task_data in tasks_template:
            task = PersonalTask(
                user_id=current_user_id,
                title=task_data.get('title', ''),
                description=task_data.get('description', ''),
                status='todo',
                priority=task_data.get('priority', 'medium'),
                scheduled_date=base_date,
                estimated_minutes=task_data.get('estimated_minutes'),
                tags=','.join(task_data.get('tags', [])) if task_data.get('tags') else ''
            )
            db.session.add(task)
            created_tasks.append(task)

        db.session.commit()

        return jsonify({
            'success': True,
            'data': {
                'created_tasks': [t.to_dict() for t in created_tasks],
                'count': len(created_tasks)
            },
            'message': f'已从模板创建 {len(created_tasks)} 个任务'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"应用模板失败: {str(e)}")
        return jsonify({'success': False, 'message': f'应用模板失败: {str(e)}'}), 500


@personal_plan_bp.route('/reviews', methods=['GET'])
@jwt_required()
def get_reviews():
    """获取复盘记录列表"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import ReviewRecord

        reviews = ReviewRecord.query.filter(
            ReviewRecord.user_id == current_user_id
        ).order_by(ReviewRecord.date_range_start.desc()).all()

        return jsonify({
            'success': True,
            'data': {
                'reviews': [r.to_dict() for r in reviews],
                'total': len(reviews)
            }
        })

    except Exception as e:
        logger.error(f"获取复盘记录失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取复盘记录失败: {str(e)}'}), 500


@personal_plan_bp.route('/reviews/generate', methods=['POST'])
@jwt_required()
def generate_review():
    """自动生成复盘报告"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import ReviewRecord, PersonalTask
        import json
        from datetime import date, timedelta

        data = request.get_json()
        review_type = data.get('review_type', 'weekly')
        custom_start = data.get('date_start')
        custom_end = data.get('date_end')

        today = date.today()

        if review_type == 'weekly':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif review_type == 'monthly':
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        else:
            start_date = datetime.strptime(custom_start, '%Y-%m-%d').date()
            end_date = datetime.strptime(custom_end, '%Y-%m-%d').date()

        # 统计任务数据
        tasks = PersonalTask.query.filter(
            PersonalTask.user_id == current_user_id,
            PersonalTask.scheduled_date >= start_date.strftime('%Y-%m-%d'),
            PersonalTask.scheduled_date <= end_date.strftime('%Y-%m-%d')
        ).all()

        total_planned = len(tasks)
        total_completed = sum(1 for t in tasks if t.completed or t.status == 'done')
        total_planned_hours = sum(t.estimated_minutes or 0 for t in tasks) / 60.0
        total_actual_hours = sum(t.actual_minutes or 0 for t in tasks) / 60.0

        # 超时任务统计
        overdue_tasks = [
            t for t in tasks
            if t.due_date and t.due_date < today.strftime('%Y-%m-%d')
            and not (t.completed or t.status == 'done')
        ]
        overdue_count = len(overdue_tasks)

        if overdue_tasks:
            avg_overdue_days = sum(
                (today - datetime.strptime(t.due_date, '%Y-%m-%d').date()).days
                for t in overdue_tasks
            ) / len(overdue_tasks)
        else:
            avg_overdue_days = 0

        # 生成周报文案
        summary_text = generate_weekly_summary(start_date, end_date, tasks, total_planned, total_completed)

        review = ReviewRecord(
            user_id=current_user_id,
            title=f"{start_date.strftime('%Y年%m月%d')} - {end_date.strftime('%m月%d日')} 复盘",
            date_range_start=start_date.strftime('%Y-%m-%d'),
            date_range_end=end_date.strftime('%Y-%m-%d'),
            review_type=review_type,
            total_planned=total_planned,
            total_completed=total_completed,
            total_planned_hours=round(total_planned_hours, 1),
            total_actual_hours=round(total_actual_hours, 1),
            overdue_count=overdue_count,
            avg_overdue_days=round(avg_overdue_days, 1),
            summary_text=summary_text
        )

        db.session.add(review)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': review.to_dict(),
            'message': '复盘报告生成成功'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"生成复盘报告失败: {str(e)}")
        return jsonify({'success': False, 'message': f'生成复盘报告失败: {str(e)}'}), 500


@personal_plan_bp.route('/reviews/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """更新复盘报告"""
    models = get_models()
    db = models['db']
    current_user_id = get_jwt_identity()

    try:
        from enhanced_app import ReviewRecord

        review = ReviewRecord.query.filter(
            ReviewRecord.id == review_id,
            ReviewRecord.user_id == current_user_id
        ).first()

        if not review:
            return jsonify({'success': False, 'message': '复盘记录不存在'}), 404

        data = request.get_json()

        editable_fields = ['key_achievements', 'challenges', 'lessons_learned', 'next_week_plan', 'summary_text']
        for field in editable_fields:
            if field in data:
                setattr(review, field, data[field])

        db.session.commit()

        return jsonify({
            'success': True,
            'data': review.to_dict(),
            'message': '复盘报告更新成功'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"更新复盘报告失败: {str(e)}")
        return jsonify({'success': False, 'message': f'更新复盘报告失败: {str(e)}'}), 500


# ==================== 辅助函数 ====================

def update_parent_progress(parent_task):
    """根据子任务完成情况更新父任务进度"""
    from enhanced_app import PersonalTask

    subtasks = PersonalTask.query.filter(PersonalTask.parent_id == parent_task.id).all()

    if subtasks:
        completed_count = sum(1 for s in subtasks if s.completed)
        total_count = len(subtasks)
        parent_task.progress = int((completed_count / total_count) * 100)

        if parent_task.progress >= 100:
            parent_task.completed = True
            parent_task.status = 'done'
        else:
            parent_task.completed = False
            if parent_task.progress > 0:
                parent_task.status = 'in_progress'


def generate_weekly_summary(start_date, end_date, tasks, total_planned, total_completed):
    """自动生成周报摘要文案"""
    completion_rate = (total_completed / total_planned * 100) if total_planned > 0 else 0

    # 获取重点工作（已完成的高优先级任务）
    key_tasks = [
        t.title for t in tasks
        if (t.completed or t.status == 'done')
        and t.priority in ['urgent', 'high']
    ][:5]

    # 获取未完成任务
    incomplete_tasks = [
        t.title for t in tasks
        if not (t.completed or t.status == 'done')
    ][:5]

    summary = f"""## 本周工作复盘 ({start_date.strftime('%m/%d')} - {end_date.strftime('%m/%d')})

### 📊 整体概况
- 计划任务：{total_planned} 项
- 已完成：{total_completed} 项
- 完成率：{completion_rate:.1f}%

### ✅ 重点工作成果
"""

    if key_tasks:
        summary += "\n".join([f"- {task}" for task in key_tasks])
    else:
        summary += "- 暂无高优先级任务完成"

    summary += "\n\n### ⚠️ 未完成事项\n"
    if incomplete_tasks:
        summary += "\n".join([f"- {task}" for task in incomplete_tasks])
    else:
        summary += "- 所有任务已完成！🎉"

    summary += "\n\n### 💡 下周建议\n"
    if completion_rate >= 90:
        summary += "表现优秀！继续保持高效的工作节奏。"
    elif completion_rate >= 70:
        summary += "整体良好，可适当优化时间分配，提高专注度。"
    elif completion_rate >= 50:
        summary += "建议回顾未完成任务原因，合理调整下周计划。"
    else:
        summary += "需要重点关注任务规划与执行，建议减少任务数量，聚焦重点。"

    return summary