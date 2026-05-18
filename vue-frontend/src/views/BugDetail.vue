<template>
  <div class="bug-detail-container" v-loading="loading">
    <div v-if="bug && bug.id" class="bug-detail-content">
      <!-- 页面头部 - 玻璃拟态风格 -->
      <div class="page-header animate-fade-in-down">
        <div class="header-bg-decoration">
          <div class="gradient-orb orb-1"></div>
          <div class="gradient-orb orb-2"></div>
        </div>
        <div class="header-content">
          <div class="header-left">
            <el-button @click="$router.back()" class="btn-back">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <div class="title-section">
              <h1>{{ bug.title }}</h1>
              <div class="status-section">
                <el-tag :type="getStatusType(bug.status)" size="large" class="status-tag" :class="`status-${bug.status}`">
                  {{ getStatusText(bug.status) }}
                </el-tag>
                <span v-if="currentStatusDuration" class="status-duration">
                  <el-icon><Timer /></el-icon>
                  {{ currentStatusDuration }}
                </span>
              </div>
            </div>
          </div>
          <div class="header-right">
            <!-- 状态流转按钮组 -->
            <el-button-group v-if="availableTransitions.length > 0" class="transition-buttons">
              <el-button 
                v-for="transition in availableTransitions" 
                :key="transition.to"
                :class="`btn-transition btn-${transition.type}`"
                @click="handleStatusTransition(transition)"
              >
                {{ transition.label }}
              </el-button>
            </el-button-group>
            
            <el-button v-if="canDelete" class="btn-gradient-danger" @click="handleDelete">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
            <el-button class="btn-gradient" @click="handleEdit">
              <el-icon><Edit /></el-icon>
              编辑Bug
            </el-button>
          </div>
        </div>
      </div>

      <!-- 工作流建议面板 -->
      <el-card class="workflow-suggestion-card glass-card animate-fade-in-up delay-100" v-if="workflowSuggestions.length > 0">
        <template #header>
          <div class="card-header">
            <span class="card-title">
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
              <el-tag :type="suggestion.type === 'recommended' ? 'success' : suggestion.type === 'warning' ? 'warning' : 'info'" size="small" effect="light">
                {{ suggestion.type === 'recommended' ? '建议' : suggestion.type === 'warning' ? '注意' : '提示' }}
              </el-tag>
              <span class="suggestion-title">{{ suggestion.title }}</span>
            </div>
            <div class="suggestion-content">{{ suggestion.description }}</div>
            <div class="suggestion-actions" v-if="suggestion.actions && suggestion.actions.length > 0">
              <el-button 
                v-for="action in suggestion.actions" 
                :key="action.to"
                :class="`btn-${action.btnType}`"
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
      <el-dialog v-model="showTransitionDialog" title="状态变更" width="500px" class="custom-dialog">
        <el-form label-width="100px">
          <el-form-item label="当前状态">
            <el-tag :type="getStatusType(bug.status)" effect="light">{{ getStatusText(bug.status) }}</el-tag>
          </el-form-item>
          <el-form-item label="目标状态">
            <el-tag :type="getStatusType(transitionForm.newStatus)" effect="light">{{ getStatusText(transitionForm.newStatus) }}</el-tag>
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
          <el-button @click="showTransitionDialog = false" class="btn-secondary">取消</el-button>
          <el-button class="btn-gradient" @click="confirmTransition" :loading="transitionLoading">确认</el-button>
        </template>
      </el-dialog>

      <!-- 附件预览对话框 -->
      <el-dialog v-model="showPreviewDialog" title="预览附件" width="800px" class="preview-dialog custom-dialog" @close="handlePreviewClose">
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
      <el-row :gutter="20" class="animate-fade-in-up delay-200">
        <el-col :span="16">
          <el-card class="info-card glass-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Document /></el-icon>
                  基本信息
                </span>
              </div>
            </template>
            
            <el-descriptions :column="2" border class="custom-descriptions">
              <el-descriptions-item label="ID">
                <span class="id-badge">#{{ bug.id }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getStatusType(bug.status)" size="small" effect="light" class="status-badge" :class="`status-${bug.status}`">
                  {{ getStatusText(bug.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="严重程度">
                <el-tag :type="getSeverityType(bug.severity)" size="small" effect="light" class="severity-badge">
                  {{ getSeverityText(bug.severity) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="优先级">
                <el-tag :type="getPriorityType(bug.priority)" size="small" effect="light" class="priority-badge">
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
                  <el-tag v-if="bug.resolved_at" size="small" type="info" effect="light" class="time-tag">
                    {{ formatDate(bug.resolved_at) }}
                  </el-tag>
                </span>
                <div v-else>-</div>
              </el-descriptions-item>
              <el-descriptions-item label="验证者">
                <span v-if="bug.verifier_name">
                  <span class="clickable-link" @click="goToUser(bug.verifier_id)">{{ bug.verifier_name }}</span>
                  <el-tag v-if="bug.verified_at" size="small" type="info" effect="light" class="time-tag">
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
          <el-card class="timeline-card glass-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Clock /></el-icon>
                  状态时间线
                </span>
              </div>
            </template>

            <el-timeline v-if="statusTimeline.length > 0" class="custom-timeline">
              <el-timeline-item
                v-for="item in statusTimeline"
                :key="item.id"
                :timestamp="formatDate(item.timestamp)"
                placement="top"
                :type="item.type === 'creation' ? 'primary' : item.type === 'resolved' ? 'success' : item.type === 'reopened' ? 'danger' : 'warning'"
              >
                <div class="timeline-item-content">
                  <h4>{{ item.title }}</h4>
                  <p>{{ item.description }}</p>
                  <div class="timeline-tags">
                    <el-tag v-if="item.type === 'resolved'" size="small" type="success" effect="light">已解决</el-tag>
                    <el-tag v-if="item.type === 'reopened'" size="small" type="danger" effect="light">重新打开</el-tag>
                    <el-tag v-if="item.type === 'closed'" size="small" type="info" effect="light">已关闭</el-tag>
                    <el-tag v-if="item.type === 'in_progress'" size="small" type="warning" effect="light">处理中</el-tag>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无状态变更记录" />
          </el-card>
          
          <!-- Bug 活动记录 -->
          <el-card class="field-changes-card glass-card" v-if="fieldChangeActivities.length > 0">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><List /></el-icon>
                  Bug 活动记录
                </span>
                <el-tag size="small" type="info" effect="light" class="count-badge">{{ fieldChangeActivities.length }} 条记录</el-tag>
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
                    <el-tag size="small" type="primary" effect="light">{{ activity.user_name || '未知用户' }}</el-tag>
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
          <el-card class="description-card glass-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Document /></el-icon>
                  Bug描述
                </span>
              </div>
            </template>
            
            <div class="description-content">
              <pre>{{ bug.description }}</pre>
            </div>
          </el-card>
          
          <!-- 重现步骤 -->
          <el-card class="steps-card glass-card" v-if="bug.steps_to_reproduce">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Refresh /></el-icon>
                  重现步骤
                </span>
              </div>
            </template>
            
            <div class="steps-content">
              <pre>{{ bug.steps_to_reproduce }}</pre>
            </div>
          </el-card>
          
          <!-- 预期结果和实际结果 -->
          <el-row :gutter="20" v-if="bug.expected_result || bug.actual_result">
            <el-col :span="12">
              <el-card class="result-card glass-card">
                <template #header>
                  <div class="card-header">
                    <span class="card-title">
                      <el-icon><CircleCheck /></el-icon>
                      预期结果
                    </span>
                  </div>
                </template>
                
                <div class="result-content">
                  <pre>{{ bug.expected_result || '无' }}</pre>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="12">
              <el-card class="result-card glass-card">
                <template #header>
                  <div class="card-header">
                    <span class="card-title">
                      <el-icon><CircleClose /></el-icon>
                      实际结果
                    </span>
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
          <el-card class="tags-card glass-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><CollectionTag /></el-icon>
                  标签
                </span>
              </div>
            </template>
            
            <div class="tags-content">
              <el-tag 
                v-for="tag in parsedTags" 
                :key="tag" 
                class="tag-item"
                type="primary"
                effect="light"
              >
                {{ tag }}
              </el-tag>
              <div v-if="!parsedTags || parsedTags.length === 0" class="no-tags">
                <el-icon><InfoFilled /></el-icon>
                暂无标签
              </div>
            </div>
          </el-card>
          
          <!-- 附件 -->
          <el-card class="attachments-card glass-card">
            <template #header>
              <div class="card-header attachments-header">
                <span class="card-title">
                  <el-icon><Paperclip /></el-icon>
                  附件
                </span>
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
                    <el-button class="btn-gradient" size="small" :disabled="!canEdit">
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
                    class="action-link"
                  >
                    预览
                  </el-button>
                  <el-button type="primary" link size="small" @click="downloadAttachment(attachment)" class="action-link">
                    下载
                  </el-button>
                  <el-button
                    type="danger"
                    link
                    size="small"
                    @click="deleteAttachment(attachment)"
                    v-if="canDeleteAttachment(attachment)"
                    :loading="deletingAttachmentId === attachment.id"
                    class="action-link danger"
                  >
                    删除
                  </el-button>
                </div>
              </div>
              <div v-if="!bug.attachments || bug.attachments.length === 0" class="no-attachments">
                <el-icon><Document /></el-icon>
                暂无附件，请点击"选择文件"按钮添加附件
              </div>
            </div>
          </el-card>
          
          <!-- 评论区域 -->
          <el-card class="comments-card glass-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><ChatDotRound /></el-icon>
                  评论
                </span>
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
                class="comment-textarea"
              />
              <div class="comment-actions">
                <el-button class="btn-gradient" @click="addComment" :disabled="!newComment.trim()">
                  <el-icon><Promotion /></el-icon>
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
                <div class="comment-avatar">
                  <div class="avatar-circle">{{ comment.author_name ? comment.author_name.charAt(0).toUpperCase() : '?' }}</div>
                </div>
                <div class="comment-body">
                  <div class="comment-header">
                    <span class="comment-author">{{ comment.author_name }}</span>
                    <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
                  </div>
                  <div class="comment-content">
                    {{ comment.content }}
                  </div>
                </div>
              </div>
              
              <div v-if="comments.length === 0" class="no-comments">
                <el-icon><ChatDotRound /></el-icon>
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
import { 
  ArrowLeft, Edit, Delete, InfoFilled, Document, Upload, Loading, 
  Clock, List, Refresh, CircleCheck, CircleClose, CollectionTag, 
  Paperclip, ChatDotRound, Promotion, Timer 
} from '@element-plus/icons-vue'
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
    'closed': 'info',
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
/* 导入设计系统 */
@import '@/styles/design-system.css';

.bug-detail-container {
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  min-height: 100%;
}

.bug-detail-content {
  padding-bottom: 24px;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
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
  color: white;
  transform: translateY(-2px);
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.title-section h1 {
  margin: 0;
  color: white;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.status-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-tag {
  font-size: 14px;
  font-weight: 600;
  padding: 6px 14px;
  border-radius: 20px;
  border: none;
}

.status-tag.status-new {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  color: white;
}

.status-tag.status-in_progress {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  color: white;
}

.status-tag.status-resolved,
.status-tag.status-verified,
.status-tag.status-closed {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  color: white;
}

.status-tag.status-reopened {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  color: white;
}

.status-duration {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  background: rgba(255, 255, 255, 0.15);
  padding: 4px 10px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

/* 渐变按钮 */
.btn-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(102, 126, 234, 0.5);
  color: white;
}

.btn-gradient-danger {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-gradient-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(239, 68, 68, 0.5);
  color: white;
}

.btn-secondary {
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(99, 102, 241, 0.1);
  border-color: #6366f1;
  color: #6366f1;
}

/* 状态流转按钮 */
.transition-buttons {
  margin-right: 8px;
}

.btn-transition {
  transition: all 0.3s;
}

.btn-transition:hover {
  transform: translateY(-2px);
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  border: none;
  color: white;
}

.btn-primary:hover {
  box-shadow: 0 8px 20px -5px rgba(59, 130, 246, 0.5);
  color: white;
}

.btn-success {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  border: none;
  color: white;
}

.btn-success:hover {
  box-shadow: 0 8px 20px -5px rgba(16, 185, 129, 0.5);
  color: white;
}

.btn-warning {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  border: none;
  color: white;
}

.btn-warning:hover {
  box-shadow: 0 8px 20px -5px rgba(245, 158, 11, 0.5);
  color: white;
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
  color: #6366f1;
  font-size: 18px;
}

.count-badge {
  font-weight: 500;
}

/* 工作流建议面板 */
.workflow-suggestion-card {
  margin-bottom: 20px;
}

.workflow-suggestions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  padding: 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-left: 4px solid #6366f1;
  transition: all 0.3s;
}

.suggestion-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.suggestion-item.recommended {
  border-left-color: #10b981;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
}

.suggestion-item.warning {
  border-left-color: #f59e0b;
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
}

.suggestion-item.info {
  border-left-color: #6b7280;
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.suggestion-title {
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
}

.suggestion-content {
  color: #475569;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 12px;
}

.suggestion-actions {
  display: flex;
  gap: 10px;
}

/* 信息卡片 */
.id-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
}

.status-badge,
.severity-badge,
.priority-badge {
  font-weight: 500;
  border-radius: 6px;
}

.status-badge.status-new {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1d4ed8;
  border: none;
}

.status-badge.status-in_progress {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #b45309;
  border: none;
}

.status-badge.status-resolved,
.status-badge.status-verified,
.status-badge.status-closed {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #047857;
  border: none;
}

.status-badge.status-reopened {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #b91c1c;
  border: none;
}

.time-tag {
  margin-left: 8px;
}

.clickable-link {
  color: #6366f1;
  cursor: pointer;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
}

.clickable-link:hover {
  color: #4f46e5;
  text-decoration: underline;
}

/* 自定义描述列表 */
.custom-descriptions :deep(.el-descriptions__header) {
  margin-bottom: 16px;
}

.custom-descriptions :deep(.el-descriptions__label) {
  background: rgba(241, 245, 249, 0.8);
  font-weight: 500;
  color: #475569;
}

.custom-descriptions :deep(.el-descriptions__content) {
  color: #1e293b;
}

/* 时间线 */
.timeline-card :deep(.el-card__body) {
  max-height: 400px;
  overflow-y: auto;
}

.custom-timeline :deep(.el-timeline-item__node) {
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2);
}

.timeline-item-content {
  background: rgba(255, 255, 255, 0.6);
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.timeline-item-content h4 {
  margin: 0 0 8px 0;
  color: #1e293b;
  font-size: 15px;
  font-weight: 600;
}

.timeline-item-content p {
  margin: 0 0 12px 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.5;
}

.timeline-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* 字段变更记录 */
.field-changes-card :deep(.el-card__body) {
  max-height: 400px;
  overflow-y: auto;
}

.field-changes-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field-change-item {
  padding: 16px;
  background: rgba(248, 250, 252, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(226, 232, 240, 0.6);
  transition: all 0.3s;
}

.field-change-item:hover {
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
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
}

.field-change-header .header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.field-change-action {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.field-change-time {
  color: #94a3b8;
  font-size: 12px;
}

.changes-summary {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
}

.changes-summary .el-icon {
  color: #6366f1;
}

.field-changes-detail {
  padding: 12px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 10px;
}

.field-change-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  font-size: 13px;
  border-bottom: 1px dashed rgba(203, 213, 225, 0.5);
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
  color: #1e293b;
  display: inline-block;
  padding: 4px 10px;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  border-radius: 6px;
  font-size: 12px;
}

.field-value-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.field-old-value {
  color: #94a3b8;
  text-decoration: line-through;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.field-arrow {
  color: #6366f1;
  font-weight: bold;
  font-size: 16px;
}

.field-new-value {
  color: #059669;
  font-weight: 500;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 描述、步骤、结果卡片 */
.description-content,
.steps-content,
.result-content {
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #334155;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

/* 标签卡片 */
.tags-content {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-item {
  font-weight: 500;
  border-radius: 8px;
  padding: 6px 12px;
  transition: all 0.3s;
}

.tag-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.no-tags {
  color: #94a3b8;
  font-style: italic;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 20px;
  justify-content: center;
}

/* 附件卡片 */
.attachments-card .card-header.attachments-header {
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
}

.upload-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.upload-tip-container {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.upload-tip {
  font-size: 12px;
  color: #94a3b8;
}

.attachments-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  background: rgba(248, 250, 252, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(226, 232, 240, 0.6);
  transition: all 0.3s;
}

.attachment-item:hover {
  background: rgba(255, 255, 255, 0.95);
  border-color: #c7d2fe;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
  transform: translateY(-2px);
}

.attachment-item.uploading {
  opacity: 0.7;
  background: rgba(241, 245, 249, 0.9);
}

.attachment-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  border-radius: 10px;
  color: #6366f1;
  font-size: 20px;
}

.attachment-item.uploading .attachment-icon {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  color: #94a3b8;
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

.attachment-info {
  flex: 1;
  min-width: 0;
}

.attachment-name {
  font-size: 14px;
  color: #1e293b;
  font-weight: 500;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #64748b;
  flex-wrap: wrap;
}

.attachment-size {
  background: rgba(226, 232, 240, 0.6);
  padding: 2px 8px;
  border-radius: 4px;
}

.attachment-uploader {
  color: #64748b;
}

.attachment-time {
  color: #94a3b8;
}

.attachment-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-link {
  font-weight: 500;
}

.action-link.danger:hover {
  color: #ef4444;
}

.no-attachments {
  color: #94a3b8;
  font-style: italic;
  text-align: center;
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.no-attachments .el-icon {
  font-size: 32px;
  color: #cbd5e1;
}

/* 评论卡片 */
.comment-input {
  margin-bottom: 20px;
}

.comment-textarea :deep(.el-textarea__inner) {
  border-radius: 12px;
  background: rgba(248, 250, 252, 0.8);
  border: 1px solid rgba(226, 232, 240, 0.6);
  transition: all 0.3s;
}

.comment-textarea :deep(.el-textarea__inner:focus) {
  background: rgba(255, 255, 255, 0.95);
  border-color: #c7d2fe;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.comment-actions {
  margin-top: 12px;
  text-align: right;
}

.comments-list {
  max-height: 400px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-item {
  display: flex;
  gap: 14px;
  padding: 16px;
  background: rgba(248, 250, 252, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(226, 232, 240, 0.6);
  transition: all 0.3s;
}

.comment-item:hover {
  background: rgba(255, 255, 255, 0.95);
  border-color: #c7d2fe;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.08);
  transform: translateY(-2px);
}

.comment-avatar {
  flex-shrink: 0;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
}

.comment-body {
  flex: 1;
  min-width: 0;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.comment-author {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.comment-time {
  color: #94a3b8;
  font-size: 12px;
}

.comment-content {
  color: #475569;
  line-height: 1.6;
  font-size: 14px;
}

.no-comments {
  text-align: center;
  color: #94a3b8;
  font-style: italic;
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.no-comments .el-icon {
  font-size: 32px;
  color: #cbd5e1;
}

/* 预览对话框 */
.preview-dialog .preview-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 8px;
}

.preview-pdf {
  width: 100%;
  height: 70vh;
  border: none;
  border-radius: 8px;
}

.preview-unsupported {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  gap: 16px;
}

.preview-unsupported .preview-filename {
  font-size: 14px;
  color: #64748b;
  word-break: break-all;
  text-align: center;
  max-width: 100%;
}

/* 自定义对话框 */
:deep(.custom-dialog .el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 24px;
  margin-right: 0;
}

:deep(.custom-dialog .el-dialog__title) {
  color: white;
  font-weight: 600;
}

:deep(.custom-dialog .el-dialog__headerbtn .el-dialog__close) {
  color: rgba(255, 255, 255, 0.8);
}

:deep(.custom-dialog .el-dialog__headerbtn:hover .el-dialog__close) {
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
  .bug-detail-container {
    padding: 0;
  }

  .page-header {
    padding: 20px;
    margin-bottom: 16px;
    border-radius: 16px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    width: 100%;
  }

  .title-section h1 {
    font-size: 18px;
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
  }

  .workflow-suggestion-card {
    margin-bottom: 16px;
  }

  .workflow-suggestions {
    gap: 8px;
  }

  .suggestion-item {
    padding: 12px;
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

  .glass-card {
    margin-bottom: 16px;
    border-radius: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
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
    margin-bottom: 16px;
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

  .comment-item {
    padding: 12px;
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
    gap: 6px;
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
  .page-header {
    padding: 16px;
  }

  .title-section h1 {
    font-size: 16px;
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
    padding: 10px;
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
    padding: 12px;
    font-size: 12px;
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
    padding: 12px;
  }

  .field-change-action {
    font-size: 12px;
  }

  .field-change-time {
    font-size: 11px;
  }

  .changes-summary {
    font-size: 11px;
    padding: 6px 8px;
  }

  .field-change-row {
    font-size: 12px;
  }
}
</style>
