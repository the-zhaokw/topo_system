<template>
  <div class="requirement-doc-list" v-loading="loading">
    <div class="page-header">
      <div class="header-left">
        <h2>需求管理</h2>
        <span class="subtitle">管理项目需求文档和条目</span>
      </div>
      <div class="header-right">
        <el-button @click="goToDashboard">
          <el-icon><DataAnalysis /></el-icon>
          仪表盘
        </el-button>
        <el-button type="primary" @click="showCreateDialog = true" v-if="canCreate">
          <el-icon><Plus /></el-icon>
          新建需求文档
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="statistics-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ statistics.totalDocuments || 0 }}</div>
          <div class="stat-label">需求文档</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ statistics.totalItems || 0 }}</div>
          <div class="stat-label">需求条目</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ statistics.approvedItems || 0 }}</div>
          <div class="stat-label">已批准</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ statistics.completedItems || 0 }}</div>
          <div class="stat-label">已完成</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="评审中" value="reviewing" />
            <el-option label="已批准" value="approved" />
            <el-option label="已废弃" value="deprecated" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filterForm.docType" placeholder="全部类型" clearable>
            <el-option label="功能需求" value="functional" />
            <el-option label="非功能需求" value="non_functional" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="搜索文档名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button @click="handleFilter">筛选</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 文档列表 -->
    <el-card class="list-card">
      <el-empty v-if="documents.length === 0" description="暂无需求文档" />
      
      <div v-else class="document-list">
        <div
          v-for="doc in documents"
          :key="doc.id"
          class="document-item"
          @click="goToDetail(doc.id)"
        >
          <div class="doc-header">
            <div class="doc-title">
              <el-icon class="doc-icon"><Document /></el-icon>
              <span class="title-text">{{ doc.name }}</span>
              <el-tag :type="getStatusType(doc.status)" size="small">
                {{ getStatusText(doc.status) }}
              </el-tag>
              <el-tag type="info" size="small" v-if="doc.doc_type === 'functional'">功能需求</el-tag>
              <el-tag type="warning" size="small" v-else>非功能需求</el-tag>
            </div>
            <div class="doc-version">v{{ doc.version }}</div>
          </div>
          
          <div class="doc-description" v-if="doc.description">
            {{ doc.description }}
          </div>
          
          <div class="doc-meta">
            <span class="meta-item">
              <el-icon><User /></el-icon>
              {{ doc.creator_name }}
            </span>
            <span class="meta-item">
              <el-icon><Files /></el-icon>
              {{ doc.item_count || 0 }} 个需求条目
            </span>
            <span class="meta-item">
              <el-icon><Clock /></el-icon>
              {{ formatDate(doc.updated_at) }}
            </span>
          </div>
          
          <div class="doc-actions" @click.stop>
            <el-button type="primary" link size="small" @click="goToDetail(doc.id)">
              查看详情
            </el-button>
            <el-button 
              type="danger" 
              link 
              size="small" 
              @click="handleDelete(doc)"
              v-if="canDelete(doc)"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 创建文档对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建需求文档" width="600px">
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="文档名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入文档名称" />
        </el-form-item>
        <el-form-item label="文档类型" prop="docType">
          <el-radio-group v-model="createForm.docType">
            <el-radio label="functional">功能需求</el-radio>
            <el-radio label="non_functional">非功能需求</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="负责人" prop="ownerId">
          <UserSelector 
            v-model="createForm.ownerId" 
            :projectId="projectId" 
            :multiple="false" 
            placeholder="请选择负责人"
            :clearable="true"
          />
        </el-form-item>
        <el-form-item label="文档描述" prop="description">
          <el-input 
            v-model="createForm.description" 
            type="textarea" 
            :rows="4"
            placeholder="请输入文档描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Document, User, Files, Clock, DataAnalysis } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import api from '@/services/api'
import UserSelector from '@/components/common/UserSelector.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const documents = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const statistics = ref({})

const filterForm = ref({
  status: '',
  docType: '',
  keyword: ''
})

const showCreateDialog = ref(false)
const creating = ref(false)
const createFormRef = ref(null)
const createForm = ref({
  name: '',
  docType: 'functional',
  ownerId: null,
  description: ''
})

const createRules = {
  name: [
    { required: true, message: '请输入文档名称', trigger: 'blur' },
    { min: 2, max: 200, message: '长度在 2 到 200 个字符', trigger: 'blur' }
  ]
}

const projectId = computed(() => route.params.projectId)

const canCreate = computed(() => {
  const user = userStore.currentUser
  if (!user) return false
  if (user.is_super_admin) return true
  const position = user.position
  return position === '管理员' ||
         position?.includes('经理') ||
         position === '项目经理' ||
         position === '测试工程师' ||
         position === '软件工程师'
})

const canDelete = (doc) => {
  const user = userStore.currentUser
  if (!user) return false
  if (user.is_super_admin) return true
  const position = user.position
  return position === '管理员' ||
         position?.includes('经理') ||
         position === '项目经理' ||
         doc.created_by === user.id
}

const fetchDocuments = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...filterForm.value
    }
    
    const response = await api.get(`/projects/${projectId.value}/requirement-documents`, { params })
    if (response.success) {
      documents.value = response.documents || []
      total.value = response.total || documents.value.length
    }
  } catch (error) {
    console.error('获取需求文档列表失败:', error)
    ElMessage.error('获取需求文档列表失败')
  } finally {
    loading.value = false
  }
}

const fetchStatistics = async () => {
  try {
    const response = await api.get(`/projects/${projectId.value}/requirement-statistics`)
    if (response.success) {
      const stats = response.statistics
      statistics.value = {
        totalDocuments: Object.values(stats.document_status || {}).reduce((a, b) => a + b, 0),
        totalItems: Object.values(stats.item_status || {}).reduce((a, b) => a + b, 0),
        approvedItems: stats.item_status?.approved || 0,
        completedItems: (stats.item_status?.completed || 0) + (stats.item_status?.verified || 0)
      }
    }
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

const handleFilter = () => {
  currentPage.value = 1
  fetchDocuments()
}

const resetFilter = () => {
  filterForm.value = {
    status: '',
    docType: '',
    keyword: ''
  }
  handleFilter()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchDocuments()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchDocuments()
}

const handleCreate = async () => {
  if (!createFormRef.value) return
  
  try {
    await createFormRef.value.validate()
    creating.value = true
    
    const data = {
      name: createForm.value.name,
      doc_type: createForm.value.docType,
      owner_id: createForm.value.ownerId,
      description: createForm.value.description
    }
    
    const response = await api.post(`/projects/${projectId.value}/requirement-documents`, data)
    if (response.success) {
      ElMessage.success('需求文档创建成功')
      showCreateDialog.value = false
      createForm.value = { name: '', docType: 'functional', ownerId: null, description: '' }
      fetchDocuments()
      fetchStatistics()
    }
  } catch (error) {
    console.error('创建需求文档失败:', error)
    ElMessage.error(error.response?.data?.error || '创建失败')
  } finally {
    creating.value = false
  }
}

const handleDelete = async (doc) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除需求文档 "${doc.name}" 吗？此操作将同时删除文档下的所有需求条目。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await api.delete(`/requirement-documents/${doc.id}`)
    if (response.success) {
      ElMessage.success('删除成功')
      fetchDocuments()
      fetchStatistics()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.error || '删除失败')
    }
  }
}

const goToDetail = (docId) => {
  if (projectId.value) {
    router.push(`/projects/${projectId.value}/requirements/${docId}`)
  } else {
    router.push(`/requirements/${docId}`)
  }
}

const goToDashboard = () => {
  if (projectId.value) {
    router.push(`/projects/${projectId.value}/requirements/dashboard`)
  }
}

const getStatusType = (status) => {
  const typeMap = {
    'draft': 'info',
    'reviewing': 'warning',
    'approved': 'success',
    'deprecated': 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'draft': '草稿',
    'reviewing': '评审中',
    'approved': '已批准',
    'deprecated': '已废弃'
  }
  return textMap[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchDocuments()
  fetchStatistics()
})
</script>

<style scoped>
.requirement-doc-list {
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

.list-card {
  min-height: 400px;
}

.document-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.document-item {
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #fff;
}

.document-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
}

.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.doc-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.doc-icon {
  font-size: 24px;
  color: #409eff;
}

.title-text {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.doc-version {
  font-size: 14px;
  color: #909399;
  background-color: #f5f7fa;
  padding: 4px 12px;
  border-radius: 12px;
}

.doc-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.doc-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 13px;
}

.doc-actions {
  display: flex;
  gap: 16px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .requirement-doc-list {
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

  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 16px;
  }

  .stat-card :deep(.el-card__body) {
    padding: 12px;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-label {
    font-size: 12px;
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

  .list-card {
    margin-bottom: 16px;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
  }

  .pagination-wrapper {
    justify-content: center;
    margin-top: 16px;
  }

  :deep(.el-pagination) {
    font-size: 11px;
    flex-wrap: wrap;
    gap: 4px;
  }

  :deep(.el-pagination__sizes),
  :deep(.el-pagination__jump) {
    display: none !important;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
    max-height: 90vh !important;
  }

  .el-dialog__header,
  .el-dialog__body,
  .el-dialog__footer {
    padding: 12px !important;
  }

  .el-dialog__title {
    font-size: 16px !important;
  }

  .doc-info {
    flex-direction: column;
    gap: 8px;
  }

  .doc-meta {
    flex-wrap: wrap;
    gap: 8px;
  }
}

@media screen and (max-width: 480px) {
  .requirement-doc-list {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .stats-cards {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .stat-value {
    font-size: 18px;
  }

  .el-table {
    font-size: 10px !important;
  }

  .doc-meta {
    font-size: 11px;
  }
}
</style>
