import api from './api.js'

/**
 * Bug统计服务
 * 提供Bug管理模块的统计功能API调用
 */
const bugStatisticsService = {
  
  /**
   * 获取Bug统计仪表盘数据
   * @param {number} days - 时间范围（天数）
   * @returns {Promise} - API响应
   */
  getDashboardStats: async (days = 30) => {
    try {
      const response = await api.get(`/bug-statistics/dashboard?days=${days}`)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取Bug统计仪表盘数据失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取统计数据失败',
        data: null
      }
    }
  },

  /**
   * 获取项目级Bug统计
   * @param {number} projectId - 项目ID
   * @param {number} days - 时间范围（天数）
   * @returns {Promise} - API响应
   */
  getProjectStats: async (projectId, days = 30) => {
    try {
      const response = await api.get(`/bug-statistics/project/${projectId}?days=${days}`)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取项目Bug统计数据失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取项目统计数据失败',
        data: null
      }
    }
  },

  /**
   * 获取开发者Bug统计
   * @param {number} days - 时间范围（天数）
   * @returns {Promise} - API响应
   */
  getDeveloperPerformance: async (days = 30) => {
    try {
      const response = await api.get(`/bug-statistics/developer-performance?days=${days}`)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取开发者Bug统计数据失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取开发者统计数据失败',
        data: null
      }
    }
  },

  /**
   * 获取测试者Bug统计
   * @param {number} days - 时间范围（天数）
   * @returns {Promise} - API响应
   */
  getTesterPerformance: async (days = 30) => {
    try {
      const response = await api.get(`/bug-statistics/tester-performance?days=${days}`)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取测试者Bug统计数据失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取测试者统计数据失败',
        data: null
      }
    }
  },

  /**
   * 获取Bug根因分析数据
   * @returns {Promise} - API响应
   */
  getRootCauseAnalysis: async () => {
    try {
      const response = await api.get('/bug-statistics/root-cause-analysis')
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取Bug根因分析数据失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取根因分析数据失败',
        data: null
      }
    }
  },

  /**
   * 获取重新打开Bug分析数据
   * @param {number} days - 时间范围（天数）
   * @returns {Promise} - API响应
   */
  getReopenAnalysis: async (days = 30) => {
    try {
      const response = await api.get(`/bug-statistics/reopen-analysis?days=${days}`)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取重新打开Bug分析数据失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取重新打开分析数据失败',
        data: null
      }
    }
  },

  /**
   * 导出Bug统计数据
   * @param {Object} params - 导出参数
   * @param {string} params.type - 导出类型（csv/json）
   * @param {string} params.stats_type - 统计类型
   * @param {number} params.days - 时间范围
   * @param {number} params.project_id - 项目ID（可选）
   * @returns {Promise} - API响应
   */
  exportStatistics: async (params = {}) => {
    try {
      const queryParams = new URLSearchParams()
      Object.keys(params).forEach(key => {
        if (params[key] !== undefined && params[key] !== null) {
          queryParams.append(key, params[key])
        }
      })
      
      const response = await api.get(`/bug-statistics/export?${queryParams.toString()}`, {
        responseType: 'blob'
      })
      
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      console.error('导出Bug统计数据失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '导出数据失败',
        data: null
      }
    }
  },

  /**
   * 获取Bug生命周期分析数据
   * @param {Object} filters - 筛选条件
   * @param {number} filters.project_id - 项目ID（可选）
   * @param {string} filters.module - 模块名称（可选）
   * @returns {Promise} - API响应
   */
  getBugLifecycleAnalysis: async (filters = {}) => {
    try {
      const queryParams = new URLSearchParams()
      Object.keys(filters).forEach(key => {
        if (filters[key] !== undefined && filters[key] !== null) {
          queryParams.append(key, filters[key])
        }
      })
      
      const response = await api.get(`/bug-statistics/lifecycle-analysis?${queryParams.toString()}`)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取Bug生命周期分析数据失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取生命周期分析数据失败',
        data: null
      }
    }
  },

  /**
   * 获取自定义报表数据
   * @param {Object} config - 报表配置
   * @returns {Promise} - API响应
   */
  getCustomReport: async (config) => {
    try {
      const response = await api.post('/bug-statistics/custom-report', config)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取自定义报表数据失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取自定义报表数据失败',
        data: null
      }
    }
  },

  /**
   * 自定义报表生成器
   * @param {Object} params - 生成参数
   * @returns {Promise} - API响应
   */
  generateCustomReport: async (params) => {
    try {
      const response = await api.post('/bug-statistics/custom-report/generate', params)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('生成自定义报表失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '生成自定义报表失败',
        data: null
      }
    }
  },

  /**
   * 获取报表模板列表
   * @returns {Promise} - API响应
   */
  getReportTemplates: async () => {
    try {
      const response = await api.get('/bug-statistics/custom-report/templates')
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取报表模板失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取报表模板失败',
        data: null
      }
    }
  },

  /**
   * 保存报表模板
   * @param {Object} template - 模板数据
   * @returns {Promise} - API响应
   */
  saveReportTemplate: async (template) => {
    try {
      const response = await api.post('/bug-statistics/custom-report/templates', template)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('保存报表模板失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '保存报表模板失败',
        data: null
      }
    }
  },

  /**
   * 删除报表模板
   * @param {number} templateId - 模板ID
   * @returns {Promise} - API响应
   */
  deleteReportTemplate: async (templateId) => {
    try {
      const response = await api.delete(`/bug-statistics/custom-report/templates/${templateId}`)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('删除报表模板失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '删除报表模板失败',
        data: null
      }
    }
  },

  /**
   * 导出自定义报表
   * @param {Object} params - 导出参数
   * @returns {Promise} - API响应
   */
  exportCustomReport: async (params) => {
    try {
      const response = await api.post('/bug-statistics/custom-report/export', params, {
        responseType: 'blob'
      })
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      console.error('导出自定义报表失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '导出自定义报表失败',
        data: null
      }
    }
  },

  getFilterOptions: async () => {
    try {
      const response = await api.get('/bug-statistics/filter-options')
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取筛选选项失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取筛选选项失败',
        data: null
      }
    }
  },

  getKpiMetrics: async (filters = {}) => {
    try {
      const params = new URLSearchParams()
      Object.keys(filters).forEach(key => {
        if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
          params.append(key, filters[key])
        }
      })
      const response = await api.get(`/bug-statistics/kpi-metrics?${params.toString()}`)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取KPI指标失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取KPI指标失败',
        data: null
      }
    }
  },

  getTrendAnalysis: async (filters = {}) => {
    try {
      const params = new URLSearchParams()
      Object.keys(filters).forEach(key => {
        if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
          params.append(key, filters[key])
        }
      })
      const response = await api.get(`/bug-statistics/trend-analysis?${params.toString()}`)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取趋势分析失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取趋势分析失败',
        data: null
      }
    }
  },

  getDistributionAnalysis: async (filters = {}) => {
    try {
      const params = new URLSearchParams()
      Object.keys(filters).forEach(key => {
        if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
          params.append(key, filters[key])
        }
      })
      const response = await api.get(`/bug-statistics/distribution-analysis?${params.toString()}`)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取分布分析失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取分布分析失败',
        data: null
      }
    }
  },

  getTypeDistribution: async (filters = {}) => {
    try {
      const params = new URLSearchParams()
      Object.keys(filters).forEach(key => {
        if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
          params.append(key, filters[key])
        }
      })
      const response = await api.get(`/bug-statistics/type-distribution?${params.toString()}`)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取类型分布失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取类型分布失败',
        data: null
      }
    }
  },

  getPersonWorkload: async (filters = {}) => {
    try {
      const params = new URLSearchParams()
      Object.keys(filters).forEach(key => {
        if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
          params.append(key, filters[key])
        }
      })
      const response = await api.get(`/bug-statistics/person-workload?${params.toString()}`)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取人员工作量失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取人员工作量失败',
        data: null
      }
    }
  },

  getSurvivalDuration: async (filters = {}) => {
    try {
      const params = new URLSearchParams()
      Object.keys(filters).forEach(key => {
        if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
          params.append(key, filters[key])
        }
      })
      const response = await api.get(`/bug-statistics/survival-duration?${params.toString()}`)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取存活时长失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取存活时长失败',
        data: null
      }
    }
  },

  getBugList: async (filters = {}) => {
    try {
      const params = new URLSearchParams()
      Object.keys(filters).forEach(key => {
        if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
          params.append(key, filters[key])
        }
      })
      const response = await api.get(`/bugs?${params.toString()}`)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error) {
      console.error('获取Bug列表失败:', error)
      return {
        success: false,
        message: error.response?.data?.error || '获取Bug列表失败',
        data: null
      }
    }
  }
}

export default bugStatisticsService