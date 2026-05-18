"""
审批服务模块
提供审批相关的业务逻辑
"""
import logging
from datetime import datetime
from config.extensions import db
from models import User, Position, LeaveApplication
from models.enums import ApprovalStatus
from services.notification_service import NotificationService


class ApprovalService:
    """审批服务类"""
    
    @staticmethod
    def get_department_manager(department_name):
        """
        获取部门经理
        
        Args:
            department_name: 部门名称
            
        Returns:
            User: 部门经理用户对象，未找到返回None
        """
        try:
            position = Position.query.filter(
                Position.name.ilike('%经理%'),
                Position.name.ilike(f'%{department_name}%')
            ).first()
            
            if position:
                return User.query.filter_by(position=position.name).first()
            return None
        except Exception as e:
            logging.error(f"获取部门经理失败: {e}")
            return None
    
    @staticmethod
    def get_hr_manager():
        """
        获取人事经理
        
        Returns:
            User: 人事经理用户对象，未找到返回None
        """
        try:
            position = Position.query.filter(
                Position.name.ilike('%人事经理%')
            ).first()
            
            if position:
                return User.query.filter_by(position=position.name).first()
            return None
        except Exception as e:
            logging.error(f"获取人事经理失败: {e}")
            return None
    
    @staticmethod
    def build_approval_chain(user_id, leave_type, start_date, end_date):
        """
        构建审批链
        
        Args:
            user_id: 申请人ID
            leave_type: 请假类型
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            list: 审批人ID列表
        """
        try:
            applicant = User.query.get(user_id)
            if not applicant:
                return None
            
            chain = []
            days = (end_date - start_date).days
            
            # 根据请假类型和天数确定审批链
            if leave_type in ['sick_leave', 'personal_leave']:
                if days <= 1:
                    # 1天以内，直属上级审批
                    manager = ApprovalService.get_department_manager(applicant.department)
                    if manager:
                        chain.append(manager.id)
                else:
                    # 1天以上，需要部门经理和人事审批
                    manager = ApprovalService.get_department_manager(applicant.department)
                    if manager:
                        chain.append(manager.id)
                    hr_manager = ApprovalService.get_hr_manager()
                    if hr_manager:
                        chain.append(hr_manager.id)
            elif leave_type == 'annual_leave':
                # 年假需要部门经理审批
                manager = ApprovalService.get_department_manager(applicant.department)
                if manager:
                    chain.append(manager.id)
            elif leave_type in ['marriage_leave', 'maternity_leave', 'paternity_leave']:
                # 婚假、产假、陪产假需要部门经理和人事审批
                manager = ApprovalService.get_department_manager(applicant.department)
                if manager:
                    chain.append(manager.id)
                hr_manager = ApprovalService.get_hr_manager()
                if hr_manager:
                    chain.append(hr_manager.id)
            
            return chain
        except Exception as e:
            logging.error(f"构建审批链失败: {e}")
            return None
    
    @staticmethod
    def approve_leave_application(application_id, approver_id, comment=None):
        """
        审批通过请假申请
        
        Args:
            application_id: 申请ID
            approver_id: 审批人ID
            comment: 审批意见（可选）
            
        Returns:
            bool: 是否审批成功
        """
        try:
            application = LeaveApplication.query.get(application_id)
            if not application:
                return False
            
            application.status = ApprovalStatus.APPROVED.value
            application.approver_id = approver_id
            application.approved_at = datetime.utcnow()
            application.approval_comment = comment
            
            db.session.commit()
            
            # 发送通知
            NotificationService.create_notification(
                user_id=application.user_id,
                notification_type='approval_result',
                title='请假申请已批准',
                content=f'您的请假申请已被批准。{comment if comment else ""}'
            )
            
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"审批请假申请失败: {e}")
            return False
    
    @staticmethod
    def reject_leave_application(application_id, approver_id, comment=None):
        """
        拒绝请假申请
        
        Args:
            application_id: 申请ID
            approver_id: 审批人ID
            comment: 拒绝原因（可选）
            
        Returns:
            bool: 是否拒绝成功
        """
        try:
            application = LeaveApplication.query.get(application_id)
            if not application:
                return False
            
            application.status = ApprovalStatus.REJECTED.value
            application.approver_id = approver_id
            application.approved_at = datetime.utcnow()
            application.approval_comment = comment
            
            db.session.commit()
            
            # 发送通知
            NotificationService.create_notification(
                user_id=application.user_id,
                notification_type='approval_result',
                title='请假申请被拒绝',
                content=f'您的请假申请已被拒绝。{comment if comment else ""}'
            )
            
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"拒绝请假申请失败: {e}")
            return False
    
    @staticmethod
    def get_pending_approvals(approver_id):
        """
        获取审批人待处理的审批列表
        
        Args:
            approver_id: 审批人ID
            
        Returns:
            list: 待审批的申请列表
        """
        try:
            # 获取该审批人作为部门经理或人事经理的待审批申请
            approver = User.query.get(approver_id)
            if not approver:
                return []
            
            # 获取该审批人部门的待审批申请
            pending_applications = LeaveApplication.query.filter_by(
                status=ApprovalStatus.PENDING.value
            ).all()
            
            # 过滤出需要该审批人审批的申请
            result = []
            for app in pending_applications:
                chain = ApprovalService.build_approval_chain(
                    app.user_id, app.leave_type, app.start_date, app.end_date
                )
                if chain and approver_id in chain:
                    result.append(app)
            
            return result
        except Exception as e:
            logging.error(f"获取待审批列表失败: {e}")
            return []
