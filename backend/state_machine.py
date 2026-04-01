"""
Bug State Machine Implementation
Handles the workflow and state transitions for bug management
"""

from enum import Enum
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SMBugStatus(Enum):
    """Bug status enumeration"""
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    FIXED = "fixed"
    VERIFIED = "verified"
    CLOSED = "closed"
    REJECTED = "rejected"
    REOPENED = "reopened"


class SMBugPriority(Enum):
    """Bug priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"


class SMBugSeverity(Enum):
    """Bug severity enumeration"""
    TRIVIAL = "trivial"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


@dataclass
class StateTransition:
    """Represents a state transition"""
    from_status: SMBugStatus
    to_status: SMBugStatus
    required_roles: List[str]
    required_fields: List[str]
    notifications: List[str]
    validation_rules: List[str]
    description: str


@dataclass
class TransitionResult:
    """Result of a state transition"""
    success: bool
    message: str
    new_status: Optional[SMBugStatus] = None
    errors: List[str] = None


class BugStateMachine:
    """State machine for bug workflow management"""
    
    def __init__(self):
        self.transitions = self._define_transitions()
        self.state_transitions = self._build_state_transition_map()
        
    def _define_transitions(self) -> List[StateTransition]:
        """Define all possible state transitions"""
        return [
            # New to other states
            StateTransition(
                from_status=SMBugStatus.NEW,
                to_status=SMBugStatus.ASSIGNED,
                required_roles=['admin', 'project_manager', 'tester'],
                required_fields=['assignee_id', 'priority'],
                notifications=['assignee', 'reporter'],
                validation_rules=['assignee_exists', 'priority_valid'],
                description="Assign bug to developer"
            ),
            StateTransition(
                from_status=SMBugStatus.NEW,
                to_status=SMBugStatus.REJECTED,
                required_roles=['admin', 'project_manager'],
                required_fields=['reject_reason'],
                notifications=['reporter'],
                validation_rules=['reject_reason_provided'],
                description="Reject invalid bug report"
            ),
            
            # Assigned to other states
            StateTransition(
                from_status=SMBugStatus.ASSIGNED,
                to_status=SMBugStatus.IN_PROGRESS,
                required_roles=['admin', 'developer'],
                required_fields=[],
                notifications=['assignee', 'reporter'],
                validation_rules=['assigned_to_user'],
                description="Start working on bug"
            ),
            StateTransition(
                from_status=SMBugStatus.ASSIGNED,
                to_status=SMBugStatus.REOPENED,
                required_roles=['admin', 'project_manager', 'tester'],
                required_fields=['reopen_reason'],
                notifications=['assignee', 'reporter'],
                validation_rules=['reopen_reason_provided'],
                description="Reopen assigned bug"
            ),
            
            # In Progress to other states
            StateTransition(
                from_status=SMBugStatus.IN_PROGRESS,
                to_status=SMBugStatus.FIXED,
                required_roles=['admin', 'developer'],
                required_fields=['fix_description', 'fixed_version'],
                notifications=['assignee', 'reporter', 'tester'],
                validation_rules=['fix_description_provided', 'version_valid'],
                description="Mark bug as fixed"
            ),
            StateTransition(
                from_status=SMBugStatus.IN_PROGRESS,
                to_status=SMBugStatus.ASSIGNED,
                required_roles=['admin', 'project_manager'],
                required_fields=['reassign_reason'],
                notifications=['old_assignee', 'new_assignee', 'reporter'],
                validation_rules=['reassign_reason_provided'],
                description="Reassign to another developer"
            ),
            
            # Fixed to other states
            StateTransition(
                from_status=SMBugStatus.FIXED,
                to_status=SMBugStatus.VERIFIED,
                required_roles=['admin', 'tester'],
                required_fields=['verification_notes'],
                notifications=['assignee', 'reporter'],
                validation_rules=['verification_notes_provided'],
                description="Verify bug fix"
            ),
            StateTransition(
                from_status=SMBugStatus.FIXED,
                to_status=SMBugStatus.REOPENED,
                required_roles=['admin', 'tester'],
                required_fields=['reopen_reason'],
                notifications=['assignee', 'reporter'],
                validation_rules=['reopen_reason_provided'],
                description="Reopen fixed bug"
            ),
            
            # Verified to other states
            StateTransition(
                from_status=SMBugStatus.VERIFIED,
                to_status=SMBugStatus.CLOSED,
                required_roles=['admin', 'project_manager'],
                required_fields=[],
                notifications=['assignee', 'reporter'],
                validation_rules=[],
                description="Close verified bug"
            ),
            StateTransition(
                from_status=SMBugStatus.VERIFIED,
                to_status=SMBugStatus.REOPENED,
                required_roles=['admin', 'tester'],
                required_fields=['reopen_reason'],
                notifications=['assignee', 'reporter'],
                validation_rules=['reopen_reason_provided'],
                description="Reopen verified bug"
            ),
            
            # Closed to other states
            StateTransition(
                from_status=SMBugStatus.CLOSED,
                to_status=SMBugStatus.REOPENED,
                required_roles=['admin', 'project_manager', 'tester'],
                required_fields=['reopen_reason'],
                notifications=['assignee', 'reporter'],
                validation_rules=['reopen_reason_provided'],
                description="Reopen closed bug"
            ),
            
            # Rejected to other states
            StateTransition(
                from_status=SMBugStatus.REJECTED,
                to_status=SMBugStatus.NEW,
                required_roles=['admin', 'project_manager'],
                required_fields=['reopen_reason'],
                notifications=['reporter'],
                validation_rules=['reopen_reason_provided'],
                description="Reopen rejected bug"
            ),
            
            # Reopened to other states
            StateTransition(
                from_status=SMBugStatus.REOPENED,
                to_status=SMBugStatus.ASSIGNED,
                required_roles=['admin', 'project_manager'],
                required_fields=['assignee_id'],
                notifications=['assignee', 'reporter'],
                validation_rules=['assignee_exists'],
                description="Reassign reopened bug"
            ),
            StateTransition(
                from_status=SMBugStatus.REOPENED,
                to_status=SMBugStatus.IN_PROGRESS,
                required_roles=['admin', 'developer'],
                required_fields=[],
                notifications=['assignee', 'reporter'],
                validation_rules=['assigned_to_user'],
                description="Start working on reopened bug"
            )
        ]
    
    def _build_state_transition_map(self) -> Dict[SMBugStatus, Dict[SMBugStatus, StateTransition]]:
        """Build a map for quick transition lookup"""
        transition_map = {}
        
        for transition in self.transitions:
            if transition.from_status not in transition_map:
                transition_map[transition.from_status] = {}
            transition_map[transition.from_status][transition.to_status] = transition
        
        return transition_map
    
    def can_transition(self, from_status: SMBugStatus, to_status: SMBugStatus, 
                        user_role: str, bug_data: Dict) -> TransitionResult:
        """
        Check if a state transition is allowed
        
        Args:
            from_status: Current bug status
            to_status: Target status
            user_role: Role of the user attempting the transition
            bug_data: Current bug data
        
        Returns:
            TransitionResult with success status and details
        """
        # Check if transition exists
        if from_status not in self.state_transitions or to_status not in self.state_transitions[from_status]:
            return TransitionResult(
                success=False,
                message=f"不允许的状态转换: {from_status.value} → {to_status.value}",
                errors=["状态转换不存在"]
            )
        
        transition = self.state_transitions[from_status][to_status]
        errors = []
        
        # Check user role
        if user_role not in transition.required_roles:
            errors.append(f"用户角色 '{user_role}' 没有权限执行此转换")
        
        # Check required fields
        for field in transition.required_fields:
            if not bug_data.get(field):
                errors.append(f"缺少必填字段: {field}")
        
        # Run validation rules
        validation_errors = self._run_validation_rules(transition.validation_rules, bug_data)
        errors.extend(validation_errors)
        
        if errors:
            return TransitionResult(
                success=False,
                message="状态转换验证失败",
                errors=errors
            )
        
        return TransitionResult(
            success=True,
            message=f"状态转换允许: {transition.description}",
            new_status=to_status
        )
    
    def _run_validation_rules(self, rules: List[str], bug_data: Dict) -> List[str]:
        """Run validation rules for the transition"""
        errors = []
        
        for rule in rules:
            if rule == 'assignee_exists':
                if not bug_data.get('assignee_id'):
                    errors.append("必须指定分配给的用户")
            
            elif rule == 'priority_valid':
                priority = bug_data.get('priority')
                if priority not in [p.value for p in Priority]:
                    errors.append(f"无效的优先级: {priority}")
            
            elif rule == 'reject_reason_provided':
                if not bug_data.get('reject_reason'):
                    errors.append("必须提供拒绝原因")
            
            elif rule == 'reopen_reason_provided':
                if not bug_data.get('reopen_reason'):
                    errors.append("必须提供重新打开原因")
            
            elif rule == 'fix_description_provided':
                if not bug_data.get('fix_description'):
                    errors.append("必须提供修复描述")
            
            elif rule == 'version_valid':
                if not bug_data.get('fixed_version'):
                    errors.append("必须指定修复版本")
            
            elif rule == 'verification_notes_provided':
                if not bug_data.get('verification_notes'):
                    errors.append("必须提供验证说明")
            
            elif rule == 'reassign_reason_provided':
                if not bug_data.get('reassign_reason'):
                    errors.append("必须提供重新分配原因")
            
            elif rule == 'assigned_to_user':
                if not bug_data.get('assignee_id'):
                    errors.append("此操作需要先分配给用户")
        
        return errors
    
    def get_allowed_transitions(self, current_status: SMBugStatus, user_role: str) -> List[Dict]:
        """
        Get all allowed transitions from current status for a user role
        
        Args:
            current_status: Current bug status
            user_role: User's role
        
        Returns:
            List of allowed transitions with details
        """
        if current_status not in self.state_transitions:
            return []
        
        allowed = []
        for to_status, transition in self.state_transitions[current_status].items():
            if user_role in transition.required_roles:
                allowed.append({
                    'from_status': current_status.value,
                    'to_status': to_status.value,
                    'description': transition.description,
                    'required_fields': transition.required_fields,
                    'notifications': transition.notifications
                })
        
        return allowed
    
    def get_transition_description(self, from_status: SMBugStatus, to_status: SMBugStatus) -> str:
        """Get description of a specific transition"""
        if (from_status in self.state_transitions and 
            to_status in self.state_transitions[from_status]):
            return self.state_transitions[from_status][to_status].description
        return "未知转换"
    
    def get_required_notifications(self, from_status: SMBugStatus, to_status: SMBugStatus) -> List[str]:
        """Get list of required notifications for a transition"""
        if (from_status in self.state_transitions and 
            to_status in self.state_transitions[from_status]):
            return self.state_transitions[from_status][to_status].notifications
        return []


class BugWorkflowManager:
    """Manages bug workflow operations"""
    
    def __init__(self, state_machine: BugStateMachine):
        self.state_machine = state_machine
    
    def transition_bug(self, bug, new_status: SMBugStatus, user_role: str, 
                      transition_data: Dict = None) -> TransitionResult:
        """
        Transition a bug to a new status
        
        Args:
            bug: Bug object or dictionary with bug data
            new_status: Target status
            user_role: Role of the user performing the transition
            transition_data: Additional data for the transition
        
        Returns:
            TransitionResult with success status and details
        """
        # Prepare bug data
        bug_data = self._prepare_bug_data(bug, transition_data)
        current_status = SMBugStatus(bug_data['status'])
        
        # Check if transition is allowed
        result = self.state_machine.can_transition(
            current_status, new_status, user_role, bug_data
        )
        
        if result.success:
            # Update bug status
            result.new_status = new_status
            
            # Log the transition
            logger.info(f"Bug {bug_data.get('id', 'unknown')} transitioned from "
                       f"{current_status.value} to {new_status.value} by {user_role}")
        
        return result
    
    def _prepare_bug_data(self, bug, transition_data: Dict = None) -> Dict:
        """Prepare bug data for transition validation"""
        if isinstance(bug, dict):
            bug_data = bug.copy()
        else:
            # Convert bug object to dictionary
            bug_data = {
                'id': bug.id,
                'status': bug.status,
                'assignee_id': bug.assigned_to,
                'priority': bug.priority,
                'reporter_id': bug.reported_by,
                'project_id': bug.project_id,
                'title': bug.title,
                'description': bug.description,
                'created_at': bug.created_at,
                'updated_at': bug.updated_at
            }
        
        # Merge transition data
        if transition_data:
            bug_data.update(transition_data)
        
        return bug_data
    
    def get_workflow_suggestions(self, bug, user_role: str) -> List[Dict]:
        """
        Get workflow suggestions for a bug based on current status and user role
        
        Args:
            bug: Bug object or dictionary
            user_role: User's role
        
        Returns:
            List of suggested transitions with details
        """
        current_status = SMBugStatus(bug['status'] if isinstance(bug, dict) else bug.status)
        
        suggestions = self.state_machine.get_allowed_transitions(current_status, user_role)
        
        # Add urgency indicators
        for suggestion in suggestions:
            suggestion['urgency'] = self._calculate_transition_urgency(suggestion['to_status'])
        
        return sorted(suggestions, key=lambda x: x['urgency'], reverse=True)
    
    def _calculate_transition_urgency(self, status: str) -> int:
        """Calculate urgency score for a transition"""
        urgency_scores = {
            'urgent': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        # Simple heuristic based on status
        if status in ['in_progress', 'fixed']:
            return 3
        elif status in ['verified', 'closed']:
            return 2
        else:
            return 1
    
    def validate_workflow_rules(self, bug, user_role: str) -> List[str]:
        """
        Validate bug against workflow rules
        
        Args:
            bug: Bug object or dictionary
            user_role: User's role
        
        Returns:
            List of validation warnings
        """
        warnings = []
        
        current_status = SMBugStatus(bug['status'] if isinstance(bug, dict) else bug.status)
        
        # Check for overdue bugs
        if hasattr(bug, 'due_date') and bug.due_date:
            if datetime.utcnow() > bug.due_date:
                warnings.append("Bug 已逾期")
        
        # Check for bugs stuck in same status too long
        if hasattr(bug, 'status_changed_at') and bug.status_changed_at:
            days_in_status = (datetime.utcnow() - bug.status_changed_at).days
            if days_in_status > 7 and current_status in [SMBugStatus.ASSIGNED, SMBugStatus.IN_PROGRESS]:
                warnings.append(f"Bug 在 {current_status.value} 状态已超过 {days_in_status} 天")
        
        # Check for high priority bugs not being worked on
        if (hasattr(bug, 'priority') and bug.priority == 'urgent' and 
            current_status in [SMBugStatus.NEW, SMBugStatus.ASSIGNED]):
            warnings.append("紧急优先级的 Bug 需要尽快处理")
        
        return warnings


# Global state machine instance
bug_state_machine = BugStateMachine()
bug_workflow_manager = BugWorkflowManager(bug_state_machine)


def get_bug_workflow_manager():
    """Get the global bug workflow manager instance"""
    return bug_workflow_manager


def get_bug_state_machine():
    """Get the global bug state machine instance"""
    return bug_state_machine


# Example usage and testing
if __name__ == "__main__":
    # Test the state machine
    machine = BugStateMachine()
    
    # Test transition validation
    result = machine.can_transition(
        SMBugStatus.NEW,
        SMBugStatus.ASSIGNED,
        'project_manager',
        {'assignee_id': 1, 'priority': 'high'}
    )
    
    print(f"Transition result: {result}")
    
    # Test allowed transitions
    allowed = machine.get_allowed_transitions(SMBugStatus.NEW, 'project_manager')
    print(f"Allowed transitions from NEW for project_manager: {allowed}")
    
    # Test workflow manager
    manager = BugWorkflowManager(machine)
    
    # Test bug transition
    test_bug = {
        'id': 1,
        'status': 'new',
        'assignee_id': None,
        'priority': 'medium',
        'reporter_id': 2
    }
    
    result = manager.transition_bug(
        test_bug,
        SMBugStatus.ASSIGNED,
        'project_manager',
        {'assignee_id': 3, 'priority': 'high'}
    )
    
    print(f"Bug transition result: {result}")