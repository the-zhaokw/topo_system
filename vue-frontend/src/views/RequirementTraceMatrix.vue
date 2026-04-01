<template>
  <div class="requirement-trace-matrix" v-loading="loading">
    <div class="page-header">
      <div class="header-left">
        <h2>需求跟踪矩阵</h2>
        <span class="subtitle">查看需求与下游工作项的对应关系</span>
      </div>
      <div class="header-right">
        <el-select v-model="selectedDocId" placeholder="选择需求文档" clearable style="width: 300px; margin-right: 12px;" @change="handleDocChange">
          <el-option
            v-for="doc in documents"
            :key="doc.id"
            :label="doc.name"
            :value="doc.id"
          />
        </el-select>
        <el-button @click="exportMatrix">
          <el-icon><Download /></el-icon>
          导出矩阵
        </el-button>
      </div>
    </div>

    <!-- 统计概览 -->
    <el-row :gutter="20" class="statistics-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ statistics.totalRequirements }}</div>
          <div class="stat-label">需求总数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ statistics.linkedRequirements }}</div>
          <div class="stat-label">已关联需求</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ statistics.totalTasks }}</div>
          <div class="stat-label">关联任务</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ statistics.totalBugs }}</div>
          <div class="stat-label">关联缺陷</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="需求状态">
          <el-select v-model="filters.itemStatus" placeholder="全部状态" clearable style="width: 150px;">
            <el-option label="待评审" value="pending_review" />
            <el-option label="已评审" value="reviewed" />
            <el-option label="已批准" value="approved" />
            <el-option label="开发中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已验证" value="verified" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="filters.priority" placeholder="全部优先级" clearable style="width: 120px;">
            <el-option label="高" :value="3" />
            <el-option label="中" :value="2" />
            <el-option label="低" :value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联类型">
          <el-select v-model="filters.linkType" placeholder="全部类型" clearable style="width: 150px;">
            <el-option label="已实现" value="implements" />
            <el-option label="已验证" value="verifies" />
            <el-option label="受影响" value="affects" />
            <el-option label="相关" value="related" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button @click="handleFilter">筛选</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 跟踪矩阵表格 -->
    <el-card class="matrix-card" v-if="matrixData.length > 0">
      <el-table :data="matrixData" border stripe style="width: 100%">
        <el-table-column prop="identifier" label="需求标识" width="120" fixed>
          <template #default="{ row }">
            <el-link type="primary" @click="goToRequirement(row)">{{ row.identifier }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="需求标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="任务" width="80" align="center">
          <template #default="{ row }">
            <span v-if="row.task_count > 0" class="link-count" @click="showLinkedItems(row, 'task')">
              {{ row.task_count }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="缺陷" width="80" align="center">
          <template #default="{ row }">
            <span v-if="row.bug_count > 0" class="link-count" @click="showLinkedItems(row, 'bug')">
              {{ row.bug_count }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="测试用例" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.test_case_count > 0" class="link-count" @click="showLinkedItems(row, 'test_case')">
              {{ row.test_case_count }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="owner_name" label="负责人" width="100" show-overflow-tooltip />
        <el-table-column label="覆盖率" width="120">
          <template #default="{ row }">
            <el-progress
              :percentage="row.coverage"
              :color="getCoverageColor(row.coverage)"
              :stroke-width="10"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="addLink(row)">
              添加关联
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-empty v-else description="请选择需求文档或调整筛选条件" />

    <!-- 关联详情对话框 -->
    <el-dialog v-model="showLinkDialog" title="关联详情" width="700px">
      <div v-if="currentItem">
        <h4>{{ currentItem.identifier }} - {{ currentItem.title }}</h4>
        <el-divider />
        <el-table :data="linkedItems" border style="width: 100%">
          <el-table-column prop="target_identifier" label="工作项标识" width="120">
            <template #default="{ row }">
              <el-link type="primary" @click="goToWorkItem(row)">
                {{ row.target_identifier }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column prop="target_title" label="工作项标题" min-width="200" show-overflow-tooltip />
          <el-table-column prop="link_type" label="关联类型" width="100">
            <template #default="{ row }">
              <el-tag size="small">{{ getLinkTypeText(row.link_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getWorkItemStatusType(row.status)" size="small">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="showLinkDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 添加关联对话框 -->
    <el-dialog v-model="showAddLinkDialog" title="添加工作项关联" width="500px">
      <el-form :model="linkForm" :rules="linkRules" ref="linkFormRef" label-width="100px">
        <el-form-item label="工作项类型" prop="targetType">
          <el-select v-model="linkForm.targetType" style="width: 100%;">
            <el-option label="任务" value="task" />
            <el-option label="缺陷" value="bug" />
            <el-option label="测试用例" value="test_case" />
          </el-select>
        </el-form-item>
        <el-form-item label="工作项ID" prop="targetId">
          <el-input-number v-model="linkForm.targetId" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="关联类型" prop="linkType">
          <el-select v-model="linkForm.linkType" style="width: 100%;">
            <el-option label="实现" value="implements" />
            <el-option label="验证" value="verifies" />
            <el-option label="影响" value="affects" />
            <el-option label="相关" value="related" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddLinkDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddLink" :loading="addingLink">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const documents = ref([])
const matrixData = ref([])
const linkedItems = ref([])
const selectedDocId = ref(null)
const currentItem = ref(null)

const showLinkDialog = ref(false)
const showAddLinkDialog = ref(false)
const addingLink = ref(false)

const filters = ref({
  itemStatus: '',
  priority: '',
  linkType: ''
})

const statistics = ref({
  totalRequirements: 0,
  linkedRequirements: 0,
  totalTasks: 0,
  totalBugs: 0
})

const linkFormRef = ref(null)
const linkForm = ref({
  targetType: 'task',
  targetId: null,
  linkType: 'implements'
})

const linkRules = {
  targetType: [{ required: true, message: '请选择工作项类型', trigger: 'change' }],
  targetId: [{ required: true, message: '请输入工作项ID', trigger: 'blur' }],
  linkType: [{ required: true, message: '请选择关联类型', trigger: 'change' }]
}

const projectId = computed(() => route.params.projectId)

const fetchDocuments = async () => {
  try {
    const response = await api.get(`/projects/${projectId.value}/requirement-documents`)
    if (response.success) {
      documents.value = response.documents || []
      if (documents.value.length > 0 && !selectedDocId.value) {
        selectedDocId.value = documents.value[0].id
        fetchMatrixData()
      }
    }
  } catch (error) {
    console.error('获取需求文档列表失败:', error)
  }
}

const fetchMatrixData = async () => {
  if (!selectedDocId.value) return

  loading.value = true
  try {
    const params = {
      ...filters.value
    }
    const response = await api.get(`/requirement-documents/${selectedDocId.value}/trace-matrix`, { params })
    if (response.success) {
      matrixData.value = response.matrix_data || []
      statistics.value = response.statistics || statistics.value
    }
  } catch (error) {
    console.error('获取跟踪矩阵失败:', error)
    ElMessage.error('获取跟踪矩阵失败')
  } finally {
    loading.value = false
  }
}

const handleDocChange = () => {
  fetchMatrixData()
}

const handleFilter = () => {
  fetchMatrixData()
}

const resetFilter = () => {
  filters.value = {
    itemStatus: '',
    priority: '',
    linkType: ''
  }
  fetchMatrixData()
}

const showLinkedItems = async (row, type) => {
  currentItem.value = row
  showLinkDialog.value = true

  try {
    const response = await api.get(`/requirement-items/${row.id}/links`)
    if (response.success) {
      linkedItems.value = (response.links || []).filter(link => link.target_type === type)
    }
  } catch (error) {
    console.error('获取关联详情失败:', error)
  }
}

const addLink = (row) => {
  currentItem.value = row
  linkForm.value = {
    targetType: 'task',
    targetId: null,
    linkType: 'implements'
  }
  showAddLinkDialog.value = true
}

const handleAddLink = async () => {
  if (!linkFormRef.value) return

  try {
    await linkFormRef.value.validate()
    addingLink.value = true

    const data = {
      requirement_id: currentItem.value.id,
      target_type: linkForm.value.targetType,
      target_id: linkForm.value.targetId,
      link_type: linkForm.value.linkType
    }

    const response = await api.post('/requirement-links', data)
    if (response.success) {
      ElMessage.success('关联创建成功')
      showAddLinkDialog.value = false
      fetchMatrixData()
    }
  } catch (error) {
    console.error('创建关联失败:', error)
    ElMessage.error(error.response?.data?.error || '创建关联失败')
  } finally {
    addingLink.value = false
  }
}

const goToRequirement = (row) => {
  router.push({
    path: `/projects/${projectId.value}/requirements/${row.doc_id}`,
    query: { itemId: row.id }
  })
}

const goToWorkItem = (row) => {
  if (row.target_type === 'task') {
    router.push(`/tasks/${row.target_id}`)
  } else if (row.target_type === 'bug') {
    router.push(`/bugs/${row.target_id}`)
  } else if (row.target_type === 'test_case') {
    router.push(`/projects/${projectId.value}/tests/cases/${row.target_id}`)
  }
}

const exportMatrix = () => {
  if (matrixData.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }

  const headers = ['需求标识', '需求标题', '优先级', '状态', '任务数', '缺陷数', '测试用例数', '负责人', '覆盖率']
  const rows = matrixData.value.map(item => [
    item.identifier,
    item.title,
    getPriorityText(item.priority),
    getStatusText(item.status),
    item.task_count || 0,
    item.bug_count || 0,
    item.test_case_count || 0,
    item.owner_name || '-',
    `${item.coverage}%`
  ])

  const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n')
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `需求跟踪矩阵_${new Date().toISOString().split('T')[0]}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

const getPriorityType = (priority) => {
  const typeMap = { 1: 'info', 2: 'warning', 3: 'danger' }
  return typeMap[priority] || 'info'
}

const getPriorityText = (priority) => {
  const textMap = { 1: '低', 2: '中', 3: '高' }
  return textMap[priority] || '-'
}

const getStatusType = (status) => {
  const typeMap = {
    'pending_review': 'info',
    'reviewed': 'warning',
    'approved': 'success',
    'in_progress': 'primary',
    'completed': 'success',
    'verified': 'success'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'pending_review': '待评审',
    'reviewed': '已评审',
    'approved': '已批准',
    'in_progress': '开发中',
    'completed': '已完成',
    'verified': '已验证'
  }
  return textMap[status] || status
}

const getLinkTypeText = (linkType) => {
  const textMap = {
    'implements': '实现',
    'verifies': '验证',
    'affects': '影响',
    'related': '相关'
  }
  return textMap[linkType] || linkType
}

const getWorkItemStatusType = (status) => {
  const typeMap = {
    'open': 'danger',
    'in_progress': 'primary',
    'resolved': 'success',
    'closed': 'info'
  }
  return typeMap[status] || 'info'
}

const getCoverageColor = (coverage) => {
  if (coverage >= 80) return '#67c23a'
  if (coverage >= 50) return '#e6a23c'
  return '#f56c6c'
}

onMounted(() => {
  fetchDocuments()
})
</script>

<style scoped>
.requirement-trace-matrix {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left h2 {
  margin: 0 0 4px 0;
  font-size: 24px;
  color: #303133;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.header-right {
  display: flex;
  align-items: center;
}

.statistics-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.filter-card {
  margin-bottom: 20px;
}

.matrix-card {
  min-height: 400px;
}

.link-count {
  color: #409eff;
  cursor: pointer;
  font-weight: 600;
}

.link-count:hover {
  text-decoration: underline;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .requirement-trace-matrix {
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
  .filter-form .el-select {
    width: 100% !important;
  }

  .matrix-container {
    overflow-x: auto;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
    min-width: 80px;
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
  .requirement-trace-matrix {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .el-table {
    font-size: 10px !important;
  }
}
</style>
