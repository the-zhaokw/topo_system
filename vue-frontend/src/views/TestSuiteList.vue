<template>
  <div class="test-suite-list">
    <div class="suite-header">
      <div class="header-left">
        <el-button @click="handleGoBack" v-if="showBackButton" style="margin-right: 16px;">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>测试集管理</h2>
      </div>
      <div class="header-actions">
        <el-select v-model="selectedProjectId" placeholder="选择项目" clearable @change="handleProjectChange" style="width: 200px; margin-right: 16px;">
          <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
        </el-select>
        <el-button @click="goToDashboard" :disabled="!selectedProjectId">
          <el-icon><DataAnalysis /></el-icon>
          测试仪表盘
        </el-button>
        <el-button type="primary" @click="handleAddSuite" :disabled="!selectedProjectId">
          <el-icon><Plus /></el-icon>
          新建测试集
        </el-button>
      </div>
    </div>

    <el-card v-if="!selectedProjectId" class="empty-tip">
      <el-empty description="请先选择一个项目来查看测试集" />
    </el-card>

    <div v-else>
      <!-- 统计卡片 -->
      <el-row :gutter="16" class="stats-row">
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics.total_suites || 0 }}</div>
              <div class="stat-label">测试集总数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics.total_cases || 0 }}</div>
              <div class="stat-label">用例总数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics.automated_count || 0 }}</div>
              <div class="stat-label">自动化用例</div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <el-card shadow="hover" class="stat-card clickable" @click="$router.push(`/projects/${selectedProjectId}/tests/executions`)">
            <div class="stat-content">
              <div class="stat-number"><el-icon><ArrowRight /></el-icon></div>
              <div class="stat-label">执行记录</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 筛选栏 -->
      <el-card class="filter-card">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="搜索">
            <el-input v-model="filterForm.keyword" placeholder="输入名称搜索" clearable @input="handleFilter" style="width: 200px;">
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="类型">
            <el-select v-model="filterForm.type" placeholder="全部类型" clearable @change="handleFilter" style="width: 140px;">
              <el-option label="功能测试" value="functional" />
              <el-option label="性能测试" value="performance" />
              <el-option label="安全测试" value="security" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="全部状态" clearable @change="handleFilter" style="width: 140px;">
              <el-option label="设计中" value="designing" />
              <el-option label="已评审" value="reviewed" />
              <el-option label="已废弃" value="deprecated" />
            </el-select>
          </el-form-item>
          <el-form-item label="优先级">
            <el-select v-model="filterForm.priority" placeholder="全部优先级" clearable @change="handleFilter" style="width: 140px;">
              <el-option label="高" :value="1" />
              <el-option label="中" :value="2" />
              <el-option label="低" :value="3" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 测试集列表 -->
      <el-card class="list-card">
        <el-table
          :data="filteredSuites"
          style="width: 100%"
          v-loading="loading"
          @row-click="handleRowClick"
          highlight-current-row
        >
          <el-table-column type="index" width="50" />
          <el-table-column label="名称" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <div class="suite-name-cell">
                <el-icon v-if="row.type === 'functional'" class="type-icon"><Document /></el-icon>
                <el-icon v-else-if="row.type === 'performance'" class="type-icon warning"><TrendCharts /></el-icon>
                <el-icon v-else-if="row.type === 'security'" class="type-icon danger"><Lock /></el-icon>
                <el-icon v-else class="type-icon info"><Setting /></el-icon>
                <span class="suite-name">{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.type === 'functional'" size="small">功能</el-tag>
              <el-tag v-else-if="row.type === 'performance'" size="small" type="warning">性能</el-tag>
              <el-tag v-else-if="row.type === 'security'" size="small" type="danger">安全</el-tag>
              <el-tag v-else size="small" type="info">其他</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag v-if="row.status === 'designing'" size="small" type="info">设计中</el-tag>
              <el-tag v-else-if="row.status === 'reviewed'" size="small" type="success">已评审</el-tag>
              <el-tag v-else-if="row.status === 'deprecated'" size="small" type="danger">已废弃</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="优先级" width="80">
            <template #default="{ row }">
              <el-tag v-if="row.priority === 1" size="small" type="danger">高</el-tag>
              <el-tag v-else-if="row.priority === 2" size="small" type="warning">中</el-tag>
              <el-tag v-else size="small" type="info">低</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="用例数" width="80" align="center">
            <template #default="{ row }">
              <el-tag size="small" type="primary">{{ row.case_count || 0 }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="负责人" width="120" show-overflow-tooltip>
            <template #default="{ row }">
              <span v-if="row.owner_name">{{ row.owner_name }}</span>
              <span v-else class="text-muted">未指定</span>
            </template>
          </el-table-column>
          <el-table-column label="更新时间" width="160">
            <template #default="{ row }">
              {{ formatDate(row.updated_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click.stop="handleViewDetail(row)">
                详情
              </el-button>
              <el-button type="primary" link size="small" @click.stop="handleViewCases(row)">
                用例
              </el-button>
              <el-button type="primary" link size="small" @click.stop="handleEditSuite(row)">
                编辑
              </el-button>
              <el-dropdown @command="(cmd) => handleMoreAction(cmd, row)" @click.stop>
                <el-button type="primary" link size="small">
                  更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="execute">
                      <el-icon><VideoPlay /></el-icon>执行测试
                    </el-dropdown-item>
                    <el-dropdown-item command="copy">
                      <el-icon><CopyDocument /></el-icon>复制
                    </el-dropdown-item>
                    <el-dropdown-item command="move">
                      <el-icon><Rank /></el-icon>移动
                    </el-dropdown-item>
                    <el-dropdown-item command="history">
                      <el-icon><Clock /></el-icon>版本历史
                    </el-dropdown-item>
                    <el-dropdown-item divided command="delete" class="danger">
                      <el-icon><Delete /></el-icon>删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>

        <!-- 空状态 -->
        <el-empty v-if="filteredSuites.length === 0 && !loading" description="暂无测试集数据" />
      </el-card>
    </div>

    <!-- 新建/编辑测试集对话框 -->
    <el-dialog v-model="showCreateDialog" :title="editingSuite ? '编辑测试集' : '新建测试集'" width="600px">
      <el-form :model="suiteForm" label-width="100px" :rules="formRules" ref="formRef">
        <el-form-item label="测试集名称" prop="name">
          <el-input v-model="suiteForm.name" placeholder="请输入测试集名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="suiteForm.description" type="textarea" :rows="3" placeholder="请输入测试集描述" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="suiteForm.type" placeholder="请选择类型" style="width: 100%;">
            <el-option label="功能测试" value="functional" />
            <el-option label="性能测试" value="performance" />
            <el-option label="安全测试" value="security" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="suiteForm.status" placeholder="请选择状态" style="width: 100%;">
            <el-option label="设计中" value="designing" />
            <el-option label="已评审" value="reviewed" />
            <el-option label="已废弃" value="deprecated" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="suiteForm.priority" placeholder="请选择优先级" style="width: 100%;">
            <el-option label="高" :value="1" />
            <el-option label="中" :value="2" />
            <el-option label="低" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <UserSelector 
            v-model="suiteForm.owner_id" 
            :projectId="selectedProjectId" 
            :multiple="false" 
            placeholder="请选择负责人"
            :clearable="true"
          />
        </el-form-item>
        <el-form-item label="预计时长">
          <el-input v-model.number="suiteForm.expected_duration" type="number" placeholder="分钟">
            <template #append>分钟</template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveSuite" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 复制测试集对话框 -->
    <el-dialog v-model="showCopyDialog" title="复制测试集" width="500px">
      <el-form :model="copyForm" label-width="100px">
        <el-form-item label="新名称">
          <el-input v-model="copyForm.new_name" placeholder="留空则使用原名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCopyDialog = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmCopy" :loading="copying">确认复制</el-button>
      </template>
    </el-dialog>

    <!-- 移动测试集对话框 -->
    <el-dialog v-model="showMoveDialog" title="移动测试集" width="500px">
      <el-form :model="moveForm" label-width="100px">
        <el-form-item label="目标父级">
          <el-tree-select
            v-model="moveForm.target_parent_id"
            :data="suiteTree"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="选择目标父级（不选则为根级）"
            clearable
            check-strictly
            :render-after-expand="false"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMoveDialog = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmMove" :loading="moving">确认移动</el-button>
      </template>
    </el-dialog>

    <!-- 版本历史对话框 -->
    <el-dialog v-model="showVersionDialog" title="版本历史" width="700px">
      <el-descriptions v-if="versionInfo" :column="2" border style="margin-bottom: 20px;">
        <el-descriptions-item label="测试集">{{ versionInfo.suite?.name }}</el-descriptions-item>
        <el-descriptions-item label="当前版本">v{{ versionInfo.suite?.version }}</el-descriptions-item>
      </el-descriptions>

      <el-card v-if="versionInfo?.case_summary" class="summary-card">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="summary-item">
              <div class="summary-value">{{ versionInfo.case_summary.total }}</div>
              <div class="summary-label">用例总数</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <div class="summary-value approved">{{ versionInfo.case_summary.approved }}</div>
              <div class="summary-label">已批准</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <div class="summary-value reviewed">{{ versionInfo.case_summary.reviewed }}</div>
              <div class="summary-label">已评审</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <div class="summary-value pending">{{ versionInfo.case_summary.pending_review }}</div>
              <div class="summary-label">待评审</div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <el-table v-if="versionInfo?.cases" :data="versionInfo.cases" stripe style="width: 100%; margin-top: 16px;">
        <el-table-column prop="identifier" label="用例标识" width="120" />
        <el-table-column prop="title" label="标题" min-width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'approved'" type="success" size="small">已批准</el-tag>
            <el-tag v-else-if="row.status === 'reviewed'" type="success" size="small">已评审</el-tag>
            <el-tag v-else-if="row.status === 'pending_review'" type="warning" size="small">待评审</el-tag>
            <el-tag v-else type="info" size="small">设计</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column prop="updated_at" label="更新时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Document, TrendCharts, Setting, ArrowRight, ArrowDown, Lock, 
  CopyDocument, Rank, VideoPlay, Delete, Clock, DataAnalysis, ArrowLeft, Search 
} from '@element-plus/icons-vue'
import { apiService } from '@/services/api'
import UserSelector from '@/components/common/UserSelector.vue'

const router = useRouter()
const route = useRoute()

const projects = ref([])
const selectedProjectId = ref(null)
const suites = ref([])
const suiteTree = ref([])
const statistics = ref({})
const loading = ref(false)
const showCreateDialog = ref(false)
const editingSuite = ref(null)
const saving = ref(false)
const treeRef = ref(null)
const formRef = ref(null)

// 筛选表单
const filterForm = reactive({
  keyword: '',
  type: '',
  status: '',
  priority: null
})

// 对话框状态
const showCopyDialog = ref(false)
const showMoveDialog = ref(false)
const showVersionDialog = ref(false)
const copying = ref(false)
const moving = ref(false)
const versionInfo = ref(null)

const copyForm = reactive({
  new_name: ''
})

const moveForm = reactive({
  target_parent_id: null
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入测试集名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ]
}

const suiteForm = reactive({
  name: '',
  description: '',
  type: 'functional',
  status: 'designing',
  priority: 2,
  owner_id: null,
  expected_duration: 0,
  parent_id: null
})

// 筛选后的测试集列表
const filteredSuites = computed(() => {
  let result = [...suites.value]
  
  if (filterForm.keyword) {
    const keyword = filterForm.keyword.toLowerCase()
    result = result.filter(suite => 
      suite.name.toLowerCase().includes(keyword) ||
      (suite.description && suite.description.toLowerCase().includes(keyword))
    )
  }
  
  if (filterForm.type) {
    result = result.filter(suite => suite.type === filterForm.type)
  }
  
  if (filterForm.status) {
    result = result.filter(suite => suite.status === filterForm.status)
  }
  
  if (filterForm.priority) {
    result = result.filter(suite => suite.priority === filterForm.priority)
  }
  
  return result
})

const loadProjects = async () => {
  try {
    const response = await apiService.projects.getList({ per_page: 100 })
    projects.value = response?.projects || response || []
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

const loadSuites = async () => {
  if (!selectedProjectId.value) return
  loading.value = true
  try {
    const response = await apiService.tests.getSuites(selectedProjectId.value, { include_cases: true })
    suites.value = response || []
    buildSuiteTree()
    await loadStatistics()
  } catch (error) {
    console.error('加载测试集失败:', error)
    ElMessage.error('加载测试集失败')
  } finally {
    loading.value = false
  }
}

const buildSuiteTree = () => {
  const map = {}
  const roots = []

  suites.value.forEach(suite => {
    map[suite.id] = { ...suite, children: [] }
  })

  suites.value.forEach(suite => {
    if (suite.parent_id && map[suite.parent_id]) {
      map[suite.parent_id].children.push(map[suite.id])
    } else {
      roots.push(map[suite.id])
    }
  })

  suiteTree.value = roots
}

const loadStatistics = async () => {
  if (!selectedProjectId.value) return
  try {
    const response = await apiService.tests.getProjectStatistics(selectedProjectId.value)
    statistics.value = response?.data || {}
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const handleProjectChange = async (projectId) => {
  if (projectId) {
    await loadSuites()
  } else {
    suites.value = []
    suiteTree.value = []
  }
}

const handleFilter = () => {
  // 筛选逻辑在 computed 中处理
}

const resetFilter = () => {
  filterForm.keyword = ''
  filterForm.type = ''
  filterForm.status = ''
  filterForm.priority = null
}

const handleRowClick = (row) => {
  handleViewDetail(row)
}

const handleViewDetail = (suite) => {
  router.push(`/projects/${selectedProjectId.value}/tests/suites/${suite.id}`)
}

const handleViewCases = (suite) => {
  router.push(`/projects/${selectedProjectId.value}/tests/suites/${suite.id}/cases`)
}

const handleAddSuite = () => {
  editingSuite.value = null
  Object.assign(suiteForm, {
    name: '',
    description: '',
    type: 'functional',
    status: 'designing',
    priority: 2,
    owner_id: null,
    expected_duration: 0,
    parent_id: null
  })
  showCreateDialog.value = true
}

const handleEditSuite = (suite) => {
  editingSuite.value = suite
  Object.assign(suiteForm, {
    name: suite.name,
    description: suite.description,
    type: suite.type,
    status: suite.status,
    priority: suite.priority,
    owner_id: suite.owner_id,
    expected_duration: suite.expected_duration,
    parent_id: suite.parent_id
  })
  showCreateDialog.value = true
}

const handleMoreAction = (command, suite) => {
  switch (command) {
    case 'execute':
      handleExecuteSuite(suite)
      break
    case 'copy':
      handleCopySuite(suite)
      break
    case 'move':
      handleMoveSuite(suite)
      break
    case 'history':
      handleVersionHistory(suite)
      break
    case 'delete':
      handleDeleteSuite(suite)
      break
  }
}

const handleExecuteSuite = (suite) => {
  router.push(`/projects/${selectedProjectId.value}/tests/executions?suite_id=${suite.id}`)
}

const handleCopySuite = (suite) => {
  copyForm.new_name = `${suite.name} - 复制`
  editingSuite.value = suite
  showCopyDialog.value = true
}

const handleMoveSuite = (suite) => {
  moveForm.target_parent_id = suite.parent_id
  editingSuite.value = suite
  showMoveDialog.value = true
}

const handleVersionHistory = async (suite) => {
  try {
    const response = await apiService.tests.getSuiteVersionHistory(suite.id)
    versionInfo.value = response?.data || response
    showVersionDialog.value = true
  } catch (error) {
    ElMessage.error('加载版本历史失败')
  }
}

const handleDeleteSuite = async (suite) => {
  try {
    await ElMessageBox.confirm('确定要删除这个测试集吗？删除后不可恢复。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await apiService.tests.deleteSuite(suite.id)
    ElMessage.success('删除成功')
    await loadSuites()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleConfirmCopy = async () => {
  copying.value = true
  try {
    await apiService.tests.batchOperateSuites({
      operation: 'copy',
      suite_ids: [editingSuite.value.id],
      target_project_id: selectedProjectId.value,
      new_name: copyForm.new_name
    })
    ElMessage.success('复制成功')
    showCopyDialog.value = false
    await loadSuites()
  } catch (error) {
    ElMessage.error('复制失败')
  } finally {
    copying.value = false
  }
}

const handleConfirmMove = async () => {
  moving.value = true
  try {
    await apiService.tests.updateSuite(editingSuite.value.id, {
      parent_id: moveForm.target_parent_id
    })
    ElMessage.success('移动成功')
    showMoveDialog.value = false
    await loadSuites()
  } catch (error) {
    ElMessage.error('移动失败')
  } finally {
    moving.value = false
  }
}

const handleSaveSuite = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const data = {
      ...suiteForm,
      project_id: selectedProjectId.value
    }

    if (editingSuite.value) {
      await apiService.tests.updateSuite(editingSuite.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await apiService.tests.createSuite(data)
      ElMessage.success('创建成功')
    }

    showCreateDialog.value = false
    editingSuite.value = null
    await loadSuites()
  } catch (error) {
    ElMessage.error(editingSuite.value ? '更新失败' : '创建失败')
  } finally {
    saving.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const showBackButton = computed(() => {
  return route.params.projectId && canGoBack.value
})

const canGoBack = ref(false)

const handleGoBack = () => {
  if (canGoBack.value && window.history.length > 1) {
    router.go(-1)
  } else if (route.params.projectId) {
    router.push(`/projects/${route.params.projectId}/tests/suites`)
  } else {
    router.push('/projects/list')
  }
}

const goToDashboard = () => {
  router.push(`/projects/${selectedProjectId.value}/tests/dashboard`)
}

onMounted(async () => {
  canGoBack.value = window.history.length > 1
  await loadProjects()
  if (route.params.projectId) {
    selectedProjectId.value = parseInt(route.params.projectId)
    await handleProjectChange(selectedProjectId.value)
  }
})
</script>

<style scoped>
.test-suite-list {
  padding: 20px;
}

.suite-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.suite-header h2 {
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
}

.empty-tip {
  margin-top: 40px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-card.clickable {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-content {
  padding: 10px 0;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-form .el-form-item {
  margin-bottom: 0;
}

.list-card {
  min-height: 400px;
}

.suite-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-icon {
  font-size: 18px;
  color: #409EFF;
}

.type-icon.warning {
  color: #E6A23C;
}

.type-icon.danger {
  color: #F56C6C;
}

.type-icon.info {
  color: #909399;
}

.suite-name {
  font-weight: 500;
  color: #303133;
}

.text-muted {
  color: #909399;
}

.summary-card {
  margin-top: 16px;
}

.summary-item {
  text-align: center;
  padding: 12px 0;
}

.summary-value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
}

.summary-value.approved {
  color: #67C23A;
}

.summary-value.reviewed {
  color: #409EFF;
}

.summary-value.pending {
  color: #E6A23C;
}

.summary-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.danger {
  color: #F56C6C;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .test-suite-list {
    padding: 12px;
  }

  .suite-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  .suite-header h2 {
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

  .filter-form {
    flex-direction: column;
  }

  .filter-form .el-form-item {
    width: 100%;
    margin-right: 0;
  }

  .filter-form .el-input,
  .filter-form .el-select {
    width: 100% !important;
  }

  .el-table {
    font-size: 12px;
  }

  .el-table th,
  .el-table td {
    padding: 8px 4px;
  }

  .stat-number {
    font-size: 20px;
  }

  .stat-label {
    font-size: 12px;
  }
}

@media screen and (max-width: 480px) {
  .test-suite-list {
    padding: 8px;
  }

  .suite-header h2 {
    font-size: 16px;
  }

  .el-table {
    font-size: 11px;
  }
}
</style>
