import { systemTimeService } from '@/services/systemTimeService'

// 后端 datetime.utcnow() 存储的时间不带时区信息，JavaScript 默认视为本地时间，
// 需要加 'Z' 后缀才能正确识别为 UTC 时间并自动转换为北京时间
export function parseUTCDate(dateString) {
  if (!dateString) return null
  let str = String(dateString).trim()
  // 已带时区信息（Z 后缀或 ±HH:MM 偏移），直接解析
  if (/Z$/i.test(str) || /[+-]\d{2}:\d{2}$/.test(str)) {
    return new Date(str)
  }
  // 后端可能返回 "2026-08-28T08:30:54" 或 "2026-08-28 08:30:54" 格式
  // 都是不带时区的 UTC 时间，统一加 Z 后缀
  str = str.replace(' ', 'T')
  return new Date(str + 'Z')
}

export const formatDate = (dateString) => {
  if (!dateString) return '未设置'
  const date = parseUTCDate(dateString)
  if (!date || isNaN(date.getTime())) return '无效日期'
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
    timeZone: 'Asia/Shanghai'
  })
}

export const getTimeAgo = (dateString) => {
  if (!dateString) return ''
  const date = parseUTCDate(dateString)
  if (!date || isNaN(date.getTime())) return ''

  const now = systemTimeService.getServerTime()
  const diff = now - date
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) return `${days}天前`
  if (hours > 0) return `${hours}小时前`
  if (minutes > 0) return `${minutes}分钟前`
  return '刚刚'
}
