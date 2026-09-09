from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from utils.time_utils import now_china
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
import json
import re

# 统一权限系统
from utils.permission_unified import (
    require_perm as _require_perm,
    require_any as _require_any,
    require_admin as _require_admin,
    check_perm as _check_perm,
    check_module as _check_module,
    filter_query_by_perm as _filter_query_by_perm,
    is_system_admin as _is_system_admin,
)

# 创建考勤管理蓝图
attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

# 请假类型中文映射
LEAVE_TYPE_TEXT_MAP = {
    'annual_leave': '年假',
    'sick_leave': '病假',
    'personal_leave': '事假',
    'marriage_leave': '婚假',
    'maternity_leave': '产假',
    'paternity_leave': '陪产假',
    'bereavement_leave': '丧假',
    'other': '调休假',
}

def leave_type_to_text(leave_type):
    return LEAVE_TYPE_TEXT_MAP.get(leave_type, leave_type)

# 延迟导入工具函数和模型
def get_db():
    from enhanced_app import db
    return db

def get_logger():
    from enhanced_app import logger
    return logger

def get_create_audit_log():
    from enhanced_app import create_audit_log
    return create_audit_log

def get_create_notification():
    from enhanced_app import create_notification
    return create_notification

def require_permission(perm_code):
    """考勤子路由权限校验装饰器

    用法：@require_permission(PermissionCodes.CLOCK_IN)
    规则：
        - 系统管理员（is_super_admin）放行
        - 职位是 admin/manager 放行
        - 否则必须 check_permission(perm_code) 为 True，否则 403
    """
    from functools import wraps
    from flask import jsonify as _jsonify
    from models.permissions import PermissionCodes

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            db = get_db()
            from enhanced_app import User
            current_user_id = get_jwt_identity()
            user = db.session.query(User).get(current_user_id)
            if not user:
                return _jsonify({'error': '用户不存在'}), 404
            if user.is_super_admin:
                return f(*args, **kwargs)
            position_info = user.get_position_info()
            if position_info and (position_info.is_admin or position_info.is_manager):
                return f(*args, **kwargs)
            if not user.check_permission(perm_code):
                return _jsonify({'error': '权限不足', 'code': 'PERMISSION_DENIED', 'required_permission': perm_code}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

def get_models():
    from enhanced_app import (
        User, AttendanceRecord, LeaveApplication, OvertimeApplication, 
        AttendanceException, WorkCalendar, ShiftSchedule, UserShift,
        AttendanceStatus, ApprovalStatus, Activity
    )
    return User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity

# 同步考勤数据
def sync_attendance_data(application):
    """同步考勤数据"""
    db = get_db()
    logger = get_logger()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()
    
    try:
        if application.status == ApprovalStatus.APPROVED.value:
            start_date = application.start_date
            end_date = application.end_date
            
            current_date = start_date
            while current_date <= end_date:
                attendance_record = AttendanceRecord.query.filter_by(
                    user_id=application.user_id,
                    record_date=current_date
                ).first()
                
                if not attendance_record:
                    attendance_record = AttendanceRecord(
                        user_id=application.user_id,
                        record_date=current_date,
                        status=AttendanceStatus.LEAVE.value,
                        work_hours=0
                    )
                    db.session.add(attendance_record)
                else:
                    attendance_record.status = AttendanceStatus.LEAVE.value
                    attendance_record.work_hours = 0
                
                current_date += timedelta(days=1)
            
            db.session.commit()
            logger.info(f"考勤数据同步完成: 申请ID {application.id}")
    except Exception as e:
        logger.error(f"Error syncing attendance data: {str(e)}")

# 获取工作日历
@attendance_bp.route('/work-calendar', methods=['GET'])
@jwt_required()
@require_permission('attendance:view')
def get_work_calendar():
    """获取工作日历"""
    db = get_db()
    logger = get_logger()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        year = request.args.get('year', now_china().year, type=int)
        month = request.args.get('month', now_china().month, type=int)
        
        calendar = WorkCalendar.query.filter(
            db.extract('year', WorkCalendar.date) == year,
            db.extract('month', WorkCalendar.date) == month
        ).all()
        
        return jsonify([day.to_dict() for day in calendar])
    except Exception as e:
        logger.error(f"Error getting work calendar: {str(e)}")
        return jsonify({'error': '获取工作日历失败'}), 500

# 获取考勤记录
@attendance_bp.route('/records', methods=['GET'])
@jwt_required()
@require_permission('attendance:view')
def get_attendance_records():
    """获取考勤记录"""
    db = get_db()
    logger = get_logger()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        start_date = request.args.get('start_date') or request.args.get('dateRange[0]')
        end_date = request.args.get('end_date') or request.args.get('dateRange[1]')
        
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            user_id = request.args.get('userId', type=int)
        
        status = request.args.get('status')
        
        query = AttendanceRecord.query
        
        if current_user.role != 'admin':
            query = query.filter_by(user_id=current_user_id)
        elif user_id:
            query = query.filter_by(user_id=user_id)

        if start_date:
            query = query.filter(AttendanceRecord.record_date >= start_date)
        if end_date:
            # 仅传入日期（YYYY-MM-DD）时补齐到当天结束，避免 record_date 带时分秒
            # 在文本比较中大于纯日期字符串而漏掉最后一天的记录
            if len(str(end_date).strip()) == 10:
                end_date = str(end_date).strip() + ' 23:59:59'
            query = query.filter(AttendanceRecord.record_date <= end_date)

        if status:
            query = query.filter(AttendanceRecord.status == status)
        
        query = query.order_by(AttendanceRecord.record_date.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        records = pagination.items
        
        result = []
        for record in records:
            user = record.user
            # 关联班次：优先使用记录自身存储的 user_shift_id / shift_id，
            # 否则按 user_id + record_date 反查当天的 user_shift
            shift_data = None
            effective_user_shift = None
            try:
                if getattr(record, 'user_shift_id', None):
                    effective_user_shift = UserShift.query.get(record.user_shift_id)
                if not effective_user_shift and getattr(record, 'shift_id', None):
                    # 仅按 shift_id 查不到 user_shift，按 shift_id 构造一个简易关联
                    shift_obj = ShiftSchedule.query.get(record.shift_id)
                    if shift_obj:
                        shift_data = {
                            'id': shift_obj.id,
                            'name': shift_obj.name,
                            'start_time': shift_obj.start_time,
                            'end_time': shift_obj.end_time,
                            'flexible_range': shift_obj.flexible_range,
                            'overtime_threshold': shift_obj.overtime_threshold,
                            'shift_type': shift_obj.shift_type
                        }

                if not effective_user_shift and record.user_id and record.record_date:
                    rec_date = record.record_date.date() if hasattr(record.record_date, 'date') else record.record_date
                    rec_weekday = str(rec_date.isoweekday())
                    # 获取日期范围内的所有排班，按生效日期降序
                    candidate_shifts = UserShift.query.filter(
                        UserShift.user_id == record.user_id,
                        UserShift.effective_date <= rec_date,
                        db.or_(
                            UserShift.expire_date == None,
                            UserShift.expire_date >= rec_date
                        )
                    ).order_by(UserShift.effective_date.desc()).all()
                    # 优先匹配 days_of_week 包含当天星期几的排班，
                    # days_of_week 为空表示每天都适用
                    for candidate in candidate_shifts:
                        candidate_shift = candidate.shift
                        if not candidate_shift:
                            continue
                        if not candidate_shift.days_of_week:
                            effective_user_shift = candidate
                            break
                        weekdays = [d.strip() for d in candidate_shift.days_of_week.split(',')]
                        if rec_weekday in weekdays:
                            effective_user_shift = candidate
                            break

                if effective_user_shift and not shift_data:
                    shift_obj = effective_user_shift.shift
                    if shift_obj:
                        shift_data = {
                            'id': shift_obj.id,
                            'name': shift_obj.name,
                            'start_time': shift_obj.start_time,
                            'end_time': shift_obj.end_time,
                            'flexible_range': shift_obj.flexible_range,
                            'overtime_threshold': shift_obj.overtime_threshold,
                            'shift_type': shift_obj.shift_type
                        }
            except Exception as shift_query_error:
                logger.warning(f"查询班次信息失败: {shift_query_error}")

            if not shift_data:
                # 没有排班数据时回退到默认值，保持前端展示不空白
                shift_data = {'id': None, 'name': '正常班', 'start_time': None, 'end_time': None}

            record_data = {
                'id': record.id,
                'user': {
                    'id': user.id if user else None,
                    'username': user.username if user else '未知',
                    # 中文姓名按「姓+名」显示（last_name=姓, first_name=名）
                    'name': f"{user.last_name or ''}{user.first_name or ''}".strip() or user.username if user else '未知'
                } if user else {'id': None, 'username': '未知', 'name': '未知'},
                'date': record.record_date.strftime('%Y-%m-%d') if record.record_date else None,
                'shift': shift_data,
                'user_shift_id': effective_user_shift.id if effective_user_shift else getattr(record, 'user_shift_id', None),
                'clock_in_time': record.clock_in_time.strftime('%H:%M:%S') if record.clock_in_time else None,
                'clock_in_ip': record.clock_in_ip,
                'clock_out_time': record.clock_out_time.strftime('%H:%M:%S') if record.clock_out_time else None,
                'clock_out_ip': record.clock_out_ip,
                'work_hours': record.work_hours,
                'overtime_hours': record.overtime_hours,
                'late_minutes': record.late_minutes,
                'early_leave_minutes': record.early_leave_minutes,
                'status': record.status
            }
            result.append(record_data)
        
        return jsonify({
            'records': result,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        logger.error(f"Error getting attendance records: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '获取考勤记录失败'}), 500

# 获取单条考勤记录详情
@attendance_bp.route('/records/<int:record_id>', methods=['GET'])
@jwt_required()
@require_permission('attendance:view')
def get_attendance_record_detail(record_id):
    """获取单条考勤记录详情"""
    db = get_db()
    logger = get_logger()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        record = AttendanceRecord.query.get(record_id)
        if not record:
            return jsonify({'error': '考勤记录不存在'}), 404

        # 非管理员只能查看自己的记录
        if current_user.role != 'admin' and record.user_id != int(current_user_id):
            return jsonify({'error': '无权查看此记录'}), 403

        user = record.user
        record_data = {
            'id': record.id,
            'user': {
                'id': user.id if user else None,
                'username': user.username if user else '未知',
                'name': f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username if user else '未知'
            } if user else {'id': None, 'username': '未知', 'name': '未知'},
            'date': record.record_date.strftime('%Y-%m-%d') if record.record_date else None,
            'shift': {'name': '正常班'},
            'clock_in_time': record.clock_in_time.strftime('%Y-%m-%d %H:%M:%S') if record.clock_in_time else None,
            'clock_in_ip': record.clock_in_ip,
            'clock_in_location': record.clock_in_location,
            'clock_out_time': record.clock_out_time.strftime('%Y-%m-%d %H:%M:%S') if record.clock_out_time else None,
            'clock_out_ip': record.clock_out_ip,
            'clock_out_location': record.clock_out_location,
            'work_hours': record.work_hours,
            'overtime_hours': record.overtime_hours,
            'late_minutes': record.late_minutes,
            'early_leave_minutes': record.early_leave_minutes,
            'status': record.status,
            'note': record.note,
            'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S') if record.created_at else None,
            'updated_at': record.updated_at.strftime('%Y-%m-%d %H:%M:%S') if record.updated_at else None
        }

        return jsonify(record_data)
    except Exception as e:
        logger.error(f"Error getting attendance record detail: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '获取考勤记录详情失败'}), 500

# 打卡
@attendance_bp.route('/clock-in', methods=['POST'])
@jwt_required()
def clock_in():
    """上班打卡"""
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        current_date = now_china().replace(hour=0, minute=0, second=0, microsecond=0)
        
        existing_record = AttendanceRecord.query.filter(
            AttendanceRecord.user_id == current_user_id,
            AttendanceRecord.record_date == current_date
        ).first()
        
        if existing_record and existing_record.clock_in_time:
            return jsonify({'error': '今日已打卡'}), 400
        
        client_ip = request.remote_addr or '0.0.0.0'
        
        json_data = request.get_json(silent=True) or {}
        location = json_data.get('location')
        
        today = now_china().date()
        today_weekday = str(today.isoweekday())
        # 获取日期范围内的所有排班，按生效日期降序
        candidate_shifts = UserShift.query.filter(
            UserShift.user_id == current_user_id,
            UserShift.effective_date <= today,
            db.or_(
                UserShift.expire_date == None,
                UserShift.expire_date >= today
            )
        ).order_by(UserShift.effective_date.desc()).all()
        # 优先匹配 days_of_week 包含当天星期几的排班，
        # days_of_week 为空表示每天都适用
        user_shift = None
        for candidate in candidate_shifts:
            candidate_shift_obj = candidate.shift
            if not candidate_shift_obj:
                continue
            if not candidate_shift_obj.days_of_week:
                user_shift = candidate
                break
            weekdays = [d.strip() for d in candidate_shift_obj.days_of_week.split(',')]
            if today_weekday in weekdays:
                user_shift = candidate
                break

        shift = None
        if user_shift:
            shift = ShiftSchedule.query.get(user_shift.shift_id)

        late_minutes = 0
        if shift:
            shift_start = datetime.strptime(shift.start_time, '%H:%M').time()
            actual_time = now_china().time()
            if actual_time > shift_start:
                shift_start_dt = datetime.combine(today, shift_start)
                actual_dt = datetime.combine(today, actual_time)
                late_minutes = int((actual_dt - shift_start_dt).total_seconds() / 60)

        if existing_record:
            existing_record.clock_in_time = now_china()
            existing_record.clock_in_ip = client_ip
            existing_record.clock_in_location = location
            existing_record.late_minutes = late_minutes
            if late_minutes > 0:
                existing_record.status = AttendanceStatus.LATE.value
            else:
                existing_record.status = AttendanceStatus.PRESENT.value
            record = existing_record
        else:
            record = AttendanceRecord(
                user_id=current_user_id,
                record_date=current_date,
                clock_in_time=now_china(),
                clock_in_ip=client_ip,
                clock_in_location=location,
                late_minutes=late_minutes,
                status=AttendanceStatus.LATE.value if late_minutes > 0 else AttendanceStatus.PRESENT.value,
                work_hours=0
            )
            db.session.add(record)
        
        db.session.commit()
        
        create_audit_log(
            user_id=current_user_id,
            action='clock_in',
            resource_type='attendance',
            resource_id=record.id,
            details=f'上班打卡: {current_date}, IP: {client_ip}, 迟到: {late_minutes}分钟',
            request=request
        )
        
        return jsonify({'message': '打卡成功', 'record': record.to_dict()})
    except Exception as e:
        logger.error(f"Error clocking in: {str(e)}")
        return jsonify({'error': '打卡失败'}), 500

# 下班打卡
@attendance_bp.route('/clock-out', methods=['POST'])
@jwt_required()
def clock_out():
    """下班打卡"""
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        current_date = now_china().replace(hour=0, minute=0, second=0, microsecond=0)
        
        record = AttendanceRecord.query.filter_by(
            user_id=current_user_id,
            record_date=current_date
        ).first()
        
        if not record or not record.clock_in_time:
            return jsonify({'error': '请先进行上班打卡'}), 400
        
        if record.clock_out_time:
            return jsonify({'error': '今日已下班打卡'}), 400
        
        client_ip = request.remote_addr or '0.0.0.0'
        location = request.json.get('location') if request.json else None
        
        clock_out_time = now_china()
        record.clock_out_time = clock_out_time
        record.clock_out_ip = client_ip
        record.clock_out_location = location

        if record.clock_in_time and clock_out_time:
            # clock_in_time从数据库加载为时区无关，clock_out_time为时区感知，需统一
            clock_in = record.clock_in_time
            clock_out = clock_out_time
            if clock_out.tzinfo is not None and clock_in.tzinfo is None:
                clock_out = clock_out.replace(tzinfo=None)
            work_duration = clock_out - clock_in
            record.work_hours = work_duration.total_seconds() / 3600
        
        db.session.commit()
        
        create_audit_log(
            user_id=current_user_id,
            action='clock_out',
            resource_type='attendance',
            resource_id=record.id,
            details=f'下班打卡: {current_date}, IP: {client_ip}, 工作时长: {record.work_hours:.2f}小时',
            request=request
        )
        
        return jsonify({'message': '下班打卡成功', 'record': record.to_dict()})
    except Exception as e:
        logger.error(f"Error clocking out: {str(e)}")
        return jsonify({'error': '下班打卡失败'}), 500

# 获取今日考勤记录
@attendance_bp.route('/records/today', methods=['GET'])
@jwt_required()
@require_permission('attendance:view')
def get_today_record():
    """获取今日考勤记录"""
    db = get_db()
    logger = get_logger()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        today = now_china().replace(hour=0, minute=0, second=0, microsecond=0)
        
        record = AttendanceRecord.query.filter_by(
            user_id=current_user_id,
            record_date=today
        ).first()
        
        if record:
            user = record.user
            record_data = {
                'id': record.id,
                'user': {
                    'id': user.id if user else None,
                    'username': user.username if user else '未知',
                    # 中文姓名按「姓+名」显示（last_name=姓, first_name=名）
                    'name': f"{user.last_name or ''}{user.first_name or ''}".strip() or user.username if user else '未知'
                } if user else {'id': None, 'username': '未知', 'name': '未知'},
                'date': record.record_date.strftime('%Y-%m-%d') if record.record_date else None,
                'shift': {'name': '正常班'},
                'clock_in_time': record.clock_in_time.strftime('%H:%M:%S') if record.clock_in_time else None,
                'clock_in_ip': record.clock_in_ip,
                'clock_out_time': record.clock_out_time.strftime('%H:%M:%S') if record.clock_out_time else None,
                'clock_out_ip': record.clock_out_ip,
                'work_hours': record.work_hours,
                'overtime_hours': record.overtime_hours,
                'late_minutes': record.late_minutes,
                'early_leave_minutes': record.early_leave_minutes,
                'status': record.status
            }
            return jsonify(record_data)
        else:
            return jsonify(None)
    except Exception as e:
        logger.error(f"Error getting today record: {str(e)}")
        return jsonify({'error': '获取今日记录失败'}), 500

# 获取请假申请列表
@attendance_bp.route('/leave-applications', methods=['GET'])
@jwt_required()
@require_permission('attendance:view')
def get_leave_applications():
    """获取请假申请列表"""
    db = get_db()
    logger = get_logger()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        user_id = request.args.get('user_id', type=int)
        
        query = LeaveApplication.query.options(
            joinedload(LeaveApplication.user),
            joinedload(LeaveApplication.approver)
        )
        
        # 非管理员只能查看自己的申请
        if current_user.role != 'admin':
            query = query.filter_by(user_id=current_user_id)
        elif user_id:
            query = query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(LeaveApplication.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        applications = pagination.items
        
        result = []
        for app in applications:
            applicant = app.user
            approver = app.approver
            # 使用模型自带的 to_dict 获取多级审批等完整字段
            base_dict = app.to_dict()
            # 补充 applicant/approver 对象信息
            app_data = {
                **base_dict,
                'applicant': {
                    'id': applicant.id if applicant else None,
                    'username': applicant.username if applicant else '未知',
                    'name': f"{applicant.first_name or ''} {applicant.last_name or ''}".strip() or applicant.username if applicant else '未知'
                } if applicant else None,
                'approver': {
                    'id': approver.id if approver else None,
                    'username': approver.username if approver else None,
                    'name': f"{approver.first_name or ''} {approver.last_name or ''}".strip() or approver.username if approver else None
                } if approver else None,
                'attachment': base_dict.get('attachment_path'),
            }
            result.append(app_data)
        
        return jsonify({
            'applications': result,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        logger.error(f"Error getting leave applications: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '获取请假申请失败'}), 500

# 创建请假申请
@attendance_bp.route('/leave-applications', methods=['POST'])
@jwt_required()
@require_permission('attendance:leave_apply')
def create_leave_application():
    """提交请假申请"""
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()
    from models.enums import LeaveType

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        data = request.get_json(silent=True) or {}

        # 必填字段校验
        leave_type = data.get('leave_type')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        reason = data.get('reason')

        if not leave_type or not start_date_str or not end_date_str or not reason:
            return jsonify({'error': '请假类型、起止日期和请假原因均为必填项'}), 400

        # 解析日期
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': '开始日期格式错误，应为 YYYY-MM-DD'}), 400

        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': '结束日期格式错误，应为 YYYY-MM-DD'}), 400

        if end_date < start_date:
            return jsonify({'error': '结束日期不能早于开始日期'}), 400

        # 计算请假天数
        days = data.get('days')
        if days is None or days == '':
            days = (end_date - start_date).days + 1
        try:
            days = float(days)
        except (TypeError, ValueError):
            return jsonify({'error': '请假天数格式错误'}), 400
        if days <= 0:
            return jsonify({'error': '请假天数必须大于0'}), 400

        # 校验请假类型（兼容前端短名与枚举完整名）
        leave_type_aliases = {
            'annual': 'annual_leave',
            'sick': 'sick_leave',
            'personal': 'personal_leave',
            'compensatory': 'other',
            'marriage': 'marriage_leave',
            'maternity': 'maternity_leave',
            'paternity': 'paternity_leave',
            'bereavement': 'bereavement_leave',
        }
        if leave_type in leave_type_aliases:
            leave_type = leave_type_aliases[leave_type]
        valid_leave_types = {lt.value for lt in LeaveType}
        if leave_type not in valid_leave_types:
            return jsonify({'error': f'无效的请假类型: {leave_type}', 'valid_types': sorted(valid_leave_types)}), 400

        import json as _json

        # 多级审批配置（前端传来的审批层级列表）
        approval_levels_raw = data.get('approval_levels') or []
        is_multi_level = bool(data.get('is_multi_level')) and len(approval_levels_raw) > 0

        # 审批人（可选）
        approver_id = data.get('approver_id')
        # 如果是多级审批且已传approval_levels，approver_id取第一级审批人
        if is_multi_level:
            try:
                approver_id = int(approval_levels_raw[0]['approver_id'])
            except (TypeError, ValueError, IndexError, KeyError):
                approver_id = None
        elif approver_id is not None and approver_id != '':
            try:
                approver_id = int(approver_id)
            except (TypeError, ValueError):
                approver_id = None

        if approver_id is not None:
            approver = User.query.get(approver_id)
            if not approver:
                return jsonify({'error': '指定的审批人不存在'}), 400
        else:
            approver_id = None

        # 紧急情况标记
        emergency_flag = bool(data.get('emergency_flag', False))

        # 附件路径
        attachment_path = data.get('attachment_path') or data.get('attachment') or None

        # 构建审批层级JSON（确保每级状态为pending）
        approval_levels_json = None
        current_approver_level = 1
        if is_multi_level:
            levels_list = []
            for lv in approval_levels_raw:
                try:
                    approver_of_level = User.query.get(int(lv['approver_id']))
                    levels_list.append({
                        'level': int(lv.get('level', len(levels_list) + 1)),
                        'approver_id': int(lv['approver_id']),
                        'approver_name': (f"{approver_of_level.first_name or ''} {approver_of_level.last_name or ''}".strip() or approver_of_level.username) if approver_of_level else '未知',
                        'status': 'pending',
                        'comment': None,
                        'approved_at': None
                    })
                except (TypeError, ValueError, KeyError):
                    continue
            if levels_list:
                approval_levels_json = _json.dumps(levels_list, ensure_ascii=False)

        application = LeaveApplication(
            user_id=current_user_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            days=days,
            reason=reason,
            status=ApprovalStatus.PENDING.value,
            approver_id=approver_id,
            emergency_flag=emergency_flag,
            attachment_path=attachment_path,
            approval_levels=approval_levels_json,
            current_approver_level=current_approver_level
        )

        db.session.add(application)
        db.session.commit()

        try:
            create_audit_log(
                user_id=current_user_id,
                action='create',
                resource_type='leave_application',
                resource_id=application.id,
                details=f'提交请假申请: {leave_type} {start_date_str} 至 {end_date_str}, {days}天',
                request=request
            )
        except Exception:
            pass

        # 通知审批人有新的请假申请待审批
        if approver_id:
            try:
                create_notification = get_create_notification()
                create_notification(
                    user_id=approver_id,
                    notification_type='approval_request',
                    title=f'{current_user.username} 提交了请假申请，待你审批',
                    content=f'请假类型: {leave_type_to_text(leave_type)}，{start_date_str} 至 {end_date_str}，共 {days} 天。原因: {reason}'
                )
            except Exception:
                pass

        return jsonify({
            'message': '请假申请提交成功',
            'application': application.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating leave application: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '提交请假申请失败'}), 500


# 更新请假申请
@attendance_bp.route('/leave-applications/<int:application_id>', methods=['PUT'])
@jwt_required()
@require_permission('attendance:leave_apply')
def update_leave_application(application_id):
    """修改待审批的请假申请"""
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, _, LeaveApplication, _, _, _, _, _, _, ApprovalStatus, _ = get_models()
    from models.enums import LeaveType

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        application = LeaveApplication.query.get(application_id)
        if not application:
            return jsonify({'error': '请假申请不存在'}), 404

        # 只有申请人本人或管理员可以修改
        if str(application.user_id) != str(current_user_id) and current_user.role != 'admin':
            return jsonify({'error': '无权修改该请假申请'}), 403

        # 只有待审批状态可以修改
        if application.status != ApprovalStatus.PENDING.value:
            return jsonify({'error': f'当前状态为 {application.status}，不可修改'}), 400

        data = request.get_json(silent=True) or {}

        # 请假类型
        if 'leave_type' in data:
            leave_type = data.get('leave_type')
            leave_type_aliases = {
                'annual': 'annual_leave',
                'sick': 'sick_leave',
                'personal': 'personal_leave',
                'compensatory': 'other',
                'marriage': 'marriage_leave',
                'maternity': 'maternity_leave',
                'paternity': 'paternity_leave',
                'bereavement': 'bereavement_leave',
            }
            if leave_type in leave_type_aliases:
                leave_type = leave_type_aliases[leave_type]
            valid_leave_types = {lt.value for lt in LeaveType}
            if leave_type not in valid_leave_types:
                return jsonify({'error': f'无效的请假类型: {leave_type}'}), 400
            application.leave_type = leave_type

        # 起止日期
        start_date = application.start_date
        end_date = application.end_date
        if 'start_date' in data:
            try:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
                application.start_date = start_date
            except ValueError:
                return jsonify({'error': '开始日期格式错误，应为 YYYY-MM-DD'}), 400
        if 'end_date' in data:
            try:
                end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
                application.end_date = end_date
            except ValueError:
                return jsonify({'error': '结束日期格式错误，应为 YYYY-MM-DD'}), 400

        if end_date < start_date:
            return jsonify({'error': '结束日期不能早于开始日期'}), 400

        # 请假天数
        if 'days' in data:
            days = data.get('days')
            if days is None or days == '':
                days = (end_date - start_date).days + 1
            try:
                days = float(days)
            except (TypeError, ValueError):
                return jsonify({'error': '请假天数格式错误'}), 400
            if days <= 0:
                return jsonify({'error': '请假天数必须大于0'}), 400
            application.days = days

        # 请假原因
        if 'reason' in data:
            reason = data.get('reason')
            if not reason:
                return jsonify({'error': '请假原因不能为空'}), 400
            application.reason = reason

        # 紧急情况
        if 'emergency_flag' in data:
            application.emergency_flag = bool(data.get('emergency_flag', False))

        # 附件
        if 'attachment_path' in data or 'attachment' in data:
            application.attachment_path = data.get('attachment_path') or data.get('attachment') or None

        # 审批人
        if 'approver_id' in data:
            approver_id = data.get('approver_id')
            if approver_id is not None and approver_id != '':
                try:
                    approver_id = int(approver_id)
                except (TypeError, ValueError):
                    return jsonify({'error': '审批人ID格式错误'}), 400
                approver = User.query.get(approver_id)
                if not approver:
                    return jsonify({'error': '指定的审批人不存在'}), 400
                application.approver_id = approver_id
            else:
                application.approver_id = None
            # 修改审批人后重置多级审批配置
            application.approval_levels = None
            application.current_approver_level = 1

        db.session.commit()

        try:
            create_audit_log(
                user_id=current_user_id,
                action='update',
                resource_type='leave_application',
                resource_id=application.id,
                details=f'修改请假申请: {application.leave_type}',
                request=request
            )
        except Exception:
            pass

        return jsonify({
            'message': '请假申请修改成功',
            'application': application.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating leave application: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '修改请假申请失败'}), 500


# 获取加班申请列表
@attendance_bp.route('/overtime-applications', methods=['GET'])
@jwt_required()
@require_permission('attendance:view')
def get_overtime_applications():
    """获取加班申请列表"""
    db = get_db()
    logger = get_logger()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        user_id = request.args.get('user_id', type=int)
        
        query = OvertimeApplication.query.options(
            joinedload(OvertimeApplication.user),
            joinedload(OvertimeApplication.approver)
        )
        
        # 非管理员只能查看自己的申请
        if current_user.role != 'admin':
            query = query.filter_by(user_id=current_user_id)
        elif user_id:
            query = query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(OvertimeApplication.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        applications = pagination.items
        
        result = []
        for app in applications:
            applicant = app.user
            approver = app.approver
            # 计算加班时长（小时）
            total_hours = 0
            try:
                if app.start_time and app.end_time:
                    sh, sm = map(int, app.start_time.split(':'))
                    eh, em = map(int, app.end_time.split(':'))
                    total_hours = round((eh * 60 + em - sh * 60 - sm) / 60, 1)
            except Exception:
                total_hours = 0
            # 申请人名称
            user_real_name = ''
            user_name = ''
            if applicant:
                user_real_name = f"{applicant.first_name or ''} {applicant.last_name or ''}".strip()
                user_name = applicant.username
            # 审批人名称
            approver_name = ''
            if approver:
                approver_name = f"{approver.first_name or ''} {approver.last_name or ''}".strip() or approver.username
            app_data = {
                'id': app.id,
                'user_id': app.user_id,
                'user_real_name': user_real_name or user_name,
                'user_name': user_name,
                'applicant': {
                    'id': applicant.id if applicant else None,
                    'username': applicant.username if applicant else '未知',
                    'name': user_real_name or (applicant.username if applicant else '未知')
                } if applicant else None,
                'date': app.date.strftime('%Y-%m-%d') if app.date and hasattr(app.date, 'strftime') else (str(app.date) if app.date else None),
                'overtime_date': app.date.strftime('%Y-%m-%d') if app.date and hasattr(app.date, 'strftime') else (str(app.date) if app.date else None),
                'start_time': app.start_time,
                'end_time': app.end_time,
                'total_hours': total_hours,
                'reason': app.reason,
                'status': app.status.value if hasattr(app.status, 'value') else str(app.status),
                'approver_id': app.approver_id,
                'approver_name': approver_name or None,
                'approver': {
                    'id': approver.id if approver else None,
                    'username': approver.username if approver else None,
                    'name': approver_name or None
                } if approver else None,
                'approved_at': app.approved_at.isoformat() if app.approved_at else None,
                'rejection_reason': app.rejection_reason,
                'created_at': app.created_at.isoformat() if app.created_at else None
            }
            result.append(app_data)
        
        return jsonify({
            'applications': result,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        logger.error(f"Error getting overtime applications: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '获取加班申请失败'}), 500

# 创建加班申请
@attendance_bp.route('/overtime', methods=['POST'])
@jwt_required()
@require_permission('attendance:overtime_apply')
def create_overtime_application():
    """创建加班申请"""
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        data = request.get_json(silent=True) or {}

        # 必填字段校验
        date_str = data.get('date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        reason = data.get('reason')

        if not date_str or not start_time or not end_time or not reason:
            return jsonify({'error': '日期、开始时间、结束时间和加班原因均为必填项'}), 400

        # 解析日期
        try:
            overtime_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': '日期格式错误，应为 YYYY-MM-DD'}), 400

        # 时间格式校验
        import re
        time_pattern = re.compile(r'^([01]\d|2[0-3]):[0-5]\d$')
        if not time_pattern.match(start_time) or not time_pattern.match(end_time):
            return jsonify({'error': '时间格式错误，应为 HH:MM'}), 400

        # 审批人（可选）
        approver_id = data.get('approver_id')
        if approver_id is not None:
            try:
                approver_id = int(approver_id)
            except (TypeError, ValueError):
                approver_id = None

        # 转换方式（pay=转加班费，leave=转调休，默认转调休）
        compensation_type = data.get('compensation_type') or 'leave'
        if compensation_type not in ('pay', 'leave'):
            return jsonify({'error': '转换方式无效，应为 pay（转加班费）或 leave（转调休）'}), 400

        application = OvertimeApplication(
            user_id=current_user_id,
            date=overtime_date,
            start_time=start_time,
            end_time=end_time,
            reason=reason,
            status=ApprovalStatus.PENDING.value,
            compensation_type=compensation_type,
            approver_id=approver_id
        )

        db.session.add(application)
        db.session.commit()

        try:
            create_audit_log(
                user_id=current_user_id,
                action='create',
                resource_type='overtime_application',
                resource_id=application.id,
                details=f'提交加班申请: {date_str} {start_time}-{end_time}',
                request=request
            )
        except Exception:
            pass

        # 通知审批人有新的加班申请待审批
        if approver_id:
            try:
                create_notification = get_create_notification()
                create_notification(
                    user_id=approver_id,
                    notification_type='approval_request',
                    title=f'{current_user.username} 提交了加班申请，待你审批',
                    content=f'加班日期: {date_str}，{start_time}-{end_time}。原因: {reason}'
                )
            except Exception:
                pass

        return jsonify({
            'message': '加班申请提交成功',
            'application': application.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating overtime application: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '提交加班申请失败'}), 500

# 审批/拒绝请假申请
@attendance_bp.route('/leave-applications/<int:application_id>/approve', methods=['POST'])
@jwt_required()
@require_permission('attendance:leave_approve')
def approve_leave_application(application_id):
    """审批/拒绝请假申请（action=approve|reject）"""
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, _, LeaveApplication, _, _, _, _, _, _, ApprovalStatus, _ = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        application = LeaveApplication.query.get(application_id)
        if not application:
            return jsonify({'error': '请假申请不存在'}), 404

        if application.status != ApprovalStatus.PENDING.value:
            return jsonify({'error': f'当前状态为 {application.status}，不可重复审批'}), 400

        data = request.get_json(silent=True) or {}
        action = (data.get('action') or 'approve').lower()
        comment = data.get('comment') or data.get('rejection_reason') or ''

        import json as _json

        now = now_china()

        # 解析多级审批配置
        approval_levels_list = []
        is_multi_level = False
        current_level_index = 0  # 当前级在列表中的位置（0-based）
        total_levels = 1

        if application.approval_levels:
            try:
                approval_levels_list = _json.loads(application.approval_levels)
                is_multi_level = True
                total_levels = len(approval_levels_list)
                current_level_index = (application.current_approver_level or 1) - 1
                if current_level_index >= total_levels or current_level_index < 0:
                    current_level_index = 0
            except Exception:
                approval_levels_list = []
                is_multi_level = False

        # 校验当前用户是否是当前级审批人
        if is_multi_level and approval_levels_list:
            current_level_info = approval_levels_list[current_level_index]
            if str(current_level_info.get('approver_id')) != str(current_user_id):
                return jsonify({'error': f'你不是第{application.current_approver_level or 1}级审批人'}), 403
        else:
            # 单级审批：校验 approver_id
            if application.approver_id and str(application.approver_id) != str(current_user_id):
                return jsonify({'error': '你不是该申请的审批人'}), 403

        if action == 'reject':
            if not comment:
                return jsonify({'error': '拒绝时必须填写审批意见'}), 400
            application.status = ApprovalStatus.REJECTED.value
            # 更新多级审批JSON中当前级及后续级状态
            if is_multi_level and approval_levels_list:
                approval_levels_list[current_level_index]['status'] = 'rejected'
                approval_levels_list[current_level_index]['comment'] = comment
                approval_levels_list[current_level_index]['approved_at'] = now.isoformat() if hasattr(now, 'isoformat') else str(now)
                # 后续级标记为 rejected
                for i in range(current_level_index + 1, len(approval_levels_list)):
                    if approval_levels_list[i].get('status') == 'pending':
                        approval_levels_list[i]['status'] = 'rejected'
                        approval_levels_list[i]['comment'] = '前一级已拒绝，流程终止'
                application.approval_levels = _json.dumps(approval_levels_list, ensure_ascii=False)
        else:
            # 批准
            if is_multi_level and approval_levels_list:
                # 更新当前级状态为 approved
                approval_levels_list[current_level_index]['status'] = 'approved'
                approval_levels_list[current_level_index]['comment'] = comment
                approval_levels_list[current_level_index]['approved_at'] = now.isoformat() if hasattr(now, 'isoformat') else str(now)
                application.approval_comment = comment
                application.approved_at = now
                application.approver_id = current_user_id

                if current_level_index + 1 < total_levels:
                    # 还有下一级，推进流程
                    next_level = approval_levels_list[current_level_index + 1]
                    application.current_approver_level = next_level.get('level', current_level_index + 2)
                    application.approver_id = int(next_level['approver_id'])
                    application.status = ApprovalStatus.PENDING.value
                    application.approval_levels = _json.dumps(approval_levels_list, ensure_ascii=False)
                    db.session.commit()

                    # 通知下一级审批人
                    try:
                        create_notification = get_create_notification()
                        next_approver = User.query.get(application.approver_id)
                        next_approver_name = (f"{next_approver.first_name or ''} {next_approver.last_name or ''}".strip() or next_approver.username) if next_approver else '未知'
                        create_notification(
                            user_id=application.approver_id,
                            notification_type='approval_request',
                            title=f'[{next_approver_name}] 请假申请需第{application.current_approver_level}级审批',
                            content=f'请假类型: {leave_type_to_text(application.leave_type)}，{application.start_date.strftime("%Y-%m-%d") if application.start_date else ""} 至 {application.end_date.strftime("%Y-%m-%d") if application.end_date else ""}，共 {application.days} 天。前一级审批人已通过。'
                        )
                    except Exception:
                        pass

                    # 审计日志
                    try:
                        create_audit_log(
                            user_id=current_user_id,
                            action='approve',
                            resource_type='leave_application',
                            resource_id=application.id,
                            details=f"第{current_level_index + 1}级审批通过，流转至第{application.current_approver_level}级审批人",
                            request=request
                        )
                    except Exception:
                        pass

                    # 不通知申请人（流程未结束）
                    return jsonify({
                        'message': f'第{current_level_index + 1}级审批通过，已流转至第{application.current_approver_level}级',
                        'application': application.to_dict()
                    })
                else:
                    # 最后一级批准，整体通过
                    application.status = ApprovalStatus.APPROVED.value
                    application.approval_levels = _json.dumps(approval_levels_list, ensure_ascii=False)
            else:
                # 单级审批直接通过
                application.status = ApprovalStatus.APPROVED.value
                application.approval_comment = comment

        if action != 'reject':
            application.approver_id = current_user_id
        application.approved_at = now

        db.session.commit()

        try:
            create_audit_log(
                user_id=current_user_id,
                action='approve' if action != 'reject' else 'reject',
                resource_type='leave_application',
                resource_id=application.id,
                details=f"{'审批通过' if action != 'reject' else '拒绝'}请假申请 #{application.id}",
                request=request
            )
        except Exception:
            pass

        # 通知申请人审批结果
        if application.user_id and application.user_id != current_user_id:
            try:
                create_notification = get_create_notification()
                result_text = '已通过' if action != 'reject' else '被拒绝'
                create_notification(
                    user_id=application.user_id,
                    notification_type='approval_result',
                    title=f'你的请假申请{result_text}',
                    content=f'请假类型: {leave_type_to_text(application.leave_type)}，审批意见: {comment or "无"}'
                )
            except Exception:
                pass

        return jsonify({
            'message': '审批通过' if action != 'reject' else '已拒绝',
            'application': application.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error approving leave application: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '审批操作失败'}), 500

# 审批/拒绝加班申请
@attendance_bp.route('/overtime-applications/<int:application_id>/approve', methods=['POST'])
@jwt_required()
@require_permission('attendance:overtime_approve')
def approve_overtime_application(application_id):
    """审批/拒绝加班申请（action=approve|reject）"""
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, _, _, OvertimeApplication, _, _, _, _, _, ApprovalStatus, _ = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        application = OvertimeApplication.query.get(application_id)
        if not application:
            return jsonify({'error': '加班申请不存在'}), 404

        if application.status != ApprovalStatus.PENDING.value:
            return jsonify({'error': f'当前状态为 {application.status}，不可重复审批'}), 400

        data = request.get_json(silent=True) or {}
        action = (data.get('action') or 'approve').lower()
        comment = data.get('comment') or data.get('rejection_reason') or ''

        if action == 'reject':
            if not comment:
                return jsonify({'error': '拒绝时必须填写审批意见'}), 400
            application.status = ApprovalStatus.REJECTED.value
            application.rejection_reason = comment
        else:
            application.status = ApprovalStatus.APPROVED.value
            if comment:
                application.rejection_reason = comment

        application.approver_id = current_user_id
        application.approved_at = now_china()
        db.session.commit()

        try:
            create_audit_log(
                user_id=current_user_id,
                action='approve' if action != 'reject' else 'reject',
                resource_type='overtime_application',
                resource_id=application.id,
                details=f"{'审批通过' if action != 'reject' else '拒绝'}加班申请 #{application.id}",
                request=request
            )
        except Exception:
            pass

        # 通知申请人审批结果
        if application.user_id and application.user_id != current_user_id:
            try:
                create_notification = get_create_notification()
                result_text = '已通过' if action != 'reject' else '被拒绝'
                ot_date = application.date.strftime('%Y-%m-%d') if application.date else '未知'
                create_notification(
                    user_id=application.user_id,
                    notification_type='approval_result',
                    title=f'你的加班申请{result_text}',
                    content=f'加班日期: {ot_date}，审批意见: {comment or "无"}'
                )
            except Exception:
                pass

        return jsonify({
            'message': '审批通过' if action != 'reject' else '已拒绝',
            'application': application.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error approving overtime application: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '审批操作失败'}), 500

# 获取班次列表
@attendance_bp.route('/shifts', methods=['GET'])
@jwt_required()
@require_permission('attendance:shift_manage')
def get_shifts():
    """获取班次列表"""
    db = get_db()
    logger = get_logger()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()

    try:
        shifts = ShiftSchedule.query.filter_by(is_active=True).all()
        return jsonify([shift.to_dict() for shift in shifts])
    except Exception as e:
        logger.error(f"Error getting shifts: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '获取班次列表失败'}), 500

# 创建班次
@attendance_bp.route('/shifts', methods=['POST'])
@jwt_required()
@require_permission('attendance:shift_manage')
def create_shift():
    """创建班次"""
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, _, _, _, _, _, ShiftSchedule, _, _, _, _ = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': '无权限操作'}), 403

        data = request.get_json(silent=True) or {}
        name = (data.get('name') or '').strip()
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        shift_type = data.get('shift_type') or 'day'

        if not name or not start_time or not end_time:
            return jsonify({'error': '班次名称、开始时间、结束时间为必填项'}), 400

        import re
        time_pattern = re.compile(r'^([01]\d|2[0-3]):[0-5]\d$')
        if not time_pattern.match(start_time) or not time_pattern.match(end_time):
            return jsonify({'error': '时间格式错误，应为 HH:MM'}), 400

        if ShiftSchedule.query.filter_by(name=name).first():
            return jsonify({'error': '班次名称已存在'}), 400

        shift = ShiftSchedule(
            name=name,
            start_time=start_time,
            end_time=end_time,
            shift_type=shift_type,
            flexible_range=int(data.get('flexible_range') or 30),
            overtime_threshold=int(data.get('overtime_threshold') or 60),
            is_active=bool(data.get('is_active', True)),
            days_of_week=','.join(str(d) for d in data.get('days_of_week', [])) if isinstance(data.get('days_of_week'), list) else (data.get('days_of_week') or ''),
            description=data.get('description')
        )
        db.session.add(shift)
        db.session.commit()

        try:
            create_audit_log(
                user_id=current_user_id,
                action='create',
                resource_type='shift_schedule',
                resource_id=shift.id,
                details=f'创建班次: {shift.name}',
                request=request
            )
        except Exception:
            pass

        return jsonify({'message': '创建成功', 'shift': shift.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating shift: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '创建班次失败'}), 500

# 更新班次
@attendance_bp.route('/shifts/<int:shift_id>', methods=['PUT'])
@jwt_required()
@require_permission('attendance:shift_manage')
def update_shift(shift_id):
    """更新班次"""
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, _, _, _, _, _, ShiftSchedule, _, _, _, _ = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': '无权限操作'}), 403

        shift = ShiftSchedule.query.get(shift_id)
        if not shift:
            return jsonify({'error': '班次不存在'}), 404

        data = request.get_json(silent=True) or {}

        if 'name' in data:
            new_name = (data.get('name') or '').strip()
            if not new_name:
                return jsonify({'error': '班次名称不能为空'}), 400
            if new_name != shift.name and ShiftSchedule.query.filter_by(name=new_name).first():
                return jsonify({'error': '班次名称已存在'}), 400
            shift.name = new_name
        if 'start_time' in data:
            shift.start_time = data.get('start_time')
        if 'end_time' in data:
            shift.end_time = data.get('end_time')
        if 'shift_type' in data and data.get('shift_type'):
            shift.shift_type = data.get('shift_type')
        if 'flexible_range' in data and data.get('flexible_range') is not None:
            shift.flexible_range = int(data.get('flexible_range'))
        if 'overtime_threshold' in data and data.get('overtime_threshold') is not None:
            shift.overtime_threshold = int(data.get('overtime_threshold'))
        if 'is_active' in data:
            shift.is_active = bool(data.get('is_active'))
        if 'days_of_week' in data:
            dow = data.get('days_of_week')
            if isinstance(dow, list):
                shift.days_of_week = ','.join(str(d) for d in dow)
            else:
                shift.days_of_week = dow or ''
        if 'description' in data:
            shift.description = data.get('description')

        db.session.commit()

        try:
            create_audit_log(
                user_id=current_user_id,
                action='update',
                resource_type='shift_schedule',
                resource_id=shift.id,
                details=f'更新班次: {shift.name}',
                request=request
            )
        except Exception:
            pass

        return jsonify({'message': '更新成功', 'shift': shift.to_dict()})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating shift: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '更新班次失败'}), 500

# 删除班次
@attendance_bp.route('/shifts/<int:shift_id>', methods=['DELETE'])
@jwt_required()
@require_permission('attendance:shift_manage')
def delete_shift(shift_id):
    """删除班次（软删除：停用）"""
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, _, _, _, _, _, ShiftSchedule, UserShift, _, _, _ = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': '无权限操作'}), 403

        shift = ShiftSchedule.query.get(shift_id)
        if not shift:
            return jsonify({'error': '班次不存在'}), 404

        # 如果已被用户排班使用，禁止硬删除；采用停用方式
        in_use = UserShift.query.filter_by(shift_id=shift_id).first()
        if in_use:
            shift.is_active = False
            db.session.commit()
            return jsonify({'message': '班次已被使用，已切换为停用状态'})
        else:
            db.session.delete(shift)
            db.session.commit()
            return jsonify({'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting shift: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '删除班次失败'}), 500

# 获取用户班次安排
@attendance_bp.route('/user-shifts', methods=['GET'])
@jwt_required()
@require_permission('attendance:user_shift_assign')
def get_user_shifts():
    """获取用户班次安排"""
    db = get_db()
    logger = get_logger()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        date_str = request.args.get('date')
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else now_china().date()
        
        # 查询所有用户的班次安排
        user_shifts = UserShift.query.filter(
            UserShift.effective_date <= target_date,
            db.or_(
                UserShift.expire_date == None,
                UserShift.expire_date >= target_date
            )
        ).all()
        
        result = []
        for us in user_shifts:
            user = us.user
            shift = us.shift
            # 部门信息
            department = None
            if user:
                try:
                    department = user.department
                except Exception:
                    department = None
            # 真实姓名
            full_name = ''
            if user:
                full_name = f"{getattr(user, 'first_name', '') or ''} {getattr(user, 'last_name', '') or ''}".strip()
            display_name = full_name or (user.username if user else '未知')

            result.append({
                'id': us.id,
                'user_id': us.user_id,
                'user': {
                    'id': user.id if user else None,
                    'username': user.username if user else '未知',
                    'name': display_name,
                    'first_name': getattr(user, 'first_name', None) if user else None,
                    'last_name': getattr(user, 'last_name', None) if user else None,
                    'department': department,
                    'position': getattr(user, 'position', None) if user else None
                } if user else None,
                'shift_id': us.shift_id,
                'shift': {
                    'id': shift.id if shift else None,
                    'name': shift.name if shift else '未知',
                    'start_time': shift.start_time if shift else None,
                    'end_time': shift.end_time if shift else None,
                    'flexible_range': shift.flexible_range if shift else None,
                    'overtime_threshold': shift.overtime_threshold if shift else None,
                    'shift_type': shift.shift_type if shift else None
                } if shift else None,
                'effective_date': us.effective_date.strftime('%Y-%m-%d') if us.effective_date else None,
                'expire_date': us.expire_date.strftime('%Y-%m-%d') if us.expire_date else None
            })

        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting user shifts: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '获取用户班次安排失败'}), 500

# 批量创建用户排班
@attendance_bp.route('/user-shifts/batch', methods=['POST'])
@jwt_required()
@require_permission('attendance:user_shift_assign')
def create_user_shifts_batch():
    """批量为多个用户在日期范围内创建/更新排班
    
    apply_mode: 'overlay'（叠加，默认）或 'replace'（替换已有重叠排班）
    """
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, _, _, _, _, _, ShiftSchedule, UserShift, _, _, _ = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': '无权限操作'}), 403

        data = request.get_json(silent=True) or {}
        user_ids = data.get('user_ids') or []
        shift_id = data.get('shift_id')
        date_range = data.get('date_range') or []
        apply_mode = data.get('apply_mode', 'overlay')  # overlay=叠加, replace=替换

        if not user_ids or not shift_id:
            return jsonify({'error': '员工和班次均为必填项'}), 400

        if apply_mode not in ('overlay', 'replace'):
            return jsonify({'error': '应用方式参数无效，应为 overlay 或 replace'}), 400

        # date_range 可能是 ['2025-01-01', '2025-01-31'] 或 null（表示永久生效）
        shift = ShiftSchedule.query.get(shift_id)
        if not shift:
            return jsonify({'error': '班次不存在'}), 404

        effective_date = None
        expire_date = None
        if isinstance(date_range, list) and len(date_range) == 2 and date_range[0] and date_range[1]:
            try:
                effective_date = datetime.strptime(date_range[0], '%Y-%m-%d')
                expire_date = datetime.strptime(date_range[1], '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': '日期格式错误，应为 YYYY-MM-DD'}), 400
            if expire_date < effective_date:
                return jsonify({'error': '结束日期不能早于开始日期'}), 400

        new_effective = effective_date or now_china().replace(hour=0, minute=0, second=0, microsecond=0)
        new_expire = expire_date

        created_count = 0
        replaced_count = 0
        for uid in user_ids:
            try:
                uid_int = int(uid)
            except (TypeError, ValueError):
                continue
            target_user = User.query.get(uid_int)
            if not target_user:
                continue

            # 替换模式：删除日期范围内已有的重叠排班记录
            if apply_mode == 'replace':
                # 查询与新排班日期范围重叠的已有记录
                overlap_query = UserShift.query.filter(UserShift.user_id == uid_int)
                
                if new_expire:
                    # 新排班有结束日期：已有记录的生效日期 <= 新结束日期
                    overlap_query = overlap_query.filter(UserShift.effective_date <= new_expire)
                    # 已有记录的失效日期为空 或 失效日期 >= 新开始日期
                    overlap_query = overlap_query.filter(
                        db.or_(
                            UserShift.expire_date == None,
                            UserShift.expire_date >= new_effective
                        )
                    )
                else:
                    # 新排班永久生效：所有已有记录都重叠（因为新记录没有结束日期）
                    pass  # 该用户的所有排班记录都将被替换
                
                overlapping = overlap_query.all()
                if overlapping:
                    replaced_count += len(overlapping)
                    for us_old in overlapping:
                        db.session.delete(us_old)

            us = UserShift(
                user_id=uid_int,
                shift_id=shift_id,
                effective_date=new_effective,
                expire_date=new_expire
            )
            db.session.add(us)
            created_count += 1

        db.session.commit()

        try:
            mode_text = '替换模式' if apply_mode == 'replace' else '叠加模式'
            details = f'批量排班({mode_text}): 班次ID={shift_id}, 员工数={created_count}'
            if apply_mode == 'replace' and replaced_count > 0:
                details += f', 替换已有记录{replaced_count}条'
            create_audit_log(
                user_id=current_user_id,
                action='batch_create',
                resource_type='user_shift',
                resource_id=None,
                details=details,
                request=request
            )
        except Exception:
            pass

        if apply_mode == 'replace':
            return jsonify({
                'message': f'批量排班成功，创建 {created_count} 条记录，替换 {replaced_count} 条已有记录',
                'count': created_count,
                'replaced_count': replaced_count
            }), 201
        return jsonify({'message': f'批量排班成功，共创建 {created_count} 条记录', 'count': created_count}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error batch creating user shifts: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '批量排班失败'}), 500

# 删除用户排班安排
@attendance_bp.route('/user-shifts/<int:user_shift_id>', methods=['DELETE'])
@jwt_required()
@require_permission('attendance:user_shift_assign')
def delete_user_shift(user_shift_id):
    """删除用户排班安排"""
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, _, _, _, _, _, _, UserShift, _, _, _ = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': '无权限操作'}), 403

        us = UserShift.query.get(user_shift_id)
        if not us:
            return jsonify({'error': '排班安排不存在'}), 404

        db.session.delete(us)
        db.session.commit()

        try:
            create_audit_log(
                user_id=current_user_id,
                action='delete',
                resource_type='user_shift',
                resource_id=user_shift_id,
                details=f'删除排班: ID={user_shift_id}',
                request=request
            )
        except Exception:
            pass

        return jsonify({'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting user shift: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '删除排班失败'}), 500

# 获取考勤异常列表
@attendance_bp.route('/exceptions', methods=['GET'])
@jwt_required()
@require_permission('attendance:view')
def get_exceptions():
    """获取考勤异常列表"""
    db = get_db()
    logger = get_logger()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        user_id = request.args.get('user_id', type=int)
        department = request.args.get('department')
        period = request.args.get('period', 'daily')
        date_str = request.args.get('date')
        
        query = AttendanceException.query
        
        # 非管理员只能查看自己的异常
        if current_user.role != 'admin':
            query = query.filter_by(user_id=current_user_id)
        elif user_id:
            query = query.filter_by(user_id=user_id)
        
        # 按部门筛选
        if department and current_user.role == 'admin':
            query = query.join(User, AttendanceException.user_id == User.id).filter(User.department == department)
        
        # 按状态筛选
        if status:
            query = query.filter_by(status=status)
        
        # 按日期筛选
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if period == 'daily':
                query = query.filter(
                    db.func.date(AttendanceException.record_date) == target_date
                )
            elif period == 'weekly':
                week_start = target_date - timedelta(days=target_date.weekday())
                week_end = week_start + timedelta(days=6)
                query = query.filter(
                    AttendanceException.record_date >= week_start,
                    AttendanceException.record_date <= week_end
                )
            elif period == 'monthly':
                query = query.filter(
                    db.extract('year', AttendanceException.record_date) == target_date.year,
                    db.extract('month', AttendanceException.record_date) == target_date.month
                )
        
        query = query.order_by(AttendanceException.record_date.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        exceptions = pagination.items
        
        result = []
        for exc in exceptions:
            user = exc.user
            approver = exc.approver
            result.append({
                'id': exc.id,
                'user_id': exc.user_id,
                'user': {
                    'id': user.id if user else None,
                    'username': user.username if user else '未知',
                    # 中文姓名按「姓+名」显示（last_name=姓, first_name=名）
                    'name': f"{user.last_name or ''}{user.first_name or ''}".strip() or user.username if user else '未知',
                    'department': user.department if user else None
                } if user else None,
                'record_date': exc.record_date.strftime('%Y-%m-%d') if exc.record_date else None,
                'exception_type': exc.exception_type,
                'reason': exc.reason,
                'status': exc.status,
                'approver_id': exc.approver_id,
                'approver': {
                    'id': approver.id if approver else None,
                    'username': approver.username if approver else None,
                    'name': f"{approver.first_name or ''} {approver.last_name or ''}".strip() or approver.username if approver else None
                } if approver else None,
                'approved_at': exc.approved_at.isoformat() if exc.approved_at else None,
                'created_at': exc.created_at.isoformat() if exc.created_at else None
            })
        
        return jsonify({
            'records': result,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        logger.error(f"Error getting exceptions: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '获取考勤异常失败'}), 500

# 获取考勤统计
@attendance_bp.route('/statistics', methods=['GET'])
@jwt_required()
@require_permission('attendance:view')
def get_statistics():
    """获取考勤统计"""
    db = get_db()
    logger = get_logger()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        period = request.args.get('period', 'daily')
        date_str = request.args.get('date')
        department = request.args.get('department')
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else now_china().date()
        
        # 确定日期范围
        if period == 'daily':
            start_date = end_date = target_date
        elif period == 'weekly':
            start_date = target_date - timedelta(days=target_date.weekday())
            end_date = start_date + timedelta(days=6)
        elif period == 'monthly':
            start_date = target_date.replace(day=1)
            if target_date.month == 12:
                end_date = target_date.replace(year=target_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = target_date.replace(month=target_date.month + 1, day=1) - timedelta(days=1)
        else:
            start_date = end_date = target_date
        
        # 构建基础查询
        query = AttendanceRecord.query.filter(
            AttendanceRecord.record_date >= start_date,
            AttendanceRecord.record_date <= end_date
        )
        
        # 按部门筛选
        if department:
            query = query.join(User).filter(User.department == department)
        
        # 非管理员只能查看自己的统计
        if current_user.role != 'admin':
            query = query.filter_by(user_id=current_user_id)
        
        records = query.all()
        
        # 计算统计数据
        total_employees = len(set(r.user_id for r in records))
        present_count = len([r for r in records if r.status == AttendanceStatus.PRESENT.value])
        late_count = len([r for r in records if r.status == AttendanceStatus.LATE.value])
        absent_count = len([r for r in records if r.status == AttendanceStatus.ABSENT.value])
        leave_count = len([r for r in records if r.status == AttendanceStatus.LEAVE.value])
        
        total_work_hours = sum(r.work_hours for r in records if r.work_hours)
        total_overtime_hours = sum(r.overtime_hours for r in records if r.overtime_hours)
        
        attendance_rate = (present_count / total_employees * 100) if total_employees > 0 else 0
        
        # 获取加班统计
        overtime_query = OvertimeApplication.query.filter(
            db.func.date(OvertimeApplication.date) >= start_date,
            db.func.date(OvertimeApplication.date) <= end_date,
            OvertimeApplication.status == ApprovalStatus.APPROVED.value
        )
        
        if department and current_user.role == 'admin':
            overtime_query = overtime_query.join(User, OvertimeApplication.user_id == User.id).filter(User.department == department)
        if current_user.role != 'admin':
            overtime_query = overtime_query.filter_by(user_id=current_user_id)
        
        overtime_records = overtime_query.all()
        
        return jsonify({
            'total_employees': total_employees,
            'attendance_rate': round(attendance_rate, 2),
            'present_count': present_count,
            'late_count': late_count,
            'absent_count': absent_count,
            'leave_count': leave_count,
            'total_work_hours': round(total_work_hours, 2),
            'total_overtime_hours': round(total_overtime_hours, 2),
            'overtime_count': len(overtime_records),
            'period': period,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        })
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '获取考勤统计失败'}), 500

# 获取报告概览
@attendance_bp.route('/reports/overview', methods=['GET'])
@jwt_required()
@require_permission('attendance:report')
def get_reports_overview():
    """获取考勤报告概览"""
    db = get_db()
    logger = get_logger()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        period = request.args.get('period', 'daily')
        date_str = request.args.get('date')
        department = request.args.get('department')
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else now_china().date()
        
        # 确定日期范围
        if period == 'daily':
            start_date = end_date = target_date
        elif period == 'weekly':
            start_date = target_date - timedelta(days=target_date.weekday())
            end_date = start_date + timedelta(days=6)
        elif period == 'monthly':
            start_date = target_date.replace(day=1)
            if target_date.month == 12:
                end_date = target_date.replace(year=target_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = target_date.replace(month=target_date.month + 1, day=1) - timedelta(days=1)
        else:
            start_date = end_date = target_date
        
        # 构建用户查询
        user_query = User.query
        if department:
            user_query = user_query.filter_by(department=department)
        
        total_employees = user_query.count()
        
        # 获取考勤记录
        record_query = AttendanceRecord.query.filter(
            AttendanceRecord.record_date >= start_date,
            AttendanceRecord.record_date <= end_date
        )
        
        if department:
            record_query = record_query.join(User).filter(User.department == department)
        if current_user.role != 'admin':
            record_query = record_query.filter_by(user_id=current_user_id)
        
        records = record_query.all()
        
        # 计算概览数据
        present_count = len([r for r in records if r.status == AttendanceStatus.PRESENT.value])
        late_count = len([r for r in records if r.status == AttendanceStatus.LATE.value])
        early_leave_count = len([r for r in records if r.early_leave_minutes and r.early_leave_minutes > 0])
        missing_count = len([r for r in records if r.status == AttendanceStatus.ABSENT.value])
        
        attendance_rate = (present_count / total_employees * 100) if total_employees > 0 else 0
        
        # 计算加班时长
        total_overtime_hours = sum(r.overtime_hours for r in records if r.overtime_hours)
        
        return jsonify({
            'totalEmployees': total_employees,
            'attendanceRate': round(attendance_rate, 2),
            'lateCount': late_count,
            'earlyLeaveCount': early_leave_count,
            'missingCount': missing_count,
            'overtimeHours': round(total_overtime_hours, 2)
        })
    except Exception as e:
        logger.error(f"Error getting reports overview: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '获取报告概览失败'}), 500

# 获取详细报告
@attendance_bp.route('/reports/detail', methods=['GET'])
@jwt_required()
@require_permission('attendance:report')
def get_reports_detail():
    """获取详细考勤报告"""
    db = get_db()
    logger = get_logger()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        period = request.args.get('period', 'daily')
        date_str = request.args.get('date')
        department = request.args.get('department')
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else now_china().date()
        
        # 确定日期范围
        if period == 'daily':
            start_date = end_date = target_date
        elif period == 'weekly':
            start_date = target_date - timedelta(days=target_date.weekday())
            end_date = start_date + timedelta(days=6)
        elif period == 'monthly':
            start_date = target_date.replace(day=1)
            if target_date.month == 12:
                end_date = target_date.replace(year=target_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = target_date.replace(month=target_date.month + 1, day=1) - timedelta(days=1)
        else:
            start_date = end_date = target_date
        
        # 构建查询
        query = AttendanceRecord.query.filter(
            AttendanceRecord.record_date >= start_date,
            AttendanceRecord.record_date <= end_date
        )
        
        if department:
            query = query.join(User).filter(User.department == department)
        if current_user.role != 'admin':
            query = query.filter_by(user_id=current_user_id)
        
        query = query.order_by(AttendanceRecord.record_date.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        records = pagination.items
        
        result = []
        for record in records:
            user = record.user
            result.append({
                'id': record.id,
                'user_id': record.user_id,
                'user': {
                    'id': user.id if user else None,
                    'username': user.username if user else '未知',
                    # 中文姓名按「姓+名」显示（last_name=姓, first_name=名）
                    'name': f"{user.last_name or ''}{user.first_name or ''}".strip() or user.username if user else '未知',
                    'department': user.department if user else None
                } if user else None,
                'date': record.record_date.strftime('%Y-%m-%d') if record.record_date else None,
                'clock_in_time': record.clock_in_time.strftime('%H:%M:%S') if record.clock_in_time else None,
                'clock_out_time': record.clock_out_time.strftime('%H:%M:%S') if record.clock_out_time else None,
                'work_hours': record.work_hours,
                'overtime_hours': record.overtime_hours,
                'late_minutes': record.late_minutes,
                'early_leave_minutes': record.early_leave_minutes,
                'status': record.status
            })
        
        return jsonify({
            'records': result,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        logger.error(f"Error getting reports detail: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '获取详细报告失败'}), 500


# 获取个人考勤汇总（我的考勤）
@attendance_bp.route('/my-summary', methods=['GET'])
@jwt_required()
@require_permission('attendance:view')
def get_my_attendance_summary():
    """获取个人考勤汇总信息"""
    db = get_db()
    logger = get_logger()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        # 支持自定义日期范围，默认本月
        date_str = request.args.get('date')
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else now_china().date()

        year = request.args.get('year', target_date.year, type=int)
        month = request.args.get('month', target_date.month, type=int)

        # 计算月份起止日期
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)

        # 1) 应出勤天数：根据工作日历统计本月工作日
        work_calendar_entries = WorkCalendar.query.filter(
            db.func.date(WorkCalendar.date) >= start_date,
            db.func.date(WorkCalendar.date) <= end_date
        ).all()
        if work_calendar_entries:
            expected_days = sum(1 for d in work_calendar_entries if d.is_working_day and not d.is_holiday)
        else:
            # 没有工作日历时，按周一到周五计算
            expected_days = 0
            cur = start_date
            while cur <= end_date:
                if cur.weekday() < 5:
                    expected_days += 1
                cur += timedelta(days=1)

        # 2) 实际出勤天数：状态为 present / late / early_leave / overtime / business_trip 的天数
        #    结束边界用「下月1日」比较，避免日期参数漏掉月末当天的记录
        records = AttendanceRecord.query.filter(
            AttendanceRecord.user_id == current_user_id,
            AttendanceRecord.record_date >= start_date,
            AttendanceRecord.record_date < end_date + timedelta(days=1)
        ).all()

        valid_statuses = {
            AttendanceStatus.PRESENT.value,
            AttendanceStatus.LATE.value,
            AttendanceStatus.EARLY_LEAVE.value,
            AttendanceStatus.OVERTIME.value,
            AttendanceStatus.BUSINESS_TRIP.value
        }
        actual_days = sum(1 for r in records if r.status in valid_statuses)

        # 3) 迟到/早退 次数及时长
        late_count = sum(1 for r in records if r.late_minutes and r.late_minutes > 0)
        late_minutes_total = sum((r.late_minutes or 0) for r in records)
        early_leave_count = sum(1 for r in records if r.early_leave_minutes and r.early_leave_minutes > 0)
        early_leave_minutes_total = sum((r.early_leave_minutes or 0) for r in records)

        # 迟到分级
        if late_count == 0:
            late_level = 'normal'
            late_message = '正常'
        elif late_count <= 3:
            late_level = 'warning'
            late_message = '警告：建议调整作息'
        else:
            late_level = 'danger'
            late_message = '严重：已达3次以上警告线'

        # 4) 旷工天数：状态为 absent 或工作日未打卡且无请假
        absent_count = sum(1 for r in records if r.status == AttendanceStatus.ABSENT.value)
        # 缺卡但未补卡的次数
        missing_count = sum(1 for r in records if (
            (not r.clock_in_time or not r.clock_out_time)
            and r.status != AttendanceStatus.LEAVE.value
            and r.status != AttendanceStatus.ABSENT.value
        ))

        # 5) 请假时长（按类型统计）
        leave_records = LeaveApplication.query.filter(
            LeaveApplication.user_id == current_user_id,
            LeaveApplication.start_date <= end_date,
            LeaveApplication.end_date >= start_date,
            LeaveApplication.status == ApprovalStatus.APPROVED.value
        ).all()

        leave_breakdown = {}
        leave_total_days = 0.0
        for lv in leave_records:
            lv_type = lv.leave_type or 'other'
            days = lv.days or 0
            leave_breakdown[lv_type] = round(leave_breakdown.get(lv_type, 0) + days, 2)
            leave_total_days += days

        # 6) 加班时长（按类型：工作日加班 / 周末加班 / 节假日加班）
        overtime_records = OvertimeApplication.query.filter(
            OvertimeApplication.user_id == current_user_id,
            db.func.date(OvertimeApplication.date) >= start_date,
            db.func.date(OvertimeApplication.date) <= end_date,
            OvertimeApplication.status == ApprovalStatus.APPROVED.value
        ).all()

        def _parse_hours(start, end):
            try:
                sh, sm = [int(x) for x in str(start).split(':')[:2]]
                eh, em = [int(x) for x in str(end).split(':')[:2]]
                return max(0.0, (eh * 60 + em - sh * 60 - sm) / 60.0)
            except Exception:
                return 0.0

        def _ot_day_type(d):
            """加班日期分类：holiday=节假日，rest=休息日，workday=工作日"""
            cal_entry = next((e for e in work_calendar_entries
                              if (e.date.date() if hasattr(e.date, 'date') else e.date) == d), None)
            if cal_entry and cal_entry.is_holiday:
                return 'holiday'
            if cal_entry and not cal_entry.is_working_day:
                return 'rest'
            return 'rest' if d.weekday() >= 5 else 'workday'

        # 先按日期汇总考勤记录上的加班时长（钉钉导入/打卡统计的权威结果）
        overtime_by_day = {}
        for r in records:
            h = float(r.overtime_hours or 0)
            if h > 0:
                d = r.record_date.date() if hasattr(r.record_date, 'date') else r.record_date
                overtime_by_day[d] = max(overtime_by_day.get(d, 0.0), h)
        # 已批准的加班申请仅补充记录中未体现加班的日期，避免重复统计
        for ot in overtime_records:
            d = ot.date.date() if hasattr(ot.date, 'date') else ot.date
            if overtime_by_day.get(d, 0.0) <= 0:
                h = _parse_hours(ot.start_time, ot.end_time)
                if h > 0:
                    overtime_by_day[d] = h

        overtime_workday = 0.0
        overtime_weekend = 0.0
        overtime_holiday = 0.0
        overtime_total = 0.0
        for d, hours in overtime_by_day.items():
            overtime_total += hours
            day_type = _ot_day_type(d)
            if day_type == 'holiday':
                overtime_holiday += hours
            elif day_type == 'rest':
                overtime_weekend += hours
            else:
                overtime_workday += hours

        overtime_breakdown = {
            'workday': round(overtime_workday, 2),
            'weekend': round(overtime_weekend, 2),
            'holiday': round(overtime_holiday, 2)
        }

        # 7) 年假余额（按全年统计，每满一年5天，若无入职信息则默认为5天）
        annual_leave_quota = 5.0
        # 全年的年假使用记录（从当年1月1日到12月31日）
        year_start = datetime(year, 1, 1).date()
        year_end = datetime(year, 12, 31).date()
        annual_leave_records = LeaveApplication.query.filter(
            LeaveApplication.user_id == current_user_id,
            LeaveApplication.leave_type == 'annual_leave',
            LeaveApplication.start_date <= year_end,
            LeaveApplication.end_date >= year_start,
            LeaveApplication.status == ApprovalStatus.APPROVED.value
        ).all()
        annual_leave_used = sum((lv.days or 0) for lv in annual_leave_records)
        annual_leave_remaining = max(0.0, round(annual_leave_quota - annual_leave_used, 2))

        # 迟到分级提示
        late_grade = {
            'level': late_level,
            'message': late_message,
            'count': late_count,
            'threshold_warn': 3,
            'threshold_danger': 5
        }

        return jsonify({
            'period': {
                'year': year,
                'month': month,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            },
            'expected_days': expected_days,
            'actual_days': actual_days,
            'attendance_rate': round((actual_days / expected_days * 100) if expected_days > 0 else 0, 2),
            'late': {
                'count': late_count,
                'minutes': late_minutes_total,
                'hours': round(late_minutes_total / 60.0, 2),
                'grade': late_grade
            },
            'early_leave': {
                'count': early_leave_count,
                'minutes': early_leave_minutes_total,
                'hours': round(early_leave_minutes_total / 60.0, 2)
            },
            'absent_days': absent_count,
            'missing_count': missing_count,
            'leave': {
                'total_days': round(leave_total_days, 2),
                'breakdown': leave_breakdown,
                'annual_leave': {
                    'quota': annual_leave_quota,
                    'used': annual_leave_used,
                    'remaining': annual_leave_remaining
                }
            },
            'overtime': {
                'total_hours': round(overtime_total, 2),
                'breakdown': overtime_breakdown
            }
        })
    except Exception as e:
        logger.error(f"Error getting my attendance summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '获取个人考勤汇总失败'}), 500


# 考勤状态中文映射
ATTENDANCE_STATUS_LABELS = {
    'present': '正常',
    'absent': '旷工',
    'late': '迟到',
    'early_leave': '早退',
    'leave': '请假',
    'business_trip': '出差',
    'overtime': '加班',
    'missing': '缺卡'
}


def _can_view_employee_attendance(user):
    """员工考勤记录功能访问权限：超级管理员 / 总经理 / 人事经理 / 人事专员"""
    if not user:
        return False
    if getattr(user, 'is_super_admin', False):
        return True
    role = (getattr(user, 'role', '') or '')
    position = (getattr(user, 'position', '') or '')
    # 系统管理员角色
    if role == 'admin':
        return True
    # 总经理（分管领导）
    if role in ('division_leader', 'general_manager') or '总经理' in position:
        return True
    # 人事经理 / 人事专员
    if role == 'hr' or '人事' in position:
        return True
    return False


# 员工考勤报表阈值常量
SEVERE_LATE_MINUTES = 60      # 严重迟到阈值（分钟）
ABSENT_LATE_MINUTES = 120     # 旷工迟到阈值（分钟），达到记 1 天旷工迟到
DAILY_WORK_HOURS = 8          # 每日标准工作时长（小时），用于请假天数与小时的换算


def _build_employee_summary_data(month_str, department):
    """构建员工考勤记录汇总数据（钉钉式月度考勤报表口径，按员工工号顺序）

    返回 (month_label, employees)；数据异常时抛出 ValueError
    """
    db = get_db()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()

    today = now_china().date()
    # 解析统计月份，默认当月
    if month_str:
        try:
            base_date = datetime.strptime(month_str, '%Y-%m').date()
        except ValueError:
            raise ValueError('月份格式错误，应为 YYYY-MM')
    else:
        base_date = today

    month_start = base_date.replace(day=1)
    if month_start.month == 12:
        month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
    year_start = month_start.replace(month=1, day=1)
    year_end = month_start.replace(month=12, day=31)

    # 员工列表（在职用户），按工号顺序排序，无工号的按用户名排在后面
    user_query = User.query.filter_by(is_active=True)
    if department:
        user_query = user_query.filter(User.department == department)
    users = user_query.all()

    def _employee_sort_key(user):
        emp_id = (user.employee_id or '').strip()
        return (0, emp_id, user.username or '') if emp_id else (1, '', user.username or '')

    users.sort(key=_employee_sort_key)
    user_ids = [u.id for u in users]

    def _parse_hours(start, end):
        try:
            sh, sm = [int(x) for x in str(start).split(':')[:2]]
            eh, em = [int(x) for x in str(end).split(':')[:2]]
            return max(0.0, (eh * 60 + em - sh * 60 - sm) / 60.0)
        except Exception:
            return 0.0

    def _day_category(d):
        """加班日期分类：holiday=节假日，rest=休息日，weekday=工作日"""
        cal = workday_map.get(d)
        if cal is not None:
            if cal.get('is_holiday'):
                return 'holiday'
            if not cal.get('is_working_day'):
                return 'rest'
            return 'weekday'
        # 无日历数据时按周末判断
        return 'rest' if d.weekday() >= 5 else 'weekday'

    # ---- 日历数据（工作日/节假日），月度整月预取 ----
    cal_rows = WorkCalendar.query.filter(
        WorkCalendar.date >= month_start,
        WorkCalendar.date <= month_end
    ).all()
    workday_map = {r.date.date() if hasattr(r.date, 'date') else r.date: {'is_working_day': r.is_working_day, 'is_holiday': r.is_holiday} for r in cal_rows}

    # 月内总天数与休息天数（非工作日）
    total_days = (month_end - month_start).days + 1
    all_days = [month_start + timedelta(days=i) for i in range(total_days)]
    rest_days_count = sum(1 for d in all_days if _day_category(d) != 'weekday')

    # ---- 考勤记录（年度预取，月度内存过滤）----
    year_records = []
    if user_ids:
        # 结束边界用次年1月1日比较，避免年末当天记录因带时分秒被漏掉
        year_end_next = year_end + timedelta(days=1)
        year_records = AttendanceRecord.query.filter(
            AttendanceRecord.user_id.in_(user_ids),
            AttendanceRecord.record_date >= year_start,
            AttendanceRecord.record_date < year_end_next
        ).all()

    def _record_date(r):
        d = r.record_date
        return d.date() if hasattr(d, 'date') else d

    month_records = [r for r in year_records if month_start <= _record_date(r) <= month_end]

    # ---- 请假申请（年度，已批准，区间交集）----
    leaves = []
    if user_ids:
        leaves = LeaveApplication.query.filter(
            LeaveApplication.user_id.in_(user_ids),
            LeaveApplication.status == ApprovalStatus.APPROVED.value,
            LeaveApplication.start_date <= year_end,
            LeaveApplication.end_date >= year_start
        ).all()

    # ---- 加班申请（年度，已批准）----
    overtimes = []
    if user_ids:
        overtimes = OvertimeApplication.query.filter(
            OvertimeApplication.user_id.in_(user_ids),
            OvertimeApplication.status == ApprovalStatus.APPROVED.value,
            db.func.date(OvertimeApplication.date) >= year_start,
            db.func.date(OvertimeApplication.date) <= year_end
        ).all()

    def _overtime_date(o):
        d = o.date
        return d.date() if hasattr(d, 'date') else d

    # ---- 班次分配（当月生效的排班）----
    shift_map = {}
    try:
        shift_rows = db.session.query(UserShift, ShiftSchedule).join(
            ShiftSchedule, UserShift.shift_id == ShiftSchedule.id
        ).filter(
            UserShift.user_id.in_(user_ids) if user_ids else db.false(),
            UserShift.effective_date <= month_end,
            db.or_(UserShift.expire_date.is_(None), UserShift.expire_date >= month_start)
        ).all()
        # 每个用户取生效日期最近的一条
        for us, shift in shift_rows:
            eff = us.effective_date.date() if hasattr(us.effective_date, 'date') else us.effective_date
            cur = shift_map.get(us.user_id)
            if cur is None or eff > cur[0]:
                shift_map[us.user_id] = (eff, shift.name)
    except Exception:
        shift_map = {}

    # ---- 汇总每个员工 ----
    _zero = {'checkin_count': 0, 'leave_days': 0.0, 'overtime_hours': 0.0}
    employees = []
    for user in users:
        # 当月考勤明细统计
        recs = [r for r in month_records if r.user_id == user.id]
        attendance_days = sum(1 for r in recs if (r.clock_in_time is not None) or (getattr(r.status, 'value', str(r.status)) == AttendanceStatus.BUSINESS_TRIP.value))
        work_hours_total = sum((r.work_hours or 0) for r in recs)
        late_count = sum(1 for r in recs if (r.late_minutes or 0) > 0)
        late_minutes_total = sum((r.late_minutes or 0) for r in recs)
        severe_late_count = sum(1 for r in recs if (r.late_minutes or 0) >= SEVERE_LATE_MINUTES)
        severe_late_minutes = sum((r.late_minutes or 0) for r in recs if (r.late_minutes or 0) >= SEVERE_LATE_MINUTES)
        absent_late_days = sum(1 for r in recs if (r.late_minutes or 0) >= ABSENT_LATE_MINUTES)
        early_count = sum(1 for r in recs if (r.early_leave_minutes or 0) > 0)
        early_minutes_total = sum((r.early_leave_minutes or 0) for r in recs)
        missing_in = sum(1 for r in recs if r.clock_in_time is None)
        missing_out = sum(1 for r in recs if r.clock_out_time is None)
        absenteeism = sum(1 for r in recs if getattr(r.status, 'value', str(r.status)) == AttendanceStatus.ABSENT.value)
        business_trip_days = sum(1 for r in recs if getattr(r.status, 'value', str(r.status)) == AttendanceStatus.BUSINESS_TRIP.value)

        # 请假分类型统计（区间交集当月部分，按申请总天数折算）
        leave_stats = {'personal_h': 0.0, 'comp_h': 0.0, 'sick_h': 0.0, 'annual_d': 0.0, 'maternity_d': 0.0,
                       'paternity_d': 0.0, 'marriage_d': 0.0, 'period_d': 0.0, 'bereavement_d': 0.0, 'nursing_h': 0.0}
        user_leaves = [lv for lv in leaves if lv.user_id == user.id]
        month_leave_count = 0
        for lv in user_leaves:
            lv_start = lv.start_date.date() if hasattr(lv.start_date, 'date') else lv.start_date
            lv_end = lv.end_date.date() if hasattr(lv.end_date, 'date') else lv.end_date
            if lv_start <= month_end and lv_end >= month_start:
                month_leave_count += 1
            # 当月内生效天数（区间交集）
            overlap_days = (min(lv_end, month_end) - max(lv_start, month_start)).days + 1
            if overlap_days <= 0:
                continue
            lv_type = getattr(lv.leave_type, 'value', str(lv.leave_type))
            days = float(lv.days or 0)
            hours = days * DAILY_WORK_HOURS
            if lv_type == 'personal_leave':
                leave_stats['personal_h'] += hours
            elif lv_type == 'other':
                leave_stats['comp_h'] += hours
            elif lv_type == 'sick_leave':
                leave_stats['sick_h'] += hours
            elif lv_type == 'annual_leave':
                leave_stats['annual_d'] += days
            elif lv_type == 'maternity_leave':
                leave_stats['maternity_d'] += days
            elif lv_type == 'paternity_leave':
                leave_stats['paternity_d'] += days
            elif lv_type == 'marriage_leave':
                leave_stats['marriage_d'] += days
            elif lv_type == 'bereavement_leave':
                leave_stats['bereavement_d'] += days
            # period（例假）、nursing（哺乳假）暂无数据来源，保留列默认 0

        # 加班分类统计（转换方式 × 日期类型）
        # 加班分类型统计：优先取考勤记录上的加班时长（钉钉导入/打卡统计），
        # 已批准加班申请仅补充记录中未体现加班的日期，避免重复统计
        overtime_total = 0.0
        overtime_pay = {'weekday': 0.0, 'rest': 0.0, 'holiday': 0.0}
        overtime_leave = {'weekday': 0.0, 'rest': 0.0, 'holiday': 0.0}
        user_ots = [o for o in overtimes if o.user_id == user.id]
        month_overtime_count = 0
        # 当月每日加班时长（先填记录里的值）
        ot_month_map = {}
        for r in recs:
            h = float(r.overtime_hours or 0)
            if h > 0:
                d = _record_date(r)
                ot_month_map[d] = max(ot_month_map.get(d, 0.0), h)
        overtime_total += sum(ot_month_map.values())
        for o in user_ots:
            o_date = _overtime_date(o)
            if not (month_start <= o_date <= month_end):
                continue
            month_overtime_count += 1
            hours = _parse_hours(o.start_time, o.end_time)
            if ot_month_map.get(o_date, 0.0) <= 0 and hours > 0:
                # 打卡记录中该日无加班，采用申请单时长
                ot_month_map[o_date] = hours
                overtime_total += hours
            # 加班费/调休明细拆分仅按申请单口径统计
            bucket = overtime_pay if (getattr(o, 'compensation_type', None) or 'leave') == 'pay' else overtime_leave
            bucket[_day_category(o_date)] += hours

        # 年度汇总：加班 = 全年打卡记录加班时长 + 申请单补充
        year_recs = [r for r in year_records if r.user_id == user.id]
        y_checkin = sum(1 for r in year_recs if r.clock_in_time is not None)
        y_leave_days = sum((lv.days or 0) for lv in user_leaves)
        y_ot_day_map = {}
        for r in year_recs:
            h = float(r.overtime_hours or 0)
            if h > 0:
                d = _record_date(r)
                y_ot_day_map[d] = max(y_ot_day_map.get(d, 0.0), h)
        for o in user_ots:
            o_date = _overtime_date(o)
            if year_start <= o_date <= year_end and y_ot_day_map.get(o_date, 0.0) <= 0:
                h = _parse_hours(o.start_time, o.end_time)
                if h > 0:
                    y_ot_day_map[o_date] = h
        y_overtime = round(sum(y_ot_day_map.values()), 2)
        annual_used = sum((lv.days or 0) for lv in user_leaves
                          if getattr(lv.leave_type, 'value', str(lv.leave_type)) == 'annual_leave')

        shift_name = ''
        if user.id in shift_map:
            shift_name = shift_map[user.id][1]

        display_name = f"{user.last_name or ''}{user.first_name or ''}".strip() or user.username
        employees.append({
            'user_id': user.id,
            'employee_id': user.employee_id or '',
            'username': user.username,
            'name': display_name,
            'department': user.department or '',
            'position': user.position or '',
            'date': month_start.strftime('%Y-%m'),
            'shift_name': shift_name,
            'approval_count': month_leave_count + month_overtime_count,
            'attendance_days': attendance_days,
            'rest_days': rest_days_count,
            'work_hours': round(work_hours_total, 2),
            'late_count': late_count,
            'late_hours': round(late_minutes_total / 60.0, 2),
            'severe_late_count': severe_late_count,
            'severe_late_hours': round(severe_late_minutes / 60.0, 2),
            'absent_late_days': absent_late_days,
            'early_leave_count': early_count,
            'early_leave_hours': round(early_minutes_total / 60.0, 2),
            'missing_clock_in': missing_in,
            'missing_clock_out': missing_out,
            'absenteeism_days': absenteeism,
            'business_trip_hours': round(business_trip_days * DAILY_WORK_HOURS, 2),
            'outing_hours': 0.0,
            'leave': {
                'personal_h': round(leave_stats['personal_h'], 2),
                'comp_h': round(leave_stats['comp_h'], 2),
                'sick_h': round(leave_stats['sick_h'], 2),
                'annual_d': round(leave_stats['annual_d'], 2),
                'maternity_d': round(leave_stats['maternity_d'], 2),
                'paternity_d': round(leave_stats['paternity_d'], 2),
                'marriage_d': round(leave_stats['marriage_d'], 2),
                'period_d': round(leave_stats['period_d'], 2),
                'bereavement_d': round(leave_stats['bereavement_d'], 2),
                'nursing_h': round(leave_stats['nursing_h'], 2)
            },
            'overtime_total_hours': round(overtime_total, 2),
            'overtime_pay': {f'{k}_h': round(v, 2) for k, v in overtime_pay.items()},
            'overtime_leave': {f'{k}_h': round(v, 2) for k, v in overtime_leave.items()},
            # 年度汇总与年假（保留原口径）
            'month': {
                'checkin_count': sum(1 for r in recs if r.clock_in_time is not None),
                'leave_days': round(sum((lv.days or 0) for lv in user_leaves
                                        if (lv.start_date.date() if hasattr(lv.start_date, 'date') else lv.start_date) <= month_end
                                        and (lv.end_date.date() if hasattr(lv.end_date, 'date') else lv.end_date) >= month_start), 2),
                'overtime_hours': round(overtime_total, 2)
            },
            'year': {
                'checkin_count': y_checkin,
                'leave_days': round(y_leave_days, 2),
                'overtime_hours': round(y_overtime, 2)
            },
            'annual_leave': {
                'quota': 5.0,
                'used': round(annual_used, 2),
                'remaining': round(max(0.0, 5.0 - annual_used), 2)
            }
        })

    return month_start.strftime('%Y-%m'), employees


@attendance_bp.route('/employee-summary', methods=['GET'])
@jwt_required()
def get_employee_attendance_summary():
    """员工考勤记录汇总

    按员工工号顺序列出每位员工：
    - 当月打卡次数 / 请假时长 / 加班时长
    - 当年打卡次数 / 请假时长 / 加班时长
    - 剩余年假
    权限：仅超级管理员 / 总经理 / 人事经理 / 人事专员
    查询参数：month（YYYY-MM，默认当月）、department（可选）
    """
    db = get_db()
    logger = get_logger()
    User, _, _, _, _, _, _, _, _, _, _ = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        # 功能访问权限：超级管理员 / 总经理 / 人事经理 / 人事专员
        if not _can_view_employee_attendance(current_user):
            return jsonify({'error': '权限不足，仅超级管理员、总经理、人事经理、人事专员可查看员工考勤记录'}), 403

        month_str = request.args.get('month')
        department = request.args.get('department')
        try:
            month_label, employees = _build_employee_summary_data(month_str, department)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400

        summary = {'checkin_count': 0, 'leave_days': 0.0, 'overtime_hours': 0.0}
        for emp in employees:
            summary['checkin_count'] += emp['month']['checkin_count']
            summary['leave_days'] += emp['month']['leave_days']
            summary['overtime_hours'] += emp['month']['overtime_hours']

        return jsonify({
            'month': month_label,
            'total_employees': len(employees),
            'summary': {
                'checkin_count': int(summary['checkin_count']),
                'leave_days': round(summary['leave_days'], 2),
                'overtime_hours': round(summary['overtime_hours'], 2)
            },
            'employees': employees
        })
    except Exception as e:
        logger.error(f"Error getting employee attendance summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '获取员工考勤记录失败'}), 500


@attendance_bp.route('/employee-summary/export', methods=['GET'])
@jwt_required()
def export_employee_attendance_summary():
    """导出员工考勤记录汇总 Excel

    权限：仅超级管理员 / 总经理 / 人事经理 / 人事专员
    查询参数：month（YYYY-MM，默认当月）、department（可选）
    """
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, _, _, _, _, _, _, _, _, _, _ = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        # 功能访问权限：超级管理员 / 总经理 / 人事经理 / 人事专员
        if not _can_view_employee_attendance(current_user):
            return jsonify({'error': '权限不足，仅超级管理员、总经理、人事经理、人事专员可导出'}), 403

        month_str = request.args.get('month')
        department = request.args.get('department')
        try:
            month_label, employees = _build_employee_summary_data(month_str, department)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400

        # 构造导出行（钉钉式月度考勤报表口径）
        rows = []
        for emp in employees:
            rows.append({
                '姓名': emp['name'],
                '部门': emp['department'],
                '工号': emp['employee_id'] or '',
                '职位': emp['position'],
                '日期': emp['date'],
                '班次': emp['shift_name'],
                '关联的审批单': emp['approval_count'],
                '出勤天数': emp['attendance_days'],
                '休息天数': emp['rest_days'],
                '工作时长': emp['work_hours'],
                '迟到次数': emp['late_count'],
                '迟到时长': emp['late_hours'],
                '严重迟到次数': emp['severe_late_count'],
                '严重迟到时长': emp['severe_late_hours'],
                '旷工迟到天数': emp['absent_late_days'],
                '早退次数': emp['early_leave_count'],
                '早退时长': emp['early_leave_hours'],
                '上班缺卡次数': emp['missing_clock_in'],
                '下班缺卡次数': emp['missing_clock_out'],
                '旷工天数': emp['absenteeism_days'],
                '出差时长': emp['business_trip_hours'],
                '外出时长': emp['outing_hours'],
                '事假(小时)': emp['leave']['personal_h'],
                '调休(小时)': emp['leave']['comp_h'],
                '病假(小时)': emp['leave']['sick_h'],
                '年假(天)': emp['leave']['annual_d'],
                '产假(天)': emp['leave']['maternity_d'],
                '陪产假(天)': emp['leave']['paternity_d'],
                '婚假(天)': emp['leave']['marriage_d'],
                '例假(天)': emp['leave']['period_d'],
                '丧假(天)': emp['leave']['bereavement_d'],
                '哺乳假(小时)': emp['leave']['nursing_h'],
                '加班总时长': emp['overtime_total_hours'],
                '工作日（转加班费）': emp['overtime_pay']['weekday_h'],
                '休息日（转加班费）': emp['overtime_pay']['rest_h'],
                '节假日（转加班费）': emp['overtime_pay']['holiday_h'],
                '工作日（转调休）': emp['overtime_leave']['weekday_h'],
                '休息日（转调休）': emp['overtime_leave']['rest_h'],
                '节假日（转调休）': emp['overtime_leave']['holiday_h']
            })

        try:
            import pandas as pd
            from io import BytesIO
            from flask import send_file, make_response
        except ImportError:
            return jsonify({'error': '缺少 pandas 依赖，无法导出 Excel'}), 500

        filename = f'员工考勤记录_{month_label}.xlsx'
        df = pd.DataFrame(rows)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='员工考勤记录')
        output.seek(0)

        response = make_response(send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        ))
        origin = request.headers.get('Origin')
        response.headers['Access-Control-Allow-Origin'] = origin or '*'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'

        # 记录审计日志
        try:
            create_audit_log(
                user_id=current_user_id,
                action='export',
                resource_type='attendance',
                resource_id=None,
                details=f'导出员工考勤记录（{month_label}）{len(rows)} 条',
                request=request
            )
        except Exception:
            pass

        return response
    except Exception as e:
        logger.error(f"Error exporting employee attendance summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '导出员工考勤记录失败'}), 500


# ==================== 每月考勤确认单 ====================

# 全勤奖金额（元）：当月无迟到/早退/漏卡/旷工/事假/病假时发放（年假、调休等不影响全勤）
FULL_ATTENDANCE_BONUS = 200
# 公司邮箱域名：纯拼音账号（如 zhaokangwei）按 {username}@域名 推导收件邮箱
COMPANY_EMAIL_DOMAIN = 'chenxiaotech.com'


def _confirmation_recipient_email(user):
    """解析考勤确认单收件邮箱：
    1) 纯拼音账号（如 zhaokangwei）按公司邮箱规则推导 {username}@chenxiaotech.com；
    2) 已配置真实邮箱（非导入占位的 @attendance.local）直接使用；
    3) dt_ 钉钉建档等无法推导的账号返回 None（前端提示未配置邮箱）。
    """
    import re
    username = (getattr(user, 'username', '') or '').strip()
    if re.match(r'^[a-z]{2,}$', username):
        return f'{username}@{COMPANY_EMAIL_DOMAIN}'
    email = (getattr(user, 'email', '') or '').strip()
    if email and 'attendance.local' not in email:
        return email
    return None


def _build_confirmation_stats(emp, user_month_records):
    """根据员工月度汇总数据 + 当月打卡记录，构造考勤确认单表格统计项（对齐钉钉确认单样式）"""
    # 迟到/早退分档：<10分钟、10-30分钟（按当天迟到/早退较大值计 1 次）
    late_under10 = 0
    late_under30 = 0
    for r in user_month_records:
        minutes = max(int(r.late_minutes or 0), int(r.early_leave_minutes or 0))
        if 0 < minutes < 10:
            late_under10 += 1
        elif 10 <= minutes < 30:
            late_under30 += 1

    leave = emp.get('leave', {}) or {}
    # 请假（单位统一折算为小时展示，8H=1天）
    personal_h = float(leave.get('personal_h') or 0)      # 事假
    sick_h = float(leave.get('sick_h') or 0)              # 病假
    annual_h = round(float(leave.get('annual_d') or 0) * DAILY_WORK_HOURS)  # 年假
    other_leave_h = (
        float(leave.get('comp_h') or 0)                   # 调休
        + float(leave.get('marriage_d') or 0) * DAILY_WORK_HOURS   # 婚假
        + float(leave.get('maternity_d') or 0) * DAILY_WORK_HOURS  # 产假
        + float(leave.get('paternity_d') or 0) * DAILY_WORK_HOURS  # 陪产假
        + float(leave.get('bereavement_d') or 0) * DAILY_WORK_HOURS  # 丧假
        + float(leave.get('nursing_h') or 0)              # 哺乳假
        + float(leave.get('period_d') or 0) * DAILY_WORK_HOURS     # 例假
    )

    # 加班：直接取打卡记录上的加班时长（钉钉导入/打卡统计权威结果），按工作日/休息日/法定节假日分类
    ot_weekday = 0.0
    ot_rest = 0.0
    ot_holiday = 0.0
    ot_day_map = {}
    for r in user_month_records:
        h = float(getattr(r, 'overtime_hours', 0) or 0)
        if h > 0:
            d = r.record_date.date() if hasattr(r.record_date, 'date') else r.record_date
            ot_day_map[d] = max(ot_day_map.get(d, 0.0), h)
    # 法定节假日（工作日历中标记为节假日的日期）
    holiday_dates = set()
    if ot_day_map:
        try:
            _models = get_models()
            WorkCalendar = _models[5]
            any_d = next(iter(ot_day_map))
            cal_rows = WorkCalendar.query.filter(
                WorkCalendar.date >= datetime(any_d.year, any_d.month, 1),
                WorkCalendar.date < datetime(any_d.year + (1 if any_d.month == 12 else 0),
                                              1 if any_d.month == 12 else any_d.month + 1, 1)
            ).all()
            for cr in cal_rows:
                cd = cr.date.date() if hasattr(cr.date, 'date') else cr.date
                if getattr(cr, 'is_holiday', False):
                    holiday_dates.add(cd)
        except Exception:
            pass
    for d, h in ot_day_map.items():
        if d in holiday_dates:
            ot_holiday += h
        elif d.weekday() >= 5:
            ot_rest += h
        else:
            ot_weekday += h

    missing = int(emp.get('missing_clock_in') or 0) + int(emp.get('missing_clock_out') or 0)
    other_h = float(emp.get('business_trip_hours') or 0) + float(emp.get('outing_hours') or 0)

    # 备注：旷工/旷工迟到需人工核对
    remarks = []
    if float(emp.get('absenteeism_days') or 0) > 0:
        remarks.append(f"旷工{emp['absenteeism_days']}天")
    if float(emp.get('absent_late_days') or 0) > 0:
        remarks.append(f"旷工迟到{emp['absent_late_days']}天")

    return {
        # 全勤奖默认 200，发送前由人事核对修改（非全勤可改为 0 或留空）
        'full_attendance_bonus': FULL_ATTENDANCE_BONUS,
        'late_under10': late_under10,
        'late_under30': late_under30,
        'personal_h': round(personal_h, 1),
        'sick_h': round(sick_h, 1),
        'annual_h': annual_h,
        'other_leave_h': round(other_leave_h, 1),
        'ot_weekday': round(ot_weekday, 1),
        'ot_rest': round(ot_rest, 1),
        'ot_holiday': round(ot_holiday, 1),
        'other_h': round(other_h, 1),
        'missing': missing,
        'remark': '、'.join(remarks)
    }


# 确认单可人工修改的统计字段（overrides 白名单）
_CONFIRMATION_STAT_FIELDS = [
    'full_attendance_bonus', 'late_under10', 'late_under30',
    'personal_h', 'sick_h', 'annual_h', 'other_leave_h',
    'ot_weekday', 'ot_rest', 'ot_holiday',
    'other_h', 'missing'
]


def _apply_confirmation_overrides(stats, override):
    """将前端人工修改的统计项合并进 stats（数值字段转 float，备注为文本）"""
    if not override or not isinstance(override, dict):
        return stats
    for k in _CONFIRMATION_STAT_FIELDS:
        if k in override and override[k] not in (None, ''):
            try:
                stats[k] = round(float(override[k]), 1) if k != 'full_attendance_bonus' else int(float(override[k]))
            except (TypeError, ValueError):
                pass
    if 'remark' in override and override['remark'] is not None:
        stats['remark'] = str(override['remark']).strip()
    return stats


def _render_confirmation_email(emp, stats, year, month, sender_name, sender_email):
    """渲染考勤确认单邮件（主题 + 纯文本 + HTML），对齐人事邮件示例"""
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    mm = f'{month:02d}'
    period_title = f'{year}-{mm}-01---{year}-{mm}-{last_day:02d}（{month}月）考勤确认单'
    subject = period_title

    # 回复截止时间：次月3日 16:00；若已过期则顺延至次日 16:00
    deadline = datetime(year + (1 if month == 12 else 0), 1 if month == 12 else month + 1, 3, 16, 0)
    now_naive = now_china().replace(tzinfo=None)
    if deadline < now_naive:
        deadline = now_naive + timedelta(days=1)
        deadline = deadline.replace(hour=16, minute=0, second=0, microsecond=0)
    deadline_text = f'{deadline.year}年{deadline.month:02d}月{deadline.day:02d}日 16:00'

    name = emp.get('name') or emp.get('username')

    def _h(v):
        """请假小时展示：整数不带小数，加 H 后缀；0 留空"""
        if not v:
            return ''
        return f'{int(v) if float(v) == int(v) else v}H'

    def _n(v):
        """次数/加班小时展示：0 留空"""
        if not v:
            return ''
        return str(int(v) if float(v) == int(v) else v)

    def _cell(v, color=''):
        """表格单元格：color 非空时文字着色加粗（对齐示例中全勤/加班的红字）"""
        style = 'border:1px solid #333;padding:6px 10px;text-align:center;'
        if color:
            style += 'color:' + color + ';font-weight:bold;'
        return f'<td style="{style}">{v}</td>'

    html_body = f'''<html><body style="font-family:'Microsoft YaHei',Arial,sans-serif;font-size:14px;color:#000;">
<p style="font-size:16px;font-weight:bold;">{period_title}</p>
<p style="font-size:16px;">{name} 您好！</p>
<p style="text-indent:2em;line-height:1.9;">
请确认您当月的考勤，有任何意见请在{deadline_text}前回复
“{sender_name}&nbsp;<a href="mailto:{sender_email}">{sender_email}</a>” 查核；<br>
逾期无回复，默认与实际考勤一致，将据此核算工资。
</p>
<table style="border-collapse:collapse;margin-top:16px;font-size:13px;">
  <tr>
    <td rowspan="2" style="border:1px solid #333;padding:6px 10px;text-align:center;font-weight:bold;">全勤</td>
    <td colspan="2" style="border:1px solid #333;padding:6px 10px;text-align:center;font-weight:bold;">迟到早退/次</td>
    <td colspan="4" style="border:1px solid #333;padding:6px 10px;text-align:center;font-weight:bold;">请假/天</td>
    <td colspan="3" style="border:1px solid #333;padding:6px 10px;text-align:center;font-weight:bold;color:red;">加班/H</td>
    <td rowspan="2" style="border:1px solid #333;padding:6px 10px;text-align:center;font-weight:bold;">其它</td>
    <td rowspan="2" style="border:1px solid #333;padding:6px 10px;text-align:center;font-weight:bold;">漏卡/<br>次</td>
    <td rowspan="2" style="border:1px solid #333;padding:6px 10px;text-align:center;font-weight:bold;">备注</td>
  </tr>
  <tr>
    <td style="border:1px solid #333;padding:6px 10px;text-align:center;">&lt;10’</td>
    <td style="border:1px solid #333;padding:6px 10px;text-align:center;">&lt;30’</td>
    <td style="border:1px solid #333;padding:6px 10px;text-align:center;">事假</td>
    <td style="border:1px solid #333;padding:6px 10px;text-align:center;">病假</td>
    <td style="border:1px solid #333;padding:6px 10px;text-align:center;">年假</td>
    <td style="border:1px solid #333;padding:6px 10px;text-align:center;">其它</td>
    <td style="border:1px solid #333;padding:6px 10px;text-align:center;color:red;">平日</td>
    <td style="border:1px solid #333;padding:6px 10px;text-align:center;color:#1f4e9b;">调休</td>
    <td style="border:1px solid #333;padding:6px 10px;text-align:center;color:red;">法定</td>
  </tr>
  <tr>
    {_cell(_n(stats['full_attendance_bonus']), 'red')}
    {_cell(_n(stats['late_under10']))}
    {_cell(_n(stats['late_under30']))}
    {_cell(_h(stats['personal_h']))}
    {_cell(_h(stats['sick_h']))}
    {_cell(_h(stats['annual_h']))}
    {_cell(_h(stats['other_leave_h']))}
    {_cell(_n(stats['ot_weekday']), 'red')}
    {_cell(_n(stats['ot_rest']), '#1f4e9b')}
    {_cell(_n(stats['ot_holiday']), 'red')}
    {_cell(_h(stats['other_h']))}
    {_cell(_n(stats['missing']))}
    {_cell(stats['remark'])}
  </tr>
</table>
</body></html>'''

    text_body = f'''{period_title}

{name} 您好！
  请确认您当月的考勤，有任何意见请在{deadline_text}前回复“{sender_name} {sender_email}”查核；逾期无回复，默认与实际考勤一致，将据此核算工资。

全勤：{_n(stats['full_attendance_bonus'])}
迟到早退 <10分钟：{_n(stats['late_under10'])} 次；<30分钟：{_n(stats['late_under30'])} 次
请假 - 事假：{_h(stats['personal_h'])} 病假：{_h(stats['sick_h'])} 年假：{_h(stats['annual_h'])} 其它：{_h(stats['other_leave_h'])}
加班 - 平日：{_n(stats['ot_weekday'])}H 调休(休息日)：{_n(stats['ot_rest'])}H 法定：{_n(stats['ot_holiday'])}H
其它：{_h(stats['other_h'])} 漏卡：{_n(stats['missing'])} 次
备注：{stats['remark']}
'''
    return subject, text_body, html_body


@attendance_bp.route('/confirmations', methods=['GET'])
@jwt_required()
def get_attendance_confirmations():
    """每月考勤确认单列表：返回当月员工的确认单发送状态
    权限：仅超级管理员 / 总经理 / 人事经理 / 人事专员
    查询参数：month（YYYY-MM，默认当月）、department（可选）
    """
    db = get_db()
    logger = get_logger()
    User, AttendanceRecord, _, _, _, _, _, _, _, _, _ = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user:
            return jsonify({'error': '用户不存在'}), 404
        if not _can_view_employee_attendance(current_user):
            return jsonify({'error': '权限不足，仅超级管理员、总经理、人事经理、人事专员可查看考勤确认单'}), 403

        month_str = request.args.get('month')
        department = request.args.get('department')
        try:
            month_label, employees = _build_employee_summary_data(month_str, department)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400

        # 预取当月打卡记录，用于生成每人完整确认单数据（迟到分档/加班等）
        _y = int(month_label[:4])
        _m = int(month_label[5:7])
        _next = datetime(_y + 1, 1, 1) if _m == 12 else datetime(_y, _m + 1, 1)
        month_records = AttendanceRecord.query.filter(
            AttendanceRecord.record_date >= datetime(_y, _m, 1),
            AttendanceRecord.record_date < _next
        ).all()
        records_by_user = {}
        for r in month_records:
            records_by_user.setdefault(r.user_id, []).append(r)

        from enhanced_app import AttendanceConfirmation
        confs = AttendanceConfirmation.query.filter_by(period=month_label).all()
        conf_map = {c.user_id: c for c in confs}
        sender_ids = {c.sent_by for c in confs if c.sent_by}
        sender_map = {u.id: u for u in User.query.filter(User.id.in_(sender_ids)).all()} if sender_ids else {}

        try:
            from services.email_service import email_service
            mail_configured = email_service.is_configured()
        except Exception:
            mail_configured = False

        rows = []
        for emp in employees:
            user = User.query.get(emp['user_id'])
            email = _confirmation_recipient_email(user) if user else None
            conf = conf_map.get(emp['user_id'])
            sender = sender_map.get(conf.sent_by) if conf else None
            # 确认单完整数据：优先取上次发送时人工核对的快照，否则按当月记录计算
            stats = None
            if conf and conf.stats_snapshot:
                try:
                    stats = json.loads(conf.stats_snapshot)
                except Exception:
                    stats = None
            if stats is None:
                stats = _build_confirmation_stats(emp, records_by_user.get(emp['user_id'], []))
            rows.append({
                'user_id': emp['user_id'],
                'employee_id': emp.get('employee_id') or '',
                'username': emp.get('username'),
                'name': emp.get('name'),
                'department': emp.get('department') or '',
                'position': emp.get('position') or '',
                'recipient_email': email or '',
                'has_email': bool(email),
                'attendance_days': emp.get('attendance_days'),
                'missing_clock_in': emp.get('missing_clock_in'),
                'missing_clock_out': emp.get('missing_clock_out'),
                'late_count': emp.get('late_count'),
                'early_leave_count': emp.get('early_leave_count'),
                'overtime_total_hours': emp.get('overtime_total_hours'),
                'stats': stats,
                'status': conf.status if conf else 'unsent',
                'error_message': conf.error_message if conf else None,
                'sent_at': conf.sent_at.strftime('%Y-%m-%d %H:%M:%S') if conf and conf.sent_at else None,
                'sent_by_name': (f"{sender.last_name or ''}{sender.first_name or ''}".strip() or sender.username) if sender else None
            })

        return jsonify({
            'month': month_label,
            'total_employees': len(rows),
            'mail_configured': mail_configured,
            'sent_count': sum(1 for r in rows if r['status'] == 'sent'),
            'employees': rows
        })
    except Exception as e:
        logger.error(f"Error getting attendance confirmations: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '获取考勤确认单列表失败'}), 500


@attendance_bp.route('/confirmations/send', methods=['POST'])
@jwt_required()
def send_attendance_confirmations():
    """发送每月考勤确认单到员工邮箱
    权限：仅超级管理员 / 总经理 / 人事经理 / 人事专员
    请求体：{month: 'YYYY-MM', user_ids?: [..]（不传=全部）, department?: '..'}
    """
    db = get_db()
    logger = get_logger()
    User, AttendanceRecord, _, _, _, _, _, _, _, _, _ = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user:
            return jsonify({'error': '用户不存在'}), 404
        if not _can_view_employee_attendance(current_user):
            return jsonify({'error': '权限不足，仅超级管理员、总经理、人事经理、人事专员可发送考勤确认单'}), 403

        payload = request.get_json(silent=True) or {}
        month_str = payload.get('month')
        department = payload.get('department')
        user_ids = payload.get('user_ids') or None
        # 人工核对后的统计项覆盖：{user_id: {field: value}}
        overrides = payload.get('overrides') or {}
        try:
            month_label, employees = _build_employee_summary_data(month_str, department)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400

        if user_ids:
            id_set = {int(i) for i in user_ids}
            employees = [e for e in employees if e['user_id'] in id_set]
        if not employees:
            return jsonify({'error': '没有需要发送确认单的员工'}), 400

        year = int(month_label[:4])
        month = int(month_label[5:7])
        month_start = datetime(year, month, 1)
        next_month = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

        # 一次性预取当月全部打卡记录，用于迟到/早退分档统计
        month_records = AttendanceRecord.query.filter(
            AttendanceRecord.record_date >= month_start,
            AttendanceRecord.record_date < next_month
        ).all()
        records_by_user = {}
        for r in month_records:
            records_by_user.setdefault(r.user_id, []).append(r)

        from enhanced_app import AttendanceConfirmation
        from services.email_service import email_service

        # 回复联系人（发件人）：优先当前操作人姓名+真实邮箱
        sender_name = f"{current_user.last_name or ''}{current_user.first_name or ''}".strip() or current_user.username
        sender_email = (getattr(current_user, 'email', '') or '').strip()
        if not sender_email or 'attendance.local' in sender_email:
            sender_email = email_service.from_address

        existing = AttendanceConfirmation.query.filter_by(period=month_label).all()
        conf_map = {c.user_id: c for c in existing}

        details = []
        sent_count = 0
        failed_count = 0
        for emp in employees:
            user = User.query.get(emp['user_id'])
            name = emp.get('name') or emp.get('username')
            if not user:
                failed_count += 1
                details.append({'user_id': emp['user_id'], 'name': name, 'status': 'failed', 'error': '用户不存在'})
                continue

            email = _confirmation_recipient_email(user)
            if not email:
                failed_count += 1
                details.append({'user_id': user.id, 'name': name, 'email': '', 'status': 'failed',
                                'error': '该员工无有效邮箱（钉钉建档账号需先在员工管理中补充邮箱）'})
                continue

            # 统计数据：优先使用人工核对后已保存的数据，未保存过则按当月打卡记录实时计算
            conf = conf_map.get(user.id)
            stats = None
            if conf and conf.stats_snapshot:
                try:
                    stats = json.loads(conf.stats_snapshot)
                except Exception:
                    stats = None
            if stats is None:
                stats = _build_confirmation_stats(emp, records_by_user.get(user.id, []))
            # 兼容前端随发送提交的覆盖项（一般为空，数据以保存为准）
            stats = _apply_confirmation_overrides(stats, overrides.get(str(user.id)))
            subject, text_body, html_body = _render_confirmation_email(
                emp, stats, year, month, sender_name, sender_email)

            result = email_service.send_email(email, subject, text_body, html_body,
                                              from_name=f'{sender_name}-考勤确认')
            ok = bool(result.get('success'))
            now = now_china().replace(tzinfo=None)

            if not conf:
                conf = AttendanceConfirmation(
                    user_id=user.id, period=month_label, year=year, month=month)
                db.session.add(conf)
                conf_map[user.id] = conf
            conf.recipient_email = email
            conf.stats_snapshot = json.dumps(stats, ensure_ascii=False)
            conf.status = 'sent' if ok else 'failed'
            conf.error_message = None if ok else str(result.get('error') or '发送失败')
            conf.sent_by = current_user.id
            conf.sent_at = now

            if ok:
                sent_count += 1
            else:
                failed_count += 1
            details.append({
                'user_id': user.id, 'name': name, 'email': email,
                'status': 'sent' if ok else 'failed',
                'error': None if ok else conf.error_message
            })

        db.session.commit()
        logger.info(f"考勤确认单发送完成（{month_label}）：成功 {sent_count}，失败 {failed_count}，操作人 {current_user.username}")

        return jsonify({
            'month': month_label,
            'total': len(employees),
            'sent': sent_count,
            'failed': failed_count,
            'details': details
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error sending attendance confirmations: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'发送考勤确认单失败：{str(e)}'}), 500


@attendance_bp.route('/confirmations/save', methods=['POST'])
@jwt_required()
def save_confirmation():
    """保存某人某月考勤确认单的人工核对数据（直接生效，不发送邮件）。
    点击列表行编辑后保存；发送时直接以此数据为准。"""
    db = get_db()
    logger = get_logger()
    User, _, _, _, _, _, _, _, _, _, _ = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user:
            return jsonify({'error': '用户不存在'}), 404
        if not _can_view_employee_attendance(current_user):
            return jsonify({'error': '权限不足，仅超级管理员、总经理、人事经理、人事专员可保存考勤确认单'}), 403

        payload = request.get_json(silent=True) or {}
        month_str = payload.get('month')
        user_id = payload.get('user_id')
        stats_in = payload.get('stats') or {}
        if not month_str or not user_id:
            return jsonify({'error': '缺少月份或员工参数'}), 400

        try:
            year, month = map(int, month_str.split('-')[:2])
            month_label = f'{year:04d}-{month:02d}'
        except Exception:
            return jsonify({'error': '月份格式错误，应为 YYYY-MM'}), 400

        user = User.query.get(int(user_id))
        if not user:
            return jsonify({'error': '员工不存在'}), 404

        # 以空模板为底合并人工修改，保证字段完整
        stats = {
            'full_attendance_bonus': None, 'late_under10': 0, 'late_under30': 0,
            'personal_h': 0, 'sick_h': 0, 'annual_h': 0, 'other_leave_h': 0,
            'ot_weekday': 0, 'ot_rest': 0, 'ot_holiday': 0,
            'other_h': 0, 'missing': 0, 'remark': ''
        }
        stats = _apply_confirmation_overrides(stats, stats_in)

        from enhanced_app import AttendanceConfirmation
        conf = AttendanceConfirmation.query.filter_by(
            user_id=user.id, period=month_label).first()
        if not conf:
            conf = AttendanceConfirmation(
                user_id=user.id, period=month_label, year=year, month=month)
            db.session.add(conf)
        email = _confirmation_recipient_email(user)
        conf.recipient_email = email or ''
        conf.stats_snapshot = json.dumps(stats, ensure_ascii=False)
        # 直接保存生效；未发送过保持 unsent，已发送过的保留原状态（数据更新后可重新发送）
        if conf.status not in ('sent', 'failed'):
            conf.status = 'unsent'
        conf.error_message = None
        db.session.commit()

        logger.info(f"考勤确认单核对数据已保存（{month_label}，{user.username}），操作人 {current_user.username}")
        return jsonify({
            'success': True,
            'month': month_label,
            'user_id': user.id,
            'status': conf.status,
            'stats': stats
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving attendance confirmation: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'保存核对数据失败：{str(e)}'}), 500


def _build_attendance_export_rows(query, User, AttendanceRecord):
    """根据查询构造考勤导出数据行"""
    rows = []
    for record in query.all():
        user = record.user
        rows.append({
            'ID': record.id,
            '员工账号': user.username if user else '',
            '员工姓名': f"{user.last_name or ''}{user.first_name or ''}".strip() or (user.username if user else '未知'),
            '部门': user.department if user and getattr(user, 'department', None) else '',
            '日期': record.record_date.strftime('%Y-%m-%d') if record.record_date else '',
            '上班打卡': record.clock_in_time.strftime('%H:%M:%S') if record.clock_in_time else '',
            '上班IP': record.clock_in_ip or '',
            '下班打卡': record.clock_out_time.strftime('%H:%M:%S') if record.clock_out_time else '',
            '下班IP': record.clock_out_ip or '',
            '工作时长(小时)': round(record.work_hours, 2) if record.work_hours else 0,
            '加班时长(小时)': round(record.overtime_hours, 2) if record.overtime_hours else 0,
            '迟到(分钟)': record.late_minutes or 0,
            '早退(分钟)': record.early_leave_minutes or 0,
            '考勤状态': ATTENDANCE_STATUS_LABELS.get(record.status, record.status or '')
        })
    return rows


# 导出考勤记录
@attendance_bp.route('/records/export', methods=['GET'])
@jwt_required()
@require_permission('attendance:export')
def export_attendance_records():
    """导出考勤记录为 Excel 文件"""
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, AttendanceRecord, _, _, _, _, _, _, AttendanceStatus, _, _ = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        # 解析筛选条件（与 /records 保持一致）
        start_date = request.args.get('start_date') or request.args.get('dateRange[0]')
        end_date = request.args.get('end_date') or request.args.get('dateRange[1]')
        user_id = request.args.get('user_id', type=int) or request.args.get('userId', type=int)
        status = request.args.get('status')

        query = AttendanceRecord.query

        # 非管理员仅能导出自己的数据
        if current_user.role != 'admin':
            query = query.filter_by(user_id=current_user_id)
        elif user_id:
            query = query.filter_by(user_id=user_id)

        if start_date:
            query = query.filter(AttendanceRecord.record_date >= start_date)
        if end_date:
            # 仅传入日期（YYYY-MM-DD）时补齐到当天结束，避免漏掉最后一天的记录
            if len(str(end_date).strip()) == 10:
                end_date = str(end_date).strip() + ' 23:59:59'
            query = query.filter(AttendanceRecord.record_date <= end_date)
        if status:
            # 前端可能传入 normal/late/early_leave/missing/overtime，需要兼容枚举值
            status_map = {
                'normal': AttendanceStatus.PRESENT.value,
                'late': AttendanceStatus.LATE.value,
                'early_leave': AttendanceStatus.EARLY_LEAVE.value,
                'missing': AttendanceStatus.MISSING.value,
                'overtime': AttendanceStatus.OVERTIME.value
            }
            mapped_status = status_map.get(status, status)
            query = query.filter(AttendanceRecord.status == mapped_status)

        query = query.order_by(AttendanceRecord.record_date.desc())
        rows = _build_attendance_export_rows(query, User, AttendanceRecord)

        # 生成 Excel 文件
        try:
            import pandas as pd
            from io import BytesIO
            from flask import send_file, make_response
        except ImportError:
            return jsonify({'error': '缺少 pandas 依赖，无法导出 Excel'}), 500

        filename = f'考勤记录_{datetime.now().strftime("%Y-%m-%d")}.xlsx'
        if not rows:
            # 没有任何数据时仍然返回带表头的空文件
            rows = []

        df = pd.DataFrame(rows)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='考勤记录')
        output.seek(0)

        response = make_response(send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        ))
        origin = request.headers.get('Origin')
        response.headers['Access-Control-Allow-Origin'] = origin or '*'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'

        # 记录审计日志
        try:
            create_audit_log(
                user_id=current_user_id,
                action='export',
                resource_type='attendance',
                resource_id=None,
                details=f'导出考勤记录 {len(rows)} 条',
                request=request
            )
        except Exception:
            pass

        return response
    except Exception as e:
        logger.error(f"Error exporting attendance records: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '导出考勤记录失败'}), 500


# 导出考勤报表
@attendance_bp.route('/reports/export', methods=['GET'])
@jwt_required()
@require_permission('attendance:export')
def export_attendance_report():
    """导出考勤统计报表为 Excel 文件"""
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, AttendanceRecord, _, _, _, _, _, _, AttendanceStatus, _, _ = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        period = request.args.get('period', 'daily')
        date_str = request.args.get('date')
        department = request.args.get('department')
        start_date = request.args.get('start_date') or request.args.get('dateRange[0]')
        end_date = request.args.get('end_date') or request.args.get('dateRange[1]')

        target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else now_china().date()

        # 自定义周期优先使用 dateRange
        if period == 'custom' and start_date and end_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date() if isinstance(start_date, str) else start_date
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() if isinstance(end_date, str) else end_date
        elif period == 'daily':
            start_date_obj = end_date_obj = target_date
        elif period == 'weekly':
            start_date_obj = target_date - timedelta(days=target_date.weekday())
            end_date_obj = start_date_obj + timedelta(days=6)
        elif period == 'monthly':
            start_date_obj = target_date.replace(day=1)
            if target_date.month == 12:
                end_date_obj = target_date.replace(year=target_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date_obj = target_date.replace(month=target_date.month + 1, day=1) - timedelta(days=1)
        else:
            start_date_obj = end_date_obj = target_date

        query = AttendanceRecord.query.filter(
            AttendanceRecord.record_date >= start_date_obj,
            AttendanceRecord.record_date <= end_date_obj
        )
        if department:
            query = query.join(User).filter(User.department == department)
        if current_user.role != 'admin':
            query = query.filter_by(user_id=current_user_id)

        query = query.order_by(AttendanceRecord.record_date.desc())
        rows = _build_attendance_export_rows(query, User, AttendanceRecord)

        try:
            import pandas as pd
            from io import BytesIO
            from flask import send_file, make_response
        except ImportError:
            return jsonify({'error': '缺少 pandas 依赖，无法导出 Excel'}), 500

        period_label = {
            'daily': '日报',
            'weekly': '周报',
            'monthly': '月报',
            'custom': '自定义'
        }.get(period, period)
        filename = f'考勤报表_{period_label}_{start_date_obj}_{end_date_obj}.xlsx'

        df = pd.DataFrame(rows)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='考勤报表')
        output.seek(0)

        response = make_response(send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        ))
        origin = request.headers.get('Origin')
        response.headers['Access-Control-Allow-Origin'] = origin or '*'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'

        try:
            create_audit_log(
                user_id=current_user_id,
                action='export',
                resource_type='attendance_report',
                resource_id=None,
                details=f'导出考勤报表 {len(rows)} 条 ({period_label} {start_date_obj}~{end_date_obj})',
                request=request
            )
        except Exception:
            pass

        return response
    except Exception as e:
        logger.error(f"Error exporting attendance report: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '导出考勤报表失败'}), 500


# ==================== 考勤记录导入（适配钉钉「打卡时间」月度网格表 / 「每日统计」明细表） ====================

# 月度网格表中的汇总列标签
_GRID_SUMMARY_LABELS = ['迟到', '事假', '病假', '年假', '加班', '节日', '调休', '漏卡']


def _import_cell_text(value):
    """单元格值转纯文本"""
    if value is None:
        return ''
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _import_extract_times(value):
    """从打卡时间单元格提取 (hour, minute) 列表，去重保序。

    支持 Excel 时间类型（datetime/time）与多行文本（如 "08:28\\n17:35"）。
    """
    import datetime as _dt
    if value is None:
        return []
    if isinstance(value, _dt.datetime):
        return [(value.hour, value.minute)]
    if isinstance(value, _dt.time):
        return [(value.hour, value.minute)]
    times = []
    for m in re.finditer(r'(\d{1,2}):(\d{2})', str(value)):
        h, mi = int(m.group(1)), int(m.group(2))
        if 0 <= h <= 23 and 0 <= mi <= 59 and (h, mi) not in times:
            times.append((h, mi))
    return times


def _import_parse_date(value):
    """解析日期单元格，返回 date 对象。

    支持 Excel 日期类型、'2026-05-01 星期五'/'26-05-01' 两种年份写法，
    以及钉钉 workDate 列的 13 位毫秒时间戳字符串。
    """
    import datetime as _dt
    if value is None:
        return None
    if isinstance(value, _dt.datetime):
        return value.date()
    if isinstance(value, _dt.date):
        return value
    text = str(value).strip()
    # 13 位毫秒时间戳（如 1777564800000）
    if re.fullmatch(r'\d{13}', text):
        try:
            return datetime.fromtimestamp(int(text) / 1000).date()
        except (ValueError, OSError, OverflowError):
            pass
    m = re.search(r'(\d{4}|\d{2})\s*[-/年.]\s*(\d{1,2})\s*[-/月.]\s*(\d{1,2})', text)
    if m:
        year = int(m.group(1))
        if year < 100:
            year += 2000
        try:
            return _dt.date(year, int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    return None


def _import_parse_hours(value):
    """解析时长为小时，支持 '3H'、'3.5小时'、'120分钟'、纯数字（按小时）"""
    if value is None or value == '':
        return 0.0
    if isinstance(value, (int, float)):
        return round(float(value), 2)
    text = str(value).strip()
    m = re.search(r'(\d+(?:\.\d+)?)\s*(小时|h|H|分钟|分)?', text)
    if not m:
        return 0.0
    num = float(m.group(1))
    unit = m.group(2) or ''
    if '分钟' in unit or unit == '分':
        return round(num / 60.0, 2)
    return round(num, 2)


def _import_parse_minutes(value):
    """解析时长为分钟，支持 '12分钟'、'0.5小时'、纯数字（按分钟）"""
    if value is None or value == '':
        return 0
    if isinstance(value, (int, float)):
        return int(round(float(value)))
    text = str(value).strip()
    m = re.search(r'(\d+(?:\.\d+)?)\s*(小时|h|H|分钟|分)?', text)
    if not m:
        return 0
    num = float(m.group(1))
    unit = m.group(2) or ''
    if '小时' in unit or unit.lower() == 'h':
        return int(round(num * 60))
    return int(round(num))


def _import_parse_count(value):
    """解析次数/天数等整数值"""
    if value is None or value == '':
        return 0
    if isinstance(value, (int, float)):
        return int(float(value))
    m = re.search(r'\d+', str(value))
    return int(m.group(0)) if m else 0


def _import_build_user_map(User):
    """构建 姓名 / 用户名 / 工号 -> User 的映射缓存"""
    name_map = {}
    users = User.query.all()
    for u in users:
        keys = set()
        # 中文姓名按「姓+名」拼接（last_name=姓, first_name=名），
        # 同时兼容西式「名+姓」顺序，两种顺序都加入映射
        cn_full = f"{u.last_name or ''}{u.first_name or ''}".strip()
        if cn_full:
            keys.add(cn_full.replace(' ', ''))
        full = f"{u.first_name or ''}{u.last_name or ''}".strip()
        if full:
            keys.add(full.replace(' ', ''))
        spaced = f"{u.first_name or ''} {u.last_name or ''}".strip()
        if spaced:
            keys.add(spaced)
        if u.username:
            keys.add(str(u.username).strip())
        if getattr(u, 'employee_id', None):
            keys.add(str(u.employee_id).strip())
        for k in keys:
            if k and k not in name_map:
                name_map[k] = u
    return name_map


def _import_match_user(user_map, name, employee_id=''):
    """按姓名优先、工号兜底匹配用户"""
    name = (name or '').strip()
    if name and name in user_map:
        return user_map[name]
    emp = (employee_id or '').strip()
    if emp and emp in user_map:
        return user_map[emp]
    return None


def _import_ensure_user(User, user_map, name, userid='', employee_id='',
                        department='', position='', created_names=None):
    """匹配用户，匹配不到时自动建档（钉钉考勤账号）。

    返回 (user, created_bool)。建档规则：
    - username = dt_{钉钉UserId}（无 UserId 时用姓名），保证唯一；
    - 中文姓名按「姓 + 名」拆分填入 last_name/first_name；
    - 随机密码（不可直接登录，需管理员重置），默认激活。
    """
    import secrets
    from werkzeug.security import generate_password_hash

    user = _import_match_user(user_map, name, employee_id)
    if user:
        return user, False
    if userid and str(userid).strip() in user_map:
        return user_map[str(userid).strip()], False

    display = re.sub(r'\s+', '', str(name or ''))
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', display)
    if chinese_chars:
        last_name = display[0]
        first_name = display[1:]
    else:
        last_name = ''
        first_name = display or 'employee'

    uid_base = re.sub(r'[^0-9A-Za-z]', '', str(userid or '')) or display or 'employee'
    base_username = f'dt_{uid_base}'[:70]
    username = base_username
    i = 2
    while User.query.filter_by(username=username).first():
        username = f'{base_username}_{i}'[:70]
        i += 1

    email = f'{username}@attendance.local'
    j = 2
    while User.query.filter_by(email=email).first():
        email = f'{base_username}_{j}@attendance.local'
        j += 1

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(secrets.token_hex(20)),
        salt=secrets.token_hex(16),
        first_name=first_name,
        last_name=last_name,
        department=str(department or '').strip(),
        position=str(position or '').strip(),
        employee_id=str(employee_id).strip() if employee_id else None,
        is_active=True
    )
    db = get_db()
    db.session.add(user)
    db.session.flush()

    # 同步映射缓存
    for k in {display, username, str(employee_id).strip() if employee_id else '',
              str(userid).strip() if userid else ''}:
        if k and k not in user_map:
            user_map[k] = user
    if created_names is not None and display:
        created_names.append(display)
    return user, True


def _parse_grid_sheet(ws):
    """解析钉钉「打卡时间」月度网格表

    结构：前若干行为标题（含 统计日期：YYYY-MM-DD 至 YYYY-MM-DD），
    表头行依次为 姓名 | 劳动节/六/日/1/2/3...（每日一列）| 迟到 事假 病假 年假 加班 节日 调休 漏卡，
    其后每行一个员工，每日单元格内为多行打卡时间。

    返回 dict(year, month, name_col, day_cols=[(col_idx, day, day_type)], summary_cols={label: col_idx}, data_rows)
    无法识别时返回 None。
    """
    rows = [list(row) for row in ws.iter_rows(values_only=True)]

    # 1) 从标题行解析统计年月
    year = month = None
    for row in rows[:12]:
        for cell in row:
            if cell and '统计日期' in str(cell):
                m = re.search(r'(\d{4})\s*[-/年.]\s*(\d{1,2})', str(cell))
                if m:
                    year, month = int(m.group(1)), int(m.group(2))
                break
        if year:
            break

    # 2) 定位日期表头行（同时包含「迟到」「漏卡」和「六/日」）
    header_idx = None
    for idx, row in enumerate(rows):
        texts = [_import_cell_text(c) for c in row]
        if '迟到' in texts and '漏卡' in texts and ('六' in texts or '日' in texts):
            header_idx = idx
            break
    if header_idx is None:
        return None

    header = [_import_cell_text(c) for c in rows[header_idx]]

    # 3) 定位姓名列与 UserId 列（表头可能在「打卡时间」合并表头行 R3 中）
    name_col = 0
    userid_col = None
    for r in rows[:header_idx + 1]:
        for ci, c in enumerate(r):
            text = _import_cell_text(c)
            if text == '姓名':
                name_col = ci
            elif text.lower() == 'userid':
                userid_col = ci

    # 4) 汇总列位置
    summary_cols = {}
    for ci, text in enumerate(header):
        if text in _GRID_SUMMARY_LABELS and text not in summary_cols:
            summary_cols[text] = ci
    if '迟到' not in summary_cols:
        return None

    # 5) 日期列：跳过 UserId、打卡时间分组表头等非日期列，
    #    从第一个「日标记」列（节假日名/六/日/数字）开始，到「迟到」汇总列前结束
    skip_headers = {'userid', '打卡时间', '姓名', '工号', '部门', '考勤组', '职位', 'UserId'}
    day_end = summary_cols['迟到']
    day_start = None
    for ci in range(name_col + 1, day_end):
        text = (header[ci] if ci < len(header) else '').strip()
        if not text or text in skip_headers or text in summary_cols:
            continue
        day_start = ci
        break
    if day_start is None:
        return None

    day_cols = []
    day_counter = 1
    for ci in range(day_start, day_end):
        text = header[ci] if ci < len(header) else ''
        if text in ('六', '日', '周六', '周日'):
            day_type = 'weekend'
        elif re.fullmatch(r'\d{1,2}', text):
            day_type = 'workday'
        elif text and text not in skip_headers:
            day_type = 'holiday'  # 节假日名称（劳动节、端午节等）
        else:
            day_type = 'workday'
        day_cols.append((ci, day_counter, day_type))
        day_counter += 1

    # 6) 员工数据行
    data_rows = []
    for row in rows[header_idx + 1:]:
        name = _import_cell_text(row[name_col]) if name_col < len(row) else ''
        if not name or name in ('姓名', 'Name', '姓名 '):
            continue
        data_rows.append(row)

    return {
        'year': year,
        'month': month,
        'name_col': name_col,
        'userid_col': userid_col,
        'day_cols': day_cols,
        'summary_cols': summary_cols,
        'data_rows': data_rows
    }


def _build_grid_record_fields(times, day_type, date_obj):
    """根据网格表某日打卡时间生成考勤字段"""
    from datetime import time as _time
    from models.enums import AttendanceStatus
    times_sorted = sorted(times)
    first_h, first_m = times_sorted[0]
    last_h, last_m = times_sorted[-1]

    clock_in = datetime.combine(date_obj, _time(first_h, first_m))
    clock_out = datetime.combine(date_obj, _time(last_h, last_m))
    note_parts = []
    if len(times_sorted) == 1:
        # 仅一次打卡：午前记为上班卡，午后记为下班卡
        if first_h < 12:
            clock_out = None
        else:
            clock_in = None

    work_hours = 0.0
    overtime_hours = 0.0
    if clock_in and clock_out:
        work_hours = round(max((clock_out - clock_in).total_seconds() / 3600, 0), 2)

    late_minutes = 0
    early_leave_minutes = 0
    status = AttendanceStatus.PRESENT.value

    if day_type in ('weekend', 'holiday'):
        # 周末/节假日有打卡记为加班
        status = AttendanceStatus.OVERTIME.value
        overtime_hours = work_hours
        note_parts.append('节假日加班' if day_type == 'holiday' else '周末加班')
    else:
        # 工作日：09:00 后上班记迟到
        if clock_in and (first_h, first_m) > (9, 0):
            late_minutes = (first_h - 9) * 60 + first_m
            status = AttendanceStatus.LATE.value
        # 17:30 前下班记早退
        if clock_out and (last_h, last_m) < (17, 30):
            early_leave_minutes = (17 - last_h) * 60 + (30 - last_m)
            if status == AttendanceStatus.PRESENT.value:
                status = AttendanceStatus.EARLY_LEAVE.value
        # 缺卡
        if clock_in is None or clock_out is None:
            status = AttendanceStatus.MISSING.value
            note_parts.append('漏卡')

    return {
        'clock_in_time': clock_in,
        'clock_out_time': clock_out,
        'work_hours': work_hours,
        'overtime_hours': overtime_hours,
        'late_minutes': late_minutes,
        'early_leave_minutes': early_leave_minutes,
        'status': status,
        'note_parts': note_parts
    }


def _parse_daily_detail_sheet(ws):
    """解析钉钉「每日统计」明细表（每人每天一行，含上下班打卡时间与统计列）

    钉钉报表为两行表头：主表头行含 姓名/日期/上班1打卡时间 等，
    其下一行为「请假/加班」等合并分组的子表头（事假(小时)、年假(天) 等）。

    返回 dict(header_idx, col={表头: 列索引}, rows=数据行)，无法识别返回 None。
    """
    def _norm(v):
        return _import_cell_text(v).replace('\n', '').replace(' ', '').replace('\t', '')

    rows = [list(row) for row in ws.iter_rows(values_only=True)]
    header_idx = None
    for idx, row in enumerate(rows):
        texts = [_norm(c) for c in row]
        if '姓名' in texts and '日期' in texts and any('上班1打卡时间' in t for t in texts):
            header_idx = idx
            break
    if header_idx is None:
        return None

    col = {}
    for ci, t in enumerate([_norm(c) for c in rows[header_idx]]):
        if t and t not in col:
            col[t] = ci

    # 合并子表头行（如「请假」分组下的 事假(小时)/年假(天)，「加班」分组下的明细列）
    data_start = header_idx + 1
    if header_idx + 1 < len(rows):
        sub_row = [_norm(c) for c in rows[header_idx + 1]]
        has_sub = False
        for ci, t in enumerate(sub_row):
            if t and ('(' in t or '（' in t):
                col[t] = ci
                has_sub = True
        if has_sub:
            data_start = header_idx + 2

    return {
        'header_idx': header_idx,
        'col': col,
        'data_rows': rows[data_start:]
    }


def _build_daily_record_fields(times, date_obj, get_cell):
    """根据每日统计行的统计列生成考勤字段。get_cell(列名) 取原始单元格值。"""
    from datetime import time as _time
    from models.enums import AttendanceStatus

    note_parts = []
    shift_text = _import_cell_text(get_cell('班次'))
    is_rest = '休息' in shift_text

    late_count = _import_parse_count(get_cell('迟到次数'))
    late_minutes = _import_parse_minutes(get_cell('迟到时长')) if late_count > 0 else 0
    early_count = _import_parse_count(get_cell('早退次数'))
    early_minutes = _import_parse_minutes(get_cell('早退时长')) if early_count > 0 else 0
    missing_in = _import_parse_count(get_cell('上班缺卡次数'))
    missing_out = _import_parse_count(get_cell('下班缺卡次数'))
    absent_days = _import_parse_count(get_cell('旷工天数'))

    # 请假/外出/出差
    leave_hours = 0.0
    leave_notes = []
    leave_hour_cols = [('事假(小时)', '事假'), ('病假(小时)', '病假'), ('调休(小时)', '调休'),
                       ('哺乳假(小时)', '哺乳假'), ('外出时长', '外出'), ('出差时长', '出差')]
    for col_name, label in leave_hour_cols:
        h = _import_parse_hours(get_cell(col_name))
        if h > 0:
            leave_hours += h
            leave_notes.append(f'{label}{h:g}小时')
    for col_name, label in [('年假(天)', '年假'), ('产假(天)', '产假'), ('陪产假(天)', '陪产假'),
                            ('婚假(天)', '婚假'), ('例假(天)', '例假'), ('丧假(天)', '丧假')]:
        d = _import_parse_hours(get_cell(col_name))
        if d > 0:
            leave_hours += d * 8
            leave_notes.append(f'{label}{d:g}天')

    overtime_hours = _import_parse_hours(get_cell('加班总时长'))

    # 打卡时间
    clock_in = clock_out = None
    work_hours = 0.0
    if times:
        times_sorted = sorted(times)
        first_h, first_m = times_sorted[0]
        last_h, last_m = times_sorted[-1]
        clock_in = datetime.combine(date_obj, _time(first_h, first_m))
        clock_out = datetime.combine(date_obj, _time(last_h, last_m))
        if len(times_sorted) == 1:
            if first_h < 12:
                clock_out = None
            else:
                clock_in = None
        if clock_in and clock_out:
            work_hours = round(max((clock_out - clock_in).total_seconds() / 3600, 0), 2)

    # 工作时长优先取报表统计值（钉钉导出单位为分钟，如 491 = 8.2 小时）
    reported_minutes = _import_parse_count(get_cell('工作时长'))
    if reported_minutes > 0:
        work_hours = round(reported_minutes / 60.0, 2)

    # 状态判定（优先级：旷工 > 缺卡 > 迟到 > 早退 > 加班 > 请假 > 正常）
    if absent_days > 0:
        status = AttendanceStatus.ABSENT.value
        note_parts.append('旷工')
    elif (missing_in > 0 or missing_out > 0 or (times and (clock_in is None or clock_out is None))):
        status = AttendanceStatus.MISSING.value
        note_parts.append('缺卡')
    elif late_count > 0:
        status = AttendanceStatus.LATE.value
    elif early_count > 0:
        status = AttendanceStatus.EARLY_LEAVE.value
    elif is_rest and times:
        status = AttendanceStatus.OVERTIME.value
        note_parts.append('休息加班')
    elif not times and leave_hours >= 8:
        status = AttendanceStatus.LEAVE.value
    elif times:
        status = AttendanceStatus.PRESENT.value
    else:
        return None  # 无打卡、无请假、非旷工的休息日，跳过

    if overtime_hours > 0:
        note_parts.append(f'加班{overtime_hours:g}小时')
    note_parts.extend(leave_notes)

    return {
        'clock_in_time': clock_in,
        'clock_out_time': clock_out,
        'work_hours': work_hours,
        'overtime_hours': overtime_hours,
        'late_minutes': late_minutes,
        'early_leave_minutes': early_minutes,
        'status': status,
        'note_parts': note_parts,
        'is_rest': is_rest
    }


def _upsert_attendance_record(AttendanceRecord, user_id, date_obj, fields, source_label, dry_run, stats, preview_list):
    """按 (用户, 日期) 插入或更新考勤记录。

    dry_run 时只查询与统计，不写数据库会话；
    调用方需保证同一 (user_id, date) 只调用一次（多 sheet 先在内存合并）。
    """
    from datetime import time as _time
    existing = AttendanceRecord.query.filter(
        AttendanceRecord.user_id == user_id,
        AttendanceRecord.record_date >= datetime.combine(date_obj, _time.min),
        AttendanceRecord.record_date <= datetime.combine(date_obj, _time.max)
    ).first()

    note_text = '；'.join([p for p in fields.get('note_parts', []) if p])
    note = f'{source_label}' + (f'：{note_text}' if note_text else '')

    if len(preview_list) < 30:
        preview_list.append({
            'user_id': user_id,
            'date': date_obj.isoformat(),
            'clock_in': fields['clock_in_time'].strftime('%H:%M') if fields.get('clock_in_time') else None,
            'clock_out': fields['clock_out_time'].strftime('%H:%M') if fields.get('clock_out_time') else None,
            'status': fields['status'],
            'work_hours': fields.get('work_hours', 0),
            'overtime_hours': fields.get('overtime_hours', 0),
            'late_minutes': fields.get('late_minutes', 0),
            'note': note,
            'action': 'update' if existing else 'create'
        })

    if dry_run:
        # 预览模式：仅统计，不落库
        if existing:
            stats['updated'] += 1
        else:
            stats['created'] += 1
        return

    if existing:
        existing.clock_in_time = fields.get('clock_in_time')
        existing.clock_out_time = fields.get('clock_out_time')
        existing.work_hours = fields.get('work_hours', 0) or 0
        existing.overtime_hours = fields.get('overtime_hours', 0) or 0
        existing.late_minutes = fields.get('late_minutes', 0) or 0
        existing.early_leave_minutes = fields.get('early_leave_minutes', 0) or 0
        existing.status = fields['status']
        existing.note = note
        stats['updated'] += 1
    else:
        record = AttendanceRecord(
            user_id=user_id,
            record_date=datetime.combine(date_obj, _time.min),
            clock_in_time=fields.get('clock_in_time'),
            clock_out_time=fields.get('clock_out_time'),
            work_hours=fields.get('work_hours', 0) or 0,
            overtime_hours=fields.get('overtime_hours', 0) or 0,
            late_minutes=fields.get('late_minutes', 0) or 0,
            early_leave_minutes=fields.get('early_leave_minutes', 0) or 0,
            status=fields['status'],
            note=note
        )
        db = get_db()
        db.session.add(record)
        stats['created'] += 1


@attendance_bp.route('/records/import', methods=['POST'])
@jwt_required()
def import_attendance_records():
    """导入考勤打卡记录 Excel

    自动适配两种钉钉导出格式：
    1. 「打卡时间」月度网格表：每人一行，每日一列，单元格内为打卡时间，末尾为迟到/请假/加班/漏卡汇总列；
    2. 「每日统计」明细表：每人每天一行，含上/下班打卡时间、迟到早退、请假、加班等统计列。

    表单参数：
        file: Excel 文件（.xlsx）
        dry_run: 1=仅预览不写入（默认），0=确认导入
        year/month: 网格表无法从标题识别年月时的兜底值
    """
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, AttendanceRecord, _, _, _, _, _, _, AttendanceStatus, _, _ = get_models()

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        # 导入全员考勤属于人事管理操作：超级管理员 / 管理员 / 总经理 / 人事可操作
        if not _can_view_employee_attendance(current_user):
            return jsonify({'error': '权限不足，仅管理员、总经理、人事人员可导入考勤记录'}), 403

        if 'file' not in request.files:
            return jsonify({'error': '请上传 Excel 文件'}), 400
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': '文件名为空'}), 400
        if not file.filename.lower().endswith(('.xlsx', '.xlsm')):
            return jsonify({'error': '仅支持 .xlsx 格式的 Excel 文件'}), 400

        dry_run = request.form.get('dry_run', '1') != '0'

        try:
            import openpyxl
            from io import BytesIO
        except ImportError:
            return jsonify({'error': '服务器缺少 openpyxl 依赖，无法解析 Excel'}), 500

        try:
            wb = openpyxl.load_workbook(BytesIO(file.read()), data_only=True)
        except Exception as e:
            logger.error(f"考勤导入文件解析失败: {str(e)}")
            return jsonify({'error': f'Excel 文件解析失败：{str(e)}'}), 400

        # 按工作表名称解析：钉钉报表同时包含「打卡时间」网格表与「每日统计」明细表，
        # 两个 sheet 都解析（网格表覆盖全员，明细表含更准确的班次/统计，后处理覆盖）
        grid_info = None
        daily_info = None
        for ws_item in wb.worksheets:
            title = ws_item.title or ''
            try:
                if '打卡时间' in title and grid_info is None:
                    grid_info = _parse_grid_sheet(ws_item)
                elif '每日统计' in title and daily_info is None:
                    daily_info = _parse_daily_detail_sheet(ws_item)
            except Exception as parse_err:
                logger.warning(f"工作表[{title}]解析失败: {str(parse_err)}")
        # 兜底：按活动工作表识别
        if grid_info is None and daily_info is None:
            ws_item = wb.active
            daily_info = _parse_daily_detail_sheet(ws_item)
            if daily_info is None:
                grid_info = _parse_grid_sheet(ws_item)

        if daily_info is None and grid_info is None:
            return jsonify({'error': '无法识别的报表格式，请上传钉钉导出的「打卡时间」月度表或「每日统计」明细表'}), 400

        auto_create = request.form.get('auto_create_users', '1') != '0'

        user_map = _import_build_user_map(User)
        stats = {'created': 0, 'updated': 0, 'skipped_rest': 0, 'users_created': 0}
        unmatched_names = []
        created_user_names = []
        matched_users = {}
        errors = []
        preview_list = []
        monthly_summary = []
        period_labels = []
        # 多 sheet 合并：key=(user_id, date)，value=(fields, 来源标签)；
        # 每日统计表数据更权威，后处理时覆盖网格表结果
        merged_records = {}

        def _mark_user(user, days=0):
            # 中文姓名按「姓+名」显示（last_name=姓, first_name=名）
            label = f"{user.last_name or ''}{user.first_name or ''}".strip() or user.username
            info = matched_users.setdefault(user.id, {'name': label, 'username': user.username, 'days': 0})
            info['days'] += days
            return label

        # 预处理：每日统计表中能匹配到系统账号的行，用钉钉 UserId 预注册映射，
        # 使网格表中的中文姓名（如「赵康卫」）可关联到同一系统账号，避免重复建档
        if daily_info is not None:
            pre_col = daily_info['col']

            def _pre_get(row, col_name):
                ci = pre_col.get(col_name)
                return row[ci] if ci is not None and ci < len(row) else None

            for row in daily_info['data_rows']:
                pre_name = _import_cell_text(_pre_get(row, '姓名'))
                if not pre_name:
                    continue
                pre_emp = _import_cell_text(_pre_get(row, '工号'))
                pre_uid = str(_pre_get(row, 'UserId') or '').strip()
                pre_user = _import_match_user(user_map, pre_name, pre_emp)
                if pre_user and pre_uid:
                    user_map.setdefault(pre_uid, pre_user)

        # ===== 一、「打卡时间」月度网格表（全员每日打卡）=====
        if grid_info is not None:
            year = grid_info['year'] or request.form.get('year', type=int) or now_china().year
            month = grid_info['month'] or request.form.get('month', type=int) or now_china().month
            period_labels.append(f'{year}-{month:02d}')
            name_col = grid_info['name_col']
            userid_col = grid_info.get('userid_col')

            for row in grid_info['data_rows']:
                name = _import_cell_text(row[name_col]) if name_col < len(row) else ''
                if not name:
                    continue
                userid = ''
                if userid_col is not None and userid_col < len(row):
                    userid = _import_cell_text(row[userid_col])

                if auto_create:
                    try:
                        user, _created = _import_ensure_user(
                            User, user_map, name, userid=userid, created_names=created_user_names)
                        if _created:
                            stats['users_created'] += 1
                    except Exception as create_err:
                        logger.warning(f"员工「{name}」自动建档失败: {str(create_err)}")
                        user = None
                else:
                    user = _import_match_user(user_map, name)

                if not user:
                    if name not in unmatched_names:
                        unmatched_names.append(name)
                    errors.append(f'员工「{name}」在系统中未找到对应账号，已跳过')
                    continue

                _mark_user(user)
                user_label = _mark_user(user)

                # 月度汇总列（迟到/事假/病假/年假/加班/节日/调休/漏卡）
                summary_parts = []
                for label in _GRID_SUMMARY_LABELS:
                    ci = grid_info['summary_cols'].get(label)
                    if ci is not None and ci < len(row):
                        val = _import_cell_text(row[ci])
                        if val:
                            summary_parts.append(f'{label}{val}')
                if summary_parts:
                    monthly_summary.append({'name': user_label, 'summary': '；'.join(summary_parts)})

                # 逐日解析打卡时间
                record_days = 0
                for ci, day, day_type in grid_info['day_cols']:
                    try:
                        date_obj = datetime(year, month, day).date()
                    except ValueError:
                        continue  # 当月无此日期（如 2 月 30/31 列）
                    cell = row[ci] if ci < len(row) else None
                    times = _import_extract_times(cell)
                    if not times:
                        continue
                    fields = _build_grid_record_fields(times, day_type, date_obj)
                    merged_records[(user.id, date_obj)] = (fields, '钉钉打卡导入')
                    record_days += 1

                _mark_user(user, record_days)

        # ===== 二、「每日统计」明细表（班次/迟到/缺卡/请假/加班等权威统计，覆盖网格结果）=====
        if daily_info is not None:
            col = daily_info['col']

            def _get_cell(row, col_name):
                ci = col.get(col_name)
                if ci is None or ci >= len(row):
                    return None
                return row[ci]

            period_dates = []
            for row in daily_info['data_rows']:
                try:
                    name = _import_cell_text(_get_cell(row, '姓名'))
                    if not name:
                        continue
                    emp_id = _import_cell_text(_get_cell(row, '工号'))
                    userid = str(_get_cell(row, 'UserId') or '').strip()
                    dept = _import_cell_text(_get_cell(row, '部门'))
                    pos = _import_cell_text(_get_cell(row, '职位'))

                    if auto_create:
                        try:
                            user, _created = _import_ensure_user(
                                User, user_map, name, userid=userid, employee_id=emp_id,
                                department=dept, position=pos, created_names=created_user_names)
                            if _created:
                                stats['users_created'] += 1
                        except Exception as create_err:
                            logger.warning(f"员工「{name}」自动建档失败: {str(create_err)}")
                            user = None
                    else:
                        user = _import_match_user(user_map, name, emp_id)

                    if not user:
                        if name not in unmatched_names:
                            unmatched_names.append(name)
                            errors.append(f'员工「{name}」在系统中未找到对应账号，已跳过')
                        continue

                    date_obj = _import_parse_date(_get_cell(row, '日期'))
                    if not date_obj:
                        continue
                    period_dates.append(date_obj)

                    # 收集三班次的上下班打卡时间
                    times = []
                    for punch_col in ['上班1打卡时间', '下班1打卡时间', '上班2打卡时间', '下班2打卡时间',
                                      '上班3打卡时间', '下班3打卡时间']:
                        for t in _import_extract_times(_get_cell(row, punch_col)):
                            if t not in times:
                                times.append(t)

                    fields = _build_daily_record_fields(
                        times, date_obj, lambda cn: _get_cell(row, cn)
                    )
                    if fields is None:
                        stats['skipped_rest'] += 1
                        continue

                    _mark_user(user)
                    # 每日统计数据更权威，覆盖网格表结果
                    merged_records[(user.id, date_obj)] = (fields, '钉钉每日统计导入')
                except Exception as row_err:
                    errors.append(f'明细行解析失败：{str(row_err)}')

            if period_dates:
                period_labels.append(f'{min(period_dates).isoformat()} 至 {max(period_dates).isoformat()}')

        # ===== 三、统一写入（按 用户+日期 去重后的合并结果）=====
        user_days = {}
        for (uid, date_obj), (fields, source_label) in merged_records.items():
            user_days[uid] = user_days.get(uid, 0) + 1
        for uid, days in user_days.items():
            info = matched_users.get(uid)
            if info is not None:
                info['days'] = days

        for (uid, date_obj), (fields, source_label) in sorted(
                merged_records.items(), key=lambda kv: (kv[0][0], kv[0][1])):
            _upsert_attendance_record(
                AttendanceRecord, uid, date_obj, fields,
                source_label, dry_run, stats, preview_list
            )

        stats['employees'] = len(matched_users)
        matched_list = list(matched_users.values())
        period_label = '；'.join(period_labels)
        formats = []
        if grid_info is not None:
            formats.append('grid')
        if daily_info is not None:
            formats.append('daily_detail')

        if not dry_run:
            try:
                db.session.commit()
            except Exception as commit_err:
                db.session.rollback()
                logger.error(f"考勤导入提交失败: {str(commit_err)}")
                return jsonify({'error': f'数据写入失败：{str(commit_err)}'}), 500
            try:
                create_audit_log(
                    user_id=current_user_id,
                    action='import',
                    resource_type='attendance',
                    resource_id=None,
                    details=f'导入考勤记录：新增 {stats["created"]} 条，更新 {stats["updated"]} 条，'
                            f'新建员工账号 {stats["users_created"]} 个，跳过休息日 {stats["skipped_rest"]} 条',
                    request=request
                )
            except Exception:
                pass
        else:
            # 预览模式：回滚自动建档 flush 的数据，确保不写入任何内容
            db.session.rollback()

        logger.info(
            f"考勤记录导入(dry_run={dry_run}) by user {current_user_id}: "
            f"formats={formats}, period={period_label}, "
            f"created={stats['created']}, updated={stats['updated']}, "
            f"users_created={stats['users_created']}, unmatched={unmatched_names}"
        )

        return jsonify({
            'message': '预览成功，请确认后导入' if dry_run else f'导入成功：新增 {stats["created"]} 条，更新 {stats["updated"]} 条',
            'dry_run': dry_run,
            'formats': formats,
            'format': '+'.join(formats),
            'period': period_label,
            'employees_total': stats['employees'],
            'matched_users': matched_list,
            'unmatched_names': unmatched_names,
            'created_users': created_user_names,
            'users_created': stats['users_created'],
            'records_total': stats['created'] + stats['updated'],
            'created': stats['created'],
            'updated': stats['updated'],
            'skipped_rest': stats['skipped_rest'],
            'monthly_summary': monthly_summary,
            'errors': errors[:50],
            'preview': preview_list
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error importing attendance records: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'导入考勤记录失败：{str(e)}'}), 500
