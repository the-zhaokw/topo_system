<template>
  <div class="bug-detail" v-loading="loading">
    <div v-if="bug && bug.id">
    <!-- 头部操作栏 -->
    <div class="bug-detail-header">
      <div class="header-left">
        <el-button @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>{{ bug.title }}</h2>
        <el-tag :type="getStatusType(bug.status)" size="large" class="status-tag">
          {{ getStatusText(bug.status) }}
          <span v-if="currentStatusDuration" class="status-duration">
            ({{ currentStatusDuration }})
          </span>
        </el-tag>
      </div>
      <div class="header-right">
        <!-- 状态流转按钮组 -->
        <el-button-group v-if="availableTransitions.length > 0" class="transition-buttons">
          <el-button 
            v-for="transition in availableTransitions" 
            :key="transition.to"
            :type="transition.type"
            @click="handleStatusTransition(transition)"
          >
            {{ transition.label }}
          </el-button>
        </el-button-group>
        
        <el-button v-if="canDelete" type="danger" @click="handleDelete">
          <el-icon><Delete /></el-icon>
          删除
        </el-button>
        <el-button type="primary" @click="handleEdit">
          <el-icon><Edit /></el-icon>
          编辑Bug
        </el-button>
      </div>
    </div>

    <!-- 工作流建议面板 -->
    <el-card class="workflow-suggestion-card" v-if="workflowSuggestions.length > 0">
      <template #header>
        <div class="card-header">
          <span>
            <el-icon><InfoFilled /></el-icon>
            工作流建议
          </span>
        </div>
      </template>
      <div class="workflow-suggestions">
        <div 
          v-for="(suggestion, index) in workflowSuggestions" 
          :key="index"
          class="suggestion-item"
          :class="suggestion.type"
        >
          <div class="suggestion-header">
            <el-tag :type="suggestion.type === 'recommended' ? 'success' : suggestion.type === 'warning' ? 'warning' : 'info'" size="small">
              {{ suggestion.type === 'recommended' ? '建议' : suggestion.type === 'warning' ? '注意' : '提示' }}
            </el-tag>
            <span class="suggestion-title">{{ suggestion.title }}</span>
          </div>
          <div class="suggestion-content">{{ suggestion.description }}</div>
          <div class="suggestion-actions" v-if="suggestion.actions && suggestion.actions.length > 0">
            <el-button 
              v-for="action in suggestion.actions" 
              :key="action.to"
              :type="action.btnType"
              size="small"
              @click="handleStatusTransition({ to: action.to, label: action.label })"
            >
              {{ action.label }}
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 状态流转对话框 -->
    <el-dialog v-model="showTransitionDialog" title="状态变更" width="500px">
      <el-form label-width="100px">
        <el-form-item label="当前状态">
          <el-tag :type="getStatusType(bug.status)">{{ getStatusText(bug.status) }}</el-tag>
        </el-form-item>
        <el-form-item label="目标状态">
          <el-tag :type="getStatusType(transitionForm.newStatus)">{{ getStatusText(transitionForm.newStatus) }}</el-tag>
        </el-form-item>
        <el-form-item label="修复说明" v-if="needResolution">
          <el-input
            v-model="transitionForm.resolution"
            type="textarea"
            :rows="4"
            placeholder="请输入修复说明（必填）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTransitionDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmTransition" :loading="transitionLoading">确认</el-button>
      </template>
    </el-dialog>

    <!-- 附件预览对话框 -->
    <el-dialog v-model="showPreviewDialog" title="预览附件" width="800px" class="preview-dialog" @close="handlePreviewClose">
      <div class="preview-content" v-loading="previewLoading">
        <img v-if="isImageFile(previewFile)" :src="previewUrl" class="preview-image" />
        <iframe v-else-if="isPdfFile(previewFile)" :src="previewUrl" class="preview-pdf" />
        <div v-else class="preview-unsupported">
          <el-icon size="64"><Document /></el-icon>
          <p>该文件类型暂不支持预览</p>
          <p class="preview-filename">{{ previewFile?.filename }}</p>
        </div>
      </div>
    </el-dialog>
    
    <!-- Bug基本信息 -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
            </div>
          </template>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="ID">{{ bug.id }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(bug.status)" size="small">
                {{ getStatusText(bug.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="严重程度">
              <el-tag :type="getSeverityType(bug.severity)" size="small">
                {{ getSeverityText(bug.severity) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="优先级">
              <el-tag :type="getPriorityType(bug.priority)" size="small">
                {{ getPriorityText(bug.priority) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="项目">
              <span class="clickable-link" @click="goToProject(bug.project_id)">{{ bug.project_name }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="创建人">
              <span class="clickable-link" @click="goToUser(bug.reported_by)">{{ bug.creator_name }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(bug.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ formatDate(bug.updated_at) }}</el-descriptions-item>
            <el-descriptions-item label="归属版本">{{ bug.version || '-' }}</el-descriptions-item>
            <el-descriptions-item label="问题类型">{{ bug.issue_type || '-' }}</el-descriptions-item>
            <el-descriptions-item label="重现频率">{{ bug.reproduce_frequency || '-' }}</el-descriptions-item>
            <el-descriptions-item label="发现构建">{{ bug.found_build || '-' }}</el-descriptions-item>
            <el-descriptions-item label="测试版本">{{ bug.test_version || '-' }}</el-descriptions-item>
            <el-descriptions-item label="模块">{{ bug.module || '-' }}</el-descriptions-item>
            <el-descriptions-item label="客户MR编号">{{ bug.customer_mr_number || '-' }}</el-descriptions-item>
            <el-descriptions-item label="计划解决版本">{{ bug.plan_resolve_version || '-' }}</el-descriptions-item>
            <el-descriptions-item label="解决构建">{{ bug.resolve_build || '-' }}</el-descriptions-item>
            <el-descriptions-item label="解决者">
              <span v-if="bug.resolver_name">
                <span class="clickable-link" @click="goToUser(bug.resolver_id)">{{ bug.resolver_name }}</span>
                <el-tag v-if="bug.resolved_at" size="small" type="info">
                  {{ formatDate(bug.resolved_at) }}
                </el-tag>
              </span>
              <div v-else>-</div>
            </el-descriptions-item>
            <el-descriptions-item label="验证者">
              <span v-if="bug.verifier_name">
                <span class="clickable-link" @click="goToUser(bug.verifier_id)">{{ bug.verifier_name }}</span>
                <el-tag v-if="bug.verified_at" size="small" type="info">
                  {{ formatDate(bug.verified_at) }}
                </el-tag>
              </span>
              <div v-else>-</div>
            </el-descriptions-item>
            <el-descriptions-item label="期限">{{ bug.deadline ? formatDate(bug.deadline) : '-' }}</el-descriptions-item>
            <el-descriptions-item label="重新打开次数">{{ bug.reopened_count || 0 }}</el-descriptions-item>
            <el-descriptions-item label="预计工时">{{ bug.estimated_hours ? bug.estimated_hours + ' 小时' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="实际工时">{{ bug.actual_hours ? bug.actual_hours + ' 小时' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="关联测试用例">{{ bug.test_case_id || '-' }}</el-descriptions-item>
            <el-descriptions-item label="相关Bug">{{ bug.related_bug_id ? `#${bug.related_bug_id}` : '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
        
        <!-- 状态时间线 -->
        <el-card class="timeline-card">
          <template #header>
            <div class="card-header">
              <span>状态时间线</span>
            </div>
          </template>

          <el-timeline v-if="statusTimeline.length > 0">
            <el-timeline-item
              v-for="item in statusTimeline"
              :key="item.id"
              :timestamp="formatDate(item.timestamp)"
              placement="top"
            >
              <el-card>
                <h4>{{ item.title }}</h4>
                <p>{{ item.description }}</p>
                <el-tag v-if="item.type === 'resolved'" size="small" type="success">已解决</el-tag>
                <el-tag v-if="item.type === 'reopened'" size="small" type="warning">重新打开</el-tag>
                <el-tag v-if="item.type === 'closed'" size="small" type="info">已关闭</el-tag>
                <el-tag v-if="item.type === 'in_progress'" size="small" type="primary">处理中</el-tag>
              </el-card>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无状态变更记录" />
        </el-card>
        
        <!-- Bug 活动记录 -->
        <el-card class="field-changes-card" v-if="fieldChangeActivities.length > 0">
          <template #header>
            <div class="card-header">
              <span>Bug 活动记录</span>
              <el-tag size="small" type="info">{{ fieldChangeActivities.length }} 条记录</el-tag>
            </div>
          </template>
          
          <div class="field-changes-list">
            <div 
              v-for="activity in fieldChangeActivities" 
              :key="activity.id" 
              class="field-change-item"
            >
              <div class="field-change-header">
                <div class="header-left">
                  <span class="field-change-action">{{ getActivityActionText(activity.action) }}</span>
                  <span class="field-change-time" :title="formatFullDate(activity.created_at)">
                    {{ formatActivityDate(activity.created_at) }}
                  </span>
                </div>
                <div class="header-right">
                  <el-tag size="small" type="primary">{{ activity.user_name || '未知用户' }}</el-tag>
                </div>
              </div>
              <div v-if="activity.field_changes && activity.field_changes.length > 0" class="field-changes-detail">
                <div class="changes-summary">
                  <el-icon><Edit /></el-icon>
                  <span>共修改 {{ activity.field_changes.length }} 个字段</span>
                </div>
                <div 
                  v-for="(change, index) in activity.field_changes" 
                  :key="index" 
                  class="field-change-row"
                >
                  <div class="field-label-wrapper">
                    <span class="field-name">{{ change.field_label || change.field }}</span>
                  </div>
                  <div class="field-value-wrapper">
                    <span class="field-old-value" :title="change.old_value">{{ change.old_value || '空' }}</span>
                    <span class="field-arrow">→</span>
                    <span class="field-new-value" :title="change.new_value">{{ change.new_value || '空' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- Bug描述 -->
        <el-card class="description-card">
          <template #header>
            <div class="card-header">
              <span>Bug描述</span>
            </div>
          </template>
          
          <div class="description-content">
            <pre>{{ bug.description }}</pre>
          </div>
        </el-card>
        
        <!-- 重现步骤 -->
        <el-card class="steps-card" v-if="bug.steps_to_reproduce">
          <template #header>
            <div class="card-header">
              <span>重现步骤</span>
            </div>
          </template>
          
          <div class="steps-content">
            <pre>{{ bug.steps_to_reproduce }}</pre>
          </div>
        </el-card>
        
        <!-- 预期结果和实际结果 -->
        <el-row :gutter="20" v-if="bug.expected_result || bug.actual_result">
          <el-col :span="12">
            <el-card class="result-card">
              <template #header>
                <div class="card-header">
                  <span>预期结果</span>
                </div>
              </template>
              
              <div class="result-content">
                <pre>{{ bug.expected_result || '无' }}</pre>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card class="result-card">
              <template #header>
                <div class="card-header">
                  <span>实际结果</span>
                </div>
              </template>
              
              <div class="result-content">
                <pre>{{ bug.actual_result || '无' }}</pre>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-col>
      
      <el-col :span="8">
        <!-- 标签 -->
        <el-card class="tags-card">
          <template #header>
            <div class="card-header">
              <span>标签</span>
            </div>
          </template>
          
          <div class="tags-content">
            <el-tag 
              v-for="tag in parsedTags" 
              :key="tag" 
              class="tag-item"
              type="primary"
            >
              {{ tag }}
            </el-tag>
            <div v-if="!parsedTags || parsedTags.length === 0" class="no-tags">
              暂无标签
            </div>
          </div>
        </el-card>
        
        <!-- 附件 -->
        <el-card class="attachments-card">
          <template #header>
            <div class="card-header attachments-header">
              <span class="header-title">附件</span>
              <div class="upload-actions">
                <el-upload
                  ref="uploadRef"
                  :http-request="uploadFile"
                  :before-upload="beforeUpload"
                  :show-file-list="false"
                  :multiple="true"
                  :limit="10"
                  accept="*"
                >
                  <el-button type="primary" size="small" :disabled="!canEdit">
                    <el-icon><Upload /></el-icon>
                    选择文件
                  </el-button>
                </el-upload>
                <div class="upload-tip-container">
                  <span class="upload-tip">支持多文件上传，单个文件最大 50MB</span>
                </div>
              </div>
            </div>
          </template>
          
          <div class="attachments-content">
            <div
              v-for="uploading in uploadingFiles"
              :key="uploading.id"
              class="attachment-item uploading"
            >
              <div class="attachment-icon">
                <el-icon class="uploading-icon"><Loading /></el-icon>
              </div>
              <div class="attachment-info">
                <div class="attachment-name">{{ uploading.name }}</div>
                <div class="attachment-meta">
                  <el-progress :percentage="uploading.percent" :stroke-width="4" />
                </div>
              </div>
            </div>
            <div
              v-for="attachment in bug.attachments"
              :key="attachment.id"
              class="attachment-item"
            >
              <div class="attachment-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="attachment-info">
                <div class="attachment-name">{{ attachment.filename }}</div>
                <div class="attachment-meta">
                  <span class="attachment-size">{{ formatFileSize(attachment.file_size) }}</span>
                  <span class="attachment-uploader">上传者：{{ getUploaderName(attachment) }}</span>
                  <span class="attachment-time">{{ formatDate(attachment.created_at) }}</span>
                </div>
              </div>
              <div class="attachment-actions">
                <el-button
                  type="primary"
                  link
                  size="small"
                  @click="previewAttachment(attachment)"
                  v-if="canPreview(attachment)"
                >
                  预览
                </el-button>
                <el-button type="primary" link size="small" @click="downloadAttachment(attachment)">
                  下载
                </el-button>
                <el-button
                  type="danger"
                  link
                  size="small"
                  @click="deleteAttachment(attachment)"
                  v-if="canDeleteAttachment(attachment)"
                  :loading="deletingAttachmentId === attachment.id"
                >
                  删除
                </el-button>
              </div>
            </div>
            <div v-if="!bug.attachments || bug.attachments.length === 0" class="no-attachments">
              暂无附件，请点击"选择文件"按钮添加附件
            </div>
          </div>
        </el-card>
        
        <!-- 评论区域 -->
        <el-card class="comments-card">
          <template #header>
            <div class="card-header">
              <span>评论</span>
            </div>
          </template>
          
          <div class="comment-input">
            <el-input
              v-model="newComment"
              type="textarea"
              :rows="3"
              placeholder="请输入评论..."
              maxlength="500"
              show-word-limit
            />
            <div class="comment-actions">
              <el-button type="primary" @click="addComment" :disabled="!newComment.trim()">
                发表评论
              </el-button>
            </div>
          </div>
          
          <div class="comments-list">
            <div 
              v-for="comment in comments" 
              :key="comment.id" 
              class="comment-item"
            >
              <div class="comment-header">
                <span class="comment-author">{{ comment.author_name }}</span>
                <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
              </div>
              <div class="comment-content">
                {{ comment.content }}
              </div>
            </div>
            
            <div v-if="comments.length === 0" class="no-comments">
              暂无评论
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Edit, Delete, InfoFilled, Document, Upload, Right, Loading } from '@element-plus/icons-vue'
import { useBugStore } from '@/stores/bug'
import { useUserStore } from '@/stores/user'
import { systemTimeService } from '@/services/systemTimeService'
import { apiService, api as axios } from '@/services/api'

const route = useRoute()
const router = useRouter()
const bugStore = useBugStore()
const userStore = useUserStore()

const loading = ref(false)
const bug = ref({
  id: null,
  title: '',
  status: '',
  severity: '',
  priority: '',
  project_id: null,
  project_name: '',
  reported_by: null,
  creator_name: '',
  created_at: null,
  updated_at: null,
  version: '',
  issue_type: '',
  reproduce_frequency: '',
  found_build: '',
  test_version: '',
  module: '',
  customer_mr_number: '',
  plan_resolve_version: '',
  resolve_build: '',
  resolver_id: null,
  resolver_name: '',
  resolved_at: null,
  verifier_id: null,
  verifier_name: '',
  verified_at: null,
  closed_at: null,
  deadline: null,
  reopened_count: 0,
  estimated_hours: null,
  actual_hours: null,
  test_case_id: null,
  related_bug_id: null,
  description: '',
  steps_to_reproduce: '',
  expected_result: '',
  actual_result: '',
  tags: [],
  attachments: [],
  resolution: ''
})
const comments = ref([])
const newComment = ref('')
const activities = ref([])
const uploadRef = ref(null)
const uploadingFiles = ref([])
const deletingAttachmentId = ref(null)
const showPreviewDialog = ref(false)
const previewUrl = ref('')
const previewFile = ref(null)
const previewLoading = ref(false)

// 上传相关
const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token')
  return {
    'Authorization': `Bearer ${token}`
  }
})

// 过滤出有字段变更的活动记录（用于 Bug 活动记录）
const fieldChangeActivities = computed(() => {
  return activities.value.filter(activity => {
    // 确保 field_changes 存在且是数组，并且长度大于 0
    if (!activity.field_changes) {
      return false
    }
    if (Array.isArray(activity.field_changes)) {
      return activity.field_changes.length > 0
    }
    return false
  })
})

// 状态时间线 - 从Activity记录中提取所有状态变更
const statusTimeline = computed(() => {
  const timeline = []

  // 1. 添加创建记录
  timeline.push({
    id: 'creation',
    timestamp: bug.value?.created_at,
    title: 'Bug创建',
    description: `由 ${bug.value?.creator_name || '未知'} 创建`,
    type: 'creation'
  })

  // 2. 从Activity记录中提取状态变更
  activities.value.forEach(activity => {
    if (activity.action === 'update_bug' || activity.action === 'bug_status_transition') {
      let fieldChanges = activity.field_changes

      // 兼容处理：如果field_changes是字符串，尝试解析为数组
      if (typeof fieldChanges === 'string') {
        try {
          fieldChanges = JSON.parse(fieldChanges)
        } catch (e) {
          fieldChanges = []
        }
      }

      if (!Array.isArray(fieldChanges)) {
        fieldChanges = []
      }

      // 检查是否有状态变更
      const hasStatusChange = fieldChanges.some(
        change => change.field === 'status'
      )
      if (hasStatusChange) {
        const statusChange = fieldChanges.find(c => c.field === 'status')
        const oldStatus = statusChange.old_value
        const newStatus = statusChange.new_value
        const statusTitles = {
          'new': '新建',
          'in_progress': '开始处理',
          'resolved': '已解决',
          'verified': '已验证',
          'closed': '已关闭',
          'reopened': '重新打开'
        }
        timeline.push({
          id: activity.id,
          timestamp: activity.created_at,
          title: statusTitles[newStatus] || newStatus,
          description: `由 ${activity.user_name || '未知'} 变更: ${statusTitles[oldStatus] || oldStatus} → ${statusTitles[newStatus] || newStatus}`,
          type: newStatus,
          oldStatus,
          newStatus
        })
      }
    }
  })

  // 3. 如果当前状态是reopened且没有在activities中找到，添加重新打开记录
  if (bug.value?.status === 'reopened') {
    const hasReopenedInTimeline = timeline.some(item => item.newStatus === 'reopened')
    if (!hasReopenedInTimeline) {
      timeline.push({
        id: 'reopened-current',
        timestamp: bug.value.updated_at,
        title: '重新打开',
        description: `Bug已被重新打开，需要重新处理。重新打开次数: ${bug.value.reopened_count || 0}`,
        type: 'reopened'
      })
    }
  }

  // 按时间排序（升序）
  timeline.sort((a, b) => {
    if (!a.timestamp) return 1
    if (!b.timestamp) return -1
    return new Date(a.timestamp) - new Date(b.timestamp)
  })

  return timeline
})

// 状态流转相关
const showTransitionDialog = ref(false)
const transitionLoading = ref(false)
const transitionForm = ref({
  newStatus: '',
  resolution: ''
})
const needResolution = computed(() => {
  if (!bug.value?.id) return false
  return bug.value.status === 'in_progress' && transitionForm.value.newStatus === 'resolved'
})

const bugId = computed(() => route.params.id)
const currentUser = computed(() => userStore.currentUser)

// 解析标签数据，后端已返回数组格式，这里做兼容处理
const parsedTags = computed(() => {
  const tags = bug.value.tags
  if (!tags) return []
  if (Array.isArray(tags)) return tags
  if (typeof tags === 'string') {
    // 兼容处理：如果后端返回的是JSON字符串格式
    try {
      const parsed = JSON.parse(tags)
      if (Array.isArray(parsed)) {
        return parsed
      }
    } catch {
      // JSON解析失败，尝试逗号分隔格式
    }
    return tags.split(',').map(t => t.trim()).filter(t => t)
  }
  return []
})

// 计算当前状态持续时间
const currentStatusDuration = computed(() => {
  if (!bug.value?.updated_at) return ''

  const now = systemTimeService.getServerTime()
  const updated = new Date(bug.value.updated_at)
  const diffMs = now - updated

  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))

  if (diffDays > 0) {
    return `${diffDays}天${diffHours}小时`
  } else if (diffHours > 0) {
    return `${diffHours}小时${diffMinutes}分钟`
  } else {
    return `${diffMinutes}分钟`
  }
})

// 权限检查
const canEdit = computed(() => {
  if (!bug.value?.id) return false
  // 已关闭的 Bug 不能编辑
  if (bug.value.status === 'closed') return false
  // 管理员或创建者可以编辑
  const user = currentUser.value
  if (!user) return false
  if (user.is_super_admin) return true
  if (user.position === '管理员' || user.position?.includes('经理')) return true
  return bug.value.reported_by === currentUser.value?.id
})

const canDelete = computed(() => {
  if (!bug.value?.id) return false
  const user = currentUser.value
  if (!user) return false
  if (user.is_super_admin) return true
  if (user.position === '管理员' || user.position?.includes('经理')) return true
  return bug.value.reported_by === currentUser.value?.id
})

// 可用的状态流转
const availableTransitions = computed(() => {
  if (!bug.value?.id) return []

  const transitions = []
  const status = bug.value.status
  const user = currentUser.value
  if (!user) return []
  
  const position = user.position
  const isSuperAdmin = user.is_super_admin
  const isManager = position === '管理员' || position?.includes('经理') || position === '项目经理'
  const isDeveloper = position === '软件工程师'
  const isTester = position === '测试工程师'

  if (isSuperAdmin || isManager) {
    if (status === 'new') {
      transitions.push({ to: 'in_progress', label: '开始处理', type: 'primary' })
    }
    if (status === 'in_progress') {
      transitions.push({ to: 'resolved', label: '标记解决', type: 'success' })
    }
    if (status === 'resolved') {
      transitions.push({ to: 'closed', label: '关闭', type: 'success' })
      transitions.push({ to: 'reopened', label: '重新打开', type: 'warning' })
    }
    if (status === 'closed') {
      transitions.push({ to: 'reopened', label: '重新打开', type: 'warning' })
    }
    if (status === 'reopened') {
      transitions.push({ to: 'in_progress', label: '开始处理', type: 'primary' })
    }
  }

  if (isDeveloper) {
    if (status === 'new') {
      transitions.push({ to: 'in_progress', label: '开始处理', type: 'primary' })
    }
    if (status === 'in_progress') {
      transitions.push({ to: 'resolved', label: '标记解决', type: 'success' })
    }
    if (status === 'reopened') {
      transitions.push({ to: 'in_progress', label: '开始处理', type: 'primary' })
    }
  }

  if (isTester) {
    if (status === 'resolved') {
      transitions.push({ to: 'closed', label: '关闭', type: 'success' })
      transitions.push({ to: 'reopened', label: '重新打开', type: 'warning' })
    }
    if (status === 'closed') {
      transitions.push({ to: 'reopened', label: '重新打开', type: 'warning' })
    }
  }

  return transitions
})

// 工作流建议
const workflowSuggestions = computed(() => {
  if (!bug.value?.id) return []

  const suggestions = []
  const status = bug.value.status
  const severity = bug.value.severity
  const priority = bug.value.priority
  const user = currentUser.value
  const position = user?.position
  const isSuperAdmin = user?.is_super_admin
  const isManager = position === '管理员' || position?.includes('经理') || position === '项目经理'
  const isDeveloper = position === '软件工程师'
  const isTester = position === '测试工程师'

  if (status === 'new') {
    suggestions.push({
      type: 'info',
      title: 'Bug 新建',
      description: '此 Bug 已创建，等待处理。',
      actions: []
    })

    if (severity === 'Blocker' || severity === 'Critical') {
      suggestions.push({
        type: 'recommended',
        title: '高严重程度 Bug',
        description: '这是一个阻塞性或严重级别的问题，建议优先处理。',
        actions: []
      })
    }

    if (isSuperAdmin || isManager || isDeveloper) {
      suggestions.push({
        type: 'recommended',
        title: '开始处理 Bug',
        description: '您可以开始处理此 Bug，将其状态变更为"进行中"。',
        actions: [{ to: 'in_progress', label: '开始处理', btnType: 'primary' }]
      })
    }
  }

  if (status === 'in_progress') {
    suggestions.push({
      type: 'info',
      title: 'Bug 处理中',
      description: '此 Bug 正在处理中。',
      actions: []
    })

    if (isManager || isDeveloper) {
      suggestions.push({
        type: 'recommended',
        title: '提交解决方案',
        description: 'Bug 修复完成后，请提交解决方案并将状态变更为"已解决"。',
        actions: [{ to: 'resolved', label: '标记解决', btnType: 'success' }]
      })
    }
  }

  if (status === 'resolved') {
    if (isTester || isSuperAdmin || isManager) {
      suggestions.push({
        type: 'recommended',
        title: '验证修复',
        description: `请验证 Bug 修复是否有效，如有效请关闭此 Bug。${bug.resolver_name ? `此 Bug 由 ${bug.resolver_name} 解决。` : ''}${bug.resolved_at ? `解决时间：${formatDate(bug.resolved_at)}。` : ''}${bug.resolution ? `解决方案：${bug.resolution.substring(0, 100)}${bug.resolution.length > 100 ? '...' : ''}` : ''}`,
        actions: [
          { to: 'closed', label: '关闭', btnType: 'success' },
          { to: 'reopened', label: '重新打开', btnType: 'warning' }
        ]
      })
    }
  }

  if (status === 'closed') {
    suggestions.push({
      type: 'info',
      title: 'Bug已关闭',
      description: '此Bug已关闭。如需重新打开，请联系测试人员或项目经理。',
      actions: [{ to: 'reopened', label: '重新打开', btnType: 'warning' }]
    })
  }

  if (status === 'reopened') {
    if (isManager || isDeveloper) {
      suggestions.push({
        type: 'recommended',
        title: '重新处理Bug',
        description: '此Bug被重新打开，请检查问题并重新修复。',
        actions: [{ to: 'in_progress', label: '开始处理', btnType: 'primary' }]
      })
    }
  }

  if (priority === 'Highest' || priority === 'High') {
    const hasHighPrioritySuggestion = suggestions.some(s => s.title.includes('优先级'))
    if (!hasHighPrioritySuggestion) {
      suggestions.push({
        type: 'warning',
        title: '高优先级Bug',
        description: '这是一个高优先级问题，请优先处理。',
        actions: []
      })
    }
  }

  return suggestions
})

// 获取 Bug 详情
const fetchBugDetail = async () => {
  // 验证 bugId 是否为有效数字
  const id = bugId.value
  if (!id || isNaN(Number(id))) {
    console.error('无效的 Bug ID:', id)
    ElMessage.error('无效的 Bug ID')
    loading.value = false
    return
  }
  
  loading.value = true
  try {
    const bugResult = await bugStore.fetchBug(id)
    if (bugResult.success && bugResult.bug) {
      bug.value = bugResult.bug
      
      // 后端已经返回 attachments 数组，不需要再转换
      // 如果没有 attachments 字段，初始化为空数组
      if (!bug.value.attachments) {
        bug.value.attachments = []
      }
    } else {
      ElMessage.error(bugResult.error || '获取 Bug 详情失败')
      return
    }
    
    // 获取评论
    await fetchComments()
  } catch (error) {
    console.error('获取 Bug 详情失败:', error)
    ElMessage.error('获取 Bug 详情失败')
  } finally {
    loading.value = false
  }
}

// 获取评论
const fetchComments = async () => {
  try {
    const result = await bugStore.fetchComments(bugId.value)
    if (result.success) {
      comments.value = result.comments || []
    } else {
      comments.value = []
    }
  } catch (error) {
    console.error('获取评论失败:', error)
    comments.value = []
  }
}

// 获取活动记录
const fetchActivities = async () => {
  try {
    const response = await apiService.activities.getByResource('bug', bugId.value)
    if (Array.isArray(response)) {
      activities.value = response
    } else if (response && response.activities) {
      activities.value = response.activities
    } else {
      activities.value = []
    }
  } catch (error) {
    console.error('获取活动记录失败:', error)
    activities.value = []
  }
}

// 添加评论
const addComment = async () => {
  if (!newComment.value.trim()) return
  
  try {
    const result = await bugStore.addComment(bugId.value, {
      content: newComment.value.trim()
    })
    
    if (result.success) {
      ElMessage.success('评论发表成功')
      newComment.value = ''
      await fetchComments()
    } else {
      ElMessage.error(result.error || '发表评论失败')
    }
  } catch (error) {
    console.error('发表评论失败:', error)
    ElMessage.error(error.response?.data?.error || '发表评论失败')
  }
}

// 状态流转处理
const handleStatusTransition = (transition) => {
  transitionForm.value.newStatus = transition.to
  transitionForm.value.resolution = ''
  showTransitionDialog.value = true
}

// 确认状态流转
const confirmTransition = async () => {
  if (needResolution.value && !transitionForm.value.resolution.trim()) {
    ElMessage.warning('请填写修复说明')
    return
  }
  
  transitionLoading.value = true
  try {
    const response = await apiService.bugs.transitionBug(bugId.value, {
      status: transitionForm.value.newStatus,
      resolution: transitionForm.value.resolution
    })
    
    ElMessage.success(response.message || '状态变更成功')
    showTransitionDialog.value = false
    await fetchBugDetail() // 重新获取所有数据，包括活动记录
  } catch (error) {
    console.error('状态变更失败:', error)
    const errorMsg = error.response?.data?.message || error.response?.data?.error || error.message || '状态变更失败'
    ElMessage.error(errorMsg)
  } finally {
    transitionLoading.value = false
  }
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
    if (error.response?.status === 404) {
      ElMessage.warning('附件不存在或已被删除，正在刷新列表')
      fetchBugDetail()
    } else {
      ElMessage.error('下载附件失败')
    }
  }
}

// 判断文件是否为图片
const isImageFile = (attachment) => {
  if (!attachment) return false
  const mimeType = attachment.mime_type || ''
  const filename = attachment.filename || ''
  return mimeType.startsWith('image/') ||
         /\.(jpg|jpeg|png|gif|webp|bmp|svg)$/i.test(filename)
}

// 判断文件是否为PDF
const isPdfFile = (attachment) => {
  if (!attachment) return false
  const mimeType = attachment.mime_type || ''
  const filename = attachment.filename || ''
  return mimeType === 'application/pdf' || /\.pdf$/i.test(filename)
}

// 判断附件是否可预览
const canPreview = (attachment) => {
  return isImageFile(attachment) || isPdfFile(attachment)
}

// 预览附件
const previewAttachment = async (attachment) => {
  previewFile.value = attachment
  previewUrl.value = ''
  showPreviewDialog.value = true
  previewLoading.value = true

  try {
    const response = await apiService.bugs.getAttachmentUrl(bugId.value, attachment.id)
    previewUrl.value = window.URL.createObjectURL(new Blob([response.data], { type: attachment.mime_type || 'application/octet-stream' }))
  } catch (error) {
    console.error('预览附件失败:', error)
    ElMessage.error('预览附件失败')
    showPreviewDialog.value = false
  } finally {
    previewLoading.value = false
  }
}

// 关闭预览对话框时清理资源
const handlePreviewClose = () => {
  if (previewUrl.value) {
    window.URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = ''
  }
  previewFile.value = null
}

// 上传附件成功处理
const handleUploadSuccess = (response, file, fileList) => {
  console.log('Upload success response:', response)
  if (response && response.attachment) {
    ElMessage.success('附件上传成功')
    fetchBugDetail()
  } else {
    const errorMsg = response?.message || response?.msg || response?.error || '上传失败'
    ElMessage.error(errorMsg)
  }
}

// 上传附件失败处理
const handleUploadError = (error, file, fileList) => {
  console.error('上传附件失败:', error)

  let errorMsg = '上传附件失败'
  if (error.response) {
    const errorData = error.response.data
    if (typeof errorData === 'string') {
      try {
        const parsed = JSON.parse(errorData)
        errorMsg = parsed?.message || parsed?.msg || parsed?.error || errorMsg
      } catch {
        errorMsg = errorData || errorMsg
      }
    } else {
      errorMsg = errorData?.message || errorData?.msg || errorData?.error || errorMsg
    }

    if (error.response.status === 401) {
      errorMsg = '未授权，请重新登录'
    } else if (error.response.status === 403) {
      errorMsg = '无权上传附件'
    } else if (error.response.status === 404) {
      errorMsg = 'Bug 不存在'
    } else if (error.response.status === 400 && !errorData?.message) {
      errorMsg = '上传请求无效'
    }
  } else if (error.message) {
    errorMsg = error.message
  }

  ElMessage.error(errorMsg)
}

// 自定义上传方法
const uploadFile = async (options) => {
  const { file, onSuccess, onError } = options

  const formData = new FormData()
  formData.append('file', file)

  const uploadId = Date.now() + Math.random()
  uploadingFiles.value.push({ id: uploadId, name: file.name, percent: 0 })

  try {
    const response = await apiService.bugs.uploadAttachment(bugId.value, formData)

    uploadingFiles.value = uploadingFiles.value.filter(f => f.id !== uploadId)

    if (onSuccess && typeof onSuccess === 'function') {
      onSuccess(response.data?.attachment || response)
    }
    ElMessage.success('附件上传成功')
    fetchBugDetail()
  } catch (error) {
    console.error('Upload error:', error)
    uploadingFiles.value = uploadingFiles.value.filter(f => f.id !== uploadId)
    
    let errorMsg = '上传附件失败'
    if (error.response) {
      const errorData = error.response.data
      if (typeof errorData === 'string') {
        try {
          const parsed = JSON.parse(errorData)
          errorMsg = parsed?.message || parsed?.error || errorMsg
        } catch {
          errorMsg = errorData || errorMsg
        }
      } else {
        errorMsg = errorData?.message || errorData?.error || errorMsg
      }
      
      if (error.response.status === 401) {
        errorMsg = '未授权，请重新登录'
      } else if (error.response.status === 403) {
        errorMsg = '无权上传附件'
      } else if (error.response.status === 404) {
        errorMsg = 'Bug 不存在'
      } else if (error.response.status === 400 && !errorData?.message) {
        errorMsg = '上传请求无效'
      }
    } else if (error.message) {
      errorMsg = error.message
    }
    
    if (onError && typeof onError === 'function') {
      onError(new Error(errorMsg))
    }
    ElMessage.error(errorMsg)
  }
}

// 上传前验证
const beforeUpload = (file) => {
  const maxSize = 50 * 1024 * 1024 // 50MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  return true
}

// 删除附件
const deleteAttachment = async (attachment) => {
  if (deletingAttachmentId.value === attachment.id) {
    return
  }

  const attachmentIndex = bug.value.attachments.findIndex(a => a.id === attachment.id)
  if (attachmentIndex === -1) {
    ElMessage.warning('附件不存在')
    return
  }

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
    const response = await apiService.bugs.deleteAttachment(bugId.value, attachment.id)

    const responseData = response.data || response
    if (responseData.success) {
      ElMessage.success('附件删除成功')
      bug.value.attachments.splice(attachmentIndex, 1)
      fetchBugDetail()
    } else {
      ElMessage.error(responseData.message || '删除失败')
      fetchBugDetail()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除附件失败:', error)
      if (error.response?.status === 404) {
        ElMessage.warning('附件已被删除或不存在，正在刷新列表')
        bug.value.attachments.splice(attachmentIndex, 1)
        fetchBugDetail()
      } else {
        ElMessage.error('删除附件失败')
        fetchBugDetail()
      }
    }
  } finally {
    deletingAttachmentId.value = null
  }
}

// 判断是否可以删除附件
const canDeleteAttachment = (attachment) => {
  if (!canEdit.value) return false
  const currentUserId = userStore.currentUser?.id
  const user = userStore.currentUser
  if (!user) return false
  if (user.is_super_admin) return true
  if (user.position === '管理员' || user.position?.includes('经理')) return true
  return currentUserId === attachment.uploaded_by
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return ''
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

// 获取上传者名称
const getUploaderName = (attachment) => {
  if (attachment.uploader_name) {
    return attachment.uploader_name
  }
  if (!attachment.uploaded_by) return '未知'
  // 如果是当前用户
  if (attachment.uploaded_by === userStore.currentUser?.id) {
    return userStore.currentUser.username || '我'
  }
  // TODO: 可以缓存用户信息，避免重复查询
  return `用户${attachment.uploaded_by}`
}

// 删除Bug
const handleEdit = () => {
  if (route.name === 'ProjectBugDetail') {
    router.push(`/projects/${route.params.projectId}/bugs/${bugId.value}/edit`)
  } else {
    router.push(`/bugs/${bugId.value}/edit`)
  }
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除Bug "${bug.value.title}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await bugStore.deleteBug(bugId.value)
    ElMessage.success('Bug删除成功')

    if (route.name === 'ProjectBugDetail') {
      router.push(`/projects/${route.params.projectId}/bugs`)
    } else {
      router.push('/bugs')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除Bug失败:', error)
      ElMessage.error('删除Bug失败')
    }
  }
}

// 状态类型映射
const getStatusType = (status) => {
  const typeMap = {
    'new': 'info',
    'open': 'danger',
    'in_progress': 'warning',
    'resolved': 'success',
    'verified': 'success',
    'closed': 'success',
    'reopened': 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'new': '新建',
    'open': '打开',
    'in_progress': '进行中',
    'resolved': '已解决',
    'verified': '已验证',
    'closed': '已关闭',
    'reopened': '重新打开'
  }
  return textMap[status] || status
}

// 严重程度类型映射
const getSeverityType = (severity) => {
  const typeMap = {
    'low': 'success',
    'medium': 'info',
    'high': 'warning',
    'critical': 'danger',
    'Low': 'success',
    'Medium': 'info',
    'High': 'warning',
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
    'high': 'danger'
  }
  return typeMap[priority] || 'info'
}

const getPriorityText = (priority) => {
  const textMap = {
    'low': '低',
    'medium': '中',
    'high': '高'
  }
  return textMap[priority] || priority
}

// 格式化日期
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 格式化活动记录的日期（更友好的显示）
const formatActivityDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = systemTimeService.getServerTime()
  const diffMs = now - date
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffMinutes < 1) {
    return '刚刚'
  } else if (diffMinutes < 60) {
    return `${diffMinutes}分钟前`
  } else if (diffHours < 24) {
    return `${diffHours}小时前`
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

// 格式化完整日期（用于 title 提示）
const formatFullDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取活动操作文本
const getActivityActionText = (action) => {
  const actionMap = {
    'create_bug': '创建Bug',
    'update_bug': '更新Bug',
    'delete_bug': '删除Bug',
    'bug_status_transition': '状态变更',
    'add_comment': '添加评论',
    'delete_comment': '删除评论',
    'upload_attachment': '上传附件',
    'delete_attachment': '删除附件',
    'assign_bug': '分配Bug',
    'resolve_bug': '解决Bug',
    'verify_bug': '验证Bug',
    'close_bug': '关闭Bug',
    'reopen_bug': '重新打开Bug'
  }
  return actionMap[action] || action
}

// 跳转到项目详情
const goToProject = (projectId) => {
  if (projectId) {
    router.push(`/projects/${projectId}`)
  }
}

// 跳转到用户详情
const goToUser = (userId) => {
  if (userId) {
    router.push(`/users/${userId}`)
  }
}

onMounted(async () => {
  await systemTimeService.ensureSynced()
  fetchBugDetail()
  fetchActivities()
})
</script>

<style scoped>
.bug-detail {
  padding: 0;
}

.bug-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #EBEEF5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  margin: 0;
  color: #303133;
}

.header-right {
  display: flex;
  gap: 8px;
}

.info-card,
.description-card,
.steps-card,
.result-card,
.tags-card,
.attachments-card,
.comments-card,
.timeline-card {
  margin-bottom: 20px;
}

.timeline-card :deep(.el-card__body) {
  max-height: 400px;
  overflow-y: auto;
}

.timeline-card :deep(.el-timeline) {
  padding-left: 10px;
}

.timeline-card :deep(.el-timeline-item__content) {
  min-width: 200px;
}

.field-changes-card {
  margin-bottom: 20px;
}

.field-changes-card :deep(.el-card__body) {
  max-height: 400px;
  overflow-y: auto;
}

.card-header {
  font-weight: 600;
  color: #303133;
}

.description-content,
.steps-content,
.result-content {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.tags-content {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  margin-bottom: 8px;
}

.no-tags {
  color: #909399;
  font-style: italic;
}

.attachments-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #EBEEF5;
  border-radius: 4px;
  transition: all 0.3s;
}

.attachment-item:hover {
  border-color: #409EFF;
  background-color: #f5f7fa;
}

.attachment-icon {
  display: flex;
  align-items: center;
  color: #409EFF;
  font-size: 24px;
}

.attachment-info {
  flex: 1;
  min-width: 0;
}

.attachment-name {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #909399;
  flex-wrap: wrap;
}

.attachment-size {
  color: #909399;
}

.attachment-uploader {
  color: #606266;
}

.attachment-time {
  color: #C0C4CC;
}

.attachment-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.attachment-item.uploading {
  opacity: 0.7;
  background-color: #f5f7fa;
}

.attachment-item.uploading .attachment-icon {
  color: #909399;
}

.uploading-icon {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.no-attachments {
  color: #909399;
  font-style: italic;
  text-align: center;
  padding: 40px 20px;
}

.attachments-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: nowrap;
}

.attachments-card .card-header.attachments-header {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.attachments-card .card-header .header-title {
  flex-shrink: 0;
  white-space: nowrap;
}

.upload-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.upload-tip-container {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
}

.comment-input {
  margin-bottom: 20px;
}

.comment-actions {
  margin-top: 12px;
  text-align: right;
}

.comments-list {
  max-height: 400px;
  overflow-y: auto;
}

.comment-item {
  padding: 12px 0;
  border-bottom: 1px solid #EBEEF5;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.comment-author {
  font-weight: 600;
  color: #303133;
}

.comment-time {
  color: #909399;
  font-size: 12px;
}

.comment-content {
  color: #606266;
  line-height: 1.5;
}

.no-comments {
  text-align: center;
  color: #909399;
  font-style: italic;
  padding: 20px;
}

/* 状态流转按钮样式 */
.status-tag {
  margin-left: 12px;
}

.status-duration {
  margin-left: 4px;
  font-size: 12px;
  opacity: 0.8;
}

.transition-buttons {
  margin-right: 12px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 工作流建议面板样式 */
.workflow-suggestion-card {
  margin-bottom: 16px;
}

.workflow-suggestion-card .card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.workflow-suggestions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  padding: 12px;
  border-radius: 8px;
  background-color: #f5f7fa;
  border-left: 4px solid #409eff;
}

.suggestion-item.recommended {
  border-left-color: #67c23a;
  background-color: #f0f9eb;
}

.suggestion-item.warning {
  border-left-color: #e6a23c;
  background-color: #fdf6ec;
}

.suggestion-item.info {
  border-left-color: #909399;
  background-color: #f4f4f5;
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.suggestion-title {
  font-weight: 500;
  color: #303133;
}

.suggestion-content {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 8px;
}

.suggestion-actions {
  display: flex;
  gap: 8px;
}

/* 时间线样式 */
.resolution-text {
  margin-top: 8px;
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
}

.resolution-alert {
  margin-top: 12px;
}

.resolution-meta {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.timeline-card .el-timeline-item__wrapper {
  padding-left: 28px;
}

.timeline-card .el-card__body {
  padding: 16px;
}

.timeline-card h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
}

.timeline-card p {
  margin: 4px 0;
  color: #606266;
  font-size: 14px;
}

/* Bug 活动记录样式 */
.field-changes-list {
  max-height: 500px;
  overflow-y: auto;
}

.field-change-item {
  padding: 12px 0;
  border-bottom: 1px solid #EBEEF5;
}

.field-change-item:last-child {
  border-bottom: none;
}

.field-change-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 12px;
}

.field-change-header .header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.field-change-header .header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.field-change-action {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.field-change-time {
  color: #909399;
  font-size: 12px;
  cursor: help;
}

.field-change-user {
  color: #409eff;
  font-size: 12px;
}

.changes-summary {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
  padding: 6px 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.changes-summary .el-icon {
  color: #409eff;
}

.field-changes-detail {
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  margin-top: 8px;
}

.field-change-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 8px 0;
  font-size: 13px;
  border-bottom: 1px dashed #EBEEF5;
}

.field-change-row:last-child {
  border-bottom: none;
}

.field-label-wrapper {
  min-width: 100px;
  flex-shrink: 0;
}

.field-name {
  font-weight: 500;
  color: #303133;
  display: inline-block;
  padding: 2px 6px;
  background-color: #e8f4ff;
  border-radius: 3px;
}

.field-value-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.field-old-value {
  color: #909399;
  text-decoration: line-through;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: help;
}

.field-arrow {
  color: #409eff;
  font-weight: bold;
  font-size: 16px;
  flex-shrink: 0;
}

.field-new-value {
  color: #67c23a;
  font-weight: 500;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: help;
}

.field-changes-detail {
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-top: 8px;
}

.field-change-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  font-size: 13px;
  flex-wrap: wrap;
}

.field-name {
  font-weight: 500;
  color: #303133;
  min-width: 80px;
}

.field-old-value {
  color: #909399;
  text-decoration: line-through;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.field-arrow {
  color: #409eff;
  font-weight: bold;
}

.field-new-value {
  color: #67c23a;
  font-weight: 500;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.clickable-link {
  color: #409eff;
  cursor: pointer;
  text-decoration: none;
}

.clickable-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.preview-dialog .preview-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background-color: #f5f5f5;
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
}

.preview-pdf {
  width: 100%;
  height: 70vh;
  border: none;
}

.preview-unsupported {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  gap: 16px;
}

.preview-unsupported .preview-filename {
  font-size: 14px;
  color: #606266;
  word-break: break-all;
  text-align: center;
  max-width: 100%;
}

@media screen and (max-width: 768px) {
  .bug-detail {
    padding: 12px;
  }

  .bug-detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 12px;
  }

  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    width: 100%;
  }

  .header-left h2 {
    font-size: 16px;
    word-break: break-all;
  }

  .header-right {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-right .el-button {
    flex: 1;
    min-width: 80px;
    font-size: 12px;
    padding: 8px 12px;
  }

  .transition-buttons {
    width: 100%;
    margin-right: 0;
    margin-bottom: 8px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .transition-buttons .el-button {
    flex: 1;
    font-size: 12px;
    padding: 8px 12px;
    min-width: 70px;
  }

  .status-tag {
    margin-left: 0;
    margin-bottom: 8px;
  }

  .workflow-suggestion-card {
    margin-bottom: 16px;
  }

  .workflow-suggestions {
    gap: 8px;
  }

  .suggestion-item {
    padding: 10px;
  }

  .suggestion-header {
    flex-wrap: wrap;
    gap: 6px;
  }

  .suggestion-actions {
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
  }

  .suggestion-actions .el-button {
    flex: 1;
    min-width: 70px;
    font-size: 11px;
    padding: 6px 10px;
  }

  .info-card .el-row {
    flex-direction: column;
  }

  .info-card .el-col {
    width: 100% !important;
    max-width: 100% !important;
    margin-bottom: 12px;
  }

  .description-card,
  .attachments-card,
  .comments-card,
  .timeline-card,
  .field-changes-card,
  .steps-card,
  .result-card,
  .tags-card,
  .workflow-suggestion-card {
    margin-bottom: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    font-size: 14px;
  }

  .attachments-header {
    align-items: flex-start;
  }

  .upload-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }

  .upload-tip-container {
    width: 100%;
  }

  .comment-input {
    margin-bottom: 12px;
  }

  .comment-actions {
    text-align: right;
  }

  .comment-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .comments-list {
    max-height: 300px;
  }

  .field-change-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .field-change-header .header-left,
  .field-change-header .header-right {
    width: 100%;
    flex-wrap: wrap;
  }

  .field-change-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .field-label-wrapper {
    min-width: auto;
  }

  .field-value-wrapper {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
    width: 100%;
  }

  .field-old-value,
  .field-new-value {
    max-width: 100%;
    word-break: break-all;
  }

  .preview-dialog .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
  }

  .preview-content {
    min-height: 300px;
  }

  .preview-image {
    max-width: 100%;
    max-height: 50vh;
  }

  .preview-pdf {
    height: 50vh;
  }

  .el-descriptions {
    font-size: 12px;
  }

  .el-descriptions-item {
    display: block !important;
  }

  .el-descriptions-item__label {
    width: 100% !important;
    padding: 4px !important;
  }

  .el-descriptions-item__content {
    width: 100% !important;
    padding: 4px !important;
  }

  .el-timeline {
    padding-left: 0;
  }

  .el-timeline-item {
    padding-left: 20px;
  }

  .el-timeline-item__wrapper {
    padding-left: 24px;
  }

  .attachment-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .attachment-icon {
    margin-bottom: 8px;
  }

  .attachment-info {
    width: 100%;
  }

  .attachment-name {
    word-break: break-all;
  }

  .attachment-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
  }

  .attachment-actions .el-button {
    flex: 1;
    min-width: 60px;
    font-size: 11px;
    padding: 4px 8px;
  }
}

@media screen and (max-width: 480px) {
  .bug-detail {
    padding: 8px;
  }

  .bug-detail-header {
    margin-bottom: 12px;
    padding-bottom: 10px;
  }

  .header-left h2 {
    font-size: 14px;
  }

  .header-right .el-button {
    font-size: 11px;
    padding: 6px 10px;
    min-width: 70px;
  }

  .transition-buttons .el-button {
    font-size: 11px;
    padding: 6px 8px;
    min-width: 60px;
  }

  .suggestion-item {
    padding: 8px;
  }

  .suggestion-content {
    font-size: 12px;
  }

  .el-descriptions {
    font-size: 11px;
  }

  .description-content,
  .steps-content,
  .result-content {
    padding: 10px;
    font-size: 12px;
    white-space: pre-wrap;
    word-break: break-all;
  }

  .comment-input :deep(.el-textarea__inner) {
    min-height: 60px !important;
  }

  .comment-actions {
    margin-top: 8px;
  }

  .comment-actions .el-button {
    width: 100%;
  }

  .field-change-item {
    padding: 10px 0;
  }

  .field-change-action {
    font-size: 12px;
  }

  .field-change-time {
    font-size: 11px;
  }

  .changes-summary {
    font-size: 11px;
    padding: 4px 6px;
  }

  .field-change-row {
    font-size: 12px;
  }
}
</style>