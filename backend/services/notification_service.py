"""
通知服务模块
提供通知相关的业务逻辑
"""
import logging
import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config.extensions import db
from models import Notification


class NotificationService:
    """通知服务类"""
    
    @staticmethod
    def _load_mail_config():
        """
        加载邮件配置
        
        Returns:
            dict: 邮件配置字典
        """
        config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'mail_config.json')
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"加载邮件配置失败: {e}")
            return {
                'host': os.environ.get('MAIL_HOST', 'smtp.gmail.com'),
                'port': int(os.environ.get('MAIL_PORT', 587)),
                'username': os.environ.get('MAIL_USERNAME', ''),
                'password': os.environ.get('MAIL_PASSWORD', ''),
                'sender': os.environ.get('MAIL_SENDER', 'noreply@example.com')
            }
    
    @staticmethod
    def send_email_notification(to_email, subject, body, html_body=None):
        """
        发送邮件通知
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            body: 邮件正文（纯文本）
            html_body: 邮件正文（HTML格式，可选）
            
        Returns:
            bool: 是否发送成功
        """
        try:
            mail_config = NotificationService._load_mail_config()
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = mail_config['sender']
            msg['To'] = to_email
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            if html_body:
                msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            with smtplib.SMTP(mail_config['host'], mail_config['port']) as server:
                server.starttls()
                server.login(mail_config['username'], mail_config['password'])
                server.send_message(msg)
            
            logging.info(f"邮件已发送至 {to_email}")
            return True
        except Exception as e:
            logging.error(f"发送邮件失败: {e}")
            return False
    
    @staticmethod
    def create_notification(user_id, notification_type, title, content, 
                          related_bug_id=None, related_comment_id=None, related_project_id=None):
        """
        创建应用内通知
        
        Args:
            user_id: 用户ID
            notification_type: 通知类型
            title: 通知标题
            content: 通知内容
            related_bug_id: 关联的Bug ID（可选）
            related_comment_id: 关联的评论ID（可选）
            related_project_id: 关联的项目ID（可选）
            
        Returns:
            Notification: 创建的通知对象，失败返回None
        """
        try:
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                content=content,
                is_read=False,
                related_bug_id=related_bug_id,
                related_comment_id=related_comment_id,
                related_project_id=related_project_id
            )
            db.session.add(notification)
            db.session.commit()
            return notification
        except Exception as e:
            db.session.rollback()
            logging.error(f"创建通知失败: {e}")
            return None
    
    @staticmethod
    def send_bug_assigned_notification(user, bug):
        """
        发送Bug分配通知
        
        Args:
            user: 被分配的用户
            bug: Bug对象
            
        Returns:
            bool: 是否发送成功
        """
        if not user.email_notification_enabled or not user.email_on_bug_assigned:
            return False
        
        subject = f"Bug分配通知: {bug.title}"
        body = f"您好，\n\n您被分配了一个新的Bug:\n\n标题: {bug.title}\n描述: {bug.description}\n\n请尽快处理。"
        
        return NotificationService.send_email_notification(user.email, subject, body)
    
    @staticmethod
    def send_bug_closed_notification(user, bug):
        """
        发送Bug关闭通知
        
        Args:
            user: 报告Bug的用户
            bug: Bug对象
            
        Returns:
            bool: 是否发送成功
        """
        if not user.email_notification_enabled or not user.email_on_bug_closed:
            return False
        
        subject = f"Bug关闭通知: {bug.title}"
        body = f"您好，\n\n您报告的Bug已被关闭:\n\n标题: {bug.title}\n\n感谢您的反馈。"
        
        return NotificationService.send_email_notification(user.email, subject, body)
    
    @staticmethod
    def get_unread_notifications(user_id, limit=None):
        """
        获取用户的未读通知
        
        Args:
            user_id: 用户ID
            limit: 限制数量（可选）
            
        Returns:
            list: 未读通知列表
        """
        query = Notification.query.filter_by(user_id=user_id, is_read=False).order_by(Notification.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def mark_all_as_read(user_id):
        """
        标记用户的所有通知为已读
        
        Args:
            user_id: 用户ID
            
        Returns:
            int: 标记为已读的通知数量
        """
        try:
            count = Notification.query.filter_by(user_id=user_id, is_read=False).update({
                'is_read': True,
                'read_at': datetime.utcnow()
            })
            db.session.commit()
            return count
        except Exception as e:
            db.session.rollback()
            logging.error(f"标记通知为已读失败: {e}")
            return 0
