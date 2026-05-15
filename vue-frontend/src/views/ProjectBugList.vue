<template>
  <div class="bug-list">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><BugIcon /></el-icon>
          </div>
          <div class="title-text">
            <h1>{{ projectName }} - 缺陷报告</h1>
            <p class="subtitle">管理和跟踪项目缺陷问题</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button text class="btn-back" @click="$router.back()">
            <el-icon><ArrowLeft /></el-icon>
            返回项目
          </el-button>
          <el-button class="btn-gradient" @click="$router.push(`/projects/${projectId}/bugs/new`)">
            <el-icon><Plus /></el-icon>
            新建Bug
          </el-button>
          <el-button class="btn-success-gradient" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出缺陷
          </el-button>
          <el-button class="btn-warning-gradient" @click="showImportDialog = true">
            <el-icon><Upload /></el-icon>
            导入缺陷
          </el-button>
        </div>
      </div>
    </div>

    <!-- 导入缺陷对话框 -->
    <el-dialog v-model="showImportDialog" title="导入缺陷" width="500px" class="custom-dialog">
      <el-upload
        ref="uploadRef"
        :action="''"
        :auto-upload="false"
        :file-list="fileList"
        :on-change="handleFileChange"
        :before-upload="beforeUpload"
        accept=".xlsx,.xls,.csv"
        drag
        class="upload-area"
      >
        <el-icon class="el-icon--upload upload-icon"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持上传 .xlsx, .xls, .csv 格式文件，文件大小不超过 10MB
          </div>
        </template>
      </el-upload>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showImportDialog = false">取消</el-button>
          <el-button type="primary" @click="handleImport" :loading="importLoading" class="btn-gradient">
            导入
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 缺陷统计卡片 -->
    <el-row :gutter="16" class="bug-stats animate-fade-in-up">
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <div class="stat-card stat-card-primary" @click="filterByStat('assignedToMe')">
          <div class="stat-icon-wrapper stat-icon-wrapper-primary">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.assignedToMe || 0 }}</div>
            <div class="stat-label">待我处理的</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <div class="stat-card stat-card-warning" @click="filterByStat('unassigned')">
          <div class="stat-icon-wrapper stat-icon-wrapper-warning">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.unassigned || 0 }}</div>
            <div class="stat-label">待领取的</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <div class="stat-card stat-card-info" @click="filterByStat('openBugs')">
          <div class="stat-icon-wrapper stat-icon-wrapper-info">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.openBugs || 0 }}</div>
            <div class="stat-label">所有未关闭的</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6" :lg="6">
        <div class="stat-card stat-card-secondary" @click="filterByStat('all')">
          <div class="stat-icon-wrapper stat-icon-wrapper-secondary">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalBugs || 0 }}</div>
            <div class="stat-label">所有</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 筛选条件 - 玻璃拟态卡片 -->
    <el-card class="filter-card glass-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><Filter /></el-icon>
            筛选条件
          </span>
        </div>
      </template>
      <el-form :model="filters" label-width="80px">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="关键词">
              <el-input
                v-model="filters.keyword"
                placeholder="搜索标题或描述"
                clearable
                @clear="handleFilter"
                @keyup.enter="handleFilter"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="状态">
              <el-select v-model="filters.status" placeholder="全部" clearable @change="handleFilter">
                <el-option label="新建" value="new" />
                <el-option label="已分配" value="assigned" />
                <el-option label="进行中" value="in_progress" />
                <el-option label="已修复" value="fixed" />
                <el-option label="已解决" value="resolved" />
                <el-option label="已验证" value="verified" />
                <el-option label="已关闭" value="closed" />
                <el-option label="重新打开" value="reopened" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="严重程度">
              <el-select v-model="filters.severity" placeholder="全部" clearable @change="handleFilter">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="严重" value="critical" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="优先级">
              <el-select v-model="filters.priority" placeholder="全部" clearable @change="handleFilter">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="紧急" value="critical" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="版本">
              <el-select
                v-model="filters.version"
                placeholder="全部"
                clearable
                @change="handleFilter"
                filterable
                allow-create
                default-first-option
              >
                <el-option
                  v-for="version in availableVersions"
                  :key="version"
                  :label="version"
                  :value="version"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="模块">
              <el-select
                v-model="filters.module"
                placeholder="全部"
                clearable
                @change="handleFilter"
                filterable
                allow-create
                default-first-option
              >
                <el-option
                  v-for="module in availableModules"
                  :key="module"
                  :label="module"
                  :value="module"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="问题类型">
              <el-select
                v-model="filters.issue_type"
                placeholder="全部"
                clearable
                @change="handleFilter"
              >
                <el-option label="功能缺陷" value="功能缺陷" />
                <el-option label="界面缺陷" value="界面缺陷" />
                <el-option label="性能缺陷" value="性能缺陷" />
                <el-option label="兼容性问题" value="兼容性问题" />
                <el-option label="安全问题" value="安全问题" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label-width="0" class="filter-actions">
              <el-button @click="resetFilter">重置</el-button>
              <el-button type="primary" @click="handleFilter" class="btn-gradient">筛选</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 批量操作工具栏 -->
    <el-card v-if="selectedBugs.length > 0" class="batch-toolbar glass-card-warning" shadow="never">
      <div class="batch-toolbar-content">
        <span class="selected-count">
          <el-icon><Check /></el-icon>
          已选择 {{ selectedBugs.length }} 项
        </span>
        <div class="batch-actions">
          <el-button type="primary" size="small" @click="showBatchStatusDialog = true" class="batch-btn">
            <el-icon><Edit /></el-icon>
            批量修改状态
          </el-button>
          <el-button type="warning" size="small" @click="showBatchPriorityDialog = true" class="batch-btn">
            <el-icon><Flag /></el-icon>
            批量修改优先级
          </el-button>
          <el-button type="info" size="small" @click="showBatchSeverityDialog = true" class="batch-btn">
            <el-icon><Warning /></el-icon>
            批量修改严重程度
          </el-button>
          <el-button type="danger" size="small" @click="handleBatchDelete" class="batch-btn">
            <el-icon><Delete /></el-icon>
            批量删除
          </el-button>
          <el-button size="small" @click="selectedBugs = []" class="batch-btn">
            <el-icon><Close /></el-icon>
            取消选择
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 批量修改状态对话框 -->
    <el-dialog v-model="showBatchStatusDialog" title="批量修改状态" width="400px" class="custom-dialog">
      <el-form label-width="80px">
        <el-form-item label="新状态">
          <el-select v-model="batchUpdateData.status" placeholder="请选择状态">
            <el-option label="新建" value="new" />
            <el-option label="已分配" value="assigned" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已修复" value="fixed" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已验证" value="verified" />
            <el-option label="已关闭" value="closed" />
            <el-option label="重新打开" value="reopened" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showBatchStatusDialog = false">取消</el-button>
          <el-button type="primary" @click="handleBatchStatusUpdate" :loading="batchLoading" class="btn-gradient">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 批量修改优先级对话框 -->
    <el-dialog v-model="showBatchPriorityDialog" title="批量修改优先级" width="400px" class="custom-dialog">
      <el-form label-width="80px">
        <el-form-item label="新优先级">
          <el-select v-model="batchUpdateData.priority" placeholder="请选择优先级">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="critical" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showBatchPriorityDialog = false">取消</el-button>
          <el-button type="primary" @click="handleBatchPriorityUpdate" :loading="batchLoading" class="btn-gradient">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 批量修改严重程度对话框 -->
    <el-dialog v-model="showBatchSeverityDialog" title="批量修改严重程度" width="400px" class="custom-dialog">
      <el-form label-width="80px">
        <el-form-item label="严重程度">
          <el-select v-model="batchUpdateData.severity" placeholder="请选择严重程度">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="严重" value="critical" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showBatchSeverityDialog = false">取消</el-button>
          <el-button type="primary" @click="handleBatchSeverityUpdate" :loading="batchLoading" class="btn-gradient">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Bug表格 - 玻璃拟态卡片 -->
    <el-card class="bug-table-card glass-card" shadow="never">
      <el-table
        :data="bugs"
        v-loading="loading"
        style="width: 100%"
        @sort-change="handleSortChange"
        @selection-change="handleSelectionChange"
        class="custom-table"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="id" label="ID" width="80" sortable="custom" />

        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <router-link :to="`/projects/${projectId}/bugs/${row.id}`" class="bug-title-link">
              {{ row.title }}
            </router-link>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small" effect="light" class="status-tag">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)" size="small" effect="light" class="severity-tag">
              {{ getSeverityText(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small" effect="light" class="priority-tag">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="version" label="版本" width="100" />

        <el-table-column prop="module" label="模块" width="120" />

        <el-table-column prop="issue_type" label="问题类型" width="100">
          <template #default="{ row }">
            <span class="issue-type">{{ row.issue_type || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="reproduce_frequency" label="重现频率" width="100">
          <template #default="{ row }">
            <span class="frequency-text">{{ row.reproduce_frequency || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="tags" label="标签" width="150">
          <template #default="{ row }">
            <div v-if="row.tags" class="tags-container">
              <el-tag
                v-for="tag in getTagsArray(row.tags)"
                :key="tag"
                size="small"
                class="tag-item"
              >
                {{ tag }}
              </el-tag>
            </div>
            <span v-else class="no-tags">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="180" sortable="custom">
          <template #default="{ row }">
            <span class="date-text">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="updated_at" label="更新时间" width="180" sortable="custom">
          <template #default="{ row }">
            <span class="date-text">{{ formatDate(row.updated_at) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                type="primary"
                link
                size="small"
                @click="$router.push(`/projects/${projectId}/bugs/${row.id}`)"
                class="action-btn"
              >
                <el-icon><View /></el-icon>查看
              </el-button>
              <el-button
                type="primary"
                link
                size="small"
                @click="$router.push(`/projects/${projectId}/bugs/${row.id}/edit`)"
                class="action-btn"
              >
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-button
                type="success"
                link
                size="small"
                @click="handleQuickStatusChange(row, 'resolved')"
                v-if="row.status !== 'resolved' && row.status !== 'closed' && row.status !== 'verified'"
                class="action-btn"
              >
                <el-icon><Check /></el-icon>标记解决
              </el-button>
              <el-button
                type="danger"
                link
                size="small"
                @click="handleDelete(row)"
                class="action-btn"
              >
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Download,
  Upload,
  UploadFilled,
  Filter,
  Plus,
  Search,
  User,
  CircleCheck,
  Warning,
  Document,
  Edit,
  Flag,
  Delete,
  Close,
  View,
  Check,
  ArrowLeft
} from '@element-plus/icons-vue'
import { useBugStore } from '@/stores/bug'
import { useUserStore } from '@/stores/user'
import { apiService } from '@/services/api'

// 自定义 Bug 图标组件
const BugIcon = {
  render() {
    return h('svg', {
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '2',
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round',
      class: 'bug-icon'
    }, [
      h('path', { d: 'm8 2 1.88 1.88' }),
      h('path', { d: 'M14.12 3.88 16 2' }),
      h('path', { d: 'M9 7.13v-1a3.003 3.003 0 1 1 6 0v1' }),
      h('path', { d: 'M12 20c-3.3 0-6-2.7-6-6v-3a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v3c0 3.3-2.7 6-6 6' }),
      h('path', { d: 'M12 20v-9' }),
      h('path', { d: 'M6.53 9C4.6 8.8 3 7.1 3 5' }),
      h('path', { d: 'M6 13H2' }),
      h('path', { d: 'M3 21c0-2.1 1.7-3.9 3.8-4' }),
      h('path', { d: 'M20.97 5c0 2.1-1.6 3.8-3.5 4' }),
      h('path', { d: 'M22 13h-4' }),
      h('path', { d: 'M17.2 17c2.1.1 3.8 1.9 3.8 4' })
    ])
  }
}

const router = useRouter()
const route = useRoute()
const bugStore = useBugStore()
const userStore = useUserStore()

const projectId = computed(() => route.params.projectId ? parseInt(route.params.projectId) : null)
const projectName = ref('')

const loading = ref(false)
const bugs = ref([])
const stats = ref({
  assignedToMe: 0,
  unassigned: 0,
  openBugs: 0,
  totalBugs: 0
})

const filters = reactive({
  keyword: '',
  status: '',
  severity: '',
  priority: '',
  version: '',
  module: '',
  issue_type: '',
  reproduce_frequency: '',
  found_build: '',
  test_version: '',
  assignee: '',
  filter_type: ''
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

const sort = reactive({
  field: 'created_at',
  order: 'desc'
})

const showImportDialog = ref(false)
const uploadRef = ref(null)
const fileList = ref([])
const importLoading = ref(false)

const selectedBugs = ref([])
const showBatchStatusDialog = ref(false)
const showBatchPriorityDialog = ref(false)
const showBatchSeverityDialog = ref(false)
const batchLoading = ref(false)
const batchUpdateData = reactive({
  status: '',
  priority: '',
  severity: ''
})

const availableVersions = computed(() => {
  const versions = new Set()
  bugs.value.forEach(bug => {
    if (bug.version) versions.add(bug.version)
  })
  return Array.from(versions).sort()
})

const availableModules = computed(() => {
  const modules = new Set()
  bugs.value.forEach(bug => {
    if (bug.module) modules.add(bug.module)
  })
  return Array.from(modules).sort()
})

const handleSelectionChange = (selection) => {
  selectedBugs.value = selection
}

const handleBatchStatusUpdate = async () => {
  if (!batchUpdateData.status) {
    ElMessage.warning('请选择状态')
    return
  }
  if (selectedBugs.value.length === 0) {
    ElMessage.warning('请先选择要更新的缺陷')
    return
  }
  batchLoading.value = true
  try {
    const bugIds = selectedBugs.value.map(b => b.id)
    await apiService.bugs.batchUpdate(bugIds, { status: batchUpdateData.status })
    ElMessage.success('批量更新状态成功')
    showBatchStatusDialog.value = false
    batchUpdateData.status = ''
    selectedBugs.value = []
    await fetchBugs()
  } catch (error) {
    console.error('批量更新状态失败:', error)
    const errorMsg = error?.response?.data?.error || error?.message || '批量更新失败'
    ElMessage.error(errorMsg)
  } finally {
    batchLoading.value = false
    fetchBugStats()
  }
}

const handleBatchPriorityUpdate = async () => {
  if (!batchUpdateData.priority) {
    ElMessage.warning('请选择优先级')
    return
  }
  if (selectedBugs.value.length === 0) {
    ElMessage.warning('请先选择要更新的缺陷')
    return
  }
  batchLoading.value = true
  try {
    const bugIds = selectedBugs.value.map(b => b.id)
    await apiService.bugs.batchUpdate(bugIds, { priority: batchUpdateData.priority })
    ElMessage.success('批量更新优先级成功')
    showBatchPriorityDialog.value = false
    batchUpdateData.priority = ''
    selectedBugs.value = []
    await fetchBugs()
  } catch (error) {
    console.error('批量更新优先级失败:', error)
    const errorMsg = error?.response?.data?.error || error?.message || '批量更新失败'
    ElMessage.error(errorMsg)
  } finally {
    batchLoading.value = false
    fetchBugStats()
  }
}

const handleBatchSeverityUpdate = async () => {
  if (!batchUpdateData.severity) {
    ElMessage.warning('请选择严重程度')
    return
  }
  if (selectedBugs.value.length === 0) {
    ElMessage.warning('请先选择要更新的缺陷')
    return
  }
  batchLoading.value = true
  try {
    const bugIds = selectedBugs.value.map(b => b.id)
    await apiService.bugs.batchUpdate(bugIds, { severity: batchUpdateData.severity })
    ElMessage.success('批量更新严重程度成功')
    showBatchSeverityDialog.value = false
    batchUpdateData.severity = ''
    selectedBugs.value = []
    await fetchBugs()
  } catch (error) {
    console.error('批量更新严重程度失败:', error)
    const errorMsg = error?.response?.data?.error || error?.message || '批量更新失败'
    ElMessage.error(errorMsg)
  } finally {
    batchLoading.value = false
    fetchBugStats()
  }
}

const handleBatchDelete = async () => {
  if (selectedBugs.value.length === 0) {
    ElMessage.warning('请先选择要删除的缺陷')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedBugs.value.length} 个缺陷吗？此操作不可恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    batchLoading.value = true
    const bugIds = selectedBugs.value.map(b => b.id)
    await apiService.bugs.batchDelete(bugIds)
    ElMessage.success('批量删除成功')
    selectedBugs.value = []
    await fetchBugs()
  } catch (error) {
    console.error('批量删除失败:', error)
    if (error !== 'cancel') {
      const errorMsg = error?.response?.data?.error || error?.message || '批量删除失败'
      ElMessage.error(errorMsg)
    }
  } finally {
    batchLoading.value = false
    await fetchBugStats()
  }
}
const selectedFile = ref(null)

const getCurrentUserRole = () => {
  return userStore.currentUser?.role || null
}

const isTester = () => {
  const role = getCurrentUserRole()
  return role === 'test_engineer'
}

const isDeveloperOrManager = () => {
  const role = getCurrentUserRole()
  return role === 'software_engineer' || role === 'manager' || role === 'project_manager'
}

const fetchBugStats = async () => {
  try {
    const params = { per_page: 1 }

    if (projectId.value) {
      params.project_id = projectId.value
    }

    const currentUserId = getCurrentUserId()
    const tester = isTester()

    const response = await apiService.bugs.getList({
      ...params,
      filter_type: 'all_open'
    })

    const allResponse = await apiService.bugs.getList({
      ...params,
      per_page: 1
    })

    let totalCount = 0
    if (allResponse && typeof allResponse === 'object') {
      totalCount = allResponse.total || 0
    }

    let openCount = 0
    let unassignedCount = 0
    let assignedToMeCount = 0

    if (response && response.bugs) {
      openCount = response.total || response.bugs.length

      const unassignedResponse = await apiService.bugs.getList({
        ...params,
        per_page: 1,
        filter_type: 'to_claim'
      })

      if (unassignedResponse && typeof unassignedResponse === 'object') {
        unassignedCount = unassignedResponse.total || 0
      }

      if (currentUserId) {
        const myHandlingResponse = await apiService.bugs.getList({
          ...params,
          per_page: 1,
          filter_type: 'my_handling'
        })

        if (myHandlingResponse && typeof myHandlingResponse === 'object') {
          assignedToMeCount = myHandlingResponse.total || 0
        }
      }
    }

    stats.value = {
      totalBugs: totalCount,
      openBugs: openCount,
      unassigned: unassignedCount,
      assignedToMe: assignedToMeCount
    }
  } catch (error) {
    console.error('获取缺陷统计信息失败:', error)
    try {
      const fallbackResponse = await apiService.bugs.getList({ per_page: 1000, project_id: projectId.value })
      if (fallbackResponse && fallbackResponse.bugs) {
        const allBugs = fallbackResponse.bugs
        const currentUserId = getCurrentUserId()
        const testerRole = isTester()

        stats.value.totalBugs = allBugs.length
        stats.value.openBugs = allBugs.filter(bug =>
          bug.status !== 'closed' && bug.status !== 'resolved' && bug.status !== 'verified'
        ).length
        stats.value.unassigned = allBugs.filter(bug =>
          !bug.resolved_by && !bug.verifier_id
        ).length

        if (testerRole) {
          stats.value.assignedToMe = allBugs.filter(bug =>
            bug.reported_by === currentUserId && !bug.resolved_by
          ).length
        } else {
          stats.value.assignedToMe = allBugs.filter(bug =>
            bug.resolved_by === currentUserId
          ).length
        }
      }
    } catch (fallbackError) {
      console.error('获取缺陷统计信息备用方案失败:', fallbackError)
    }
  }
}

const filterByStat = (statType) => {
  filters.status = ''
  filters.severity = ''
  filters.priority = ''
  filters.keyword = ''
  filters.version = ''
  filters.module = ''
  filters.issue_type = ''
  filters.assignee = ''
  filters.assigned_to_me = false
  filters.filter_type = ''

  switch (statType) {
    case 'openBugs':
      filters.status = 'new,assigned,in_progress,fixed,reopened'
      break
    case 'assignedToMe':
      filters.filter_type = 'my_handling'
      break
    case 'unassigned':
      filters.filter_type = 'to_claim'
      break
    case 'all':
      break
  }

  pagination.currentPage = 1
  fetchBugs()
}

const fetchBugs = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      per_page: pagination.pageSize,
      sort: sort.field,
      order: sort.order
    }

    if (filters.keyword) params.search = filters.keyword
    if (filters.status) params.status = filters.status
    if (filters.severity) params.severity = filters.severity
    if (filters.priority) params.priority = filters.priority
    if (filters.assignee) params.assignee = filters.assignee
    if (filters.assigned_to_me) params.assigned_to_me = filters.assigned_to_me
    if (filters.version) params.version = filters.version
    if (filters.module) params.module = filters.module
    if (filters.issue_type) params.issue_type = filters.issue_type
    if (filters.reproduce_frequency) params.reproduce_frequency = filters.reproduce_frequency
    if (filters.found_build) params.found_build = filters.found_build
    if (filters.test_version) params.test_version = filters.test_version
    if (filters.filter_type) params.filter_type = filters.filter_type

    if (projectId.value) {
      params.project_id = projectId.value
    }

    const response = await apiService.bugs.getList(params)

    if (typeof response === 'object' && response !== null) {
      if (Array.isArray(response.bugs)) {
        bugs.value = response.bugs
        pagination.total = response.total || response.bugs.length
      } else if (Array.isArray(response)) {
        bugs.value = response
        pagination.total = response.length
      } else {
        bugs.value = []
        pagination.total = 0
      }
    } else {
      bugs.value = []
      pagination.total = 0
    }
  } catch (error) {
    console.error('获取Bug列表失败:', error)
    ElMessage.error('获取Bug列表失败: ' + (error.message || '未知错误'))
    bugs.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

const loadProjectInfo = async () => {
  if (!projectId.value) return
  try {
    const response = await apiService.projects.getById(projectId.value)
    const projectData = response.project || response || {}
    projectName.value = projectData.name || '项目'
  } catch (error) {
    console.error('获取项目信息失败:', error)
    projectName.value = '项目'
  }
}

const handleFilter = () => {
  pagination.currentPage = 1
  fetchBugs()
}

const resetFilter = () => {
  Object.keys(filters).forEach(key => {
    filters[key] = ''
  })
  filters.filter_type = ''
  pagination.currentPage = 1
  fetchBugs()
}

const handleSortChange = ({ prop, order }) => {
  if (prop) {
    sort.field = prop
    sort.order = order === 'ascending' ? 'asc' : 'desc'
    fetchBugs()
  }
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  fetchBugs()
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
  fetchBugs()
}

const handleDelete = async (bug) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除Bug "${bug.title}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await bugStore.deleteBug(bug.id)
    ElMessage.success('Bug删除成功')
    fetchBugs()
    fetchBugStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除Bug失败:', error)
      ElMessage.error('删除Bug失败')
    }
  }
}

const handleQuickStatusChange = async (bug, newStatus) => {
  try {
    const statusTextMap = {
      'resolved': '已解决',
      'closed': '已关闭',
      'verified': '已验证'
    }

    const statusText = statusTextMap[newStatus] || newStatus

    await ElMessageBox.confirm(
      `确定要将Bug "${bug.title}" 标记为${statusText}吗？`,
      '确认状态更改',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const updateData = { status: newStatus }

    if (newStatus === 'resolved') {
      updateData.resolved_at = new Date().toISOString()
    } else if (newStatus === 'closed') {
      updateData.closed_at = new Date().toISOString()
    }

    await bugStore.updateBug(bug.id, updateData)
    ElMessage.success(`Bug状态已更新为${statusText}`)
    fetchBugs()
    fetchBugStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('状态更改失败:', error)
      ElMessage.error('状态更改失败')
    }
  }
}

const getStatusType = (status) => {
  const typeMap = {
    'new': 'info',
    'assigned': 'warning',
    'in_progress': 'warning',
    'fixed': 'success',
    'resolved': 'success',
    'verified': 'success',
    'closed': 'info',
    'reopened': 'warning',
    'rejected': 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'new': '新建',
    'assigned': '已分配',
    'in_progress': '进行中',
    'fixed': '已修复',
    'resolved': '已解决',
    'verified': '已验证',
    'closed': '已关闭',
    'reopened': '重新打开',
    'rejected': '已拒绝'
  }
  return textMap[status] || status
}

const getSeverityType = (severity) => {
  const typeMap = {
    'low': 'success',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger',
    'Low': 'success',
    'Medium': 'warning',
    'High': 'danger',
    'Critical': 'danger'
  }
  return typeMap[severity] || 'info'
}

const getSeverityText = (severity) => {
  const textMap = {
    'low': '低',
    'medium': '中',
    'high': '高',
    'critical': '严重',
    'Low': '低',
    'Medium': '中',
    'High': '高',
    'Critical': '严重'
  }
  return textMap[severity] || severity
}

const getPriorityType = (priority) => {
  const typeMap = {
    'low': 'info',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger'
  }
  return typeMap[priority] || 'info'
}

const getPriorityText = (priority) => {
  const textMap = {
    'low': '低',
    'medium': '中',
    'high': '高',
    'critical': '紧急'
  }
  return textMap[priority] || priority
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const getTagsArray = (tagsString) => {
  if (!tagsString) return []
  return tagsString.split(',').filter(tag => tag.trim() !== '')
}

const getCurrentUserId = () => {
  return userStore.currentUser?.id || null
}

const handleExport = async () => {
  try {
    const exportParams = { ...filters }

    if (projectId.value) {
      exportParams.project_id = projectId.value
    }

    const response = await apiService.bugs.export(exportParams)

    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `缺陷报告_${new Date().toISOString().slice(0, 10)}.xlsx`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)

    ElMessage.success('缺陷导出成功')
  } catch (error) {
    console.error('导出缺陷失败:', error)
    ElMessage.error('导出缺陷失败')
  }
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
  fileList.value = [file]
}

const beforeUpload = (file) => {
  const allowedTypes = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel', 'text/csv']
  const allowedExtensions = ['.xlsx', '.xls', '.csv']
  const maxSize = 10 * 1024 * 1024

  if (!allowedTypes.includes(file.type) && !allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext))) {
    ElMessage.error('只支持上传 .xlsx, .xls, .csv 格式文件')
    return false
  }

  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }

  return true
}

const handleImport = async () => {
  if (!selectedFile.value) {
    ElMessage.error('请选择要导入的文件')
    return
  }

  try {
    importLoading.value = true

    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('project_id', projectId.value)

    const response = await apiService.bugs.import(formData)

    if (response.errors && response.errors.length > 0) {
      ElMessage.warning(`成功导入 ${response.imported_count || 0} 个缺陷，有 ${response.errors.length} 个缺陷导入失败`)
      console.error('导入失败详情:', response.errors)
    } else {
      ElMessage.success(`成功导入 ${response.imported_count || 0} 个缺陷`)
    }

    showImportDialog.value = false
    fileList.value = []
    selectedFile.value = null

    fetchBugs()
    fetchBugStats()
  } catch (error) {
    console.error('导入缺陷失败:', error)
    ElMessage.error('导入缺陷失败')
  } finally {
    importLoading.value = false
  }
}

onMounted(() => {
  loadProjectInfo()
  fetchBugs()
  fetchBugStats()
})
</script>

<style scoped>
.bug-list {
  padding: 0;
}

/* 页面头部样式 */
.page-header {
  position: relative;
  margin-bottom: 24px;
  padding: 24px;
  background: linear-gradient(135deg, var(--danger-500) 0%, var(--warning-600) 100%);
  border-radius: var(--radius-lg);
  overflow: hidden;
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
  opacity: 0.4;
}

.orb-1 {
  width: 200px;
  height: 200px;
  background: var(--accent-400);
  top: -50px;
  right: 10%;
  animation: float 6s ease-in-out infinite;
}

.orb-2 {
  width: 150px;
  height: 150px;
  background: var(--success-400);
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
  gap: 16px;
}

.title-icon-wrapper {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.title-icon {
  font-size: 28px;
  color: white;
}

.title-text h1 {
  margin: 0;
  color: white;
  font-size: 28px;
  font-weight: 700;
}

.subtitle {
  margin: 4px 0 0 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-back {
  color: white;
  border-color: rgba(255, 255, 255, 0.3);
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}

.btn-success-gradient {
  background: linear-gradient(135deg, var(--success-500) 0%, var(--success-600) 100%);
  border: none;
  color: white;
}

.btn-success-gradient:hover {
  background: linear-gradient(135deg, var(--success-600) 0%, var(--success-700) 100%);
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-success);
}

.btn-warning-gradient {
  background: linear-gradient(135deg, var(--warning-500) 0%, var(--warning-600) 100%);
  border: none;
  color: white;
}

.btn-warning-gradient:hover {
  background: linear-gradient(135deg, var(--warning-600) 0%, var(--warning-700) 100%);
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-warning);
}

/* 统计卡片区域 */
.bug-stats {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  background: var(--bg-elevated);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--gradient-primary);
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-card-primary {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  color: white;
}

.stat-card-warning {
  background: linear-gradient(135deg, var(--warning-500) 0%, var(--warning-600) 100%);
  color: white;
}

.stat-card-info {
  background: linear-gradient(135deg, var(--secondary-500) 0%, var(--secondary-600) 100%);
  color: white;
}

.stat-card-secondary {
  background: linear-gradient(135deg, var(--neutral-500) 0%, var(--neutral-600) 100%);
  color: white;
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: all var(--transition-normal);
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.stat-card:hover .stat-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
  color: white;
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  margin-top: 4px;
}

/* 玻璃拟态卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.glass-card-warning {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 191, 36, 0.1) 100%);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

/* 筛选卡片 */
.filter-card {
  margin-bottom: 24px;
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
  color: var(--text-primary);
}

.filter-actions {
  display: flex;
  gap: 8px;
}

/* 批量操作工具栏 */
.batch-toolbar {
  margin-bottom: 16px;
}

.batch-toolbar-content {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.selected-count {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: var(--warning-600);
  padding: 6px 12px;
  background: rgba(245, 158, 11, 0.1);
  border-radius: var(--radius-md);
}

.batch-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.batch-btn {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 表格卡片 */
.bug-table-card {
  margin-bottom: 24px;
}

.custom-table {
  --el-table-header-bg-color: var(--neutral-50);
  --el-table-row-hover-bg-color: var(--primary-50);
}

:deep(.el-table th) {
  font-weight: 600;
  color: var(--text-primary);
  background: var(--neutral-50);
}

.bug-title-link {
  color: var(--primary-500);
  text-decoration: none;
  font-weight: 500;
  transition: color var(--transition-fast);
}

.bug-title-link:hover {
  color: var(--primary-600);
  text-decoration: underline;
}

.status-tag,
.severity-tag,
.priority-tag {
  border-radius: var(--radius-sm);
}

.issue-type,
.frequency-text {
  color: var(--text-secondary);
  font-size: 13px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag-item {
  border-radius: var(--radius-sm);
}

.no-tags {
  color: var(--text-tertiary);
}

.date-text {
  color: var(--text-secondary);
  font-size: 13px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

/* 上传区域 */
.upload-area {
  border-radius: var(--radius-lg);
}

.upload-icon {
  font-size: 48px;
  color: var(--primary-400);
}

/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 动画 */
.animate-fade-in-down {
  animation: fadeInDown 0.6s ease-out;
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s ease-out;
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

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-15px);
  }
}

/* 响应式适配 */
@media (max-width: 768px) {
  .page-header {
    padding: 16px;
  }

  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .title-text h1 {
    font-size: 20px;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .bug-stats .el-col {
    margin-bottom: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-value {
    font-size: 22px;
  }

  .batch-toolbar-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .batch-actions {
    width: 100%;
  }

  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }
}

@media screen and (max-width: 480px) {
  .title-icon-wrapper {
    width: 44px;
    height: 44px;
  }

  .title-icon {
    font-size: 22px;
  }

  .title-text h1 {
    font-size: 18px;
  }

  .subtitle {
    font-size: 12px;
  }

  .stat-icon-wrapper {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-label {
    font-size: 12px;
  }
}
</style>
