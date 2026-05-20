from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
import json

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

def get_require_permission():
    from enhanced_app import require_permission
    return require_permission

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

# 获取加班申请列表
@attendance_bp.route('/overtime-applications', methods=['GET'])
@jwt_required()
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

# 获取班次列表
@attendance_bp.route('/shifts', methods=['GET'])
@jwt_required()
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

# 获取用户班次安排
@attendance_bp.route('/user-shifts', methods=['GET'])
@jwt_required()
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

# 获取考勤异常列表
@attendance_bp.route('/exceptions', methods=['GET'])
@jwt_required()
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
