from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
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
