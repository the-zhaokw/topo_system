from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
from enhanced_app import create_audit_log, logger, require_permission, db, AttendanceStatus, ApprovalStatus, Activity
import json

# 创建考勤管理蓝图
attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

# 同步考勤数据
def sync_attendance_data(application):
    """同步考勤数据"""
    # 延迟导入模型以避免循环导入
    from enhanced_app import User, AttendanceRecord, LeaveApplication, OvertimeApplication, AttendanceException
    
    try:
        if application.status == ApprovalStatus.APPROVED.value:
            # 更新考勤记录
            start_date = application.start_date
            end_date = application.end_date
            
            current_date = start_date
            while current_date <= end_date:
                # 查找或创建考勤记录
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
    # 延迟导入模型以避免循环导入
    from enhanced_app import User, WorkCalendar
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        year = request.args.get('year', datetime.utcnow().year, type=int)
        month = request.args.get('month', datetime.utcnow().month, type=int)
        
        # 获取指定年月的工作日历
        calendar = WorkCalendar.query.filter(
            db.extract('year', WorkCalendar.date) == year,
            db.extract('month', WorkCalendar.date) == month
        ).all()
        
        return jsonify([day.to_dict() for day in calendar])
    except Exception as e:
        logger.error(f"Error getting work calendar: {str(e)}")
        return jsonify({'error': '获取工作日历失败'}), 500

# 创建/更新工作日历
@attendance_bp.route('/work-calendar', methods=['POST'])
def update_work_calendar():
    # 延迟导入模型以避免循环导入
    from enhanced_app import WorkCalendar
    
    @require_permission('manage_attendance')
    def permission_wrapped_function():
        """创建/更新工作日历"""
        try:
            data = request.json
            year = data.get('year')
            month = data.get('month')
            calendar_data = data.get('calendar')
            
            if not all([year, month, calendar_data]):
                return jsonify({'error': '缺少必要参数'}), 400
            
            # 更新日历数据
            for day_data in calendar_data:
                date = datetime.strptime(f"{year}-{month}-{day_data['day']}", '%Y-%m-%d').date()
                calendar = WorkCalendar.query.filter_by(date=date).first()
                
                if calendar:
                    calendar.is_working_day = day_data['is_working_day']
                    calendar.is_holiday = day_data['is_holiday']
                    calendar.note = day_data.get('note', '')
                else:
                    calendar = WorkCalendar(
                        date=date,
                        is_working_day=day_data['is_working_day'],
                        is_holiday=day_data['is_holiday'],
                        note=day_data.get('note', '')
                    )
                    db.session.add(calendar)
            
            db.session.commit()
            return jsonify({'message': '工作日历更新成功'})
        except Exception as e:
            logger.error(f"Error updating work calendar: {str(e)}")
            return jsonify({'error': '更新工作日历失败'}), 500
    
    return permission_wrapped_function()

# 获取班次列表
@attendance_bp.route('/shifts', methods=['GET'])
@jwt_required()
def get_shifts():
    """获取班次列表"""
    from enhanced_app import User, ShiftSchedule, UserShift

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        if current_user.can('manage_attendance'):
            shifts = ShiftSchedule.query.all()
        else:
            shifts = ShiftSchedule.query.join(UserShift).filter(
                UserShift.user_id == current_user_id
            ).all()

        return jsonify([shift.to_dict() for shift in shifts])
    except Exception as e:
        logger.error(f"Error getting shifts: {str(e)}")
        return jsonify({'error': '获取班次失败'}), 500

# 创建班次
@attendance_bp.route('/shifts', methods=['POST'])
def create_shift():
    # 延迟导入模型以避免循环导入
    from enhanced_app import ShiftSchedule

    @require_permission('manage_attendance')
    def permission_wrapped_function():
        """创建班次"""
        try:
            data = request.json
            shift = ShiftSchedule(
                name=data['name'],
                start_time=data['start_time'],
                end_time=data['end_time'],
                shift_type=data.get('shift_type', 'normal'),
                flexible_range=data.get('flexible_range', 30),
                overtime_threshold=data.get('overtime_threshold', 60),
                is_active=data.get('is_active', True),
                description=data.get('description', '')
            )
            db.session.add(shift)
            db.session.commit()
            return jsonify(shift.to_dict()), 201
        except Exception as e:
            logger.error(f"Error creating shift: {str(e)}")
            return jsonify({'error': '创建班次失败'}), 500

    return permission_wrapped_function()

# 更新班次
@attendance_bp.route('/shifts/<int:shift_id>', methods=['PUT'])
def update_shift(shift_id):
    from enhanced_app import ShiftSchedule

    @require_permission('manage_attendance')
    def permission_wrapped_function():
        """更新班次"""
        try:
            data = request.json
            shift = ShiftSchedule.query.get(shift_id)
            if not shift:
                return jsonify({'error': '班次不存在'}), 404

            if 'name' in data:
                shift.name = data['name']
            if 'start_time' in data:
                shift.start_time = data['start_time']
            if 'end_time' in data:
                shift.end_time = data['end_time']
            if 'shift_type' in data:
                shift.shift_type = data['shift_type']
            if 'flexible_range' in data:
                shift.flexible_range = data['flexible_range']
            if 'overtime_threshold' in data:
                shift.overtime_threshold = data['overtime_threshold']
            if 'is_active' in data:
                shift.is_active = data['is_active']
            if 'description' in data:
                shift.description = data['description']

            db.session.commit()
            return jsonify(shift.to_dict()), 200
        except Exception as e:
            logger.error(f"Error updating shift: {str(e)}")
            return jsonify({'error': '更新班次失败'}), 500

    return permission_wrapped_function()

# 删除班次
@attendance_bp.route('/shifts/<int:shift_id>', methods=['DELETE'])
def delete_shift(shift_id):
    from enhanced_app import ShiftSchedule

    @require_permission('manage_attendance')
    def permission_wrapped_function():
        """删除班次"""
        try:
            shift = ShiftSchedule.query.get(shift_id)
            if not shift:
                return jsonify({'error': '班次不存在'}), 404

            db.session.delete(shift)
            db.session.commit()
            return jsonify({'message': '删除成功'}), 200
        except Exception as e:
            logger.error(f"Error deleting shift: {str(e)}")
            return jsonify({'error': '删除班次失败'}), 500

    return permission_wrapped_function()

# 获取用户班次列表
@attendance_bp.route('/user-shifts', methods=['GET'])
@jwt_required()
def get_user_shifts():
    """获取用户班次列表"""
    from enhanced_app import UserShift, User, ShiftSchedule

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        date_param = request.args.get('date')

        query = UserShift.query

        if not current_user.can('manage_attendance'):
            query = query.filter_by(user_id=current_user_id)
        elif request.args.get('user_id'):
            query = query.filter_by(user_id=request.args.get('user_id', type=int))

        if date_param:
            query = query.filter_by(effective_date=date_param)

        user_shifts = query.all()

        result = []
        for us in user_shifts:
            us_dict = us.to_dict()
            if us.user:
                us_dict['user_name'] = us.user.username
                us_dict['user_real_name'] = f"{us.user.first_name or ''} {us.user.last_name or ''}".strip()
            if us.shift:
                us_dict['shift_name'] = us.shift.name
                us_dict['shift_start_time'] = us.shift.start_time
                us_dict['shift_end_time'] = us.shift.end_time
            result.append(us_dict)

        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting user shifts: {str(e)}")
        return jsonify({'error': '获取用户班次失败'}), 500

# 分配用户班次
@attendance_bp.route('/user-shifts', methods=['POST'])
@jwt_required()
def assign_user_shift():
    from enhanced_app import UserShift, User, db

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        if not current_user.can('manage_attendance'):
            return jsonify({'error': '权限不足'}), 403
        
        data = request.get_json()
        # 检查是否已存在相同的用户班次分配
        existing = UserShift.query.filter_by(
            user_id=data['user_id'],
            effective_date=data['effective_date']
        ).first()
        
        if existing:
            existing.shift_id = data['shift_id']
            user_shift = existing
        else:
            user_shift = UserShift(
                user_id=data['user_id'],
                shift_id=data['shift_id'],
                effective_date=data['effective_date'],
                expire_date=data.get('expire_date')
            )
            db.session.add(user_shift)
        
        db.session.commit()
        return jsonify(user_shift.to_dict()), 201
    except Exception as e:
        logger.error(f"Error assigning user shift: {str(e)}")
        return jsonify({'error': '分配班次失败'}), 500

# 获取考勤记录
@attendance_bp.route('/records', methods=['GET'])
@jwt_required()
def get_attendance_records():
    """获取考勤记录"""
    from enhanced_app import User, AttendanceRecord
    
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

# 获取今日考勤记录
@attendance_bp.route('/records/today', methods=['GET'])
@jwt_required()
def get_today_attendance_record():
    """获取今日考勤记录"""
    from enhanced_app import User, AttendanceRecord
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        # 获取今日日期（使用与 clock_in 相同的格式）
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 查询今日考勤记录
        record = AttendanceRecord.query.filter_by(
            user_id=current_user_id,
            record_date=today
        ).first()
        
        if record:
            return jsonify(record.to_dict())
        else:
            return jsonify({
                'user_id': current_user_id,
                'record_date': today.isoformat(),
                'clock_in_time': None,
                'clock_out_time': None,
                'status': 'absent'
            })
    except Exception as e:
        logger.error(f"Error getting today's attendance record: {str(e)}")
        return jsonify({'error': '获取今日考勤记录失败'}), 500

# 删除考勤记录
@attendance_bp.route('/records/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_attendance_record(record_id):
    """删除考勤记录"""
    from enhanced_app import AttendanceRecord, User

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        record = AttendanceRecord.query.get(record_id)

        if not record:
            return jsonify({'error': '考勤记录不存在'}), 404

        if current_user.role != 'admin' and record.user_id != current_user_id:
            return jsonify({'error': '没有权限删除此记录'}), 403

        db.session.delete(record)
        db.session.commit()

        create_audit_log(
            user_id=current_user_id,
            action='delete_attendance_record',
            resource_type='attendance',
            resource_id=record_id,
            details=f'删除考勤记录: {record_id}',
            request=request
        )

        return jsonify({'success': True, 'message': '删除成功'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting attendance record: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '删除考勤记录失败'}), 500

# 打卡
def get_client_ip():
    """获取客户端IP地址"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    elif request.remote_addr:
        return request.remote_addr
    return request.remote_addr or '0.0.0.0'

@attendance_bp.route('/clock-in', methods=['POST'])
@jwt_required()
def clock_in():
    """上班打卡"""
    from enhanced_app import User, AttendanceRecord, ShiftSchedule, UserShift
    
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
        
        client_ip = get_client_ip()
        
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
    from enhanced_app import User, AttendanceRecord, ShiftSchedule, UserShift
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        # 获取当前日期（使用datetime而不是date，与clock_in保持一致）
        current_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 查找考勤记录
        record = AttendanceRecord.query.filter_by(
            user_id=current_user_id,
            record_date=current_date
        ).first()
        
        if not record or not record.clock_in_time:
            return jsonify({'error': '请先进行上班打卡'}), 400
        
        if record.clock_out_time:
            return jsonify({'error': '今日已下班打卡'}), 400
        
        client_ip = get_client_ip()
        location = request.json.get('location') if request.json else None
        
        record.clock_out_time = datetime.utcnow()
        record.clock_out_ip = client_ip
        record.clock_out_location = location
        
        if record.clock_in_time and record.clock_out_time:
            work_duration = record.clock_out_time - record.clock_in_time
            record.work_hours = work_duration.total_seconds() / 3600
        
        today = datetime.utcnow().date()
        user_shift = UserShift.query.filter(
            UserShift.user_id == current_user_id,
            UserShift.effective_date <= today
        ).order_by(UserShift.effective_date.desc()).first()
        
        if user_shift:
            shift = ShiftSchedule.query.get(user_shift.shift_id)
            if shift:
                shift_end = datetime.strptime(shift.end_time, '%H:%M').time()
                actual_time = datetime.utcnow().time()
                if actual_time < shift_end:
                    shift_end_dt = datetime.combine(today, shift_end)
                    actual_dt = datetime.combine(today, actual_time)
                    early_leave_minutes = int((shift_end_dt - actual_dt).total_seconds() / 60)
                    record.early_leave_minutes = early_leave_minutes
                    record.status = AttendanceStatus.EARLY_LEAVE.value
        
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

# 请假申请
@attendance_bp.route('/leave', methods=['POST'])
@jwt_required()
def apply_leave():
    """请假申请"""
    # 延迟导入模型以避免循环导入
    from enhanced_app import User, LeaveApplication
    
    try:
        current_user_id = get_jwt_identity()
        data = request.json
        
        # 验证输入
        required_fields = ['start_date', 'end_date', 'leave_type', 'reason']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
        
        # 创建请假申请
        application = LeaveApplication(
            user_id=current_user_id,
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            leave_type=data['leave_type'],
            reason=data['reason'],
            status=ApprovalStatus.PENDING.value,
            created_at=datetime.utcnow()
        )
        
        db.session.add(application)
        db.session.commit()
        
        # 创建活动记录
        activity = Activity(
            performed_by=current_user_id,
            action='apply_leave',
            description=f'提交请假申请: {data["leave_type"]}',
            target_type='leave_application',
            target_id=application.id
        )
        db.session.add(activity)
        db.session.commit()
        
        # 创建log
        create_audit_log(
            user_id=current_user_id,
            action='apply_leave',
            resource_type='leave',
            resource_id=application.id,
            details=f'请假申请: {data["leave_type"]}',
            request=request
        )
        
        return jsonify({'message': '请假申请提交成功', 'application': application.to_dict()}), 201
    except Exception as e:
        logger.error(f"Error applying leave: {str(e)}")
        return jsonify({'error': '请假申请失败'}), 500


@attendance_bp.route('/leave-applications', methods=['POST'])
@jwt_required()
def create_leave_application():
    """创建请假申请（支持多级审批）"""
    from enhanced_app import User, LeaveApplication
    import json
    
    try:
        current_user_id = get_jwt_identity()
        data = request.json
        
        required_fields = ['start_date', 'end_date', 'leave_type', 'reason']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
        
        application = LeaveApplication(
            user_id=current_user_id,
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            leave_type=data['leave_type'],
            reason=data['reason'],
            status='pending',
            emergency_flag=data.get('emergency_flag', False),
            attachment_path=data.get('attachment_path', ''),
            current_approver_level=1
        )
        
        if data.get('approver_id'):
            application.approver_id = data['approver_id']
        
        approval_levels = data.get('approval_levels', [])
        if approval_levels:
            application.approval_levels = json.dumps(approval_levels)
            if len(approval_levels) > 0:
                first_approver = approval_levels[0]
                if 'approver_id' in first_approver:
                    application.approver_id = first_approver['approver_id']
        
        db.session.add(application)
        db.session.commit()
        
        # 创建活动记录
        activity = Activity(
            performed_by=current_user_id,
            action='create_leave_application',
            description=f'创建请假申请: {data["leave_type"]}',
            target_type='leave_application',
            target_id=application.id
        )
        db.session.add(activity)
        db.session.commit()
        
        create_audit_log(
            user_id=current_user_id,
            action='create_leave_application',
            resource_type='leave_application',
            resource_id=application.id,
            details=f'创建请假申请: {data["leave_type"]}',
            request=request
        )
        
        return jsonify({'message': '请假申请提交成功', 'application': application.to_dict()}), 201
    except Exception as e:
        logger.error(f"Error creating leave application: {str(e)}")
        db.session.rollback()
        return jsonify({'error': '请假申请失败'}), 500

# 加班申请
@attendance_bp.route('/overtime', methods=['POST'])
@jwt_required()
def apply_overtime():
    """加班申请"""
    # 延迟导入模型以避免循环导入
    from enhanced_app import User, OvertimeApplication
    
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证输入
        required_fields = ['date', 'start_time', 'end_time', 'reason']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
        
        # 创建加班申请
        application = OvertimeApplication(
            user_id=current_user_id,
            date=datetime.strptime(data['date'], '%Y-%m-%d'),
            start_time=data['start_time'],
            end_time=data['end_time'],
            reason=data['reason'],
            status="pending"
        )
        
        # 如果指定了审批人，验证审批人是否存在
        if data.get('approver_id'):
            approver = User.query.get(int(data['approver_id']))
            if not approver:
                return jsonify({'error': '指定的审批人不存在'}), 404
            application.approver_id = int(data['approver_id'])
        
        db.session.add(application)
        db.session.commit()
        
        # 创建活动记录
        activity = Activity(
            performed_by=current_user_id,
            action='apply_overtime',
            description=f'提交加班申请: {data["date"]}',
            target_type='overtime_application',
            target_id=application.id
        )
        db.session.add(activity)
        db.session.commit()
        
        # 创建log
        create_audit_log(
            user_id=current_user_id,
            action='apply_overtime',
            resource_type='overtime',
            resource_id=application.id,
            details=f'加班申请: {data["date"]}',
            request=request
        )
        
        return jsonify({'message': '加班申请提交成功', 'application': application.to_dict()}), 201
    except Exception as e:
        logger.error(f"Error applying overtime: {str(e)}")
        return jsonify({'error': '加班申请失败'}), 500

# 考勤异常处理 API (F-005-07)
@attendance_bp.route('/exceptions', methods=['GET'])
@jwt_required()
def get_exceptions():
    """获取考勤异常列表"""
    from enhanced_app import User, AttendanceException
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        # 构建查询
        query = AttendanceException.query
        
        # 普通员工只能查看自己的异常记录，管理员可以查看所有
        if current_user.role != 'admin' and current_user.role != 'hr_admin':
            query = query.filter_by(user_id=current_user_id)
        
        # 按状态筛选
        if status:
            query = query.filter_by(status=status)
        
        # 分页
        pagination = query.order_by(AttendanceException.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = []
        for exc in pagination.items:
            exc_dict = exc.to_dict()
            # 添加用户名信息
            if exc.user:
                exc_dict['user_name'] = exc.user.username
            if exc.approver:
                exc_dict['approver_name'] = exc.approver.username
            result.append(exc_dict)
        
        return jsonify({
            'exceptions': result,
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        logger.error(f"Error getting exceptions: {str(e)}")
        return jsonify({'error': '获取异常记录失败'}), 500


@attendance_bp.route('/exceptions', methods=['POST'])
@jwt_required()
def create_exception():
    """提交考勤异常说明"""
    from enhanced_app import User, AttendanceException
    
    try:
        current_user_id = get_jwt_identity()
        data = request.json
        
        # 验证输入
        required_fields = ['record_date', 'exception_type', 'reason']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
        
        # 验证异常类型
        valid_types = ['missing_card', 'late', 'early_leave', 'absent', 'other']
        if data['exception_type'] not in valid_types:
            return jsonify({'error': '无效的异常类型'}), 400
        
        # 创建异常记录
        exception = AttendanceException(
            user_id=current_user_id,
            record_date=datetime.strptime(data['record_date'], '%Y-%m-%d'),
            exception_type=data['exception_type'],
            reason=data['reason'],
            status='pending'
        )
        
        db.session.add(exception)
        db.session.commit()
        
        # 创建审计日志
        create_audit_log(
            user_id=current_user_id,
            action='create_exception',
            resource_type='attendance_exception',
            resource_id=exception.id,
            details=f'提交考勤异常说明: {data["exception_type"]}',
            request=request
        )
        
        return jsonify({
            'message': '异常说明提交成功',
            'exception': exception.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error creating exception: {str(e)}")
        db.session.rollback()
        return jsonify({'error': '提交异常说明失败'}), 500


@attendance_bp.route('/exceptions/<exception_id>/approve', methods=['POST'])
@jwt_required()
def approve_exception(exception_id):
    """审批考勤异常"""
    from enhanced_app import User, AttendanceException
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        data = request.json
        
        if isinstance(exception_id, str) and exception_id.startswith('attendance_exception_'):
            exception_id = int(exception_id.replace('attendance_exception_', ''))
        
        # 只有管理员和 HR 可以审批
        if current_user.role != 'admin' and current_user.role != 'hr_admin':
            return jsonify({'error': '无权限审批异常'}), 403
        
        # 查找异常记录
        exception = AttendanceException.query.get(exception_id)
        if not exception:
            return jsonify({'error': '异常记录不存在'}), 404
        
        if exception.status != 'pending':
            return jsonify({'error': '该异常已处理'}), 400
        
        # 审批
        exception.status = data.get('status', 'approved')
        exception.approver_id = current_user_id
        exception.approved_at = datetime.utcnow()
        
        db.session.commit()
        
        # 创建审计日志
        create_audit_log(
            user_id=current_user_id,
            action='approve_exception',
            resource_type='attendance_exception',
            resource_id=exception_id,
            details=f'审批考勤异常: {exception.status}',
            request=request
        )
        
        return jsonify({
            'message': '审批成功',
            'exception': exception.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error approving exception: {str(e)}")
        db.session.rollback()
        return jsonify({'error': '审批失败'}), 500


@attendance_bp.route('/leave-applications', methods=['GET'])
@jwt_required()
def get_leave_applications():
    """获取请假申请列表"""
    from enhanced_app import User, LeaveApplication
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        query = LeaveApplication.query
        
        if current_user.role != 'admin' and current_user.role != 'hr_admin':
            query = query.filter(LeaveApplication.user_id == current_user_id)
        
        if status:
            query = query.filter(LeaveApplication.status == status)
        
        query = query.order_by(LeaveApplication.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        applications = pagination.items
        
        result = []
        for app in applications:
            app_dict = app.to_dict()
            user = User.query.get(app.user_id)
            if user:
                app_dict['applicant'] = user.username
                app_dict['applicant_name'] = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username
            if app.approver_id:
                approver = User.query.get(app.approver_id)
                if approver:
                    app_dict['approver_name'] = approver.username
            result.append(app_dict)
        
        return jsonify({
            'applications': result,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting leave applications: {str(e)}")
        return jsonify({'error': '获取请假申请列表失败'}), 500


@attendance_bp.route('/leave-applications/<app_id>/approve', methods=['POST'])
@jwt_required()
def approve_leave_application(app_id):
    """审批请假申请（支持多级审批）"""
    from enhanced_app import User, LeaveApplication
    import json
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        data = request.json
        
        if current_user.role not in ['admin', 'hr_admin', 'project_manager']:
            return jsonify({'error': '无权限审批请假申请'}), 403
        
        if isinstance(app_id, str) and app_id.startswith('leave_'):
            app_id = int(app_id.replace('leave_', ''))
        
        application = LeaveApplication.query.get(app_id)
        if not application:
            return jsonify({'error': '请假申请不存在'}), 404
        
        if application.status not in ['pending', 'approved_level_1', 'approved_level_2']:
            return jsonify({'error': '该申请已处理完毕'}), 400
        
        approval_action = data.get('action', 'approve')
        approval_comment = data.get('comment', '')
        approval_level = application.current_approver_level or 1
        
        approval_levels_list = []
        if application.approval_levels:
            try:
                approval_levels_list = json.loads(application.approval_levels)
            except:
                approval_levels_list = []
        
        if approval_action == 'approve':
            if approval_level < 3:
                application.status = f'approved_level_{approval_level}'
                application.current_approver_level = approval_level + 1
                application.approver_id = current_user_id
                application.approved_at = datetime.utcnow()
                approval_levels_list.append({
                    'level': approval_level,
                    'approver_id': current_user_id,
                    'approver_name': current_user.username,
                    'status': 'approved',
                    'comment': approval_comment,
                    'approved_at': datetime.utcnow().isoformat()
                })
                application.approval_levels = json.dumps(approval_levels_list)
                next_approver_id = data.get('next_approver_id')
                if next_approver_id:
                    application.approver_id = int(next_approver_id)
            else:
                application.status = 'approved'
                application.approver_id = current_user_id
                application.approved_at = datetime.utcnow()
                approval_levels_list.append({
                    'level': approval_level,
                    'approver_id': current_user_id,
                    'approver_name': current_user.username,
                    'status': 'approved',
                    'comment': approval_comment,
                    'approved_at': datetime.utcnow().isoformat()
                })
                application.approval_levels = json.dumps(approval_levels_list)
        else:
            application.status = 'rejected'
            application.approver_id = current_user_id
            application.approved_at = datetime.utcnow()
            approval_levels_list.append({
                'level': approval_level,
                'approver_id': current_user_id,
                'approver_name': current_user.username,
                'status': 'rejected',
                'comment': approval_comment,
                'approved_at': datetime.utcnow().isoformat()
            })
            application.approval_levels = json.dumps(approval_levels_list)
        
        db.session.commit()
        
        # 创建活动记录
        activity = Activity(
            performed_by=current_user_id,
            action='approve_leave_application',
            description=f'审批请假申请: {application.status}',
            target_type='leave_application',
            target_id=app_id
        )
        db.session.add(activity)
        db.session.commit()
        
        create_audit_log(
            user_id=current_user_id,
            action='approve_leave_application',
            resource_type='leave_application',
            resource_id=app_id,
            details=f'审批请假申请: {application.status}',
            request=request
        )
        
        return jsonify({
            'message': '审批成功',
            'application': application.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error approving leave application: {str(e)}")
        db.session.rollback()
        return jsonify({'error': '审批失败'}), 500


@attendance_bp.route('/leave/<int:app_id>', methods=['PUT'])
@jwt_required()
def update_leave_application(app_id):
    """更新请假申请（包含多级审批配置）"""
    from enhanced_app import User, LeaveApplication
    import json
    
    try:
        current_user_id = get_jwt_identity()
        data = request.json
        
        application = LeaveApplication.query.get(app_id)
        if not application:
            return jsonify({'error': '请假申请不存在'}), 404
        
        if application.user_id != int(current_user_id):
            return jsonify({'error': '无权限修改此申请'}), 403
        
        if application.status != 'pending':
            return jsonify({'error': '只能修改待审批状态的申请'}), 400
        
        if 'emergency_flag' in data:
            application.emergency_flag = data['emergency_flag']
        
        if 'approval_levels' in data:
            application.approval_levels = json.dumps(data['approval_levels'])
            if data['approval_levels'] and len(data['approval_levels']) > 0:
                first_approver = data['approval_levels'][0]
                if 'approver_id' in first_approver:
                    application.approver_id = first_approver['approver_id']
        
        db.session.commit()
        
        return jsonify({
            'message': '更新成功',
            'application': application.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error updating leave application: {str(e)}")
        db.session.rollback()
        return jsonify({'error': '更新失败'}), 500


# 加班申请列表 API
@attendance_bp.route('/overtime-applications', methods=['GET'])
@jwt_required()
def get_overtime_applications():
    """获取加班申请列表"""
    from enhanced_app import User, OvertimeApplication
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', '')
        user_id = request.args.get('user_id', '')
        
        query = OvertimeApplication.query
        
        # 根据角色过滤
        if current_user.role not in ['admin', 'hr', 'department_manager']:
            query = query.filter(OvertimeApplication.user_id == current_user_id)
        elif user_id:
            query = query.filter(OvertimeApplication.user_id == user_id)
        
        if status:
            query = query.filter(OvertimeApplication.status == status)
        
        applications = query.order_by(OvertimeApplication.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = []
        for app in applications.items:
            user = User.query.get(app.user_id)
            app_dict = app.to_dict()
            app_dict['user_name'] = user.username if user else ''
            app_dict['user_real_name'] = f"{user.first_name or ''} {user.last_name or ''}".strip() if user else ''
            
            approver = User.query.get(app.approver_id) if app.approver_id else None
            app_dict['approver_name'] = approver.username if approver else ''
            
            result.append(app_dict)
        
        return jsonify({
            'applications': result,
            'total': applications.total,
            'pages': applications.pages,
            'current_page': page
        }), 200
    except Exception as e:
        logger.error(f"Error getting overtime applications: {str(e)}")
        return jsonify({'error': '获取加班申请列表失败'}), 500


# 加班审批 API
@attendance_bp.route('/overtime-applications/<app_id>/approve', methods=['POST'])
@jwt_required()
def approve_overtime_application(app_id):
    """审批加班申请"""
    from enhanced_app import User, OvertimeApplication
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        if current_user.role not in ['admin', 'hr', 'department_manager']:
            return jsonify({'error': '无权限审批加班申请'}), 403
        
        if isinstance(app_id, str) and app_id.startswith('overtime_'):
            app_id = int(app_id.replace('overtime_', ''))
        
        data = request.json
        action = data.get('action', 'approve')
        approval_comment = data.get('comment', '')
        
        application = OvertimeApplication.query.get(app_id)
        if not application:
            return jsonify({'error': '加班申请不存在'}), 404
        
        if application.status != 'pending':
            return jsonify({'error': '该申请已审批，不能重复审批'}), 400
        
        if action == 'approve':
            application.status = 'approved'
        elif action == 'reject':
            application.status = 'rejected'
            application.rejection_reason = approval_comment
        else:
            return jsonify({'error': '无效的审批操作'}), 400
        
        application.approver_id = int(current_user_id)
        application.approved_at = datetime.utcnow()
        
        db.session.commit()
        
        # 创建活动记录
        activity = Activity(
            performed_by=current_user_id,
            action='approve_overtime_application',
            description=f'审批加班申请: {action}',
            target_type='overtime_application',
            target_id=app_id
        )
        db.session.add(activity)
        db.session.commit()
        
        create_audit_log(
            user_id=current_user_id,
            action='approve_overtime_application',
            resource_type='overtime_application',
            resource_id=app_id,
            details=f'审批加班申请: {action}, 批注: {approval_comment}',
            request=request
        )
        
        return jsonify({
            'message': '审批成功',
            'application': application.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error approving overtime application: {str(e)}")
        db.session.rollback()
        return jsonify({'error': '审批失败'}), 500


@attendance_bp.route('/reports/monthly', methods=['GET'])
@jwt_required()
def get_monthly_report():
    """获取月度考勤报表"""
    from enhanced_app import User, AttendanceRecord, LeaveApplication, OvertimeApplication
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        year = request.args.get('year', datetime.utcnow().year, type=int)
        month = request.args.get('month', datetime.utcnow().month, type=int)
        user_id = request.args.get('user_id', type=int)

        if not current_user.can('manage_attendance') and not current_user.can('view_attendance'):
            user_id = current_user_id
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        query = AttendanceRecord.query.filter(
            AttendanceRecord.record_date >= start_date,
            AttendanceRecord.record_date <= end_date
        )
        
        if user_id:
            query = query.filter(AttendanceRecord.user_id == user_id)
        
        records = query.all()
        
        user_ids = set(r.user_id for r in records)
        users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
        user_map = {u.id: u for u in users}
        
        result = []
        for record in records:
            record_dict = record.to_dict()
            user = user_map.get(record.user_id)
            if user:
                record_dict['user_name'] = user.username
                record_dict['user_real_name'] = f"{user.first_name or ''} {user.last_name or ''}".strip()
            result.append(record_dict)
        
        summary = calculate_monthly_summary(records, year, month)
        
        return jsonify({
            'records': result,
            'summary': summary,
            'year': year,
            'month': month
        })
    except Exception as e:
        logger.error(f"Error getting monthly report: {str(e)}")
        return jsonify({'error': '获取月度报表失败'}), 500


def calculate_monthly_summary(records, year, month):
    """计算月度考勤汇总"""
    from collections import defaultdict
    
    user_stats = defaultdict(lambda: {
        'present': 0, 'late': 0, 'early_leave': 0, 
        'absent': 0, 'leave': 0, 'work_hours': 0,
        'overtime_hours': 0, 'late_minutes': 0, 'early_leave_minutes': 0
    })
    
    for record in records:
        uid = record.user_id
        status = record.status
        
        if status == AttendanceStatus.PRESENT.value:
            user_stats[uid]['present'] += 1
        elif status == AttendanceStatus.LATE.value:
            user_stats[uid]['late'] += 1
            user_stats[uid]['late_minutes'] += record.late_minutes or 0
        elif status == AttendanceStatus.EARLY_LEAVE.value:
            user_stats[uid]['early_leave'] += 1
            user_stats[uid]['early_leave_minutes'] += record.early_leave_minutes or 0
        elif status == AttendanceStatus.ABSENT.value:
            user_stats[uid]['absent'] += 1
        elif status == AttendanceStatus.LEAVE.value:
            user_stats[uid]['leave'] += 1
        
        user_stats[uid]['work_hours'] += record.work_hours or 0
        user_stats[uid]['overtime_hours'] += record.overtime_hours or 0
    
    return dict(user_stats)


@attendance_bp.route('/reports/overview', methods=['GET'])
@jwt_required()
def get_reports_overview():
    """获取考勤报表概览数据"""
    from enhanced_app import User, AttendanceRecord
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date:
            start_date = datetime.utcnow().replace(day=1).date()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

        if not end_date:
            end_date = datetime.utcnow().date()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        query = AttendanceRecord.query.filter(
            AttendanceRecord.record_date >= start_date,
            AttendanceRecord.record_date <= end_date
        )

        if not current_user.can('manage_attendance'):
            query = query.filter(AttendanceRecord.user_id == current_user_id)

        records = query.all()
        
        total = len(records)
        present = sum(1 for r in records if r.status == AttendanceStatus.PRESENT.value)
        late = sum(1 for r in records if r.status == AttendanceStatus.LATE.value)
        early_leave = sum(1 for r in records if r.status == AttendanceStatus.EARLY_LEAVE.value)
        absent = sum(1 for r in records if r.status == AttendanceStatus.ABSENT.value)
        
        total_work_hours = sum(r.work_hours or 0 for r in records)
        total_overtime = sum(r.overtime_hours or 0 for r in records)
        
        user_ids = set(r.user_id for r in records)
        total_employees = len(user_ids)
        
        attendance_rate = round((present / total * 100), 2) if total > 0 else 0
        
        return jsonify({
            'totalEmployees': total_employees,
            'attendanceRate': attendance_rate,
            'lateCount': late,
            'earlyLeaveCount': early_leave,
            'absenceCount': absent,
            'overtimeHours': round(total_overtime, 2),
            'totalWorkHours': round(total_work_hours, 2),
            'presentCount': present,
            'totalRecords': total
        })
    except Exception as e:
        logger.error(f"Error getting reports overview: {str(e)}")
        return jsonify({'error': '获取报表概览失败'}), 500


@attendance_bp.route('/reports/detail', methods=['GET'])
@jwt_required()
def get_reports_detail():
    """获取考勤报表详细数据"""
    from enhanced_app import User, AttendanceRecord
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        if not current_user:
            return jsonify({'error': '用户不存在'}), 404

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        user_id = request.args.get('user_id', type=int)

        query = AttendanceRecord.query

        if start_date:
            query = query.filter(AttendanceRecord.record_date >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(AttendanceRecord.record_date <= datetime.strptime(end_date, '%Y-%m-%d'))

        if not current_user.can('manage_attendance'):
            query = query.filter(AttendanceRecord.user_id == current_user_id)
        elif user_id:
            query = query.filter(AttendanceRecord.user_id == user_id)
        
        query = query.order_by(AttendanceRecord.record_date.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for record in pagination.items:
            record_dict = record.to_dict()
            user = User.query.get(record.user_id)
            if user:
                record_dict['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            result.append(record_dict)
        
        return jsonify({
            'records': result,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
    except Exception as e:
        logger.error(f"Error getting reports detail: {str(e)}")
        return jsonify({'error': '获取报表详情失败'}), 500


# ==================== 考勤统计报表 API ====================

@attendance_bp.route('/reports/overview', methods=['GET'])
@jwt_required()
def get_attendance_overview():
    """获取考勤统计概览"""
    from enhanced_app import User, AttendanceRecord, LeaveApplication, OvertimeApplication
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        period = request.args.get('period', 'daily')
        date = request.args.get('date')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        today = datetime.utcnow().date()
        
        if period == 'daily':
            target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else today
            start = datetime.combine(target_date, datetime.min.time())
            end = datetime.combine(target_date + timedelta(days=1), datetime.min.time())
        elif period == 'weekly':
            target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else today
            week_start = target_date - timedelta(days=target_date.weekday())
            start = datetime.combine(week_start, datetime.min.time())
            end = datetime.combine(week_start + timedelta(days=7), datetime.min.time())
        elif period == 'monthly':
            target_date = datetime.strptime(date, '%Y-%m').date() if date else today
            month_start = target_date.replace(day=1)
            if target_date.month == 12:
                month_end = target_date.replace(year=target_date.year + 1, month=1, day=1)
            else:
                month_end = target_date.replace(month=target_date.month + 1, day=1)
            start = datetime.combine(month_start, datetime.min.time())
            end = datetime.combine(month_end, datetime.min.time())
        elif period == 'custom' and start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        else:
            start = datetime.combine(today, datetime.min.time())
            end = datetime.combine(today + timedelta(days=1), datetime.min.time())
        
        users = User.query.filter(User.is_active == True).all() if hasattr(User, 'is_active') else User.query.all()
        total_employees = len([u for u in users if u.role not in ['admin', 'super_admin']])
        
        attendance_records = AttendanceRecord.query.filter(
            AttendanceRecord.record_date >= start,
            AttendanceRecord.record_date < end
        ).all()
        
        present_count = sum(1 for r in attendance_records if r.status in ['present', 'normal'])
        late_count = sum(1 for r in attendance_records if r.late_minutes and r.late_minutes > 0)
        absent_count = sum(1 for r in attendance_records if r.status in ['absent', 'missing'])
        
        attendance_rate = round((present_count / (total_employees * max(1, (end - start).days)) * 100), 1) if total_employees > 0 else 0
        
        overtime_records = OvertimeApplication.query.filter(
            OvertimeApplication.date >= start,
            OvertimeApplication.date < end,
            OvertimeApplication.status == 'approved'
        ).all()
        
        total_overtime_hours = sum(
            (datetime.strptime(o.end_time, '%H:%M') - datetime.strptime(o.start_time, '%H:%M')).seconds / 3600
            for o in overtime_records if o.start_time and o.end_time
        )
        
        return jsonify({
            'totalEmployees': total_employees,
            'attendanceRate': attendance_rate,
            'lateCount': late_count,
            'absenceCount': absent_count,
            'overtimeHours': round(total_overtime_hours, 1)
        })
    except Exception as e:
        logger.error(f"Error getting attendance overview: {str(e)}")
        return jsonify({'error': '获取考勤概览失败'}), 500


@attendance_bp.route('/reports/detail', methods=['GET'])
@jwt_required()
def get_attendance_detail():
    """获取考勤明细"""
    from enhanced_app import User, AttendanceRecord
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        period = request.args.get('period', 'daily')
        date = request.args.get('date')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        today = datetime.utcnow().date()
        
        if period == 'daily':
            target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else today
            start = datetime.combine(target_date, datetime.min.time())
            end = datetime.combine(target_date + timedelta(days=1), datetime.min.time())
        elif period == 'weekly':
            target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else today
            week_start = target_date - timedelta(days=target_date.weekday())
            start = datetime.combine(week_start, datetime.min.time())
            end = datetime.combine(week_start + timedelta(days=7), datetime.min.time())
        elif period == 'monthly':
            target_date = datetime.strptime(date, '%Y-%m').date() if date else today
            month_start = target_date.replace(day=1)
            if target_date.month == 12:
                month_end = target_date.replace(year=target_date.year + 1, month=1, day=1)
            else:
                month_end = target_date.replace(month=target_date.month + 1, day=1)
            start = datetime.combine(month_start, datetime.min.time())
            end = datetime.combine(month_end, datetime.min.time())
        elif period == 'custom' and start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        else:
            start = datetime.combine(today, datetime.min.time())
            end = datetime.combine(today + timedelta(days=1), datetime.min.time())
        
        query = AttendanceRecord.query.filter(
            AttendanceRecord.record_date >= start,
            AttendanceRecord.record_date < end
        )
        
        if current_user.role != 'admin':
            query = query.filter(AttendanceRecord.user_id == current_user_id)
        
        pagination = query.order_by(AttendanceRecord.record_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        records = []
        for record in pagination.items:
            user = User.query.get(record.user_id)
            record_dict = record.to_dict()
            record_dict['user'] = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            } if user else None
            records.append(record_dict)
        
        return jsonify({
            'records': records,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        logger.error(f"Error getting attendance detail: {str(e)}")
        return jsonify({'error': '获取考勤明细失败'}), 500


@attendance_bp.route('/reports/exception', methods=['GET'])
@jwt_required()
def get_attendance_exception():
    """获取考勤异常统计"""
    from enhanced_app import User, AttendanceRecord
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        period = request.args.get('period', 'daily')
        date = request.args.get('date')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        today = datetime.utcnow().date()
        
        if period == 'daily':
            target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else today
            start = datetime.combine(target_date, datetime.min.time())
            end = datetime.combine(target_date + timedelta(days=1), datetime.min.time())
        elif period == 'weekly':
            target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else today
            week_start = target_date - timedelta(days=target_date.weekday())
            start = datetime.combine(week_start, datetime.min.time())
            end = datetime.combine(week_start + timedelta(days=7), datetime.min.time())
        elif period == 'monthly':
            target_date = datetime.strptime(date, '%Y-%m').date() if date else today
            month_start = target_date.replace(day=1)
            if target_date.month == 12:
                month_end = target_date.replace(year=target_date.year + 1, month=1, day=1)
            else:
                month_end = target_date.replace(month=target_date.month + 1, day=1)
            start = datetime.combine(month_start, datetime.min.time())
            end = datetime.combine(month_end, datetime.min.time())
        elif period == 'custom' and start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        else:
            start = datetime.combine(today, datetime.min.time())
            end = datetime.combine(today + timedelta(days=1), datetime.min.time())
        
        query = AttendanceRecord.query.filter(
            AttendanceRecord.record_date >= start,
            AttendanceRecord.record_date < end
        )
        
        if current_user.role != 'admin':
            query = query.filter(AttendanceRecord.user_id == current_user_id)
        
        records = query.all()
        
        user_exception_stats = {}
        for record in records:
            user_id = record.user_id
            if user_id not in user_exception_stats:
                user = User.query.get(user_id)
                user_exception_stats[user_id] = {
                    'user_id': user_id,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    } if user else None,
                    'late_count': 0,
                    'early_leave_count': 0,
                    'absence_count': 0,
                    'overtime_count': 0,
                    'total_exceptions': 0
                }
            
            if record.late_minutes and record.late_minutes > 0:
                user_exception_stats[user_id]['late_count'] += 1
                user_exception_stats[user_id]['total_exceptions'] += 1
            
            if record.early_leave_minutes and record.early_leave_minutes > 0:
                user_exception_stats[user_id]['early_leave_count'] += 1
                user_exception_stats[user_id]['total_exceptions'] += 1
            
            if record.status in ['absent', 'missing']:
                user_exception_stats[user_id]['absence_count'] += 1
                user_exception_stats[user_id]['total_exceptions'] += 1
            
            if record.overtime_hours and record.overtime_hours > 0:
                user_exception_stats[user_id]['overtime_count'] += 1
        
        return jsonify(list(user_exception_stats.values()))
    except Exception as e:
        logger.error(f"Error getting attendance exception: {str(e)}")
        return jsonify({'error': '获取考勤异常统计失败'}), 500


@attendance_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_attendance_statistics():
    """获取考勤统计数据（与reports/overtime功能相同，作为统一统计接口）"""
    from enhanced_app import User, OvertimeApplication

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        period = request.args.get('period', 'daily')
        date = request.args.get('date')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        today = datetime.utcnow().date()

        if period == 'daily':
            target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else today
            start = datetime.combine(target_date, datetime.min.time())
            end = datetime.combine(target_date + timedelta(days=1), datetime.min.time())
        elif period == 'weekly':
            target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else today
            week_start = target_date - timedelta(days=target_date.weekday())
            start = datetime.combine(week_start, datetime.min.time())
            end = datetime.combine(week_start + timedelta(days=7), datetime.min.time())
        elif period == 'monthly':
            target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else today
            month_start = target_date.replace(day=1)
            if target_date.month == 12:
                month_end = target_date.replace(year=target_date.year + 1, month=1, day=1)
            else:
                month_end = target_date.replace(month=target_date.month + 1, day=1)
            start = datetime.combine(month_start, datetime.min.time())
            end = datetime.combine(month_end, datetime.min.time())
        elif period == 'custom' and start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        else:
            start = datetime.combine(today, datetime.min.time())
            end = datetime.combine(today + timedelta(days=1), datetime.min.time())

        query = OvertimeApplication.query.filter(
            OvertimeApplication.date >= start,
            OvertimeApplication.date < end,
            OvertimeApplication.status == 'approved'
        )

        if current_user.role != 'admin':
            query = query.filter(OvertimeApplication.user_id == current_user_id)

        overtime_records = query.all()

        user_overtime_stats = {}
        for record in overtime_records:
            user_id = record.user_id
            if user_id not in user_overtime_stats:
                user = User.query.get(user_id)
                user_overtime_stats[user_id] = {
                    'user_id': user_id,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    } if user else None,
                    'total_overtime': 0,
                    'weekday_overtime': 0,
                    'weekend_overtime': 0,
                    'holiday_overtime': 0
                }

            overtime_hours = 0
            if record.start_time and record.end_time:
                overtime_hours = (datetime.strptime(record.end_time, '%H:%M') - datetime.strptime(record.start_time, '%H:%M')).seconds / 3600

            user_overtime_stats[user_id]['total_overtime'] += overtime_hours

            record_date = record.date.date() if isinstance(record.date, datetime) else record.date
            if record_date.weekday() < 5:
                user_overtime_stats[user_id]['weekday_overtime'] += overtime_hours
            else:
                user_overtime_stats[user_id]['weekend_overtime'] += overtime_hours

        for user_id in user_overtime_stats:
            user_overtime_stats[user_id]['total_overtime'] = round(user_overtime_stats[user_id]['total_overtime'], 1)
            user_overtime_stats[user_id]['weekday_overtime'] = round(user_overtime_stats[user_id]['weekday_overtime'], 1)
            user_overtime_stats[user_id]['weekend_overtime'] = round(user_overtime_stats[user_id]['weekend_overtime'], 1)

        return jsonify(list(user_overtime_stats.values()))
    except Exception as e:
        logger.error(f"Error getting attendance statistics: {str(e)}")
        return jsonify({'error': '获取考勤统计失败'}), 500


@attendance_bp.route('/reports/overtime', methods=['GET'])
@jwt_required()
def get_overtime_statistics():
    """获取加班统计"""
    from enhanced_app import User, OvertimeApplication
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        period = request.args.get('period', 'daily')
        date = request.args.get('date')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        today = datetime.utcnow().date()
        
        if period == 'daily':
            target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else today
            start = datetime.combine(target_date, datetime.min.time())
            end = datetime.combine(target_date + timedelta(days=1), datetime.min.time())
        elif period == 'weekly':
            target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else today
            week_start = target_date - timedelta(days=target_date.weekday())
            start = datetime.combine(week_start, datetime.min.time())
            end = datetime.combine(week_start + timedelta(days=7), datetime.min.time())
        elif period == 'monthly':
            target_date = datetime.strptime(date, '%Y-%m').date() if date else today
            month_start = target_date.replace(day=1)
            if target_date.month == 12:
                month_end = target_date.replace(year=target_date.year + 1, month=1, day=1)
            else:
                month_end = target_date.replace(month=target_date.month + 1, day=1)
            start = datetime.combine(month_start, datetime.min.time())
            end = datetime.combine(month_end, datetime.min.time())
        elif period == 'custom' and start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        else:
            start = datetime.combine(today, datetime.min.time())
            end = datetime.combine(today + timedelta(days=1), datetime.min.time())
        
        query = OvertimeApplication.query.filter(
            OvertimeApplication.date >= start,
            OvertimeApplication.date < end,
            OvertimeApplication.status == 'approved'
        )
        
        if current_user.role != 'admin':
            query = query.filter(OvertimeApplication.user_id == current_user_id)
        
        overtime_records = query.all()
        
        user_overtime_stats = {}
        for record in overtime_records:
            user_id = record.user_id
            if user_id not in user_overtime_stats:
                user = User.query.get(user_id)
                user_overtime_stats[user_id] = {
                    'user_id': user_id,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    } if user else None,
                    'total_overtime': 0,
                    'weekday_overtime': 0,
                    'weekend_overtime': 0,
                    'holiday_overtime': 0
                }
            
            overtime_hours = 0
            if record.start_time and record.end_time:
                overtime_hours = (datetime.strptime(record.end_time, '%H:%M') - datetime.strptime(record.start_time, '%H:%M')).seconds / 3600
            
            user_overtime_stats[user_id]['total_overtime'] += overtime_hours
            
            record_date = record.date.date() if isinstance(record.date, datetime) else record.date
            if record_date.weekday() < 5:
                user_overtime_stats[user_id]['weekday_overtime'] += overtime_hours
            else:
                user_overtime_stats[user_id]['weekend_overtime'] += overtime_hours
        
        for user_id in user_overtime_stats:
            user_overtime_stats[user_id]['total_overtime'] = round(user_overtime_stats[user_id]['total_overtime'], 1)
            user_overtime_stats[user_id]['weekday_overtime'] = round(user_overtime_stats[user_id]['weekday_overtime'], 1)
            user_overtime_stats[user_id]['weekend_overtime'] = round(user_overtime_stats[user_id]['weekend_overtime'], 1)
        
        return jsonify(list(user_overtime_stats.values()))
    except Exception as e:
        logger.error(f"Error getting overtime statistics: {str(e)}")
        return jsonify({'error': '获取加班统计失败'}), 500


@attendance_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """获取考勤统计"""
    from enhanced_app import User, OvertimeApplication

    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        period = request.args.get('period', 'daily')
        date = request.args.get('date')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        today = datetime.utcnow().date()

        if period == 'daily':
            target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else today
            start = datetime.combine(target_date, datetime.min.time())
            end = datetime.combine(target_date + timedelta(days=1), datetime.min.time())
        elif period == 'weekly':
            target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else today
            week_start = target_date - timedelta(days=target_date.weekday())
            start = datetime.combine(week_start, datetime.min.time())
            end = datetime.combine(week_start + timedelta(days=7), datetime.min.time())
        elif period == 'monthly':
            target_date = datetime.strptime(date, '%Y-%m').date() if date else today
            month_start = target_date.replace(day=1)
            if target_date.month == 12:
                month_end = target_date.replace(year=target_date.year + 1, month=1, day=1)
            else:
                month_end = target_date.replace(month=target_date.month + 1, day=1)
            start = datetime.combine(month_start, datetime.min.time())
            end = datetime.combine(month_end, datetime.min.time())
        elif period == 'custom' and start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        else:
            start = datetime.combine(today, datetime.min.time())
            end = datetime.combine(today + timedelta(days=1), datetime.min.time())

        query = OvertimeApplication.query.filter(
            OvertimeApplication.date >= start,
            OvertimeApplication.date < end,
            OvertimeApplication.status == 'approved'
        )

        if current_user.role != 'admin':
            query = query.filter(OvertimeApplication.user_id == current_user_id)

        overtime_records = query.all()

        total_overtime_hours = 0
        for record in overtime_records:
            if record.start_time and record.end_time:
                try:
                    start_dt = datetime.strptime(record.start_time, '%H:%M')
                    end_dt = datetime.strptime(record.end_time, '%H:%M')
                    hours = (end_dt - start_dt).seconds / 3600
                    total_overtime_hours += hours
                except:
                    pass

        return jsonify({
            'overtime_hours': round(total_overtime_hours, 1),
            'overtime_count': len(overtime_records),
            'period': period,
            'start_date': start.isoformat() if isinstance(start, datetime) else str(start),
            'end_date': end.isoformat() if isinstance(end, datetime) else str(end)
        })

    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': '获取统计失败'}), 500


@attendance_bp.route('/reports/export', methods=['GET'])
@jwt_required()
def export_attendance_report():
    """导出考勤报表"""
    import pandas as pd
    from io import BytesIO
    from flask import send_file
    from enhanced_app import User, AttendanceRecord, OvertimeApplication
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        period = request.args.get('period', 'daily')
        date = request.args.get('date')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        today = datetime.utcnow().date()
        
        if period == 'daily':
            target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else today
            start = datetime.combine(target_date, datetime.min.time())
            end = datetime.combine(target_date + timedelta(days=1), datetime.min.time())
        elif period == 'weekly':
            target_date = datetime.strptime(date, '%Y-%m-%d').date() if date else today
            week_start = target_date - timedelta(days=target_date.weekday())
            start = datetime.combine(week_start, datetime.min.time())
            end = datetime.combine(week_start + timedelta(days=7), datetime.min.time())
        elif period == 'monthly':
            target_date = datetime.strptime(date, '%Y-%m').date() if date else today
            month_start = target_date.replace(day=1)
            if target_date.month == 12:
                month_end = target_date.replace(year=target_date.year + 1, month=1, day=1)
            else:
                month_end = target_date.replace(month=target_date.month + 1, day=1)
            start = datetime.combine(month_start, datetime.min.time())
            end = datetime.combine(month_end, datetime.min.time())
        elif period == 'custom' and start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        else:
            start = datetime.combine(today, datetime.min.time())
            end = datetime.combine(today + timedelta(days=1), datetime.min.time())
        
        query = AttendanceRecord.query.filter(
            AttendanceRecord.record_date >= start,
            AttendanceRecord.record_date < end
        )
        
        if current_user.role != 'admin':
            query = query.filter(AttendanceRecord.user_id == current_user_id)
        
        records = query.all()
        
        export_data = []
        for record in records:
            user = User.query.get(record.user_id)
            export_data.append({
                '员工姓名': f'{user.first_name or ""} {user.last_name or ""}'.strip() if user else '',
                '用户名': user.username if user else '',
                '日期': record.record_date.strftime('%Y-%m-%d') if record.record_date else '',
                '上班打卡时间': record.clock_in_time.strftime('%H:%M:%S') if record.clock_in_time else '',
                '下班打卡时间': record.clock_out_time.strftime('%H:%M:%S') if record.clock_out_time else '',
                '工作时长': record.work_hours or 0,
                '加班时长': record.overtime_hours or 0,
                '迟到分钟数': record.late_minutes or 0,
                '早退分钟数': record.early_leave_minutes or 0,
                '状态': record.status or ''
            })
        
        df = pd.DataFrame(export_data)
        output = BytesIO()
        df.to_excel(output, index=False, sheet_name='考勤报表')
        output.seek(0)
        
        filename = f'考勤报表_{start.strftime("%Y%m%d")}_{end.strftime("%Y%m%d")}.xlsx'
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Error exporting attendance report: {str(e)}")
        return jsonify({'error': '导出考勤报表失败'}), 500


@attendance_bp.route('/leave-applications/export', methods=['GET'])
@jwt_required()
def export_leave_applications():
    """导出请假申请列表"""
    import pandas as pd
    from io import BytesIO
    from flask import send_file
    from enhanced_app import User, LeaveApplication
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = LeaveApplication.query
        
        if current_user.role != 'admin' and current_user.role != 'hr_admin':
            query = query.filter(LeaveApplication.user_id == current_user_id)
        
        if status:
            query = query.filter(LeaveApplication.status == status)
        
        if start_date:
            query = query.filter(LeaveApplication.start_date >= datetime.strptime(start_date, '%Y-%m-%d'))
        
        if end_date:
            query = query.filter(LeaveApplication.end_date <= datetime.strptime(end_date, '%Y-%m-%d'))
        
        applications = query.order_by(LeaveApplication.created_at.desc()).all()
        
        user_cache = {u.id: u for u in User.query.all()}
        approver_cache = {u.id: u for u in User.query.all()}
        
        export_data = []
        for app in applications:
            user = user_cache.get(app.user_id)
            approver = approver_cache.get(app.approver_id)
            
            days = (app.end_date - app.start_date).days + 1 if app.start_date and app.end_date else 0
            
            export_data.append({
                '申请ID': app.id,
                '申请人': f'{user.first_name or ""} {user.last_name or ""}'.strip() if user else '',
                '用户名': user.username if user else '',
                '请假类型': app.leave_type or '',
                '开始日期': app.start_date.strftime('%Y-%m-%d') if app.start_date else '',
                '结束日期': app.end_date.strftime('%Y-%m-%d') if app.end_date else '',
                '天数': days,
                '请假事由': app.reason or '',
                '状态': app.status or '',
                '审批人': f'{approver.first_name or ""} {approver.last_name or ""}'.strip() if approver else '',
                '审批时间': app.approved_at.strftime('%Y-%m-%d %H:%M:%S') if app.approved_at else '',
                '当前审批层级': app.current_approver_level or 1,
                '紧急标志': '是' if app.emergency_flag else '否',
                '附件路径': app.attachment_path or '',
                '创建时间': app.created_at.strftime('%Y-%m-%d %H:%M:%S') if app.created_at else ''
            })
        
        if not export_data:
            return jsonify({'error': '没有可导出的请假申请数据'}), 404
        
        df = pd.DataFrame(export_data)
        output = BytesIO()
        df.to_excel(output, index=False, sheet_name='请假申请')
        output.seek(0)
        
        filename = f'请假申请_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.xlsx'
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Error exporting leave applications: {str(e)}")
        return jsonify({'error': '导出请假申请失败'}), 500


@attendance_bp.route('/leave-applications/import', methods=['POST'])
@jwt_required()
def import_leave_applications():
    """导入请假申请"""
    import pandas as pd
    from io import BytesIO
    from enhanced_app import User, LeaveApplication
    import openpyxl
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        if current_user.role not in ['admin', 'hr_admin']:
            return jsonify({'error': '权限不足，只有管理员可以导入请假申请'}), 403
        
        if 'file' not in request.files:
            return jsonify({'error': '请上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        filename = file.filename.lower()
        if not filename.endswith(('.csv', '.xlsx')):
            return jsonify({'error': '不支持的文件格式，请上传 CSV 或 Excel 文件'}), 400
        
        user_cache = {u.username: u for u in User.query.all()}
        
        success_count = 0
        error_count = 0
        errors = []
        
        if filename.endswith('.csv'):
            content = file.read().decode('utf-8')
            if content.startswith('\ufeff'):
                content = content[1:]
            from io import StringIO
            input_file = StringIO(content)
            df = pd.read_csv(input_file)
        else:
            input_file = BytesIO(file.read())
            df = pd.read_excel(input_file)
        
        required_columns = ['申请人', '请假类型', '开始日期', '结束日期', '请假事由']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({'error': f'文件缺少必要的列：{", ".join(missing_columns)}'}), 400
        
        leave_type_map = {
            '年假': 'annual', '病假': 'sick', '事假': 'personal',
            '调休假': 'compensatory', '婚假': 'marriage',
            '产假': 'maternity', '陪产假': 'paternity', '丧假': 'bereavement'
        }
        
        for idx, row in df.iterrows():
            try:
                username = str(row.get('申请人', '')).strip()
                leave_type = str(row.get('请假类型', '')).strip()
                start_date_str = str(row.get('开始日期', '')).strip()
                end_date_str = str(row.get('结束日期', '')).strip()
                reason = str(row.get('请假事由', '')).strip()
                
                if not username:
                    errors.append(f'第{idx+2}行：申请人为空')
                    error_count += 1
                    continue
                
                user = user_cache.get(username)
                if not user:
                    errors.append(f'第{idx+2}行：用户"{username}"不存在')
                    error_count += 1
                    continue
                
                if not leave_type:
                    errors.append(f'第{idx+2}行：请假类型为空')
                    error_count += 1
                    continue
                
                if not start_date_str or not end_date_str:
                    errors.append(f'第{idx+2}行：开始日期或结束日期为空')
                    error_count += 1
                    continue
                
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except:
                    errors.append(f'第{idx+2}行：日期格式错误，应为YYYY-MM-DD')
                    error_count += 1
                    continue
                
                if not reason:
                    errors.append(f'第{idx+2}行：请假事由为空')
                    error_count += 1
                    continue
                
                db_type = leave_type_map.get(leave_type, leave_type)
                
                application = LeaveApplication(
                    user_id=user.id,
                    start_date=start_date,
                    end_date=end_date,
                    leave_type=db_type,
                    reason=reason,
                    status='pending',
                    current_approver_level=1,
                    created_at=datetime.utcnow()
                )
                
                db.session.add(application)
                success_count += 1
                
            except Exception as e:
                errors.append(f'第{idx+2}行：{str(e)}')
                error_count += 1
        
        if success_count > 0:
            db.session.commit()
        
        return jsonify({
            'message': f'导入完成，成功{success_count}条，失败{error_count}条',
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors[:50]
        }), 200
        
    except Exception as e:
        logger.error(f"Error importing leave applications: {str(e)}")
        return jsonify({'error': f'导入请假申请失败：{str(e)}'}), 500


@attendance_bp.route('/overtime-applications/export', methods=['GET'])
@jwt_required()
def export_overtime_applications():
    """导出加班申请列表"""
    import pandas as pd
    from io import BytesIO
    from flask import send_file
    from enhanced_app import User, OvertimeApplication
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = OvertimeApplication.query
        
        if current_user.role not in ['admin', 'hr', 'department_manager']:
            query = query.filter(OvertimeApplication.user_id == current_user_id)
        
        if status:
            query = query.filter(OvertimeApplication.status == status)
        
        if start_date:
            query = query.filter(OvertimeApplication.date >= datetime.strptime(start_date, '%Y-%m-%d'))
        
        if end_date:
            query = query.filter(OvertimeApplication.date <= datetime.strptime(end_date, '%Y-%m-%d'))
        
        applications = query.order_by(OvertimeApplication.created_at.desc()).all()
        
        user_cache = {u.id: u for u in User.query.all()}
        
        export_data = []
        for app in applications:
            user = user_cache.get(app.user_id)
            approver = user_cache.get(app.approver_id)
            
            overtime_hours = 0
            if app.start_time and app.end_time:
                try:
                    start = datetime.strptime(app.start_time, '%H:%M')
                    end = datetime.strptime(app.end_time, '%H:%M')
                    overtime_hours = (end - start).seconds / 3600
                except:
                    pass
            
            export_data.append({
                '申请ID': app.id,
                '申请人': f'{user.first_name or ""} {user.last_name or ""}'.strip() if user else '',
                '用户名': user.username if user else '',
                '加班日期': app.date.strftime('%Y-%m-%d') if app.date else '',
                '开始时间': app.start_time or '',
                '结束时间': app.end_time or '',
                '加班时长': overtime_hours,
                '加班事由': app.reason or '',
                '状态': app.status or '',
                '审批人': f'{approver.first_name or ""} {approver.last_name or ""}'.strip() if approver else '',
                '审批时间': app.approved_at.strftime('%Y-%m-%d %H:%M:%S') if app.approved_at else '',
                '拒绝原因': app.rejection_reason or '',
                '创建时间': app.created_at.strftime('%Y-%m-%d %H:%M:%S') if app.created_at else ''
            })
        
        if not export_data:
            return jsonify({'error': '没有可导出的加班申请数据'}), 404
        
        df = pd.DataFrame(export_data)
        output = BytesIO()
        df.to_excel(output, index=False, sheet_name='加班申请')
        output.seek(0)
        
        filename = f'加班申请_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.xlsx'
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Error exporting overtime applications: {str(e)}")
        return jsonify({'error': '导出加班申请失败'}), 500


@attendance_bp.route('/overtime-applications/import', methods=['POST'])
@jwt_required()
def import_overtime_applications():
    """导入加班申请"""
    import pandas as pd
    from io import BytesIO
    from enhanced_app import User, OvertimeApplication
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        if current_user.role not in ['admin', 'hr', 'department_manager']:
            return jsonify({'error': '权限不足，只有管理员可以导入加班申请'}), 403
        
        if 'file' not in request.files:
            return jsonify({'error': '请上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        filename = file.filename.lower()
        if not filename.endswith(('.csv', '.xlsx')):
            return jsonify({'error': '不支持的文件格式，请上传 CSV 或 Excel 文件'}), 400
        
        user_cache = {u.username: u for u in User.query.all()}
        
        success_count = 0
        error_count = 0
        errors = []
        
        if filename.endswith('.csv'):
            content = file.read().decode('utf-8')
            if content.startswith('\ufeff'):
                content = content[1:]
            from io import StringIO
            input_file = StringIO(content)
            df = pd.read_csv(input_file)
        else:
            input_file = BytesIO(file.read())
            df = pd.read_excel(input_file)
        
        required_columns = ['申请人', '加班日期', '开始时间', '结束时间', '加班事由']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({'error': f'文件缺少必要的列：{", ".join(missing_columns)}'}), 400
        
        for idx, row in df.iterrows():
            try:
                username = str(row.get('申请人', '')).strip()
                date_str = str(row.get('加班日期', '')).strip()
                start_time = str(row.get('开始时间', '')).strip()
                end_time = str(row.get('结束时间', '')).strip()
                reason = str(row.get('加班事由', '')).strip()
                
                if not username:
                    errors.append(f'第{idx+2}行：申请人为空')
                    error_count += 1
                    continue
                
                user = user_cache.get(username)
                if not user:
                    errors.append(f'第{idx+2}行：用户"{username}"不存在')
                    error_count += 1
                    continue
                
                if not date_str:
                    errors.append(f'第{idx+2}行：加班日期为空')
                    error_count += 1
                    continue
                
                if not start_time or not end_time:
                    errors.append(f'第{idx+2}行：开始时间或结束时间为空')
                    error_count += 1
                    continue
                
                if not reason:
                    errors.append(f'第{idx+2}行：加班事由为空')
                    error_count += 1
                    continue
                
                try:
                    overtime_date = datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    errors.append(f'第{idx+2}行：日期格式错误，应为YYYY-MM-DD')
                    error_count += 1
                    continue
                
                application = OvertimeApplication(
                    user_id=user.id,
                    date=overtime_date,
                    start_time=start_time,
                    end_time=end_time,
                    reason=reason,
                    status='pending',
                    created_at=datetime.utcnow()
                )
                
                db.session.add(application)
                success_count += 1
                
            except Exception as e:
                errors.append(f'第{idx+2}行：{str(e)}')
                error_count += 1
        
        if success_count > 0:
            db.session.commit()
        
        return jsonify({
            'message': f'导入完成，成功{success_count}条，失败{error_count}条',
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors[:50]
        }), 200
        
    except Exception as e:
        logger.error(f"Error importing overtime applications: {str(e)}")
        return jsonify({'error': f'导入加班申请失败：{str(e)}'}), 500