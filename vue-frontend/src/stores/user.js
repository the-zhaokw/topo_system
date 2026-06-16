import { defineStore } from 'pinia'
import { apiService } from '@/services/api'

const getStoredUser = () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      return JSON.parse(userStr)
    } catch (e) {
      return null
    }
  }
  return null
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    currentUser: getStoredUser(),
    userLoading: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.currentUser,
    isSuperAdmin: (state) => !!(state.currentUser && (state.currentUser.is_super_admin || state.currentUser.is_admin)),
    /**
     * 检查用户是否拥有指定细分权限
     * @param {string} code - 权限编码，如 'bug:create'
     */
    hasPermission: (state) => (code) => {
      const u = state.currentUser
      if (!u) return false
      // 超级管理员 / 系统管理员
      if (u.is_super_admin || u.is_admin) return true
      const cp = u.custom_permissions || {}
      // 限制权限优先：denied 视为无权限
      if (Array.isArray(cp.denied) && cp.denied.includes(code)) return false
      // 额外权限显式授予
      if (Array.isArray(cp.allowed) && cp.allowed.includes(code)) return true
      return false
    },
    /**
     * 检查用户是否拥有任一/全部指定权限
     * @param {string|string[]} codes
     * @param {boolean} all - true 表示要全部满足；false（默认）任一即可
     */
    hasAnyPermission: (state) => (codes) => {
      if (!Array.isArray(codes) || codes.length === 0) return false
      return codes.some(c => state.currentUser && (state.currentUser.is_super_admin || state.currentUser.is_admin || (() => {
        const cp = state.currentUser.custom_permissions || {}
        if (Array.isArray(cp.denied) && cp.denied.includes(c)) return false
        if (Array.isArray(cp.allowed) && cp.allowed.includes(c)) return true
        return false
      })()))
    }
  },

  actions: {
    async login(credentials) {
      this.userLoading = true
      try {
        const response = await apiService.auth.login(credentials)
        if (response && (response.access_token || response.token)) {
          this.token = response.access_token || response.token
          localStorage.setItem('token', this.token)
          if (response.user) {
            this.currentUser = response.user
            localStorage.setItem('user', JSON.stringify(response.user))
          } else {
            await this.fetchCurrentUser()
          }
          return { success: true, message: '登录成功' }
        }
        return { success: false, message: response?.message || '登录失败' }
      } catch (error) {
        return { success: false, message: error.response?.data?.error || error.response?.data?.message || '登录失败' }
      } finally {
        this.userLoading = false
      }
    },

    async register(userData) {
      this.userLoading = true
      try {
        const response = await apiService.auth.register(userData)
        if (response && response.token) {
          this.token = response.token
          localStorage.setItem('token', response.token)
          await this.fetchCurrentUser()
          return { success: true, message: '注册成功' }
        }
        return { success: false, message: '注册失败' }
      } catch (error) {
        return { success: false, message: error.response?.data?.error || '注册失败' }
      } finally {
        this.userLoading = false
      }
    },

    async fetchCurrentUser() {
      if (!this.token) return null
      this.userLoading = true
      try {
        const response = await apiService.auth.getCurrentUser()
        this.currentUser = response
        localStorage.setItem('user', JSON.stringify(response))
        return response
      } catch (error) {
        console.error('获取用户信息失败:', error)
        this.logout()
        return null
      } finally {
        this.userLoading = false
      }
    },

    logout() {
      this.token = ''
      this.currentUser = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },

    setUser(userData) {
      this.currentUser = userData
      localStorage.setItem('user', JSON.stringify(userData))
    },

    async updateProfile(profileData) {
      try {
        const response = await apiService.auth.updateProfile(profileData)
        if (this.currentUser) {
          this.currentUser = { ...this.currentUser, ...response }
        }
        return { success: true, message: '更新成功' }
      } catch (error) {
        return { success: false, message: error.response?.data?.error || '更新失败' }
      }
    },

    async changePassword(passwordData) {
      try {
        await apiService.auth.changePassword(passwordData)
        return { success: true, message: '密码修改成功' }
      } catch (error) {
        return { success: false, message: error.response?.data?.error || '密码修改失败' }
      }
    }
  }
})
