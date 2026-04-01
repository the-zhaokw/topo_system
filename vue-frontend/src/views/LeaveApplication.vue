<template>
  <div class="leave-application">
    <div class="header">
      <h1>请假申请</h1>
      <div class="header-actions">
        <el-button @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
    </div>

    <!-- 请假申请表单 -->
    <el-card class="application-form">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="请假类型" prop="leave_type">
          <el-select v-model="form.leave_type" placeholder="请选择请假类型">
            <el-option label="年假" value="annual" />
            <el-option label="病假" value="sick" />
            <el-option label="事假" value="personal" />
            <el-option label="调休假" value="compensatory" />
            <el-option label="婚假" value="marriage" />
            <el-option label="产假" value="maternity" />
            <el-option label="陪产假" value="paternity" />
            <el-option label="丧假" value="bereavement" />
          </el-select>
        </el-form-item>

        <el-form-item label="请假时间" required>
          <el-col :span="11">
            <el-form-item prop="start_date">
              <el-date-picker
                v-model="form.start_date"
                type="date"
                placeholder="开始日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="2" class="text-center">-</el-col>
          <el-col :span="11">
            <el-form-item prop="end_date">
              <el-date-picker
                v-model="form.end_date"
                type="date"
                placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-form-item>

        <el-form-item label="请假天数" prop="days">
          <el-input-number
            v-model="form.days"
            :min="0.5"
            :step="0.5"
            :precision="1"
            placeholder="请假天数"
          />
          <span class="days-hint">天（0.5表示半天）</span>
        </el-form-item>

        <el-form-item label="紧急情况" prop="emergency_flag">
          <el-switch
            v-model="form.emergency_flag"
            active-text="紧急"
            inactive-text="正常"
          />
          <span class="emergency-hint">紧急情况可先电话/微信口头报备，48小时内补单</span>
        </el-form-item>

        <el-form-item label="附件上传" prop="attachment">
          <el-upload
            class="upload-demo"
            :action="uploadUrl"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            :show-file-list="false"
          >
            <el-button type="primary">
              <el-icon><Upload /></el-icon>
              上传附件
            </el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持上传病假证明、结婚证等附件，文件大小不超过10MB
              </div>
            </template>
          </el-upload>
          <div v-if="form.attachment_path" class="attachment-info">
            <el-icon><Document /></el-icon>
            <span>{{ getFileName(form.attachment_path) }}</span>
            <el-button type="text" @click="removeAttachment">删除</el-button>
          </div>
        </el-form-item>

        <el-form-item label="审批人" prop="approver_id">
          <el-select
            v-model="form.approver_id"
            placeholder="请选择审批人"
            filterable
            clearable
            remote
            :remote-method="searchUsers"
            :loading="loading"
            style="width: 100%"
          >
            <el-option
              v-for="user in allUsers"
              :key="user.id"
              :label="`${user.username} (${user.email}) - ${user.position || ''}`"
              :value="user.id"
            />
          </el-select>
          <div style="font-size: 12px; color: #666; margin-top: 5px;">
            支持搜索用户名、邮箱、姓名、工号
          </div>
        </el-form-item>

        <el-form-item label="多级审批">
          <el-switch
            v-model="enableMultiLevelApproval"
            active-text="启用多级审批"
            inactive-text="单级审批"
          />
        </el-form-item>

        <el-form-item v-if="enableMultiLevelApproval" label="审批流程">
          <div v-for="(level, index) in approvalLevels" :key="index" class="approval-level-item">
            <el-tag type="info">第{{ index + 1 }}级审批</el-tag>
            <el-select
              v-model="level.approver_id"
              placeholder="选择审批人"
              filterable
              clearable
              remote
              :remote-method="searchUsers"
              :loading="loading"
              style="width: 280px; margin-left: 10px;"
            >
              <el-option
                v-for="user in allUsers"
                :key="user.id"
                :label="`${user.username} (${user.position || ''})`"
                :value="user.id"
              />
            </el-select>
            <el-button 
              v-if="index > 0" 
              type="danger" 
              link 
              @click="removeApprovalLevel(index)"
              style="margin-left: 10px;"
            >
              删除
            </el-button>
          </div>
          <el-button 
            v-if="approvalLevels.length < 3" 
            type="primary" 
            link 
            @click="addApprovalLevel"
          >
            + 添加下一级审批
          </el-button>
          <div style="font-size: 12px; color: #666; margin-top: 5px;">
            最多支持3级审批（如：组长 → 经理 → 总监）
          </div>
        </el-form-item>

        <el-form-item label="请假事由" prop="reason">
          <el-input
            v-model="form.reason"
            type="textarea"
            :rows="4"
            placeholder="请详细说明请假原因"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            提交申请
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 我的请假记录 -->
    <el-card class="my-applications">
      <template #header>
        <div class="card-header">
          <span>我的请假记录</span>
          <el-button type="primary" @click="fetchMyApplications">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table :data="myApplications" v-loading="tableLoading">
        <el-table-column prop="id" label="申请ID" width="80" />
        <el-table-column prop="leave_type" label="请假类型">
          <template #default="{ row }">
            <el-tag :type="getLeaveTypeTag(row.leave_type)">
              {{ getLeaveTypeText(row.leave_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期" width="120" />
        <el-table-column prop="end_date" label="结束日期" width="120" />
        <el-table-column label="天数" width="80">
          <template #default="{ row }">
            {{ Math.ceil(row.total_hours / 8) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="审批人" width="120">
          <template #default="{ row }">
            {{ getApproverName(row) }}
          </template>
        </el-table-column>
        <el-table-column label="审批时间" width="160">
          <template #default="{ row }">
            {{ row.status === 'approved' ? row.approved_at : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" @click="viewApplication(row)">查看</el-button>
            <el-button 
              v-if="row.status === 'pending'" 
              size="small" 
              type="primary" 
              @click="editApplication(row)"
            >
              修改
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 修改申请对话框 -->
    <el-dialog
      v-model="editDialog.visible"
      title="修改请假申请"
      width="600px"
      :before-close="() => editDialog.visible = false"
    >
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
        <el-form-item label="请假类型" prop="leave_type">
          <el-select v-model="editForm.leave_type" placeholder="请选择请假类型">
            <el-option label="年假" value="annual" />
            <el-option label="病假" value="sick" />
            <el-option label="事假" value="personal" />
            <el-option label="调休假" value="compensatory" />
            <el-option label="婚假" value="marriage" />
            <el-option label="产假" value="maternity" />
            <el-option label="陪产假" value="paternity" />
            <el-option label="丧假" value="bereavement" />
          </el-select>
        </el-form-item>

        <el-form-item label="请假时间" required>
          <el-col :span="11">
            <el-form-item prop="start_date">
              <el-date-picker
                v-model="editForm.start_date"
                type="date"
                placeholder="开始日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="2" class="text-center">-</el-col>
          <el-col :span="11">
            <el-form-item prop="end_date">
              <el-date-picker
                v-model="editForm.end_date"
                type="date"
                placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-form-item>

        <el-form-item label="请假天数" prop="days">
          <el-input-number
            v-model="editForm.days"
            :min="1"
            :max="365"
            controls-position="right"
            style="width: 120px"
          />
          <div class="days-hint">系统将根据请假时间自动计算天数</div>
        </el-form-item>

        <el-form-item label="紧急情况" prop="emergency_flag">
          <el-switch
            v-model="editForm.emergency_flag"
            active-text="紧急"
            inactive-text="正常"
          />
        </el-form-item>

        <el-form-item label="附件上传" prop="attachment_path">
          <el-upload
            class="upload-demo"
            action="/api/upload"
            :on-success="handleEditUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            :show-file-list="false"
          >
            <el-button type="primary">
              <el-icon><Upload /></el-icon>
              上传附件
            </el-button>
          </el-upload>
          <div v-if="editForm.attachment_path" class="attachment-info">
            <el-icon><Document /></el-icon>
            {{ getFileName(editForm.attachment_path) }}
            <el-button type="text" @click="editForm.attachment_path = ''">删除</el-button>
          </div>
        </el-form-item>

        <el-form-item label="审批人" prop="approver_id">
          <el-select v-model="editForm.approver_id" placeholder="请选择审批人" filterable>
            <el-option
              v-for="user in allUsers"
              :key="user.id"
              :label="`${user.username} (${user.email}) - ${user.position || ''}`"
              :value="user.id"
            />
          </el-select>
          <div class="approver-hint">请选择一位用户作为审批人</div>
        </el-form-item>

        <el-form-item label="请假事由" prop="reason">
          <el-input
            v-model="editForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请详细说明请假原因"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialog.visible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="handleEditSubmit"
            :loading="editDialog.loading"
          >
            确认修改
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 详细信息对话框 -->
    <el-dialog
      v-model="detailDialog.visible"
      title="请假申请详情"
      width="600px"
      :before-close="() => detailDialog.visible = false"
    >
      <el-descriptions :column="1" border v-if="detailDialog.currentApplication">
        <el-descriptions-item label="申请ID">
          {{ detailDialog.currentApplication.id }}
        </el-descriptions-item>
        <el-descriptions-item label="申请人">
          {{ detailDialog.currentApplication.user_name || detailDialog.currentApplication.user_email }}
        </el-descriptions-item>
        <el-descriptions-item label="请假类型">
          <el-tag :type="getLeaveTypeTag(detailDialog.currentApplication.leave_type)">
            {{ getLeaveTypeText(detailDialog.currentApplication.leave_type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="开始日期">
          {{ detailDialog.currentApplication.start_date }}
        </el-descriptions-item>
        <el-descriptions-item label="结束日期">
          {{ detailDialog.currentApplication.end_date }}
        </el-descriptions-item>
        <el-descriptions-item label="请假天数">
          {{ detailDialog.currentApplication.days }} 天
        </el-descriptions-item>
        <el-descriptions-item label="紧急情况">
          <el-tag :type="detailDialog.currentApplication.emergency_flag ? 'danger' : 'success'">
            {{ detailDialog.currentApplication.emergency_flag ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTag(detailDialog.currentApplication.status)">
            {{ getStatusText(detailDialog.currentApplication.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="审批人">
          {{ getApproverName(detailDialog.currentApplication) }}
        </el-descriptions-item>
        <el-descriptions-item label="申请时间">
          {{ detailDialog.currentApplication.created_at }}
        </el-descriptions-item>
        <el-descriptions-item label="审批时间" v-if="detailDialog.currentApplication.approved_at">
          {{ detailDialog.currentApplication.approved_at }}
        </el-descriptions-item>
        <el-descriptions-item label="请假事由">
          {{ detailDialog.currentApplication.reason }}
        </el-descriptions-item>
        <el-descriptions-item label="附件" v-if="detailDialog.currentApplication.attachment_path">
          <a :href="detailDialog.currentApplication.attachment_path" target="_blank">
            {{ getFileName(detailDialog.currentApplication.attachment_path) }}
          </a>
        </el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialog.visible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Refresh, Upload, Document } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const router = useRouter()
const formRef = ref()
const editFormRef = ref()
const loading = ref(false)
const tableLoading = ref(false)

// 表单数据
const form = reactive({
  leave_type: '',
  start_date: '',
  end_date: '',
  days: 1,
  reason: '',
  emergency_flag: false,
  attachment_path: '',
  approver_id: ''
})

// 编辑表单数据
const editForm = reactive({
  id: null,
  leave_type: '',
  start_date: '',
  end_date: '',
  days: 1,
  reason: '',
  emergency_flag: false,
  attachment_path: '',
  approver_id: ''
})

// 编辑对话框
const editDialog = reactive({
  visible: false,
  loading: false
})

// 详情对话框
const detailDialog = reactive({
  visible: false,
  currentApplication: null
})

// 文件上传URL
const uploadUrl = '/api/upload'

// 表单验证规则
const rules = {
  leave_type: [{ required: true, message: '请选择请假类型', trigger: 'change' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
  days: [
    { required: true, message: '请输入请假天数', trigger: 'blur' },
    { type: 'number', min: 0.5, message: '请假天数不能小于0.5天', trigger: 'blur' }
  ],
  reason: [
    { required: true, message: '请输入请假事由', trigger: 'blur' },
    { min: 5, max: 500, message: '请假事由长度在5到500个字符之间', trigger: 'blur' }
  ],
  approver_id: [{ required: true, message: '请选择审批人', trigger: 'change' }]
}

// 编辑表单验证规则（与主表单相同）
const editRules = {
  leave_type: [{ required: true, message: '请选择请假类型', trigger: 'change' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
  days: [
    { required: true, message: '请输入请假天数', trigger: 'blur' },
    { type: 'number', min: 0.5, message: '请假天数不能小于0.5天', trigger: 'blur' }
  ],
  reason: [
    { required: true, message: '请输入请假事由', trigger: 'blur' },
    { min: 5, max: 500, message: '请假事由长度在5到500个字符之间', trigger: 'blur' }
  ],
  approver_id: [{ required: true, message: '请选择审批人', trigger: 'change' }]
}

// 所有用户列表（用于审批人选择）
const allUsers = ref([])

// 多级审批相关
const enableMultiLevelApproval = ref(false)
const approvalLevels = ref([
  { level: 1, approver_id: null, status: 'pending' }
])

const addApprovalLevel = () => {
  if (approvalLevels.value.length < 3) {
    approvalLevels.value.push({
      level: approvalLevels.value.length + 1,
      approver_id: null,
      status: 'pending'
    })
  }
}

const removeApprovalLevel = (index) => {
  approvalLevels.value.splice(index, 1)
  approvalLevels.value.forEach((level, i) => {
    level.level = i + 1
  })
}

// 我的申请记录
const myApplications = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 搜索用户
const searchUsers = async (keyword) => {
  loading.value = true
  try {
    if (!keyword.trim()) {
      await fetchAllUsers()
      return
    }
    
    const response = await apiService.users.getApprovers()
    const allUsersList = response.users || []
    const keywordLower = keyword.toLowerCase()
    allUsers.value = allUsersList.filter(user => 
      user.username.toLowerCase().includes(keywordLower) ||
      user.email.toLowerCase().includes(keywordLower) ||
      (user.first_name && user.first_name.toLowerCase().includes(keywordLower)) ||
      (user.last_name && user.last_name.toLowerCase().includes(keywordLower))
    )
  } catch (error) {
    console.error('搜索用户失败:', error)
    await fetchAllUsers()
  } finally {
    loading.value = false
  }
}

// 获取所有用户列表
const fetchAllUsers = async () => {
  try {
    const response = await apiService.users.getApprovers()
    allUsers.value = response.users || []
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  }
}

// 文件上传相关函数
const handleUploadSuccess = (response, file) => {
  if (response && response.file_path) {
    form.attachment_path = response.file_path
    ElMessage.success('附件上传成功')
  } else {
    ElMessage.error('上传失败')
  }
}

const handleUploadError = (error, file) => {
  console.error('上传失败:', error)
  ElMessage.error('附件上传失败')
}

const beforeUpload = (file) => {
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('附件大小不能超过10MB')
    return false
  }
  return true
}

const removeAttachment = () => {
  form.attachment_path = ''
}

const getFileName = (path) => {
  return path.split('/').pop()
}

// 获取我的请假申请
const fetchMyApplications = async () => {
  tableLoading.value = true
  try {
    const response = await apiService.attendance.getLeaveApplications()
    if (response && (response.applications || response.data)) {
      myApplications.value = response.applications || response.data || []
      total.value = response.pagination?.total || response.total || myApplications.value.length || 0
    } else {
      myApplications.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取请假申请失败:', error)
    ElMessage.error('获取请假申请失败')
  } finally {
    tableLoading.value = false
  }
}

// 请假类型标签
const getLeaveTypeTag = (type) => {
  const tags = {
    annual: 'success',
    sick: 'warning',
    personal: 'info',
    compensatory: 'primary',
    marriage: 'danger',
    maternity: 'danger',
    paternity: 'primary',
    bereavement: 'info'
  }
  return tags[type] || ''
}

const getLeaveTypeText = (type) => {
  const texts = {
    annual: '年假',
    sick: '病假',
    personal: '事假',
    compensatory: '调休假',
    marriage: '婚假',
    maternity: '产假',
    paternity: '陪产假',
    bereavement: '丧假'
  }
  return texts[type] || type
}

// 状态标签
const getStatusTag = (status) => {
  const tags = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return tags[status] || ''
}

const getStatusText = (status) => {
  const texts = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝'
  }
  return texts[status] || status
}

// 获取审批人名称
const getApproverName = (application) => {
  if (application.approver_name) {
    return application.approver_name
  }
  if (application.approver_id) {
    const approver = allUsers.value.find(user => user.id === application.approver_id)
    return approver ? `${approver.username} (${approver.email})` : '未知审批人'
  }
  return '未指定'
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchMyApplications()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchMyApplications()
}

// 查看申请详情
const viewApplication = (application) => {
  // 显示详细信息对话框
  detailDialog.currentApplication = application
  detailDialog.visible = true
}

// 编辑申请
const editApplication = (application) => {
  // 填充编辑表单
  editForm.id = application.id
  editForm.leave_type = application.leave_type
  editForm.start_date = application.start_date
  editForm.end_date = application.end_date
  editForm.days = application.days
  editForm.reason = application.reason
  editForm.approver_id = application.approver_id
  editForm.emergency_flag = application.emergency_flag
  editForm.attachment_path = application.attachment_path
  
  editDialog.visible = true
}

// 处理编辑表单提交
const handleEditSubmit = async () => {
  if (!editFormRef.value) return
  
  await editFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    editDialog.loading = true
    try {
      // 计算实际天数
      const startDate = new Date(editForm.start_date)
      const endDate = new Date(editForm.end_date)
      const actualDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1
      
      // 准备提交数据
      const submitData = {
        leave_type: editForm.leave_type,
        start_date: editForm.start_date,
        end_date: editForm.end_date,
        reason: editForm.reason,
        approver_id: editForm.approver_id,
        emergency_flag: editForm.emergency_flag,
        attachment_path: editForm.attachment_path
      }
      
      // 调用更新API
      const response = await apiService.attendance.updateLeaveApplication(editForm.id, submitData)
      ElMessage.success('请假申请修改成功')
      editDialog.visible = false
      fetchMyApplications()
    } catch (error) {
      ElMessage.error(error.response?.data?.error || '修改失败')
    } finally {
      editDialog.loading = false
    }
  })
}

// 处理编辑表单上传成功
const handleEditUploadSuccess = (response) => {
  if (response.file_path) {
    editForm.attachment_path = response.file_path
    ElMessage.success('附件上传成功')
  }
}

// 提交申请
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      const submitData = { ...form }
      
      if (enableMultiLevelApproval.value && approvalLevels.value.length > 0) {
        submitData.approval_levels = approvalLevels.value.filter(level => level.approver_id)
        if (submitData.approval_levels.length > 0) {
          submitData.approver_id = submitData.approval_levels[0].approver_id
        }
      }
      
      const response = await apiService.attendance.createLeaveApplication(submitData)
      ElMessage.success('请假申请提交成功')
      handleReset()
      fetchMyApplications()
    } catch (error) {
      ElMessage.error(error.response?.data?.error || '提交失败')
    } finally {
      loading.value = false
    }
  })
}

// 重置表单
const handleReset = () => {
  formRef.value?.resetFields()
  form.days = 1
  enableMultiLevelApproval.value = false
  approvalLevels.value = [
    { level: 1, approver_id: null, status: 'pending' }
  ]
}

onMounted(() => {
  fetchAllUsers()
  fetchMyApplications()
})
</script>

<style scoped>
.leave-application {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.application-form, .my-applications {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.days-hint {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.approver-hint {
  margin-top: 5px;
  color: #909399;
  font-size: 12px;
}

.text-center {
  text-align: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .leave-application {
    padding: 12px;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  .header h1 {
    font-size: 18px;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .el-button {
    width: 100%;
  }

  .application-form {
    margin-bottom: 16px;
  }

  .application-form :deep(.el-card__body) {
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

  .days-hint,
  .emergency-hint {
    font-size: 11px;
    margin-top: 4px;
    display: block;
  }

  .attachment-info {
    flex-wrap: wrap;
    gap: 8px;
  }

  .history-card {
    margin-top: 16px;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
  }

  .pagination {
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

  .el-dialog__header {
    padding: 12px !important;
  }

  .el-dialog__title {
    font-size: 16px !important;
  }

  .el-dialog__body {
    padding: 12px !important;
    max-height: 60vh !important;
    overflow-y: auto !important;
  }

  .el-dialog__footer {
    padding: 12px !important;
  }
}

@media screen and (max-width: 480px) {
  .leave-application {
    padding: 8px;
  }

  .header h1 {
    font-size: 16px;
  }

  .application-form :deep(.el-card__body) {
    padding: 12px;
  }

  .el-form-item__label {
    font-size: 12px;
  }

  .el-table {
    font-size: 10px !important;
  }

  .days-hint,
  .emergency-hint {
    font-size: 10px;
  }
}
</style>