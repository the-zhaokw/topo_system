import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

// 路由组件
const Dashboard = () => import('@/views/Dashboard.vue')
const BugList = () => import('@/views/BugList.vue')
const BugDetail = () => import('@/views/BugDetail.vue')
const BugForm = () => import('@/views/BugForm.vue')
const ProjectList = () => import('@/views/ProjectList.vue')
const ProjectDetail = () => import('@/views/ProjectDetail.vue')
const ProjectForm = () => import('@/views/ProjectForm.vue')
const UserList = () => import('@/views/UserList.vue')
const UserDetail = () => import('@/views/UserDetail.vue')
const UserProfile = () => import('@/views/UserProfile.vue')
const TaskList = () => import('@/views/TaskList.vue')
const TaskDetail = () => import('@/views/TaskDetail.vue')
const Login = () => import('@/views/Login.vue')
const NotificationList = () => import('@/views/NotificationList.vue')
const AttendanceList = () => import('@/views/AttendanceList.vue')
const AttendanceDetail = () => import('@/views/AttendanceDetail.vue')
const ShiftManagement = () => import('@/views/ShiftManagement.vue')
const AttendanceReport = () => import('@/views/AttendanceReport.vue')
const LeaveApplication = () => import('@/views/LeaveApplication.vue')
const LeaveApproval = () => import('@/views/LeaveApproval.vue')
const OvertimeApproval = () => import('@/views/OvertimeApproval.vue')
const OvertimeApplication = () => import('@/views/OvertimeApplication.vue')

// 物料管理组件
const MaterialCategoryList = () => import('@/views/MaterialCategoryList.vue')
const MaterialList = () => import('@/views/MaterialList.vue')
const WarehouseList = () => import('@/views/WarehouseList.vue')
const InventoryList = () => import('@/views/InventoryList.vue')
const LocationList = () => import('@/views/LocationList.vue')
const SerialNumberList = () => import('@/views/SerialNumberList.vue')
const MaterialRelationshipList = () => import('@/views/MaterialRelationshipList.vue')
const MaterialReport = () => import('@/views/MaterialReport.vue')

// 合同管理组件
const ContractList = () => import('@/views/ContractList.vue')
const ContractDetail = () => import('@/views/ContractDetail.vue')
const ContractStatistics = () => import('@/views/ContractStatistics.vue')

// 统计报表组件
const BugStatistics = () => import('@/views/BugStatistics.vue')
const ProjectStatistics = () => import('@/views/ProjectStatistics.vue')
const CustomReport = () => import('@/views/CustomReport.vue')
const SystemSettings = () => import('@/views/SystemSettings.vue')
const ProjectBugList = () => import('@/views/ProjectBugList.vue')

// 活动记录组件
const ActivityList = () => import('@/views/ActivityList.vue')

// 系统监控组件
const MonitoringList = () => import('@/views/MonitoringList.vue')

// 测试管理组件
const TestSuiteList = () => import('@/views/TestSuiteList.vue')
const TestSuiteDetail = () => import('@/views/TestSuiteDetail.vue')
const TestCaseList = () => import('@/views/TestCaseList.vue')
const TestCaseDetail = () => import('@/views/TestCaseDetail.vue')
const TestExecutionList = () => import('@/views/TestExecutionList.vue')
const TestReport = () => import('@/views/TestReport.vue')
const TestDashboard = () => import('@/views/TestDashboard.vue')

// 需求管理组件
const RequirementDocumentList = () => import('@/views/RequirementDocumentList.vue')
const RequirementDocumentDetail = () => import('@/views/RequirementDocumentDetail.vue')
const RequirementTraceMatrix = () => import('@/views/RequirementTraceMatrix.vue')
const RequirementDashboard = () => import('@/views/RequirementDashboard.vue')

// 工作统计详情组件
const WorkStatisticsDetail = () => import('@/views/WorkStatisticsDetail.vue')

// 工作日志组件
const WorkLogList = () => import('@/views/WorkLogList.vue')

// 项目日志组件
const ProjectLogList = () => import('@/views/ProjectLogList.vue')

// 个人待办事项组件
const MyTodos = () => import('@/views/MyTodos.vue')

const MyDepartment = () => import('@/views/MyDepartment.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/work-statistics',
    name: 'WorkStatisticsDetail',
    component: WorkStatisticsDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/work-logs',
    name: 'WorkLogList',
    component: WorkLogList,
    meta: { requiresAuth: true }
  },
  {
    path: '/my-todos',
    name: 'MyTodos',
    component: MyTodos,
    meta: { requiresAuth: true }
  },
  {
    path: '/my-department',
    name: 'MyDepartment',
    component: MyDepartment,
    meta: { requiresAuth: true }
  },
  // Bug管理模块 - 嵌套路由
  {
    path: '/bugs',
    name: 'BugManagement',
    redirect: '/bugs/list',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'list',
        name: 'BugList',
        component: BugList,
        meta: { requiresAuth: true }
      },
      {
        path: 'new',
        name: 'BugCreate',
        component: BugForm,
        meta: { requiresAuth: true }
      },
      {
        path: 'statistics',
        name: 'BugStatistics',
        component: BugStatistics,
        meta: { requiresAuth: true }
      },
      {
        path: ':id',
        name: 'BugDetail',
        component: BugDetail,
        meta: { requiresAuth: true }
      },
      {
        path: ':id/edit',
        name: 'BugEdit',
        component: BugForm,
        meta: { requiresAuth: true }
      }
    ]
  },
  // 项目管理模块 - 嵌套路由
  {
    path: '/projects',
    name: 'ProjectManagement',
    redirect: '/projects/list',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'list',
        name: 'ProjectList',
        component: ProjectList,
        meta: { requiresAuth: true }
      },
      {
        path: 'new',
        name: 'ProjectCreate',
        component: ProjectForm,
        meta: { requiresAuth: true }
      },
      {
        path: 'statistics',
        name: 'ProjectStatistics',
        component: ProjectStatistics,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/bugs',
        name: 'ProjectBugList',
        component: ProjectBugList,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/bugs/new',
        name: 'ProjectBugCreate',
        component: BugForm,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/bugs/:id',
        name: 'ProjectBugDetail',
        component: BugDetail,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/bugs/:id/edit',
        name: 'ProjectBugEdit',
        component: BugForm,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/logs',
        name: 'ProjectLogList',
        component: ProjectLogList,
        meta: { requiresAuth: true }
      },
      {
        path: ':id',
        name: 'ProjectDetail',
        component: ProjectDetail,
        meta: { requiresAuth: true }
      },
      {
        path: ':id/edit',
        name: 'ProjectEdit',
        component: ProjectForm,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/requirements',
        name: 'ProjectRequirementList',
        component: RequirementDocumentList,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/requirements/dashboard',
        name: 'ProjectRequirementDashboard',
        component: RequirementDashboard,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/requirements/:docId',
        name: 'ProjectRequirementDetail',
        component: RequirementDocumentDetail,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/requirements/:docId/trace-matrix',
        name: 'ProjectRequirementTraceMatrix',
        component: RequirementTraceMatrix,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/tests/suites',
        name: 'ProjectTestSuiteList',
        component: TestSuiteList,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/tests/suites/:suiteId',
        name: 'ProjectTestSuiteDetail',
        component: TestSuiteDetail,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/tests/suites/:suiteId/cases',
        name: 'ProjectTestCaseList',
        component: TestCaseList,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/tests/suites/:suiteId/cases/new',
        name: 'ProjectTestCaseCreate',
        component: TestCaseDetail,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/tests/suites/:suiteId/cases/:caseId',
        name: 'ProjectTestCaseDetail',
        component: TestCaseDetail,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/tests/suites/:suiteId/cases/:caseId/edit',
        name: 'ProjectTestCaseEdit',
        component: TestCaseDetail,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/tests/executions',
        name: 'ProjectTestExecutionList',
        component: TestExecutionList,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/tests/executions/:executionId/report',
        name: 'ProjectTestReport',
        component: TestReport,
        meta: { requiresAuth: true }
      },
      {
        path: ':projectId/tests/dashboard',
        name: 'ProjectTestDashboard',
        component: TestDashboard,
        meta: { requiresAuth: true }
      },
      {
        path: 'custom-report',
        name: 'ProjectCustomReport',
        component: CustomReport,
        meta: { requiresAuth: true }
      }
    ]
  },
  // 考勤管理模块 - 嵌套路由
  {
    path: '/attendance',
    name: 'AttendanceManagement',
    redirect: '/attendance/records',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'records',
        name: 'AttendanceList',
        component: AttendanceList,
        meta: { requiresAuth: true }
      },
      {
        path: 'records/:id',
        name: 'AttendanceDetail',
        component: AttendanceDetail,
        meta: { requiresAuth: true }
      },
      {
        path: 'shifts',
        name: 'ShiftManagement',
        component: ShiftManagement,
        meta: { requiresAuth: true }
      },
      {
        path: 'reports',
        name: 'AttendanceReport',
        component: AttendanceReport,
        meta: { requiresAuth: true }
      },
      {
        path: 'leave-application',
        name: 'LeaveApplication',
        component: LeaveApplication,
        meta: { requiresAuth: true }
      },
      {
        path: 'overtime-application',
        name: 'OvertimeApplication',
        component: OvertimeApplication,
        meta: { requiresAuth: true }
      },
      {
        path: 'leave-approval',
        name: 'LeaveApproval',
        component: LeaveApproval,
        meta: { requiresAuth: true }
      },
      {
        path: 'overtime-approval',
        name: 'OvertimeApproval',
        component: OvertimeApproval,
        meta: { requiresAuth: true }
      }
    ]
  },
  // 用户管理模块 - 嵌套路由
  {
    path: '/users',
    name: 'UserManagement',
    redirect: '/users/list',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'list',
        name: 'UserList',
        component: UserList,
        meta: { requiresAuth: true }
      },
      {
        path: ':id',
        name: 'UserDetail',
        component: UserDetail,
        meta: { requiresAuth: true }
      }
    ]
  },
  // 个人设置
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfile,
    meta: { requiresAuth: true }
  },
  // 通知列表页面
  {
    path: '/notifications',
    name: 'NotificationList',
    component: NotificationList,
    meta: { requiresAuth: true }
  },
  // 任务管理模块 - 嵌套路由
  {
    path: '/tasks',
    name: 'TaskManagement',
    redirect: '/tasks/list',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'list',
        name: 'TaskList',
        component: TaskList,
        meta: { requiresAuth: true }
      },
      {
        path: ':id',
        name: 'TaskDetail',
        component: TaskDetail,
        meta: { requiresAuth: true }
      }
    ]
  },
  // 物料管理模块 - 嵌套路由
  {
    path: '/materials',
    name: 'MaterialManagement',
    redirect: '/materials/list',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'categories',
        name: 'MaterialCategoryList',
        component: MaterialCategoryList,
        meta: { requiresAuth: true }
      },
      {
        path: 'list',
        name: 'MaterialList',
        component: MaterialList,
        meta: { requiresAuth: true }
      },
      {
        path: 'warehouses',
        name: 'WarehouseList',
        component: WarehouseList,
        meta: { requiresAuth: true }
      },
      {
        path: 'inventory',
        name: 'InventoryList',
        component: InventoryList,
        meta: { requiresAuth: true }
      },
      {
        path: 'locations',
        name: 'LocationList',
        component: LocationList,
        meta: { requiresAuth: true }
      },
      {
        path: 'serial-numbers',
        name: 'SerialNumberList',
        component: SerialNumberList,
        meta: { requiresAuth: true }
      },
      {
        path: 'relationships',
        name: 'MaterialRelationshipList',
        component: MaterialRelationshipList,
        meta: { requiresAuth: true }
      },
      {
        path: 'reports',
        name: 'MaterialReport',
        component: MaterialReport,
        meta: { requiresAuth: true }
      }
    ]
  },
  // 合同管理模块 - 嵌套路由
  {
    path: '/contracts',
    name: 'ContractManagement',
    redirect: '/contracts/list',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'list',
        name: 'ContractList',
        component: ContractList,
        meta: { requiresAuth: true }
      },
      {
        path: 'statistics',
        name: 'ContractStatistics',
        component: ContractStatistics,
        meta: { requiresAuth: true }
      },
      {
        path: ':id',
        name: 'ContractDetail',
        component: ContractDetail,
        meta: { requiresAuth: true }
      }
    ]
  },
  // 统计报表模块 - 嵌套路由
  {
    path: '/reports',
    name: 'ReportManagement',
    redirect: '/reports/bug-statistics',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'bug-statistics',
        name: 'ReportBugStatistics',
        component: BugStatistics,
        meta: { requiresAuth: true }
      }
    ]
  },
  // 活动记录模块
  {
    path: '/activities',
    name: 'ActivityList',
    component: ActivityList,
    meta: { requiresAuth: true }
  },
  // 知识库模块（新版）
  {
    path: '/knowledge',
    name: 'KnowledgeBase',
    component: () => import('@/views/KnowledgeBase.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/knowledge/articles/:id',
    name: 'KnowledgeArticleDetail',
    component: () => import('@/views/KnowledgeListFinal.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/knowledge/share/:token',
    name: 'KnowledgeShare',
    component: () => import('@/views/KnowledgeShare.vue'),
    meta: { title: '知识分享', public: true }
  },
  // 系统监控模块
  {
    path: '/monitoring',
    name: 'MonitoringList',
    component: MonitoringList,
    meta: { requiresAuth: true, allowedRoles: ['admin', 'manager'] }
  },
  // 系统设置模块
  {
    path: '/settings',
    name: 'SystemSettings',
    component: SystemSettings,
    meta: { requiresAuth: true, allowedRoles: ['admin', 'manager'] }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  handleRoute(to, next, userStore)
})

// 权限配置
const permissionConfig = {
  '/users': {
    allowedRoles: ['admin', 'manager'],
    errorMessage: '权限不足，只有管理员可以访问用户管理页面'
  },

  '/attendance': {
    allowedRoles: ['admin', 'manager', 'project_manager', 'hr', 'department_manager', 'software_engineer', 'test_engineer'],
    errorMessage: '权限不足，无法访问考勤管理页面'
  },

  '/materials': {
    allowedRoles: ['admin', 'manager', 'project_manager'],
    errorMessage: '权限不足，无法访问物料管理页面'
  },

  '/contracts': {
    allowedRoles: ['admin', 'manager', 'project_manager'],
    errorMessage: '权限不足，无法访问合同管理页面'
  },

  '/reports': {
    allowedRoles: ['admin', 'manager', 'project_manager', 'hr', 'department_manager'],
    errorMessage: '权限不足，无法访问统计报表页面'
  }
}

// 检查用户是否有权限访问指定路径
function hasPermission(path, userRole) {
  for (const [routePath, config] of Object.entries(permissionConfig)) {
    if (path.startsWith(routePath)) {
      return config.allowedRoles.includes(userRole)
    }
  }
  // 默认允许访问
  return true
}

// 获取权限错误信息
function getPermissionErrorMessage(path) {
  for (const [routePath, config] of Object.entries(permissionConfig)) {
    if (path.startsWith(routePath)) {
      return config.errorMessage
    }
  }
  return '权限不足，无法访问该页面'
}

function handleRoute(to, next, userStore) {
  // 检查是否有token存在（即使currentUser还没加载完成）
  const hasToken = !!localStorage.getItem('token')
  
  // 如果有token但用户信息还没加载完成，需要等待
  if (hasToken && !userStore.currentUser && userStore.userLoading) {
    const waitForUserLoad = () => {
      if (!userStore.userLoading) {
        continueHandleRoute(to, next, userStore)
      } else {
        setTimeout(waitForUserLoad, 50)
      }
    }
    waitForUserLoad()
    return
  }
  
  continueHandleRoute(to, next, userStore)
}

function continueHandleRoute(to, next, userStore) {
  // 对于登录页面，我们总是允许访问，不做自动重定向
  // 这确保即使用户已登录，也能看到登录页面（比如想切换账号）
  // 只有当用户明确点击登录按钮后才会跳转到dashboard
  if (to.path === '/login') {
    // 如果用户已经认证，可以显示登录页面但允许用户手动导航到其他页面
    if (userStore.isAuthenticated) {
      // 用户已登录，允许访问登录页面（比如用户想切换账号）
      next()
    } else {
      // 用户未登录，允许访问登录页面
      next()
    }
    return
  }
  
  // 对于需要认证的页面，检查用户是否已认证
  if (!userStore.isAuthenticated) {
    // 如果用户未认证，则重定向到登录页面
    next('/login')
    return
  }
  
  // 检查用户权限
  const userRole = userStore.currentUser?.role

  // 首先检查路由的meta.allowedRoles配置
  if (to.meta?.allowedRoles) {
    if (!to.meta.allowedRoles.includes(userRole)) {
      next('/dashboard')
      setTimeout(() => {
        import('element-plus').then(({ ElMessage }) => {
          ElMessage.error('权限不足，无法访问该页面')
        })
      }, 100)
      return
    }
  } else if (!hasPermission(to.path, userRole)) {
    // 无权限用户重定向到首页并显示权限不足提示
    next('/dashboard')
    setTimeout(() => {
      import('element-plus').then(({ ElMessage }) => {
        ElMessage.error(getPermissionErrorMessage(to.path))
      })
    }, 100)
    return
  }
  
  // 权限检查通过，允许访问
  next()
}

export default router