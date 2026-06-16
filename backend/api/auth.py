from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import re
import logging
import traceback

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# 全局错误处理
@auth_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Auth 500 error: {error}")
    return jsonify({
        'success': False,
        'error': '服务器内部错误',
        'code': 'INTERNAL_ERROR'
    }), 500

@auth_bp.errorhandler(Exception)
def handle_exception(error):
    logger.error(f"Auth unhandled exception: {error}\n{traceback.format_exc()}")
    return jsonify({
        'success': False,
        'error': f'请求处理失败: {str(error)}',
        'code': 'UNHANDLED_ERROR'
    }), 500

# 延迟导入数据库和模型，避免循环导入
def get_db():
    """延迟获取数据库实例，避免循环导入"""
    from enhanced_app import db
    return db

def get_models():
    """延迟获取数据库模型"""
    from enhanced_app import User, UserRole
    return User, UserRole

def get_create_audit_log():
    """延迟获取log函数"""
    from enhanced_app import create_audit_log
    return create_audit_log

# 用户注册
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 验证输入
    if not data:
        return jsonify({
            'success': False,
            'error': '请求数据不能为空',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({
                'success': False,
                'error': f'{field} 字段为必填项',
                'code': 'VALIDATION_ERROR'
            }), 400
    
    # 验证邮箱格式
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_pattern, data['email']):
        return jsonify({
            'success': False,
            'error': '邮箱格式不正确',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    # 验证用户名
    username = data['username']
    if len(username) < 3 or len(username) > 20:
        return jsonify({
            'success': False,
            'error': '用户名长度应在3-20个字符之间',
            'code': 'VALIDATION_ERROR'
        }), 400
    # 验证用户名只包含允许的字符（字母、数字、下划线）
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return jsonify({
            'success': False,
            'error': '用户名只能包含字母、数字和下划线',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    # 验证密码强度
    password = data['password']
    if len(password) < 8:
        return jsonify({
            'success': False,
            'error': '密码长度至少为8个字符',
            'code': 'VALIDATION_ERROR'
        }), 400
    if not re.search(r'[a-zA-Z]', password):
        return jsonify({
            'success': False,
            'error': '密码必须包含至少一个字母',
            'code': 'VALIDATION_ERROR'
        }), 400
    if not re.search(r'\d', password):
        return jsonify({
            'success': False,
            'error': '密码必须包含至少一个数字',
            'code': 'VALIDATION_ERROR'
        }), 400
    if not re.match(r'^[a-zA-Z0-9]+$', password):
        return jsonify({
            'success': False,
            'error': '密码只能包含字母和数字',
            'code': 'VALIDATION_ERROR'
        }), 400
    
    # 延迟导入数据库模型和函数
    db = get_db()
    User, UserRole = get_models()
    create_audit_log = get_create_audit_log()
    
    # 在应用上下文中执行数据库操作
    from enhanced_app import app
    with app.app_context():
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'error': '用户名已存在',
                'code': 'USERNAME_EXISTS'
            }), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'error': '邮箱已被注册',
                'code': 'EMAIL_EXISTS'
            }), 400
        
        # 创建新用户
        try:
            # 直接在应用上下文中创建用户对象
            new_user = User()
            new_user.username = data['username']
            new_user.email = data['email']
            
            # 使用客户端传来的salt值
            salt = data.get('salt')
            if not salt:
                # 如果客户端没有提供salt，则生成一个新的
                import secrets
                salt = secrets.token_hex(16)
            new_user.salt = salt
            
            # 使用User模型的set_password方法设置密码
            new_user.set_password(data['password'])
            
            # 处理角色分配，确保安全性
            # 对于普通注册，无论请求中提供什么角色，都使用默认角色USER
            # 只有管理员用户才能创建其他管理员用户，这需要单独的API
            new_user.role = UserRole.USER.value
            
            new_user.department = data.get('department', '')
            new_user.position = data.get('position', '')
            new_user.phone = data.get('phone', '')
            
            db.session.add(new_user)
            db.session.flush()  # 获取新用户的ID但不提交事务
            
            # 创建log
            create_audit_log(
                user_id=new_user.id,
                action='user_register',
                resource_type='user',
                resource_id=new_user.id,
                details=f'用户注册: {new_user.username}',
                request=request
            )
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '注册成功',
                'data': {
                    'user': {
                        'id': new_user.id,
                        'username': new_user.username,
                        'email': new_user.email,
                        'role': new_user.role.value if hasattr(new_user.role, 'value') else str(new_user.role)
                    }
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f'注册失败: {str(e)}',
                'code': 'REGISTRATION_ERROR'
            }), 500

# 用户登录
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json(silent=True)

        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': '用户名和密码为必填项',
                'code': 'VALIDATION_ERROR'
            }), 400

        username = data.get('username', '').strip() if isinstance(data.get('username'), str) else data.get('username')
        password = data.get('password', '')

        if not username or not password:
            return jsonify({
                'success': False,
                'error': '用户名和密码为必填项',
                'code': 'VALIDATION_ERROR'
            }), 400

        # 延迟导入数据库模型和函数
        from enhanced_app import app
        db = get_db()
        User, UserRole = get_models()
        create_audit_log = get_create_audit_log()

        with app.app_context():
            session = db.session
            # 查找用户
            user = session.query(User).filter_by(username=username).first()

            if not user:
                return jsonify({
                    'success': False,
                    'error': '用户名或密码错误',
                    'code': 'AUTHENTICATION_ERROR'
                }), 401

            # 验证密码
            if not user.check_password(password):
                return jsonify({
                    'success': False,
                    'error': '用户名或密码错误',
                    'code': 'AUTHENTICATION_ERROR'
                }), 401

            # 更新用户的last_login时间和状态为在线
            try:
                user.last_login = datetime.utcnow()
                user.status = 'online'
                user.last_activity = datetime.utcnow()
            except Exception as field_err:
                logger.warning(f"更新用户状态字段失败（忽略继续）: {field_err}")

            # 创建访问令牌
            access_token = create_access_token(identity=user.id)

            # 创建log
            try:
                create_audit_log(
                    user_id=user.id,
                    action='user_login',
                    resource_type='user',
                    resource_id=user.id,
                    details=f'用户登录: {user.username}',
                    request=request
                )
            except Exception as log_err:
                logger.warning(f"创建审计日志失败（忽略继续）: {log_err}")

            # 提交所有更改
            try:
                db.session.commit()
            except Exception as commit_err:
                logger.error(f"提交登录事务失败: {commit_err}")
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'error': '登录状态保存失败，请重试',
                    'code': 'COMMIT_ERROR'
                }), 500

            # 获取职位信息
            try:
                position_info = user.get_position_info()
                is_admin = user.is_super_admin or (position_info and (position_info.is_admin or position_info.is_manager))
            except Exception as pos_err:
                logger.warning(f"获取职位信息失败: {pos_err}")
                position_info = None
                is_admin = user.is_super_admin

            # 返回用户信息和令牌
            return jsonify({
                'success': True,
                'message': '登录成功',
                'data': {
                    'access_token': access_token,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': user.role.value if hasattr(user.role, 'value') else str(user.role),
                        'department': user.department,
                        'position': user.position,
                        'is_super_admin': user.is_super_admin,
                        'is_admin': is_admin,
                        'phone': user.phone,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'employee_id': user.employee_id,
                        'company_phone': user.company_phone,
                        'mobile_phone': user.mobile_phone,
                        'birthday': user.birthday.isoformat() if user.birthday else None,
                        'gender': user.gender,
                        'work_language': user.work_language,
                        'avatar': user.avatar,
                        'status': user.status or 'online',
                        'created_at': user.created_at.isoformat() if user.created_at else None,
                        'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                        'last_login': user.last_login.isoformat() if user.last_login else None,
                        'accessible_modules': user.get_accessible_modules()
                    }
                }
            }), 200
    except Exception as e:
        logger.error(f"登录异常: {e}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'登录失败: {str(e)}',
            'code': 'INTERNAL_ERROR'
        }), 500

# 获取当前用户信息
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    # 延迟导入数据库模型
    User, UserRole = get_models()
    
    current_user_id = get_jwt_identity()
    
    # 在应用上下文中查找用户
    from enhanced_app import app
    with app.app_context():
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': '用户不存在',
                'code': 'USER_NOT_FOUND'
            }), 404
        
        # 获取职位信息
        position_info = user.get_position_info()
        is_admin = user.is_super_admin or (position_info and (position_info.is_admin or position_info.is_manager))

        return jsonify({
            'success': True,
            'message': '获取用户信息成功',
            'data': {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,  # 现在role是字符串，直接返回
                    'department': user.department,
                    'position': user.position,
                    'is_super_admin': user.is_super_admin,
                    'is_admin': is_admin,
                    'phone': user.phone,  # 保留原字段，用于向后兼容
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'employee_id': user.employee_id,
                    'company_phone': user.company_phone,
                    'mobile_phone': user.mobile_phone,
                    'birthday': user.birthday.isoformat() if user.birthday else None,
                    'gender': user.gender,
                    'work_language': user.work_language,
                    'avatar': user.avatar,
                    'status': user.status or 'online',
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'accessible_modules': user.get_accessible_modules()
                }
            }
        }), 200

# 更新个人资料
@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    import logging
    logger = logging.getLogger(__name__)
    logger.info("=== update_profile 函数开始执行 ===")
    
    try:
        current_user_id = get_jwt_identity()
        logger.info(f"当前用户ID: {current_user_id}")
    except Exception as e:
        logger.error(f"获取JWT identity失败: {str(e)}")
        return jsonify({'error': f'认证失败: {str(e)}'}), 401
    
    try:
        data = request.get_json()
        logger.info(f"update_profile接收到的数据: {data}")
        logger.info(f"Content-Type: {request.content_type}")
    except Exception as e:
        logger.error(f"解析JSON数据失败: {str(e)}")
        return jsonify({'error': '请求数据格式错误'}), 400

    if not data:
        logger.error("接收到的数据为空")
        return jsonify({'error': '请求数据不能为空'}), 400
    
    # 记录所有接收到的数据
    logger.info(f"update_profile接收到的完整数据: {data}")
    logger.info(f"数据类型: {type(data)}")
    for key, value in data.items():
        logger.info(f"  字段: {key}, 值: {value}, 类型: {type(value)}")
    
    # 在应用上下文中执行数据库操作
    from enhanced_app import app
    with app.app_context():
        try:
            db = get_db()
            User, UserRole = get_models()
            create_audit_log = get_create_audit_log()
        except Exception as e:
            logger.error(f"获取数据库连接失败: {str(e)}")
            return jsonify({'error': '服务器配置错误'}), 500
        
        try:
            user = User.query.get(current_user_id)
            if not user:
                return jsonify({'error': '用户不存在'}), 404
        except Exception as e:
            logger.error(f"查询用户失败: {str(e)}")
            return jsonify({'error': '数据库查询失败'}), 500
        
        # 更新用户信息
        if 'email' in data and data['email'] and data['email'] != '':
            # 验证邮箱格式
            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_pattern, data['email']):
                logger.error(f"邮箱格式验证失败: {data['email']}")
                return jsonify({'error': '邮箱格式不正确'}), 400
        
            # 检查邮箱是否已被其他用户使用
            try:
                existing_user = User.query.filter_by(email=data['email']).first()
                if existing_user and existing_user.id != current_user_id:
                    logger.error(f"邮箱已被其他用户使用: {data['email']}")
                    return jsonify({'error': '邮箱已被其他用户使用'}), 400
            except Exception as e:
                logger.error(f"查询邮箱失败: {str(e)}")
                return jsonify({'error': '数据库查询失败'}), 500
            
            user.email = data['email']
        
        # 更新其他非敏感信息
        updatable_fields = [
            'department', 'position', 'phone',  # 保留原字段，用于向后兼容
            'first_name', 'last_name', 'employee_id', 
            'company_phone', 'mobile_phone', 'birthday', 
            'gender', 'work_language', 'avatar'
        ]

        for field in updatable_fields:
            if field in data:
                logger.info(f"处理字段: {field}, 值: {data[field]}, 类型: {type(data[field])}")
                # 处理日期字段特殊情况
                if field == 'birthday':
                    if data[field] is None or data[field] == '' or data[field] == 'null':
                        user.birthday = None
                        logger.info(f"将birthday设置为None")
                    else:
                        from datetime import datetime
                        try:
                            if isinstance(data[field], str):
                                # 支持多种日期格式
                                if 'T' in data[field]:
                                    # ISO format with time
                                    user.birthday = datetime.fromisoformat(data[field].split('T')[0])
                                elif '/' in data[field]:
                                    # YYYY/MM/DD format
                                    user.birthday = datetime.strptime(data[field], '%Y/%m/%d')
                                else:
                                    # YYYY-MM-DD format
                                    user.birthday = datetime.strptime(data[field], '%Y-%m-%d')
                            else:
                                user.birthday = data[field]
                            logger.info(f"成功解析 birthday: {user.birthday}")
                        except ValueError as e:
                            logger.error(f"生日格式解析失败：{data[field]}, 错误：{str(e)}")
                            return jsonify({'error': '生日格式不正确，应为 YYYY-MM-DD 或 YYYY/MM/DD'}), 400
                        except Exception as e:
                            logger.error(f"生日解析异常：{str(e)}")
                            return jsonify({'error': f'生日格式不正确：{str(e)}'}), 400
                elif data[field] is not None and data[field] != '':
                    try:
                        setattr(user, field, data[field])
                        logger.info(f"成功设置字段 {field} = {data[field]}")
                    except Exception as e:
                        logger.error(f"设置字段 {field} 失败: {str(e)}, 类型: {type(data[field])}")
                        return jsonify({'error': f'更新字段 {field} 失败: {str(e)}'}), 500
                else:
                    # 设置为空值
                    try:
                        setattr(user, field, None)
                        logger.info(f"成功设置字段 {field} = None")
                    except Exception as e:
                        logger.error(f"设置字段 {field} 为None失败: {str(e)}")
        
        try:
            logger.info("准备提交数据库更改...")
            db.session.commit()
            logger.info("数据库提交成功")
            
            logger.info("准备返回成功响应")
            return jsonify({
            'message': '个人资料更新成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,  # 现在role是字符串，直接返回
                'department': user.department,
                'position': user.position,
                'phone': user.phone,  # 保留原字段，用于向后兼容
                'first_name': user.first_name,
                'last_name': user.last_name,
                'employee_id': user.employee_id,
                'company_phone': user.company_phone,
                'mobile_phone': user.mobile_phone,
                'birthday': user.birthday.isoformat() if user.birthday else None,
                'gender': user.gender,
                'work_language': user.work_language,
                'avatar': user.avatar,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        }), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新个人资料时发生异常: {str(e)}", exc_info=True)
            return jsonify({'error': f'更新失败: {str(e)}'}), 500