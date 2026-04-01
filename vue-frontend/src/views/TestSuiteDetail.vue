<template>
  <div class="test-suite-detail">
    <div class="detail-header">
      <div class="header-left">
        <el-button @click="handleGoBack" style="margin-right: 16px;">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
        <div class="header-title">
          <h2>{{ suiteInfo.name }}</h2>
          <div class="header-tags">
            <el-tag v-if="suiteInfo.type === 'functional'" size="small">功能测试</el-tag>
            <el-tag v-else-if="suiteInfo.type === 'performance'" size="small" type="warning">性能测试</el-tag>
            <el-tag v-else-if="suiteInfo.type === 'security'" size="small" type="danger">安全测试</el-tag>
            <el-tag v-else size="small" type="info">其他</el-tag>
            <el-tag v-if="suiteInfo.status === 'designing'" size="small" type="info">设计中</el-tag>
            <el-tag v-else-if="suiteInfo.status === 'reviewed'" size="small" type="success">已评审</el-tag>
            <el-tag v-else-if="suiteInfo.status === 'deprecated'" size="small" type="danger">已废弃</el-tag>
            <el-tag v-if="suiteInfo.priority === 1" size="small" type="danger">高优先级</el-tag>
            <el-tag v-else-if="suiteInfo.priority === 2" size="small" type="warning">中优先级</el-tag>
            <el-tag v-else size="small" type="info">低优先级</el-tag>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <el-button @click="handleEdit">
          <el-icon><Edit /></el-icon>
          编辑
        </el-button>
        <el-button type="primary" @click="handleExecute">
          <el-icon><VideoPlay /></el-icon>
          执行测试
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：详细信息 -->
      <el-col :xs="24" :sm="24" :md="8" :lg="6">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>详细信息</span>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="负责人">{{ suiteInfo.owner_name || '未指定' }}</el-descriptions-item>
            <el-descriptions-item label="预计时长">{{ suiteInfo.expected_duration || 0 }} 分钟</el-descriptions-item>
            <el-descriptions-item label="用例数量">
              <el-tag type="primary">{{ suiteInfo.case_count || 0 }} 个</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="当前版本">v{{ suiteInfo.version || 1 }}</el-descriptions-item>
            <el-descriptions-item label="创建人">{{ suiteInfo.creator_name || '未知' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(suiteInfo.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ formatDate(suiteInfo.updated_at) }}</el-descriptions-item>
          </el-descriptions>
          <div v-if="suiteInfo.description" class="description-section">
            <div class="section-title">描述</div>
            <div class="description-content">{{ suiteInfo.description }}</div>
          </div>
        </el-card>

        <el-card class="stats-card">
          <template #header>
            <div class="card-header">
              <el-icon><TrendCharts /></el-icon>
              <span>用例统计</span>
            </div>
          </template>
          <div class="stats-list">
            <div class="stats-item">
              <span class="stats-label">用例总数</span>
              <span class="stats-value">{{ caseStats.total || 0 }}</span>
            </div>
            <div class="stats-item">
              <span class="stats-label">已批准</span>
              <span class="stats-value success">{{ caseStats.approved || 0 }}</span>
            </div>
            <div class="stats-item">
              <span class="stats-label">已评审</span>
              <span class="stats-value primary">{{ caseStats.reviewed || 0 }}</span>
            </div>
            <div class="stats-item">
              <span class="stats-label">设计中</span>
              <span class="stats-value info">{{ caseStats.designing || 0 }}</span>
            </div>
            <div class="stats-item">
              <span class="stats-label">自动化</span>
              <span class="stats-value warning">{{ caseStats.automated || 0 }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：用例列表 -->
      <el-col :xs="24" :sm="24" :md="16" :lg="18">
        <el-card class="cases-card">
          <template #header>
            <div class="card-header-with-actions">
              <div class="card-header">
                <el-icon><Document /></el-icon>
                <span>用例列表</span>
                <el-tag type="info" size="small" style="margin-left: 8px;">{{ filteredCases.length }}</el-tag>
              </div>
              <div class="header-actions">
                <el-input
                  v-model="caseFilter.keyword"
                  placeholder="搜索用例"
                  clearable
                  style="width: 200px; margin-right: 12px;"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-select v-model="caseFilter.priority" placeholder="优先级" clearable style="width: 120px; margin-right: 12px;">
                  <el-option label="P0" :value="0" />
                  <el-option label="P1" :value="1" />
                  <el-option label="P2" :value="2" />
                  <el-option label="P3" :value="3" />
                </el-select>
                <el-select v-model="caseFilter.status" placeholder="状态" clearable style="width: 120px; margin-right: 12px;">
                  <el-option label="设计中" value="designing" />
                  <el-option label="待评审" value="pending_review" />
                  <el-option label="已评审" value="reviewed" />
                  <el-option label="已批准" value="approved" />
                </el-select>
                <el-button type="primary" @click="handleAddCase">
                  <el-icon><Plus /></el-icon>
                  新建用例
                </el-button>
              </div>
            </div>
          </template>

          <el-table
            :data="filteredCases"
            style="width: 100%"
            v-loading="loading"
            @row-click="handleCaseClick"
            highlight-current-row
          >
            <el-table-column type="index" width="50" />
            <el-table-column label="标识" width="100" prop="identifier" />
            <el-table-column label="标题" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <div class="case-title-cell">
                  <span class="case-title">{{ row.title }}</span>
                  <el-tag v-if="row.is_automated" size="small" type="success" effect="plain">自动</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="优先级" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.priority === 0" size="small" type="danger">P0</el-tag>
                <el-tag v-else-if="row.priority === 1" size="small" type="warning">P1</el-tag>
                <el-tag v-else-if="row.priority === 2" size="small" type="info">P2</el-tag>
                <el-tag v-else size="small">P3</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag v-if="row.status === 'designing'" size="small" type="info">设计中</el-tag>
                <el-tag v-else-if="row.status === 'pending_review'" size="small" type="warning">待评审</el-tag>
                <el-tag v-else-if="row.status === 'reviewed'" size="small" type="success">已评审</el-tag>
                <el-tag v-else-if="row.status === 'approved'" size="small" type="success">已批准</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="设计者" width="100" prop="designer_name" />
            <el-table-column label="更新时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.updated_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click.stop="handleEditCase(row)">
                  编辑
                </el-button>
                <el-button type="primary" link size="small" @click.stop="handleViewCase(row)">
                  查看
                </el-button>
                <el-button type="danger" link size="small" @click.stop="handleDeleteCase(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="filteredCases.length === 0 && !loading" description="暂无测试用例" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 编辑测试集对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑测试集" width="600px">
      <el-form :model="editForm" label-width="100px" :rules="formRules" ref="editFormRef">
        <el-form-item label="测试集名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入测试集名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" placeholder="请输入测试集描述" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="editForm.type" placeholder="请选择类型" style="width: 100%;">
            <el-option label="功能测试" value="functional" />
            <el-option label="性能测试" value="performance" />
            <el-option label="安全测试" value="security" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" placeholder="请选择状态" style="width: 100%;">
            <el-option label="设计中" value="designing" />
            <el-option label="已评审" value="reviewed" />
            <el-option label="已废弃" value="deprecated" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="editForm.priority" placeholder="请选择优先级" style="width: 100%;">
            <el-option label="高" :value="1" />
            <el-option label="中" :value="2" />
            <el-option label="低" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <UserSelector 
            v-model="editForm.owner_id" 
            :projectId="projectId" 
            :multiple="false" 
            placeholder="请选择负责人"
            :clearable="true"
          />
        </el-form-item>
        <el-form-item label="预计时长">
          <el-input v-model.number="editForm.expected_duration" type="number" placeholder="分钟">
            <template #append>分钟</template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveEdit" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ArrowLeft, Edit, VideoPlay, InfoFilled, TrendCharts, 
  Document, Search, Plus 
} from '@element-plus/icons-vue'
import { apiService } from '@/services/api'
import UserSelector from '@/components/common/UserSelector.vue'

const router = useRouter()
const route = useRoute()

const projectId = computed(() => parseInt(route.params.projectId))
const suiteId = computed(() => parseInt(route.params.suiteId))

const loading = ref(false)
const suiteInfo = ref({})
const cases = ref([])
const showEditDialog = ref(false)
const saving = ref(false)
const editFormRef = ref(null)

const caseFilter = reactive({
  keyword: '',
  priority: null,
  status: ''
})

const editForm = reactive({
  name: '',
  description: '',
  type: 'functional',
  status: 'designing',
  priority: 2,
  owner_id: null,
  expected_duration: 0
})

const formRules = {
  name: [
    { required: true, message: '请输入测试集名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ]
}

const filteredCases = computed(() => {
  let result = [...cases.value]
  
  if (caseFilter.keyword) {
    const keyword = caseFilter.keyword.toLowerCase()
    result = result.filter(c => 
      c.title.toLowerCase().includes(keyword) ||
      c.identifier.toLowerCase().includes(keyword)
    )
  }
  
  if (caseFilter.priority !== null) {
    result = result.filter(c => c.priority === caseFilter.priority)
  }
  
  if (caseFilter.status) {
    result = result.filter(c => c.status === caseFilter.status)
  }
  
  return result
})

const caseStats = computed(() => {
  const stats = {
    total: cases.value.length,
    approved: 0,
    reviewed: 0,
    designing: 0,
    automated: 0
  }
  
  cases.value.forEach(c => {
    if (c.status === 'approved') stats.approved++
    else if (c.status === 'reviewed') stats.reviewed++
    else if (c.status === 'designing') stats.designing++
    
    if (c.is_automated) stats.automated++
  })
  
  return stats
})

const loadSuiteInfo = async () => {
  try {
    const response = await apiService.tests.getSuiteDetail(suiteId.value)
    suiteInfo.value = response || {}
  } catch (error) {
    console.error('加载测试集信息失败:', error)
    ElMessage.error('加载测试集信息失败')
  }
}

const loadCases = async () => {
  loading.value = true
  try {
    const response = await apiService.tests.getCasesBySuite(suiteId.value)
    cases.value = response || []
  } catch (error) {
    console.error('加载用例列表失败:', error)
    ElMessage.error('加载用例列表失败')
  } finally {
    loading.value = false
  }
}

const handleGoBack = () => {
  router.push(`/projects/${projectId.value}/tests/suites`)
}

const handleEdit = () => {
  Object.assign(editForm, {
    name: suiteInfo.value.name,
    description: suiteInfo.value.description,
    type: suiteInfo.value.type,
    status: suiteInfo.value.status,
    priority: suiteInfo.value.priority,
    owner_id: suiteInfo.value.owner_id,
    expected_duration: suiteInfo.value.expected_duration
  })
  showEditDialog.value = true
}

const handleSaveEdit = async () => {
  const valid = await editFormRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    await apiService.tests.updateSuite(suiteId.value, editForm)
    ElMessage.success('更新成功')
    showEditDialog.value = false
    await loadSuiteInfo()
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    saving.value = false
  }
}

const handleExecute = () => {
  router.push(`/projects/${projectId.value}/tests/executions?suite_id=${suiteId.value}`)
}

const handleAddCase = () => {
  router.push(`/projects/${projectId.value}/tests/suites/${suiteId.value}/cases/new`)
}

const handleCaseClick = (row) => {
  handleViewCase(row)
}

const handleViewCase = (row) => {
  router.push(`/projects/${projectId.value}/tests/suites/${suiteId.value}/cases/${row.id}`)
}

const handleEditCase = (row) => {
  router.push(`/projects/${projectId.value}/tests/suites/${suiteId.value}/cases/${row.id}/edit`)
}

const handleDeleteCase = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个用例吗？删除后不可恢复。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await apiService.tests.deleteCase(row.id)
    ElMessage.success('删除成功')
    await loadCases()
    await loadSuiteInfo()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
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

onMounted(async () => {
  await loadSuiteInfo()
  await loadCases()
})
</script>

<style scoped>
.test-suite-detail {
  padding: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-title h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
}

.header-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.card-header-with-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.description-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.section-title {
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
}

.description-content {
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.stats-card {
  margin-bottom: 20px;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stats-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stats-item:last-child {
  border-bottom: none;
}

.stats-label {
  color: #606266;
}

.stats-value {
  font-weight: 500;
  color: #409EFF;
}

.stats-value.success {
  color: #67C23A;
}

.stats-value.primary {
  color: #409EFF;
}

.stats-value.info {
  color: #909399;
}

.stats-value.warning {
  color: #E6A23C;
}

.cases-card {
  min-height: 500px;
}

.case-title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.case-title {
  font-weight: 500;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .test-suite-detail {
    padding: 12px;
  }

  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-title h2 {
    font-size: 18px;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .el-button {
    flex: 1;
  }

  .card-header-with-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .header-actions .el-input,
  .header-actions .el-select {
    width: 100% !important;
    margin-right: 0 !important;
    margin-bottom: 8px;
  }

  .el-table {
    font-size: 12px;
  }
}

@media screen and (max-width: 480px) {
  .test-suite-detail {
    padding: 8px;
  }

  .header-title h2 {
    font-size: 16px;
  }

  .el-table {
    font-size: 11px;
  }
}
</style>
