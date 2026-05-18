<template>
  <div class="my-todos">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-left">
          <el-button @click="$router.push('/dashboard')" class="btn-back">
            <el-icon><ArrowLeft /></el-icon>
            返回个人工作台
          </el-button>
        </div>
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Bell /></el-icon>
          </div>
          <div class="title-text">
            <h1>待办事项</h1>
            <p class="subtitle">查看和处理您的待办任务</p>
          </div>
        </div>
        <div class="header-actions">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索待办事项..."
            prefix-icon="Search"
            clearable
            class="search-input"
          />
          <el-select v-model="filterCategory" placeholder="筛选类型" clearable class="filter-select">
            <el-option label="全部" value="" />
            <el-option label="审批类" value="approval" />
            <el-option label="Bug相关" value="bug" />
            <el-option label="评审类" value="review" />
            <el-option label="合同相关" value="contract" />
          </el-select>
          <el-select v-model="filterPriority" placeholder="筛选优先级" clearable class="filter-select-priority">
            <el-option label="全部" value="" />
            <el-option label="紧急" value="urgent" />
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
          <el-button type="primary" @click="refreshAll" :loading="loading" class="btn-refresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-total" @click="filterByCategory('')">
            <div class="stat-icon-wrapper stat-icon-wrapper-total">
              <el-icon><Bell /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ summary.total }}</div>
              <div class="stat-label">待办总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-approval" @click="filterByCategory('approval')">
            <div class="stat-icon-wrapper stat-icon-wrapper-approval">
              <el-icon><Stamp /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ summary.approvals?.total || 0 }}</div>
              <div class="stat-label">待我审批</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-bug" @click="filterByCategory('bug')">
            <div class="stat-icon-wrapper stat-icon-wrapper-bug">
              <el-icon><CircleClose /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ summary.bugs?.total || 0 }}</div>
              <div class="stat-label">待处理Bug</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-review" @click="filterByCategory('review')">
            <div class="stat-icon-wrapper stat-icon-wrapper-review">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ summary.reviews?.total || 0 }}</div>
              <div class="stat-label">待我评审</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 全部待办事项 -->
    <div class="content-section animate-fade-in-up delay-200">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <el-icon><List /></el-icon>
              <h3>全部待办事项</h3>
              <span class="total-count">共 {{ filteredTodos.length }} 项</span>
            </div>
          </div>
        </template>

        <el-table 
          :data="paginatedTodos" 
          v-loading="loading" 
          stripe 
          class="custom-table"
          :row-class-name="getRowClassName"
          @row-click="handleRowClick"
        >
          <el-table-column prop="type_name" label="类型" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getCategoryTagType(row.category)" size="small" effect="light" class="category-tag">
                {{ row.type_name }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="250">
            <template #default="{ row }">
              <div class="todo-title">
                <el-icon v-if="row.is_overdue" class="overdue-icon"><WarningFilled /></el-icon>
                <span :class="{ 'overdue-text': row.is_overdue }">{{ row.title }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)" size="small" effect="light" class="status-tag">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="优先级" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="getPriorityTagType(row.priority)" size="small" effect="dark" class="priority-tag">
                {{ getPriorityText(row.priority) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="applicant_name" label="申请人" width="100">
            <template #default="{ row }">
              <div class="applicant-name">{{ row.applicant_name || '-' }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="due_date" label="截止时间" width="120" align="center">
            <template #default="{ row }">
              <span :class="{ 'overdue-text': row.is_overdue }">
                {{ row.due_date ? formatDate(row.due_date) : '-' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160" align="center">
            <template #default="{ row }">
              <div class="timestamp">{{ formatDateTime(row.created_at) }}</div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click.stop="handleTodoAction(row)" class="action-btn">
                {{ getActionText(row) }}
              </el-button>
              <el-button size="small" @click.stop="viewDetail(row)" class="detail-btn">详情</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-section">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredTodos.length"
            layout="total, sizes, prev, pager, next, jumper"
          />
        </div>
      </el-card>
    </div>

    <!-- 待我审批 -->
    <div class="content-section animate-fade-in-up delay-300" v-if="approvalTodos.length > 0">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <el-icon><Stamp /></el-icon>
              <h3>待我审批</h3>
              <span class="section-badge badge-approval">{{ approvalTodos.length }}</span>
            </div>
          </div>
        </template>

        <el-table :data="approvalTodos" v-loading="loading" stripe class="custom-table">
          <el-table-column prop="type_name" label="审批类型" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getApprovalTypeTag(row.type)" size="small" effect="light" class="category-tag">
                {{ row.type_name }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="200">
            <template #default="{ row }">
              <el-button type="primary" link @click="viewDetail(row)" class="title-link">
                {{ row.title }}
              </el-button>
            </template>
          </el-table-column>
          <el-table-column prop="applicant_name" label="申请人" width="100">
            <template #default="{ row }">
              <div class="applicant-name">{{ row.applicant_name }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="warning" size="small" effect="light" class="status-tag">待审批</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="申请时间" width="160" align="center">
            <template #default="{ row }">
              <div class="timestamp">{{ formatDateTime(row.created_at) }}</div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="success" size="small" @click="handleApprove(row)" class="approve-btn">
                <el-icon><Check /></el-icon>批准
              </el-button>
              <el-button type="danger" size="small" @click="handleReject(row)" class="reject-btn">
                <el-icon><Close /></el-icon>拒绝
              </el-button>
              <el-button size="small" @click="viewDetail(row)" class="detail-btn">详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Bug待办 -->
    <div class="content-section animate-fade-in-up delay-300" v-if="bugTodos.length > 0" ref="bugSectionRef">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <el-icon><CircleClose /></el-icon>
              <h3>Bug待办</h3>
              <span class="section-badge badge-bug">{{ bugTodos.length }}</span>
            </div>
          </div>
        </template>

        <el-table :data="bugTodos" v-loading="loading" stripe class="custom-table">
          <el-table-column prop="type_name" label="类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.type === 'to_resolve' ? 'danger' : 'primary'" size="small" effect="light" class="category-tag">
                {{ row.type_name }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="Bug标题" min-width="200">
            <template #default="{ row }">
              <el-button type="primary" link @click="row.link ? router.push(row.link) : null" class="title-link">
                {{ row.title }}
              </el-button>
            </template>
          </el-table-column>
          <el-table-column prop="severity" label="严重程度" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getSeverityTagType(row.severity)" size="small" effect="light" class="severity-tag">
                {{ getSeverityText(row.severity) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="优先级" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="getPriorityTagType(row.priority)" size="small" effect="light" class="priority-tag">
                {{ getPriorityText(row.priority) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getBugStatusTagType(row.status)" size="small" effect="light" class="status-tag">
                {{ getBugStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160" align="center">
            <template #default="{ row }">
              <div class="timestamp">{{ formatDateTime(row.created_at) }}</div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="row.link ? router.push(row.link) : null" class="action-btn">
                {{ row.type === 'to_resolve' ? '处理' : '验证' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 待我评审 -->
    <div class="content-section animate-fade-in-up delay-300" v-if="reviewTodos.length > 0">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <el-icon><Document /></el-icon>
              <h3>待我评审</h3>
              <span class="section-badge badge-review">{{ reviewTodos.length }}</span>
            </div>
          </div>
        </template>

        <el-table :data="reviewTodos" v-loading="loading" stripe class="custom-table">
          <el-table-column prop="type_name" label="评审类型" width="120" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="light" class="category-tag">{{ row.type_name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="200">
            <template #default="{ row }">
              <el-button type="primary" link @click="viewDetail(row)" class="title-link">
                {{ row.title }}
              </el-button>
            </template>
          </el-table-column>
          <el-table-column prop="identifier" label="编号" width="120" align="center">
            <template #default="{ row }">
              <span class="id-badge">{{ row.identifier }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="warning" size="small" effect="light" class="status-tag">待评审</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160" align="center">
            <template #default="{ row }">
              <div class="timestamp">{{ formatDateTime(row.created_at) }}</div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="viewDetail(row)" class="action-btn">评审</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 合同待办 -->
    <div class="content-section animate-fade-in-up delay-300" v-if="contractTodos.length > 0">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <el-icon><FolderOpened /></el-icon>
              <h3>合同待办</h3>
              <span class="section-badge badge-contract">{{ contractTodos.length }}</span>
            </div>
          </div>
        </template>

        <el-table :data="contractTodos" v-loading="loading" stripe class="custom-table">
          <el-table-column prop="type_name" label="类型" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getContractTypeTag(row.type)" size="small" effect="light" class="category-tag">
                {{ row.type_name }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="200">
            <template #default="{ row }">
              <el-button type="primary" link @click="viewDetail(row)" class="title-link">
                {{ row.title }}
              </el-button>
            </template>
          </el-table-column>
          <el-table-column prop="contract_title" label="关联合同" width="150" show-overflow-tooltip>
            <template #default="{ row }">
              <div class="contract-title">{{ row.contract_title }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="warning" size="small" effect="light" class="status-tag">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="优先级" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="getPriorityTagType(row.priority)" size="small" effect="light" class="priority-tag">
                {{ getPriorityText(row.priority) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="计划时间" width="120" align="center">
            <template #default="{ row }">
              <div class="timestamp">{{ row.created_at ? formatDate(row.created_at) : '-' }}</div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="viewDetail(row)" class="action-btn">处理</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <el-dialog v-model="approvalDialogVisible" :title="isApprovalMode ? '审批申请' : '申请详情'" width="600px" class="approval-dialog">
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
  WarningFilled, CircleClose, FolderOpened, Check, Close
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
    review: 'success',
    contract: 'info'
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
/* 导入设计系统 */
@import '@/styles/design-system.css';

.my-todos {
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  min-height: 100%;
}

/* 页面头部 - 玻璃拟态风格 */
.page-header {
  position: relative;
  margin-bottom: 24px;
  padding: 28px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px -10px rgba(102, 126, 234, 0.4);
}

.page-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at top right, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse at bottom left, rgba(118, 75, 162, 0.3) 0%, transparent 50%);
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
}

.header-left {
  margin-bottom: 16px;
}

.btn-back {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transition: all 0.3s;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
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

.header-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.search-input {
  width: 280px;
}

.search-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 10px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.filter-select,
.filter-select-priority {
  width: 140px;
}

.filter-select :deep(.el-input__wrapper),
.filter-select-priority :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 10px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.btn-refresh {
  background: rgba(255, 255, 255, 0.95);
  border: none;
  color: #667eea;
  font-weight: 600;
  transition: all 0.3s;
  border-radius: 10px;
}

.btn-refresh:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
}

/* 统计卡片区域 */
.stats-row {
  margin-bottom: 24px;
  padding: 0 4px;
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
  cursor: pointer;
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

.stat-card-total::before { background: linear-gradient(90deg, #667eea, #764ba2); }
.stat-card-approval::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-bug::before { background: linear-gradient(90deg, #ef4444, #f87171); }
.stat-card-review::before { background: linear-gradient(90deg, #10b981, #34d399); }

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
  color: #667eea;
  box-shadow: 0 4px 15px -3px rgba(102, 126, 234, 0.4);
}

.stat-icon-wrapper-approval {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-bug {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
  box-shadow: 0 4px 15px -3px rgba(239, 68, 68, 0.4);
}

.stat-icon-wrapper-review {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-approval .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-bug .stat-value {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-review .stat-value {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
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
  margin-bottom: 20px;
}

.glass-card:hover {
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.12), 0 10px 20px -5px rgba(0, 0, 0, 0.08);
}

.glass-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

/* 内容区域 */
.content-section {
  margin-bottom: 20px;
  padding: 0 4px;
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
}

.card-title .el-icon {
  color: #6366f1;
  font-size: 20px;
}

.card-title h3 {
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

.section-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  margin-left: 8px;
}

.badge-approval {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
}

.badge-bug {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
}

.badge-review {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
}

.badge-contract {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #6366f1;
}

/* 自定义表格 */
.custom-table {
  --el-table-header-bg-color: rgba(241, 245, 249, 0.8);
  --el-table-row-hover-bg-color: rgba(99, 102, 241, 0.05);
}

.custom-table :deep(.el-table__header th) {
  font-weight: 600;
  color: #1e293b;
  background: rgba(241, 245, 249, 0.8);
}

.custom-table :deep(.el-table__row) {
  transition: all 0.3s;
}

/* 待办标题 */
.todo-title {
  display: flex;
  align-items: center;
  gap: 6px;
}

.overdue-icon {
  color: #ef4444;
  font-size: 16px;
}

.overdue-text {
  color: #ef4444;
  font-weight: 500;
}

/* 标签样式 */
.category-tag,
.status-tag,
.priority-tag,
.severity-tag {
  font-weight: 500;
  border-radius: 6px;
}

.priority-tag {
  font-size: 11px;
}

/* 申请人 */
.applicant-name {
  font-weight: 500;
  color: #475569;
}

/* 时间戳 */
.timestamp {
  font-size: 13px;
  color: #64748b;
}

/* ID徽章 */
.id-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
}

/* 合同标题 */
.contract-title {
  font-size: 13px;
  color: #64748b;
}

/* 标题链接 */
.title-link {
  font-weight: 500;
}

/* 操作按钮 */
.action-btn,
.detail-btn,
.approve-btn,
.reject-btn {
  transition: all 0.3s;
}

.action-btn:hover,
.approve-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px -2px rgba(99, 102, 241, 0.4);
}

.reject-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px -2px rgba(239, 68, 68, 0.4);
}

.detail-btn:hover {
  transform: translateY(-2px);
}

/* 行样式 */
.overdue-row {
  background-color: rgba(254, 226, 226, 0.5) !important;
}

.urgent-row {
  background-color: rgba(254, 243, 199, 0.5) !important;
}

/* 分页 */
.pagination-section {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

/* 审批对话框 */
.approval-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  border-radius: 16px 16px 0 0;
}

.approval-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.approval-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
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
  .my-todos {
    padding: 0;
  }

  .page-header {
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 16px;
  }

  .header-left {
    margin-bottom: 12px;
  }

  .header-title {
    gap: 14px;
    margin-bottom: 16px;
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

  .header-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .search-input,
  .filter-select,
  .filter-select-priority {
    width: 100% !important;
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

  .content-section {
    margin-bottom: 16px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .card-title {
    flex-wrap: wrap;
  }

  .custom-table :deep(.el-table__row:hover) .view-btn {
    opacity: 1;
  }

  .pagination-section {
    justify-content: center;
  }

  .el-table {
    font-size: 12px !important;
  }

  .el-table th,
  .el-table td {
    padding: 8px 6px !important;
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

  .el-pagination {
    font-size: 11px !important;
  }
}
</style>
