import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,  // 增加超时时间到30秒
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 从localStorage获取token，避免在组件外部使用useUserStore()
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 如果是FormData，删除默认的Content-Type，让浏览器自动处理multipart/form-data
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 如果是 blob 类型响应，直接返回完整响应对象
    if (response.config.responseType === 'blob') {
      return response
    }
    
    const data = response.data

    // 处理后端返回的嵌套格式 { success: true, message: "xxx", data: {...} }
    if (typeof data === 'object' && data !== null) {
      // 如果响应包含data字段且data不为空，则返回data字段的值
      if ('data' in data && data.data !== null && data.data !== undefined) {
        return data.data
      }
      // 否则返回原始数据（如删除操作返回的 { success, message, data: null }）
      return data
    }
    
    return data
  },
  (error) => {
    const status = error.response?.status;
    const errorData = error.response?.data;
    
    if (status === 401) {
      const isAuthError = errorData?.code === 'AUTHENTICATION_ERROR';
      
      if (isAuthError) {
        // 认证错误不显示消息，由组件处理
      } else {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        ElMessage.error('登录已过期，请重新登录')
        window.location.href = '/login'
      }
    } else if (error.response?.status === 403) {
      ElMessage.error(error.response?.data?.error || '权限不足，无法执行此操作')
    } else if (error.response?.status === 404) {
      ElMessage.error(error.response?.data?.error || '请求的资源不存在')
    } else if (error.response?.status === 400) {
      // 更详细的400错误处理
      const errorData = error.response?.data
      let errorMessage = '请求参数错误'
      
      if (errorData) {
        if (errorData.error) {
          errorMessage = errorData.error
        } else if (errorData.message) {
          errorMessage = errorData.message
        }
        
        // 如果是验证错误，显示更详细的信息
        if (errorData.code === 'VALIDATION_ERROR' && errorData.details) {
          errorMessage += '\n' + errorData.details
        }
      }
      
      ElMessage.error({
        message: errorMessage,
        duration: 5000,
        showClose: true
      })
    } else if (error.response?.status === 500) {
      ElMessage.error(error.response?.data?.error || '服务器内部错误，请稍后重试')
    } else {
      ElMessage.error(error.response?.data?.error || error.response?.data?.message || '请求失败，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

// API服务对象
export const apiService = {
  // 认证相关
  auth: {
    login: (credentials) => api.post('/auth/login', credentials),
    logout: () => api.post('/auth/logout'),
    register: (userData) => api.post('/auth/register', userData),
    getCurrentUser: () => api.get('/auth/me'),
    updateProfile: (profileData) => api.put('/auth/me', profileData),
    changePassword: (passwordData) => api.put('/auth/change-password', passwordData),
    uploadAvatar: (formData) => api.post('/avatar/upload', formData),
    removeAvatar: () => api.delete('/avatar/remove')
  },
  
  // 缺陷管理
  bugs: {
    getList: (params = {}) => api.get('/bugs', { params }),
    getById: (id) => api.get(`/bugs/${id}`),
    create: (bugData) => api.post('/bugs', bugData),
    update: (id, bugData) => api.put(`/bugs/${id}`, bugData),
    delete: (id) => api.delete(`/bugs/${id}`),
    batchDelete: (ids) => api.post('/bugs/batch-delete', { bug_ids: ids }),
    batchUpdate: (bugIds, updates) => api.put('/bugs/batch-update', { bug_ids: bugIds, updates }),
    updateStatus: (id, status) => api.put(`/bugs/${id}/status`, { status }),
    assignBug: (id, assigneeId) => api.put(`/bugs/${id}/assign`, { assignee_id: assigneeId }),
    getComments: (id) => api.get(`/bugs/${id}/comments`),
    addComment: (id, commentData) => api.post(`/bugs/${id}/comments`, commentData),
    uploadAttachment: (id, fileData) => api.post(`/bugs/${id}/attachments/upload`, fileData, {
      headers: { 'Content-Type': undefined }
    }),
    getAttachments: (id) => api.get(`/bugs/${id}/attachments`),
    transitionBug: (id, data) => api.post(`/bugs/${id}/transition`, data),
    downloadAttachment: (id, attachmentId) => api.get(`/bugs/${id}/attachments/${attachmentId}`, { responseType: 'blob' }),
    getAttachmentUrl: (id, attachmentId) => api.get(`/bugs/${id}/attachments/${attachmentId}`, { responseType: 'blob' }),
    deleteAttachment: (id, attachmentId) => api.delete(`/bugs/${id}/attachments/${attachmentId}`),
    getStatistics: (projectId) => api.get('/bugs/statistics', { params: { project_id: projectId } }),
    export: (params = {}) => api.get('/bugs/export', { params, responseType: 'blob' }),
    import: (fileData) => api.post('/bugs/import', fileData)
  },
  
  // 项目管理
  projects: {
    getList: (params = {}) => api.get('/projects/', { params }),
    getById: (id) => api.get(`/projects/${id}/`),
    create: (projectData) => api.post('/projects/', projectData),
    update: (id, projectData) => api.put(`/projects/${id}/`, projectData),
    delete: (id) => api.delete(`/projects/${id}/`),
    getProjectMembers: (projectId) => api.get(`/projects/${projectId}/members`),
    addProjectMember: (projectId, memberData) => api.post(`/projects/${projectId}/members/`, memberData),
    updateProjectMember: (projectId, memberId, memberData) => api.put(`/projects/${projectId}/members/${memberId}/`, memberData),
    removeProjectMember: (projectId, memberId) => api.delete(`/projects/${projectId}/members/${memberId}/`),
    getProjectStatistics: (projectId) => api.get(`/statistics/projects/${projectId}/`),
    export: (format = 'excel', params = {}) => {
      const exportData = {
        export_type: 'projects',
        format: format,
        ...params
      };
      return api.post('/statistics/export', exportData, {
        responseType: 'blob'
      });
    }
  },
  
  // 用户管理
  users: {
    getList: (params = {}) => api.get('/users/', { params }),
    getById: (id) => api.get(`/users/${id}/`),
    create: (userData) => api.post('/users/', userData),
    update: (id, userData) => api.put(`/users/${id}/`, userData),
    delete: (id) => api.delete(`/users/${id}/`),
    batchDelete: (ids) => api.post('/users/batch-delete/', { ids }),
    search: (keyword) => api.get('/users/search/', { params: { keyword } }),
    getApprovers: () => api.get('/users/approvers/'),
    exportUsers: (format = 'xlsx') => api.get(`/users/export/${format}`, {
      responseType: 'blob'
    }),
    importUsers: (fileData) => api.post('/users/import', fileData),
    resetPassword: (id, passwordData) => api.post(`/users/${id}/reset-password`, passwordData),
    getUserHome: (id) => api.get(`/users/${id}/home`),
    getDepartments: () => api.get('/users/departments'),
    getDepartmentMembers: (departmentName, params = {}) => api.get(`/users/department/${encodeURIComponent(departmentName)}/members`, { params }),
    createDepartment: (departmentName) => api.post('/users/departments', { department: departmentName }),
    updateDepartment: (oldName, newName) => api.put(`/users/departments/${encodeURIComponent(oldName)}`, { department: newName }),
    deleteDepartment: (departmentName) => api.delete(`/users/departments/${encodeURIComponent(departmentName)}`),
    batchAddDepartmentMembers: (departmentName, userIds) => api.post(`/users/departments/${encodeURIComponent(departmentName)}/members/batch-add`, { user_ids: userIds }),
    batchRemoveDepartmentMembers: (departmentName, userIds) => api.post(`/users/departments/${encodeURIComponent(departmentName)}/members/batch-remove`, { user_ids: userIds }),
    getPositions: () => api.get('/users/positions'),
    getPositionMembers: (positionName, params = {}) => api.get(`/users/position/${encodeURIComponent(positionName)}/members`, { params }),
    createPosition: (positionName) => api.post('/users/positions', { position: positionName }),
    updatePosition: (oldName, newName) => api.put(`/users/positions/${encodeURIComponent(oldName)}`, { position: newName }),
    deletePosition: (positionName) => api.delete(`/users/positions/${encodeURIComponent(positionName)}`),
    getAllPermissions: () => api.get('/users/permissions'),
    getUserPermissions: (userId) => api.get(`/users/${userId}/permissions`),
    updateUserPermissions: (userId, permissionsData) => api.put(`/users/${userId}/permissions`, permissionsData),
    batchUpdatePosition: (userIds, position) => api.post('/users/batch-update-position', { user_ids: userIds, position }),
    getPositions: () => api.get('/users/positions'),
    getMyDepartment: (params = {}) => api.get('/users/my-department', { params })
  },

  // 通用模块
  common: {
    uploadFile: (formData) => api.post('/common/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    getFileUrl: (fileId) => api.get(`/common/files/${fileId}`),
    deleteFile: (fileId) => api.delete(`/common/files/${fileId}`)
  },

  // 统计分析
  statistics: {
    getDashboardData: () => api.get('/statistics/dashboard'),
    getTaskStatistics: (params = {}) => api.get('/statistics/tasks', { params }),
    getBugStatistics: (params = {}) => api.get('/statistics/bugs', { params }),
    getUserStatistics: (params = {}) => api.get('/statistics/users', { params }),
    getProjectStatistics: (params = {}) => api.get('/statistics/projects', { params }),
    exportData: (dataType, params = {}) => api.get(`/statistics/export/${dataType}`, { params })
  },
  
  // 活动记录
  activities: {
    getList: (params = {}) => api.get('/activities', { params }),
    getById: (id) => api.get(`/activities/${id}`),
    getRecent: () => api.get('/activities/recent'),
    getByResource: (resourceType, resourceId, params = {}) => api.get(`/activities/${resourceType}/${resourceId}`, { params }),
    create: (activityData) => api.post('/activities', activityData),
    update: (id, activityData) => api.put(`/activities/${id}`, activityData),
    delete: (id) => api.delete(`/activities/${id}`)
  },

  // 工作日志
  workLogs: {
    getList: (params = {}) => api.get('/work-logs', { params }),
    getById: (id) => api.get(`/work-logs/${id}`),
    create: (logData) => api.post('/work-logs', logData),
    update: (id, logData) => api.put(`/work-logs/${id}`, logData),
    delete: (id) => api.delete(`/work-logs/${id}`),
    getMyLogs: (params = {}) => api.get('/work-logs/my', { params }),
    getStats: (params = {}) => api.get('/work-logs/stats', { params })
  },

  // 项目日志
  projectLogs: {
    getList: (params = {}) => api.get('/project-logs', { params }),
    getById: (id) => api.get(`/project-logs/${id}`),
    create: (logData) => api.post('/project-logs', logData),
    update: (id, logData) => api.put(`/project-logs/${id}`, logData),
    delete: (id) => api.delete(`/project-logs/${id}`),
    getStats: (params = {}) => api.get('/project-logs/stats', { params })
  },

  // 通知管理
  notifications: {
    getList: (params = {}) => api.get('/notifications', { params }),
    getUnreadCount: () => api.get('/notifications/unread-count'),
    markAsRead: (notificationId) => api.put(`/notifications/${notificationId}/read`),
    markAllAsRead: () => api.put('/notifications/read-all'),
    delete: (notificationId) => api.delete(`/notifications/${notificationId}`),
    sendTest: () => api.post('/notifications/test'),
    getTypeStats: () => api.get('/notifications/type-stats')
  },

  // 需求管理相关
  requirements: {
    getSets: (projectId, params = {}) => api.get(`/projects/${projectId}/requirement-sets`, { params }),
    getSetById: (id) => api.get(`/requirement-sets/${id}`),
    createSet: (projectId, setData) => api.post(`/projects/${projectId}/requirement-sets`, setData),
    updateSet: (id, setData) => api.put(`/requirement-sets/${id}`, setData),
    deleteSet: (id) => api.delete(`/requirement-sets/${id}`),

    getItems: (setId, params = {}) => api.get(`/requirement-sets/${setId}/items`, { params }),
    getItemById: (id) => api.get(`/requirements/${id}`),
    createItem: (setId, itemData) => api.post(`/requirement-sets/${setId}/items`, itemData),
    updateItem: (id, itemData) => api.put(`/requirements/${id}`, itemData),
    deleteItem: (id) => api.delete(`/requirements/${id}`)
  },

  // 需求文档相关
  requirementDocuments: {
    getList: (projectId, params = {}) => api.get(`/projects/${projectId}/requirement-documents`, { params }),
    getById: (docId) => api.get(`/requirement-documents/${docId}`),
    create: (projectId, docData) => api.post(`/projects/${projectId}/requirement-documents`, docData),
    update: (docId, docData) => api.put(`/requirement-documents/${docId}`, docData),
    delete: (docId) => api.delete(`/requirement-documents/${docId}`),
    export: (docId, format = 'markdown') => api.get(`/requirement-documents/${docId}/export`, {
      params: { format },
      responseType: 'blob'
    }),
    getVersions: (docId) => api.get(`/requirement-documents/${docId}/versions`),
    compareVersions: (docId, params) => api.get(`/requirement-documents/${docId}/compare-versions`, { params }),
    rollback: (docId, version) => api.post(`/requirement-documents/${docId}/rollback/${version}`),
    createVersion: (docId, data) => api.post(`/requirement-documents/${docId}/create-version`, data),
    changeStatus: (docId, status) => api.post(`/requirement-documents/${docId}/change-status`, { status }),
    getComments: (docId) => api.get(`/requirement-documents/${docId}/comments`),
    addComment: (docId, commentData) => api.post(`/requirement-documents/${docId}/comments`, commentData)
  },

  // 需求条目相关
  requirementItems: {
    getById: (itemId) => api.get(`/requirement-items/${itemId}`),
    create: (docId, itemData) => api.post(`/requirement-documents/${docId}/items`, itemData),
    update: (itemId, itemData) => api.put(`/requirement-items/${itemId}`, itemData),
    delete: (itemId) => api.delete(`/requirement-items/${itemId}`),
    copy: (itemId, data) => api.post(`/requirement-items/${itemId}/copy`, data),
    move: (itemId, data) => api.post(`/requirement-items/${itemId}/move`, data),
    changeStatus: (itemId, status) => api.post(`/requirement-items/${itemId}/change-status`, { status }),
    getHistory: (itemId) => api.get(`/requirement-items/${itemId}/history`),
    getImpactAnalysis: (itemId) => api.get(`/requirement-items/${itemId}/impact-analysis`),
    getComments: (itemId) => api.get(`/requirement-items/${itemId}/comments`),
    addComment: (itemId, commentData) => api.post(`/requirement-items/${itemId}/comments`, commentData),
    submitReview: (itemId, reviewData) => api.post(`/requirement-items/${itemId}/review`, reviewData),
    getLinks: (itemId) => api.get(`/requirement-items/${itemId}/links`)
  },

  // 需求评审相关
  requirementReviews: {
    initiate: (docId, reviewData) => api.post(`/requirement-documents/${docId}/review`, reviewData),
    getReviewList: (docId) => api.get(`/requirement-documents/${docId}/reviews`),
    getReviewDetail: (reviewId) => api.get(`/requirement-reviews/${reviewId}`),
    submitReview: (reviewId, reviewData) => api.post(`/requirement-reviews/${reviewId}/submit`, reviewData)
  },

  // 需求跟踪矩阵相关
  requirementTrace: {
    getMatrix: (docId, params = {}) => api.get(`/requirement-documents/${docId}/trace-matrix`, { params }),
    getCoverage: (projectId) => api.get(`/projects/${projectId}/requirement-coverage`),
    createLink: (linkData) => api.post('/requirement-links', linkData),
    deleteLink: (linkId) => api.delete(`/requirement-links/${linkId}`),
    getLinkTypes: () => api.get('/requirement-links/types')
  },

  // 需求统计相关
  requirementStatistics: {
    getProjectStatistics: (projectId) => api.get(`/projects/${projectId}/requirement-statistics`),
    getDocumentStatistics: (docId) => api.get(`/requirement-documents/${docId}/statistics`),
    getMyTodos: () => api.get('/my/requirement-todos'),
    getTrend: (projectId, params = {}) => api.get(`/projects/${projectId}/requirement-trend`, { params })
  },

  // 个人待办事项
  todos: {
    getSummary: () => api.get('/todos/summary'),
    getAll: (params = {}) => api.get('/todos/all', { params }),
    getApprovals: (params = {}) => api.get('/todos/approvals', { params }),
    getBugs: (params = {}) => api.get('/todos/bugs', { params }),
    getTasks: (params = {}) => api.get('/todos/tasks', { params }),
    getReviews: (params = {}) => api.get('/todos/reviews', { params }),
    getContracts: (params = {}) => api.get('/todos/contracts', { params }),
    getMyTodos: () => api.get('/todos/all'),
    getLeaveApprovals: (params = {}) => api.get('/attendance/leave-applications', { params }),
    getOvertimeApprovals: (params = {}) => api.get('/attendance/overtime-applications', { params }),
    getMyBugs: (params = {}) => api.get('/bugs', { params }),
    getMyTasks: (params = {}) => api.get('/tasks', { params }),
    getMyReviews: () => api.get('/todos/reviews')
  },

  // 任务管理
  tasks: {
    getList: (params = {}) => api.get('/tasks', { params }),
    getById: (id) => api.get(`/tasks/${id}`),
    create: (taskData) => api.post('/tasks', taskData),
    update: (id, taskData) => api.put(`/tasks/${id}`, taskData),
    delete: (id) => api.delete(`/tasks/${id}`),
    batchDelete: (ids) => api.post('/tasks/batch-delete', { ids }),
    batchUpdateStatus: (ids, status) => api.post('/tasks/batch-update-status', { ids, status }),
    updateStatus: (id, status) => api.put(`/tasks/${id}/status`, { status }),
    assignTask: (id, assigneeId) => api.put(`/tasks/${id}/assign`, { assignee_id: assigneeId })
  },
  
  // 测试管理相关
  tests: {
    getSuites: (projectId, params = {}) => api.get(`/test-management/suites/${projectId}`, { params }),
    getSuiteById: (id, params = {}) => api.get(`/test-management/suites/${id}`, { params }),
    getSuiteDetail: (id) => api.get(`/test-management/suites/${id}`),
    createSuite: (suiteData) => api.post('/test-management/suites', suiteData),
    updateSuite: (id, suiteData) => api.put(`/test-management/suites/${id}`, suiteData),
    deleteSuite: (id) => api.delete(`/test-management/suites/${id}`),
    batchOperateSuites: (data) => api.post('/test-management/suites/batch', data),
    getSuiteVersionInfo: (suiteId) => api.get(`/test-management/suites/${suiteId}/version`),
    getSuiteVersionHistory: (suiteId) => api.get(`/test-management/suites/${suiteId}/version-history`),

    getCasesBySuite: (suiteId, params = {}) => api.get(`/test-management/cases/by-suite/${suiteId}`, { params }),
    getCaseById: (id, params = {}) => api.get(`/test-management/cases/${id}`, { params }),
    createCase: (caseData) => api.post('/test-management/cases', caseData),
    updateCase: (id, caseData) => api.put(`/test-management/cases/${id}`, caseData),
    deleteCase: (id) => api.delete(`/test-management/cases/${id}`),
    batchOperateCases: (data) => api.post('/test-management/cases/batch', data),
    getCaseHistory: (caseId) => api.get(`/test-management/cases/${caseId}/history`),
    submitCaseReview: (caseId, data) => api.post(`/test-management/cases/${caseId}/review`, data),
    copyCase: (caseId, data) => api.post(`/test-management/cases/${caseId}/copy`, data),
    restoreCaseVersion: (caseId, versionId) => api.post(`/test-management/cases/${caseId}/restore/${versionId}`),
    importCases: (suiteId, fileData) => {
      const formData = new FormData()
      formData.append('file', fileData)
      formData.append('suite_id', suiteId)
      return api.post('/test-management/cases/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    },
    exportCases: (suiteId, format = 'excel') => api.get(`/test-management/cases/export/${suiteId}`, {
      params: { format },
      responseType: 'blob'
    }),
    exportCasesToXmind: (suiteId) => api.get(`/test-management/cases/export/xmind/${suiteId}`),

    getExecutionsByProject: (projectId, params = {}) => api.get(`/test-management/executions/by-project/${projectId}`, { params }),
    getExecutionById: (id, params = {}) => api.get(`/test-management/executions/${id}`, { params }),
    createExecution: (executionData) => api.post('/test-management/executions', executionData),
    updateExecution: (id, executionData) => api.put(`/test-management/executions/${id}`, executionData),
    deleteExecution: (id) => api.delete(`/test-management/executions/${id}`),
    submitTestResult: (executionId, resultData) => api.post(`/test-management/executions/${executionId}/results`, resultData),

    getResultsByCase: (caseId, params = {}) => api.get(`/test-management/results/by-case/${caseId}`, { params }),

    createRequirementLink: (linkData) => api.post('/test-management/links', linkData),
    deleteRequirementLink: (id) => api.delete(`/test-management/links/${id}`),
    getLinksByCase: (caseId) => api.get(`/test-management/links/by-case/${caseId}`),
    getLinksByRequirement: (requirementId) => api.get(`/test-management/links/by-requirement/${requirementId}`),

    getProjectStatistics: (projectId) => api.get(`/test-management/statistics/project/${projectId}`),
    getExecutionReport: (executionId) => api.get(`/test-management/reports/execution/${executionId}`),
    getProjectTestReport: (projectId) => api.get(`/test-management/reports/project/${projectId}`),
    getTestDashboard: (projectId) => api.get(`/test-management/dashboard/${projectId}`),
    exportExecutionReport: (executionId) => api.get(`/test-management/reports/execution/${executionId}/export`, {
      responseType: 'blob'
    })
  },
  
  // 风险与问题相关
  risks: {
    getList: (projectId, params = {}) => api.get(`/projects/${projectId}/risks`, { params }),
    getById: (id) => api.get(`/risks/${id}`),
    create: (projectId, riskData) => api.post(`/projects/${projectId}/risks`, riskData),
    update: (id, riskData) => api.put(`/risks/${id}`, riskData),
    delete: (id) => api.delete(`/risks/${id}`)
  },
  
  issues: {
    getList: (projectId, params = {}) => api.get(`/projects/${projectId}/issues`, { params }),
    getById: (id) => api.get(`/issues/${id}`),
    create: (projectId, issueData) => api.post(`/projects/${projectId}/issues`, issueData),
    update: (id, issueData) => api.put(`/issues/${id}`, issueData),
    delete: (id) => api.delete(`/issues/${id}`)
  },
  
  // 考勤管理
  attendance: {
    getWorkCalendar: (params = {}) => api.get('/attendance/work-calendar', { params }),
    updateWorkCalendar: (calendarData) => api.post('/attendance/work-calendar', calendarData),
    
    getShifts: () => api.get('/attendance/shifts'),
    createShift: (shiftData) => api.post('/attendance/shifts', shiftData),
    updateShift: (id, shiftData) => api.put(`/attendance/shifts/${id}`, shiftData),
    deleteShift: (id) => api.delete(`/attendance/shifts/${id}`),
    getUserShifts: (params = {}) => api.get('/attendance/user-shifts', { params }),
    assignUserShift: (assignmentData) => api.post('/attendance/user-shifts', assignmentData),
    updateUserShift: (id, assignmentData) => api.put(`/attendance/user-shifts/${id}`, assignmentData),
    deleteUserShift: (id) => api.delete(`/attendance/user-shifts/${id}`),
    
    getAttendanceRecords: (params = {}) => api.get('/attendance/records', { params }),
    getRecordById: (id) => api.get(`/attendance/records/${id}`),
    getTodayRecord: () => api.get('/attendance/records/today'),
    createRecord: (recordData) => api.post('/attendance/records', recordData),
    updateRecord: (id, recordData) => api.put(`/attendance/records/${id}`, recordData),
    deleteRecord: (id) => api.delete(`/attendance/records/${id}`),
    clockIn: (clockData = {}) => api.post('/attendance/clock-in', clockData),
    clockOut: (clockData = {}) => api.post('/attendance/clock-out', clockData),
    
    getLeaveApplications: (params = {}) => api.get('/attendance/leave-applications', { params }),
    getLeaveApplicationById: (id) => api.get(`/attendance/leave-applications/${id}`),
    createLeaveApplication: (applicationData) => api.post('/attendance/leave-applications', applicationData),
    updateLeaveApplication: (id, applicationData) => api.put(`/attendance/leave-applications/${id}`, applicationData),
    deleteLeaveApplication: (id) => api.delete(`/attendance/leave-applications/${id}`),
    approveLeaveApplication: (id, approvalData) => api.post(`/attendance/leave-applications/${id}/approve`, approvalData),
    rejectLeaveApplication: (id, rejectionData) => api.post(`/attendance/leave-applications/${id}/approve`, { ...rejectionData, action: 'reject' }),
    exportLeaveApplications: (params = {}) => api.get('/attendance/leave-applications/export', { params, responseType: 'blob' }),
    importLeaveApplications: (formData) => api.post('/attendance/leave-applications/import', formData),
    
    getOvertimeApplications: (params = {}) => api.get('/attendance/overtime-applications', { params }),
    getOvertimeApplicationById: (id) => api.get(`/attendance/overtime-applications/${id}`),
    createOvertimeApplication: (applicationData) => api.post('/attendance/overtime', applicationData),
    updateOvertimeApplication: (id, applicationData) => api.put(`/attendance/overtime-applications/${id}`, applicationData),
    deleteOvertimeApplication: (id) => api.delete(`/attendance/overtime-applications/${id}`),
    approveOvertimeApplication: (id, approvalData) => api.post(`/attendance/overtime-applications/${id}/approve`, approvalData),
    rejectOvertimeApplication: (id, rejectionData) => api.post(`/attendance/overtime-applications/${id}/approve`, { ...rejectionData, action: 'reject' }),
    exportOvertimeApplications: (params = {}) => api.get('/attendance/overtime-applications/export', { params, responseType: 'blob' }),
    importOvertimeApplications: (formData) => api.post('/attendance/overtime-applications/import', formData),
    
    getApprovals: (params = {}) => api.get('/attendance/approvals', { params }),
    approveApplication: (type, id, approvalData) => api.post(`/attendance/approve/${type}/${id}`, approvalData),
    
    getExceptions: (params = {}) => api.get('/attendance/exceptions', { params }),
    getExceptionById: (id) => api.get(`/attendance/exceptions/${id}`),
    createException: (exceptionData) => api.post('/attendance/exceptions', exceptionData),
    updateException: (id, exceptionData) => api.put(`/attendance/exceptions/${id}`, exceptionData),
    deleteException: (id) => api.delete(`/attendance/exceptions/${id}`),
    approveException: (id, approvalData) => api.post(`/attendance/exceptions/${id}/approve`, approvalData),
    rejectException: (id, rejectionData) => api.post(`/attendance/exceptions/${id}/approve`, { ...rejectionData, status: 'rejected' }),
    
    getStatistics: (params = {}) => api.get('/attendance/statistics', { params }),
    getMonthlyReport: (params = {}) => api.get('/attendance/reports/monthly', { params }),
    getReportsOverview: (params = {}) => api.get('/attendance/reports/overview', { params }),
    getReportsDetail: (params = {}) => api.get('/attendance/reports/detail', { params }),
    exportAttendanceReport: (params = {}) => api.get('/attendance/reports/export', { params }),
    getDepartmentReport: (params = {}) => api.get('/attendance/reports/department', { params }),
    exportData: (params = {}) => api.get('/attendance/export', { params }),
    getAbsenceSummary: (params = {}) => api.get('/attendance/summary/absence', { params }),
    getOvertimeSummary: (params = {}) => api.get('/attendance/summary/overtime', { params })
  },
  
  // 物料管理
  materials: {
    getCategories: () => api.get('/materials/categories'),
    getCategory: (id) => api.get(`/materials/categories/${id}`),
    createCategory: (data) => api.post('/materials/categories', data),
    updateCategory: (id, data) => api.put(`/materials/categories/${id}`, data),
    deleteCategory: (id) => api.delete(`/materials/categories/${id}`),
    
    getList: (params = {}) => api.get('/materials/', { params }),
    getById: (id) => api.get(`/materials/${id}`),
    create: (data) => api.post('/materials/', data),
    update: (id, data) => api.put(`/materials/${id}`, data),
    delete: (id) => api.delete(`/materials/${id}`),
    
    getWarehouses: () => api.get('/materials/warehouses'),
    getWarehouse: (id) => api.get(`/materials/warehouses/${id}`),
    createWarehouse: (data) => api.post('/materials/warehouses', data),
    updateWarehouse: (id, data) => api.put(`/materials/warehouses/${id}`, data),
    deleteWarehouse: (id) => api.delete(`/materials/warehouses/${id}`),
    
    getLocations: (params = {}) => api.get('/materials/locations', { params }),
    getLocation: (id) => api.get(`/materials/locations/${id}`),
    createLocation: (data) => api.post('/materials/locations', data),
    updateLocation: (id, data) => api.put(`/materials/locations/${id}`, data),
    deleteLocation: (id) => api.delete(`/materials/locations/${id}`),
    
    getInventory: (params = {}) => api.get('/materials/inventory', { params }),
    getInventoryStats: () => api.get('/materials/inventory/stats'),
    
    getTransactions: (params = {}) => api.get('/materials/transactions', { params }),
    getTransaction: (id) => api.get(`/materials/transactions/${id}`),
    createTransaction: (data) => api.post('/materials/transactions', data),
    
    getSerialNumbers: (params = {}) => api.get('/materials/serial-numbers', { params }),
    getSerialNumber: (id) => api.get(`/materials/serial-numbers/${id}`),
    createSerialNumber: (data) => api.post('/materials/serial-numbers', data),
    updateSerialNumber: (id, data) => api.put(`/materials/serial-numbers/${id}`, data),
    
    getRelationships: (params = {}) => api.get('/materials/relationships', { params }),
    createRelationship: (data) => api.post('/materials/relationships', data),
    deleteRelationship: (id) => api.delete(`/materials/relationships/${id}`),

    exportMaterials: (params = {}) => api.get('/materials/export', { params, responseType: 'blob' }),
    importMaterials: (fileData) => api.post('/materials/import', fileData)
  },
  
  // 文件上传
  upload: {
    uploadFile: (fileData) => api.post('/upload', fileData),
    getFileUrl: (fileId) => `${api.defaults.baseURL}/upload/${fileId}`
  },

  // 系统管理
  system: {
    createBackup: () => api.post('/system/backup'),
    getBackups: () => api.get('/system/backups'),
    deleteBackup: (filename) => api.delete(`/system/backups/${filename}`),
    downloadBackup: (filename) => api.get(`/system/backups/${filename}`, {
      responseType: 'blob'
    }),
    getSystemTime: () => api.get('/system/time'),

    getConfig: () => api.get('/system/config'),
    updateConfig: (configData) => api.put('/system/config', configData),

    integrityCheck: () => api.post('/system/integrity-check'),

    testEmail: (email) => api.post('/system/test-email', { email })
  },

  // 知识库管理
  knowledge: {
    // 分类管理
    getCategories: (params = {}) => api.get('/knowledge/categories', { params }),
    getCategoryTree: () => api.get('/knowledge/categories/tree'),
    getCategory: (id) => api.get(`/knowledge/categories/${id}`),
    createCategory: (data) => api.post('/knowledge/categories', data),
    updateCategory: (id, data) => api.put(`/knowledge/categories/${id}`, data),
    deleteCategory: (id, data) => api.delete(`/knowledge/categories/${id}`, { data }),
    archiveCategory: (id) => api.post(`/knowledge/categories/${id}/archive`),
    getCategoryArticles: (id, params = {}) => api.get(`/knowledge/categories/${id}/articles`, { params }),

    // 文章管理
    getArticles: (params = {}) => api.get('/knowledge/articles', { params }),
    getMyArticles: (params = {}) => api.get('/knowledge/articles/my', { params }),
    getArticleById: (id) => api.get(`/knowledge/articles/${id}`),
    createArticle: (data) => api.post('/knowledge/articles', data),
    updateArticle: (id, data) => api.put(`/knowledge/articles/${id}`, data),
    deleteArticle: (id) => api.delete(`/knowledge/articles/${id}`),
    updateArticleStatus: (id, status) => api.put(`/knowledge/articles/${id}/status`, { status }),
    likeArticle: (id) => api.post(`/knowledge/articles/${id}/like`),

    // 批量操作
    batchMoveArticles: (articleIds, targetCategoryId) => api.post('/knowledge/articles/batch/move', { article_ids: articleIds, target_category_id: targetCategoryId }),
    batchUpdateStatus: (articleIds, status) => api.post('/knowledge/articles/batch/status', { article_ids: articleIds, status }),
    batchDeleteArticles: (articleIds) => api.post('/knowledge/articles/batch/delete', { article_ids: articleIds }),

    // 搜索
    search: (params = {}) => api.get('/knowledge/search', { params }),

    // 标签
    getTags: () => api.get('/knowledge/tags'),

    // 统计
    getStatistics: () => api.get('/knowledge/statistics'),

    // 附件管理
    uploadAttachment: (articleId, file) => {
      const formData = new FormData()
      formData.append('file', file)
      return api.post(`/knowledge/articles/${articleId}/attachments`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    },
    downloadAttachment: (articleId, attachmentId) => api.get(`/knowledge/articles/${articleId}/attachments/${attachmentId}`, { responseType: 'blob' }),
    deleteAttachment: (articleId, attachmentId) => api.delete(`/knowledge/articles/${articleId}/attachments/${attachmentId}`)
  },

  // 系统监控管理
  monitoring: {
    getHealth: () => api.get('/monitoring/health'),
    getPerformance: () => api.get('/monitoring/performance'),
    getPerformanceHistory: (params) => api.get('/monitoring/performance/history', { params }),
    getDatabaseStats: () => api.get('/monitoring/database'),
    getApiStats: () => api.get('/monitoring/api/stats'),
    getLogs: (params) => api.get('/monitoring/logs', { params }),
    getAlerts: (params) => api.get('/monitoring/alerts', { params }),
    createAlert: (data) => api.post('/monitoring/alerts', data),
    resolveAlert: (id) => api.post(`/monitoring/alerts/${id}/resolve`),
    getAlertRules: () => api.get('/monitoring/alert-rules'),
    getSystemInfo: () => api.get('/monitoring/system-info'),
    getDashboard: () => api.get('/monitoring/dashboard')
  }
}

// 导出axios实例
export { api as axios, api }
export default api