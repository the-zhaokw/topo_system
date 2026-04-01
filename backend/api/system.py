# 系统管理API - F-008

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import os
import shutil
import json
from flask_jwt_extended import jwt_required, get_jwt_identity

# 系统管理蓝图
system_bp = Blueprint('system', __name__, url_prefix='/system')

@system_bp.route('/time', methods=['GET'])
def get_system_time():
    """获取系统当前时间"""
    return jsonify({
        'server_time': datetime.now().isoformat(),
        'timestamp': int(datetime.now().timestamp() * 1000),
        'timezone': 'Asia/Shanghai'
    }), 200

def get_db():
    from enhanced_app import db
    return db

def get_models():
    from enhanced_app import db, User
    return User

# 数据库备份 API (F-008-02)
@system_bp.route('/backup', methods=['POST'])
@jwt_required()
def create_backup():
    """创建数据库备份"""
    from enhanced_app import app
    
    try:
        current_user_id = get_jwt_identity()
        User = get_models()
        current_user = User.query.get(int(current_user_id))
        
        # 检查权限
        if current_user.role != 'admin':
            return jsonify({'error': '无权限执行此操作'}), 403
        
        with app.app_context():
            # 获取数据库路径
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            
            # 确定源数据库文件
            if 'sqlite:///' in db_uri:
                db_path = db_uri.replace('sqlite:///', '')
            else:
                return jsonify({'error': '仅支持SQLite数据库备份'}), 400
            
            if not os.path.exists(db_path):
                return jsonify({'error': '数据库文件不存在'}), 404
            
            # 创建备份目录
            backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成备份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'topo_system_backup_{timestamp}.db'
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # 复制数据库文件
            shutil.copy2(db_path, backup_path)
            
            return jsonify({
                'message': '数据库备份成功',
                'backup_file': backup_filename,
                'backup_path': backup_path,
                'created_at': datetime.now().isoformat()
            }), 201
            
    except Exception as e:
        return jsonify({'error': f'备份失败: {str(e)}'}), 500


@system_bp.route('/backups', methods=['GET'])
@jwt_required()
def list_backups():
    """获取备份列表"""
    from enhanced_app import app
    
    try:
        current_user_id = get_jwt_identity()
        User = get_models()
        current_user = User.query.get(int(current_user_id))
        
        if current_user.role != 'admin':
            return jsonify({'error': '无权限执行此操作'}), 403
        
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
        
        if not os.path.exists(backup_dir):
            return jsonify({'backups': []}), 200
        
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.endswith('.db'):
                filepath = os.path.join(backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # 按时间倒序
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({'backups': backups}), 200
        
    except Exception as e:
        return jsonify({'error': f'获取备份列表失败: {str(e)}'}), 500


@system_bp.route('/backups/<filename>', methods=['GET'])
@jwt_required()
def download_backup(filename):
    """下载备份文件"""
    from enhanced_app import app
    
    try:
        current_user_id = get_jwt_identity()
        User = get_models()
        current_user = User.query.get(int(current_user_id))
        
        if current_user.role != 'admin':
            return jsonify({'error': '无权限执行此操作'}), 403
        
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
        filepath = os.path.join(backup_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': '备份文件不存在'}), 404
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500


@system_bp.route('/backups/<filename>', methods=['DELETE'])
@jwt_required()
def delete_backup(filename):
    """删除备份文件"""
    from enhanced_app import app
    
    try:
        current_user_id = get_jwt_identity()
        User = get_models()
        current_user = User.query.get(int(current_user_id))
        
        if current_user.role != 'admin':
            return jsonify({'error': '无权限执行此操作'}), 403
        
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
        filepath = os.path.join(backup_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': '备份文件不存在'}), 404
        
        os.remove(filepath)
        
        return jsonify({'message': '备份删除成功'}), 200
        
    except Exception as e:
        return jsonify({'error': f'删除失败: {str(e)}'}), 500


# 系统配置 API (F-008-04)
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'system_config.json')

def load_config():
    """加载系统配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return get_default_config()

def save_config(config):
    """保存系统配置"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def get_default_config():
    """获取默认配置"""
    return {
        'mail_server': {
            'enabled': False,
            'host': 'smtp.vip.163.com',
            'port': 465,
            'use_tls': False,
            'use_ssl': True,
            'username': '',
            'password': '',
            'from_address': '',
            'from_name': 'TOPO系统',
            'max_daily_limit': 80,
            'max_hourly_limit': 30,
            'max_per_minute': 5
        },
        'upload': {
            'max_file_size': 16,  # MB
            'allowed_extensions': ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx']
        },
        'backup': {
            'auto_backup': False,
            'backup_time': '02:00',
            'retention_days': 7
        }
    }

@system_bp.route('/config', methods=['GET'])
@jwt_required()
def get_config():
    """获取系统配置"""
    try:
        current_user_id = get_jwt_identity()
        User = get_models()
        current_user = User.query.get(int(current_user_id))
        
        if current_user.role != 'admin':
            return jsonify({'error': '无权限执行此操作'}), 403
        
        config = load_config()
        # 隐藏敏感信息
        if 'mail_server' in config and config['mail_server'].get('password'):
            config['mail_server']['password'] = '********'
        
        return jsonify(config), 200
        
    except Exception as e:
        return jsonify({'error': f'获取配置失败: {str(e)}'}), 500


@system_bp.route('/config', methods=['PUT'])
@jwt_required()
def update_config():
    """更新系统配置"""
    try:
        current_user_id = get_jwt_identity()
        User = get_models()
        current_user = User.query.get(int(current_user_id))
        
        if current_user.role != 'admin':
            return jsonify({'error': '无权限执行此操作'}), 403
        
        data = request.get_json()
        
        # 验证配置
        config = load_config()
        
        # 更新邮件配置
        if 'mail_server' in data:
            for key in ['enabled', 'host', 'port', 'use_tls', 'use_ssl', 'username', 'from_address', 'from_name', 
                       'max_daily_limit', 'max_hourly_limit', 'max_per_minute']:
                if key in data['mail_server']:
                    config['mail_server'][key] = data['mail_server'][key]
            # 只有当提供新密码时才更新
            if data['mail_server'].get('password') and data['mail_server']['password'] != '********':
                config['mail_server']['password'] = data['mail_server']['password']
        
        # 更新上传配置
        if 'upload' in data:
            for key in ['max_file_size', 'allowed_extensions']:
                if key in data['upload']:
                    config['upload'][key] = data['upload'][key]
        
        # 更新备份配置
        if 'backup' in data:
            for key in ['auto_backup', 'backup_time', 'retention_days']:
                if key in data['backup']:
                    config['backup'][key] = data['backup'][key]
        
        save_config(config)
        
        return jsonify({'message': '配置更新成功'}), 200
        
    except Exception as e:
        return jsonify({'error': f'更新配置失败: {str(e)}'}), 500


# 数据库完整性检查 API (F-008-03)
@system_bp.route('/integrity-check', methods=['POST'])
@jwt_required()
def integrity_check():
    """数据库完整性检查"""
    from enhanced_app import app
    
    try:
        current_user_id = get_jwt_identity()
        User = get_models()
        current_user = User.query.get(int(current_user_id))
        
        if current_user.role != 'admin':
            return jsonify({'error': '无权限执行此操作'}), 403
        
        with app.app_context():
            db = get_db()
            
            results = {
                'tables': [],
                'issues': []
            }
            
            result = db.session.execute(db.text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            
            for table in tables:
                try:
                    count_result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.scalar()
                    
                    results['tables'].append({
                        'name': table,
                        'status': 'ok',
                        'record_count': count
                    })
                except Exception as e:
                    results['issues'].append({
                        'table': table,
                        'issue': str(e)
                    })
            
            results['status'] = 'ok' if not results['issues'] else 'error'
            
            return jsonify(results), 200
            
    except Exception as e:
        return jsonify({'error': f'检查失败: {str(e)}'}), 500


@system_bp.route('/test-email', methods=['POST'])
@jwt_required()
def test_email():
    """测试邮件发送"""
    try:
        current_user_id = get_jwt_identity()
        User = get_models()
        current_user = User.query.get(int(current_user_id))
        
        if current_user.role != 'admin':
            return jsonify({'error': '无权限执行此操作'}), 403
        
        data = request.get_json()
        test_email_addr = data.get('email')
        
        if not test_email_addr:
            return jsonify({'error': '请提供测试邮箱地址'}), 400
        
        config = load_config()
        mail_config = config.get('mail_server', {})
        
        if not mail_config.get('enabled'):
            return jsonify({'error': '邮件服务未启用'}), 400
        
        if not mail_config.get('host') or not mail_config.get('username'):
            return jsonify({'error': '邮件配置不完整'}), 400
        
        from services.email_service import EmailService
        email_service = EmailService(config)
        result = email_service.send_test_email(test_email_addr)
        
        if result.get('success'):
            return jsonify({
                'message': f'测试邮件已发送到 {test_email_addr}',
                'success': True
            }), 200
        else:
            return jsonify({'error': result.get('error', '发送失败')}), 500
        
    except Exception as e:
        return jsonify({'error': f'发送测试邮件失败: {str(e)}'}), 500
