<template>
  <div class="leave-application-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Calendar /></el-icon>
          </div>
          <div class="title-text">
            <h1>请假申请</h1>
            <p class="subtitle">提交和管理您的请假申请</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button @click="$router.back()" class="btn-back">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-total">
            <div class="stat-icon-wrapper stat-icon-wrapper-total">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ totalApplications }}</div>
              <div class="stat-label">请假总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-pending">
            <div class="stat-icon-wrapper stat-icon-wrapper-pending">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ pendingCount }}</div>
              <div class="stat-label">待审批</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-approved">
            <div class="stat-icon-wrapper stat-icon-wrapper-approved">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ approvedCount }}</div>
              <div class="stat-label">已通过</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-rejected">
            <div class="stat-icon-wrapper stat-icon-wrapper-rejected">
              <el-icon><CircleClose /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ rejectedCount }}</div>
              <div class="stat-label">已拒绝</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 本年度请假天数统计 -->
    <div class="year-stats-row animate-fade-in-up delay-200">
      <el-row :gutter="16">
        <el-col :span="24">
          <div class="year-stat-card">
            <div class="year-stat-icon">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="year-stat-content">
              <div class="year-stat-value">{{ currentYearDays }}<span class="year-stat-unit">天</span></div>
              <div class="year-stat-label">本年度请假天数</div>
            </div>
            <div class="year-stat-decoration"></div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 请假申请表单 -->
    <div class="form-section animate-fade-in-up delay-300">
      <el-card class="glass-card application-form" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><EditPen /></el-icon>
              填写请假申请
            </span>
          </div>
        </template>
        <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
          <el-form-item label="请假类型" prop="leave_type">
            <el-select v-model="form.leave_type" placeholder="请选择请假类型" class="form-select">
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
              <el-button type="primary" class="btn-gradient">
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
              <el-button type="text" @click="removeAttachment" class="btn-text-danger">删除</el-button>
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
              class="form-select"
            >
              <el-option
                v-for="user in allUsers"
                :key="user.id"
                :label="`${user.username} (${user.email}) - ${user.position || ''}`"
                :value="user.id"
              />
            </el-select>
            <div class="approver-hint">
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
              <el-tag type="info" class="level-tag">第{{ index + 1 }}级审批</el-tag>
              <el-select
                v-model="level.approver_id"
                placeholder="选择审批人"
                filterable
                clearable
                remote
                :remote-method="searchUsers"
                :loading="loading"
                style="width: 280px; margin-left: 10px;"
                class="form-select"
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
                class="btn-text-danger"
              >
                删除
              </el-button>
            </div>
            <el-button 
              v-if="approvalLevels.length < 3" 
              type="primary" 
              link 
              @click="addApprovalLevel"
              class="btn-link-primary"
            >
              + 添加下一级审批
            </el-button>
            <div class="approver-hint">
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
            <el-button type="primary" @click="handleSubmit" :loading="loading" class="btn-gradient">
              提交申请
            </el-button>
            <el-button @click="handleReset" class="btn-secondary">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 我的请假记录 -->
    <div class="history-section animate-fade-in-up delay-400">
      <el-card class="glass-card my-applications" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><List /></el-icon>
              我的请假记录
            </span>
            <el-button type="primary" @click="fetchMyApplications" class="btn-refresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>

        <el-table :data="myApplications" v-loading="tableLoading" class="custom-table" stripe>
          <el-table-column prop="id" label="申请ID" width="80" align="center">
            <template #default="{ row }">
              <span class="id-badge">{{ row.id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="leave_type" label="请假类型" align="center">
            <template #default="{ row }">
              <el-tag :type="getLeaveTypeTag(row.leave_type)" effect="light" class="type-tag">
                {{ getLeaveTypeText(row.leave_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="start_date" label="开始日期" width="120" align="center" />
          <el-table-column prop="end_date" label="结束日期" width="120" align="center" />
          <el-table-column label="天数" width="80" align="center">
            <template #default="{ row }">
              <span class="days-badge">{{ Math.ceil(row.total_hours / 8) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusTag(row.status)" effect="light" class="status-tag">
                <el-icon v-if="row.status === 'pending'"><Clock /></el-icon>
                <el-icon v-else-if="row.status === 'approved'"><CircleCheck /></el-icon>
                <el-icon v-else><CircleClose /></el-icon>
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="审批人" width="120" align="center">
            <template #default="{ row }">
              <span class="approver-name">{{ getApproverName(row) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="审批时间" width="160" align="center">
            <template #default="{ row }">
              <span class="time-text">{{ row.status === 'approved' ? row.approved_at : '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" align="center" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="viewApplication(row)" class="btn-view">查看</el-button>
              <el-button 
                v-if="row.status === 'pending'" 
                size="small" 
                type="primary" 
                @click="editApplication(row)"
                class="btn-edit"
              >
                修改
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-section">
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
    </div>

    <!-- 修改申请对话框 -->
    <el-dialog
      v-model="editDialog.visible"
      title="修改请假申请"
      width="600px"
      :before-close="() => editDialog.visible = false"
      class="custom-dialog"
    >
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
        <el-form-item label="请假类型" prop="leave_type">
          <el-select v-model="editForm.leave_type" placeholder="请选择请假类型" class="form-select">
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
            <el-button type="primary" class="btn-gradient">
              <el-icon><Upload /></el-icon>
              上传附件
            </el-button>
          </el-upload>
          <div v-if="editForm.attachment_path" class="attachment-info">
            <el-icon><Document /></el-icon>
            {{ getFileName(editForm.attachment_path) }}
            <el-button type="text" @click="editForm.attachment_path = ''" class="btn-text-danger">删除</el-button>
          </div>
        </el-form-item>

        <el-form-item label="审批人" prop="approver_id">
          <el-select v-model="editForm.approver_id" placeholder="请选择审批人" filterable class="form-select">
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
            class="btn-gradient"
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
      class="custom-dialog"
    >
      <el-descriptions :column="1" border v-if="detailDialog.currentApplication" class="detail-descriptions">
        <el-descriptions-item label="申请ID">
          <span class="id-badge">{{ detailDialog.currentApplication.id }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="申请人">
          {{ detailDialog.currentApplication.user_name || detailDialog.currentApplication.user_email }}
        </el-descriptions-item>
        <el-descriptions-item label="请假类型">
          <el-tag :type="getLeaveTypeTag(detailDialog.currentApplication.leave_type)" effect="light">
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
          <span class="days-badge">{{ detailDialog.currentApplication.days }} 天</span>
        </el-descriptions-item>
        <el-descriptions-item label="紧急情况">
          <el-tag :type="detailDialog.currentApplication.emergency_flag ? 'danger' : 'success'" effect="light">
            {{ detailDialog.currentApplication.emergency_flag ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTag(detailDialog.currentApplication.status)" effect="light">
            <el-icon v-if="detailDialog.currentApplication.status === 'pending'"><Clock /></el-icon>
            <el-icon v-else-if="detailDialog.currentApplication.status === 'approved'"><CircleCheck /></el-icon>
            <el-icon v-else><CircleClose /></el-icon>
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
          <a :href="detailDialog.currentApplication.attachment_path" target="_blank" class="attachment-link">
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
import { ref, onMounted, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Refresh, Upload, Document, Calendar, Clock, CircleCheck, CircleClose, EditPen, List, Timer } from '@element-plus/icons-vue'
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

// 统计数据计算
const totalApplications = computed(() => myApplications.value.length)

const pendingCount = computed(() => {
  return myApplications.value.filter(app => app.status === 'pending').length
})

const approvedCount = computed(() => {
  return myApplications.value.filter(app => app.status === 'approved').length
})

const rejectedCount = computed(() => {
  return myApplications.value.filter(app => app.status === 'rejected').length
})

const currentYearDays = computed(() => {
  const currentYear = new Date().getFullYear()
  return myApplications.value
    .filter(app => {
      const appYear = new Date(app.start_date).getFullYear()
      return appYear === currentYear && app.status === 'approved'
    })
    .reduce((sum, app) => sum + (app.days || Math.ceil(app.total_hours / 8) || 0), 0)
})

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
/* 导入设计系统 */
@import '@/styles/design-system.css';

.leave-application-container {
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  min-height: 100%;
}

/* 页面头部 - 玻璃拟态风格 */
.page-header {
  position: relative;
  margin-bottom: 24px;
  padding: 28px 32px;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px -10px rgba(56, 189, 248, 0.4);
}

.page-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at top right, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse at bottom left, rgba(14, 165, 233, 0.3) 0%, transparent 50%);
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
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 20px;
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

.btn-back {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transition: all 0.3s;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

/* 统计卡片区域 */
.stats-row {
  margin-bottom: 16px;
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

.stat-card-total::before { background: linear-gradient(90deg, #7dd3fc, #38bdf8); }
.stat-card-pending::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-approved::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-rejected::before { background: linear-gradient(90deg, #ef4444, #f87171); }

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
  color: #7dd3fc;
  box-shadow: 0 4px 15px -3px rgba(56, 189, 248, 0.4);
}

.stat-icon-wrapper-pending {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-approved {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-rejected {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
  box-shadow: 0 4px 15px -3px rgba(239, 68, 68, 0.4);
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
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-pending .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-approved .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-rejected .stat-value {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
}

/* 本年度请假天数统计 */
.year-stats-row {
  margin-bottom: 24px;
}

.year-stat-card {
  position: relative;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(14, 165, 233, 0.1) 100%);
  border-radius: 16px;
  padding: 24px 28px;
  display: flex;
  align-items: center;
  gap: 20px;
  border: 1px solid rgba(56, 189, 248, 0.2);
  overflow: hidden;
}

.year-stat-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
  box-shadow: 0 8px 20px -4px rgba(56, 189, 248, 0.4);
}

.year-stat-content {
  flex: 1;
}

.year-stat-value {
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
}

.year-stat-unit {
  font-size: 16px;
  font-weight: 500;
  margin-left: 4px;
  color: #64748b;
}

.year-stat-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
}

.year-stat-decoration {
  position: absolute;
  right: -20px;
  top: 50%;
  transform: translateY(-50%);
  width: 120px;
  height: 120px;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.15) 0%, transparent 70%);
  border-radius: 50%;
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
}

.glass-card:hover {
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.12), 0 10px 20px -5px rgba(0, 0, 0, 0.08);
}

/* 表单区域 */
.form-section {
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
  color: #1e293b;
  font-size: 15px;
}

.card-title .el-icon {
  color: #0ea5e9;
  font-size: 18px;
}

.application-form :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.application-form :deep(.el-card__body) {
  padding: 24px;
}

.form-select {
  width: 100%;
}

.days-hint {
  margin-left: 10px;
  color: #64748b;
  font-size: 12px;
}

.emergency-hint {
  margin-left: 10px;
  color: #64748b;
  font-size: 12px;
}

.approver-hint {
  font-size: 12px;
  color: #64748b;
  margin-top: 5px;
}

.text-center {
  text-align: center;
}

.attachment-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  padding: 10px 14px;
  background: rgba(241, 245, 249, 0.8);
  border-radius: 10px;
  font-size: 13px;
}

.approval-level-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.level-tag {
  font-weight: 500;
}

/* 按钮样式 */
.btn-gradient {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.5);
}

.btn-secondary {
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(56, 189, 248, 0.1);
  border-color: #0ea5e9;
  color: #0ea5e9;
}

.btn-refresh {
  transition: all 0.3s;
}

.btn-refresh:hover {
  transform: translateY(-2px);
}

.btn-view, .btn-edit {
  transition: all 0.3s;
}

.btn-view:hover, .btn-edit:hover {
  transform: translateY(-2px);
}

.btn-text-danger {
  color: #ef4444;
}

.btn-text-danger:hover {
  color: #dc2626;
}

.btn-link-primary {
  color: #7dd3fc;
}

.btn-link-primary:hover {
  color: #38bdf8;
}

/* 历史记录区域 */
.history-section {
  margin-bottom: 20px;
}

.my-applications :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

/* 自定义表格 */
.custom-table {
  --el-table-header-bg-color: rgba(241, 245, 249, 0.8);
  --el-table-row-hover-bg-color: rgba(56, 189, 248, 0.05);
}

.custom-table :deep(.el-table__header th) {
  font-weight: 600;
  color: #1e293b;
  background: rgba(241, 245, 249, 0.8);
}

.custom-table :deep(.el-table__row) {
  transition: all 0.3s;
}

.id-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
}

.type-tag, .status-tag {
  font-weight: 500;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.days-badge {
  font-weight: 600;
  color: #7dd3fc;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
}

.approver-name {
  font-size: 13px;
  color: #475569;
}

.time-text {
  font-size: 13px;
  color: #64748b;
}

/* 分页 */
.pagination-section {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

/* 对话框样式 */
.custom-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  padding: 20px 24px;
  margin-right: 0;
}

.custom-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.custom-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

.custom-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.detail-descriptions :deep(.el-descriptions__label) {
  font-weight: 600;
  color: #1e293b;
  background: rgba(241, 245, 249, 0.8);
}

.attachment-link {
  color: #7dd3fc;
  text-decoration: none;
  font-weight: 500;
}

.attachment-link:hover {
  color: #38bdf8;
  text-decoration: underline;
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
.delay-400 { animation-delay: 400ms; }

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .leave-application-container {
    padding: 0;
  }

  .page-header {
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 16px;
  }

  .header-title {
    gap: 14px;
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

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
  }

  .btn-back {
    width: 100%;
  }

  .stats-row {
    margin-bottom: 16px;
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

  .year-stat-card {
    padding: 20px;
  }

  .year-stat-icon {
    width: 48px;
    height: 48px;
    font-size: 24px;
  }

  .year-stat-value {
    font-size: 28px;
  }

  .form-section,
  .history-section {
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

  .approval-level-item {
    flex-wrap: wrap;
    gap: 8px;
  }

  .approval-level-item .el-select {
    width: 100% !important;
    margin-left: 0 !important;
  }

  .days-hint,
  .emergency-hint {
    font-size: 11px;
    margin-top: 4px;
    display: block;
    margin-left: 0;
  }

  .attachment-info {
    flex-wrap: wrap;
  }

  .custom-table :deep(.el-table__header th) {
    font-size: 12px;
  }

  .custom-table :deep(.el-table__row td) {
    font-size: 12px;
  }

  .id-badge {
    font-size: 11px;
    padding: 2px 6px;
  }

  .type-tag,
  .status-tag {
    font-size: 11px;
  }

  .pagination-section {
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

  .custom-dialog {
    width: 95% !important;
    margin: 10px auto !important;
  }

  .custom-dialog :deep(.el-dialog__body) {
    padding: 16px;
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

  .year-stat-value {
    font-size: 24px;
  }

  .application-form :deep(.el-card__body) {
    padding: 12px;
  }

  .el-form-item__label {
    font-size: 12px;
  }

  .custom-table :deep(.el-table__row td) {
    font-size: 11px;
  }
}
</style>
