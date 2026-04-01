<template>
  <div class="bug-list">
    <div class="bug-list-header">
      <h2>缺陷报告</h2>
      <div class="header-actions">
        <el-button type="primary" @click="$router.push('/bugs/new')">
          <el-icon><Plus /></el-icon>
          新建Bug
        </el-button>
        <el-button type="success" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出缺陷
        </el-button>
        <el-button type="warning" @click="showImportDialog = true">
          <el-icon><Upload /></el-icon>
          导入缺陷
        </el-button>
      </div>
    </div>
    
    <!-- 项目过滤提示 -->
    <el-card v-if="projectId" class="project-filter-tip" shadow="never">
      <div class="project-filter-content">
        <el-icon><Filter /></el-icon>
        <span>当前仅显示项目 ID {{ projectId }} 下的缺陷</span>
        <el-button type="primary" link @click="clearProjectFilter">
          清除过滤
        </el-button>
      </div>
    </el-card>
    
    <!-- 导入缺陷对话框 -->
    <el-dialog v-model="showImportDialog" title="导入缺陷" width="500px">
      <el-upload
        ref="uploadRef"
        :action="''"
        :auto-upload="false"
        :file-list="fileList"
        :on-change="handleFileChange"
        :before-upload="beforeUpload"
        accept=".xlsx,.xls,.csv"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
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
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="handleImport" :loading="importLoading">
          导入
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 缺陷统计卡片 -->
    <el-row :gutter="16" class="bug-stats">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" @click="filterByStat('assignedToMe')" style="cursor: pointer;">
          <div class="stat-content">
            <div class="stat-number">{{ stats.assignedToMe || 0 }}</div>
            <div class="stat-label">待我处理的</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" @click="filterByStat('unassigned')" style="cursor: pointer;">
          <div class="stat-content">
            <div class="stat-number">{{ stats.unassigned || 0 }}</div>
            <div class="stat-label">待领取的</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" @click="filterByStat('openBugs')" style="cursor: pointer;">
          <div class="stat-content">
            <div class="stat-number">{{ stats.openBugs || 0 }}</div>
            <div class="stat-label">所有未关闭的</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" @click="filterByStat('all')" style="cursor: pointer;">
          <div class="stat-content">
            <div class="stat-number">{{ stats.totalBugs || 0 }}</div>
            <div class="stat-label">所有</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 筛选条件 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="filters" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="6">
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
          
          <el-col :span="4">
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
          
          <el-col :span="4">
            <el-form-item label="严重程度">
              <el-select v-model="filters.severity" placeholder="全部" clearable @change="handleFilter">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="严重" value="critical" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="4">
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
          
          <el-col :span="4">
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
          
          <el-col :span="4">
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

          <el-col :span="6">
            <el-form-item label-width="0">
              <el-button @click="resetFilter">重置</el-button>
              <el-button type="primary" @click="handleFilter">筛选</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>
    
    <!-- 批量操作工具栏 -->
    <el-card v-if="selectedBugs.length > 0" class="batch-toolbar" shadow="never">
      <div class="batch-toolbar-content">
        <span class="selected-count">已选择 {{ selectedBugs.length }} 项</span>
        <el-button type="primary" size="small" @click="showBatchStatusDialog = true">
          批量修改状态
        </el-button>
        <el-button type="warning" size="small" @click="showBatchPriorityDialog = true">
          批量修改优先级
        </el-button>
        <el-button type="info" size="small" @click="showBatchSeverityDialog = true">
          批量修改严重程度
        </el-button>
        <el-button type="danger" size="small" @click="handleBatchDelete">
          批量删除
        </el-button>
        <el-button size="small" @click="selectedBugs = []">
          取消选择
        </el-button>
      </div>
    </el-card>
    
    <!-- 批量修改状态对话框 -->
    <el-dialog v-model="showBatchStatusDialog" title="批量修改状态" width="400px">
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
        <el-button @click="showBatchStatusDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchStatusUpdate" :loading="batchLoading">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 批量修改优先级对话框 -->
    <el-dialog v-model="showBatchPriorityDialog" title="批量修改优先级" width="400px">
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
        <el-button @click="showBatchPriorityDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchPriorityUpdate" :loading="batchLoading">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 批量修改严重程度对话框 -->
    <el-dialog v-model="showBatchSeverityDialog" title="批量修改严重程度" width="400px">
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
        <el-button @click="showBatchSeverityDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchSeverityUpdate" :loading="batchLoading">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- Bug表格 -->
    <el-card shadow="never" style="position: relative;">
      <el-table 
        :data="bugs" 
        v-loading="loading"
        style="width: 100%"
        @sort-change="handleSortChange"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="id" label="ID" width="80" sortable="custom" />
        
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <router-link :to="`/bugs/${row.id}`" class="bug-title-link">
              {{ row.title }}
            </router-link>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)" size="small">
              {{ getSeverityText(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="project_name" label="项目" width="150" />
        
        <el-table-column prop="version" label="版本" width="100" />
        
        <el-table-column prop="module" label="模块" width="120" />
        
        <el-table-column prop="issue_type" label="问题类型" width="100" />
        
        <el-table-column prop="reproduce_frequency" label="重现频率" width="100" />
        
        <el-table-column prop="tags" label="标签" width="150">
          <template #default="{ row }">
            <div v-if="row.tags" class="tags-container">
              <el-tag 
                v-for="tag in getTagsArray(row.tags)" 
                :key="tag" 
                size="small" 
                type="info"
                style="margin-right: 4px; margin-bottom: 4px;"
              >
                {{ tag }}
              </el-tag>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180" sortable="custom">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="updated_at" label="更新时间" width="180" sortable="custom">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              link 
              size="small" 
              @click="$router.push(`/bugs/${row.id}`)"
            >
              查看
            </el-button>
            <el-button 
              type="primary" 
              link 
              size="small" 
              @click="$router.push(`/bugs/${row.id}/edit`)"
            >
              编辑
            </el-button>
            <el-button 
              type="success" 
              link 
              size="small" 
              @click="handleQuickStatusChange(row, 'resolved')"
              v-if="row.status !== 'resolved' && row.status !== 'closed' && row.status !== 'verified'"
            >
              标记解决
            </el-button>
            <el-button 
              type="danger" 
              link 
              size="small" 
              @click="handleDelete(row)"
            >
              删除
            </el-button>
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
import { ref, onMounted, reactive, computed, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Upload, UploadFilled, Filter } from '@element-plus/icons-vue'
import { useBugStore } from '@/stores/bug'
import { useUserStore } from '@/stores/user'
import { apiService, api as axios } from '@/services/api'

const router = useRouter()
const route = useRoute()
const bugStore = useBugStore()
const userStore = useUserStore()

const projectId = computed(() => route.query.project_id ? parseInt(route.query.project_id) : null)

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

// 导入导出相关变量
const showImportDialog = ref(false)
const uploadRef = ref(null)
const fileList = ref([])
const importLoading = ref(false)

// 批量操作相关变量
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

// 可用的筛选选项（从已有数据中提取）
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

// 处理选择变化
const handleSelectionChange = (selection) => {
  selectedBugs.value = selection
}

// 批量更新状态
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
    const response = await apiService.bugs.batchUpdate(bugIds, { status: batchUpdateData.status })
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

// 批量更新优先级
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
    const response = await apiService.bugs.batchUpdate(bugIds, { priority: batchUpdateData.priority })
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

// 批量更新严重程度
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
    const response = await apiService.bugs.batchUpdate(bugIds, { severity: batchUpdateData.severity })
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

// 批量删除
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
    const response = await apiService.bugs.batchDelete(bugIds)
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

// 获取当前用户职位
const getCurrentUserPosition = () => {
  return userStore.currentUser?.position || null
}

const isTester = () => {
  const position = getCurrentUserPosition()
  return position === '测试工程师'
}

const isDeveloperOrManager = () => {
  const position = getCurrentUserPosition()
  return position === '软件工程师' || position?.includes('经理') || position === '项目经理'
}

// 获取缺陷统计信息
const fetchBugStats = async () => {
  try {
    const params = {}
    
    if (projectId.value) {
      params.project_id = projectId.value
    }
    
    const currentUserId = getCurrentUserId()
    const testerRole = isTester()
    const devManagerRole = isDeveloperOrManager()
    
    const response = await apiService.bugs.getList({
      ...params,
      per_page: 1,
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
        const tester = isTester()
        
        stats.value.totalBugs = allBugs.length
        stats.value.openBugs = allBugs.filter(bug =>
          bug.status !== 'closed' && bug.status !== 'resolved' && bug.status !== 'verified'
        ).length
        stats.value.unassigned = allBugs.filter(bug => 
          !bug.resolved_by && !bug.verifier_id
        ).length
        
        if (tester) {
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

// 根据统计卡片筛选缺陷
const filterByStat = (statType) => {
  // 重置其他筛选条件
  filters.status = ''
  filters.severity = ''
  filters.priority = ''
  filters.keyword = ''
  filters.version = ''
  filters.module = ''
  filters.issue_type = ''
  filters.assignee = ''
  filters.assigned_to_me = false

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

  // 重置分页并获取列表
  pagination.currentPage = 1
  fetchBugs()
}

// 获取Bug列表
const fetchBugs = async () => {
    loading.value = true
    try {
      const params = {
        page: pagination.currentPage,
        per_page: pagination.pageSize,
        sort: sort.field,
        order: sort.order
      }
      
      // 添加筛选条件 - 注意：后端期望的参数名是search而不是keyword
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
      
      // 添加项目ID过滤
      if (projectId.value) {
        params.project_id = projectId.value
      }
      
      // 添加用户ID过滤（用于查看用户相关的bug）
      if (route.query.user_id) {
        params.user_id = route.query.user_id
      }
      
      console.log('Fetching bugs with params:', params)
      
      // 直接调用API，不通过store，以便调试
      const response = await apiService.bugs.getList(params)
      console.log('API response:', response)
      
      // 确保response是一个对象
      if (typeof response === 'object' && response !== null) {
        // 检查是否有bugs数组
        if (Array.isArray(response.bugs)) {
          bugs.value = response.bugs
          pagination.total = response.total || response.bugs.length
          console.log('Bugs loaded:', bugs.value.length, 'total:', pagination.total)
          console.log('Bugs data:', bugs.value)
        } else if (Array.isArray(response)) {
          // 如果response直接是一个数组，可能是API返回格式变化
          bugs.value = response
          pagination.total = response.length
          console.log('Bugs loaded (direct array):', bugs.value.length, 'total:', pagination.total)
          console.log('Bugs data:', bugs.value)
        } else {
          console.error('获取Bug列表失败: 无效的API响应格式', response)
          ElMessage.error('获取Bug列表失败: 无效的API响应格式')
          // 不使用模拟数据，保持数据真实
          bugs.value = []
          pagination.total = 0
        }
      } else {
        console.error('获取Bug列表失败: 无效的API响应', response)
        ElMessage.error('获取Bug列表失败: 无效的API响应')
        // 不使用模拟数据，保持数据真实
        bugs.value = []
        pagination.total = 0
      }
    } catch (error) {
      console.error('获取Bug列表失败:', error)
      console.error('Error details:', error.response || error.message || error)
      ElMessage.error('获取Bug列表失败: ' + (error.message || '未知错误'))
      // 不使用模拟数据，保持数据真实
      bugs.value = []
      pagination.total = 0
    } finally {
      loading.value = false
    }
  }

// 处理筛选
const handleFilter = () => {
  pagination.currentPage = 1
  fetchBugs()
}

// 重置筛选
const resetFilter = () => {
  Object.keys(filters).forEach(key => {
    filters[key] = ''
  })
  filters.filter_type = ''
  pagination.currentPage = 1
  fetchBugs()
}

// 清除项目过滤
const clearProjectFilter = () => {
  router.push('/bugs')
}

// 处理排序
const handleSortChange = ({ prop, order }) => {
  if (prop) {
    sort.field = prop
    sort.order = order === 'ascending' ? 'asc' : 'desc'
    fetchBugs()
  }
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  fetchBugs()
}

// 处理当前页变化
const handleCurrentChange = (page) => {
  pagination.currentPage = page
  fetchBugs()
}

// 删除Bug
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

// 快速状态更改
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
    
    // 更新Bug状态
    const updateData = {
      status: newStatus
    }
    
    // 如果是解决或关闭状态，设置相应的时间
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

// 状态类型映射
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

// 严重程度类型映射
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

// 优先级类型映射
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

// 格式化日期
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 处理标签字符串转换为数组
const getTagsArray = (tagsString) => {
  if (!tagsString) return []
  return tagsString.split(',').filter(tag => tag.trim() !== '')
}

// 获取当前用户ID
const getCurrentUserId = () => {
  return userStore.currentUser?.id || null
}

// 导出缺陷
const handleExport = async () => {
  try {
    // 构建导出参数，包含当前筛选条件
    const exportParams = {
      ...filters
    }
    
    // 添加项目ID过滤
    if (projectId.value) {
      exportParams.project_id = projectId.value
    }
    
    // 调用导出API
    const response = await apiService.bugs.export(exportParams)
    
    // 创建下载链接并触发下载
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

// 文件选择变化处理
const handleFileChange = (file) => {
  selectedFile.value = file.raw
  fileList.value = [file]
}

// 文件上传前验证
const beforeUpload = (file) => {
  const allowedTypes = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel', 'text/csv']
  const allowedExtensions = ['.xlsx', '.xls', '.csv']
  const maxSize = 10 * 1024 * 1024 // 10MB
  
  // 验证文件类型
  if (!allowedTypes.includes(file.type) && !allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext))) {
    ElMessage.error('只支持上传 .xlsx, .xls, .csv 格式文件')
    return false
  }
  
  // 验证文件大小
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  
  return true
}

// 导入缺陷
const handleImport = async () => {
  if (!selectedFile.value) {
    ElMessage.error('请选择要导入的文件')
    return
  }
  
  try {
    importLoading.value = true
    
    // 创建FormData对象
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    // 调用导入API
    const response = await apiService.bugs.import(formData)
    
    // 处理导入结果
    if (response.errors && response.errors.length > 0) {
      // 显示成功数量和错误信息
      ElMessage.warning(`成功导入 ${response.imported_count || 0} 个缺陷，有 ${response.errors.length} 个缺陷导入失败`)
      // 打印错误详情到控制台，方便调试
      console.error('导入失败详情:', response.errors)
    } else {
      // 全部成功
      ElMessage.success(`成功导入 ${response.imported_count || 0} 个缺陷`)
    }
    
    // 关闭对话框，清空文件列表
    showImportDialog.value = false
    fileList.value = []
    selectedFile.value = null
    
    // 重新加载缺陷列表和统计信息
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
  fetchBugs()
  fetchBugStats()
})
</script>

<style scoped>
.bug-list {
  padding: 0;
}

.bug-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.bug-list-header h2 {
  margin: 0;
  color: #303133;
}

.project-filter-tip {
  margin-bottom: 16px;
  background-color: #f0f9ff;
  border: 1px solid #409EFF;
}

.project-filter-content {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409EFF;
  font-weight: 500;
}

.bug-stats {
  margin-bottom: 24px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
}

.stat-content {
  text-align: center;
  padding: 16px 0;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.filter-card {
  margin-bottom: 24px;
  border: 1px solid #EBEEF5;
}

.bug-title-link {
  color: #409EFF;
  text-decoration: none;
}

.bug-title-link:hover {
  text-decoration: underline;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.bug-title-link {
  color: #409EFF;
  text-decoration: none;
  font-weight: 500;
}

.bug-title-link:hover {
  text-decoration: underline;
  color: #67c23a;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 8px;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
}

.stat-content {
  text-align: center;
  padding: 16px 0;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.filter-card {
  margin-bottom: 24px;
  border: 1px solid #EBEEF5;
  border-radius: 8px;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.bug-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 0 16px;
}

.bug-list-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

/* 批量操作工具栏样式 */
.batch-toolbar {
  margin-bottom: 16px;
  background-color: #f0f9ff;
  border: 1px solid #409EFF;
}

.batch-toolbar-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selected-count {
  font-weight: 600;
  color: #409EFF;
  margin-right: 8px;
}

@media screen and (max-width: 768px) {
  .bug-list {
    padding: 0;
  }

  .bug-list-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding: 0 8px;
    margin-bottom: 16px;
  }

  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    width: 100%;
  }

  .bug-list-header h2 {
    font-size: 18px;
  }

  .bug-list-header p {
    font-size: 12px;
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

  .project-filter-tip {
    margin-bottom: 12px;
  }

  .project-filter-content {
    flex-wrap: wrap;
    font-size: 12px;
  }

  .bug-stats {
    margin-bottom: 16px;
  }

  .bug-stats .el-row {
    flex-wrap: wrap;
    margin: 0 -6px;
  }

  .bug-stats .el-col {
    width: 50%;
    max-width: 50%;
    flex: 0 0 50%;
    margin-bottom: 8px;
    padding: 0 6px;
  }

  .stat-content {
    padding: 12px 0;
  }

  .stat-number {
    font-size: 24px;
  }

  .stat-label {
    font-size: 12px;
  }

  .filter-card {
    margin-bottom: 16px;
  }

  .filter-card .el-form {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .filter-card .el-row {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .filter-card .el-col {
    width: 100%;
    max-width: 100%;
    flex: 0 0 100%;
    padding: 0;
    margin-bottom: 8px;
  }

  .filter-card .el-form-item {
    margin-bottom: 0;
  }

  .filter-card .el-form-item__label {
    width: 80px !important;
    min-width: 80px !important;
    font-size: 12px;
  }

  .filter-card .el-input,
  .filter-card .el-select {
    width: 100% !important;
  }

  .filter-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: flex-start;
  }

  .filter-actions .el-button {
    flex: none;
    font-size: 12px;
    padding: 6px 12px;
  }

  .batch-toolbar {
    margin-bottom: 12px;
    padding: 10px;
  }

  .batch-toolbar-content {
    flex-wrap: wrap;
    gap: 8px;
  }

  .selected-count {
    width: 100%;
    margin-bottom: 8px;
    font-size: 12px;
  }

  .batch-toolbar-content .el-button {
    flex: 1;
    min-width: calc(50% - 4px);
    font-size: 11px;
    padding: 6px 8px;
  }

  .bug-table-container {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .el-table {
    font-size: 11px !important;
    min-width: 600px;
  }

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
  }

  .el-table__cell {
    font-size: 11px !important;
  }

  .cell {
    padding: 0 4px !important;
  }

  .pagination-container {
    margin-top: 16px;
    padding: 8px 0;
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

  .tags-container {
    flex-wrap: wrap;
    gap: 4px;
  }

  .tag-item {
    font-size: 10px;
    padding: 1px 4px;
    margin: 1px;
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

  .dialog-footer {
    flex-direction: column;
    gap: 8px;
  }

  .dialog-footer .el-button {
    width: 100%;
    margin: 0;
  }
}

@media screen and (max-width: 480px) {
  .bug-list-header {
    padding: 0 4px;
  }

  .bug-list-header h2 {
    font-size: 16px;
  }

  .header-actions .el-button {
    max-width: 100%;
    flex: none;
    width: 100%;
    font-size: 11px;
    padding: 6px 10px;
  }

  .bug-stats .el-col {
    width: 50%;
    padding: 0 4px;
  }

  .stat-number {
    font-size: 20px;
  }

  .stat-label {
    font-size: 11px;
  }

  .batch-toolbar-content .el-button {
    font-size: 10px;
    padding: 5px 6px;
  }

  .el-table {
    font-size: 10px !important;
    min-width: 500px;
  }

  .el-form-item {
    margin-bottom: 12px !important;
  }

  .el-input__inner,
  .el-textarea__inner {
    font-size: 14px !important;
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