<template>
  <div class="activity-list-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Clock /></el-icon>
          </div>
          <div class="title-text">
            <h1>活动记录</h1>
            <p class="subtitle">查看系统中的所有活动记录</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-total">
            <div class="stat-icon-wrapper stat-icon-wrapper-total">
              <el-icon><List /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.total }}</div>
              <div class="stat-label">总记录数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-create">
            <div class="stat-icon-wrapper stat-icon-wrapper-create">
              <el-icon><CirclePlus /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.create_count }}</div>
              <div class="stat-label">创建操作</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-update">
            <div class="stat-icon-wrapper stat-icon-wrapper-update">
              <el-icon><Edit /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.update_count }}</div>
              <div class="stat-label">更新操作</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-today">
            <div class="stat-icon-wrapper stat-icon-wrapper-today">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.today_count }}</div>
              <div class="stat-label">今日记录</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

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
          <el-form-item label="资源类型">
            <el-select v-model="filterForm.resource_type" placeholder="请选择资源类型" clearable class="filter-select" filterable>
              <el-option label="项目" value="project"></el-option>
              <el-option label="缺陷" value="bug"></el-option>
              <el-option label="用户" value="user"></el-option>
              <el-option label="项目成员" value="project_member"></el-option>
              <el-option label="工作日志" value="work_log"></el-option>
              <el-option label="项目日志" value="project_log"></el-option>
              <el-option label="需求文档" value="requirement_document"></el-option>
              <el-option label="需求条目" value="requirement_item"></el-option>
              <el-option label="个人任务" value="personal_task"></el-option>
              <el-option label="任务模板" value="personal_template"></el-option>
              <el-option label="知识文章" value="knowledge_article"></el-option>
              <el-option label="知识分类" value="knowledge_category"></el-option>
              <el-option label="请假申请" value="leave_application"></el-option>
              <el-option label="加班申请" value="overtime_application"></el-option>
              <el-option label="考勤" value="attendance"></el-option>
              <el-option label="班次" value="shift_schedule"></el-option>
              <el-option label="排班" value="user_shift"></el-option>
              <el-option label="风险" value="risk"></el-option>
              <el-option label="测试套件" value="test_suite"></el-option>
              <el-option label="测试用例" value="test_case"></el-option>
              <el-option label="物料" value="material"></el-option>
              <el-option label="合同" value="contract"></el-option>
              <el-option label="数据" value="data"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="操作类型">
            <el-select v-model="filterForm.action" placeholder="请选择操作类型" clearable class="filter-select" filterable>
              <el-option label="创建" value="create"></el-option>
              <el-option label="更新" value="update"></el-option>
              <el-option label="删除" value="delete"></el-option>
              <el-option label="状态变更" value="status"></el-option>
              <el-option label="分配" value="assign"></el-option>
              <el-option label="审批" value="approve"></el-option>
              <el-option label="拒绝" value="reject"></el-option>
              <el-option label="打卡" value="clock"></el-option>
              <el-option label="上传附件" value="upload"></el-option>
              <el-option label="删除附件" value="delete_attachment"></el-option>
              <el-option label="导出" value="export"></el-option>
              <el-option label="导入" value="import"></el-option>
              <el-option label="登录" value="login"></el-option>
              <el-option label="注册" value="register"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="用户">
            <el-input v-model="filterForm.user_name" placeholder="输入用户名" clearable class="filter-input"></el-input>
          </el-form-item>
          
          <el-form-item label="日期范围">
            <el-date-picker
              v-model="filterForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              class="date-picker">
            </el-date-picker>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handleSearch" :loading="loading" class="btn-gradient">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset" class="btn-secondary">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <div class="content-section animate-fade-in-up delay-300">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="table-header">
            <div class="table-title">
              <el-icon><Document /></el-icon>
              <h3>活动记录列表</h3>
              <span class="total-count">共 {{ total }} 条记录</span>
            </div>
            <div class="table-actions">
              <el-button @click="refreshData" :loading="loading" class="btn-refresh">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
              <el-button @click="exportData" class="btn-export">
                <el-icon><Download /></el-icon>
                导出
              </el-button>
            </div>
          </div>
        </template>

        <el-table
          :data="activities"
          v-loading="loading"
          stripe
          class="custom-table"
          style="width: 100%">
          <el-table-column prop="id" label="ID" width="70" align="center">
            <template #default="{ row }">
              <span class="id-badge">{{ row.id }}</span>
            </template>
          </el-table-column>
          
          <el-table-column label="操作类型" width="110" align="center">
            <template #default="{ row }">
              <el-tag :type="getActionType(row.action)" size="small" effect="light" class="action-tag">
                {{ getActionText(row.action) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="资源类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getResourceType(row.resource_type)" size="small" effect="light" class="resource-tag">
                {{ getResourceText(row.resource_type) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="资源信息" min-width="180">
            <template #default="{ row }">
              <div class="resource-info">
                <div class="resource-name">{{ row.resource_name || '未知资源' }}</div>
                <div class="resource-id">ID: {{ row.resource_id }}</div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="操作内容" min-width="250">
            <template #default="{ row }">
              <div class="action-content">
                <div class="action-text">{{ row.description }}</div>
                <div class="changes" v-if="row.field_changes && row.field_changes.length">
                  <el-tag v-for="(change, idx) in getChanges(row.field_changes)" :key="idx" size="small" type="info" effect="light" class="change-tag">
                    {{ change.field }}: {{ change.from }} → {{ change.to }}
                  </el-tag>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="操作用户" width="140">
            <template #default="{ row }">
              <div class="user-info">
                <div class="user-name">{{ row.user_name || '未知用户' }}</div>
                <div class="user-role">{{ row.user_role || '' }}</div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="操作时间" width="160" align="center">
            <template #default="{ row }">
              <div class="timestamp">
                <div class="time-main">{{ formatDate(row.created_at) }}</div>
                <div class="time-ago">{{ getTimeAgo(row.created_at) }}</div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="90" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewDetail(row)" class="view-btn">
                <el-icon><View /></el-icon>
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-section">
          <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange">
          </el-pagination>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Download, View, Clock, List, CirclePlus, Edit, Calendar, Filter, Document } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'
import { formatDate, getTimeAgo } from '@/utils/dateUtils'

// 响应式数据
const loading = ref(false)
const activities = ref([])
const total = ref(0)

// 统计数据（从后端获取全量统计）
const stats = ref({
  total: 0,
  create_count: 0,
  update_count: 0,
  delete_count: 0,
  today_count: 0
})

const loadStatistics = async () => {
  try {
    const response = await apiService.activities.getStatistics()
    stats.value = response
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 分页配置
const pagination = reactive({
  currentPage: 1,
  pageSize: 20
})

// 筛选表单
const filterForm = reactive({
  resource_type: '',
  action: '',
  user_name: '',
  dateRange: []
})

// 获取操作类型样式
const getActionType = (action) => {
  if (!action) return 'info'
  if (action.includes('create') || action.includes('register')) return 'success'
  if (action.includes('update') || action.includes('approve')) return 'warning'
  if (action.includes('delete') || action.includes('reject') || action.includes('remove')) return 'danger'
  if (action.includes('assign') || action.includes('add')) return 'primary'
  if (action.includes('clock') || action.includes('upload')) return 'primary'
  if (action.includes('login') || action.includes('logout')) return 'info'
  if (action.includes('status') || action.includes('transition')) return 'info'
  if (action.includes('export') || action.includes('batch')) return 'info'
  return 'info'
}

// 获取操作类型文本
const getActionText = (action) => {
  const texts = {
    'create': '创建',
    'create_bug': '创建Bug',
    'create_project': '创建项目',
    'create_project_log': '创建日志',
    'update': '更新',
    'update_bug': '更新Bug',
    'update_project': '更新项目',
    'update_project_log': '更新日志',
    'update_project_member': '更新成员',
    'delete': '删除',
    'delete_project': '删除项目',
    'delete_attachment': '删除附件',
    'bug_status_update': '状态更新',
    'bug_status_transition': '状态转换',
    'assign_bug': '分配',
    'add_project_member': '添加成员',
    'remove_project_member': '移除成员',
    'approve': '审批通过',
    'reject': '审批拒绝',
    'clock_in': '上班打卡',
    'clock_out': '下班打卡',
    'upload_attachment': '上传附件',
    'export': '导出',
    'user_register': '用户注册',
    'user_login': '用户登录',
    'batch_create': '批量创建',
    'import': '导入'
  }
  return texts[action] || action
}

// 获取资源类型样式
const getResourceType = (resourceType) => {
  const types = {
    'project': 'success',
    'bug': 'danger',
    'user': 'info',
    'project_member': 'primary',
    'work_log': 'success',
    'project_log': 'success',
    'requirement_document': 'primary',
    'requirement_item': 'primary',
    'requirement_comment': 'info',
    'requirement_link': 'info',
    'requirement_version': 'info',
    'personal_task': 'warning',
    'personal_template': 'warning',
    'personal_review': 'success',
    'knowledge_article': 'success',
    'knowledge_category': 'info',
    'knowledge_comment': 'info',
    'leave_application': 'warning',
    'overtime_application': 'warning',
    'attendance': 'primary',
    'attendance_report': 'primary',
    'shift_schedule': 'info',
    'user_shift': 'info',
    'risk': 'danger',
    'test_suite': 'warning',
    'test_case': 'warning',
    'material': 'info',
    'contract': 'success',
    'data': 'info'
  }
  return types[resourceType] || 'info'
}

// 获取资源类型文本
const getResourceText = (resourceType) => {
  const texts = {
    'project': '项目',
    'bug': '缺陷',
    'user': '用户',
    'project_member': '项目成员',
    'work_log': '工作日志',
    'project_log': '项目日志',
    'requirement_document': '需求文档',
    'requirement_item': '需求条目',
    'requirement_comment': '需求评论',
    'requirement_link': '需求关联',
    'requirement_version': '需求版本',
    'personal_task': '个人任务',
    'personal_template': '任务模板',
    'personal_review': '复盘',
    'knowledge_article': '知识文章',
    'knowledge_category': '知识分类',
    'knowledge_comment': '知识评论',
    'leave_application': '请假申请',
    'overtime_application': '加班申请',
    'attendance': '考勤',
    'attendance_report': '考勤报表',
    'shift_schedule': '班次',
    'user_shift': '排班',
    'risk': '风险',
    'test_suite': '测试套件',
    'test_case': '测试用例',
    'material': '物料',
    'contract': '合同',
    'data': '数据'
  }
  return texts[resourceType] || resourceType
}

// 解析变更数据
const getChanges = (changes) => {
  if (!changes) return []

  try {
    if (typeof changes === 'string') {
      changes = JSON.parse(changes)
    }

    if (Array.isArray(changes)) {
      return changes.map(c => ({
        field: c.field || c.field_label || '',
        from: c.old_value || c.from || '',
        to: c.new_value || c.to || ''
      }))
    }

    if (typeof changes === 'object') {
      return Object.keys(changes).map(field => ({
        field: field,
        from: changes[field].from || changes[field].old_value || '',
        to: changes[field].to || changes[field].new_value || ''
      }))
    }
  } catch (error) {
    return []
  }
  return []
}

// 加载数据
const loadActivities = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      per_page: pagination.pageSize,
      ...filterForm
    }
    
    // 处理日期范围
    if (filterForm.dateRange && filterForm.dateRange.length === 2) {
      params.start_date = filterForm.dateRange[0]
      params.end_date = filterForm.dateRange[1]
    }
    
    const response = await apiService.activities.getList(params)
    activities.value = response.activities || []
    total.value = response.total || 0
  } catch (error) {
    console.error('加载活动记录失败:', error)
    ElMessage.error('加载活动记录失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.currentPage = 1
  loadActivities()
}

// 重置筛选
const handleReset = () => {
  Object.keys(filterForm).forEach(key => {
    if (Array.isArray(filterForm[key])) {
      filterForm[key] = []
    } else {
      filterForm[key] = ''
    }
  })
  pagination.currentPage = 1
  loadActivities()
}

// 刷新数据
const refreshData = () => {
  loadActivities()
  loadStatistics()
}

// 导出数据
const exportData = async () => {
  try {
    ElMessage.info('导出功能开发中...')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 查看详情
const viewDetail = (activity) => {
  ElMessageBox.alert(
    `<div>
      <p><strong>操作类型：</strong>${getActionText(activity.action)}</p>
      <p><strong>资源类型：</strong>${getResourceText(activity.resource_type)}</p>
      <p><strong>资源名称：</strong>${activity.resource_name || '未知'}</p>
      <p><strong>资源ID：</strong>${activity.resource_id}</p>
      <p><strong>操作用户：</strong>${activity.user_name || '未知用户'}</p>
      <p><strong>操作时间：</strong>${formatDate(activity.created_at)}</p>
      <p><strong>操作描述：</strong>${activity.description}</p>
      ${activity.field_changes && activity.field_changes.length ? `<p><strong>变更详情：</strong></p><pre>${JSON.stringify(activity.field_changes, null, 2)}</pre>` : ''}
    </div>`,
    '活动记录详情',
    {
      dangerouslyUseHTMLString: true,
      customClass: 'activity-detail-dialog'
    }
  )
}

// 分页事件处理
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadActivities()
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
  loadActivities()
}

onMounted(() => {
  loadActivities()
  loadStatistics()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.activity-list-container {
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

.page-header::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.5;
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
  font-weight: 400;
}

/* 统计卡片区域 */
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.stat-card::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  transform: scaleX(0);
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.15), 0 10px 20px -5px rgba(0, 0, 0, 0.1);
}

.stat-card:hover::before {
  transform: scaleX(1);
}

.stat-card-total::before { background: linear-gradient(90deg, #7dd3fc, #38bdf8); }
.stat-card-create::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-update::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-today::before { background: linear-gradient(90deg, #ec4899, #f472b6); }

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: all 0.4s;
}

.stat-card:hover .stat-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.stat-icon-wrapper-total {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #7dd3fc;
  box-shadow: 0 4px 15px -3px rgba(56, 189, 248, 0.4);
}

.stat-icon-wrapper-create {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-update {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-today {
  background: linear-gradient(135deg, #fce7f3 0%, #f9a8d4 100%);
  color: #db2777;
  box-shadow: 0 4px 15px -3px rgba(236, 72, 153, 0.4);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 26px;
  font-weight: 800;
  line-height: 1.2;
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-card-total .stat-value {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-create .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-update .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-today .stat-value {
  background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
}

/* 玻璃拟态卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  transition: all 0.4s;
}

.glass-card:hover {
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.12), 0 10px 20px -5px rgba(0, 0, 0, 0.08);
}

/* 筛选区域 */
.filter-section {
  margin-bottom: 24px;
}

.filter-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
}

.card-title .el-icon {
  color: #0ea5e9;
  font-size: 18px;
}

.filter-form {
  padding: 10px 0;
}

.filter-select,
.filter-input {
  width: 160px;
}

.date-picker {
  width: 260px;
}

/* 按钮样式 */
.btn-gradient {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.5);
}

.btn-secondary {
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(56, 189, 248, 0.1);
  border-color: #0ea5e9;
  color: #0ea5e9;
}

.btn-refresh,
.btn-export {
  transition: all 0.3s;
}

.btn-refresh:hover,
.btn-export:hover {
  transform: translateY(-2px);
}

/* 内容区域 */
.content-section {
  margin-bottom: 20px;
}

/* 表格头部 */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-title .el-icon {
  color: #0ea5e9;
  font-size: 20px;
}

.table-title h3 {
  margin: 0;
  font-size: 16px;
  color: #1e293b;
  font-weight: 600;
}

.total-count {
  font-size: 13px;
  color: #64748b;
  margin-left: 8px;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 12px;
  border-radius: 20px;
}

.table-actions {
  display: flex;
  gap: 10px;
}

/* 自定义表格 */
.custom-table {
  --el-table-header-bg-color: rgba(241, 245, 249, 0.8);
  --el-table-row-hover-bg-color: rgba(56, 189, 248, 0.05);
}

.custom-table :deep(.el-table__header th) {
  font-weight: 600;
  color: #1e293b;
  background: rgba(241, 245, 249, 0.8);
}

.custom-table :deep(.el-table__row) {
  transition: all 0.3s;
}

.id-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
}

.action-tag,
.resource-tag {
  font-weight: 500;
  border-radius: 6px;
}

.resource-info {
  line-height: 1.4;
}

.resource-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.resource-id {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}

.action-content {
  line-height: 1.4;
}

.action-text {
  margin-bottom: 6px;
  color: #475569;
  font-size: 13px;
}

.changes {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.change-tag {
  margin: 2px;
  font-size: 11px;
}

.user-info {
  line-height: 1.4;
}

.user-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.user-role {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}

.timestamp {
  line-height: 1.4;
}

.time-main {
  font-size: 13px;
  color: #475569;
}

.time-ago {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}

.view-btn {
  opacity: 0;
  transition: all 0.3s;
}

.custom-table :deep(.el-table__row:hover) .view-btn {
  opacity: 1;
}

/* 分页 */
.pagination-section {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

/* 详情对话框 */
:deep(.activity-detail-dialog) {
  max-width: 600px;
  border-radius: 16px;
}

:deep(.activity-detail-dialog .el-message-box__header) {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  padding: 20px;
  border-radius: 16px 16px 0 0;
}

:deep(.activity-detail-dialog .el-message-box__title) {
  color: white;
  font-weight: 600;
}

:deep(.activity-detail-dialog .el-message-box__content) {
  padding: 24px;
}

:deep(.activity-detail-dialog pre) {
  background: #f8fafc;
  padding: 16px;
  border-radius: 10px;
  font-size: 12px;
  overflow-x: auto;
  margin-top: 12px;
  border: 1px solid #e2e8f0;
}

/* 动画 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-fade-in-down {
  animation: fadeInDown 0.6s ease-out;
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s ease-out;
  animation-fill-mode: both;
}

.delay-100 { animation-delay: 100ms; }
.delay-200 { animation-delay: 200ms; }
.delay-300 { animation-delay: 300ms; }

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .activity-list-container {
    padding: 0;
  }

  .page-header {
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 16px;
  }

  .header-title {
    gap: 14px;
  }

  .title-icon-wrapper {
    width: 48px;
    height: 48px;
    border-radius: 14px;
  }

  .title-icon {
    font-size: 24px;
  }

  .title-text h1 {
    font-size: 22px;
  }

  .subtitle {
    font-size: 13px;
  }

  .stats-row {
    margin-bottom: 20px;
  }

  .stat-card {
    padding: 16px;
    gap: 12px;
    margin-bottom: 12px;
  }

  .stat-icon-wrapper {
    width: 44px;
    height: 44px;
    border-radius: 12px;
  }

  .stat-value {
    font-size: 22px;
  }

  .stat-label {
    font-size: 12px;
  }

  .filter-form {
    flex-direction: column;
  }

  .filter-form .el-form-item {
    margin-right: 0;
    margin-bottom: 12px;
    width: 100%;
  }

  .filter-select,
  .filter-input,
  .date-picker {
    width: 100% !important;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .table-actions {
    width: 100%;
  }

  .table-actions .el-button {
    flex: 1;
  }

  .view-btn {
    opacity: 1;
  }

  .el-table {
    font-size: 12px !important;
  }

  .el-table th,
  .el-table td {
    padding: 8px 6px !important;
  }

  .pagination-section {
    justify-content: center;
  }
}

@media screen and (max-width: 480px) {
  .page-header {
    padding: 16px;
  }

  .title-text h1 {
    font-size: 20px;
  }

  .stat-card {
    padding: 14px;
  }

  .stat-value {
    font-size: 20px;
  }

  .el-table {
    font-size: 11px !important;
  }
}
</style>
