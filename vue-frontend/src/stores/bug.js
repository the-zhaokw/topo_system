import { defineStore } from 'pinia'
import { apiService } from '@/services/api'

export const useBugStore = defineStore('bug', {
  state: () => ({
    bugs: [],
    currentBug: null,
    loading: false,
    total: 0,
    queryParams: {
      page: 1,
      page_size: 20,
      project_id: null,
      status: null,
      severity: null,
      priority: null,
      search: '',
      sort_field: 'created_at',
      sort_order: 'descending'
    }
  }),

  getters: {
    getBugById: (state) => (id) => {
      return state.bugs.find(bug => bug.id === id)
    }
  },

  actions: {
    async fetchBugs(params = {}) {
      this.loading = true
      try {
        const queryParams = { ...this.queryParams, ...params }
        const response = await apiService.bugs.getList(queryParams)
        this.bugs = response.items || response.data || response || []
        this.total = response.total || this.bugs.length
        return { success: true, bugs: this.bugs, total: this.total }
      } catch (error) {
        console.error('获取Bug列表失败:', error)
        return { success: false, error: error.message }
      } finally {
        this.loading = false
      }
    },

    async fetchBug(id) {
      this.loading = true
      try {
        const response = await apiService.bugs.getById(id)
        if (response && response.data && response.data.bug) {
          this.currentBug = response.data.bug
        } else if (response && response.bug) {
          this.currentBug = response.bug
        } else if (response) {
          this.currentBug = response
        } else {
          this.currentBug = null
        }
        return { success: true, bug: this.currentBug }
      } catch (error) {
        console.error('获取Bug详情失败:', error)
        return { success: false, error: error.message || '获取Bug详情失败' }
      } finally {
        this.loading = false
      }
    },

    async fetchBugById(id) {
      return this.fetchBug(id)
    },

    async fetchComments(bugId) {
      try {
        const response = await apiService.bugs.getComments(bugId)
        const comments = response?.data || response?.comments || response || []
        return { success: true, comments }
      } catch (error) {
        console.error('获取评论失败:', error)
        return { success: false, error: error.message }
      }
    },

    async addComment(bugId, commentData) {
      try {
        const response = await apiService.bugs.addComment(bugId, commentData)
        return { success: true, data: response }
      } catch (error) {
        return { success: false, message: error.response?.data?.error || '添加评论失败' }
      }
    },

    async createBug(bugData) {
      try {
        const response = await apiService.bugs.create(bugData)
        return { success: true, data: response }
      } catch (error) {
        return { success: false, message: error.response?.data?.error || '创建失败' }
      }
    },

    async updateBug(id, bugData) {
      try {
        const response = await apiService.bugs.update(id, bugData)
        return { success: true, data: response }
      } catch (error) {
        return { success: false, message: error.response?.data?.error || '更新失败' }
      }
    },

    async deleteBug(id) {
      try {
        await apiService.bugs.delete(id)
        this.bugs = this.bugs.filter(bug => bug.id !== id)
        return { success: true }
      } catch (error) {
        return { success: false, message: error.response?.data?.error || '删除失败' }
      }
    },

    async updateBugStatus(id, status) {
      try {
        await apiService.bugs.updateStatus(id, status)
        const bug = this.bugs.find(b => b.id === id)
        if (bug) bug.status = status
        return { success: true }
      } catch (error) {
        return { success: false, message: error.response?.data?.error || '状态更新失败' }
      }
    },

    setQueryParams(params) {
      this.queryParams = { ...this.queryParams, ...params }
    },

    resetQueryParams() {
      this.queryParams = {
        page: 1,
        page_size: 20,
        project_id: null,
        status: null,
        severity: null,
        priority: null,
        search: '',
        sort_field: 'created_at',
        sort_order: 'descending'
      }
    }
  }
})
