<template>
  <div class="activity-list-container">
    <div class="page-header">
      <h1>活动记录</h1>
      <p>查看系统中的所有活动记录</p>
    </div>

    <div class="filter-section">
      <el-card class="filter-card">
        <el-form :model="filterForm" inline>
          <el-form-item label="资源类型">
            <el-select v-model="filterForm.resource_type" placeholder="请选择资源类型" clearable>
              <el-option label="项目" value="project"></el-option>
              <el-option label="缺陷" value="bug"></el-option>
              <el-option label="任务" value="task"></el-option>
              <el-option label="用户" value="user"></el-option>
              <el-option label="请假申请" value="leave_application"></el-option>
              <el-option label="加班申请" value="overtime_application"></el-option>
              <el-option label="考勤" value="attendance"></el-option>
              <el-option label="物料" value="material"></el-option>
              <el-option label="合同" value="contract"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="操作类型">
            <el-select v-model="filterForm.action" placeholder="请选择操作类型" clearable>
              <el-option label="创建" value="create"></el-option>
              <el-option label="更新" value="update"></el-option>
              <el-option label="删除" value="delete"></el-option>
              <el-option label="状态变更" value="status_change"></el-option>
              <el-option label="分配" value="assign"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="用户">
            <el-input v-model="filterForm.user_name" placeholder="输入用户名" clearable></el-input>
          </el-form-item>
          
          <el-form-item label="日期范围">
            <el-date-picker
              v-model="filterForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD">
            </el-date-picker>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handleSearch" :loading="loading">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <div class="content-section">
      <el-card>
        <div class="table-header">
          <div class="table-title">
            <h3>活动记录列表</h3>
            <span class="total-count">共 {{ total }} 条记录</span>
          </div>
          <div class="table-actions">
            <el-button @click="refreshData" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button @click="exportData">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </div>
        </div>

        <el-table
          :data="activities"
          v-loading="loading"
          stripe
          style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
          
          <el-table-column label="操作类型" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getActionType(row.action)" size="small">
                {{ getActionText(row.action) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="资源类型" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getResourceType(row.resource_type)" size="small">
                {{ getResourceText(row.resource_type) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="资源信息" min-width="200">
            <template #default="{ row }">
              <div class="resource-info">
                <div class="resource-name">{{ row.resource_name || '未知资源' }}</div>
                <div class="resource-id">ID: {{ row.resource_id }}</div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="操作内容" min-width="300">
            <template #default="{ row }">
              <div class="action-content">
                <div class="action-text">{{ row.description }}</div>
                <div class="changes" v-if="row.changes">
                  <el-tag v-for="change in getChanges(row.changes)" :key="change.field" size="small" type="info" class="change-tag">
                    {{ change.field }}: {{ change.from }} → {{ change.to }}
                  </el-tag>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="操作用户" width="150">
            <template #default="{ row }">
              <div class="user-info">
                <div class="user-name">{{ row.user_name || '未知用户' }}</div>
                <div class="user-role">{{ row.user_role || '' }}</div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="操作时间" width="180" align="center">
            <template #default="{ row }">
              <div class="timestamp">
                <div>{{ formatDate(row.created_at) }}</div>
                <div class="time-ago">{{ getTimeAgo(row.created_at) }}</div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="viewDetail(row)">
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
import { Search, Refresh, Download, View } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'
import { formatDate, getTimeAgo } from '@/utils/dateUtils'

// 响应式数据
const loading = ref(false)
const activities = ref([])
const total = ref(0)

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
  const types = {
    'create': 'success',
    'create_bug': 'success',
    'create_leave_application': 'success',
    'apply_leave': 'success',
    'apply_overtime': 'success',
    'update': 'warning',
    'update_bug': 'warning',
    'delete': 'danger',
    'status_change': 'info',
    'bug_status_update': 'info',
    'bug_status_transition': 'info',
    'assign': 'primary',
    'assign_bug': 'primary',
    'approve': 'warning',
    'approve_leave_application': 'warning',
    'approve_overtime_application': 'warning',
    'approve_exception': 'warning',
    'clock_in': 'primary',
    'clock_out': 'primary'
  }
  return types[action] || 'info'
}

// 获取操作类型文本
const getActionText = (action) => {
  const texts = {
    'create': '创建',
    'create_bug': '创建Bug',
    'create_leave_application': '创建请假申请',
    'apply_leave': '提交请假',
    'apply_overtime': '提交加班',
    'update': '更新',
    'update_bug': '更新Bug',
    'delete': '删除',
    'status_change': '状态变更',
    'bug_status_update': 'Bug状态更新',
    'bug_status_transition': 'Bug状态转换',
    'assign': '分配',
    'assign_bug': '分配Bug',
    'approve': '审批',
    'approve_leave_application': '审批请假',
    'approve_overtime_application': '审批加班',
    'approve_exception': '审批异常',
    'clock_in': '上班打卡',
    'clock_out': '下班打卡'
  }
  return texts[action] || action
}

// 获取资源类型样式
const getResourceType = (resourceType) => {
  const types = {
    'project': 'success',
    'bug': 'danger',
    'task': 'warning',
    'user': 'info',
    'leave_application': 'warning',
    'overtime_application': 'warning',
    'attendance': 'primary',
    'material': 'info',
    'contract': 'success'
  }
  return types[resourceType] || 'info'
}

// 获取资源类型文本
const getResourceText = (resourceType) => {
  const texts = {
    'project': '项目',
    'bug': '缺陷',
    'task': '任务',
    'user': '用户',
    'leave_application': '请假申请',
    'overtime_application': '加班申请',
    'attendance': '考勤',
    'material': '物料',
    'contract': '合同'
  }
  return texts[resourceType] || resourceType
}

// 解析变更数据
const getChanges = (changes) => {
  if (!changes || typeof changes !== 'object') return []
  
  try {
    if (typeof changes === 'string') {
      changes = JSON.parse(changes)
    }
    
    return Object.keys(changes).map(field => ({
      field: field,
      from: changes[field].from || '',
      to: changes[field].to || ''
    }))
  } catch (error) {
    return []
  }
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
      ${activity.changes ? `<p><strong>变更详情：</strong></p><pre>${JSON.stringify(JSON.parse(activity.changes), null, 2)}</pre>` : ''}
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

// 生命周期
onMounted(() => {
  loadActivities()
})
</script>

<style scoped>
.activity-list-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.page-header p {
  margin: 5px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-card {
  margin-bottom: 0;
}

.content-section {
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.total-count {
  font-size: 14px;
  color: #909399;
  margin-left: 10px;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.resource-info {
  line-height: 1.4;
}

.resource-name {
  font-weight: 500;
  color: #303133;
}

.resource-id {
  font-size: 12px;
  color: #909399;
}

.action-content {
  line-height: 1.4;
}

.action-text {
  margin-bottom: 5px;
  color: #303133;
}

.changes {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.change-tag {
  margin: 2px;
}

.user-info {
  line-height: 1.4;
}

.user-name {
  font-weight: 500;
  color: #303133;
}

.user-role {
  font-size: 12px;
  color: #909399;
}

.timestamp {
  line-height: 1.4;
}

.time-ago {
  font-size: 12px;
  color: #909399;
}

.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

:deep(.activity-detail-dialog) {
  max-width: 600px;
}

:deep(.activity-detail-dialog pre) {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
  margin-top: 10px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .activity-list {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  .page-header h2 {
    font-size: 18px;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 80px;
    font-size: 12px;
    padding: 8px 12px;
  }

  .filter-card {
    margin-bottom: 16px;
  }

  .filter-form {
    flex-direction: column;
    gap: 12px;
  }

  .filter-form .el-form-item {
    margin-right: 0;
    margin-bottom: 8px;
    width: 100%;
  }

  .filter-form .el-input,
  .filter-form .el-select,
  .filter-form .el-date-picker {
    width: 100% !important;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
  }

  .pagination-container {
    justify-content: center;
    margin-top: 16px;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
  }
}

@media screen and (max-width: 480px) {
  .activity-list {
    padding: 8px;
  }

  .el-table {
    font-size: 10px !important;
  }
}
</style>