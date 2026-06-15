<template>
  <div class="my-attendance">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
        <div class="gradient-orb orb-3"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Clock /></el-icon>
          </div>
          <div class="title-text">
            <h1>我的考勤</h1>
            <p class="subtitle">实时了解个人出勤状态、异常情况与假期余额</p>
          </div>
        </div>
        <div class="header-actions">
          <el-date-picker
            v-model="periodValue"
            type="month"
            placeholder="选择月份"
            format="YYYY 年 MM 月"
            value-format="YYYY-MM"
            @change="handlePeriodChange"
            class="period-picker"
          />
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-container animate-fade-in-up">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else class="attendance-content">
      <!-- 概览统计卡片：应出勤 / 实际出勤 / 出勤率 / 缺卡 -->
      <div class="overview-section animate-fade-in-up delay-100">
        <el-row :gutter="16">
          <el-col :xs="12" :sm="6">
            <div class="stat-card stat-expected">
              <div class="stat-icon-wrapper">
                <el-icon><Calendar /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ summary.expected_days || 0 }}</div>
                <div class="stat-label">应出勤天数</div>
                <div class="stat-hint">基于工作日历</div>
              </div>
              <div class="stat-decoration"></div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-card stat-actual">
              <div class="stat-icon-wrapper">
                <el-icon><CircleCheckFilled /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ summary.actual_days || 0 }}</div>
                <div class="stat-label">实际出勤天数</div>
                <div class="stat-hint">扣除异常后</div>
              </div>
              <div class="stat-decoration"></div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-card stat-rate">
              <div class="stat-icon-wrapper">
                <el-icon><DataLine /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ summary.attendance_rate || 0 }}%</div>
                <div class="stat-label">出勤率</div>
                <el-progress
                  :percentage="summary.attendance_rate || 0"
                  :stroke-width="6"
                  :show-text="false"
                  :color="rateColor"
                  class="rate-progress"
                />
              </div>
              <div class="stat-decoration"></div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-card stat-missing" :class="{ 'stat-warn': (summary.missing_count || 0) > 0 }">
              <div class="stat-icon-wrapper">
                <el-icon><QuestionFilled /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ summary.missing_count || 0 }}</div>
                <div class="stat-label">缺卡次数</div>
                <div class="stat-hint">未打卡且未补卡</div>
              </div>
              <div class="stat-decoration"></div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 迟到/早退 + 旷工 -->
      <div class="anomaly-section animate-fade-in-up delay-200">
        <el-row :gutter="16">
          <el-col :xs="24" :md="16">
            <el-card class="glass-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <div class="card-title">
                    <div class="card-icon-wrapper card-icon-orange">
                      <el-icon><AlarmClock /></el-icon>
                    </div>
                    <span>迟到 / 早退</span>
                    <el-tag v-if="lateGrade.level" :type="lateGradeTagType" size="small" effect="light" class="grade-tag">
                      {{ lateGrade.message }}
                    </el-tag>
                  </div>
                </div>
              </template>
              <el-row :gutter="16">
                <el-col :xs="12">
                  <div class="metric-block">
                    <div class="metric-header">
                      <el-icon class="metric-icon metric-icon-late"><Timer /></el-icon>
                      <span class="metric-name">迟到</span>
                    </div>
                    <div class="metric-stats">
                      <div class="metric-item">
                        <div class="metric-value">{{ summary.late?.count || 0 }}</div>
                        <div class="metric-label">次数</div>
                      </div>
                      <div class="metric-divider"></div>
                      <div class="metric-item">
                        <div class="metric-value">{{ formatMinutes(summary.late?.minutes || 0) }}</div>
                        <div class="metric-label">累计时长</div>
                      </div>
                    </div>
                    <el-alert
                      :type="lateGrade.level === 'danger' ? 'error' : (lateGrade.level === 'warning' ? 'warning' : 'success')"
                      :closable="false"
                      show-icon
                      class="metric-alert"
                    >
                      <template #title>
                        <span>{{ lateGrade.hint }}</span>
                      </template>
                    </el-alert>
                  </div>
                </el-col>
                <el-col :xs="12">
                  <div class="metric-block">
                    <div class="metric-header">
                      <el-icon class="metric-icon metric-icon-early"><Back /></el-icon>
                      <span class="metric-name">早退</span>
                    </div>
                    <div class="metric-stats">
                      <div class="metric-item">
                        <div class="metric-value">{{ summary.early_leave?.count || 0 }}</div>
                        <div class="metric-label">次数</div>
                      </div>
                      <div class="metric-divider"></div>
                      <div class="metric-item">
                        <div class="metric-value">{{ formatMinutes(summary.early_leave?.minutes || 0) }}</div>
                        <div class="metric-label">累计时长</div>
                      </div>
                    </div>
                    <el-alert
                      :type="(summary.early_leave?.count || 0) > 0 ? 'warning' : 'success'"
                      :closable="false"
                      show-icon
                      class="metric-alert"
                    >
                      <template #title>
                        <span v-if="(summary.early_leave?.count || 0) === 0">本月无早退记录</span>
                        <span v-else>累计早退 {{ summary.early_leave.count }} 次</span>
                      </template>
                    </el-alert>
                  </div>
                </el-col>
              </el-row>
            </el-card>
          </el-col>

          <el-col :xs="24" :md="8">
            <el-card class="glass-card stat-card-absent" shadow="hover">
              <template #header>
                <div class="card-header">
                  <div class="card-title">
                    <div class="card-icon-wrapper card-icon-red">
                      <el-icon><WarningFilled /></el-icon>
                    </div>
                    <span>旷工天数</span>
                  </div>
                </div>
              </template>
              <div class="absent-block">
                <div class="absent-value" :class="{ 'absent-danger': (summary.absent_days || 0) > 0 }">
                  {{ summary.absent_days || 0 }}
                  <span class="absent-unit">天</span>
                </div>
                <div class="absent-desc">
                  旷工将直接影响薪资红线
                </div>
                <el-alert
                  :type="(summary.absent_days || 0) > 0 ? 'error' : 'success'"
                  :closable="false"
                  show-icon
                  class="absent-alert"
                >
                  <template #title>
                    <span v-if="(summary.absent_days || 0) === 0">本月无旷工记录</span>
                    <span v-else>已触发薪资红线警告</span>
                  </template>
                </el-alert>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 请假 + 加班 -->
      <div class="leave-overtime-section animate-fade-in-up delay-300">
        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-card class="glass-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <div class="card-title">
                    <div class="card-icon-wrapper card-icon-blue">
                      <el-icon><Postcard /></el-icon>
                    </div>
                    <span>请假时长</span>
                  </div>
                  <el-button type="primary" link @click="$router.push('/attendance/leave-application')">
                    申请请假 <el-icon><ArrowRight /></el-icon>
                  </el-button>
                </div>
              </template>

              <div class="annual-leave-block">
                <div class="annual-leave-header">
                  <span class="annual-leave-label">年假余额</span>
                  <span class="annual-leave-value">
                    {{ annualLeave.remaining }}<span class="annual-leave-unit">天</span>
                  </span>
                </div>
                <el-progress
                  :percentage="annualLeavePercent"
                  :stroke-width="8"
                  :color="annualLeavePercent > 50 ? '#10b981' : (annualLeavePercent > 20 ? '#f59e0b' : '#ef4444')"
                />
                <div class="annual-leave-detail">
                  <span>总额度 {{ annualLeave.quota }} 天</span>
                  <span>已使用 {{ annualLeave.used }} 天</span>
                </div>
              </div>

              <el-divider />

              <div class="leave-breakdown">
                <div class="breakdown-title">分类型统计</div>
                <div v-if="leaveItems.length === 0" class="empty-mini">
                  本月暂无请假记录
                </div>
                <div v-else class="breakdown-list">
                  <div v-for="item in leaveItems" :key="item.type" class="breakdown-item">
                    <div class="breakdown-info">
                      <div class="breakdown-dot" :style="{ background: item.color }"></div>
                      <span class="breakdown-name">{{ item.label }}</span>
                    </div>
                    <div class="breakdown-value">
                      {{ item.days }}<span class="breakdown-unit">天</span>
                    </div>
                  </div>
                  <div class="breakdown-total">
                    <span>合计</span>
                    <span class="breakdown-total-value">
                      {{ summary.leave?.total_days || 0 }}<span class="breakdown-unit">天</span>
                    </span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>

          <el-col :xs="24" :md="12">
            <el-card class="glass-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <div class="card-title">
                    <div class="card-icon-wrapper card-icon-purple">
                      <el-icon><Moon /></el-icon>
                    </div>
                    <span>加班时长</span>
                  </div>
                  <el-button type="primary" link @click="$router.push('/attendance/overtime-application')">
                    申请加班 <el-icon><ArrowRight /></el-icon>
                  </el-button>
                </div>
              </template>

              <div class="overtime-total">
                <div class="overtime-value">
                  {{ summary.overtime?.total_hours || 0 }}
                  <span class="overtime-unit">小时</span>
                </div>
                <div class="overtime-desc">可用于调休或加班费结算</div>
              </div>

              <el-divider />

              <div class="overtime-breakdown">
                <div class="breakdown-title">分类型统计</div>
                <div class="overtime-type-list">
                  <div class="overtime-type-item">
                    <div class="overtime-type-icon overtime-type-workday">
                      <el-icon><Sunny /></el-icon>
                    </div>
                    <div class="overtime-type-info">
                      <div class="overtime-type-label">工作日加班</div>
                      <div class="overtime-type-value">
                        {{ summary.overtime?.breakdown?.workday || 0 }} 小时
                      </div>
                    </div>
                  </div>
                  <div class="overtime-type-item">
                    <div class="overtime-type-icon overtime-type-weekend">
                      <el-icon><Sunny /></el-icon>
                    </div>
                    <div class="overtime-type-info">
                      <div class="overtime-type-label">周末加班</div>
                      <div class="overtime-type-value">
                        {{ summary.overtime?.breakdown?.weekend || 0 }} 小时
                      </div>
                    </div>
                  </div>
                  <div class="overtime-type-item">
                    <div class="overtime-type-icon overtime-type-holiday">
                      <el-icon><Star /></el-icon>
                    </div>
                    <div class="overtime-type-info">
                      <div class="overtime-type-label">节假日加班</div>
                      <div class="overtime-type-value">
                        {{ summary.overtime?.breakdown?.holiday || 0 }} 小时
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 底部快捷入口 -->
      <div class="quick-actions animate-fade-in-up delay-400">
        <el-card class="glass-card" shadow="hover">
          <div class="quick-grid">
            <div class="quick-item" @click="$router.push('/attendance/records')">
              <el-icon class="quick-icon"><Document /></el-icon>
              <span>考勤明细</span>
            </div>
            <div class="quick-item" @click="handleClockIn">
              <el-icon class="quick-icon"><Promotion /></el-icon>
              <span>立即打卡</span>
            </div>
            <div class="quick-item" @click="$router.push('/attendance/leave-application')">
              <el-icon class="quick-icon"><Postcard /></el-icon>
              <span>申请请假</span>
            </div>
            <div class="quick-item" @click="$router.push('/attendance/overtime-application')">
              <el-icon class="quick-icon"><Moon /></el-icon>
              <span>申请加班</span>
            </div>
            <div class="quick-item" @click="$router.push('/attendance/shifts')">
              <el-icon class="quick-icon"><Calendar /></el-icon>
              <span>班次安排</span>
            </div>
            <div class="quick-item" @click="$router.push('/attendance/reports')">
              <el-icon class="quick-icon"><DataAnalysis /></el-icon>
              <span>考勤报表</span>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Clock, Calendar, CircleCheckFilled, DataLine, QuestionFilled,
  AlarmClock, Timer, Back, WarningFilled, Postcard, ArrowRight,
  Moon, Sunny, Star, Document, Promotion, DataAnalysis
} from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const router = useRouter()

const loading = ref(false)
const summary = ref({})
const periodValue = ref('')

const annualLeave = computed(() => {
  return summary.value.leave?.annual_leave || { quota: 0, used: 0, remaining: 0 }
})

const annualLeavePercent = computed(() => {
  if (!annualLeave.value.quota) return 0
  return Math.round((annualLeave.value.remaining / annualLeave.value.quota) * 100)
})

const lateGrade = computed(() => {
  const grade = summary.value.late?.grade || {}
  const count = grade.count || 0
  if (count === 0) {
    return {
      level: 'normal',
      message: '良好',
      hint: '本月无迟到记录',
      tagType: 'success'
    }
  } else if (count <= 3) {
    return {
      level: 'warning',
      message: '警告',
      hint: `已迟到 ${count} 次，累计 ${formatMinutes(summary.value.late?.minutes || 0)}，建议调整作息`,
      tagType: 'warning'
    }
  } else {
    return {
      level: 'danger',
      message: '严重',
      hint: `已迟到 ${count} 次，超过 3 次警告线，请关注考勤表现`,
      tagType: 'danger'
    }
  }
})

const lateGradeTagType = computed(() => lateGrade.value.tagType)

const rateColor = computed(() => {
  const rate = summary.value.attendance_rate || 0
  if (rate >= 95) return '#10b981'
  if (rate >= 80) return '#3b82f6'
  if (rate >= 60) return '#f59e0b'
  return '#ef4444'
})

const leaveTypeMap = {
  annual_leave: { label: '年假', color: '#10b981' },
  sick_leave: { label: '病假', color: '#f59e0b' },
  personal_leave: { label: '事假', color: '#ef4444' },
  marriage_leave: { label: '婚假', color: '#ec4899' },
  maternity_leave: { label: '产假', color: '#a855f7' },
  paternity_leave: { label: '陪产假', color: '#a855f7' },
  bereavement_leave: { label: '丧假', color: '#64748b' },
  other: { label: '其他', color: '#94a3b8' }
}

const leaveItems = computed(() => {
  const breakdown = summary.value.leave?.breakdown || {}
  return Object.keys(breakdown)
    .filter((key) => breakdown[key] > 0)
    .map((key) => ({
      type: key,
      label: leaveTypeMap[key]?.label || key,
      color: leaveTypeMap[key]?.color || '#94a3b8',
      days: breakdown[key]
    }))
    .sort((a, b) => b.days - a.days)
})

const formatMinutes = (minutes) => {
  if (!minutes) return '0 分钟'
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (h > 0 && m > 0) return `${h} 小时 ${m} 分`
  if (h > 0) return `${h} 小时`
  return `${m} 分钟`
}

const handlePeriodChange = () => {
  fetchSummary()
}

const handleClockIn = () => {
  router.push('/attendance/records')
}

const fetchSummary = async () => {
  loading.value = true
  try {
    const params = {}
    if (periodValue.value) {
      const [year, month] = periodValue.value.split('-')
      params.year = year
      params.month = month
    }
    const data = await apiService.attendance.getMySummary(params)
    summary.value = data || {}
  } catch (error) {
    console.error('获取个人考勤汇总失败:', error)
    ElMessage.error(error.response?.data?.error || '获取个人考勤汇总失败')
    summary.value = {}
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const now = new Date()
  periodValue.value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  fetchSummary()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.my-attendance {
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  min-height: 100%;
}

/* 页面头部 */
.page-header {
  margin: -16px -16px 24px -16px;
  padding: 32px;
  background: linear-gradient(135deg, #0c4a6e 0%, #0c4a6e 50%, #0c4a6e 100%);
  border-radius: 0 0 24px 24px;
  color: white;
  position: relative;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(30, 27, 75, 0.3);
}

.header-bg-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
}

.gradient-orb.orb-1 {
  width: 360px;
  height: 360px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.4), rgba(14, 165, 233, 0.3));
  top: -100px;
  right: -100px;
}

.gradient-orb.orb-2 {
  width: 260px;
  height: 260px;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.3), rgba(14, 165, 233, 0.2));
  bottom: -80px;
  left: 10%;
}

.gradient-orb.orb-3 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.3), rgba(249, 112, 102, 0.2));
  top: 30%;
  right: 20%;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
  gap: 24px;
  flex-wrap: wrap;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 20px;
}

.title-icon-wrapper {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.18), rgba(255, 255, 255, 0.05));
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.title-icon-wrapper .title-icon {
  font-size: 32px;
  color: #a5b4fc;
}

.title-text h1 {
  margin: 0 0 6px 0;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, #ffffff 0%, #c7d2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-text .subtitle {
  margin: 0;
  font-size: 14px;
  opacity: 0.75;
}

.header-actions :deep(.period-picker) {
  width: 180px;
}

.header-actions :deep(.period-picker .el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: none;
  backdrop-filter: blur(12px);
  color: white;
}

.header-actions :deep(.period-picker input) {
  color: white;
}

.header-actions :deep(.period-picker .el-input__placeholder) {
  color: rgba(255, 255, 255, 0.6);
}

/* 加载容器 */
.loading-container {
  padding: 24px;
  background: white;
  border-radius: 16px;
}

/* 玻璃拟态卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.08);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
  box-shadow: 0 12px 48px rgba(31, 38, 135, 0.12);
  border-color: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
}

/* 概览统计卡片 */
.overview-section {
  margin-bottom: 20px;
}

.stat-card {
  position: relative;
  padding: 24px 20px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.08);
  display: flex;
  align-items: center;
  gap: 16px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(31, 38, 135, 0.12);
}

.stat-card .stat-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-card .stat-icon-wrapper .el-icon {
  font-size: 28px;
}

.stat-card .stat-content {
  flex: 1;
  min-width: 0;
}

.stat-card .stat-value {
  font-size: 32px;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 4px;
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-card .stat-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 600;
  margin-bottom: 2px;
}

.stat-card .stat-hint {
  font-size: 11px;
  color: #94a3b8;
}

.stat-decoration {
  position: absolute;
  top: -40px;
  right: -40px;
  width: 140px;
  height: 140px;
  border-radius: 50%;
  opacity: 0.12;
  filter: blur(20px);
}

.stat-expected .stat-icon-wrapper {
  background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 100%);
  color: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}
.stat-expected .stat-decoration {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
}

.stat-actual .stat-icon-wrapper {
  background: linear-gradient(135deg, #d1fae5 0%, #6ee7b7 100%);
  color: #059669;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.2);
}
.stat-actual .stat-decoration {
  background: linear-gradient(135deg, #10b981, #34d399);
}

.stat-rate .stat-icon-wrapper {
  background: linear-gradient(135deg, #f3e8ff 0%, #d8b4fe 100%);
  color: #0284c7;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2);
}
.stat-rate .stat-decoration {
  background: linear-gradient(135deg, #38bdf8, #7dd3fc);
}

.rate-progress {
  margin-top: 8px;
}

.stat-missing .stat-icon-wrapper {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 12px rgba(217, 119, 6, 0.2);
}
.stat-missing .stat-decoration {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}

.stat-missing.stat-warn {
  border-color: rgba(245, 158, 11, 0.4);
  box-shadow: 0 8px 32px rgba(245, 158, 11, 0.15);
}

.stat-missing.stat-warn .stat-icon-wrapper {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.2);
}

.stat-missing.stat-warn .stat-decoration {
  background: linear-gradient(135deg, #ef4444, #f87171);
}

/* 异常区域 */
.anomaly-section,
.leave-overtime-section {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  color: #1e293b;
  font-size: 16px;
}

.card-icon-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-icon-wrapper .el-icon {
  font-size: 18px;
}

.card-icon-orange {
  background: linear-gradient(135deg, #ffedd5 0%, #fed7aa 100%);
  color: #ea580c;
}

.card-icon-red {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
}

.card-icon-blue {
  background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 100%);
  color: #2563eb;
}

.card-icon-purple {
  background: linear-gradient(135deg, #f3e8ff 0%, #d8b4fe 100%);
  color: #0284c7;
}

.grade-tag {
  margin-left: 8px;
  font-weight: 600;
}

.metric-block {
  padding: 8px 0;
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
}

.metric-icon {
  font-size: 20px;
}

.metric-icon-late {
  color: #ea580c;
}

.metric-icon-early {
  color: #2563eb;
}

.metric-name {
  font-weight: 600;
  color: #1e293b;
}

.metric-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 14px;
  margin-bottom: 12px;
}

.metric-item {
  flex: 1;
  text-align: center;
}

.metric-value {
  font-size: 26px;
  font-weight: 800;
  color: #1e293b;
  line-height: 1.1;
  margin-bottom: 4px;
}

.metric-label {
  font-size: 12px;
  color: #64748b;
}

.metric-divider {
  width: 1px;
  height: 36px;
  background: #e2e8f0;
}

.metric-alert :deep(.el-alert__title) {
  font-size: 13px;
}

/* 旷工卡片 */
.stat-card-absent :deep(.el-card__body) {
  padding: 20px;
}

.absent-block {
  text-align: center;
  padding: 12px 0;
}

.absent-value {
  font-size: 56px;
  font-weight: 800;
  line-height: 1;
  color: #10b981;
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}

.absent-value.absent-danger {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.absent-unit {
  font-size: 18px;
  font-weight: 600;
  margin-left: 4px;
  opacity: 0.7;
}

.absent-desc {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 16px;
}

.absent-alert {
  text-align: left;
}

/* 年假 */
.annual-leave-block {
  padding: 4px 0;
}

.annual-leave-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
}

.annual-leave-label {
  font-size: 14px;
  color: #475569;
  font-weight: 600;
}

.annual-leave-value {
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.annual-leave-unit {
  font-size: 14px;
  margin-left: 2px;
  opacity: 0.7;
}

.annual-leave-detail {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #94a3b8;
}

/* 分类明细 */
.breakdown-title {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 12px;
}

.breakdown-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.breakdown-item:hover {
  background: rgba(241, 245, 249, 0.9);
  transform: translateX(4px);
}

.breakdown-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.breakdown-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.breakdown-name {
  font-size: 13px;
  color: #1e293b;
  font-weight: 500;
}

.breakdown-value {
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
}

.breakdown-unit {
  font-size: 11px;
  margin-left: 2px;
  color: #94a3b8;
  font-weight: 500;
}

.breakdown-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border-radius: 10px;
  margin-top: 4px;
  font-size: 13px;
  color: #1e40af;
  font-weight: 600;
}

.breakdown-total-value {
  font-size: 16px;
  font-weight: 800;
}

.empty-mini {
  text-align: center;
  padding: 20px;
  font-size: 13px;
  color: #94a3b8;
  background: rgba(241, 245, 249, 0.5);
  border-radius: 10px;
}

/* 加班 */
.overtime-total {
  text-align: center;
  padding: 8px 0 4px;
}

.overtime-value {
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(135deg, #0284c7 0%, #7dd3fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.1;
}

.overtime-unit {
  font-size: 16px;
  margin-left: 4px;
  opacity: 0.7;
}

.overtime-desc {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.overtime-type-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.overtime-type-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.overtime-type-item:hover {
  background: rgba(241, 245, 249, 0.9);
  transform: translateX(4px);
}

.overtime-type-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: white;
}

.overtime-type-workday {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
}

.overtime-type-weekend {
  background: linear-gradient(135deg, #60a5fa, #3b82f6);
}

.overtime-type-holiday {
  background: linear-gradient(135deg, #f87171, #ef4444);
}

.overtime-type-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.overtime-type-label {
  font-size: 13px;
  color: #475569;
  font-weight: 500;
}

.overtime-type-value {
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
}

/* 快捷入口 */
.quick-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.quick-item:hover {
  background: white;
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  border-color: rgba(56, 189, 248, 0.15);
}

.quick-icon {
  font-size: 24px;
  color: #5b6df5;
}

.quick-item span {
  font-size: 13px;
  color: #475569;
  font-weight: 500;
}

.quick-item:hover span {
  color: #5b6df5;
}

/* 动画 */
@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in-down { animation: fadeInDown 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.animate-fade-in-up { animation: fadeInUp 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275); animation-fill-mode: both; }

.delay-100 { animation-delay: 100ms; }
.delay-200 { animation-delay: 200ms; }
.delay-300 { animation-delay: 300ms; }
.delay-400 { animation-delay: 400ms; }

/* 响应式 */
@media screen and (max-width: 768px) {
  .page-header {
    padding: 20px 16px;
    margin: -8px -8px 16px -8px;
    border-radius: 0 0 16px 16px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .title-icon-wrapper {
    width: 52px;
    height: 52px;
  }

  .title-icon-wrapper .title-icon {
    font-size: 26px;
  }

  .title-text h1 {
    font-size: 22px;
  }

  .quick-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .stat-card {
    padding: 18px 14px;
  }

  .stat-card .stat-icon-wrapper {
    width: 44px;
    height: 44px;
  }

  .stat-card .stat-icon-wrapper .el-icon {
    font-size: 22px;
  }

  .stat-card .stat-value {
    font-size: 24px;
  }
}
</style>
