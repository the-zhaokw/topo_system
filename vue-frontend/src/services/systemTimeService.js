import { apiService } from './api'

class SystemTimeService {
  constructor() {
    this.serverTimeOffset = 0
    this.lastFetchTime = 0
    this.cacheDuration = 60000
    this.initialized = false
  }

  async syncServerTime() {
    try {
      const response = await apiService.system.getSystemTime()
      const serverTime = response.timestamp || new Date(response.server_time).getTime()
      const clientTime = Date.now()

      this.serverTimeOffset = serverTime - clientTime
      this.lastFetchTime = clientTime
      this.initialized = true

      localStorage.setItem('serverTimeOffset', this.serverTimeOffset.toString())
      localStorage.setItem('serverTimeLastSync', this.lastFetchTime.toString())

      return this.getServerTime()
    } catch (error) {
      console.error('Failed to sync server time:', error)
      const cachedOffset = localStorage.getItem('serverTimeOffset')
      const cachedLastSync = localStorage.getItem('serverTimeLastSync')

      if (cachedOffset && cachedLastSync) {
        const timeSinceSync = Date.now() - parseInt(cachedLastSync)
        if (timeSinceSync < this.cacheDuration * 10) {
          this.serverTimeOffset = parseInt(cachedOffset)
          this.initialized = true
          return this.getServerTime()
        }
      }

      return new Date()
    }
  }

  getServerTime() {
    if (!this.initialized) {
      const cachedOffset = localStorage.getItem('serverTimeOffset')
      const cachedLastSync = localStorage.getItem('serverTimeLastSync')

      if (cachedOffset && cachedLastSync) {
        const timeSinceSync = Date.now() - parseInt(cachedLastSync)
        if (timeSinceSync < this.cacheDuration * 10) {
          this.serverTimeOffset = parseInt(cachedOffset)
          this.initialized = true
        }
      }
    }

    return new Date(Date.now() + this.serverTimeOffset)
  }

  getServerTimeStamp() {
    return this.getServerTime().getTime()
  }

  async ensureSynced() {
    if (!this.initialized || Date.now() - this.lastFetchTime > this.cacheDuration) {
      await this.syncServerTime()
    }
  }
}

export const systemTimeService = new SystemTimeService()
export default systemTimeService