<template>
  <div class="risk-list">
    <div class="risk-list-header">
      <div class="header-left">
        <el-button text @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回项目
        </el-button>
        <h2>{{ projectName }} - 风险与问题管理</h2>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showRiskDialog = true">
          <el-icon><Plus /></el-icon>
          新建风险/问题
        </el-button>
      </div>
    </div>

    <el-row :gutter="16" class="risk-stats">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.total || 0 }}</div>
            <div class="stat-label">总计</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.open || 0 }}</div>
            <div class="stat-label">待处理</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.resolved || 0 }}</div>
            <div class="stat-label">已解决</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-danger">
          <div class="stat-content">
            <div class="stat-number">{{ stats.high_risk || 0 }}</div>
            <div class="stat-label">高风险</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="filter-card" shadow="never">
      <el-form :model="filters" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="5">
            <el-form-item label="类型">
              <el-select v-model="filters.risk_type" placeholder="全部" clearable @change="handleFilter">
                <el-option label="风险" value="risk" />
                <el-option label="问题" value="issue" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="状态">
              <el-select v-model="filters.status" placeholder="全部" clearable @change="handleFilter">
                <el-option label="已识别" value="identified" />
                <el-option label="已分析" value="analyzed" />
                <el-option label="处理中" value="mitigating" />
                <el-option label="已解决" value="resolved" />
                <el-option label="已关闭" value="closed" />
                <el-option label="已接受" value="accepted" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="风险等级">
              <el-select v-model="filters.level" placeholder="全部" clearable @change="handleFilter">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="严重" value="critical" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="优先级">
              <el-select v-model="filters.priority" placeholder="全部" clearable @change="handleFilter">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="紧急" value="critical" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="关键词">
              <el-input v-model="filters.search" placeholder="搜索..." clearable @keyup.enter="handleFilter" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item>
              <el-button type="primary" @click="handleFilter">查询</el-button>
              <el-button @click="resetFilters">重置</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table :data="risks" stripe v-loading="loading">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="类型" width="90">
          <template #default="{ row }">
            <el-tag :type="row.risk_type === 'risk' ? 'warning' : 'danger'" size="small">
              {{ row.risk_type === 'risk' ? '风险' : '问题' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="level" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small">
              {{ getLevelText(row.level) }}
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
        <el-table-column prop="priority" label="优先级" width="90">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="类别" width="100">
          <template #default="{ row }">
            {{ getCategoryText(row.category) }}
          </template>
        </el-table-column>
        <el-table-column prop="exposure" label="暴露度" width="80">
          <template #default="{ row }">
            <span :class="getExposureClass(row.exposure)">{{ row.exposure || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="assignee_name" label="负责人" width="120" />
        <el-table-column prop="due_date" label="截止日期" width="120">
          <template #default="{ row }">
            {{ row.due_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" :icon="Edit" circle @click="editRisk(row)" />
            <el-button type="danger" size="small" :icon="Delete" circle @click="deleteRisk(row)" />
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="showRiskDialog" :title="dialogTitle" width="700px" @closed="resetForm">
      <el-form :model="riskForm" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="类型" prop="risk_type">
          <el-radio-group v-model="riskForm.risk_type">
            <el-radio value="risk">风险</el-radio>
            <el-radio value="issue">问题</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="标题" prop="title">
          <el-input v-model="riskForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="riskForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="风险等级" prop="level">
              <el-select v-model="riskForm.level" placeholder="请选择" style="width: 100%">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="严重" value="critical" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="riskForm.priority" placeholder="请选择" style="width: 100%">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="紧急" value="critical" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="riskForm.status" placeholder="请选择" style="width: 100%">
                <el-option label="已识别" value="identified" />
                <el-option label="已分析" value="analyzed" />
                <el-option label="处理中" value="mitigating" />
                <el-option label="已解决" value="resolved" />
                <el-option label="已关闭" value="closed" />
                <el-option label="已接受" value="accepted" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="类别">
              <el-select v-model="riskForm.category" placeholder="请选择" style="width: 100%">
                <el-option label="技术风险" value="technical" />
                <el-option label="进度风险" value="schedule" />
                <el-option label="预算风险" value="budget" />
                <el-option label="资源风险" value="resource" />
                <el-option label="需求风险" value="requirement" />
                <el-option label="质量风险" value="quality" />
                <el-option label="外部风险" value="external" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="负责人">
              <el-select v-model="riskForm.assigned_to" placeholder="请选择负责人" clearable style="width: 100%">
                <el-option v-for="member in projectMembers" :key="member.user_id" :label="member.username" :value="member.user_id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="截止日期">
              <el-date-picker v-model="riskForm.due_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="发生概率">
              <el-slider v-model="riskForm.probability" :min="0" :max="1" :step="0.1" show-input />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="影响程度">
              <el-slider v-model="riskForm.impact" :min="0" :max="1" :step="0.1" show-input />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="应对策略">
          <el-input v-model="riskForm.mitigation_strategy" type="textarea" :rows="2" placeholder="请输入应对策略" />
        </el-form-item>
        <el-form-item label="应急预案">
          <el-input v-model="riskForm.contingency_plan" type="textarea" :rows="2" placeholder="请输入应急预案" />
        </el-form-item>
        <el-form-item label="解决方案">
          <el-input v-model="riskForm.resolution" type="textarea" :rows="2" placeholder="请输入解决方案" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRiskDialog = false">取消</el-button>
        <el-button type="primary" @click="saveRisk" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const route = useRoute()
const router = useRouter()
const projectId = route.params.projectId

const projectName = ref('')
const loading = ref(false)
const saving = ref(false)
const showRiskDialog = ref(false)
const editingRiskId = ref(null)

const risks = ref([])
const projectMembers = ref([])
const stats = ref({})

const filters = ref({
  risk_type: '',
  status: '',
  level: '',
  priority: '',
  category: '',
  search: ''
})

const pagination = ref({
  page: 1,
  per_page: 20,
  total: 0
})

const riskForm = ref({
  risk_type: 'risk',
  title: '',
  description: '',
  level: 'medium',
  priority: 'medium',
  status: 'identified',
  category: '',
  assigned_to: null,
  due_date: '',
  probability: 0.5,
  impact: 0.5,
  mitigation_strategy: '',
  contingency_plan: '',
  resolution: ''
})

const formRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  level: [{ required: true, message: '请选择风险等级', trigger: 'change' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const dialogTitle = computed(() => editingRiskId.value ? '编辑风险/问题' : '新建风险/问题')

const getLevelType = (level) => {
  const typeMap = { low: 'info', medium: 'warning', high: 'danger', critical: 'danger' }
  return typeMap[level] || 'info'
}

const getLevelText = (level) => {
  const textMap = { low: '低', medium: '中', high: '高', critical: '严重' }
  return textMap[level] || level
}

const getStatusType = (status) => {
  const typeMap = {
    identified: 'info',
    analyzed: 'warning',
    mitigating: 'primary',
    resolved: 'success',
    closed: 'success',
    accepted: 'warning'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    identified: '已识别',
    analyzed: '已分析',
    mitigating: '处理中',
    resolved: '已解决',
    closed: '已关闭',
    accepted: '已接受'
  }
  return textMap[status] || status
}

const getPriorityType = (priority) => {
  const typeMap = { low: 'info', medium: 'warning', high: 'danger', critical: 'danger' }
  return typeMap[priority] || 'info'
}

const getPriorityText = (priority) => {
  const textMap = { low: '低', medium: '中', high: '高', critical: '紧急' }
  return textMap[priority] || priority
}

const getCategoryText = (category) => {
  const textMap = {
    technical: '技术',
    schedule: '进度',
    budget: '预算',
    resource: '资源',
    requirement: '需求',
    quality: '质量',
    external: '外部',
    other: '其他'
  }
  return textMap[category] || category || '-'
}

const getExposureClass = (exposure) => {
  if (exposure >= 0.7) return 'exposure-high'
  if (exposure >= 0.4) return 'exposure-medium'
  return 'exposure-low'
}

const fetchRisks = async () => {
  loading.value = true
  try {
    const params = {
      project_id: projectId,
      page: pagination.value.page,
      per_page: pagination.value.per_page,
      ...filters.value
    }
    Object.keys(params).forEach(key => {
      if (!params[key]) delete params[key]
    })

    const response = await apiService.risks.getList(params)
    risks.value = response.risks || []
    pagination.value.total = response.total || 0
  } catch (error) {
    console.error('获取风险列表失败:', error)
    ElMessage.error('获取风险列表失败')
  } finally {
    loading.value = false
  }
}

const fetchStatistics = async () => {
  try {
    const response = await apiService.risks.getStatistics({ project_id: projectId })
    stats.value = response.data || response || {}
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

const fetchProjectMembers = async () => {
  try {
    const response = await apiService.projects.getProjectMembers(projectId)
    projectMembers.value = response.members || []
  } catch (error) {
    console.error('获取项目成员失败:', error)
  }
}

const fetchProjectInfo = async () => {
  try {
    const response = await apiService.projects.getById(projectId)
    projectName.value = response.project?.name || response.name || '项目'
  } catch (error) {
    console.error('获取项目信息失败:', error)
    projectName.value = '项目'
  }
}

const handleFilter = () => {
  pagination.value.page = 1
  fetchRisks()
}

const resetFilters = () => {
  filters.value = {
    risk_type: '',
    status: '',
    level: '',
    priority: '',
    category: '',
    search: ''
  }
  handleFilter()
}

const handlePageChange = (page) => {
  pagination.value.page = page
  fetchRisks()
}

const handleSizeChange = (size) => {
  pagination.value.per_page = size
  fetchRisks()
}

const editRisk = async (row) => {
  editingRiskId.value = row.id
  try {
    const response = await apiService.risks.getById(row.id)
    const risk = response.risk || response

    riskForm.value = {
      risk_type: risk.risk_type || 'risk',
      title: risk.title || '',
      description: risk.description || '',
      level: risk.level || 'medium',
      priority: risk.priority || 'medium',
      status: risk.status || 'identified',
      category: risk.category || '',
      assigned_to: risk.assigned_to || null,
      due_date: risk.due_date || '',
      probability: risk.probability || 0.5,
      impact: risk.impact || 0.5,
      mitigation_strategy: risk.mitigation_strategy || '',
      contingency_plan: risk.contingency_plan || '',
      resolution: risk.resolution || ''
    }
    showRiskDialog.value = true
  } catch (error) {
    console.error('获取风险详情失败:', error)
    ElMessage.error('获取风险详情失败')
  }
}

const deleteRisk = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除风险/问题"${row.title}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await apiService.risks.delete(row.id)
    ElMessage.success('删除成功')
    fetchRisks()
    fetchStatistics()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const saveRisk = async () => {
  try {
    await formRef.value.validate()
  } catch (error) {
    return
  }

  saving.value = true
  try {
    const data = {
      ...riskForm.value,
      project_id: parseInt(projectId)
    }

    if (editingRiskId.value) {
      await apiService.risks.update(editingRiskId.value, data)
      ElMessage.success('更新成功')
    } else {
      await apiService.risks.create(data)
      ElMessage.success('创建成功')
    }

    showRiskDialog.value = false
    fetchRisks()
    fetchStatistics()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  editingRiskId.value = null
  riskForm.value = {
    risk_type: 'risk',
    title: '',
    description: '',
    level: 'medium',
    priority: 'medium',
    status: 'identified',
    category: '',
    assigned_to: null,
    due_date: '',
    probability: 0.5,
    impact: 0.5,
    mitigation_strategy: '',
    contingency_plan: '',
    resolution: ''
  }
}

const formRef = ref(null)

onMounted(() => {
  fetchRisks()
  fetchStatistics()
  fetchProjectMembers()
  fetchProjectInfo()
})
</script>

<style scoped>
.risk-list {
  padding: 20px;
}

.risk-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.risk-stats {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  cursor: pointer;
}

.stat-danger {
  border-color: #f56c6c;
}

.stat-danger .stat-number {
  color: #f56c6c;
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px 0;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
  background: #fff;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.exposure-high {
  color: #f56c6c;
  font-weight: bold;
}

.exposure-medium {
  color: #e6a23c;
  font-weight: bold;
}

.exposure-low {
  color: #67c23a;
}

@media screen and (max-width: 768px) {
  .risk-list {
    padding: 12px;
  }

  .risk-list-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .header-left h2 {
    font-size: 16px;
  }

  .header-actions {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .risk-stats .el-col {
    width: 50%;
    margin-bottom: 12px;
  }
}
</style>