<template>
  <div class="test-execution-list">
    <div class="execution-header">
      <div class="header-left">
        <el-button @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>测试执行</h2>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建执行
        </el-button>
      </div>
    </div>

    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.total_executions || 0 }}</div>
            <div class="stat-label">执行总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.in_progress || 0 }}</div>
            <div class="stat-label">进行中</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.completed || 0 }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ passRate }}%</div>
            <div class="stat-label">通过率</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 120px;">
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试集">
          <el-select v-model="filters.suite_id" placeholder="全部" clearable style="width: 150px;">
            <el-option v-for="suite in suites" :key="suite.id" :label="suite.name" :value="suite.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">筛选</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table :data="executions" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="执行名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="suite_name" label="测试集" width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'in_progress'" type="warning" size="small">进行中</el-tag>
            <el-tag v-else type="success" size="small">已完成</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="environment" label="环境" width="120" />
        <el-table-column prop="test_version" label="测试版本" width="120" />
        <el-table-column prop="executor_name" label="执行人" width="100" />
        <el-table-column label="执行结果" width="200">
          <template #default="{ row }">
            <div class="result-summary">
              <span class="passed">{{ row.passed_count || 0 }}</span>
              <span class="separator">/</span>
              <span class="total">{{ row.result_count || 0 }}</span>
              <span class="rate" v-if="row.result_count > 0">
                ({{ ((row.passed_count / row.result_count) * 100).toFixed(1) }}%)
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="started_at" label="开始时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.started_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">查看</el-button>
            <el-button type="success" link size="small" @click="handleExecute(row)" v-if="row.status === 'in_progress'">执行</el-button>
            <el-button type="warning" link size="small" @click="handleEditExecution(row)" v-if="row.status === 'in_progress'">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDeleteExecution(row)" v-if="row.status === 'completed'">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="showCreateDialog" title="新建测试执行" width="600px">
      <el-form :model="executionForm" label-width="100px" :rules="executionRules" ref="executionFormRef">
        <el-form-item label="执行名称" prop="name">
          <el-input v-model="executionForm.name" placeholder="如：回归测试-2024-03-20" />
        </el-form-item>
        <el-form-item label="测试集">
          <el-select v-model="executionForm.suite_id" placeholder="请选择测试集（可选）" clearable style="width: 100%;" @change="handleSuiteChange">
            <el-option v-for="suite in suites" :key="suite.id" :label="suite.name" :value="suite.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试环境">
          <el-input v-model="executionForm.environment" placeholder="如：测试环境1" />
        </el-form-item>
        <el-form-item label="测试版本">
          <el-input v-model="executionForm.test_version" placeholder="如：v1.0.0" />
        </el-form-item>
        <el-form-item label="构建号">
          <el-input v-model="executionForm.build_number" placeholder="如：Build-1234" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="executionForm.notes" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
        <el-form-item label="选择用例" v-if="executionForm.suite_id && availableCases.length > 0">
          <div class="case-selector">
            <el-checkbox v-model="selectAllCases" @change="handleSelectAll">全选</el-checkbox>
            <el-scrollbar height="200px">
              <el-checkbox-group v-model="executionForm.case_ids">
                <el-checkbox v-for="c in availableCases" :key="c.id" :label="c.id" style="display: block; margin-left: 0; margin-bottom: 8px;">
                  {{ c.identifier }} - {{ c.title }}
                </el-checkbox>
              </el-checkbox-group>
            </el-scrollbar>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateExecution" :loading="saving">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showExecuteDialog" title="执行测试" width="1000px" :close-on-click-modal="false">
      <div v-if="currentExecution" class="execution-detail">
        <el-alert :title="`执行: ${currentExecution.name}`" type="info" :closable="false" style="margin-bottom: 16px;" />

        <el-card class="progress-card">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="progress-item">
                <div class="progress-label">总用例数</div>
                <div class="progress-value">{{ currentExecution.result_count || 0 }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="progress-item">
                <div class="progress-label">已完成</div>
                <div class="progress-value completed">{{ currentExecution.passed_count + currentExecution.failed_count + currentExecution.blocked_count + currentExecution.skipped_count || 0 }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="progress-item">
                <div class="progress-label">通过</div>
                <div class="progress-value passed">{{ currentExecution.passed_count || 0 }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="progress-item">
                <div class="progress-label">失败</div>
                <div class="progress-value failed">{{ currentExecution.failed_count || 0 }}</div>
              </div>
            </el-col>
          </el-row>
          <el-progress :percentage="executionProgress" :color="progressColor" style="margin-top: 16px;" />
        </el-card>

        <el-table :data="executionResults" stripe style="width: 100%; margin-top: 16px;" ref="resultsTableRef" :row-class-name="getRowClassName">
          <el-table-column prop="case_identifier" label="用例标识" width="100" />
          <el-table-column prop="case_title" label="用例标题" min-width="150" show-overflow-tooltip />
          <el-table-column prop="priority" label="优先级" width="80">
            <template #default="{ row }">
              <el-tag v-if="row.priority === 0" type="danger" size="small">P0</el-tag>
              <el-tag v-else-if="row.priority === 1" type="warning" size="small">P1</el-tag>
              <el-tag v-else size="small">P2</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="result" label="结果" width="120">
            <template #default="{ row }">
              <el-select v-model="row.result" placeholder="选择结果" style="width: 100%;" @change="handleResultChange(row)">
                <el-option label="通过" value="passed" />
                <el-option label="失败" value="failed" />
                <el-option label="阻塞" value="blocked" />
                <el-option label="跳过" value="skipped" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="actual_result" label="实际结果" min-width="150">
            <template #default="{ row }">
              <el-input v-model="row.actual_result" placeholder="实际结果" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template #default="{ row, $index }">
              <el-button type="primary" size="small" @click="submitSingleResult(row, $index)" :disabled="!row.result">提交</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="batch-actions" style="margin-top: 20px;">
          <el-button type="success" @click="handleBatchPass">批量标记通过</el-button>
          <el-button type="danger" @click="handleBatchFail">批量标记失败</el-button>
          <el-button type="warning" @click="handleBatchBlocked">批量标记阻塞</el-button>
          <el-button type="info" @click="handleBatchSkip">批量跳过</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="handleSaveResults">保存结果</el-button>
        <el-button type="primary" @click="handleCompleteExecution" :loading="completing">完成执行</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showViewDialog" title="执行详情" width="1000px">
      <div v-if="currentExecution" class="view-detail">
        <el-descriptions :column="2" border style="margin-bottom: 20px;">
          <el-descriptions-item label="执行名称">{{ currentExecution.name }}</el-descriptions-item>
          <el-descriptions-item label="测试集">{{ currentExecution.suite_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag v-if="currentExecution.status === 'in_progress'" type="warning" size="small">进行中</el-tag>
            <el-tag v-else type="success" size="small">已完成</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="执行人">{{ currentExecution.executor_name }}</el-descriptions-item>
          <el-descriptions-item label="环境">{{ currentExecution.environment || '-' }}</el-descriptions-item>
          <el-descriptions-item label="测试版本">{{ currentExecution.test_version || '-' }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(currentExecution.started_at) }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ formatDate(currentExecution.completed_at) || '-' }}</el-descriptions-item>
        </el-descriptions>

        <h4>执行结果统计</h4>
        <el-row :gutter="16" style="margin-bottom: 20px;">
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card success">
              <div class="stat-number">{{ currentExecution.passed_count || 0 }}</div>
              <div class="stat-label">通过</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card danger">
              <div class="stat-number">{{ currentExecution.failed_count || 0 }}</div>
              <div class="stat-label">失败</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card warning">
              <div class="stat-number">{{ currentExecution.blocked_count || 0 }}</div>
              <div class="stat-label">阻塞</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card info">
              <div class="stat-number">{{ currentExecution.skipped_count || 0 }}</div>
              <div class="stat-label">跳过</div>
            </el-card>
          </el-col>
        </el-row>

        <h4>用例执行结果</h4>
        <el-table :data="executionResults" stripe style="width: 100%;">
          <el-table-column prop="case_identifier" label="用例标识" width="100" />
          <el-table-column prop="case_title" label="用例标题" min-width="150" show-overflow-tooltip />
          <el-table-column prop="result" label="结果" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.result === 'passed'" type="success" size="small">通过</el-tag>
              <el-tag v-else-if="row.result === 'failed'" type="danger" size="small">失败</el-tag>
              <el-tag v-else-if="row.result === 'blocked'" type="warning" size="small">阻塞</el-tag>
              <el-tag v-else-if="row.result === 'skipped'" type="info" size="small">跳过</el-tag>
              <el-tag v-else type="info" size="small">未执行</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="actual_result" label="实际结果" min-width="150" show-overflow-tooltip />
          <el-table-column prop="executor_name" label="执行人" width="100" />
          <el-table-column prop="executed_at" label="执行时间" width="160">
            <template #default="{ row }">
              {{ formatDate(row.executed_at) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <el-dialog v-model="showEditDialog" title="编辑执行" width="500px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="执行名称">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="环境">
          <el-input v-model="editForm.environment" />
        </el-form-item>
        <el-form-item label="测试版本">
          <el-input v-model="editForm.test_version" />
        </el-form-item>
        <el-form-item label="构建号">
          <el-input v-model="editForm.build_number" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmEdit" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDefectDialog" title="关联缺陷" width="500px">
      <el-form :model="defectForm" label-width="100px">
        <el-form-item label="缺陷ID">
          <el-input v-model="defectForm.defect_id" placeholder="请输入缺陷ID" />
        </el-form-item>
        <el-form-item label="缺陷描述">
          <el-input v-model="defectForm.description" type="textarea" :rows="3" placeholder="请输入缺陷描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDefectDialog = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmDefect" :loading="saving">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const router = useRouter()
const route = useRoute()

const projectId = ref(null)
const executions = ref([])
const suites = ref([])
const availableCases = ref([])
const loading = ref(false)
const showCreateDialog = ref(false)
const showExecuteDialog = ref(false)
const showViewDialog = ref(false)
const showEditDialog = ref(false)
const saving = ref(false)
const completing = ref(false)
const selectAllCases = ref(false)
const statistics = ref({})
const currentExecution = ref(null)
const executionResults = ref([])
const showDefectDialog = ref(false)
const defectForm = reactive({
  defect_id: null,
  description: ''
})
const selectedCaseForDefect = ref(null)
const availableDefects = ref([])
const resultsTableRef = ref(null)
const executionFormRef = ref(null)

const filters = reactive({
  status: '',
  suite_id: null
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const executionForm = reactive({
  name: '',
  suite_id: null,
  environment: '',
  test_version: '',
  build_number: '',
  notes: '',
  case_ids: []
})

const editForm = reactive({
  name: '',
  environment: '',
  test_version: '',
  build_number: '',
  notes: ''
})

const executionRules = {
  name: [{ required: true, message: '请输入执行名称', trigger: 'blur' }]
}

const passRate = computed(() => {
  const total = executions.value.reduce((sum, e) => sum + (e.result_count || 0), 0)
  const passed = executions.value.reduce((sum, e) => sum + (e.passed_count || 0), 0)
  if (total === 0) return 0
  return ((passed / total) * 100).toFixed(1)
})

const executionProgress = computed(() => {
  if (!currentExecution.value || !currentExecution.value.result_count) return 0
  const completed = (currentExecution.value.passed_count || 0) +
    (currentExecution.value.failed_count || 0) +
    (currentExecution.value.blocked_count || 0) +
    (currentExecution.value.skipped_count || 0)
  return Math.round((completed / currentExecution.value.result_count) * 100)
})

const progressColor = computed(() => {
  if (executionProgress.value < 50) return '#F56C6C'
  if (executionProgress.value < 80) return '#E6A23C'
  return '#67C23A'
})

const handleBack = () => {
  router.push(`/projects/${projectId.value}/tests/suites`)
}

const loadExecutions = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page
    }
    if (filters.status) params.status = filters.status
    if (filters.suite_id) params.suite_id = filters.suite_id

    const response = await apiService.tests.getExecutionsByProject(projectId.value, params)
    const data = response?.data || response
    executions.value = data?.executions || []
    pagination.total = data?.total || 0

    const statsResponse = await apiService.tests.getProjectStatistics(projectId.value)
    statistics.value = statsResponse?.data || {}
    statistics.value.total_executions = executions.value.length
    statistics.value.in_progress = executions.value.filter(e => e.status === 'in_progress').length
    statistics.value.completed = executions.value.filter(e => e.status === 'completed').length
  } catch (error) {
    console.error('加载执行记录失败:', error)
    ElMessage.error('加载执行记录失败')
  } finally {
    loading.value = false
  }
}

const loadSuites = async () => {
  try {
    const response = await apiService.tests.getSuites(projectId.value)
    suites.value = response?.data || []
  } catch (error) {
    console.error('加载测试集失败:', error)
  }
}

const loadCasesForSuite = async (suiteId) => {
  if (!suiteId) {
    availableCases.value = []
    return
  }
  try {
    const response = await apiService.tests.getCasesBySuite(suiteId, { per_page: 100 })
    const data = response?.data || response
    availableCases.value = data?.cases || []
  } catch (error) {
    console.error('加载用例失败:', error)
  }
}

const handleSuiteChange = (suiteId) => {
  if (suiteId) {
    loadCasesForSuite(suiteId)
  } else {
    availableCases.value = []
    executionForm.case_ids = []
  }
}

const handleFilter = () => {
  pagination.page = 1
  loadExecutions()
}

const handleReset = () => {
  filters.status = ''
  filters.suite_id = null
  handleFilter()
}

const handlePageChange = (page) => {
  pagination.page = page
  loadExecutions()
}

const handleSizeChange = (size) => {
  pagination.per_page = size
  loadExecutions()
}

const handleSelectAll = (checked) => {
  if (checked) {
    executionForm.case_ids = availableCases.value.map(c => c.id)
  } else {
    executionForm.case_ids = []
  }
}

const handleCreateExecution = async () => {
  if (!executionForm.name) {
    ElMessage.warning('请输入执行名称')
    return
  }

  saving.value = true
  try {
    await apiService.tests.createExecution({
      ...executionForm,
      project_id: projectId.value
    })
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    Object.assign(executionForm, {
      name: '',
      suite_id: null,
      environment: '',
      test_version: '',
      build_number: '',
      notes: '',
      case_ids: []
    })
    selectAllCases.value = false
    await loadExecutions()
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    saving.value = false
  }
}

const handleView = async (row) => {
  try {
    const response = await apiService.tests.getExecutionById(row.id, { include_results: true })
    currentExecution.value = response?.data || response
    executionResults.value = currentExecution.value?.results || []
    showViewDialog.value = true
  } catch (error) {
    ElMessage.error('加载执行详情失败')
  }
}

const handleExecute = async (row) => {
  try {
    const response = await apiService.tests.getExecutionById(row.id, { include_results: true })
    currentExecution.value = response?.data || response
    executionResults.value = currentExecution.value?.results || []
    showExecuteDialog.value = true
  } catch (error) {
    ElMessage.error('加载执行详情失败')
  }
}

const handleEditExecution = (row) => {
  Object.assign(editForm, {
    name: row.name,
    environment: row.environment || '',
    test_version: row.test_version || '',
    build_number: row.build_number || '',
    notes: row.notes || ''
  })
  currentExecution.value = row
  showEditDialog.value = true
}

const handleConfirmEdit = async () => {
  if (!editForm.name) {
    ElMessage.warning('请输入执行名称')
    return
  }
  saving.value = true
  try {
    await apiService.tests.updateExecution(currentExecution.value.id, {
      name: editForm.name,
      environment: editForm.environment,
      test_version: editForm.test_version,
      build_number: editForm.build_number,
      notes: editForm.notes
    })
    ElMessage.success('更新成功')
    showEditDialog.value = false
    await loadExecutions()
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    saving.value = false
  }
}

const handleDeleteExecution = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个执行记录吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await apiService.tests.deleteExecution(row.id)
    ElMessage.success('删除成功')
    await loadExecutions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const getRowClassName = ({ row }) => {
  if (row.result === 'passed') return 'result-passed'
  if (row.result === 'failed') return 'result-failed'
  if (row.result === 'blocked') return 'result-blocked'
  if (row.result === 'skipped') return 'result-skipped'
  return ''
}

const handleResultChange = (row) => {
  if (row.result === 'failed') {
    selectedCaseForDefect.value = row
    showDefectDialog.value = true
  }
}

const handleConfirmDefect = async () => {
  if (!defectForm.defect_id) {
    ElMessage.warning('请输入缺陷ID')
    return
  }
  if (selectedCaseForDefect.value) {
    selectedCaseForDefect.value.defect_id = defectForm.defect_id
    selectedCaseForDefect.value.actual_result = defectForm.description
  }
  showDefectDialog.value = false
  defectForm.defect_id = ''
  defectForm.description = ''
  selectedCaseForDefect.value = null
  ElMessage.success('缺陷关联成功')
}

const submitSingleResult = async (row, index) => {
  if (!row.result) {
    ElMessage.warning('请先选择执行结果')
    return
  }
  try {
    await apiService.tests.submitTestResult(currentExecution.value.id, {
      case_id: row.case_id,
      result: row.result,
      actual_result: row.actual_result
    })
    ElMessage.success('提交成功')
    await refreshExecutionResults()
  } catch (error) {
    ElMessage.error('提交失败')
  }
}

const handleSaveResults = async () => {
  try {
    for (const row of executionResults.value) {
      if (row.result && row.result !== 'pending') {
        await apiService.tests.submitTestResult(currentExecution.value.id, {
          case_id: row.case_id,
          result: row.result,
          actual_result: row.actual_result
        })
      }
    }
    ElMessage.success('结果保存成功')
    await refreshExecutionResults()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const refreshExecutionResults = async () => {
  try {
    const response = await apiService.tests.getExecutionById(currentExecution.value.id, { include_results: true })
    currentExecution.value = response?.data || response
    executionResults.value = currentExecution.value?.results || []
  } catch (error) {
    console.error('刷新执行结果失败:', error)
  }
}

const handleCompleteExecution = async () => {
  try {
    await ElMessageBox.confirm('确定要完成本次执行吗？完成后将生成执行报告。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    completing.value = true
    for (const row of executionResults.value) {
      if (row.result && row.result !== 'pending') {
        await apiService.tests.submitTestResult(currentExecution.value.id, {
          case_id: row.case_id,
          result: row.result,
          actual_result: row.actual_result
        })
      }
    }
    await apiService.tests.updateExecution(currentExecution.value.id, { status: 'completed' })
    ElMessage.success('执行已完成')
    showExecuteDialog.value = false
    await loadExecutions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  } finally {
    completing.value = false
  }
}

const handleBatchPass = () => {
  executionResults.value.forEach(r => {
    r.result = 'passed'
  })
}

const handleBatchFail = () => {
  executionResults.value.forEach(r => {
    r.result = 'failed'
  })
}

const handleBatchBlocked = () => {
  executionResults.value.forEach(r => {
    r.result = 'blocked'
  })
}

const handleBatchSkip = () => {
  executionResults.value.forEach(r => {
    r.result = 'skipped'
  })
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

watch(() => executionForm.suite_id, (newVal) => {
  if (newVal) {
    loadCasesForSuite(newVal)
  } else {
    availableCases.value = []
    executionForm.case_ids = []
  }
})

onMounted(async () => {
  projectId.value = parseInt(route.params.projectId)
  await loadSuites()
  await loadExecutions()

  if (route.query.suite_id) {
    executionForm.suite_id = parseInt(route.query.suite_id)
  }
})
</script>

<style scoped>
.test-execution-list {
  padding: 20px;
}

.execution-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h2 {
  margin: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-card.success .stat-number {
  color: #67C23A;
}

.stat-card.danger .stat-number {
  color: #F56C6C;
}

.stat-card.warning .stat-number {
  color: #E6A23C;
}

.stat-card.info .stat-number {
  color: #909399;
}

.stat-content {
  padding: 10px 0;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.filter-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.result-summary .passed {
  color: #67C23A;
  font-weight: bold;
}

.result-summary .separator {
  color: #909399;
  margin: 0 4px;
}

.result-summary .total {
  color: #303133;
}

.result-summary .rate {
  color: #909399;
  margin-left: 4px;
}

.case-selector {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 12px;
  background: #f5f7fa;
}

.case-selector .el-checkbox {
  margin-right: 0;
}

.progress-card {
  margin-bottom: 16px;
}

.progress-item {
  text-align: center;
  padding: 8px 0;
}

.progress-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.progress-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.progress-value.completed {
  color: #67C23A;
}

.progress-value.passed {
  color: #67C23A;
}

.progress-value.failed {
  color: #F56C6C;
}

:deep(.result-passed) {
  background-color: rgba(103, 194, 58, 0.1) !important;
}

:deep(.result-failed) {
  background-color: rgba(245, 108, 108, 0.1) !important;
}

:deep(.result-blocked) {
  background-color: rgba(230, 162, 60, 0.1) !important;
}

:deep(.result-skipped) {
  background-color: rgba(144, 147, 153, 0.1) !important;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .test-execution-list {
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

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 16px;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-label {
    font-size: 12px;
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
  .test-execution-list {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .el-table {
    font-size: 10px !important;
  }
}
</style>
