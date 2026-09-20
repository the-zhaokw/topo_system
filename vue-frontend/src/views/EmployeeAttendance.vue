<template>
  <div class="employee-attendance-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><User /></el-icon>
          </div>
          <div class="title-text">
            <h1>员工考勤记录</h1>
            <p class="subtitle">按员工工号汇总当月考勤明细、请假与加班数据</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button v-if="canAccess" type="success" @click="handleExport" class="btn-gradient" :loading="exporting">
            <el-icon><Download /></el-icon>
            导出 Excel
          </el-button>
          <el-button type="primary" @click="fetchData" class="btn-gradient" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="attendance-tabs" @tab-change="onTabChange">
      <el-tab-pane label="考勤汇总" name="summary">
    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :lg="6">
          <div class="stat-card stat-card-total">
            <div class="stat-icon-wrapper stat-icon-wrapper-total">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ totalEmployees }}</div>
              <div class="stat-label">员工总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :lg="6">
          <div class="stat-card stat-card-attendance">
            <div class="stat-icon-wrapper stat-icon-wrapper-attendance">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ summary.checkin_count }}</div>
              <div class="stat-label">当月打卡总次数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :lg="6">
          <div class="stat-card stat-card-leave">
            <div class="stat-icon-wrapper stat-icon-wrapper-leave">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ summary.leave_days }}</div>
              <div class="stat-label">当月请假总天数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :lg="6">
          <div class="stat-card stat-card-overtime">
            <div class="stat-icon-wrapper stat-icon-wrapper-overtime">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ summary.overtime_hours }}</div>
              <div class="stat-label">当月加班总时长(h)</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-section animate-fade-in-up delay-200">
      <el-card class="filter-card glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Filter /></el-icon>
              筛选条件
            </span>
          </div>
        </template>
        <el-form :model="filterForm" inline class="filter-form">
          <el-form-item label="统计月份">
            <el-date-picker
              v-model="filterForm.month"
              type="month"
              placeholder="选择月份"
              format="YYYY-MM"
              value-format="YYYY-MM"
              :clearable="false"
              class="filter-select"
            />
          </el-form-item>
          <el-form-item label="部门">
            <el-select v-model="filterForm.department" placeholder="全部部门" clearable filterable class="filter-select">
              <el-option v-for="dept in departmentOptions" :key="dept" :label="dept" :value="dept" />
            </el-select>
          </el-form-item>
          <el-form-item label="关键词">
            <el-input
              v-model="filterForm.keyword"
              placeholder="搜索工号/姓名/账号"
              clearable
              class="filter-input"
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch" class="btn-gradient">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 员工考勤列表（钉钉式月度考勤报表） -->
    <div class="content-section animate-fade-in-up delay-300">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="table-header">
            <div class="table-title">
              <el-icon><Document /></el-icon>
              <h3>员工考勤汇总</h3>
              <span class="total-count">共 {{ displayedEmployees.length }} 名员工</span>
            </div>
          </div>
        </template>

        <el-table
          :data="displayedEmployees"
          v-loading="loading"
          class="custom-table"
          stripe
          border
          :default-sort="{ prop: 'employee_id', order: 'ascending' }"
          show-summary
          :summary-method="getSummary"
        >
          <!-- 基本信息 -->
          <el-table-column prop="name" label="姓名" width="90" fixed="left">
            <template #default="{ row }">
              <div class="employee-name">
                <el-avatar :size="26" class="name-avatar">{{ (row.name || row.username).charAt(0) }}</el-avatar>
                <span>{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="department" label="部门" min-width="90" fixed="left">
            <template #default="{ row }">
              <span v-if="row.department">{{ row.department }}</span>
              <span v-else class="no-data">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="employee_id" label="工号" width="80" align="center" sortable fixed="left">
            <template #default="{ row }">
              <span v-if="row.employee_id" class="employee-id">{{ row.employee_id }}</span>
              <span v-else class="no-data">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="position" label="职位" min-width="90" fixed="left">
            <template #default="{ row }">
              <span v-if="row.position">{{ row.position }}</span>
              <span v-else class="no-data">-</span>
            </template>
          </el-table-column>

          <el-table-column prop="date" label="日期" width="80" align="center" />
          <el-table-column prop="shift_name" label="班次" width="90" align="center">
            <template #default="{ row }">
              <span v-if="row.shift_name">{{ row.shift_name }}</span>
              <span v-else class="no-data">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="approval_count" label="关联的审批单" width="80" align="center" />

          <!-- 出勤统计 -->
          <el-table-column prop="attendance_days" label="出勤天数" width="80" align="center" />
          <el-table-column prop="rest_days" label="休息天数" width="80" align="center" />
          <el-table-column prop="work_hours" label="工作时长" width="80" align="center" />

          <!-- 迟到/早退 -->
          <el-table-column label="迟到" align="center">
            <el-table-column prop="late_count" label="次数" width="60" align="center" />
            <el-table-column prop="late_hours" label="时长" width="70" align="center" />
          </el-table-column>
          <el-table-column label="严重迟到" align="center">
            <el-table-column prop="severe_late_count" label="次数" width="60" align="center" />
            <el-table-column prop="severe_late_hours" label="时长" width="70" align="center" />
          </el-table-column>
          <el-table-column prop="absent_late_days" label="旷工迟到天数" width="90" align="center" />
          <el-table-column label="早退" align="center">
            <el-table-column prop="early_leave_count" label="次数" width="60" align="center" />
            <el-table-column prop="early_leave_hours" label="时长" width="70" align="center" />
          </el-table-column>

          <!-- 缺卡/旷工 -->
          <el-table-column prop="missing_clock_in" label="上班缺卡次数" width="90" align="center" />
          <el-table-column prop="missing_clock_out" label="下班缺卡次数" width="90" align="center" />
          <el-table-column prop="absenteeism_days" label="旷工天数" width="80" align="center" />

          <!-- 出差/外出 -->
          <el-table-column prop="business_trip_hours" label="出差时长" width="80" align="center" />
          <el-table-column prop="outing_hours" label="外出时长" width="80" align="center" />

          <!-- 请假分组 -->
          <el-table-column label="请假" align="center">
            <el-table-column prop="leave.personal_h" label="事假(小时)" width="80" align="center" />
            <el-table-column prop="leave.comp_h" label="调休(小时)" width="80" align="center" />
            <el-table-column prop="leave.sick_h" label="病假(小时)" width="80" align="center" />
            <el-table-column prop="leave.annual_d" label="年假(天)" width="70" align="center" />
            <el-table-column prop="leave.maternity_d" label="产假(天)" width="70" align="center" />
            <el-table-column prop="leave.paternity_d" label="陪产假(天)" width="80" align="center" />
            <el-table-column prop="leave.marriage_d" label="婚假(天)" width="70" align="center" />
            <el-table-column prop="leave.period_d" label="例假(天)" width="70" align="center" />
            <el-table-column prop="leave.bereavement_d" label="丧假(天)" width="70" align="center" />
            <el-table-column prop="leave.nursing_h" label="哺乳假(小时)" width="90" align="center" />
          </el-table-column>

          <!-- 加班分组 -->
          <el-table-column prop="overtime_total_hours" label="加班总时长" width="90" align="center" />
          <el-table-column label="加班时长（转加班费）" align="center">
            <el-table-column prop="overtime_pay.weekday_h" label="工作日" width="70" align="center" />
            <el-table-column prop="overtime_pay.rest_h" label="休息日" width="70" align="center" />
            <el-table-column prop="overtime_pay.holiday_h" label="节假日" width="70" align="center" />
          </el-table-column>
          <el-table-column label="加班时长（转调休）" align="center">
            <el-table-column prop="overtime_leave.weekday_h" label="工作日" width="70" align="center" />
            <el-table-column prop="overtime_leave.rest_h" label="休息日" width="70" align="center" />
            <el-table-column prop="overtime_leave.holiday_h" label="节假日" width="70" align="center" />
          </el-table-column>

          <!-- 年假 -->
          <el-table-column label="剩余年假(天)" width="110" align="center" fixed="right">
            <template #default="{ row }">
              <el-tag :type="getAnnualLeaveTagType(row.annual_leave)" size="small" effect="light" class="annual-tag">
                {{ row.annual_leave.remaining }} / {{ row.annual_leave.quota }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
      </el-tab-pane>

      <el-tab-pane label="考勤确认表" name="confirmation">
        <!-- 每月考勤确认单：发送状态列表 + 发送确认单 -->
        <div class="content-section animate-fade-in-up delay-200">
          <el-card class="glass-card" shadow="hover">
            <template #header>
              <div class="table-header">
                <div class="table-title">
                  <el-icon><Promotion /></el-icon>
                  <h3>每月考勤确认单</h3>
                  <span class="total-count">共 {{ displayedConfEmployees.length }} 名员工，已发送 {{ sentCount }} 份</span>
                </div>
                <div>
                  <el-button
                    type="warning"
                    class="btn-gradient-send"
                    :loading="confSending"
                    @click="handleSendAll"
                  >
                    <el-icon><Promotion /></el-icon>
                    发送确认单（全部）
                  </el-button>
                  <el-button @click="fetchConfirmations" :loading="confLoading">
                    <el-icon><Refresh /></el-icon>
                    刷新状态
                  </el-button>
                </div>
              </div>
            </template>

            <el-alert
              v-if="!mailConfigured"
              title="邮件服务未配置或未启用，确认单无法发出，请先在系统设置中配置邮件服务器"
              type="error"
              :closable="false"
              show-icon
              style="margin-bottom: 14px;"
            />
            <el-alert
              title="点击表格任意行可核对/修改该员工当月数据（保存后立即生效）；点击“发送确认单”将按示例格式把确认单发送到其邮箱，逾期未回复默认与实际考勤一致。"
              type="info"
              :closable="false"
              show-icon
              style="margin-bottom: 14px;"
            />

            <el-table
              :data="displayedConfEmployees"
              v-loading="confLoading"
              class="custom-table conf-table"
              stripe
              border
              @row-click="handleRowClick"
            >
              <el-table-column prop="name" label="姓名" width="100" fixed="left">
                <template #default="{ row }">
                  <div class="employee-name">
                    <el-avatar :size="26" class="name-avatar">{{ (row.name || row.username).charAt(0) }}</el-avatar>
                    <span>{{ row.name }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="employee_id" label="工号" width="70" align="center" fixed="left" />
              <el-table-column prop="department" label="部门" min-width="90" />
              <el-table-column label="收件邮箱" min-width="200">
                <template #default="{ row }">
                  <span v-if="row.has_email" class="conf-email">{{ row.recipient_email }}</span>
                  <el-tooltip v-else content="钉钉自动建档账号无邮箱，请先在员工管理中补充该员工邮箱" placement="top">
                    <el-tag type="danger" size="small">未配置邮箱</el-tag>
                  </el-tooltip>
                </template>
              </el-table-column>
              <el-table-column prop="attendance_days" label="出勤天数" width="75" align="center" />
              <el-table-column label="全勤/元" width="70" align="center">
                <template #default="{ row }">
                  <span :class="{ 'conf-red': row.stats?.full_attendance_bonus }">{{ showStat(row.stats?.full_attendance_bonus) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="迟到早退/次" align="center">
                <el-table-column label="<10’" width="62" align="center">
                  <template #default="{ row }">{{ showStat(row.stats?.late_under10) }}</template>
                </el-table-column>
                <el-table-column label="<30’" width="62" align="center">
                  <template #default="{ row }">{{ showStat(row.stats?.late_under30) }}</template>
                </el-table-column>
              </el-table-column>
              <el-table-column label="请假/H" align="center">
                <el-table-column label="事假" width="62" align="center">
                  <template #default="{ row }">{{ showStat(row.stats?.personal_h) }}</template>
                </el-table-column>
                <el-table-column label="病假" width="62" align="center">
                  <template #default="{ row }">{{ showStat(row.stats?.sick_h) }}</template>
                </el-table-column>
                <el-table-column label="年假" width="62" align="center">
                  <template #default="{ row }">{{ showStat(row.stats?.annual_h) }}</template>
                </el-table-column>
                <el-table-column label="其它" width="62" align="center">
                  <template #default="{ row }">{{ showStat(row.stats?.other_leave_h) }}</template>
                </el-table-column>
              </el-table-column>
              <el-table-column label="加班/H" align="center">
                <el-table-column label="平日" width="62" align="center">
                  <template #default="{ row }"><span class="conf-red">{{ showStat(row.stats?.ot_weekday) }}</span></template>
                </el-table-column>
                <el-table-column label="调休" width="62" align="center">
                  <template #default="{ row }"><span class="conf-blue">{{ showStat(row.stats?.ot_rest) }}</span></template>
                </el-table-column>
                <el-table-column label="法定" width="62" align="center">
                  <template #default="{ row }"><span class="conf-red">{{ showStat(row.stats?.ot_holiday) }}</span></template>
                </el-table-column>
              </el-table-column>
              <el-table-column label="其它/H" width="68" align="center">
                <template #default="{ row }">{{ showStat(row.stats?.other_h) }}</template>
              </el-table-column>
              <el-table-column label="漏卡/次" width="68" align="center">
                <template #default="{ row }">{{ showStat(row.stats?.missing) }}</template>
              </el-table-column>
              <el-table-column prop="remark" label="备注" min-width="110">
                <template #default="{ row }">
                  <span class="conf-remark">{{ row.stats?.remark }}</span>
                </template>
              </el-table-column>
              <el-table-column label="发送状态" width="160" align="center">
                <template #default="{ row }">
                  <el-tag v-if="row.status === 'sent'" type="success" size="small">已发送</el-tag>
                  <el-tag v-else-if="row.status === 'failed'" type="danger" size="small">
                    发送失败
                  </el-tag>
                  <el-tag v-else type="info" size="small">未发送</el-tag>
                  <div v-if="row.error_message" class="conf-error" :title="row.error_message">
                    {{ row.error_message }}
                  </div>
                  <div v-if="row.sent_at" class="conf-time">{{ row.sent_at }}</div>
                  <div v-if="row.sent_by_name" class="conf-sender">发送人：{{ row.sent_by_name }}</div>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="130" align="center" fixed="right">
                <template #default="{ row }">
                  <el-button
                    type="primary"
                    size="small"
                    :loading="row._sending"
                    :disabled="!row.has_email"
                    @click.stop="handleSendOne(row)"
                  >
                    {{ row.status === 'unsent' ? '发送确认单' : '重新发送' }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 点击行：修改数据并直接保存；点击发送按钮：只读确认后发送 -->
    <el-dialog
      v-model="confDialog.visible"
      :title="confDialog.mode === 'edit'
        ? `考勤确认单 - ${confDialog.name}（${filterForm.month}）`
        : `发送确认 - ${confDialog.name}（${filterForm.month}）`"
      width="960px"
      :close-on-click-modal="false"
    >
      <div style="margin-bottom: 10px; color: #64748b; font-size: 13px;">
        收件邮箱：<b style="color: #0c4a6e;">{{ confDialog.email }}</b>
        <span style="margin-left: 16px;">
          {{ confDialog.mode === 'edit'
            ? '可直接修改表格中的数值（全勤奖默认 200 元），点击“保存”后立即生效；发送时以此数据为准。'
            : '请确认以下当月考勤数据，确认后将发送到员工邮箱；如需修改请关闭后点击对应行进行修改并保存。' }}
        </span>
      </div>
      <table class="conf-edit-table">
        <thead>
          <tr>
            <th rowspan="2" style="width: 84px;">全勤/元</th>
            <th colspan="2">迟到早退/次</th>
            <th colspan="4">请假</th>
            <th colspan="3">加班/H</th>
            <th rowspan="2" style="width: 70px;">其它/H</th>
            <th rowspan="2" style="width: 70px;">漏卡/次</th>
            <th rowspan="2" style="width: 150px;">备注</th>
          </tr>
          <tr>
            <th>&lt;10’</th>
            <th>&lt;30’</th>
            <th>事假/H</th>
            <th>病假/H</th>
            <th>年假/H</th>
            <th>其它/H</th>
            <th class="th-red">平日</th>
            <th class="th-blue">调休</th>
            <th class="th-red">法定</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>
              <el-input-number v-model="confDialog.stats.full_attendance_bonus" :min="0" :max="9999" :controls="false" size="small" class="conf-num conf-num-wide" :disabled="confReadonly" />
            </td>
            <td><el-input-number v-model="confDialog.stats.late_under10" :min="0" :controls="false" size="small" class="conf-num" :disabled="confReadonly" /></td>
            <td><el-input-number v-model="confDialog.stats.late_under30" :min="0" :controls="false" size="small" class="conf-num" :disabled="confReadonly" /></td>
            <td><el-input-number v-model="confDialog.stats.personal_h" :min="0" :step="0.5" :controls="false" size="small" class="conf-num" :disabled="confReadonly" /></td>
            <td><el-input-number v-model="confDialog.stats.sick_h" :min="0" :step="0.5" :controls="false" size="small" class="conf-num" :disabled="confReadonly" /></td>
            <td><el-input-number v-model="confDialog.stats.annual_h" :min="0" :step="0.5" :controls="false" size="small" class="conf-num" :disabled="confReadonly" /></td>
            <td><el-input-number v-model="confDialog.stats.other_leave_h" :min="0" :step="0.5" :controls="false" size="small" class="conf-num" :disabled="confReadonly" /></td>
            <td><el-input-number v-model="confDialog.stats.ot_weekday" :min="0" :step="0.5" :controls="false" size="small" class="conf-num conf-num-red" :disabled="confReadonly" /></td>
            <td><el-input-number v-model="confDialog.stats.ot_rest" :min="0" :step="0.5" :controls="false" size="small" class="conf-num conf-num-blue" :disabled="confReadonly" /></td>
            <td><el-input-number v-model="confDialog.stats.ot_holiday" :min="0" :step="0.5" :controls="false" size="small" class="conf-num conf-num-red" :disabled="confReadonly" /></td>
            <td><el-input-number v-model="confDialog.stats.other_h" :min="0" :step="0.5" :controls="false" size="small" class="conf-num" :disabled="confReadonly" /></td>
            <td><el-input-number v-model="confDialog.stats.missing" :min="0" :controls="false" size="small" class="conf-num" :disabled="confReadonly" /></td>
            <td><el-input v-model="confDialog.stats.remark" size="small" class="conf-remark-input" placeholder="异常说明" :disabled="confReadonly" /></td>
          </tr>
        </tbody>
      </table>
      <template #footer>
        <el-button @click="confDialog.visible = false">{{ confDialog.mode === 'edit' ? '取消' : '关闭' }}</el-button>
        <el-button v-if="confDialog.mode === 'edit'" type="primary" :loading="confDialog.saving" @click="saveConfDraft">
          保存
        </el-button>
        <el-button v-else type="warning" :loading="confDialog.sending" @click="confirmSendOne">
          <el-icon><Promotion /></el-icon>
          确认发送
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Clock, Calendar, Timer, Refresh, Filter, Search, Document, Download, Promotion } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { apiService } from '@/services/api'

const userStore = useUserStore()
const router = useRouter()
const loading = ref(false)
const exporting = ref(false)

// 页签：考勤汇总 / 考勤确认表
const activeTab = ref('summary')

// 功能访问权限：仅超级管理员 / 总经理 / 人事经理 / 人事专员
const canAccess = computed(() => {
  const u = userStore.currentUser
  if (!u) return false
  if (u.is_super_admin || u.role === 'admin') return true
  const role = u.role || ''
  const position = u.position || ''
  // 总经理（分管领导）
  if (role === 'division_leader' || role === 'general_manager' || position.includes('总经理')) return true
  // 人事经理 / 人事专员
  if (role === 'hr' || position.includes('人事')) return true
  return false
})

// 当前月份（YYYY-MM）
const currentMonth = () => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
}

// 筛选条件
const filterForm = ref({
  month: currentMonth(),
  department: '',
  keyword: ''
})

// 部门列表
const departmentOptions = ref([])
const fetchDepartments = async () => {
  try {
    const res = await apiService.users.getDepartments()
    departmentOptions.value = res.departments || []
  } catch (e) {
    console.error('获取部门列表失败:', e)
  }
}

// 员工考勤数据
const employees = ref([])
const totalEmployees = ref(0)
const summary = ref({
  checkin_count: 0,
  leave_days: 0,
  overtime_hours: 0
})

const fetchData = async () => {
  loading.value = true
  try {
    const params = { month: filterForm.value.month }
    if (filterForm.value.department) {
      params.department = filterForm.value.department
    }
    const res = await apiService.attendance.getEmployeeSummary(params)
    employees.value = res.employees || []
    totalEmployees.value = res.total_employees || 0
    summary.value = res.summary || { checkin_count: 0, leave_days: 0, overtime_hours: 0 }
  } catch (e) {
    console.error('获取员工考勤记录失败:', e)
    ElMessage.error(e.response?.data?.error || '获取员工考勤记录失败')
  } finally {
    loading.value = false
  }
}

// 前端关键词过滤（工号/姓名/账号）
const displayedEmployees = computed(() => {
  const kw = filterForm.value.keyword.trim().toLowerCase()
  if (!kw) return employees.value
  return employees.value.filter(emp =>
    (emp.employee_id || '').toLowerCase().includes(kw) ||
    (emp.name || '').toLowerCase().includes(kw) ||
    (emp.username || '').toLowerCase().includes(kw)
  )
})

// 剩余年假标签颜色
const getAnnualLeaveTagType = (annual) => {
  if (!annual || annual.quota <= 0) return 'info'
  const ratio = annual.remaining / annual.quota
  if (ratio <= 0.2) return 'danger'
  if (ratio <= 0.5) return 'warning'
  return 'success'
}

// 合计行（对所有数字列求和）
const getSummary = ({ columns, data }) => {
  return columns.map((column, index) => {
    if (index === 0) {
      return `合计（${data.length} 人）`
    }
    if (!column.property) {
      return ''
    }
    const total = data.reduce((sum, row) => {
      const value = column.property.split('.').reduce((obj, key) => (obj || {})[key], row)
      return sum + (typeof value === 'number' ? value : 0)
    }, 0)
    return Math.round(total * 100) / 100
  })
}

const handleSearch = () => {
  fetchData()
  if (activeTab.value === 'confirmation') {
    fetchConfirmations()
  }
}

// ==================== 每月考勤确认单 ====================
const confEmployees = ref([])
const confLoading = ref(false)
const confSending = ref(false)
const mailConfigured = ref(true)

const sentCount = computed(() => confEmployees.value.filter(e => e.status === 'sent').length)

// 前端关键词过滤（工号/姓名/账号）
const displayedConfEmployees = computed(() => {
  const kw = filterForm.value.keyword.trim().toLowerCase()
  if (!kw) return confEmployees.value
  return confEmployees.value.filter(emp =>
    (emp.employee_id || '').toLowerCase().includes(kw) ||
    (emp.name || '').toLowerCase().includes(kw) ||
    (emp.username || '').toLowerCase().includes(kw) ||
    (emp.recipient_email || '').toLowerCase().includes(kw)
  )
})

const fetchConfirmations = async () => {
  confLoading.value = true
  try {
    const params = { month: filterForm.value.month }
    if (filterForm.value.department) {
      params.department = filterForm.value.department
    }
    const res = await apiService.attendance.getConfirmations(params)
    confEmployees.value = (res.employees || []).map(e => ({ ...e, _sending: false }))
    mailConfigured.value = res.mail_configured !== false
  } catch (e) {
    console.error('获取考勤确认单列表失败:', e)
    ElMessage.error(e.response?.data?.error || '获取考勤确认单列表失败')
  } finally {
    confLoading.value = false
  }
}

const onTabChange = (name) => {
  if (name === 'confirmation' && confEmployees.value.length === 0) {
    fetchConfirmations()
  }
}

// 发送结果统一提示
const showSendResult = (res) => {
  const { sent = 0, failed = 0, total = 0, details = [] } = res || {}
  if (failed === 0) {
    ElMessage.success(`发送完成：成功 ${sent} / 共 ${total} 份`)
  } else if (sent > 0) {
    ElMessage.warning(`发送完成：成功 ${sent} 份，失败 ${failed} 份`)
  } else {
    ElMessage.error(`发送失败：${failed} 份`)
  }
  if (failed > 0) {
    const failLines = details
      .filter(d => d.status === 'failed')
      .slice(0, 15)
      .map(d => `· ${d.name || d.user_id}${d.email ? '（' + d.email + '）' : ''}：${d.error || '失败'}`)
      .join('\n')
    ElMessageBox.alert(failLines, `失败明细（${failed} 份）`, {
      confirmButtonText: '知道了',
      type: 'warning'
    }).catch(() => {})
  }
  fetchConfirmations()
}

// 确认单数值展示：0/空 显示为空白（与邮件确认单表格一致）
const showStat = (v) => (v === null || v === undefined || v === '' || Number(v) === 0) ? '' : v

// 确认单对话框：mode='edit' 点击行编辑保存草稿；mode='confirm' 点发送按钮只读确认
const confDialog = reactive({
  visible: false,
  mode: 'edit',
  sending: false,
  saving: false,
  user_id: null,
  name: '',
  email: '',
  stats: {}
})

const confReadonly = computed(() => confDialog.mode === 'confirm')

const emptyStats = () => ({
  full_attendance_bonus: 200,
  late_under10: 0,
  late_under30: 0,
  personal_h: 0,
  sick_h: 0,
  annual_h: 0,
  other_leave_h: 0,
  ot_weekday: 0,
  ot_rest: 0,
  ot_holiday: 0,
  other_h: 0,
  missing: 0,
  remark: ''
})

// 打开对话框：预填该员工已核对/系统计算的完整数据
const openConfDialog = (row, mode) => {
  confDialog.user_id = row.user_id
  confDialog.name = row.name
  confDialog.email = row.recipient_email
  confDialog.stats = { ...emptyStats(), ...(row.stats || {}) }
  if (confDialog.stats.full_attendance_bonus === null || confDialog.stats.full_attendance_bonus === undefined) {
    confDialog.stats.full_attendance_bonus = 200
  }
  confDialog.mode = mode
  confDialog.sending = false
  confDialog.saving = false
  confDialog.visible = true
}

// 点击表格行：进入编辑模式（修改并保存草稿）
const handleRowClick = (row) => {
  openConfDialog(row, 'edit')
}

// 点击「发送确认单」按钮：只读展示确认，确认后直接发送
const handleSendOne = (row) => {
  openConfDialog(row, 'confirm')
}

// 保存人工核对数据（直接生效，不发邮件）
const saveConfDraft = async () => {
  confDialog.saving = true
  try {
    await apiService.attendance.saveConfirmation({
      month: filterForm.value.month,
      user_id: confDialog.user_id,
      stats: confDialog.stats
    })
    ElMessage.success('已保存')
    confDialog.visible = false
    fetchConfirmations()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '保存失败')
  } finally {
    confDialog.saving = false
  }
}

// 发送：仅做显示确认，数据以已保存内容为准（后端读取）
const confirmSendOne = async () => {
  confDialog.sending = true
  try {
    const res = await apiService.attendance.sendConfirmations({
      month: filterForm.value.month,
      user_ids: [confDialog.user_id]
    })
    confDialog.visible = false
    showSendResult(res)
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '发送失败')
  } finally {
    confDialog.sending = false
  }
}

// 全部发送（按当前关键词筛选结果，仅发送有邮箱的员工）
const handleSendAll = async () => {
  const targets = displayedConfEmployees.value.filter(e => e.has_email)
  const noEmail = displayedConfEmployees.value.length - targets.length
  if (targets.length === 0) {
    ElMessage.warning('当前筛选结果中没有可发送的员工（均未配置邮箱）')
    return
  }
  try {
    await ElMessageBox.confirm(
      `即将向【${targets.length} 名员工】发送 ${filterForm.value.month} 考勤确认单` +
      (noEmail > 0 ? `；另有 ${noEmail} 人因未配置邮箱将跳过。` : '。') +
      '确认发送？',
      '批量发送确认单',
      { confirmButtonText: '确认发送', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }
  confSending.value = true
  try {
    const payload = {
      month: filterForm.value.month,
      user_ids: targets.map(e => e.user_id)
    }
    if (filterForm.value.department) {
      payload.department = filterForm.value.department
    }
    const res = await apiService.attendance.sendConfirmations(payload)
    showSendResult(res)
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '发送失败')
  } finally {
    confSending.value = false
  }
}

// 导出 Excel（后端按当前筛选的月份/部门导出全量数据）
const handleExport = async () => {
  exporting.value = true
  try {
    const params = { month: filterForm.value.month }
    if (filterForm.value.department) {
      params.department = filterForm.value.department
    }
    const response = await apiService.attendance.exportEmployeeSummary(params)
    if (response && response.data) {
      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `员工考勤记录_${filterForm.value.month}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    }
  } catch (e) {
    console.error('导出员工考勤记录失败:', e)
    ElMessage.error(e.response?.data?.error || '导出失败')
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  // 页面访问守卫：无权限用户跳回个人工作台
  if (!canAccess.value) {
    ElMessage.warning('权限不足，仅超级管理员、总经理、人事经理、人事专员可查看员工考勤记录')
    router.replace('/dashboard')
    return
  }
  fetchDepartments()
  fetchData()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.employee-attendance-container {
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  min-height: 100%;
}

/* 页面头部 - 玻璃拟态风格 */
.page-header {
  position: relative;
  margin-bottom: 24px;
  padding: 28px 32px;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px -10px rgba(56, 189, 248, 0.4);
}

.page-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at top right, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse at bottom left, rgba(14, 165, 233, 0.3) 0%, transparent 50%);
  pointer-events: none;
}

.header-bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.3;
}

.orb-1 {
  width: 200px;
  height: 200px;
  background: #f093fb;
  top: -50px;
  right: 10%;
  animation: float 6s ease-in-out infinite;
}

.orb-2 {
  width: 150px;
  height: 150px;
  background: #4facfe;
  bottom: -30px;
  right: 30%;
  animation: float 8s ease-in-out infinite reverse;
}

.header-content {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 20px;
}

.title-icon-wrapper {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.title-icon {
  font-size: 32px;
  color: white;
}

.title-text h1 {
  margin: 0 0 6px 0;
  color: white;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.subtitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 8px 24px -6px rgba(15, 23, 42, 0.08);
  transition: all 0.3s ease;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 32px -8px rgba(15, 23, 42, 0.15);
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  opacity: 0;
  transition: opacity 0.3s;
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-card-total::before {
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
}

.stat-card-attendance::before {
  background: linear-gradient(90deg, #38bdf8, #0ea5e9);
}

.stat-card-leave::before {
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
}

.stat-card-overtime::before {
  background: linear-gradient(90deg, #a78bfa, #8b5cf6);
}

.stat-icon-wrapper {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  flex-shrink: 0;
}

.stat-icon-wrapper-total {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  box-shadow: 0 8px 16px -4px rgba(99, 102, 241, 0.5);
}

.stat-icon-wrapper-attendance {
  background: linear-gradient(135deg, #38bdf8, #0ea5e9);
  box-shadow: 0 8px 16px -4px rgba(14, 165, 233, 0.5);
}

.stat-icon-wrapper-leave {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  box-shadow: 0 8px 16px -4px rgba(245, 158, 11, 0.5);
}

.stat-icon-wrapper-overtime {
  background: linear-gradient(135deg, #a78bfa, #8b5cf6);
  box-shadow: 0 8px 16px -4px rgba(139, 92, 246, 0.5);
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 26px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

/* 筛选与表格卡片 */
.filter-card,
.glass-card {
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.filter-section,
.content-section {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
}

.filter-select {
  width: 180px;
}

.filter-input {
  width: 220px;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-title h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.total-count {
  margin-left: 8px;
  font-size: 13px;
  color: #94a3b8;
}

/* 表格内容样式 */
.employee-id {
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-weight: 600;
  color: #0c4a6e;
}

.employee-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name-avatar {
  background: linear-gradient(135deg, #38bdf8, #0ea5e9);
  color: white;
  font-size: 13px;
  flex-shrink: 0;
}

.no-data {
  color: #cbd5e1;
}

.annual-tag {
  font-weight: 600;
}

/* 考勤确认表 */
.attendance-tabs {
  margin-top: 4px;
}

:deep(.attendance-tabs .el-tabs__header) {
  margin-bottom: 18px;
}

:deep(.attendance-tabs .el-tabs__item) {
  font-size: 16px;
  font-weight: 700;
  color: #64748b;
}

:deep(.attendance-tabs .el-tabs__item.is-active) {
  color: #0ea5e9;
}

.btn-gradient-send {
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  border: none;
  color: #fff;
  font-weight: 600;
  box-shadow: 0 6px 16px -4px rgba(245, 158, 11, 0.45);
}

.btn-gradient-send:hover {
  background: linear-gradient(135deg, #fbbf24 0%, #fb923c 100%);
  color: #fff;
}

.conf-email {
  font-size: 13px;
  color: #0c4a6e;
  word-break: break-all;
}

.conf-error {
  font-size: 12px;
  color: #dc2626;
  margin-top: 4px;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conf-time {
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

.conf-sender {
  font-size: 12px;
  color: #94a3b8;
}

.conf-red {
  color: #dc2626;
  font-weight: 700;
}

.conf-blue {
  color: #1f4e9b;
  font-weight: 700;
}

.conf-remark {
  font-size: 12px;
  color: #b45309;
}

/* 确认表行可点击编辑：显示手型（拖拽时仍由全局插件显示 grabbing） */
.conf-table .el-table__body-wrapper .el-table__row td {
  cursor: pointer;
}

/* 确认单核对编辑表格 */
.conf-edit-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  table-layout: fixed;
}

.conf-edit-table th,
.conf-edit-table td {
  border: 1px solid #dcdfe6;
  padding: 6px 4px;
  text-align: center;
  background: #fff;
  vertical-align: middle;
}

.conf-edit-table thead th {
  background: #f8fafc;
  font-weight: 600;
  color: #0f172a;
}

.conf-edit-table .th-red {
  color: #dc2626;
}

.conf-edit-table .th-blue {
  color: #1f4e9b;
}

/* 输入框统一撑满单元格、高度/字号一致、数字居中，保证各列对齐协调 */
.conf-edit-table .el-input-number,
.conf-edit-table .el-input {
  width: 100%;
  display: block;
}

.conf-edit-table :deep(.el-input__wrapper) {
  padding: 0 6px;
  min-height: 30px;
}

.conf-edit-table :deep(.el-input__inner) {
  height: 30px;
  line-height: 30px;
  font-size: 13px;
  text-align: center;
}

/* 备注为文本，左对齐并留内边距，避免与数字列混排时显得突兀 */
.conf-edit-table .conf-remark-input :deep(.el-input__inner) {
  text-align: left;
  padding-left: 8px;
  color: #b45309;
}

.conf-num-red :deep(.el-input__inner) {
  color: #dc2626;
  font-weight: 700;
}

.conf-num-blue :deep(.el-input__inner) {
  color: #1f4e9b;
  font-weight: 700;
}

/* 表格底色 */
.custom-table {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
}

/* 多级表头背景 */
:deep(.el-table__header-wrapper th) {
  background: #f8fafc;
  font-weight: 600;
  color: #0f172a;
}

:deep(.el-table__footer .cell) {
  font-weight: 700;
  color: #0f172a;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-12px);
  }
}

/* 动画 */
.animate-fade-in-down {
  animation: fadeInDown 0.5s ease-out;
}

.animate-fade-in-up {
  animation: fadeInUp 0.5s ease-out;
}

.delay-100 {
  animation-delay: 0.1s;
  animation-fill-mode: backwards;
}

.delay-200 {
  animation-delay: 0.2s;
  animation-fill-mode: backwards;
}

.delay-300 {
  animation-delay: 0.3s;
  animation-fill-mode: backwards;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
