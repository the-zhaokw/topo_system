from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).resolve().parent.parent))

# 导入必要的模块
from enhanced_app import User, db, create_audit_log

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_category(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext in ALLOWED_EXTENSIONS:
        return 'images'
    return 'other'

def create_audit_log(user_id, action, resource_type, resource_id, details, request=None):
    pass

def get_upload_folder():
    return current_app.config.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads'))

avatar_bp = Blueprint('avatar', __name__, url_prefix='/avatar')

@avatar_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_avatar():
    """
    上传用户头像
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    # 检查是否有文件上传
    if 'avatar' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['avatar']
    
    # 检查文件是否为空
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    # 检查文件类型是否允许
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件类型，请上传图片文件'}), 400
    
    # 检查文件类别
    category = get_file_category(file.filename)
    if category != 'images':
        return jsonify({'error': '请上传有效的图片文件'}), 400
    
    try:
        # 创建头像保存目录
        upload_folder = get_upload_folder()
        avatar_dir = os.path.join(upload_folder, category)
        os.makedirs(avatar_dir, exist_ok=True)
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        # 添加用户ID前缀，确保文件唯一性
        user_filename = f"user_{current_user_id}_{filename}"
        filepath = os.path.join(avatar_dir, user_filename)
        
        # 保存文件
        file.save(filepath)
        
        # 更新用户avatar字段
        # 只存储相对路径，便于后续访问
        avatar_url = f"/uploads/{category}/{user_filename}"
        user.avatar = avatar_url
        db.session.commit()
        
        # 创建log
        create_audit_log(
            user_id=current_user_id,
            action='upload_avatar',
            resource_type='user',
            resource_id=current_user_id,
            details=f'用户 {user.username} 上传了新头像',
            request=request
        )
        
        return jsonify({
            'message': '头像上传成功',
            'avatar_url': avatar_url,
            'user': {
                'id': user.id,
                'username': user.username,
                'avatar': user.avatar
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'头像上传失败: {str(e)}'}), 500

@avatar_bp.route('/remove', methods=['DELETE'])
@jwt_required()
def remove_avatar():
    """
    删除用户头像
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    try:
        # 如果用户有头像，尝试删除文件
        if user.avatar:
            # 从avatar路径中提取文件名
            avatar_path = user.avatar.replace('/uploads/', '')
            upload_folder = get_upload_folder()
            full_path = os.path.join(upload_folder, avatar_path)
            
            # 尝试删除文件（忽略文件不存在的情况）
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                except Exception as e:
                    # 记录错误但不影响操作
                    current_app.logger.error(f"删除头像文件失败: {str(e)}")
            
            # 清除用户avatar字段
            user.avatar = None
            db.session.commit()
            
            # 创建log
            create_audit_log(
                user_id=current_user_id,
                action='remove_avatar',
                resource_type='user',
                resource_id=current_user_id,
                details=f'用户 {user.username} 删除了头像',
                request=request
            )
        
        return jsonify({
            'message': '头像删除成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'avatar': user.avatar
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'头像删除失败: {str(e)}'}), 500