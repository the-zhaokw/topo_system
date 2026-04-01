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
    isAuthenticated: (state) => !!state.token && !!state.currentUser
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
