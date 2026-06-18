from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
import json

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
        
        year = request.args.get('year', datetime.utcnow().year, type=int)
        month = request.args.get('month', datetime.utcnow().month, type=int)
        
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
            query = query.filter(AttendanceRecord.record_date <= end_date)
        
        if status:
            query = query.filter(AttendanceRecord.status == status)
        
        query = query.order_by(AttendanceRecord.record_date.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        records = pagination.items
        
        result = []
        for record in records:
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

# 打卡
@attendance_bp.route('/clock-in', methods=['POST'])
@jwt_required()
@require_permission('attendance:clock_in')
def clock_in():
    """上班打卡"""
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        current_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        existing_record = AttendanceRecord.query.filter(
            AttendanceRecord.user_id == current_user_id,
            AttendanceRecord.record_date == current_date
        ).first()
        
        if existing_record and existing_record.clock_in_time:
            return jsonify({'error': '今日已打卡'}), 400
        
        client_ip = request.remote_addr or '0.0.0.0'
        
        json_data = request.get_json(silent=True) or {}
        location = json_data.get('location')
        
        today = datetime.utcnow().date()
        user_shift = UserShift.query.filter(
            UserShift.user_id == current_user_id,
            UserShift.effective_date <= today
        ).order_by(UserShift.effective_date.desc()).first()
        
        shift = None
        if user_shift:
            shift = ShiftSchedule.query.get(user_shift.shift_id)
        
        late_minutes = 0
        if shift:
            shift_start = datetime.strptime(shift.start_time, '%H:%M').time()
            actual_time = datetime.utcnow().time()
            if actual_time > shift_start:
                shift_start_dt = datetime.combine(today, shift_start)
                actual_dt = datetime.combine(today, actual_time)
                late_minutes = int((actual_dt - shift_start_dt).total_seconds() / 60)
        
        if existing_record:
            existing_record.clock_in_time = datetime.utcnow()
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
                clock_in_time=datetime.utcnow(),
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
@require_permission('attendance:clock_out')
def clock_out():
    """下班打卡"""
    db = get_db()
    logger = get_logger()
    create_audit_log = get_create_audit_log()
    User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException, WorkCalendar, ShiftSchedule, UserShift, AttendanceStatus, ApprovalStatus, Activity = get_models()
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        current_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
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
        
        record.clock_out_time = datetime.utcnow()
        record.clock_out_ip = client_ip
        record.clock_out_location = location
        
        if record.clock_in_time and record.clock_out_time:
            work_duration = record.clock_out_time - record.clock_in_time
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
        
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
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
                    'name': f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username if user else '未知'
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
            app_data = {
                'id': app.id,
                'user_id': app.user_id,
                'applicant': {
                    'id': applicant.id if applicant else None,
                    'username': applicant.username if applicant else '未知',
                    'name': f"{applicant.first_name or ''} {applicant.last_name or ''}".strip() or applicant.username if applicant else '未知'
                } if applicant else None,
                'leave_type': app.leave_type,
                'start_date': app.start_date.strftime('%Y-%m-%d') if app.start_date else None,
                'end_date': app.end_date.strftime('%Y-%m-%d') if app.end_date else None,
                'days': getattr(app, 'days', None) or ((app.end_date - app.start_date).days + 1) if app.start_date and app.end_date else None,
                'reason': app.reason,
                'status': app.status,
                'approver_id': app.approver_id,
                'approver': {
                    'id': approver.id if approver else None,
                    'username': approver.username if approver else None,
                    'name': f"{approver.first_name or ''} {approver.last_name or ''}".strip() or approver.username if approver else None
                } if approver else None,
                'approved_at': app.approved_at.isoformat() if app.approved_at else None,
                'approval_comment': app.approval_comment,
                'attachment': app.attachment,
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

        # 审批人（可选）
        approver_id = data.get('approver_id')
        if approver_id is not None and approver_id != '':
            try:
                approver_id = int(approver_id)
                approver = User.query.get(approver_id)
                if not approver:
                    return jsonify({'error': '指定的审批人不存在'}), 400
            except (TypeError, ValueError):
                approver_id = None
        else:
            approver_id = None

        # 附件（可选）
        attachment = data.get('attachment') or data.get('attachment_path') or None

        application = LeaveApplication(
            user_id=current_user_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            days=days,
            reason=reason,
            status=ApprovalStatus.PENDING.value,
            approver_id=approver_id,
            attachment=attachment
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
            app_data = {
                'id': app.id,
                'user_id': app.user_id,
                'applicant': {
                    'id': applicant.id if applicant else None,
                    'username': applicant.username if applicant else '未知',
                    'name': f"{applicant.first_name or ''} {applicant.last_name or ''}".strip() or applicant.username if applicant else '未知'
                } if applicant else None,
                'overtime_date': app.date.strftime('%Y-%m-%d') if app.date and hasattr(app.date, 'strftime') else (app.date if app.date else None),
                'start_time': app.start_time,
                'end_time': app.end_time,
                'reason': app.reason,
                'status': app.status,
                'approver_id': app.approver_id,
                'approver': {
                    'id': approver.id if approver else None,
                    'username': approver.username if approver else None,
                    'name': f"{approver.first_name or ''} {approver.last_name or ''}".strip() or approver.username if approver else None
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

        application = OvertimeApplication(
            user_id=current_user_id,
            date=overtime_date,
            start_time=start_time,
            end_time=end_time,
            reason=reason,
            status=ApprovalStatus.PENDING.value,
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
        application.approved_at = datetime.utcnow()
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
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
        
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
            result.append({
                'id': us.id,
                'user_id': us.user_id,
                'user': {
                    'id': user.id if user else None,
                    'username': user.username if user else '未知',
                    'name': f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username if user else '未知'
                } if user else None,
                'shift_id': us.shift_id,
                'shift': {
                    'id': shift.id if shift else None,
                    'name': shift.name if shift else '未知',
                    'start_time': shift.start_time if shift else None,
                    'end_time': shift.end_time if shift else None,
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
    """批量为多个用户在日期范围内创建/更新排班"""
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

        if not user_ids or not shift_id:
            return jsonify({'error': '员工和班次均为必填项'}), 400

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

        created_count = 0
        for uid in user_ids:
            try:
                uid_int = int(uid)
            except (TypeError, ValueError):
                continue
            target_user = User.query.get(uid_int)
            if not target_user:
                continue
            us = UserShift(
                user_id=uid_int,
                shift_id=shift_id,
                effective_date=effective_date or datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
                expire_date=expire_date
            )
            db.session.add(us)
            created_count += 1

        db.session.commit()

        try:
            create_audit_log(
                user_id=current_user_id,
                action='batch_create',
                resource_type='user_shift',
                resource_id=None,
                details=f'批量排班: 班次ID={shift_id}, 员工数={created_count}',
                request=request
            )
        except Exception:
            pass

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
            query = query.join(User).filter(User.department == department)
        
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
                    'name': f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username if user else '未知',
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
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
        
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
            overtime_query = overtime_query.join(User).filter(User.department == department)
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
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
        
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
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
        
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
                    'name': f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username if user else '未知',
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
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()

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
        records = AttendanceRecord.query.filter(
            AttendanceRecord.user_id == current_user_id,
            AttendanceRecord.record_date >= start_date,
            AttendanceRecord.record_date <= end_date
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
                sh, sm = [int(x) for x in start.split(':')[:2]]
                eh, em = [int(x) for x in end.split(':')[:2]]
                return max(0.0, (eh * 60 + em - sh * 60 - sm) / 60.0)
            except Exception:
                return 0.0

        overtime_workday = 0.0
        overtime_weekend = 0.0
        overtime_holiday = 0.0
        overtime_total = 0.0
        for ot in overtime_records:
            hours = _parse_hours(ot.start_time, ot.end_time)
            overtime_total += hours
            try:
                d = ot.date.date() if hasattr(ot.date, 'date') else ot.date
                wd = d.weekday()
                cal_entry = WorkCalendar.query.filter(db.func.date(WorkCalendar.date) == d).first()
                if cal_entry and cal_entry.is_holiday:
                    overtime_holiday += hours
                elif wd >= 5:
                    overtime_weekend += hours
                else:
                    overtime_workday += hours
            except Exception:
                overtime_workday += hours

        overtime_breakdown = {
            'workday': round(overtime_workday, 2),
            'weekend': round(overtime_weekend, 2),
            'holiday': round(overtime_holiday, 2)
        }

        # 7) 年假余额（这里采用通用约定：每满一年5天，传入用户入职信息，若无则默认为5天）
        annual_leave_quota = 5.0
        annual_leave_used = leave_breakdown.get('annual_leave', 0)
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


def _build_attendance_export_rows(query, User, AttendanceRecord):
    """根据查询构造考勤导出数据行"""
    rows = []
    for record in query.all():
        user = record.user
        rows.append({
            'ID': record.id,
            '员工账号': user.username if user else '',
            '员工姓名': f"{user.first_name or ''} {user.last_name or ''}".strip() or (user.username if user else '未知'),
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

        target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()

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
