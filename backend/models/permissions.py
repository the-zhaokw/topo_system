from datetime import datetime

class PermissionCodes:
    """权限代码常量类"""
    # 顶层模块（侧边栏大功能）权限码：控制用户能看到哪些一级菜单
    MODULE_DASHBOARD = 'module:dashboard'
    MODULE_PROJECT = 'module:project'
    MODULE_BUG = 'module:bug'
    MODULE_ATTENDANCE = 'module:attendance'
    MODULE_MATERIAL = 'module:material'
    MODULE_CONTRACT = 'module:contract'
    MODULE_USER = 'module:user'
    MODULE_SETTINGS = 'module:settings'
    MODULE_ACTIVITY = 'module:activity'
    MODULE_KNOWLEDGE = 'module:knowledge'
    MODULE_MONITORING = 'module:monitoring'
    MODULE_TEST = 'module:test'
    MODULE_REQUIREMENT = 'module:requirement'
    MODULE_RISK = 'module:risk'
    MODULE_TODO = 'module:todo'
    MODULE_PLAN = 'module:plan'
    MODULE_DEPARTMENT = 'module:department'

    SYSTEM_ADMIN = 'system:admin'

    USER_VIEW = 'user:view'
    USER_CREATE = 'user:create'
    USER_EDIT = 'user:edit'
    USER_DELETE = 'user:delete'
    USER_IMPORT = 'user:import'
    USER_EXPORT = 'user:export'
    USER_ASSIGN_ROLE = 'user:assign_role'

    ROLE_VIEW = 'role:view'
    ROLE_CREATE = 'role:create'
    ROLE_EDIT = 'role:edit'
    ROLE_DELETE = 'role:delete'
    ROLE_ASSIGN_PERMISSION = 'role:assign_permission'

    PERMISSION_VIEW = 'permission:view'

    PROJECT_VIEW = 'project:view'
    PROJECT_CREATE = 'project:create'
    PROJECT_EDIT = 'project:edit'
    PROJECT_DELETE = 'project:delete'
    PROJECT_ASSIGN_MEMBER = 'project:assign_member'
    PROJECT_MANAGE_SETTINGS = 'project:manage_settings'

    BUG_VIEW = 'bug:view'
    BUG_CREATE = 'bug:create'
    BUG_EDIT = 'bug:edit'
    BUG_DELETE = 'bug:delete'
    BUG_ASSIGN = 'bug:assign'
    BUG_RESOLVE = 'bug:resolve'
    BUG_CLOSE = 'bug:close'

    TASK_VIEW = 'task:view'
    TASK_CREATE = 'task:create'
    TASK_EDIT = 'task:edit'
    TASK_DELETE = 'task:delete'
    TASK_ASSIGN = 'task:assign'
    TASK_UPDATE_STATUS = 'task:update_status'

    ATTENDANCE_VIEW = 'attendance:view'
    ATTENDANCE_MANAGE = 'attendance:manage'
    CLOCK_IN = 'attendance:clock_in'
    CLOCK_OUT = 'attendance:clock_out'
    LEAVE_APPLY = 'attendance:leave_apply'
    LEAVE_APPROVE = 'attendance:leave_approve'
    OVERTIME_APPLY = 'attendance:overtime_apply'
    OVERTIME_APPROVE = 'attendance:overtime_approve'
    EXCEPTION_HANDLE = 'attendance:exception_handle'
    EXCEPTION_APPROVE = 'attendance:exception_approve'
    ATTENDANCE_REPORT = 'attendance:report'

    STATISTICS_VIEW = 'statistics:view'
    DATA_EXPORT = 'data:export'
    DATA_IMPORT = 'data:import'

    CODE_SUBMIT = 'code:submit'


DEFAULT_ROLES = {
    'admin': {
        'name': '系统管理员',
        'description': '系统最高权限：拥有系统所有功能的完全控制权，可管理所有用户、角色、权限和系统配置',
        'scope': 'system',
        'permissions': 'all'
    },
    'manager': {
        'name': '总经理',
        'description': '总经理：拥有系统所有功能的完全控制权，可管理所有用户、角色、权限和系统配置',
        'scope': 'system',
        'permissions': 'all'
    },
    'project_manager': {
        'name': '项目经理',
        'description': '项目行政管理：创建项目、添加成员、分配任务（给任何工程师）、跟踪进度、管理项目设置',
        'scope': 'project',
        'permissions': [
            PermissionCodes.USER_VIEW,
            PermissionCodes.PROJECT_VIEW,
            PermissionCodes.PROJECT_CREATE,
            PermissionCodes.PROJECT_EDIT,
            PermissionCodes.PROJECT_DELETE,
            PermissionCodes.PROJECT_ASSIGN_MEMBER,
            PermissionCodes.PROJECT_MANAGE_SETTINGS,
            PermissionCodes.BUG_VIEW,
            PermissionCodes.BUG_CREATE,
            PermissionCodes.BUG_EDIT,
            PermissionCodes.BUG_DELETE,
            PermissionCodes.BUG_ASSIGN,
            PermissionCodes.BUG_RESOLVE,
            PermissionCodes.BUG_CLOSE,
            PermissionCodes.TASK_VIEW,
            PermissionCodes.TASK_CREATE,
            PermissionCodes.TASK_EDIT,
            PermissionCodes.TASK_DELETE,
            PermissionCodes.TASK_ASSIGN,
            PermissionCodes.TASK_UPDATE_STATUS,
            PermissionCodes.ATTENDANCE_VIEW,
            PermissionCodes.LEAVE_APPROVE,
            PermissionCodes.OVERTIME_APPROVE,
            PermissionCodes.EXCEPTION_APPROVE,
            PermissionCodes.ATTENDANCE_REPORT,
            PermissionCodes.STATISTICS_VIEW,
            PermissionCodes.DATA_EXPORT
        ]
    },
    'test_engineer': {
        'name': '测试工程师',
        'description': '测试执行：执行测试、提交Bug、查看分配给自己的任务',
        'scope': 'project',
        'permissions': [
            PermissionCodes.PROJECT_VIEW,
            PermissionCodes.BUG_VIEW,
            PermissionCodes.BUG_CREATE,
            PermissionCodes.BUG_EDIT,
            PermissionCodes.BUG_CLOSE,
            PermissionCodes.TASK_VIEW,
            PermissionCodes.CLOCK_IN,
            PermissionCodes.CLOCK_OUT,
            PermissionCodes.LEAVE_APPLY,
            PermissionCodes.OVERTIME_APPLY,
            PermissionCodes.EXCEPTION_HANDLE
        ]
    },
    'software_engineer': {
        'name': '软件工程师',
        'description': '开发执行：开发功能、修复Bug、提交代码、查看分配给自己的任务',
        'scope': 'project',
        'permissions': [
            PermissionCodes.PROJECT_VIEW,
            PermissionCodes.BUG_VIEW,
            PermissionCodes.BUG_CREATE,
            PermissionCodes.BUG_EDIT,
            PermissionCodes.BUG_RESOLVE,
            PermissionCodes.TASK_VIEW,
            PermissionCodes.TASK_CREATE,
            PermissionCodes.TASK_EDIT,
            PermissionCodes.TASK_UPDATE_STATUS,
            PermissionCodes.CODE_SUBMIT,
            PermissionCodes.CLOCK_IN,
            PermissionCodes.CLOCK_OUT,
            PermissionCodes.LEAVE_APPLY,
            PermissionCodes.OVERTIME_APPLY,
            PermissionCodes.EXCEPTION_HANDLE
        ]
    },
    'user': {
        'name': '普通用户',
        'description': '基本用户：查看项目、任务、Bug，打卡、申请请假加班等',
        'scope': 'project',
        'permissions': [
            PermissionCodes.PROJECT_VIEW,
            PermissionCodes.BUG_VIEW,
            PermissionCodes.BUG_CREATE,
            PermissionCodes.TASK_VIEW,
            PermissionCodes.CLOCK_IN,
            PermissionCodes.CLOCK_OUT,
            PermissionCodes.LEAVE_APPLY,
            PermissionCodes.OVERTIME_APPLY
        ]
    },
    'hr': {
        'name': '人事专员',
        'description': '人事管理：管理员工信息、考勤审批、统计报表等',
        'scope': 'system',
        'permissions': [
            PermissionCodes.USER_VIEW,
            PermissionCodes.USER_CREATE,
            PermissionCodes.USER_EDIT,
            PermissionCodes.ATTENDANCE_VIEW,
            PermissionCodes.ATTENDANCE_MANAGE,
            PermissionCodes.LEAVE_APPROVE,
            PermissionCodes.OVERTIME_APPROVE,
            PermissionCodes.EXCEPTION_APPROVE,
            PermissionCodes.ATTENDANCE_REPORT,
            PermissionCodes.STATISTICS_VIEW,
            PermissionCodes.DATA_EXPORT
        ]
    },
    'department_manager': {
        'name': '部门经理',
        'description': '部门管理：管理部门成员、查看部门考勤和统计、协调资源、项目审批',
        'scope': 'department',
        'permissions': [
            PermissionCodes.USER_VIEW,
            PermissionCodes.PROJECT_VIEW,
            PermissionCodes.PROJECT_CREATE,
            PermissionCodes.PROJECT_EDIT,
            PermissionCodes.PROJECT_DELETE,
            PermissionCodes.PROJECT_ASSIGN_MEMBER,
            PermissionCodes.BUG_VIEW,
            PermissionCodes.BUG_ASSIGN,
            PermissionCodes.BUG_RESOLVE,
            PermissionCodes.TASK_VIEW,
            PermissionCodes.TASK_ASSIGN,
            PermissionCodes.TASK_UPDATE_STATUS,
            PermissionCodes.ATTENDANCE_VIEW,
            PermissionCodes.ATTENDANCE_MANAGE,
            PermissionCodes.LEAVE_APPROVE,
            PermissionCodes.OVERTIME_APPROVE,
            PermissionCodes.EXCEPTION_APPROVE,
            PermissionCodes.ATTENDANCE_REPORT,
            PermissionCodes.STATISTICS_VIEW,
            PermissionCodes.DATA_EXPORT
        ]
    }
}


# 系统中所有的大功能模块（与侧边栏菜单一一对应）
# 用于在「模块权限管理」页面中给管理员勾选用户可见的功能
MODULE_CATALOG = [
    {
        'code': PermissionCodes.MODULE_DASHBOARD,
        'name': '个人工作台',
        'icon': 'House',
        'path': '/dashboard',
        'description': '个人工作台、待办、计划等',
        'default': True
    },
    {
        'code': PermissionCodes.MODULE_TODO,
        'name': '个人待办',
        'icon': 'List',
        'path': '/my-todos',
        'description': '个人待办事项管理',
        'default': True
    },
    {
        'code': PermissionCodes.MODULE_PLAN,
        'name': '个人计划',
        'icon': 'Calendar',
        'path': '/personal-plan',
        'description': '个人工作计划',
        'default': True
    },
    {
        'code': PermissionCodes.MODULE_ATTENDANCE,
        'name': '考勤管理',
        'icon': 'Clock',
        'path': '/attendance',
        'description': '考勤管理系统（打卡、请假、加班等）',
        'default': True
    },
    {
        'code': PermissionCodes.MODULE_PROJECT,
        'name': '项目管理',
        'icon': 'Folder',
        'path': '/projects',
        'description': '项目列表、统计、自定义报表',
        'default': True
    },
    {
        'code': PermissionCodes.MODULE_BUG,
        'name': '缺陷管理',
        'icon': 'Document',
        'path': '/bugs',
        'description': '缺陷列表、缺陷统计',
        'default': True
    },
    {
        'code': PermissionCodes.MODULE_REQUIREMENT,
        'name': '需求管理',
        'icon': 'Tickets',
        'path': '/requirements',
        'description': '需求文档管理、跟踪矩阵等',
        'default': True
    },
    {
        'code': PermissionCodes.MODULE_TEST,
        'name': '测试管理',
        'icon': 'MagicStick',
        'path': '/test-management',
        'description': '测试集、用例、执行、报告',
        'default': True
    },
    {
        'code': PermissionCodes.MODULE_RISK,
        'name': '风险管理',
        'icon': 'Warning',
        'path': '/risks',
        'description': '项目风险、问题跟踪',
        'default': True
    },
    {
        'code': PermissionCodes.MODULE_MATERIAL,
        'name': '物料管理',
        'icon': 'Box',
        'path': '/materials',
        'description': '物料分类、仓库、库存、序列号等',
        'default': False
    },
    {
        'code': PermissionCodes.MODULE_CONTRACT,
        'name': '合同管理',
        'icon': 'Document',
        'path': '/contracts',
        'description': '合同列表、合同统计',
        'default': False
    },
    {
        'code': PermissionCodes.MODULE_USER,
        'name': '用户管理',
        'icon': 'User',
        'path': '/users',
        'description': '用户、部门、职位、模块权限',
        'default': False
    },
    {
        'code': PermissionCodes.MODULE_DEPARTMENT,
        'name': '我的部门',
        'icon': 'OfficeBuilding',
        'path': '/my-department',
        'description': '我的部门成员',
        'default': True
    },
    {
        'code': PermissionCodes.MODULE_SETTINGS,
        'name': '系统设置',
        'icon': 'Setting',
        'path': '/settings',
        'description': '系统参数与配置',
        'default': False
    },
    {
        'code': PermissionCodes.MODULE_ACTIVITY,
        'name': '活动记录',
        'icon': 'Clock',
        'path': '/activities',
        'description': '系统活动记录',
        'default': True
    },
    {
        'code': PermissionCodes.MODULE_KNOWLEDGE,
        'name': '知识库',
        'icon': 'Reading',
        'path': '/knowledge',
        'description': '知识库文章管理',
        'default': True
    },
    {
        'code': PermissionCodes.MODULE_MONITORING,
        'name': '系统监控',
        'icon': 'Monitor',
        'path': '/monitoring',
        'description': '系统运行监控',
        'default': False
    }
]


def get_module_catalog():
    """获取大功能模块目录"""
    return MODULE_CATALOG


def get_default_accessible_modules():
    """获取默认应可见的模块权限码列表"""
    return [m['code'] for m in MODULE_CATALOG if m.get('default', False)]


