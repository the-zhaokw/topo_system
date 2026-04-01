import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api', 'system_config.json')

logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Any]:
    """加载系统配置"""
    import json
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


class EmailService:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config:
            self.config = config
        else:
            self.config = load_config().get('mail_server', {})

        if 'mail_server' in self.config:
            self.config = self.config['mail_server']

        self.enabled = self.config.get('enabled', True)
        self.host = self.config.get('host', 'smtp.163.com')
        self.port = self.config.get('port', 465)
        self.username = self.config.get('username', '')
        self.password = self.config.get('password', '')
        self.from_address = self.config.get('from_address', '')
        self.from_name = self.config.get('from_name', 'TOPO系统')
        self.use_ssl = self.config.get('use_ssl', True)
        self.max_daily_limit = self.config.get('max_daily_limit', 80)
        self.max_hourly_limit = self.config.get('max_hourly_limit', 30)
        self.max_per_minute = self.config.get('max_per_minute', 5)

    def is_configured(self) -> bool:
        """检查邮件配置是否完整"""
        return bool(
            self.enabled and 
            self.host and 
            self.username and 
            self.from_address
        )

    def send_email(
        self, 
        to_address: str, 
        subject: str, 
        body: str, 
        html_body: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送邮件"""
        if not self.is_configured():
            return {
                'success': False,
                'error': '邮件服务未配置或未启用'
            }
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{from_name or self.from_name} <{self.from_address}>"
            msg['To'] = to_address

            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)

            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)

            if self.use_ssl:
                with smtplib.SMTP_SSL(self.host, self.port) as server:
                    server.login(self.username, self.password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(self.host, self.port) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    server.send_message(msg)

            logger.info(f"邮件发送成功: {to_address}, 主题: {subject}")
            return {
                'success': True,
                'message': f'邮件已发送到 {to_address}'
            }

        except smtplib.SMTPException as e:
            logger.error(f"SMTP错误: {str(e)}")
            return {
                'success': False,
                'error': f'SMTP错误: {str(e)}'
            }
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def send_test_email(self, to_address: str) -> Dict[str, Any]:
        """发送测试邮件"""
        subject = 'TOPO系统 - 邮件配置测试'
        body = '''这是一封来自TOPO系统的测试邮件。

如果您收到这封邮件，说明邮件配置正确。

---
TOPO系统邮件服务
'''
        html_body = f'''
<html>
<body style="font-family: Arial, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #409EFF;">TOPO系统邮件配置测试</h2>
        <p>这是一封来自TOPO系统的测试邮件。</p>
        <p style="color: #67C23A;"><strong>如果您收到这封邮件，说明邮件配置正确。</strong></p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="color: #909399; font-size: 12px;">
            邮件服务器: {self.host}:{self.port}<br>
            发件人: {self.from_name} &lt;{self.from_address}&gt;<br>
            发送时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
    </div>
</body>
</html>
'''
        return self.send_email(to_address, subject, body, html_body)

    def send_bug_assigned_email(self, to_address: str, bug_title: str, assignee_name: str) -> Dict[str, Any]:
        """发送Bug分配通知邮件"""
        subject = f'[Bug分配] {bug_title}'
        body = f'''您有一个新的Bug被分配给您:

Bug标题: {bug_title}
分配人: {assignee_name}
分配时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

请及时登录TOPO系统查看并处理。

---
TOPO系统
'''
        html_body = f'''
<html>
<body style="font-family: Arial, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #E6A23C;">新的Bug分配</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Bug标题</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{bug_title}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>分配人</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{assignee_name}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>分配时间</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
            </tr>
        </table>
        <p style="margin-top: 20px;">
            <a href="#" style="background: #409EFF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">查看Bug详情</a>
        </p>
    </div>
</body>
</html>
'''
        return self.send_email(to_address, subject, body, html_body, from_name='TOPO系统-Bug通知')

    def send_task_notification_email(self, to_address: str, task_title: str, action: str, operator_name: str) -> Dict[str, Any]:
        """发送任务通知邮件"""
        subject = f'[任务{action}] {task_title}'
        body = f'''您有一个任务更新:

任务标题: {task_title}
操作: {action}
操作人: {operator_name}
操作时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

请及时登录TOPO系统查看。

---
TOPO系统
'''
        html_body = f'''
<html>
<body style="font-family: Arial, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #409EFF;">任务{action}</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>任务标题</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{task_title}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>操作</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{action}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>操作人</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{operator_name}</td>
            </tr>
        </table>
    </div>
</body>
</html>
'''
        return self.send_email(to_address, subject, body, html_body, from_name='TOPO系统-任务通知')

    def send_review_notification_email(
        self,
        to_address: str,
        doc_name: str,
        initiator_name: str,
        deadline: Optional[str] = None,
        review_type: str = '文档评审',
        review_link: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送评审通知邮件"""
        subject = f'[评审通知] {doc_name}'

        deadline_info = f'\n评审截止: {deadline}' if deadline else ''

        app_url = os.environ.get('APP_URL', 'http://localhost:3000')
        full_link = f'{app_url}{review_link}' if review_link else app_url

        body = f'''您好！

您有一个新的{review_type}需要处理：

文档名称: {doc_name}
发起人: {initiator_name}{deadline_info}

评审链接: {full_link}

请及时登录TOPO系统查看并进行评审。

---
TOPO系统
'''

        deadline_html = f'''
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>评审截止</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; color: #E6A23C;">{deadline}</td>
            </tr>
        ''' if deadline else ''

        html_body = f'''
<html>
<body style="font-family: Arial, sans-serif; background-color: #f5f7fa;">
    <div style="max-width: 600px; margin: 20px auto; padding: 20px; background-color: white; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #409EFF; margin: 0;">📋 评审通知</h2>
        </div>

        <p style="color: #606266; font-size: 14px;">您好！您有一个新的<strong>{review_type}</strong>需要处理：</p>

        <table style="width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #f5f7fa; border-radius: 4px;">
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e4e7ed; width: 100px;"><strong>文档名称</strong></td>
                <td style="padding: 12px; border-bottom: 1px solid #e4e7ed; color: #303133; font-weight: 500;">{doc_name}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e4e7ed;"><strong>发起人</strong></td>
                <td style="padding: 12px; border-bottom: 1px solid #e4e7ed; color: #606266;">{initiator_name}</td>
            </tr>
            {deadline_html}
        </table>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{full_link}" style="display: inline-block; background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%); color: white; padding: 12px 32px; text-decoration: none; border-radius: 4px; font-weight: 500; box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);">立即评审</a>
        </div>

        <p style="color: #909399; font-size: 12px; text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e4e7ed;">
            请及时登录TOPO系统查看并进行评审
        </p>

        <div style="text-align: center; margin-top: 20px; color: #C0C4CC; font-size: 12px;">
            <p>TOPO系统 · {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
    </div>
</body>
</html>
'''
        return self.send_email(to_address, subject, body, html_body, from_name='TOPO系统-评审通知')


email_service = EmailService()
