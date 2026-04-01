<template>
  <div class="test-case-list">
    <div class="case-header">
      <div class="header-left">
        <h2>测试用例</h2>
        <el-tag v-if="suiteInfo">{{ suiteInfo.name }}</el-tag>
      </div>
      <div class="header-actions">
        <el-button @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
          返回测试集
        </el-button>
        <el-button type="success" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出用例
        </el-button>
        <el-button type="warning" @click="showImportDialog = true">
          <el-icon><Upload /></el-icon>
          导入用例
        </el-button>
        <el-button type="primary" @click="handleCreateCase">
          <el-icon><Plus /></el-icon>
          新建用例
        </el-button>
      </div>
    </div>

    <el-card class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 120px;">
            <el-option label="设计" value="designing" />
            <el-option label="待评审" value="pending_review" />
            <el-option label="已评审" value="reviewed" />
            <el-option label="已批准" value="approved" />
            <el-option label="废弃" value="deprecated" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="filters.priority" placeholder="全部" clearable style="width: 100px;">
            <el-option label="P0" :value="0" />
            <el-option label="P1" :value="1" />
            <el-option label="P2" :value="2" />
            <el-option label="P3" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filters.type" placeholder="全部" clearable style="width: 100px;">
            <el-option label="功能" value="functional" />
            <el-option label="性能" value="performance" />
            <el-option label="安全" value="security" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="filters.search" placeholder="搜索标题或标识符" clearable style="width: 200px;" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">筛选</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <div class="batch-actions-bar" v-if="selectedCases.length > 0">
        <el-alert type="info" :closable="false">
          <template #title>
            已选择 {{ selectedCases.length }} 个用例
            <el-button type="primary" link size="small" @click="selectedCases = []">清空</el-button>
          </template>
        </el-alert>
        <div class="batch-buttons">
          <el-button size="small" @click="handleBatchMove">批量移动</el-button>
          <el-button size="small" @click="handleBatchCopy">批量复制</el-button>
          <el-button size="small" type="warning" @click="handleBatchChangeStatus">批量修改状态</el-button>
          <el-button size="small" type="danger" @click="handleBatchDelete">批量删除</el-button>
        </div>
      </div>

      <el-table
        :data="cases"
        stripe
        style="width: 100%"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        @row-dblclick="handleRowDoubleClick"
      >
        <el-table-column type="selection" width="45" />
        <el-table-column prop="identifier" label="标识符" width="120" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.priority === 0" type="danger" size="small">P0</el-tag>
            <el-tag v-else-if="row.priority === 1" type="warning" size="small">P1</el-tag>
            <el-tag v-else-if="row.priority === 2" size="small">P2</el-tag>
            <el-tag v-else type="info" size="small">P3</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.type === 'functional'" size="small">功能</el-tag>
            <el-tag v-else-if="row.type === 'performance'" type="success" size="small">性能</el-tag>
            <el-tag v-else-if="row.type === 'security'" type="warning" size="small">安全</el-tag>
            <el-tag v-else size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'designing'" type="info" size="small">设计</el-tag>
            <el-tag v-else-if="row.status === 'pending_review'" type="warning" size="small">待评审</el-tag>
            <el-tag v-else-if="row.status === 'reviewed'" type="success" size="small">已评审</el-tag>
            <el-tag v-else-if="row.status === 'approved'" type="success" size="small">已批准</el-tag>
            <el-tag v-else-if="row.status === 'deprecated'" type="danger" size="small">废弃</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_automated" label="自动化" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.is_automated" type="success" size="small">是</el-tag>
            <el-tag v-else type="info" size="small">否</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="step_count" label="步骤数" width="80" />
        <el-table-column prop="designer_name" label="设计人" width="100" />
        <el-table-column prop="updated_at" label="更新时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">查看</el-button>
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" link size="small" @click="handleQuickExecute(row)">执行</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="showCreateDialog" :title="editingCase ? '编辑测试用例' : '新建测试用例'" width="900px" @closed="resetCaseForm" :close-on-click-modal="false">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="basic">
          <el-form :model="caseForm" label-width="100px" :rules="caseRules" ref="caseFormRef">
            <el-form-item label="用例标题" prop="title">
              <el-input v-model="caseForm.title" placeholder="请输入用例标题" />
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="caseForm.description" type="textarea" :rows="3" placeholder="请输入用例描述" />
            </el-form-item>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="优先级">
                  <el-select v-model="caseForm.priority" placeholder="请选择">
                    <el-option label="P0 - 最高" :value="0" />
                    <el-option label="P1 - 高" :value="1" />
                    <el-option label="P2 - 中" :value="2" />
                    <el-option label="P3 - 低" :value="3" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="类型">
                  <el-select v-model="caseForm.type" placeholder="请选择">
                    <el-option label="功能测试" value="functional" />
                    <el-option label="性能测试" value="performance" />
                    <el-option label="安全测试" value="security" />
                    <el-option label="其他" value="other" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="设计人">
                  <UserSelector 
                    v-model="caseForm.designer_id" 
                    :projectId="suiteInfo?.project_id" 
                    :multiple="false" 
                    placeholder="请选择设计人"
                    style="width: 100%;"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="评审人">
                  <UserSelector 
                    v-model="caseForm.reviewer_id" 
                    :projectId="suiteInfo?.project_id" 
                    :multiple="false" 
                    placeholder="请选择评审人"
                    :clearable="true"
                    style="width: 100%;"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="前提条件">
              <el-input v-model="caseForm.precondition" type="textarea" :rows="2" placeholder="请输入前提条件" />
            </el-form-item>
            <el-form-item label="测试数据">
              <el-input v-model="caseForm.test_data" type="textarea" :rows="2" placeholder="请输入测试数据" />
            </el-form-item>
            <el-form-item label="环境要求">
              <el-input v-model="caseForm.environment" placeholder="请输入环境要求" />
            </el-form-item>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="可自动化">
                  <el-switch v-model="caseForm.is_automated" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="预计时长">
                  <el-input v-model.number="caseForm.estimated_duration" type="number" placeholder="分钟">
                    <template #append>分钟</template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="标签">
              <el-input v-model="caseForm.tags" placeholder="多个标签用逗号分隔" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="步骤设计" name="steps">
          <div class="steps-container">
            <el-alert type="info" :closable="false" style="margin-bottom: 16px;">
              共 {{ caseForm.steps.length }} 个步骤
            </el-alert>

            <el-table :data="caseForm.steps" border style="width: 100%;" row-key="index">
              <el-table-column prop="step_number" label="步骤" width="60" align="center">
                <template #default="{ $index }">
                  <span class="step-number">{{ $index + 1 }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作步骤" min-width="200">
                <template #default="{ row, $index }">
                  <el-input v-model="row.action" type="textarea" :rows="3" placeholder="请输入操作步骤" />
                </template>
              </el-table-column>
              <el-table-column label="预期结果" min-width="200">
                <template #default="{ row }">
                  <el-input v-model="row.expected_result" type="textarea" :rows="3" placeholder="请输入预期结果" />
                </template>
              </el-table-column>
              <el-table-column label="附件" width="80" align="center">
                <template #default="{ row, $index }">
                  <el-button size="small" @click="handleUploadStepAttachment($index)">
                    <el-icon><Upload /></el-icon>
                  </el-button>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="140" align="center">
                <template #default="{ $index }">
                  <el-button-group size="small">
                    <el-button @click="moveStepUp($index)" :disabled="$index === 0" title="上移">
                      <el-icon><Top /></el-icon>
                    </el-button>
                    <el-button @click="moveStepDown($index)" :disabled="$index === caseForm.steps.length - 1" title="下移">
                      <el-icon><Bottom /></el-icon>
                    </el-button>
                    <el-button @click="copyStep($index)" title="复制">
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                    <el-button @click="removeStep($index)" :disabled="caseForm.steps.length <= 1" type="danger" title="删除">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-button-group>
                </template>
              </el-table-column>
            </el-table>

            <div class="steps-actions">
              <el-button type="primary" plain @click="addStep">
                <el-icon><Plus /></el-icon>
                添加步骤
              </el-button>
              <el-button type="success" plain @click="addStepFromTemplate">
                <el-icon><Document /></el-icon>
                从模板添加
              </el-button>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="关联需求" name="requirements">
          <div class="requirements-container">
            <div class="link-header">
              <el-button type="primary" @click="showLinkRequirementDialog = true">
                <el-icon><Link /></el-icon>
                关联需求
              </el-button>
            </div>

            <el-table :data="linkedRequirements" stripe style="width: 100%;">
              <el-table-column prop="requirement_identifier" label="需求标识" width="120" />
              <el-table-column prop="requirement_title" label="需求标题" min-width="200" show-overflow-tooltip />
              <el-table-column prop="link_type" label="关联类型" width="100">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.link_type === 'tests' ? '测试' : row.link_type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <el-button type="danger" link size="small" @click="handleUnlinkRequirement(row.id)">解除</el-button>
                </template>
              </el-table-column>
            </el-table>

            <el-empty v-if="linkedRequirements.length === 0" description="暂无关联需求" />
          </div>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button @click="handleSaveAndNew">保存并新建</el-button>
        <el-button type="primary" @click="handleSaveCase" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showImportDialog" title="导入测试用例" width="500px">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :file-list="importFileList"
        :on-change="handleImportFileChange"
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

    <el-dialog v-model="showLinkRequirementDialog" title="关联需求" width="600px">
      <el-form :model="linkForm" label-width="100px">
        <el-form-item label="需求">
          <el-select
            v-model="linkForm.requirement_id"
            placeholder="搜索需求..."
            filterable
            remote
            :remote-method="searchRequirements"
            :loading="searchingRequirements"
            style="width: 100%;"
          >
            <el-option
              v-for="req in availableRequirements"
              :key="req.id"
              :label="`${req.identifier} - ${req.title}`"
              :value="req.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关联类型">
          <el-select v-model="linkForm.link_type" style="width: 100%;">
            <el-option label="测试" value="tests" />
            <el-option label=" blocked" value="blocked" />
            <el-option label="相关" value="related" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLinkRequirementDialog = false">取消</el-button>
        <el-button type="primary" @click="handleLinkRequirement" :loading="linking">关联</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showMoveDialog" title="移动用例" width="500px">
      <el-form :model="batchForm" label-width="100px">
        <el-form-item label="目标测试集">
          <el-select v-model="batchForm.target_suite_id" placeholder="请选择目标测试集" style="width: 100%;">
            <el-option v-for="suite in availableSuites" :key="suite.id" :label="suite.name" :value="suite.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMoveDialog = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmMove" :loading="batchOperating">确认移动</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showStatusDialog" title="修改用例状态" width="500px">
      <el-form :model="batchForm" label-width="100px">
        <el-form-item label="新状态">
          <el-select v-model="batchForm.new_status" placeholder="请选择新状态" style="width: 100%;">
            <el-option label="设计" value="designing" />
            <el-option label="待评审" value="pending_review" />
            <el-option label="已评审" value="reviewed" />
            <el-option label="已批准" value="approved" />
            <el-option label="废弃" value="deprecated" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showStatusDialog = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmStatusChange" :loading="batchOperating">确认修改</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showStepTemplateDialog" title="步骤模板" width="600px">
      <el-table :data="stepTemplates" stripe style="width: 100%;">
        <el-table-column prop="name" label="模板名称" min-width="120" />
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="applyStepTemplate(row)">应用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowLeft, Delete, Download, Upload, UploadFilled, Top, Bottom, CopyDocument, Link, Document } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'
import UserSelector from '@/components/common/UserSelector.vue'

const router = useRouter()
const route = useRoute()

const suiteId = ref(null)
const suiteInfo = ref(null)
const cases = ref([])
const loading = ref(false)
const showCreateDialog = ref(false)
const editingCase = ref(null)
const saving = ref(false)
const caseFormRef = ref(null)
const showImportDialog = ref(false)
const importFileList = ref([])
const importLoading = ref(false)
const uploadRef = ref(null)
const projectMembers = ref([])
const activeTab = ref('basic')
const linkedRequirements = ref([])

const selectedCases = ref([])
const showMoveDialog = ref(false)
const showStatusDialog = ref(false)
const showLinkRequirementDialog = ref(false)
const showStepTemplateDialog = ref(false)
const batchOperating = ref(false)
const linking = ref(false)
const searchingRequirements = ref(false)

const batchForm = reactive({
  target_suite_id: null,
  new_status: ''
})

const linkForm = reactive({
  requirement_id: null,
  link_type: 'tests'
})

const availableSuites = ref([])
const availableRequirements = ref([])

const stepTemplates = ref([
  { name: '登录测试', description: '标准登录流程步骤', steps: [{ action: '打开登录页面', expected_result: '登录页面正常显示' }, { action: '输入用户名密码', expected_result: '输入框正常显示输入内容' }, { action: '点击登录按钮', expected_result: '登录成功，跳转到首页' }] },
  { name: '搜索功能', description: '搜索框测试步骤', steps: [{ action: '在搜索框输入关键词', expected_result: '输入内容正常显示' }, { action: '点击搜索按钮', expected_result: '显示搜索结果' }] }
])

const filters = reactive({
  status: '',
  priority: '',
  type: '',
  search: ''
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const caseForm = reactive({
  title: '',
  description: '',
  priority: 2,
  type: 'functional',
  status: 'designing',
  precondition: '',
  test_data: '',
  environment: '',
  is_automated: false,
  tags: '',
  estimated_duration: 0,
  designer_id: null,
  reviewer_id: null,
  steps: [{ action: '', expected_result: '' }]
})

const caseRules = {
  title: [{ required: true, message: '请输入用例标题', trigger: 'blur' }]
}

const loadSuiteInfo = async () => {
  try {
    const response = await apiService.tests.getSuiteById(suiteId.value)
    suiteInfo.value = response?.data || response
  } catch (error) {
    console.error('加载测试集信息失败:', error)
  }
}

const loadCases = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page
    }
    if (filters.status) params.status = filters.status
    if (filters.priority !== '') params.priority = filters.priority
    if (filters.type) params.type = filters.type
    if (filters.search) params.search = filters.search

    const response = await apiService.tests.getCasesBySuite(suiteId.value, params)
    const data = response?.data || response
    cases.value = data?.cases || []
    pagination.total = data?.total || 0
  } catch (error) {
    console.error('加载用例列表失败:', error)
    ElMessage.error('加载用例列表失败')
  } finally {
    loading.value = false
  }
}

const loadProjectMembers = async () => {
  if (!suiteInfo.value?.project_id) return
  try {
    const response = await apiService.projects.getProjectMembers(suiteInfo.value.project_id)
    projectMembers.value = response?.members || response || []
  } catch (error) {
    console.error('加载项目成员失败:', error)
  }
}

const loadAvailableSuites = async () => {
  if (!suiteInfo.value?.project_id) return
  try {
    const response = await apiService.tests.getSuites(suiteInfo.value.project_id)
    availableSuites.value = response?.data || []
  } catch (error) {
    console.error('加载测试集列表失败:', error)
  }
}

const handleFilter = () => {
  pagination.page = 1
  loadCases()
}

const handleReset = () => {
  filters.status = ''
  filters.priority = ''
  filters.type = ''
  filters.search = ''
  handleFilter()
}

const handlePageChange = (page) => {
  pagination.page = page
  loadCases()
}

const handleSizeChange = (size) => {
  pagination.per_page = size
  loadCases()
}

const canGoBack = ref(false)

const handleBack = () => {
  if (canGoBack.value && window.history.length > 1) {
    router.go(-1)
  } else if (suiteInfo.value?.project_id) {
    router.push(`/projects/${suiteInfo.value.project_id}/tests/suites`)
  } else {
    router.push('/projects/list')
  }
}

const handleView = (row) => {
  router.push(`/projects/${suiteInfo.value.project_id}/tests/cases/${suiteId.value}/${row.id}`)
}

const handleRowDoubleClick = (row) => {
  handleView(row)
}

const handleEdit = (row) => {
  editingCase.value = row
  activeTab.value = 'basic'
  Object.assign(caseForm, {
    title: row.title,
    description: row.description,
    priority: row.priority,
    type: row.type,
    status: row.status,
    precondition: row.precondition,
    test_data: row.test_data,
    environment: row.environment,
    is_automated: row.is_automated,
    tags: row.tags,
    estimated_duration: row.estimated_duration,
    designer_id: row.designer_id,
    reviewer_id: row.reviewer_id,
    steps: row.steps?.length > 0 ? row.steps.map(s => ({ action: s.action, expected_result: s.expected_result })) : [{ action: '', expected_result: '' }]
  })
  loadLinkedRequirements(row.id)
  showCreateDialog.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个测试用例吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await apiService.tests.deleteCase(row.id)
    ElMessage.success('删除成功')
    await loadCases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleQuickExecute = (row) => {
  router.push(`/projects/${suiteInfo.value.project_id}/tests/executions?case_id=${row.id}&suite_id=${suiteId.value}`)
}

const handleCreateCase = () => {
  editingCase.value = null
  activeTab.value = 'basic'
  resetCaseForm()
  showCreateDialog.value = true
}

const resetCaseForm = () => {
  Object.assign(caseForm, {
    title: '',
    description: '',
    priority: 2,
    type: 'functional',
    status: 'designing',
    precondition: '',
    test_data: '',
    environment: '',
    is_automated: false,
    tags: '',
    estimated_duration: 0,
    designer_id: null,
    reviewer_id: null,
    steps: [{ action: '', expected_result: '' }]
  })
  editingCase.value = null
  linkedRequirements.value = []
}

const addStep = () => {
  caseForm.steps.push({ action: '', expected_result: '' })
}

const removeStep = (index) => {
  caseForm.steps.splice(index, 1)
}

const moveStepUp = (index) => {
  if (index > 0) {
    const temp = caseForm.steps[index]
    caseForm.steps.splice(index, 1)
    caseForm.steps.splice(index - 1, 0, temp)
  }
}

const moveStepDown = (index) => {
  if (index < caseForm.steps.length - 1) {
    const temp = caseForm.steps[index]
    caseForm.steps.splice(index, 1)
    caseForm.steps.splice(index + 1, 0, temp)
  }
}

const copyStep = (index) => {
  const original = caseForm.steps[index]
  caseForm.steps.push({ action: original.action, expected_result: original.expected_result })
}

const addStepFromTemplate = () => {
  showStepTemplateDialog.value = true
}

const applyStepTemplate = (template) => {
  caseForm.steps = [...caseForm.steps, ...template.steps.map(s => ({ action: s.action, expected_result: s.expected_result }))]
  showStepTemplateDialog.value = false
  ElMessage.success('已应用模板')
}

const handleUploadStepAttachment = (index) => {
  ElMessage.info('附件上传功能开发中')
}

const handleSaveCase = async () => {
  if (!caseForm.title) {
    ElMessage.warning('请输入用例标题')
    return
  }

  saving.value = true
  try {
    const data = {
      ...caseForm,
      suite_id: suiteId.value,
      steps: caseForm.steps.filter(s => s.action || s.expected_result)
    }

    if (editingCase.value) {
      await apiService.tests.updateCase(editingCase.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await apiService.tests.createCase(data)
      ElMessage.success('创建成功')
    }

    showCreateDialog.value = false
    resetCaseForm()
    await loadCases()
  } catch (error) {
    ElMessage.error(editingCase.value ? '更新失败' : '创建失败')
  } finally {
    saving.value = false
  }
}

const handleSaveAndNew = async () => {
  if (!caseForm.title) {
    ElMessage.warning('请输入用例标题')
    return
  }

  saving.value = true
  try {
    const data = {
      ...caseForm,
      suite_id: suiteId.value,
      steps: caseForm.steps.filter(s => s.action || s.expected_result)
    }

    if (editingCase.value) {
      await apiService.tests.updateCase(editingCase.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await apiService.tests.createCase(data)
      ElMessage.success('创建成功')
    }

    resetCaseForm()
    activeTab.value = 'basic'
    await loadCases()
  } catch (error) {
    ElMessage.error(editingCase.value ? '更新失败' : '创建失败')
  } finally {
    saving.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedCases.value = selection
}

const handleBatchMove = () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请先选择用例')
    return
  }
  batchForm.target_suite_id = null
  showMoveDialog.value = true
}

const handleBatchCopy = async () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请先选择用例')
    return
  }
  try {
    const caseIds = selectedCases.value.map(c => c.id)
    await apiService.tests.batchOperateCases({
      operation: 'copy',
      case_ids: caseIds,
      target_suite_id: suiteId.value
    })
    ElMessage.success('复制成功')
    await loadCases()
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const handleBatchChangeStatus = () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请先选择用例')
    return
  }
  batchForm.new_status = ''
  showStatusDialog.value = true
}

const handleBatchDelete = async () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请先选择用例')
    return
  }
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedCases.value.length} 个用例吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const caseIds = selectedCases.value.map(c => c.id)
    await apiService.tests.batchOperateCases({
      operation: 'delete',
      case_ids: caseIds
    })
    ElMessage.success('删除成功')
    selectedCases.value = []
    await loadCases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleConfirmMove = async () => {
  if (!batchForm.target_suite_id) {
    ElMessage.warning('请选择目标测试集')
    return
  }
  batchOperating.value = true
  try {
    const caseIds = selectedCases.value.map(c => c.id)
    await apiService.tests.batchOperateCases({
      operation: 'move',
      case_ids: caseIds,
      target_suite_id: batchForm.target_suite_id
    })
    ElMessage.success('移动成功')
    showMoveDialog.value = false
    selectedCases.value = []
    await loadCases()
  } catch (error) {
    ElMessage.error('移动失败')
  } finally {
    batchOperating.value = false
  }
}

const handleConfirmStatusChange = async () => {
  if (!batchForm.new_status) {
    ElMessage.warning('请选择新状态')
    return
  }
  batchOperating.value = true
  try {
    const caseIds = selectedCases.value.map(c => c.id)
    await apiService.tests.batchOperateCases({
      operation: 'change_status',
      case_ids: caseIds,
      status: batchForm.new_status
    })
    ElMessage.success('状态修改成功')
    showStatusDialog.value = false
    selectedCases.value = []
    await loadCases()
  } catch (error) {
    ElMessage.error('修改失败')
  } finally {
    batchOperating.value = false
  }
}

const loadLinkedRequirements = async (caseId) => {
  try {
    const response = await apiService.tests.getLinksByCase(caseId)
    linkedRequirements.value = response?.data || []
  } catch (error) {
    console.error('加载关联需求失败:', error)
  }
}

const searchRequirements = async (query) => {
  if (!query) {
    availableRequirements.value = []
    return
  }
  searchingRequirements.value = true
  try {
    const response = await apiService.requirements.getItems(null, { search: query, project_id: suiteInfo.value.project_id })
    availableRequirements.value = response?.data || []
  } catch (error) {
    console.error('搜索需求失败:', error)
  } finally {
    searchingRequirements.value = false
  }
}

const handleLinkRequirement = async () => {
  if (!linkForm.requirement_id) {
    ElMessage.warning('请选择需求')
    return
  }
  linking.value = true
  try {
    await apiService.tests.createRequirementLink({
      test_case_id: editingCase.value.id,
      requirement_id: linkForm.requirement_id,
      link_type: linkForm.link_type
    })
    ElMessage.success('关联成功')
    showLinkRequirementDialog.value = false
    linkForm.requirement_id = null
    linkForm.link_type = 'tests'
    await loadLinkedRequirements(editingCase.value.id)
  } catch (error) {
    ElMessage.error('关联失败')
  } finally {
    linking.value = false
  }
}

const handleUnlinkRequirement = async (linkId) => {
  try {
    await apiService.tests.deleteRequirementLink(linkId)
    ElMessage.success('解除关联成功')
    if (editingCase.value) {
      await loadLinkedRequirements(editingCase.value.id)
    }
  } catch (error) {
    ElMessage.error('解除关联失败')
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const handleExport = async () => {
  try {
    const response = await apiService.tests.exportCases(suiteId.value, 'excel')
    const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `test_cases_${suiteId.value}_${Date.now()}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const handleImportFileChange = (file) => {
  importFileList.value = [file]
}

const beforeUpload = (file) => {
  const isValidSize = file.size / 1024 / 1024 < 10
  if (!isValidSize) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  return true
}

const handleImport = async () => {
  if (importFileList.value.length === 0) {
    ElMessage.warning('请选择要导入的文件')
    return
  }

  importLoading.value = true
  try {
    const file = importFileList.value[0].raw
    const response = await apiService.tests.importCases(suiteId.value, file)
    ElMessage.success(response?.message || '导入成功')
    showImportDialog.value = false
    importFileList.value = []
    await loadCases()
  } catch (error) {
    ElMessage.error('导入失败')
  } finally {
    importLoading.value = false
  }
}

onMounted(async () => {
  canGoBack.value = window.history.length > 1
  suiteId.value = parseInt(route.params.suiteId)
  await loadSuiteInfo()
  await loadProjectMembers()
  await loadAvailableSuites()
  await loadCases()
})
</script>

<style scoped>
.test-case-list {
  padding: 20px;
}

.case-header {
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

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
  margin-top: 0;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.steps-container {
  max-height: 500px;
  overflow-y: auto;
}

.steps-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: #409EFF;
  color: #fff;
  border-radius: 50%;
  font-weight: bold;
}

.requirements-container {
  min-height: 200px;
}

.link-header {
  margin-bottom: 16px;
}

.batch-actions-bar {
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.batch-buttons {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .test-case-list {
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
  .test-case-list {
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
