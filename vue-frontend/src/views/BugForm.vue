<template>
  <div class="bug-form" v-loading="loading">
    <div class="bug-form-header">
      <el-button @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h2>{{ isEdit ? '编辑Bug' : '新建Bug' }}</h2>
    </div>
    
    <el-card>
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="100px"
        label-position="top"
      >
        <!-- 基本信息 -->
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="标题" prop="title">
              <el-input 
                v-model="form.title" 
                placeholder="请输入Bug标题"
                maxlength="200"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="8">
            <el-form-item label="项目" prop="project_id">
              <el-select 
                v-model="form.project_id" 
                placeholder="请选择项目"
                filterable
                clearable
              >
                <el-option 
                  v-for="project in projects" 
                  :key="project.id" 
                  :label="project.name" 
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 状态和优先级 -->
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择状态">
                <el-option label="新建" value="open" />
                <el-option label="进行中" value="in_progress" />
                <el-option label="已解决" value="resolved" />
                <el-option label="已关闭" value="closed" />
                <el-option label="已重开" value="reopened" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="6">
            <el-form-item label="严重程度" prop="severity">
              <el-select v-model="form.severity" placeholder="请选择严重程度">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="严重" value="critical" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="6">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="form.priority" placeholder="请选择优先级">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 版本和构建信息 -->
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="归属版本" prop="version">
              <el-select 
                v-model="form.version" 
                placeholder="请选择归属版本"
                filterable
                clearable
              >
                <el-option 
                  v-for="v in projectVersions" 
                  :key="v.name" 
                  :label="v.name" 
                  :value="v.name"
                />
                <el-option label="手动输入" value="__custom__" />
              </el-select>
              <el-input 
                v-if="form.version === '__custom__'" 
                v-model="form.customVersion" 
                placeholder="请输入版本号"
                style="margin-top: 5px;"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="6">
            <el-form-item label="问题类型" prop="issue_type">
              <el-select v-model="form.issue_type" placeholder="请选择问题类型">
                <el-option label="软件" value="software" />
                <el-option label="硬件" value="hardware" />
                <el-option label="文档" value="documentation" />
                <el-option label="需求" value="requirement" />
                <el-option label="设计" value="design" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="6">
            <el-form-item label="重现频率" prop="reproduce_frequency">
              <el-select v-model="form.reproduce_frequency" placeholder="请选择重现频率">
                <el-option label="必然复现" value="always" />
                <el-option label="经常复现" value="often" />
                <el-option label="偶尔复现" value="occasionally" />
                <el-option label="很难复现" value="rarely" />
                <el-option label="无法复现" value="never" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 构建和模块信息 -->
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="发现构建" prop="found_build">
              <el-input v-model="form.found_build" placeholder="请输入发现构建" />
            </el-form-item>
          </el-col>
          
          <el-col :span="6">
            <el-form-item label="测试版本" prop="test_version">
              <el-input v-model="form.test_version" placeholder="请输入测试版本" />
            </el-form-item>
          </el-col>
          
          <el-col :span="6">
            <el-form-item label="模块" prop="module">
              <el-select 
                v-model="form.module" 
                placeholder="请选择或输入模块"
                filterable
                clearable
                allow-create
              >
                <el-option 
                  v-for="m in projectModules" 
                  :key="m.name" 
                  :label="m.name" 
                  :value="m.name"
                />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="6">
            <el-form-item label="客户MR编号" prop="customer_mr_number">
              <el-input v-model="form.customer_mr_number" placeholder="请输入客户MR编号" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 分配和解决信息 -->
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="计划解决版本" prop="plan_resolve_version">
              <el-input v-model="form.plan_resolve_version" placeholder="请输入计划解决版本" />
            </el-form-item>
          </el-col>
          
          <el-col :span="6">
            <el-form-item label="解决构建" prop="resolve_build">
              <el-input v-model="form.resolve_build" placeholder="请输入解决构建" />
            </el-form-item>
          </el-col>
          
          <el-col :span="6">
            <el-form-item label="解决者" prop="resolver_id">
              <el-select v-model="form.resolver_id" placeholder="请选择解决者" filterable clearable>
                <el-option 
                  v-for="user in users" 
                  :key="user.id" 
                  :label="user.username" 
                  :value="user.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 验证信息 -->
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="验证者" prop="verifier_id">
              <el-select v-model="form.verifier_id" placeholder="请选择验证者" filterable clearable>
                <el-option 
                  v-for="user in users" 
                  :key="user.id" 
                  :label="user.username" 
                  :value="user.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="期限" prop="due_date">
              <el-date-picker
                v-model="form.due_date"
                type="datetime"
                placeholder="请选择期限"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- Bug描述 -->
        <el-form-item label="Bug 描述" prop="description">
          <RichTextEditor
            ref="descriptionEditorRef"
            v-model="form.description"
            placeholder="请详细描述 Bug 的现象和问题，支持富文本编辑和图片上传"
            :rows="8"
          />
        </el-form-item>

        <!-- 重现步骤 -->
        <el-form-item label="重现步骤" prop="steps_to_reproduce">
          <RichTextEditor
            ref="stepsEditorRef"
            v-model="form.steps_to_reproduce"
            placeholder="请详细描述重现 Bug 的步骤，支持富文本编辑和图片上传"
            :rows="6"
          />
        </el-form-item>
        
        <!-- 预期结果和实际结果 -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="预期结果" prop="expected_result">
              <RichTextEditor
                ref="expectedResultEditorRef"
                v-model="form.expected_result"
                placeholder="请输入预期结果，支持富文本编辑和图片上传"
                :rows="4"
              />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="实际结果" prop="actual_result">
              <RichTextEditor
                ref="actualResultEditorRef"
                v-model="form.actual_result"
                placeholder="请输入实际结果，支持富文本编辑和图片上传"
                :rows="4"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 标签 -->
        <el-form-item label="标签">
          <el-select
            v-model="form.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请选择或输入标签"
          >
            <el-option 
              v-for="tag in availableTags" 
              :key="tag" 
              :label="tag" 
              :value="tag"
            />
          </el-select>
        </el-form-item>
        
        <!-- 附件上传 -->
        <el-form-item label="附件">
          <!-- 已上传附件列表 -->
          <div v-if="isEdit && existingAttachments.length > 0" class="existing-attachments">
            <div class="existing-attachments-title">已上传附件：</div>
            <div
              v-for="attachment in existingAttachments"
              :key="attachment.id"
              class="attachment-item"
            >
              <div class="attachment-info">
                <el-icon><Document /></el-icon>
                <span class="attachment-name">{{ attachment.filename }}</span>
                <span class="attachment-size">({{ formatFileSize(attachment.file_size) }})</span>
              </div>
              <div class="attachment-actions">
                <el-button
                  type="primary"
                  link
                  size="small"
                  @click="downloadAttachment(attachment)"
                >
                  下载
                </el-button>
                <el-button
                  type="danger"
                  link
                  size="small"
                  @click="deleteAttachment(attachment)"
                  :loading="deletingAttachmentId === attachment.id"
                >
                  删除
                </el-button>
              </div>
            </div>
          </div>
          
          <!-- 新文件上传 -->
          <el-upload
            ref="uploadRef"
            :http-request="uploadFile"
            :file-list="fileList"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :on-remove="handleRemove"
            :before-upload="beforeUpload"
            multiple
            :limit="5"
            :disabled="!isEdit && !bugId"
          >
            <el-button type="primary" :disabled="!isEdit && !bugId">
              <el-icon><Plus /></el-icon>
              选择文件
            </el-button>
            <template #tip>
              <div class="el-upload__tip">
                {{ isEdit ? '支持上传图片、文档等文件，单个文件不超过50MB' : '请先保存Bug后再上传附件' }}
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <!-- 表单操作 -->
        <el-form-item>
          <div class="form-actions">
            <el-button @click="$router.back()">取消</el-button>
            <el-button type="primary" @click="submitForm">
              {{ isEdit ? '更新' : '创建' }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useBugStore } from '@/stores/bug'
import { useUserStore } from '@/stores/user'
import api, { apiService } from '@/services/api'
import { Plus, Document } from '@element-plus/icons-vue'
import RichTextEditor from '@/components/common/RichTextEditor.vue'

const route = useRoute()
const router = useRouter()
const bugStore = useBugStore()
const userStore = useUserStore()

const loading = ref(false)
const formRef = ref(null)
const uploadRef = ref(null)
const projectChangeTimer = ref(null)
const descriptionEditorRef = ref(null)
const stepsEditorRef = ref(null)
const expectedResultEditorRef = ref(null)
const actualResultEditorRef = ref(null)

const isEdit = computed(() => route.name === 'BugEdit' || route.name === 'ProjectBugEdit')

const getRedirectUrl = () => {
  if (route.name === 'ProjectBugCreate' || route.name === 'ProjectBugEdit') {
    const projectId = route.params.projectId
    return `/projects/${projectId}/bugs`
  }
  return '/bugs'
}

const form = reactive({
  title: '',
  description: '',
  steps_to_reproduce: '',
  expected_result: '',
  actual_result: '',
  status: 'new',
  severity: 'medium',
  priority: 'medium',
  project_id: '',
  tags: [],
  // 新增字段
  version: '',
  customVersion: '',
  issue_type: 'bug',
  reproduce_frequency: 'always',
  found_build: '',
  test_version: '',
  module: '',
  customer_mr_number: '',
  plan_resolve_version: '',
  resolve_build: '',
  resolver_id: '',
  verifier_id: '',
  due_date: ''
})

const projects = ref([])
const users = ref([])
const projectMembers = ref([])
const projectVersions = ref([])
const projectModules = ref([])
const availableTags = ref(['前端', '后端', '数据库', 'UI', '功能', '性能', '安全'])
const fileList = ref([])
const existingAttachments = ref([])
const deletingAttachmentId = ref(null)
const bugId = computed(() => route.params.id)

const rules = {
  title: [
    { required: true, message: '请输入Bug标题', trigger: 'blur' },
    { min: 3, max: 200, message: '标题长度在 3 到 200 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入Bug描述', trigger: 'blur' },
    { min: 10, message: '描述长度至少 10 个字符', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ],
  severity: [
    { required: true, message: '请选择严重程度', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  project_id: [
    { required: true, message: '请选择项目', trigger: 'change' }
  ]
}

// 上传配置 - 使用自定义上传方法
const uploadFile = async (options) => {
  const { file, onProgress, onSuccess, onError } = options
  
  if (!isEdit.value || !bugId.value) {
    ElMessage.error('请先保存Bug后再上传附件')
    return
  }
  
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await apiService.bugs.uploadAttachment(bugId.value, formData)
    
    if (onSuccess && typeof onSuccess === 'function') {
      onSuccess(response)
    }
    ElMessage.success(`文件 "${file.name}" 上传成功`)
    // 刷新附件列表
    await fetchBugAttachments()
  } catch (error) {
    console.error('上传失败:', error)
    let errorMsg = '上传失败'
    if (error.response?.data?.message) {
      errorMsg = error.response.data.message
    } else if (error.response?.data?.error) {
      errorMsg = error.response.data.error
    }
    if (onError && typeof onError === 'function') {
      onError(new Error(errorMsg))
    }
    ElMessage.error(errorMsg)
  }
}

// 获取Bug详情（编辑模式）
const fetchBugDetail = async () => {
  if (!isEdit.value) return

  loading.value = true
  try {
    await bugStore.fetchBug(route.params.id)
    const bug = bugStore.currentBug

    // 填充表单数据
    Object.keys(form).forEach(key => {
      if (bug[key] !== undefined) {
        form[key] = bug[key]
      }
    })

    // 处理后端返回的deadline字段，映射到前端的due_date
    if (bug.deadline) {
      form.due_date = bug.deadline
    }

    // 处理issue_type字段（后端返回的是issue_type）
    if (bug.issue_type) {
      form.issue_type = bug.issue_type
    }

    // 处理标签（如果是JSON字符串需要解析）
    if (bug.tags && typeof bug.tags === 'string') {
      try {
        form.tags = JSON.parse(bug.tags)
      } catch (e) {
        form.tags = bug.tags.split(',')
      }
    } else if (Array.isArray(bug.tags)) {
      form.tags = bug.tags
    }

    // 加载附件列表
    if (bug.attachments && Array.isArray(bug.attachments)) {
      existingAttachments.value = bug.attachments
    } else {
      await fetchBugAttachments()
    }

    // 获取项目版本列表
    if (bug.project_id) {
      try {
        const response = await api.get(`/projects/${bug.project_id}`)
        const projectData = response.project
        if (projectData && projectData.versions) {
          try {
            projectVersions.value = typeof projectData.versions === 'string'
              ? JSON.parse(projectData.versions)
              : projectData.versions
          } catch (e) {
            console.error('解析项目版本失败:', e)
            projectVersions.value = []
          }
        }
        // 获取项目模块列表
        if (projectData && projectData.modules) {
          try {
            projectModules.value = typeof projectData.modules === 'string'
              ? JSON.parse(projectData.modules)
              : projectData.modules
          } catch (e) {
            console.error('解析项目模块失败:', e)
            projectModules.value = []
          }
        }
      } catch (e) {
        console.error('获取项目版本失败:', e)
      }
    }

  } catch (error) {
    console.error('获取Bug详情失败:', error)
    ElMessage.error('获取Bug详情失败')
  } finally {
    loading.value = false
  }
}

// 获取Bug附件列表
const fetchBugAttachments = async () => {
  if (!isEdit.value || !bugId.value) return
  
  try {
    const response = await apiService.bugs.getAttachments(bugId.value)
    if (response && response.attachments) {
      existingAttachments.value = response.attachments
    } else if (Array.isArray(response)) {
      existingAttachments.value = response
    }
  } catch (error) {
    console.error('获取附件列表失败:', error)
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

// 下载附件
const downloadAttachment = async (attachment) => {
  try {
    const response = await apiService.bugs.downloadAttachment(bugId.value, attachment.id)
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', attachment.filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('开始下载附件')
  } catch (error) {
    console.error('下载附件失败:', error)
    ElMessage.error('下载附件失败')
  }
}

// 删除附件
const deleteAttachment = async (attachment) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除附件 "${attachment.filename}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    deletingAttachmentId.value = attachment.id
    await apiService.bugs.deleteAttachment(bugId.value, attachment.id)
    
    ElMessage.success('附件删除成功')
    // 从列表中移除
    existingAttachments.value = existingAttachments.value.filter(a => a.id !== attachment.id)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除附件失败:', error)
      ElMessage.error('删除附件失败')
    }
  } finally {
    deletingAttachmentId.value = null
  }
}

// 获取项目列表
const fetchProjects = async () => {
  try {
    const response = await api.get('/projects')
    projects.value = response.projects || []
  } catch (error) {
    console.error('获取项目列表失败:', error)
    projects.value = []
  }
}

// 获取用户列表
const fetchUsers = async () => {
  try {
    const response = await api.get('/users')
    users.value = response.users || []
  } catch (error) {
    console.error('获取用户列表失败:', error)
    users.value = []
  }
}

// 获取项目成员列表
const fetchProjectMembers = async (projectId) => {
  if (!projectId) {
    projectMembers.value = []
    return
  }
  
  try {
    const response = await api.get(`/projects/${projectId}`)
    projectMembers.value = response.project?.members || []
    
    // 获取项目版本列表
    const projectData = response.project
    if (projectData && projectData.versions) {
      try {
        projectVersions.value = typeof projectData.versions === 'string' 
          ? JSON.parse(projectData.versions) 
          : projectData.versions
      } catch (e) {
        console.error('解析项目版本失败:', e)
        projectVersions.value = []
      }
    } else {
      projectVersions.value = []
    }
    
    // 获取项目模块列表
    if (projectData && projectData.modules) {
      try {
        projectModules.value = typeof projectData.modules === 'string' 
          ? JSON.parse(projectData.modules) 
          : projectData.modules
      } catch (e) {
        console.error('解析项目模块失败:', e)
        projectModules.value = []
      }
    } else {
      projectModules.value = []
    }
  } catch (error) {
    console.error('获取项目成员列表失败:', error)
    projectMembers.value = []
    projectVersions.value = []
    projectModules.value = []
  }
}

// 文件上传前验证
const beforeUpload = (file) => {
  const maxSize = 50 * 1024 * 1024 // 50MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 50MB!')
    return false
  }
  return true
}

// 文件上传成功
const handleUploadSuccess = (response, file) => {
  ElMessage.success('文件上传成功')
  // 这里需要根据实际API响应处理
}

// 文件上传失败
const handleUploadError = (error, file) => {
  console.error('文件上传失败:', error)
  ElMessage.error('文件上传失败')
}

// 文件移除
const handleRemove = (file, fileList) => {
  // 这里需要根据实际API处理文件删除
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    loading.value = true
    
    const formData = { ...form }

    const apiData = {
      title: formData.title,
      description: formData.description,
      issue_type: formData.issue_type || 'bug',
      severity: formData.severity,
      priority: formData.priority,
      project_id: formData.project_id,

      resolved_by: formData.resolver_id || null,
      verifier_id: formData.verifier_id || null,

      version: formData.version === '__custom__' ? (formData.customVersion || '') : (formData.version || ''),
      found_build: formData.found_build || '',
      test_version: formData.test_version || '',
      plan_resolve_version: formData.plan_resolve_version || '',
      resolve_build: formData.resolve_build || '',

      module: formData.module || '',
      customer_mr_number: formData.customer_mr_number || '',
      reproduce_frequency: formData.reproduce_frequency || 'always',

      status: formData.status,
      deadline: formData.due_date || null,

      reproduce_steps: formData.steps_to_reproduce || '',
      expected_result: formData.expected_result || '',
      actual_result: formData.actual_result || '',

      tags: formData.tags && Array.isArray(formData.tags) ? JSON.stringify(formData.tags) : formData.tags
    }

    if (isEdit.value) {
      await bugStore.updateBug(route.params.id, apiData)
      ElMessage.success('Bug更新成功')
    } else {
      await bugStore.createBug(apiData)
      ElMessage.success('Bug创建成功')
    }

    router.push(getRedirectUrl())
  } catch (error) {
    if (error && error.errors) {
      // 表单验证错误
      return
    }
    
    console.error('提交表单失败:', error)
    ElMessage.error(isEdit.value ? '更新Bug失败' : '创建Bug失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    fetchProjects(),
    fetchUsers()
  ])

  if (isEdit.value) {
    await fetchBugDetail()
    if (form.project_id) {
      await fetchProjectMembers(form.project_id)
    }
  } else {
    const projectIdParam = route.params.projectId || route.query.project_id
    if (projectIdParam) {
      const pid = parseInt(projectIdParam)
      form.project_id = pid
      await fetchProjectMembers(pid)
    }
  }
})

// 监听项目变化，更新成员列表（添加防抖处理）
watch(() => form.project_id, async (newProjectId) => {
  if (projectChangeTimer.value) {
    clearTimeout(projectChangeTimer.value)
  }
  projectChangeTimer.value = setTimeout(async () => {
    await fetchProjectMembers(newProjectId)
  }, 300)
})
</script>

<style scoped>
.bug-form {
  padding: 0;
}

.bug-form-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.bug-form-header h2 {
  margin: 0;
  color: #303133;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #303133;
}

:deep(.el-upload__tip) {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

/* 已上传附件列表样式 */
.existing-attachments {
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.existing-attachments-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  font-size: 14px;
}

.attachment-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  margin-bottom: 8px;
  background-color: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  transition: all 0.3s;
}

.attachment-item:last-child {
  margin-bottom: 0;
}

.attachment-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.1);
}

.attachment-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.attachment-info .el-icon {
  color: #409eff;
  font-size: 18px;
  flex-shrink: 0;
}

.attachment-name {
  color: #303133;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-size {
  color: #909399;
  font-size: 12px;
  flex-shrink: 0;
}

.attachment-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .bug-form-container {
    padding: 12px;
  }

  .form-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  .form-header h2 {
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

  .bug-form-card {
    margin-bottom: 16px;
  }

  .bug-form-card :deep(.el-card__body) {
    padding: 16px;
  }

  .el-form-item {
    margin-bottom: 16px;
  }

  .el-form-item__label {
    font-size: 13px;
    padding-bottom: 4px;
  }

  .el-input__inner,
  .el-textarea__inner {
    font-size: 14px;
  }

  .el-select,
  .el-input,
  .el-textarea {
    width: 100% !important;
  }

  .attachment-list {
    max-height: 200px;
  }

  .attachment-item {
    padding: 10px 12px;
    flex-wrap: wrap;
    gap: 8px;
  }

  .attachment-info {
    flex: 1;
    min-width: 0;
  }

  .attachment-name {
    font-size: 13px;
  }

  .attachment-size {
    font-size: 11px;
  }

  .attachment-actions {
    width: 100%;
    justify-content: flex-end;
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
}

@media screen and (max-width: 480px) {
  .bug-form-container {
    padding: 8px;
  }

  .form-header h2 {
    font-size: 16px;
  }

  .bug-form-card :deep(.el-card__body) {
    padding: 12px;
  }

  .el-form-item__label {
    font-size: 12px;
  }

  .attachment-name {
    font-size: 12px;
  }

  .attachment-size {
    font-size: 10px;
  }
}
</style>