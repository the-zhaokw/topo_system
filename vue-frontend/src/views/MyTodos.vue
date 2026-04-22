<template>
  <div class="my-todos">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="$router.push('/dashboard')" type="primary" plain>
          <el-icon><ArrowLeft /></el-icon>
          返回个人工作台
        </el-button>
      </div>
      <h2>待办事项</h2>
      <div class="header-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索待办事项..."
          prefix-icon="Search"
          clearable
          style="width: 300px"
        />
        <el-select v-model="filterCategory" placeholder="筛选类型" clearable style="width: 150px; margin-left: 10px">
          <el-option label="全部" value="" />
          <el-option label="审批类" value="approval" />
          <el-option label="Bug相关" value="bug" />

          <el-option label="评审类" value="review" />
          <el-option label="合同相关" value="contract" />
        </el-select>
        <el-select v-model="filterPriority" placeholder="筛选优先级" clearable style="width: 120px; margin-left: 10px">
          <el-option label="全部" value="" />
          <el-option label="紧急" value="urgent" />
          <el-option label="高" value="high" />
          <el-option label="中" value="medium" />
          <el-option label="低" value="low" />
        </el-select>
        <el-button type="primary" @click="refreshAll" :loading="loading" style="margin-left: 10px">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="3">
        <el-card class="stat-card total-card" shadow="hover">
          <div class="stat-icon-wrapper">
            <div class="stat-icon-box" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
              <el-icon :size="24" style="color: white;"><Bell /></el-icon>
            </div>
            <div class="stat-badge-count" :style="{ background: summary.total > 0 ? '#F56C6C' : '#409EFF' }">{{ summary.total }}</div>
          </div>
          <div class="stat-content">
            <div class="stat-label">待办总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="3">
        <el-card class="stat-card" shadow="hover" @click="filterByCategory('approval')">
          <div class="stat-icon-wrapper">
            <div class="stat-icon-box" style="background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);">
              <el-icon :size="24" style="color: white;"><Stamp /></el-icon>
            </div>
            <div class="stat-badge-count" :style="{ background: summary.approvals?.total > 0 ? '#F56C6C' : '#409EFF' }">{{ summary.approvals?.total || 0 }}</div>
          </div>
          <div class="stat-content">
            <div class="stat-label">待我审批</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="3">
        <el-card class="stat-card" shadow="hover" @click="filterByCategory('bug')">
          <div class="stat-icon-wrapper">
            <div class="stat-icon-box" style="background: linear-gradient(135deg, #F44336 0%, #D32F2F 100%);">
              <el-icon :size="24" style="color: white;"><CircleClose /></el-icon>
            </div>
            <div class="stat-badge-count" :style="{ background: summary.bugs?.total > 0 ? '#F56C6C' : '#409EFF' }">{{ summary.bugs?.total || 0 }}</div>
          </div>
          <div class="stat-content">
            <div class="stat-label">Bug待办</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="3">
        <el-card class="stat-card" shadow="hover" @click="filterByCategory('review')">
          <div class="stat-icon-wrapper">
            <div class="stat-icon-box" style="background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);">
              <el-icon :size="24" style="color: white;"><Document /></el-icon>
            </div>
            <div class="stat-badge-count" :style="{ background: summary.reviews?.total > 0 ? '#F56C6C' : '#409EFF' }">{{ summary.reviews?.total || 0 }}</div>
          </div>
          <div class="stat-content">
            <div class="stat-label">待我评审</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="3">
        <el-card class="stat-card" shadow="hover" @click="filterByCategory('contract')">
          <div class="stat-icon-wrapper">
            <div class="stat-icon-box" style="background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%);">
              <el-icon :size="24" style="color: white;"><FolderOpened /></el-icon>
            </div>
            <div class="stat-badge-count" :style="{ background: summary.contracts?.total > 0 ? '#F56C6C' : '#409EFF' }">{{ summary.contracts?.total || 0 }}</div>
          </div>
          <div class="stat-content">
            <div class="stat-label">合同待办</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="3">
        <el-card class="stat-card urgent-card" shadow="hover">
          <div class="stat-icon-wrapper">
            <div class="stat-icon-box" style="background: linear-gradient(135deg, #E91E63 0%, #C2185B 100%);">
              <el-icon :size="24" style="color: white;"><Warning /></el-icon>
            </div>
            <div class="stat-badge-count" :style="{ background: urgentCount > 0 ? '#F56C6C' : '#409EFF' }">{{ urgentCount }}</div>
          </div>
          <div class="stat-content">
            <div class="stat-label">紧急待办</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="section-card">
      <template #header>
        <div class="card-header">
          <span>全部待办事项</span>
          <div class="header-tags">
            <el-tag type="info">共 {{ filteredTodos.length }} 项</el-tag>
          </div>
        </div>
      </template>

      <el-table 
        :data="paginatedTodos" 
        v-loading="loading" 
        stripe 
        :row-class-name="getRowClassName"
        @row-click="handleRowClick"
      >
        <el-table-column prop="type_name" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">
              {{ row.type_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="250">
          <template #default="{ row }">
            <div class="todo-title">
              <el-icon v-if="row.is_overdue" color="#F56C6C"><WarningFilled /></el-icon>
              <span :class="{ 'overdue-text': row.is_overdue }">{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="90">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small" effect="dark">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="applicant_name" label="申请人" width="100">
          <template #default="{ row }">
            {{ row.applicant_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="截止时间" width="120">
          <template #default="{ row }">
            <span :class="{ 'overdue-text': row.is_overdue }">
              {{ row.due_date ? formatDate(row.due_date) : '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click.stop="handleTodoAction(row)">
              {{ getActionText(row) }}
            </el-button>
            <el-button size="small" @click.stop="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredTodos.length"
          layout="total, sizes, prev, pager, next, jumper"
        />
      </div>
    </el-card>

    <el-card class="section-card" v-if="approvalTodos.length > 0">
      <template #header>
        <div class="card-header">
          <span>待我审批</span>
          <el-tag type="warning">{{ approvalTodos.length }}</el-tag>
        </div>
      </template>

      <el-table :data="approvalTodos" v-loading="loading" stripe>
        <el-table-column prop="type_name" label="审批类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getApprovalTypeTag(row.type)" size="small">
              {{ row.type_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row)">
              {{ row.title }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="applicant_name" label="申请人" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag type="warning" size="small">待审批</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="success" size="small" @click="handleApprove(row)">批准</el-button>
            <el-button type="danger" size="small" @click="handleReject(row)">拒绝</el-button>
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="section-card" v-if="bugTodos.length > 0" ref="bugSectionRef">
      <template #header>
        <div class="card-header">
          <span>Bug待办</span>
          <el-tag type="danger">{{ bugTodos.length }}</el-tag>
        </div>
      </template>

      <el-table :data="bugTodos" v-loading="loading" stripe>
        <el-table-column prop="type_name" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'to_resolve' ? 'danger' : 'primary'" size="small">
              {{ row.type_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="Bug标题" min-width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="row.link ? router.push(row.link) : null">
              {{ row.title }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTagType(row.severity)" size="small">
              {{ getSeverityText(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="90">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getBugStatusTagType(row.status)" size="small">
              {{ getBugStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="row.link ? router.push(row.link) : null">
              {{ row.type === 'to_resolve' ? '处理' : '验证' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>



    <el-card class="section-card" v-if="reviewTodos.length > 0">
      <template #header>
        <div class="card-header">
          <span>待我评审</span>
          <el-tag type="info">{{ reviewTodos.length }}</el-tag>
        </div>
      </template>

      <el-table :data="reviewTodos" v-loading="loading" stripe>
        <el-table-column prop="type_name" label="评审类型" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.type_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row)">
              {{ row.title }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="identifier" label="编号" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag type="warning" size="small">待评审</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row)">评审</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="section-card" v-if="contractTodos.length > 0">
      <template #header>
        <div class="card-header">
          <span>合同待办</span>
          <el-tag type="info">{{ contractTodos.length }}</el-tag>
        </div>
      </template>

      <el-table :data="contractTodos" v-loading="loading" stripe>
        <el-table-column prop="type_name" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getContractTypeTag(row.type)" size="small">
              {{ row.type_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row)">
              {{ row.title }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="contract_title" label="关联合同" width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag type="warning" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="90">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="计划时间" width="120">
          <template #default="{ row }">
            {{ row.created_at ? formatDate(row.created_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="approvalDialogVisible" :title="isApprovalMode ? '审批申请' : '申请详情'" width="600px">
      <el-descriptions :column="2" border v-if="currentApproval">
        <el-descriptions-item label="申请 ID" :span="2">
          {{ currentApproval.id }}
        </el-descriptions-item>
        <el-descriptions-item label="类型">
          {{ currentApproval.type_name }}
        </el-descriptions-item>
        <el-descriptions-item label="申请人">
          {{ currentApproval.applicant_name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="标题" :span="2">
          {{ currentApproval.title }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTag(currentApproval.status)" size="small">
            {{ getApprovalStatusText(currentApproval.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="申请时间">
          {{ currentApproval.created_at ? formatDateTime(currentApproval.created_at) : '-' }}
        </el-descriptions-item>
        
        <template v-if="currentApproval.details">
          <el-descriptions-item 
            v-for="(value, key) in currentApproval.details" 
            :key="key" 
            :label="getFieldLabel(key)"
          >
            {{ formatDetailValue(key, value) }}
          </el-descriptions-item>
        </template>
      </el-descriptions>
      <el-form v-if="isApprovalMode" :model="approvalForm" style="margin-top: 20px;">
        <el-form-item label="审批意见">
          <el-input v-model="approvalForm.comment" type="textarea" :rows="3" placeholder="请输入审批意见" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeApprovalDialog">关闭</el-button>
        <template v-if="isApprovalMode">
          <el-button type="success" @click="submitApproval('approve')">批准</el-button>
          <el-button type="danger" @click="submitApproval('reject')">拒绝</el-button>
        </template>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ArrowLeft, Refresh, Bell, Stamp, List, Document, Warning, 
  WarningFilled, CircleClose, FolderOpened
} from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const router = useRouter()

const loading = ref(false)
const allTodos = ref([])
const approvalTodos = ref([])
const bugTodos = ref([])

const reviewTodos = ref([])
const contractTodos = ref([])
const summary = ref({
  total: 0,
  approvals: { total: 0 },
  bugs: { total: 0 },
  reviews: { total: 0 },
  contracts: { total: 0 }
})

const searchKeyword = ref('')
const filterCategory = ref('')
const filterPriority = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

const approvalDialogVisible = ref(false)
const isApprovalMode = ref(true)
const currentApproval = ref(null)
const approvalForm = ref({
  comment: ''
})
const bugSectionRef = ref(null)

const filteredTodos = computed(() => {
  let result = allTodos.value
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(todo => 
      todo.title?.toLowerCase().includes(keyword) ||
      todo.type_name?.toLowerCase().includes(keyword) ||
      todo.applicant_name?.toLowerCase().includes(keyword)
    )
  }
  
  if (filterCategory.value) {
    result = result.filter(todo => todo.category === filterCategory.value)
  }
  
  if (filterPriority.value) {
    result = result.filter(todo => todo.priority === filterPriority.value)
  }
  
  return result
})

const paginatedTodos = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredTodos.value.slice(start, end)
})

const urgentCount = computed(() => 
  allTodos.value.filter(todo => todo.priority === 'urgent').length
)

const fetchSummary = async () => {
  try {
    const data = await apiService.todos.getSummary()
    summary.value = data || {
      total: 0,
      approvals: { total: 0 },
      bugs: { total: 0 },
      reviews: { total: 0 },
      contracts: { total: 0 }
    }
  } catch (error) {
    console.error('获取待办统计失败:', error)
  }
}

const fetchAllTodos = async () => {
  loading.value = true
  try {
    const response = await apiService.todos.getAll()
    allTodos.value = response?.todos || []
  } catch (error) {
    console.error('获取待办事项失败:', error)
    ElMessage.error('获取待办事项失败')
  } finally {
    loading.value = false
  }
}

const fetchApprovalTodos = async () => {
  try {
    const response = await apiService.todos.getApprovals()
    approvalTodos.value = response?.approvals || []
  } catch (error) {
    console.error('获取待我审批失败:', error)
    approvalTodos.value = []
  }
}

const fetchBugTodos = async () => {
  try {
    const response = await apiService.todos.getBugs()
    bugTodos.value = response?.bugs || []
  } catch (error) {
    console.error('获取Bug待办失败:', error)
    bugTodos.value = []
  }
}



const fetchReviewTodos = async () => {
  try {
    const response = await apiService.todos.getReviews()
    console.log('getReviews response:', response)
    reviewTodos.value = response?.reviews || []
    console.log('reviewTodos:', reviewTodos.value)
  } catch (error) {
    console.error('获取待我评审失败:', error)
    reviewTodos.value = []
  }
}

const fetchContractTodos = async () => {
  try {
    const response = await apiService.todos.getContracts()
    contractTodos.value = response?.contracts || []
  } catch (error) {
    console.error('获取合同待办失败:', error)
    contractTodos.value = []
  }
}

const refreshAll = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchSummary(),
      fetchAllTodos(),
      fetchApprovalTodos(),
      fetchBugTodos(),
      fetchReviewTodos(),
      fetchContractTodos()
    ])
    ElMessage.success('刷新成功')
  } finally {
    loading.value = false
  }
}

const filterByCategory = (category) => {
  filterCategory.value = category
  currentPage.value = 1
  if (category === 'bug' && bugSectionRef.value?.$el) {
    bugSectionRef.value.$el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const handleRowClick = (row) => {
  viewDetail(row)
}

const handleTodoAction = (row) => {
  if (row.category === 'approval') {
    currentApproval.value = row
    isApprovalMode.value = true
    approvalDialogVisible.value = true
  } else if (row.category === 'bug') {
    if (row.link) {
      router.push(row.link)
    }
  } else if (row.category === 'review') {
    viewDetail(row)
  }
}

const viewDetail = (row) => {
  switch (row.type) {
    case 'leave':
    case 'overtime':
    case 'attendance_exception':
      currentApproval.value = row
      isApprovalMode.value = false
      approvalDialogVisible.value = true
      break
    case 'contract':
      router.push(`/contracts/${row.contract_id || row.id}`)
      break
    case 'to_resolve':
    case 'to_verify':
      if (row.link) {
        router.push(row.link)
      }
      break

    case 'requirement':
      console.log('requirement row:', row)
      console.log('doc_id:', row.doc_id, 'project_id:', row.project_id)
      if (row.doc_id && row.project_id) {
        router.push(`/projects/${row.project_id}/requirements/${row.doc_id}`)
      } else if (row.doc_id) {
        router.push(`/requirements/${row.doc_id}`)
      } else {
        ElMessage.info('无法查看需求文档：缺少文档ID')
      }
      break
    case 'test_case':
      router.push(`/test-cases/${row.id}`)
      break
    case 'delivery':
    case 'risk':
    case 'payment':
      router.push(`/contracts/${row.contract_id || row.id}`)
      break
    default:
      if (row.link) {
        router.push(row.link)
      } else {
        ElMessage.info('暂不支持查看详情')
      }
  }
}

const handleApprove = (row) => {
  currentApproval.value = row
  isApprovalMode.value = true
  approvalDialogVisible.value = true
}

const handleReject = async (row) => {
  currentApproval.value = row
  isApprovalMode.value = true
  approvalDialogVisible.value = true
}

const closeApprovalDialog = () => {
  approvalDialogVisible.value = false
  isApprovalMode.value = true
  approvalForm.value.comment = ''
}

const submitApproval = async (action) => {
  if (!approvalForm.value.comment && action === 'reject') {
    ElMessage.warning('拒绝申请时必须填写审批意见')
    return
  }

  try {
    const row = currentApproval.value
    const numericId = row.id ? parseInt(row.id.replace(/^[a-z]+_/, ''), 10) : row.id
    
    if (row.type === 'leave') {
      if (action === 'approve') {
        await apiService.attendance.approveLeaveApplication(numericId, {
          comment: approvalForm.value.comment
        })
      } else {
        await apiService.attendance.rejectLeaveApplication(numericId, {
          comment: approvalForm.value.comment
        })
      }
    } else if (row.type === 'overtime') {
      if (action === 'approve') {
        await apiService.attendance.approveOvertimeApplication(numericId, {
          comment: approvalForm.value.comment
        })
      } else {
        await apiService.attendance.rejectOvertimeApplication(numericId, {
          comment: approvalForm.value.comment
        })
      }
    } else if (row.type === 'attendance_exception') {
      if (action === 'approve') {
        await apiService.attendance.approveException(numericId, {
          comment: approvalForm.value.comment
        })
      } else {
        await apiService.attendance.rejectException(numericId, {
          comment: approvalForm.value.comment
        })
      }
    } else {
      ElMessage.warning('暂不支持此类型审批')
      return
    }
    
    ElMessage.success(action === 'approve' ? '审批已通过' : '已拒绝申请')
    approvalDialogVisible.value = false
    isApprovalMode.value = true
    approvalForm.value.comment = ''
    refreshAll()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '审批操作失败')
  }
}

const getActionText = (row) => {
  switch (row.category) {
    case 'approval':
      return '审批'
    case 'bug':
      return row.type === 'to_resolve' ? '处理' : '验证'

    case 'review':
      return '评审'
    default:
      return '处理'
  }
}

const getRowClassName = ({ row }) => {
  if (row.is_overdue) return 'overdue-row'
  if (row.priority === 'urgent') return 'urgent-row'
  return ''
}



const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const getCategoryTagType = (category) => {
  const map = {
    approval: 'warning',
    bug: 'danger',
    task: 'primary',
    review: 'success'
  }
  return map[category] || 'info'
}

const getStatusTagType = (status) => {
  if (status === 'pending') return 'warning'
  return 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '待处理',
    in_progress: '进行中',
    resolved: '已解决',
    closed: '已关闭'
  }
  return map[status] || status || '待处理'
}

const getPriorityTagType = (priority) => {
  const map = {
    urgent: 'danger',
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return map[priority] || 'info'
}

const getPriorityText = (priority) => {
  const map = {
    urgent: '紧急',
    high: '高',
    medium: '中',
    low: '低'
  }
  return map[priority] || priority || '中'
}

const getApprovalTypeTag = (type) => {
  const map = {
    leave: 'success',
    overtime: 'warning',
    attendance_exception: 'info',
    contract: 'primary'
  }
  return map[type] || ''
}

const getContractTypeTag = (type) => {
  const map = {
    delivery: 'primary',
    risk: 'danger',
    payment: 'warning'
  }
  return map[type] || 'info'
}

const getSeverityTagType = (severity) => {
  const map = {
    low: 'info',
    medium: 'warning',
    high: 'danger',
    critical: 'danger'
  }
  return map[severity] || 'info'
}

const getSeverityText = (severity) => {
  const map = {
    low: '低',
    medium: '中',
    high: '高',
    critical: '严重'
  }
  return map[severity] || severity || '中'
}

const getBugStatusTagType = (status) => {
  const map = {
    new: 'info',
    assigned: 'primary',
    in_progress: 'warning',
    resolved: 'success',
    verified: 'success',
    closed: 'info',
    reopened: 'danger'
  }
  return map[status] || 'info'
}

const getBugStatusText = (status) => {
  const map = {
    new: '新建',
    assigned: '已分配',
    in_progress: '进行中',
    resolved: '已解决',
    verified: '已验证',
    closed: '已关闭',
    reopened: '重新打开'
  }
  return map[status] || status || '未知'
}



const getFieldLabel = (field) => {
  const labels = {
    leave_type: '请假类型',
    start_date: '开始日期',
    end_date: '结束日期',
    date: '日期',
    start_time: '开始时间',
    end_time: '结束时间',
    reason: '原因',
    emergency_flag: '紧急',
    exception_type: '异常类型',
    record_date: '记录日期',
    contract_type: '合同类型',
    total_amount: '总金额',
    party_a: '甲方',
    party_b: '乙方'
  }
  return labels[field] || field
}

const formatDetailValue = (field, value) => {
  if (field === 'emergency_flag') {
    return value ? '是' : '否'
  }
  if (field === 'total_amount' && value) {
    return `¥${value.toLocaleString()}`
  }
  if (field.includes('date') && value) {
    return formatDate(value)
  }
  return value || '-'
}

const getStatusTag = (status) => {
  const tagTypes = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    approved_level_1: 'warning',
    approved_level_2: 'warning'
  }
  return tagTypes[status] || 'info'
}

const getApprovalStatusText = (status) => {
  const texts = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝',
    approved_level_1: '一级审批通过',
    approved_level_2: '二级审批通过'
  }
  return texts[status] || status
}

onMounted(() => {
  fetchSummary()
  fetchAllTodos()
  fetchApprovalTodos()
  fetchBugTodos()
  fetchReviewTodos()
  fetchContractTodos()
})
</script>

<style scoped>
.my-todos {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.header-left {
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 24px;
}

.header-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px 0;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-icon-box {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}

.stat-icon-wrapper {
  position: relative;
  display: inline-block;
}

.stat-badge-count {
  position: absolute;
  top: -6px;
  right: -6px;
  background: #F56C6C;
  color: white;
  font-size: 12px;
  font-weight: bold;
  min-width: 22px;
  height: 22px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  z-index: 1;
}

.stat-content {
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.stat-badge {
  position: absolute;
  bottom: -6px;
  left: -6px;
}

.section-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-tags {
  display: flex;
  gap: 10px;
}

.todo-title {
  display: flex;
  align-items: center;
  gap: 4px;
}

.overdue-text {
  color: #F56C6C;
  font-weight: 500;
}

.overdue-row {
  background-color: #FEF0F0 !important;
}

.urgent-row {
  background-color: #FDF6EC !important;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.detail-item {
  margin-bottom: 8px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

:deep(.el-table .el-table__row) {
  cursor: pointer;
}

:deep(.el-table .el-table__row:hover) {
  background-color: #f5f7fa;
}

@media screen and (max-width: 768px) {
  .my-todos {
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
    margin: 0 0 12px 0;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 80px;
    max-width: calc(50% - 4px);
    font-size: 12px;
    padding: 8px 12px;
  }

  .stats-row {
    margin-bottom: 16px;
  }

  .stats-row .el-col {
    width: 50%;
    max-width: 50%;
    flex: 0 0 50%;
    margin-bottom: 12px;
  }

  .stat-card {
    padding: 16px 0;
  }

  .stat-icon-box {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    margin-bottom: 8px;
  }

  .stat-icon-box i {
    font-size: 20px;
  }

  .stat-label {
    font-size: 12px;
  }

  .section-card {
    margin-bottom: 16px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    font-size: 14px;
  }

  .header-tags {
    flex-wrap: wrap;
    gap: 6px;
  }

  .header-tags .el-tag {
    font-size: 11px;
    padding: 2px 6px;
  }

  .pagination-container {
    margin-top: 16px;
    justify-content: center;
  }

  .el-pagination {
    font-size: 11px !important;
    flex-wrap: wrap;
    gap: 4px;
  }

  .el-pagination__sizes,
  .el-pagination__jump {
    display: none !important;
  }

  .el-pagination button,
  .el-pager li {
    min-width: 26px !important;
    height: 26px !important;
    line-height: 26px !important;
    font-size: 11px !important;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
    max-height: 90vh !important;
  }

  .el-dialog__header {
    padding: 12px !important;
  }

  .el-dialog__body {
    padding: 12px !important;
    max-height: 60vh !important;
    overflow-y: auto !important;
  }

  .el-dialog__footer {
    padding: 12px !important;
  }

  .detail-item {
    font-size: 12px;
  }
}

@media screen and (max-width: 480px) {
  .my-todos {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .header-actions .el-button {
    font-size: 11px;
    padding: 6px 10px;
    min-width: 70px;
  }

  .stats-row .el-col {
    padding: 0 6px;
  }

  .stat-icon-box {
    width: 40px;
    height: 40px;
  }

  .stat-label {
    font-size: 11px;
  }

  .el-table {
    font-size: 10px !important;
  }

  .el-pagination {
    font-size: 10px !important;
  }

  .el-pagination button,
  .el-pager li {
    min-width: 24px !important;
    height: 24px !important;
    line-height: 24px !important;
  }
}
</style>
