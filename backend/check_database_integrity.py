#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库完整性检查脚本
检查数据库表结构、数据完整性和系统配置
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_app import app, db, User, Project, Bug, Activity, Comment, Attachment, AuditLog, Notification
from datetime import datetime

def check_database_integrity():
    """检查数据库完整性"""
    print("🔍 开始检查数据库完整性...")
    print("=" * 60)
    
    issues = []
    
    try:
        # 在应用程序上下文中运行
        with app.app_context():
            # 检查数据库连接
            print("📊 检查数据库连接...")
            db.session.execute(text("SELECT 1"))
            print("✅ 数据库连接正常")
            
            # 检查表结构
            print("\n📋 检查表结构...")
            tables = ['user', 'project', 'bug', 'activity', 'comment', 'attachment', 'audit_log', 'notification']
            
            for table in tables:
                try:
                    db.session.execute(f"SELECT COUNT(*) FROM {table}")
                    print(f"✅ 表 {table} 存在")
                except Exception as e:
                    issues.append(f"❌ 表 {table} 不存在或无法访问: {e}")
            
            # 检查用户数据
            print("\n👥 检查用户数据...")
            users = User.query.all()
            print(f"✅ 用户数量: {len(users)}")
            
            for user in users:
                if not user.username or not user.email:
                    issues.append(f"❌ 用户 {user.id} 缺少用户名或邮箱")
            
            # 检查项目数据
            print("\n📂 检查项目数据...")
            projects = Project.query.all()
            print(f"✅ 项目数量: {len(projects)}")
            
            for project in projects:
                if not project.name:
                    issues.append(f"❌ 项目 {project.id} 缺少名称")
            
            # 检查Bug数据
            print("\n🐛 检查Bug数据...")
            bugs = Bug.query.all()
            print(f"✅ Bug数量: {len(bugs)}")
            
            for bug in bugs:
                if not bug.title or not bug.description:
                    issues.append(f"❌ Bug {bug.id} 缺少标题或描述")
                
                # 检查关联关系
                if not bug.reporter_id:
                    issues.append(f"❌ Bug {bug.id} 缺少报告人")
                
                if bug.assignee_id and not User.query.get(bug.assignee_id):
                    issues.append(f"❌ Bug {bug.id} 的分配人不存在")
            
            # 检查活动记录
            print("\n📝 检查活动记录...")
            activities = Activity.query.all()
            print(f"✅ 活动记录数量: {len(activities)}")
            
            # 检查评论
            print("\n💬 检查评论数据...")
            comments = Comment.query.all()
            print(f"✅ 评论数量: {len(comments)}")
            
            # 检查附件
            print("\n📎 检查附件数据...")
            attachments = Attachment.query.all()
            print(f"✅ 附件数量: {len(attachments)}")
            
            # 检查审计日志
            print("\n📋 检查审计日志...")
            audit_logs = AuditLog.query.all()
            print(f"✅ 审计日志数量: {len(audit_logs)}")
            
            # 检查通知
            print("\n🔔 检查通知数据...")
            notifications = Notification.query.all()
            print(f"✅ 通知数量: {len(notifications)}")
            
            # 统计信息
            print("\n📈 数据库统计信息:")
            print(f"   用户总数: {len(users)}")
            print(f"   项目总数: {len(projects)}")
            print(f"   Bug总数: {len(bugs)}")
            print(f"   活动记录: {len(activities)}")
            print(f"   评论数量: {len(comments)}")
            print(f"   附件数量: {len(attachments)}")
            print(f"   审计日志: {len(audit_logs)}")
            print(f"   通知数量: {len(notifications)}")
            
            # 检查最近的活动
            recent_activities = Activity.query.order_by(Activity.created_at.desc()).limit(5).all()
            print("\n🕒 最近的活动记录:")
            for activity in recent_activities:
                print(f"   {activity.created_at}: {activity.user.username} - {activity.action}")
    
    except Exception as e:
        issues.append(f"❌ 数据库检查过程中出现异常: {e}")
    
    # 输出检查结果
    print("\n" + "=" * 60)
    print("📋 完整性检查结果:")
    
    if issues:
        print("❌ 发现以下问题:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("✅ 数据库完整性检查通过，未发现问题")
    
    return len(issues) == 0

def check_system_config():
    """检查系统配置"""
    print("\n🔧 检查系统配置...")
    print("=" * 60)
    
    config_issues = []
    
    # 检查必要的环境变量
    required_env_vars = ['JWT_SECRET_KEY']
    
    for env_var in required_env_vars:
        if not os.environ.get(env_var):
            config_issues.append(f"❌ 环境变量 {env_var} 未设置")
        else:
            print(f"✅ {env_var}: 已设置")
    
    # 检查上传目录
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    if os.path.exists(upload_dir):
        print(f"✅ 上传目录存在: {upload_dir}")
    else:
        config_issues.append(f"❌ 上传目录不存在: {upload_dir}")
    
    # 检查数据库文件
    db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'topo_system.db')
    if os.path.exists(db_file):
        file_size = os.path.getsize(db_file)
        print(f"✅ 数据库文件存在: {db_file} ({file_size} bytes)")
    else:
        config_issues.append(f"❌ 数据库文件不存在: {db_file}")
    
    if config_issues:
        print("\n❌ 配置检查发现问题:")
        for issue in config_issues:
            print(f"   {issue}")
    else:
        print("✅ 系统配置检查通过")
    
    return len(config_issues) == 0

def create_backup_script():
    """创建数据库备份脚本"""
    print("\n💾 创建数据库备份脚本...")
    
    backup_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"数据库备份脚本\"\"\"

import os
import shutil
from datetime import datetime

def backup_database():
    \"\"\"备份数据库\"\"\"
    source_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'topo_system.db')
    backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
    
    # 创建备份目录
    os.makedirs(backup_dir, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")
    backup_file = os.path.join(backup_dir, f'topo_system_backup_{timestamp}.db')
    
    try:
        # 复制数据库文件
        shutil.copy2(source_db, backup_file)
        print(f\"✅ 数据库备份成功: {backup_file}\")
        return True
    except Exception as e:
        print(f\"❌ 数据库备份失败: {e}\")
        return False

if __name__ == \"__main__\":
    backup_database()
"""
    
    backup_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backup_database.py')
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(backup_script)
    
    print(f"✅ 备份脚本已创建: {backup_file}")

if __name__ == "__main__":
    print("🚀 开始数据库完整性检查")
    print("=" * 60)
    
    # 检查数据库完整性
    db_ok = check_database_integrity()
    
    # 检查系统配置
    config_ok = check_system_config()
    
    # 创建备份脚本
    create_backup_script()
    
    print("\n" + "=" * 60)
    print("📊 检查总结:")
    
    if db_ok and config_ok:
        print("✅ 所有检查通过，系统状态良好")
    else:
        print("⚠️  发现一些问题，建议进行修复")
    
    print("\n💡 建议:")
    print("   1. 定期运行此脚本检查数据库状态")
    print("   2. 使用 backup_database.py 进行定期备份")
    print("   3. 监控系统日志和错误信息")
    print("=" * 60)