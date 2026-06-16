from datetime import datetime

class PermissionCodes:
    """权限代码常量类

    命名规则：
        - module:xxx    顶层模块（侧边栏大功能）权限，控制一级菜单是否可见
        - xxx:view      查看类权限（只读）
        - xxx:create    新增权限
        - xxx:edit      编辑/修改权限
        - xxx:delete    删除权限
        - xxx:export    导出权限
        - xxx:import    导入权限
    """
    # ==================== 顶层模块（一级菜单）权限码 ====================
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

    # ==================== 系统级 ====================
    SYSTEM_ADMIN = 'system:admin'
    SYSTEM_CONFIG = 'system:config'

    # ==================== 模块权限管理 ====================
    # 控制「用户管理 > 模块权限管理」页面的访问与操作
    MODULE_PERM_VIEW = 'module_perm:view'        # 查看模块权限管理页面
    MODULE_PERM_EDIT = 'module_perm:edit'        # 编辑用户可见模块/细分权限
    MODULE_PERM_RESET = 'module_perm:reset'      # 重置用户模块/权限为系统默认
    MODULE_PERM_VIEW_ALL = 'module_perm:view_all'  # 查看全员模块权限概览

    # ==================== 权限模板 ====================
    # 控制「用户管理 > 权限模板」页面的访问与操作
    TEMPLATE_VIEW = 'template:view'        # 查看模板
    TEMPLATE_CREATE = 'template:create'    # 新建模板
    TEMPLATE_EDIT = 'template:edit'        # 编辑模板
    TEMPLATE_DELETE = 'template:delete'    # 删除模板
    TEMPLATE_APPLY = 'template:apply'      # 一键应用模板给用户

    # ==================== 用户管理 ====================
    USER_VIEW = 'user:view'
    USER_CREATE = 'user:create'
    USER_EDIT = 'user:edit'
    USER_DELETE = 'user:delete'
    USER_IMPORT = 'user:import'
    USER_EXPORT = 'user:export'
    USER_RESET_PASSWORD = 'user:reset_password'
    USER_DISABLE = 'user:disable'

    # ==================== 部门/职位管理 ====================
    DEPARTMENT_VIEW = 'department:view'
    DEPARTMENT_CREATE = 'department:create'
    DEPARTMENT_EDIT = 'department:edit'
    DEPARTMENT_DELETE = 'department:delete'

    POSITION_VIEW = 'position:view'
    POSITION_CREATE = 'position:create'
    POSITION_EDIT = 'position:edit'
    POSITION_DELETE = 'position:delete'
    POSITION_ASSIGN = 'position:assign'

    # ==================== 角色/权限管理 ====================
    ROLE_VIEW = 'role:view'
    ROLE_CREATE = 'role:create'
    ROLE_EDIT = 'role:edit'
    ROLE_DELETE = 'role:delete'
    ROLE_ASSIGN_PERMISSION = 'role:assign_permission'
    PERMISSION_VIEW = 'permission:view'

    # ==================== 项目管理 ====================
    PROJECT_VIEW = 'project:view'
    PROJECT_CREATE = 'project:create'
    PROJECT_EDIT = 'project:edit'
    PROJECT_DELETE = 'project:delete'
    PROJECT_ASSIGN_MEMBER = 'project:assign_member'
    PROJECT_REMOVE_MEMBER = 'project:remove_member'
    PROJECT_MANAGE_SETTINGS = 'project:manage_settings'
    PROJECT_VIEW_STATISTICS = 'project:view_statistics'
    PROJECT_EXPORT = 'project:export'

    # ==================== 任务（项目内任务） ====================
    TASK_VIEW = 'task:view'
    TASK_CREATE = 'task:create'
    TASK_EDIT = 'task:edit'
    TASK_DELETE = 'task:delete'
    TASK_ASSIGN = 'task:assign'
    TASK_UPDATE_STATUS = 'task:update_status'

    # ==================== 工时 / 项目日志 ====================
    WORKLOG_VIEW = 'worklog:view'
    WORKLOG_CREATE = 'worklog:create'
    WORKLOG_EDIT = 'worklog:edit'
    WORKLOG_DELETE = 'worklog:delete'
    WORKLOG_REVIEW = 'worklog:review'

    # ==================== 缺陷管理 ====================
    BUG_VIEW = 'bug:view'
    BUG_CREATE = 'bug:create'
    BUG_EDIT = 'bug:edit'
    BUG_DELETE = 'bug:delete'
    BUG_ASSIGN = 'bug:assign'
    BUG_RESOLVE = 'bug:resolve'
    BUG_CLOSE = 'bug:close'
    BUG_REOPEN = 'bug:reopen'
    BUG_COMMENT = 'bug:comment'
    BUG_UPLOAD_ATTACHMENT = 'bug:upload_attachment'
    BUG_DOWNLOAD_ATTACHMENT = 'bug:download_attachment'
    BUG_EXPORT = 'bug:export'
    BUG_IMPORT = 'bug:import'
    BUG_BATCH = 'bug:batch'
    BUG_VIEW_STATISTICS = 'bug:view_statistics'

    # ==================== 需求管理 ====================
    REQUIREMENT_VIEW = 'requirement:view'
    REQUIREMENT_DOC_CREATE = 'requirement:doc_create'
    REQUIREMENT_DOC_EDIT = 'requirement:doc_edit'
    REQUIREMENT_DOC_DELETE = 'requirement:doc_delete'
    REQUIREMENT_DOC_REVIEW = 'requirement:doc_review'
    REQUIREMENT_DOC_CHANGE_STATUS = 'requirement:doc_change_status'
    REQUIREMENT_DOC_VERSION = 'requirement:doc_version'
    REQUIREMENT_DOC_ROLLBACK = 'requirement:doc_rollback'
    REQUIREMENT_ITEM_CREATE = 'requirement:item_create'
    REQUIREMENT_ITEM_EDIT = 'requirement:item_edit'
    REQUIREMENT_ITEM_DELETE = 'requirement:item_delete'
    REQUIREMENT_ITEM_CHANGE_STATUS = 'requirement:item_change_status'
    REQUIREMENT_COMMENT = 'requirement:comment'
    REQUIREMENT_LINK = 'requirement:link'
    REQUIREMENT_EXPORT = 'requirement:export'
    REQUIREMENT_VIEW_MATRIX = 'requirement:view_matrix'

    # ==================== 测试管理 ====================
    TEST_VIEW = 'test:view'
    TEST_SUITE_CREATE = 'test:suite_create'
    TEST_SUITE_EDIT = 'test:suite_edit'
    TEST_SUITE_DELETE = 'test:suite_delete'
    TEST_CASE_CREATE = 'test:case_create'
    TEST_CASE_EDIT = 'test:case_edit'
    TEST_CASE_DELETE = 'test:case_delete'
    TEST_CASE_REVIEW = 'test:case_review'
    TEST_EXECUTION_CREATE = 'test:execution_create'
    TEST_EXECUTION_EDIT = 'test:execution_edit'
    TEST_EXECUTION_DELETE = 'test:execution_delete'
    TEST_RESULT_SUBMIT = 'test:result_submit'
    TEST_EXPORT = 'test:export'
    TEST_IMPORT = 'test:import'
    TEST_VIEW_REPORT = 'test:view_report'

    # ==================== 风险管理 ====================
    RISK_VIEW = 'risk:view'
    RISK_CREATE = 'risk:create'
    RISK_EDIT = 'risk:edit'
    RISK_DELETE = 'risk:delete'
    RISK_VIEW_MATRIX = 'risk:view_matrix'
    RISK_VIEW_STATISTICS = 'risk:view_statistics'

    # ==================== 物料管理 ====================
    MATERIAL_VIEW = 'material:view'
    MATERIAL_CATEGORY_MANAGE = 'material:category_manage'
    MATERIAL_CREATE = 'material:create'
    MATERIAL_EDIT = 'material:edit'
    MATERIAL_DELETE = 'material:delete'
    MATERIAL_INVENTORY_VIEW = 'material:inventory_view'
    MATERIAL_INVENTORY_EDIT = 'material:inventory_edit'
    MATERIAL_WAREHOUSE_MANAGE = 'material:warehouse_manage'
    MATERIAL_SERIAL_MANAGE = 'material:serial_manage'
    MATERIAL_IMPORT = 'material:import'
    MATERIAL_EXPORT = 'material:export'
    MATERIAL_VIEW_REPORTS = 'material:view_reports'

    # ==================== 合同管理 ====================
    CONTRACT_VIEW = 'contract:view'
    CONTRACT_CREATE = 'contract:create'
    CONTRACT_EDIT = 'contract:edit'
    CONTRACT_DELETE = 'contract:delete'
    CONTRACT_APPROVE = 'contract:approve'
    CONTRACT_VIEW_STATISTICS = 'contract:view_statistics'
    CONTRACT_VIEW_FINANCE = 'contract:view_finance'
    CONTRACT_EXPORT = 'contract:export'

    # ==================== 考勤管理 ====================
    ATTENDANCE_VIEW = 'attendance:view'        # 查看自己/部门考勤
    ATTENDANCE_MANAGE = 'attendance:manage'    # 管理考勤设置（班次/规则）
    CLOCK_IN = 'attendance:clock_in'
    CLOCK_OUT = 'attendance:clock_out'
    LEAVE_APPLY = 'attendance:leave_apply'
    LEAVE_APPROVE = 'attendance:leave_approve'
    OVERTIME_APPLY = 'attendance:overtime_apply'
    OVERTIME_APPROVE = 'attendance:overtime_approve'
    EXCEPTION_HANDLE = 'attendance:exception_handle'    # 提交异常处理
    EXCEPTION_APPROVE = 'attendance:exception_approve'  # 审批异常处理
    SHIFT_MANAGE = 'attendance:shift_manage'            # 班次管理
    USER_SHIFT_ASSIGN = 'attendance:user_shift_assign'  # 分配员工班次
    ATTENDANCE_REPORT = 'attendance:report'            # 考勤报表
    ATTENDANCE_EXPORT = 'attendance:export'

    # ==================== 个人待办 / 待审批 ====================
    TODO_VIEW = 'todo:view'
    TODO_HANDLE = 'todo:handle'

    # ==================== 个人计划 ====================
    PLAN_VIEW = 'plan:view'
    PLAN_TASK_CREATE = 'plan:task_create'
    PLAN_TASK_EDIT = 'plan:task_edit'
    PLAN_TASK_DELETE = 'plan:task_delete'
    PLAN_HABIT_MANAGE = 'plan:habit_manage'
    PLAN_FOCUS_MANAGE = 'plan:focus_manage'
    PLAN_TIME_BLOCK_MANAGE = 'plan:time_block_manage'
    PLAN_SETTINGS = 'plan:settings'

    # ==================== 知识库 ====================
    KNOWLEDGE_VIEW = 'knowledge:view'
    KNOWLEDGE_CATEGORY_MANAGE = 'knowledge:category_manage'
    KNOWLEDGE_ARTICLE_CREATE = 'knowledge:article_create'
    KNOWLEDGE_ARTICLE_EDIT = 'knowledge:article_edit'
    KNOWLEDGE_ARTICLE_DELETE = 'knowledge:article_delete'
    KNOWLEDGE_ARTICLE_REVIEW = 'knowledge:article_review'
    KNOWLEDGE_ARTICLE_PUBLISH = 'knowledge:article_publish'
    KNOWLEDGE_COMMENT = 'knowledge:comment'
    KNOWLEDGE_LIKE_FAVORITE = 'knowledge:like_favorite'
    KNOWLEDGE_UPLOAD = 'knowledge:upload'
    KNOWLEDGE_DOWNLOAD = 'knowledge:download'
    KNOWLEDGE_SHARE_MANAGE = 'knowledge:share_manage'
    KNOWLEDGE_EXPORT = 'knowledge:export'
    KNOWLEDGE_VIEW_STATISTICS = 'knowledge:view_statistics'

    # ==================== 活动记录 ====================
    ACTIVITY_VIEW = 'activity:view'
    ACTIVITY_CREATE = 'activity:create'
    ACTIVITY_DELETE = 'activity:delete'
    ACTIVITY_EXPORT = 'activity:export'

    # ==================== 系统监控 ====================
    MONITORING_VIEW = 'monitoring:view'
    MONITORING_HEALTH = 'monitoring:health'
    MONITORING_PERFORMANCE = 'monitoring:performance'
    MONITORING_DATABASE = 'monitoring:database'
    MONITORING_LOGS = 'monitoring:logs'
    MONITORING_ALERT_MANAGE = 'monitoring:alert_manage'
    MONITORING_ALERT_RULE = 'monitoring:alert_rule'

    # ==================== 系统设置 ====================
    SETTINGS_VIEW = 'settings:view'
    SETTINGS_EDIT = 'settings:edit'
    SETTINGS_NOTIFICATION = 'settings:notification'
    SETTINGS_BACKUP = 'settings:backup'
    SETTINGS_LOG_MANAGE = 'settings:log_manage'

    # ==================== 统计/导入导出 ====================
    STATISTICS_VIEW = 'statistics:view'
    DATA_EXPORT = 'data:export'
    DATA_IMPORT = 'data:import'

    # ==================== 审计日志 ====================
    AUDIT_VIEW = 'audit:view'
    AUDIT_EXPORT = 'audit:export'

    # ==================== 通知 ====================
    NOTIFICATION_VIEW = 'notification:view'
    NOTIFICATION_SEND = 'notification:send'

    # ==================== 代码提交 ====================
    CODE_SUBMIT = 'code:submit'

    # ==================== 部门/同事 ====================
    DEPARTMENT_MEMBER_VIEW = 'department:member_view'


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


# =============================================================================
# 细分权限分类（用于「模块权限管理」页面中的「细分权限」Tab）
# 格式：{ category_key: { 'name': 显示名, 'icon': 图标名, 'module': 所属一级模块编码, 'permissions': [(code, name, desc), ...] } }
# =============================================================================
PERMISSION_CATEGORIES = {
    'project': {
        'name': '项目管理',
        'icon': 'Folder',
        'module': PermissionCodes.MODULE_PROJECT,
        'order': 10,
        'permissions': [
            (PermissionCodes.PROJECT_VIEW, '查看项目', '查看项目列表与项目详情'),
            (PermissionCodes.PROJECT_CREATE, '创建项目', '创建新项目'),
            (PermissionCodes.PROJECT_EDIT, '编辑项目', '编辑项目基础信息'),
            (PermissionCodes.PROJECT_DELETE, '删除项目', '删除项目（高危操作）'),
            (PermissionCodes.PROJECT_ASSIGN_MEMBER, '分配项目成员', '添加/邀请项目成员'),
            (PermissionCodes.PROJECT_REMOVE_MEMBER, '移除项目成员', '从项目中移除成员'),
            (PermissionCodes.PROJECT_MANAGE_SETTINGS, '项目设置', '维护项目配置、自定义字段、阶段等'),
            (PermissionCodes.PROJECT_VIEW_STATISTICS, '查看项目统计', '查看项目内统计报表'),
            (PermissionCodes.PROJECT_EXPORT, '导出项目数据', '导出项目列表/详情/统计为 Excel'),
        ]
    },
    'task': {
        'name': '任务管理',
        'icon': 'List',
        'module': PermissionCodes.MODULE_PROJECT,
        'order': 11,
        'permissions': [
            (PermissionCodes.TASK_VIEW, '查看任务', '查看任务列表与详情'),
            (PermissionCodes.TASK_CREATE, '创建任务', '新建项目任务'),
            (PermissionCodes.TASK_EDIT, '编辑任务', '修改任务内容'),
            (PermissionCodes.TASK_DELETE, '删除任务', '删除任务'),
            (PermissionCodes.TASK_ASSIGN, '指派任务', '将任务指派给指定成员'),
            (PermissionCodes.TASK_UPDATE_STATUS, '更新任务状态', '修改任务状态/进度'),
        ]
    },
    'worklog': {
        'name': '工时/工作日志',
        'icon': 'Document',
        'module': PermissionCodes.MODULE_PROJECT,
        'order': 12,
        'permissions': [
            (PermissionCodes.WORKLOG_VIEW, '查看日志', '查看项目日志与工时'),
            (PermissionCodes.WORKLOG_CREATE, '创建日志', '提交项目日志/工时'),
            (PermissionCodes.WORKLOG_EDIT, '编辑日志', '编辑自己提交的日志'),
            (PermissionCodes.WORKLOG_DELETE, '删除日志', '删除自己提交的日志'),
            (PermissionCodes.WORKLOG_REVIEW, '审核日志', '审核/驳回下属日志'),
        ]
    },
    'bug': {
        'name': '缺陷管理',
        'icon': 'Warning',
        'module': PermissionCodes.MODULE_BUG,
        'order': 20,
        'permissions': [
            (PermissionCodes.BUG_VIEW, '查看缺陷', '查看缺陷列表与详情'),
            (PermissionCodes.BUG_CREATE, '创建缺陷', '提交新缺陷'),
            (PermissionCodes.BUG_EDIT, '编辑缺陷', '修改缺陷信息（标题/描述/优先级）'),
            (PermissionCodes.BUG_DELETE, '删除缺陷', '删除缺陷（高危）'),
            (PermissionCodes.BUG_ASSIGN, '分派缺陷', '将缺陷分派给处理人'),
            (PermissionCodes.BUG_RESOLVE, '解决缺陷', '将缺陷标记为已解决'),
            (PermissionCodes.BUG_CLOSE, '关闭缺陷', '关闭已解决/已验证的缺陷'),
            (PermissionCodes.BUG_REOPEN, '重开缺陷', '重开已关闭的缺陷'),
            (PermissionCodes.BUG_COMMENT, '评论缺陷', '在缺陷下评论/回复'),
            (PermissionCodes.BUG_UPLOAD_ATTACHMENT, '上传附件', '上传缺陷相关附件'),
            (PermissionCodes.BUG_DOWNLOAD_ATTACHMENT, '下载附件', '下载缺陷附件'),
            (PermissionCodes.BUG_EXPORT, '导出缺陷', '导出缺陷列表/统计'),
            (PermissionCodes.BUG_IMPORT, '导入缺陷', '从 Excel 导入缺陷'),
            (PermissionCodes.BUG_BATCH, '批量操作', '批量更新/删除缺陷'),
            (PermissionCodes.BUG_VIEW_STATISTICS, '查看缺陷统计', '查看缺陷统计与图表'),
        ]
    },
    'requirement': {
        'name': '需求管理',
        'icon': 'Tickets',
        'module': PermissionCodes.MODULE_REQUIREMENT,
        'order': 30,
        'permissions': [
            (PermissionCodes.REQUIREMENT_VIEW, '查看需求', '查看需求文档与条目'),
            (PermissionCodes.REQUIREMENT_DOC_CREATE, '创建需求文档', '新建需求文档'),
            (PermissionCodes.REQUIREMENT_DOC_EDIT, '编辑需求文档', '编辑需求文档基础信息'),
            (PermissionCodes.REQUIREMENT_DOC_DELETE, '删除需求文档', '删除需求文档'),
            (PermissionCodes.REQUIREMENT_DOC_REVIEW, '审核需求文档', '审核/批准需求文档'),
            (PermissionCodes.REQUIREMENT_DOC_CHANGE_STATUS, '变更文档状态', '变更需求文档状态'),
            (PermissionCodes.REQUIREMENT_DOC_VERSION, '管理版本', '创建/查看文档历史版本'),
            (PermissionCodes.REQUIREMENT_DOC_ROLLBACK, '回滚版本', '回滚到指定历史版本'),
            (PermissionCodes.REQUIREMENT_ITEM_CREATE, '新建条目', '创建需求条目'),
            (PermissionCodes.REQUIREMENT_ITEM_EDIT, '编辑条目', '编辑需求条目'),
            (PermissionCodes.REQUIREMENT_ITEM_DELETE, '删除条目', '删除需求条目'),
            (PermissionCodes.REQUIREMENT_ITEM_CHANGE_STATUS, '变更条目状态', '变更需求条目状态'),
            (PermissionCodes.REQUIREMENT_COMMENT, '评论', '在需求文档/条目下评论'),
            (PermissionCodes.REQUIREMENT_LINK, '关联关系', '建立/解除需求关联'),
            (PermissionCodes.REQUIREMENT_EXPORT, '导出需求', '导出需求文档/条目'),
            (PermissionCodes.REQUIREMENT_VIEW_MATRIX, '查看跟踪矩阵', '查看需求跟踪矩阵'),
        ]
    },
    'test': {
        'name': '测试管理',
        'icon': 'MagicStick',
        'module': PermissionCodes.MODULE_TEST,
        'order': 40,
        'permissions': [
            (PermissionCodes.TEST_VIEW, '查看测试', '查看测试集、用例、执行'),
            (PermissionCodes.TEST_SUITE_CREATE, '创建测试集', '新建测试集'),
            (PermissionCodes.TEST_SUITE_EDIT, '编辑测试集', '编辑测试集'),
            (PermissionCodes.TEST_SUITE_DELETE, '删除测试集', '删除测试集'),
            (PermissionCodes.TEST_CASE_CREATE, '创建用例', '创建测试用例'),
            (PermissionCodes.TEST_CASE_EDIT, '编辑用例', '编辑测试用例'),
            (PermissionCodes.TEST_CASE_DELETE, '删除用例', '删除测试用例'),
            (PermissionCodes.TEST_CASE_REVIEW, '审核用例', '审核/批准测试用例'),
            (PermissionCodes.TEST_EXECUTION_CREATE, '创建执行', '创建测试执行'),
            (PermissionCodes.TEST_EXECUTION_EDIT, '编辑执行', '编辑测试执行'),
            (PermissionCodes.TEST_EXECUTION_DELETE, '删除执行', '删除测试执行'),
            (PermissionCodes.TEST_RESULT_SUBMIT, '提交结果', '提交/更新执行结果'),
            (PermissionCodes.TEST_EXPORT, '导出', '导出测试集/用例/报告'),
            (PermissionCodes.TEST_IMPORT, '导入', '导入测试集/用例'),
            (PermissionCodes.TEST_VIEW_REPORT, '查看报告', '查看测试报告'),
        ]
    },
    'risk': {
        'name': '风险管理',
        'icon': 'Warning',
        'module': PermissionCodes.MODULE_RISK,
        'order': 50,
        'permissions': [
            (PermissionCodes.RISK_VIEW, '查看风险', '查看风险列表与详情'),
            (PermissionCodes.RISK_CREATE, '创建风险', '新增风险'),
            (PermissionCodes.RISK_EDIT, '编辑风险', '修改风险信息'),
            (PermissionCodes.RISK_DELETE, '删除风险', '删除风险'),
            (PermissionCodes.RISK_VIEW_MATRIX, '查看风险矩阵', '查看风险矩阵视图'),
            (PermissionCodes.RISK_VIEW_STATISTICS, '查看风险统计', '查看风险统计报表'),
        ]
    },
    'attendance': {
        'name': '考勤管理',
        'icon': 'Clock',
        'module': PermissionCodes.MODULE_ATTENDANCE,
        'order': 60,
        'permissions': [
            (PermissionCodes.ATTENDANCE_VIEW, '查看考勤', '查看自己/部门考勤记录'),
            (PermissionCodes.CLOCK_IN, '上班打卡', '执行上班打卡'),
            (PermissionCodes.CLOCK_OUT, '下班打卡', '执行下班打卡'),
            (PermissionCodes.LEAVE_APPLY, '申请请假', '提交请假申请'),
            (PermissionCodes.LEAVE_APPROVE, '审批请假', '审批下属的请假申请'),
            (PermissionCodes.OVERTIME_APPLY, '申请加班', '提交加班申请'),
            (PermissionCodes.OVERTIME_APPROVE, '审批加班', '审批下属的加班申请'),
            (PermissionCodes.EXCEPTION_HANDLE, '异常处理申请', '提交考勤异常处理'),
            (PermissionCodes.EXCEPTION_APPROVE, '审批异常', '审批考勤异常处理'),
            (PermissionCodes.SHIFT_MANAGE, '班次管理', '维护班次信息'),
            (PermissionCodes.USER_SHIFT_ASSIGN, '分配员工班次', '为员工分配班次'),
            (PermissionCodes.ATTENDANCE_MANAGE, '考勤管理', '管理考勤规则与设置'),
            (PermissionCodes.ATTENDANCE_REPORT, '考勤报表', '查看考勤统计报表'),
            (PermissionCodes.ATTENDANCE_EXPORT, '导出考勤', '导出考勤数据'),
        ]
    },
    'material': {
        'name': '物料管理',
        'icon': 'Box',
        'module': PermissionCodes.MODULE_MATERIAL,
        'order': 70,
        'permissions': [
            (PermissionCodes.MATERIAL_VIEW, '查看物料', '查看物料列表与详情'),
            (PermissionCodes.MATERIAL_CATEGORY_MANAGE, '物料分类', '管理物料分类'),
            (PermissionCodes.MATERIAL_CREATE, '创建物料', '新增物料'),
            (PermissionCodes.MATERIAL_EDIT, '编辑物料', '编辑物料信息'),
            (PermissionCodes.MATERIAL_DELETE, '删除物料', '删除物料'),
            (PermissionCodes.MATERIAL_INVENTORY_VIEW, '查看库存', '查看库存数量'),
            (PermissionCodes.MATERIAL_INVENTORY_EDIT, '调整库存', '出入库、盘点调整'),
            (PermissionCodes.MATERIAL_WAREHOUSE_MANAGE, '仓库管理', '管理仓库信息'),
            (PermissionCodes.MATERIAL_SERIAL_MANAGE, '序列号管理', '管理物料序列号'),
            (PermissionCodes.MATERIAL_IMPORT, '导入物料', '从 Excel 导入物料'),
            (PermissionCodes.MATERIAL_EXPORT, '导出物料', '导出物料数据'),
            (PermissionCodes.MATERIAL_VIEW_REPORTS, '查看报表', '查看库存价值、领用、库存周转等报表'),
        ]
    },
    'contract': {
        'name': '合同管理',
        'icon': 'Document',
        'module': PermissionCodes.MODULE_CONTRACT,
        'order': 80,
        'permissions': [
            (PermissionCodes.CONTRACT_VIEW, '查看合同', '查看合同列表与详情'),
            (PermissionCodes.CONTRACT_CREATE, '创建合同', '创建新合同'),
            (PermissionCodes.CONTRACT_EDIT, '编辑合同', '编辑合同信息'),
            (PermissionCodes.CONTRACT_DELETE, '删除合同', '删除合同'),
            (PermissionCodes.CONTRACT_APPROVE, '审批合同', '审批合同流程'),
            (PermissionCodes.CONTRACT_VIEW_STATISTICS, '查看合同统计', '查看合同统计报表'),
            (PermissionCodes.CONTRACT_VIEW_FINANCE, '查看财务信息', '查看合同金额、回款等财务信息'),
            (PermissionCodes.CONTRACT_EXPORT, '导出合同', '导出合同数据'),
        ]
    },
    'user': {
        'name': '用户管理',
        'icon': 'User',
        'module': PermissionCodes.MODULE_USER,
        'order': 90,
        'permissions': [
            (PermissionCodes.USER_VIEW, '查看用户', '查看用户列表与详情'),
            (PermissionCodes.USER_CREATE, '创建用户', '新增用户'),
            (PermissionCodes.USER_EDIT, '编辑用户', '编辑用户信息'),
            (PermissionCodes.USER_DELETE, '删除用户', '删除用户'),
            (PermissionCodes.USER_RESET_PASSWORD, '重置密码', '重置用户密码'),
            (PermissionCodes.USER_DISABLE, '启用/禁用', '启用/禁用用户'),
            (PermissionCodes.USER_IMPORT, '导入用户', '从 Excel 导入用户'),
            (PermissionCodes.USER_EXPORT, '导出用户', '导出用户数据'),
        ]
    },
    'department': {
        'name': '部门/职位',
        'icon': 'OfficeBuilding',
        'module': PermissionCodes.MODULE_USER,
        'order': 91,
        'permissions': [
            (PermissionCodes.DEPARTMENT_VIEW, '查看部门', '查看部门列表'),
            (PermissionCodes.DEPARTMENT_CREATE, '创建部门', '创建部门'),
            (PermissionCodes.DEPARTMENT_EDIT, '编辑部门', '编辑部门信息'),
            (PermissionCodes.DEPARTMENT_DELETE, '删除部门', '删除部门'),
            (PermissionCodes.POSITION_VIEW, '查看职位', '查看职位'),
            (PermissionCodes.POSITION_CREATE, '创建职位', '创建职位'),
            (PermissionCodes.POSITION_EDIT, '编辑职位', '编辑职位'),
            (PermissionCodes.POSITION_DELETE, '删除职位', '删除职位'),
            (PermissionCodes.POSITION_ASSIGN, '分配职位', '为用户分配职位'),
        ]
    },
    'role': {
        'name': '角色/权限',
        'icon': 'Lock',
        'module': PermissionCodes.MODULE_USER,
        'order': 92,
        'permissions': [
            (PermissionCodes.ROLE_VIEW, '查看角色', '查看角色列表'),
            (PermissionCodes.ROLE_CREATE, '创建角色', '创建角色'),
            (PermissionCodes.ROLE_EDIT, '编辑角色', '编辑角色'),
            (PermissionCodes.ROLE_DELETE, '删除角色', '删除角色'),
            (PermissionCodes.ROLE_ASSIGN_PERMISSION, '分配权限', '为角色分配权限'),
            (PermissionCodes.PERMISSION_VIEW, '查看权限', '查看细分权限清单'),
        ]
    },
    'todo': {
        'name': '个人待办',
        'icon': 'Bell',
        'module': PermissionCodes.MODULE_TODO,
        'order': 100,
        'permissions': [
            (PermissionCodes.TODO_VIEW, '查看待办', '查看个人待办汇总'),
            (PermissionCodes.TODO_HANDLE, '处理待办', '审批/处理个人待办项'),
        ]
    },
    'plan': {
        'name': '个人计划',
        'icon': 'Calendar',
        'module': PermissionCodes.MODULE_PLAN,
        'order': 110,
        'permissions': [
            (PermissionCodes.PLAN_VIEW, '查看计划', '查看个人计划'),
            (PermissionCodes.PLAN_TASK_CREATE, '创建计划任务', '创建个人计划任务'),
            (PermissionCodes.PLAN_TASK_EDIT, '编辑计划任务', '编辑计划任务'),
            (PermissionCodes.PLAN_TASK_DELETE, '删除计划任务', '删除计划任务'),
            (PermissionCodes.PLAN_HABIT_MANAGE, '习惯打卡', '管理与打卡习惯'),
            (PermissionCodes.PLAN_FOCUS_MANAGE, '专注计时', '启动/结束专注'),
            (PermissionCodes.PLAN_TIME_BLOCK_MANAGE, '时间块', '管理时间块'),
            (PermissionCodes.PLAN_SETTINGS, '计划设置', '个人计划相关设置'),
        ]
    },
    'knowledge': {
        'name': '知识库',
        'icon': 'Reading',
        'module': PermissionCodes.MODULE_KNOWLEDGE,
        'order': 120,
        'permissions': [
            (PermissionCodes.KNOWLEDGE_VIEW, '查看知识', '查看知识库文章与分类'),
            (PermissionCodes.KNOWLEDGE_CATEGORY_MANAGE, '分类管理', '管理知识库分类'),
            (PermissionCodes.KNOWLEDGE_ARTICLE_CREATE, '创建文章', '创建知识库文章'),
            (PermissionCodes.KNOWLEDGE_ARTICLE_EDIT, '编辑文章', '编辑知识库文章'),
            (PermissionCodes.KNOWLEDGE_ARTICLE_DELETE, '删除文章', '删除知识库文章'),
            (PermissionCodes.KNOWLEDGE_ARTICLE_REVIEW, '审核文章', '审核/批准文章'),
            (PermissionCodes.KNOWLEDGE_ARTICLE_PUBLISH, '发布文章', '发布/取消发布'),
            (PermissionCodes.KNOWLEDGE_COMMENT, '评论', '在文章下评论'),
            (PermissionCodes.KNOWLEDGE_LIKE_FAVORITE, '点赞/收藏', '点赞或收藏文章'),
            (PermissionCodes.KNOWLEDGE_UPLOAD, '上传附件', '上传知识库附件'),
            (PermissionCodes.KNOWLEDGE_DOWNLOAD, '下载附件', '下载知识库附件'),
            (PermissionCodes.KNOWLEDGE_SHARE_MANAGE, '分享管理', '创建/管理外部分享链接'),
            (PermissionCodes.KNOWLEDGE_EXPORT, '导出', '导出文章内容'),
            (PermissionCodes.KNOWLEDGE_VIEW_STATISTICS, '查看统计', '查看知识库统计'),
        ]
    },
    'activity': {
        'name': '活动记录',
        'icon': 'Clock',
        'module': PermissionCodes.MODULE_ACTIVITY,
        'order': 130,
        'permissions': [
            (PermissionCodes.ACTIVITY_VIEW, '查看活动', '查看系统活动记录'),
            (PermissionCodes.ACTIVITY_CREATE, '创建活动', '手动记录活动'),
            (PermissionCodes.ACTIVITY_DELETE, '删除活动', '删除活动记录'),
            (PermissionCodes.ACTIVITY_EXPORT, '导出活动', '导出活动记录'),
        ]
    },
    'monitoring': {
        'name': '系统监控',
        'icon': 'Monitor',
        'module': PermissionCodes.MODULE_MONITORING,
        'order': 140,
        'permissions': [
            (PermissionCodes.MONITORING_VIEW, '查看监控', '查看系统监控总览'),
            (PermissionCodes.MONITORING_HEALTH, '健康检查', '查看服务健康状态'),
            (PermissionCodes.MONITORING_PERFORMANCE, '性能监控', '查看性能指标'),
            (PermissionCodes.MONITORING_DATABASE, '数据库监控', '查看数据库运行状态'),
            (PermissionCodes.MONITORING_LOGS, '查看日志', '查看系统/应用日志'),
            (PermissionCodes.MONITORING_ALERT_MANAGE, '告警管理', '处理告警事件'),
            (PermissionCodes.MONITORING_ALERT_RULE, '告警规则', '配置告警规则'),
        ]
    },
    'settings': {
        'name': '系统设置',
        'icon': 'Setting',
        'module': PermissionCodes.MODULE_SETTINGS,
        'order': 150,
        'permissions': [
            (PermissionCodes.SETTINGS_VIEW, '查看设置', '查看系统设置'),
            (PermissionCodes.SETTINGS_EDIT, '编辑设置', '修改系统设置'),
            (PermissionCodes.SETTINGS_NOTIFICATION, '通知设置', '配置通知参数'),
            (PermissionCodes.SETTINGS_BACKUP, '数据备份', '备份/恢复数据库'),
            (PermissionCodes.SETTINGS_LOG_MANAGE, '日志管理', '管理/清理系统日志'),
        ]
    },
    'audit': {
        'name': '审计日志',
        'icon': 'Notebook',
        'module': PermissionCodes.MODULE_SETTINGS,
        'order': 151,
        'permissions': [
            (PermissionCodes.AUDIT_VIEW, '查看审计', '查看操作审计日志'),
            (PermissionCodes.AUDIT_EXPORT, '导出审计', '导出审计日志'),
        ]
    },
    'data': {
        'name': '统计/导入导出',
        'icon': 'DataAnalysis',
        'module': None,
        'order': 200,
        'permissions': [
            (PermissionCodes.STATISTICS_VIEW, '查看统计', '查看跨模块统计'),
            (PermissionCodes.DATA_EXPORT, '数据导出', '跨模块数据导出'),
            (PermissionCodes.DATA_IMPORT, '数据导入', '跨模块数据导入'),
        ]
    },
    'notification': {
        'name': '系统通知',
        'icon': 'Bell',
        'module': None,
        'order': 210,
        'permissions': [
            (PermissionCodes.NOTIFICATION_VIEW, '查看通知', '查看系统通知'),
            (PermissionCodes.NOTIFICATION_SEND, '发送通知', '向用户发送系统通知'),
        ]
    },
    'dev': {
        'name': '开发/代码',
        'icon': 'Cpu',
        'module': None,
        'order': 220,
        'permissions': [
            (PermissionCodes.CODE_SUBMIT, '代码提交', '提交/关联代码提交'),
        ]
    },
    'collab': {
        'name': '我的部门',
        'icon': 'OfficeBuilding',
        'module': PermissionCodes.MODULE_DEPARTMENT,
        'order': 230,
        'permissions': [
            (PermissionCodes.DEPARTMENT_MEMBER_VIEW, '查看部门成员', '查看本部门其他成员信息'),
        ]
    },
    'module_perm': {
        'name': '模块权限管理',
        'icon': 'Key',
        'module': None,
        'order': 250,
        'permissions': [
            (PermissionCodes.MODULE_PERM_VIEW, '查看模块权限', '查看用户可见的大功能模块'),
            (PermissionCodes.MODULE_PERM_EDIT, '编辑模块/细分权限', '配置用户可见模块、额外/限制权限'),
            (PermissionCodes.MODULE_PERM_RESET, '重置为默认', '将用户的模块和细分权限重置为系统默认'),
            (PermissionCodes.MODULE_PERM_VIEW_ALL, '查看全员概览', '查看所有用户的模块权限概览'),
        ]
    },
    'template': {
        'name': '权限模板',
        'icon': 'CollectionTag',
        'module': None,
        'order': 260,
        'permissions': [
            (PermissionCodes.TEMPLATE_VIEW, '查看模板', '查看权限模板列表与详情'),
            (PermissionCodes.TEMPLATE_CREATE, '新建模板', '创建新的权限模板'),
            (PermissionCodes.TEMPLATE_EDIT, '编辑模板', '编辑权限模板'),
            (PermissionCodes.TEMPLATE_DELETE, '删除模板', '删除自定义权限模板'),
            (PermissionCodes.TEMPLATE_APPLY, '应用模板', '把模板一键应用到一个或多个用户'),
        ]
    },
}


def get_permission_categories():
    """获取按模块分组的细分权限清单，供「模块权限管理」页面使用。

    返回值格式：{
        category_key: {
            'name': 分类名,
            'icon': 图标,
            'module': 所属一级模块权限码,
            'order': 排序,
            'permissions': [{ 'code': ..., 'name': ..., 'description': ... }, ...]
        },
        ...
    }
    """
    result = {}
    for key, cat in PERMISSION_CATEGORIES.items():
        result[key] = {
            'name': cat['name'],
            'icon': cat.get('icon', ''),
            'module': cat.get('module'),
            'order': cat.get('order', 999),
            'permissions': [
                {'code': code, 'name': name, 'description': desc}
                for code, name, desc in cat['permissions']
            ]
        }
    return result


def get_all_permission_codes():
    """获取全部细分权限编码集合（用于校验 / 统计）"""
    codes = set()
    for cat in PERMISSION_CATEGORIES.values():
        for code, _, _ in cat['permissions']:
            codes.add(code)
    return codes


