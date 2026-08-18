<template>
  <el-dialog
    :model-value="visible"
    :title="null"
    width="640px"
    :with-header="false"
    :close-on-click-modal="false"
    :close-on-press-escape="true"
    :destroy-on-close="false"
    :modal="true"
    align-center
    custom-class="rd-detail-dialog"
    @update:model-value="handleClose"
  >
    <div class="detail-container" v-loading="loading">
      <!-- 顶部标题栏 -->
      <div class="detail-header">
        <div class="header-left">
          <div class="status-badge" v-if="item && item.status" :style="statusStyle">
            <span class="status-dot" :style="{ background: item.status_color || '#94a3b8' }"></span>
            {{ statusLabel }}
          </div>
          <div class="detail-title-wrap">
            <input
              v-if="editingTitle"
              ref="titleInputRef"
              v-model="editingTitleValue"
              class="detail-title-input"
              @blur="commitTitle"
              @keydown.enter.prevent="commitTitle"
              @keydown.esc="cancelTitle"
              maxlength="200"
            />
            <h2 v-else class="detail-title" @dblclick="startEditTitle" :title="item?.title">
              {{ item?.title || '加载中...' }}
            </h2>
          </div>
        </div>
        <div class="header-actions">
          <el-tooltip content="复制" placement="top">
            <button class="hdr-btn" @click="copyTitle">
              <el-icon><Link /></el-icon>
            </button>
          </el-tooltip>
          <el-tooltip content="最大化" placement="top">
            <button class="hdr-btn" @click="$emit('maximize')">
              <el-icon><FullScreen /></el-icon>
            </button>
          </el-tooltip>
          <el-tooltip content="更多" placement="top">
            <el-dropdown trigger="click" @command="onHeaderCommand">
              <button class="hdr-btn">
                <el-icon><MoreFilled /></el-icon>
              </button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="status">
                    <el-icon><Flag /></el-icon>设置状态
                  </el-dropdown-item>
                  <el-dropdown-item command="assignee">
                    <el-icon><User /></el-icon>指派负责人
                  </el-dropdown-item>
                  <el-dropdown-item command="rename">
                    <el-icon><EditPen /></el-icon>重命名
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" divided>
                    <el-icon style="color: #ef4444"><Delete /></el-icon>
                    <span style="color: #ef4444">删除卡片</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </el-tooltip>
          <el-tooltip content="关闭" placement="top">
            <button class="hdr-btn close" @click="handleClose(false)">
              <el-icon><Close /></el-icon>
            </button>
          </el-tooltip>
        </div>
      </div>

      <!-- 元信息条：列 + 指派 + 状态 + 严重度(SLA) + 更新时间 -->
      <div class="meta-strip" v-if="item">
        <!-- 所在列（点击可移列） -->
        <el-dropdown
          trigger="click"
          @command="handleMoveToColumn"
          popper-class="rd-column-dropdown"
        >
          <div class="meta-pill column-pill" :style="{ background: columnColorBg, color: columnColorFg }">
            <el-icon><Folder /></el-icon>
            <span>{{ columnName || '—' }}</span>
            <el-icon class="caret"><CaretBottom /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="c in moveableColumns"
                :key="c.key"
                :command="c.key"
                :disabled="c.key === item.column"
              >
                <span class="col-dot" :style="{ background: c.color }"></span>
                {{ c.name }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- 指派人 -->
        <el-dropdown
          trigger="click"
          @command="handleAssigneeChange"
          popper-class="rd-assignee-dropdown"
        >
          <div class="meta-pill assignee-pill">
            <el-avatar :size="18" :src="item.assignee?.avatar">
              {{ avatarText(item.assignee?.name) }}
            </el-avatar>
            <span>{{ item.assignee?.name || '未指派' }}</span>
            <el-icon class="caret"><CaretBottom /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="__unassign__">
                <el-icon><UserFilled /></el-icon>
                <span>取消指派</span>
              </el-dropdown-item>
              <el-dropdown-item
                v-for="u in userOptions"
                :key="u.id"
                :command="String(u.id)"
                :disabled="u.id === item.assignee?.id"
              >
                <el-avatar :size="18" :src="u.avatar">
                  {{ avatarText(u.name) }}
                </el-avatar>
                <span>{{ u.name }}</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- 状态徽章（点击可改） -->
        <el-dropdown
          trigger="click"
          @command="handleStatusChange"
          popper-class="rd-status-dropdown"
        >
          <div class="meta-pill status-pill" v-if="item.status" :style="statusStyle">
            <span class="status-dot" :style="{ background: item.status_color || '#94a3b8' }"></span>
            <span>{{ statusLabel }}</span>
            <el-icon class="caret"><CaretBottom /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="s in statusOptions"
                :key="s.value"
                :command="s.value"
                :disabled="s.value === item.status"
              >
                <span class="col-dot" :style="{ background: s.color }"></span>
                {{ s.label }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- 客户问题严重度（SLA 倒计时） -->
        <el-dropdown
          v-if="item.column === 'customer_issue'"
          trigger="click"
          @command="handleSeverityChange"
          popper-class="rd-severity-dropdown"
        >
          <div
            class="meta-pill severity-pill"
            :style="severityStyle"
          >
            <el-icon><Warning /></el-icon>
            <span>{{ severityLabel || '设置严重度' }}</span>
            <span class="sla-text" v-if="slaText">· {{ slaText }}</span>
            <el-icon class="caret"><CaretBottom /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="s in severityOptions"
                :key="s.value"
                :command="s.value"
                :disabled="s.value === item.severity"
              >
                <span class="col-dot" :style="{ background: s.color }"></span>
                {{ s.label }}（SLA {{ s.sla }}h）
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <div class="meta-pill" v-if="item.updated_at">
          <el-icon><Clock /></el-icon>
          <span>更新于 {{ formatTime(item.updated_at) }}</span>
        </div>
        <div class="meta-pill">
          <el-icon><ChatDotRound /></el-icon>
          <span>{{ comments.length }} 条评论</span>
        </div>
      </div>

      <!-- 主体内容区 -->
      <div class="detail-body">
        <!-- 附件 -->
        <section class="detail-section">
          <h3 class="section-title">
            <el-icon><Paperclip /></el-icon>
            <span>附件</span>
            <span class="hint">如果文件名无效，则取消上传或重命名。</span>
          </h3>
          <div
            class="upload-zone"
            :class="{ 'is-dragover': isDragover }"
            @dragover.prevent="isDragover = true"
            @dragleave.prevent="isDragover = false"
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
          >
            <input
              ref="fileInputRef"
              type="file"
              multiple
              style="display: none"
              @change="handleFileSelect"
            />
            <el-icon class="upload-icon"><Plus /></el-icon>
          </div>
          <div class="attachment-list" v-if="attachments.length">
            <div v-for="att in attachments" :key="att.id" class="attachment-item" :class="{ 'is-previewable': isPreviewable(att) }">
              <div
                class="att-icon"
                :style="{ background: iconColor(att.mime_type) }"
                @click="isPreviewable(att) && previewAttachment(att)"
              >
                <el-icon><Document /></el-icon>
              </div>
              <div
                class="att-info"
                @click="isPreviewable(att) && previewAttachment(att)"
              >
                <div class="att-name" :title="att.original_name">
                  {{ att.original_name }}
                  <el-tag v-if="isPreviewable(att)" size="small" type="success" effect="plain" class="preview-tag">可预览</el-tag>
                </div>
                <div class="att-meta">
                  {{ formatSize(att.file_size) }} ·
                  <span v-if="att.uploader">{{ att.uploader.name }}</span>
                  <span v-else>匿名</span>
                  · {{ formatTime(att.uploaded_at) }}
                </div>
              </div>
              <div class="att-actions">
                <el-tooltip :content="isPreviewable(att) ? '在线预览' : '该格式不支持预览'" placement="top">
                  <button
                    class="att-action-btn"
                    :class="{ disabled: !isPreviewable(att) }"
                    :disabled="!isPreviewable(att)"
                    @click="previewAttachment(att)"
                  >
                    <el-icon><View /></el-icon>
                  </button>
                </el-tooltip>
                <el-tooltip content="下载" placement="top">
                  <button class="att-action-btn" @click="downloadAttachment(att)">
                    <el-icon><Download /></el-icon>
                  </button>
                </el-tooltip>
                <el-tooltip content="删除" placement="top">
                  <button class="att-action-btn danger" @click="deleteAttachment(att)">
                    <el-icon><Delete /></el-icon>
                  </button>
                </el-tooltip>
              </div>
            </div>
          </div>
        </section>

        <!-- 评论 -->
        <section class="detail-section">
          <h3 class="section-title">
            <el-icon><ChatDotRound /></el-icon>
            <span>评论</span>
            <span class="section-actions">
              <button class="icon-btn" :class="{ active: mdMode }" @click="mdMode = !mdMode" title="切换 Markdown 模式">
                <el-icon><EditPen /></el-icon>
              </button>
              <button class="icon-btn" title="复制全部">
                <el-icon><CopyDocument /></el-icon>
              </button>
            </span>
          </h3>
          <!-- 评论输入 -->
          <div class="comment-editor">
            <div class="editor-toolbar">
              <button class="tool-btn" @click="insertMarkdown('**', '**')" title="加粗">
                <strong>B</strong>
              </button>
              <button class="tool-btn" @click="insertMarkdown('*', '*')" title="斜体">
                <em>I</em>
              </button>
              <button class="tool-btn" @click="insertMarkdown('~~', '~~')" title="删除线">
                <s>S</s>
              </button>
              <button class="tool-btn" @click="insertMarkdown('\n- ', '')" title="列表">
                <el-icon><List /></el-icon>
              </button>
              <button class="tool-btn" @click="insertMarkdown('\n1. ', '')" title="有序列表">
                <span style="font-weight:600">1.</span>
              </button>
              <button class="tool-btn" @click="insertMarkdown('\n```\n', '\n```\n')" title="代码块">
                <span>{ }</span>
              </button>
              <button class="tool-btn" @click="insertMarkdown('[', '](url)')" title="链接">
                <el-icon><Link /></el-icon>
              </button>
              <button class="tool-btn" @click="addEmoji('😊')" title="表情">
                <el-icon><Sunny /></el-icon>
              </button>
            </div>
            <!-- 回复提示条 -->
            <div v-if="replyingTo" class="reply-banner">
              <el-icon class="reply-banner-icon"><ChatDotRound /></el-icon>
              <span class="reply-banner-text">
                正在回复 <strong>@{{ replyingTo.name }}</strong>
                <span class="reply-banner-content">：{{ replyingTo.content }}</span>
              </span>
              <button class="reply-banner-close" @click="cancelReplyComment" title="取消回复">
                <el-icon><Close /></el-icon>
              </button>
            </div>
            <textarea
              v-model="newComment"
              class="editor-textarea"
              :placeholder="replyingTo ? `回复 @${replyingTo.name} ...` : (mdMode ? '支持 Markdown 语法（**加粗** *斜体* [链接](url) - 列表）...' : '发表评论...')"
              rows="4"
              maxlength="2000"
              @keydown.ctrl.enter.prevent="submitComment"
              @keydown.meta.enter.prevent="submitComment"
            />
            <div class="editor-footer">
              <span class="char-count">{{ newComment.length }} / 2000</span>
              <div class="editor-actions">
                <el-button @click="newComment = ''" :disabled="!newComment">清空</el-button>
                <el-button class="btn-gradient" :loading="submitting" :disabled="!newComment.trim()" @click="submitComment">
                  评论
                </el-button>
              </div>
            </div>
          </div>

          <!-- 评论列表 -->
          <div class="comment-list" v-if="comments.length">
            <div
              v-for="c in commentTree"
              :key="c.id"
              class="comment-thread"
            >
            <div
              class="comment-item"
              :class="{
                'is-self': isCommentMine(c),
                'is-reply-target': replyingTo && replyingTo.id === c.id,
              }"
            >
              <el-avatar :size="28" :src="c.user?.avatar" class="comment-avatar">
                {{ avatarText(c.user?.name) }}
              </el-avatar>
              <div class="comment-body">
                <div class="comment-head">
                  <span class="comment-author">{{ c.user?.name || '未知用户' }}</span>
                  <el-tag v-if="isCommentAuthorAdmin(c)" size="small" type="danger" effect="dark" class="admin-badge">管理员</el-tag>
                  <span class="comment-time">{{ formatTime(c.created_at) }}</span>
                </div>
                <div v-if="editingCommentId === c.id" class="comment-edit">
                  <textarea
                    v-model="editingCommentContent"
                    class="editor-textarea"
                    rows="3"
                    maxlength="2000"
                  />
                  <div class="editor-actions">
                    <el-button @click="editingCommentId = null">取消</el-button>
                    <el-button class="btn-gradient" @click="saveEditComment(c)">保存</el-button>
                  </div>
                </div>
                <div v-else class="comment-content" v-html="renderMarkdown(c.content)" />
                <!-- 表情反应 -->
                <div class="comment-reactions" v-if="c.reactions && Object.keys(c.reactions).length">
                  <span
                    v-for="(uids, emoji) in c.reactions"
                    :key="emoji"
                    class="reaction-pill"
                    :class="{ mine: uids.includes(currentUserId) }"
                    @click="toggleReaction(c, emoji)"
                    :title="`${uids.length} 人反应`"
                  >
                    {{ emoji }} {{ uids.length }}
                  </span>
                  <button class="add-reaction-btn" @click="showEmojiPicker(c)" title="添加反应">
                    <el-icon><Sunny /></el-icon>
                  </button>
                </div>
                <div v-else class="comment-reactions">
                  <button class="add-reaction-btn" @click="showEmojiPicker(c)" title="添加反应">
                    <el-icon><Sunny /></el-icon>
                  </button>
                </div>
                <!-- 操作：回复（任何登录用户）/ 编辑 / 删除 -->
                <div class="comment-actions always-show">
                  <el-button text size="small" @click="startReplyComment(c)">回复</el-button>

                  <el-tooltip
                    v-if="!canEdit(c)"
                    :content="noEditTip(c)"
                    placement="top"
                  >
                    <span class="comment-action-wrap">
                      <el-icon class="lock-icon"><Lock /></el-icon>
                      <el-button text size="small" disabled>编辑</el-button>
                    </span>
                  </el-tooltip>
                  <el-button v-else text size="small" @click="startEditComment(c)">编辑</el-button>

                  <el-tooltip
                    v-if="!canDelete(c)"
                    :content="noDeleteTip(c)"
                    placement="top"
                  >
                    <span class="comment-action-wrap">
                      <el-icon class="lock-icon"><Lock /></el-icon>
                      <el-button text size="small" type="danger" disabled>删除</el-button>
                    </span>
                  </el-tooltip>
                  <el-button v-else text size="small" type="danger" @click="deleteCommentItem(c)">删除</el-button>
                </div>
              </div>
            </div>

            <!-- 回复子列表（嵌套显示在原评论下） -->
            <div v-if="c.replies && c.replies.length" class="comment-replies">
              <div
                v-for="r in c.replies"
                :key="r.id"
                class="comment-item comment-reply-item"
                :class="{
                  'is-self': isCommentMine(r),
                  'is-reply-target': replyingTo && replyingTo.id === r.id,
                }"
              >
                <el-avatar :size="22" :src="r.user?.avatar" class="comment-avatar">
                  {{ avatarText(r.user?.name) }}
                </el-avatar>
                <div class="comment-body">
                  <div class="comment-head">
                    <span class="comment-author">{{ r.user?.name || '未知用户' }}</span>
                    <el-tag v-if="isCommentAuthorAdmin(r)" size="small" type="danger" effect="dark" class="admin-badge">管理员</el-tag>
                    <span class="reply-to-tag" v-if="r.parent_id === c.id">
                      回复 <strong>@{{ c.user?.name || '未知用户' }}</strong>
                    </span>
                    <span class="comment-time">{{ formatTime(r.created_at) }}</span>
                  </div>
                  <div v-if="editingCommentId === r.id" class="comment-edit">
                    <textarea
                      v-model="editingCommentContent"
                      class="editor-textarea"
                      rows="2"
                      maxlength="2000"
                    />
                    <div class="editor-actions">
                      <el-button size="small" @click="editingCommentId = null">取消</el-button>
                      <el-button class="btn-gradient" size="small" @click="saveEditComment(r)">保存</el-button>
                    </div>
                  </div>
                  <div v-else class="comment-content" v-html="renderMarkdown(r.content)" />
                  <!-- 回复的操作按钮 -->
                  <div class="comment-actions always-show">
                    <el-tooltip
                      v-if="!canEdit(r)"
                      :content="noEditTip(r)"
                      placement="top"
                    >
                      <span class="comment-action-wrap">
                        <el-icon class="lock-icon"><Lock /></el-icon>
                        <el-button text size="small" disabled>编辑</el-button>
                      </span>
                    </el-tooltip>
                    <el-button v-else text size="small" @click="startEditComment(r)">编辑</el-button>

                    <el-tooltip
                      v-if="!canDelete(r)"
                      :content="noDeleteTip(r)"
                      placement="top"
                    >
                      <span class="comment-action-wrap">
                        <el-icon class="lock-icon"><Lock /></el-icon>
                        <el-button text size="small" type="danger" disabled>删除</el-button>
                      </span>
                    </el-tooltip>
                    <el-button v-else text size="small" type="danger" @click="deleteCommentItem(r)">删除</el-button>
                  </div>
                </div>
              </div>
            </div>
            </div>
          </div>
          <div v-else class="comment-empty">
            暂无评论，快来发表第一条吧
          </div>
        </section>
      </div>

      <!-- 表情选择器（弹出层） -->
      <el-popover
        v-model:visible="emojiPickerVisible"
        placement="bottom"
        :width="240"
        trigger="manual"
      >
        <template #reference>
          <span class="emoji-picker-anchor"></span>
        </template>
        <div class="emoji-grid">
          <span
            v-for="e in EMOJI_LIST"
            :key="e"
            class="emoji-item"
            @click="pickEmoji(e)"
          >{{ e }}</span>
        </div>
      </el-popover>
    </div>

    <!-- 文本附件预览弹窗 -->
    <el-dialog
      v-model="previewVisible"
      :title="`文本预览 - ${previewMeta.original_name || ''}`"
      width="780px"
      align-center
      :close-on-click-modal="true"
      :close-on-press-escape="true"
      custom-class="rd-attachment-preview-dialog"
      append-to-body
    >
      <div class="preview-meta" v-if="previewMeta.size">
        <el-tag size="small" type="info">编码：{{ previewMeta.encoding }}</el-tag>
        <el-tag size="small" type="info">大小：{{ formatSize(previewMeta.size) }}</el-tag>
        <el-tag size="small" type="info">行数：{{ previewMeta.line_count }}</el-tag>
        <el-tag v-if="previewMeta.truncated" size="small" type="warning" effect="dark">已截断</el-tag>
      </div>
      <pre v-if="previewLoading" v-loading="true" class="preview-loading">加载中...</pre>
      <pre v-else class="preview-content">{{ previewContent }}</pre>
      <template #footer>
        <el-button @click="copyPreviewContent" :disabled="!previewContent">复制内容</el-button>
        <el-button class="btn-gradient" @click="previewVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Link, FullScreen, MoreFilled, Flag, User, EditPen, Delete, Close,
  Folder, Clock, ChatDotRound, Paperclip, Plus, Document, Download,
  List, Sunny, CopyDocument, CaretBottom, Warning, UserFilled, Lock, View,
} from '@element-plus/icons-vue'
import rdKanbanService from '@/services/rdKanbanService'
import { useUserStore } from '@/stores/user'
import api from '@/services/api'

const props = defineProps({
  visible: { type: Boolean, default: false },
  itemId: { type: [Number, String], default: null },
  item: { type: Object, default: null },
  columns: { type: Array, default: () => [] },
  userOptions: { type: Array, default: () => [] },
  statusOptions: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:visible', 'refresh', 'maximize', 'delete'])

const userStore = useUserStore()
const currentUserId = computed(() => userStore.currentUser?.id || 0)
const currentUserName = computed(() => userStore.currentUser?.username || '')
// admin 判定：兼容 role 字段 / is_admin / is_super_admin / roles 数组等多种返回结构
const isAdmin = computed(() => {
  const u = userStore.currentUser
  if (!u) return false
  if (u.is_super_admin === true || u.isAdmin === true) return true
  if (u.is_admin === true) return true
  if (typeof u.role === 'string' && u.role.toLowerCase() === 'admin') return true
  if (Array.isArray(u.roles) && u.roles.some((r) => String(r).toLowerCase() === 'admin')) return true
  return false
})

const loading = ref(false)
const submitting = ref(false)

// 用户列表（用于指派下拉）
const userOptions = ref([])

// 状态选项（与后端 STATUS_OPTIONS 保持一致；色值与其他页面状态色板统一）
const DEFAULT_STATUS_OPTIONS = [
  { value: 'completed',         label: '完成',         color: '#10b981' },
  { value: 'in_progress',       label: '正在备战中...', color: '#f59e0b' },
  { value: 'priority',          label: '优先',         color: '#ec4899' },
  { value: 'paused',            label: '暂停',         color: '#94a3b8' },
  { value: 'pending_discuss',   label: '待讨论',       color: '#ef4444' },
  { value: 'not_supported',     label: '不支持',       color: '#6b7280' },
  { value: 'test_completed',    label: '测试完成',     color: '#14b8a6' },
  { value: 'partially_support', label: '部分支持',     color: '#8b5cf6' },
]
const statusOptions = computed(() => {
  if (Array.isArray(props.statusOptions) && props.statusOptions.length) {
    return props.statusOptions
  }
  return DEFAULT_STATUS_OPTIONS
})

// 客户问题严重度
const severityOptions = [
  { value: 'critical', label: '致命', color: '#dc2626', sla: 4 },
  { value: 'high', label: '严重', color: '#ef4444', sla: 24 },
  { value: 'medium', label: '一般', color: '#f59e0b', sla: 72 },
  { value: 'low', label: '轻微', color: '#10b981', sla: 168 },
]

// 详情
const comments = ref([])
const attachments = ref([])

// 文本附件预览
const PREVIEW_EXTENSIONS = [
  'txt', 'md', 'markdown', 'log',
  'json', 'csv', 'tsv',
  'xml', 'html', 'htm', 'css', 'js', 'ts',
  'yaml', 'yml', 'ini', 'conf', 'cfg', 'env',
  'sh', 'bat', 'ps1', 'sql', 'py', 'java',
]
const previewVisible = ref(false)
const previewLoading = ref(false)
const previewContent = ref('')
const previewMeta = ref({}) // { encoding, size, line_count, truncated, original_name }

// 编辑标题
const editingTitle = ref(false)
const editingTitleValue = ref('')
const titleInputRef = ref(null)

// 上传
const isDragover = ref(false)
const fileInputRef = ref(null)

// 评论输入
const newComment = ref('')
const mdMode = ref(true)

// 评论回复
const replyingTo = ref(null) // { id, name, content } | null

// 评论编辑
const editingCommentId = ref(null)
const editingCommentContent = ref('')

// 表情
const emojiPickerVisible = ref(false)
const emojiPickerTarget = ref(null)
const EMOJI_LIST = ['👍', '❤️', '🎉', '😊', '😄', '😢', '😂', '🔥', '✨', '👏', '🙏', '💯', '🚀', '💪', '🤔', '👀', '✅', '❌', '⭐', '🎯']

const columnName = computed(() => {
  if (!props.item) return ''
  const c = props.columns.find((x) => x.key === props.item.column)
  return c ? c.name : props.item.column
})

const currentColumnColor = computed(() => {
  if (!props.item) return '#94a3b8'
  const c = props.columns.find((x) => x.key === props.item.column)
  return c?.color || '#94a3b8'
})

const columnColorBg = computed(() => currentColumnColor.value + '1A')
const columnColorFg = computed(() => currentColumnColor.value)

const moveableColumns = computed(() => props.columns || [])

const statusStyle = computed(() => {
  if (!props.item?.status) return {}
  return {
    background: (props.item.status_color || '#94a3b8') + '22',
    color: props.item.status_color || '#94a3b8',
    borderColor: (props.item.status_color || '#94a3b8') + '55',
  }
})

const statusLabel = computed(() => {
  if (!props.item?.status) return ''
  const s = statusOptions.value.find((x) => x.value === props.item.status)
  return s ? s.label : props.item.status
})

const severityStyle = computed(() => {
  const sev = props.item?.severity
  if (!sev) return {}
  const s = severityOptions.find((x) => x.value === sev)
  if (!s) return {}
  return {
    background: s.color + '1A',
    color: s.color,
    borderColor: s.color + '55',
  }
})

const severityLabel = computed(() => {
  const sev = props.item?.severity
  if (!sev) return ''
  const s = severityOptions.find((x) => x.value === sev)
  return s ? s.label : sev
})

const slaText = computed(() => {
  if (props.item?.column !== 'customer_issue') return ''
  if (!props.item?.severity) return ''
  if (props.item?.resolved_at) return '已解决'
  // 优先用后端计算的 due_at，否则用 created_at + SLA 估算
  let target = null
  if (props.item.due_at) {
    target = new Date(props.item.due_at).getTime()
  } else if (props.item.created_at) {
    const sla = severityOptions.find((x) => x.value === props.item.severity)?.sla
    if (sla) {
      target = new Date(props.item.created_at).getTime() + sla * 3600 * 1000
    }
  }
  if (!target) return ''
  const remain = (target - Date.now()) / 1000 / 3600
  if (remain <= 0) {
    const over = Math.ceil(-remain)
    if (over >= 24) return `已超时 ${Math.floor(over / 24)}d ${over % 24}h`
    return `已超时 ${over}h`
  }
  if (remain >= 24) {
    return `剩余 ${Math.floor(remain / 24)}d ${Math.floor(remain % 24)}h`
  }
  if (remain >= 1) {
    return `剩余 ${Math.floor(remain)}h ${Math.floor((remain % 1) * 60)}m`
  }
  return `剩余 ${Math.floor(remain * 60)}m`
})

watch(
  () => [props.visible, props.itemId],
  async ([vis, id]) => {
    if (vis && id) {
      await Promise.all([loadDetail(), loadUsers()])
    } else {
      // 关闭时清空
      comments.value = []
      attachments.value = []
      newComment.value = ''
      editingCommentId.value = null
    }
  },
  { immediate: false }
)
// 监听父组件传入的 comment_count：增长时（说明主页菜单/别处发了评论）增量拉新评论
let lastCommentCount = 0
watch(
  () => [props.visible, props.item?.comment_count],
  async ([vis, count]) => {
    if (!vis) {
      lastCommentCount = 0
      return
    }
    if (typeof count !== 'number') return
    if (lastCommentCount === 0) {
      lastCommentCount = count
      return
    }
    if (count > lastCommentCount) {
      // 增量拉取最新评论
      try {
        const res = await rdKanbanService.listComments(props.itemId)
        const list = res.comments || res || []
        // 合并：避免重复（unshift 新评论到现有列表）
        const existingIds = new Set(comments.value.map((c) => c.id))
        list.forEach((c) => {
          if (!existingIds.has(c.id)) comments.value.unshift(c)
        })
      } catch (e) {
        console.error('[CardDetailDrawer] 增量拉取评论失败', e)
      }
    }
    lastCommentCount = count
  },
  { immediate: true }
)

onMounted(() => {
  if (props.visible && props.itemId) {
    loadDetail()
    loadUsers()
  }
})

async function loadDetail() {
  if (!props.itemId) return
  loading.value = true
  try {
    const res = await rdKanbanService.detail(props.itemId)
    comments.value = res.comments || []
    attachments.value = res.attachments || []
  } catch (e) {
    console.error('加载详情失败', e)
    ElMessage.error('加载详情失败')
  } finally {
    loading.value = false
  }
}

let userOptionsLoaded = false
async function loadUsers() {
  // 1) 优先用 props 传入的（避免重复请求）
  if (Array.isArray(props.userOptions) && props.userOptions.length) {
    userOptions.value = props.userOptions
    userOptionsLoaded = true
    return
  }
  if (userOptionsLoaded && userOptions.value.length) return
  try {
    const res = await api.users.getList({ page_size: 200 })
    const list = Array.isArray(res) ? res : (res.items || res.users || res.data || [])
    userOptions.value = (list || []).map((u) => ({
      id: u.id,
      name: (u.first_name || u.last_name)
        ? `${u.first_name || ''}${u.last_name || ''}`.trim()
        : (u.username || u.name || `用户#${u.id}`),
      username: u.username,
      avatar: u.avatar,
    }))
    userOptionsLoaded = true
  } catch (e) {
    console.warn('加载用户列表失败', e)
  }
}

function handleClose(v) {
  emit('update:visible', v)
}

// ----- 标题编辑 -----
function startEditTitle() {
  if (!props.item) return
  editingTitleValue.value = props.item.title
  editingTitle.value = true
  nextTick(() => {
    titleInputRef.value?.focus()
  })
}
async function commitTitle() {
  if (!editingTitle.value) return
  const newTitle = (editingTitleValue.value || '').trim()
  editingTitle.value = false
  if (!newTitle || newTitle === props.item?.title) return
  try {
    await rdKanbanService.update(props.itemId, { title: newTitle })
    if (props.item) props.item.title = newTitle
    ElMessage.success('已更新标题')
    emit('refresh')
  } catch (e) {
    ElMessage.error('更新失败')
  }
}
function cancelTitle() {
  editingTitle.value = false
}
async function copyTitle() {
  if (!props.item?.title) return
  try {
    await navigator.clipboard.writeText(props.item.title)
    ElMessage.success('已复制标题')
  } catch {
    ElMessage.warning('复制失败')
  }
}

// ----- 顶部菜单 -----
function onHeaderCommand(cmd) {
  if (cmd === 'rename') {
    startEditTitle()
  } else if (cmd === 'delete') {
    emit('delete', props.item)
    handleClose(false)
  } else if (cmd === 'status') {
    cycleStatus()
  } else if (cmd === 'assignee') {
    cycleAssignee()
  }
}

// 状态快速切换（当用户从更多菜单点"设置状态"时）
function cycleStatus() {
  if (!props.item) return
  const cur = props.item.status
  const idx = statusOptions.value.findIndex((s) => s.value === cur)
  const next = statusOptions.value[(idx + 1) % statusOptions.value.length]
  handleStatusChange(next.value)
}

function cycleAssignee() {
  if (!props.item || !userOptions.value.length) {
    ElMessage.warning('暂无可指派用户')
    return
  }
  const cur = props.item.assignee?.id
  const idx = userOptions.value.findIndex((u) => u.id === cur)
  const next = userOptions.value[(idx + 1) % userOptions.value.length]
  handleAssigneeChange(String(next.id))
}

// ----- 移至其他列 -----
async function handleMoveToColumn(colKey) {
  if (!props.item || colKey === props.item.column) return
  const target = props.columns.find((c) => c.key === colKey)
  if (!target) return
  try {
    await rdKanbanService.sort([{ id: props.itemId, column: colKey, sort_order: 0 }])
    if (props.item) props.item.column = colKey
    ElMessage.success(`已移至「${target.name}」`)
    emit('refresh')
  } catch (e) {
    console.error(e)
    ElMessage.error('移动失败')
  }
}

// ----- 设置状态 -----
async function handleStatusChange(statusValue) {
  if (!props.item) return
  if (statusValue === props.item.status) return
  const s = statusOptions.value.find((x) => x.value === statusValue)
  try {
    await rdKanbanService.update(props.itemId, {
      status: statusValue,
      status_color: s?.color || '#94a3b8',
    })
    props.item.status = statusValue
    props.item.status_color = s?.color || '#94a3b8'
    ElMessage.success(`已设为：${s?.label || statusValue}`)
    emit('refresh')
  } catch (e) {
    console.error(e)
    ElMessage.error('状态更新失败')
  }
}

// ----- 指派 / 取消指派 -----
async function handleAssigneeChange(cmd) {
  if (!props.item) return
  // 取消指派
  if (cmd === '__unassign__') {
    try {
      await rdKanbanService.update(props.itemId, { assignee_id: null })
      props.item.assignee = null
      ElMessage.success('已取消指派')
      emit('refresh')
    } catch (e) {
      ElMessage.error('操作失败')
    }
    return
  }
  const userId = Number(cmd)
  if (!userId) return
  const u = userOptions.value.find((x) => x.id === userId)
  if (!u) return
  try {
    await rdKanbanService.update(props.itemId, { assignee_id: userId })
    props.item.assignee = {
      id: u.id,
      name: u.name,
      username: u.username,
      avatar: u.avatar,
    }
    ElMessage.success(`已指派给：${u.name}`)
    emit('refresh')
  } catch (e) {
    console.error(e)
    ElMessage.error('指派失败')
  }
}

// ----- 客户问题严重度 -----
async function handleSeverityChange(sev) {
  if (!props.item) return
  if (sev === props.item.severity) return
  const s = severityOptions.find((x) => x.value === sev)
  try {
    // 后端会在 severity 改变时按 SLA 重新计算 due_at
    const res = await rdKanbanService.update(props.itemId, { severity: sev })
    if (res && res.item) {
      props.item.severity = res.item.severity
      props.item.due_at = res.item.due_at
    } else {
      props.item.severity = sev
    }
    ElMessage.success(`已设为：${s?.label || sev}`)
    emit('refresh')
  } catch (e) {
    console.error(e)
    ElMessage.error('严重度更新失败')
  }
}

// ----- 附件 -----
function triggerFileInput() {
  fileInputRef.value?.click()
}
function handleFileSelect(e) {
  const files = Array.from(e.target.files || [])
  uploadFiles(files)
  e.target.value = ''
}
function handleDrop(e) {
  isDragover.value = false
  const files = Array.from(e.dataTransfer.files || [])
  uploadFiles(files)
}
async function uploadFiles(files) {
  for (const file of files) {
    if (file.size > 20 * 1024 * 1024) {
      ElMessage.warning(`文件 ${file.name} 超过 20MB，已跳过`)
      continue
    }
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await rdKanbanService.uploadAttachment(props.itemId, form)
      attachments.value.unshift(res.attachment)
      ElMessage.success(`${file.name} 上传成功`)
    } catch (e) {
      console.error(e)
      ElMessage.error(`上传失败：${file.name}`)
    }
  }
}
async function downloadAttachment(att) {
  try {
    const token = localStorage.getItem('token')
    const resp = await fetch(rdKanbanService.attachmentDownloadUrl(att.id), {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!resp.ok) {
      ElMessage.error('下载失败')
      return
    }
    const blob = await resp.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = att.original_name
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error(e)
    ElMessage.error('下载失败')
  }
}
function isPreviewable(att) {
  const name = (att?.original_name || '').toLowerCase()
  const dot = name.lastIndexOf('.')
  if (dot < 0) return false
  const ext = name.slice(dot + 1)
  return PREVIEW_EXTENSIONS.includes(ext)
}
async function previewAttachment(att) {
  if (!isPreviewable(att)) {
    ElMessage.warning('该文件类型不支持在线预览')
    return
  }
  previewVisible.value = true
  previewLoading.value = true
  previewContent.value = ''
  previewMeta.value = { original_name: att.original_name }
  try {
    const res = await rdKanbanService.getAttachmentRaw(att.id)
    if (res?.success) {
      previewContent.value = res.content || ''
      previewMeta.value = {
        encoding: res.encoding,
        size: res.size,
        line_count: res.line_count,
        truncated: res.truncated,
        original_name: res.original_name,
      }
    } else {
      ElMessage.error(res?.error || '预览失败')
      previewContent.value = '（加载失败）'
    }
  } catch (e) {
    console.error('[previewAttachment] error', e)
    const msg = e?.response?.data?.error || e?.message || '预览失败'
    ElMessage.error(msg)
    previewContent.value = '（加载失败）'
  } finally {
    previewLoading.value = false
  }
}
async function copyPreviewContent() {
  if (!previewContent.value) return
  try {
    await navigator.clipboard.writeText(previewContent.value)
    ElMessage.success('已复制到剪贴板')
  } catch (e) {
    // 退化方案
    const ta = document.createElement('textarea')
    ta.value = previewContent.value
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    ElMessage.success('已复制到剪贴板')
  }
}
async function deleteAttachment(att) {
  try {
    await ElMessageBox.confirm(`确定删除附件 ${att.original_name}？`, '提示', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      confirmButtonClass: 'el-button--danger',
    })
    await rdKanbanService.deleteAttachment(att.id)
    attachments.value = attachments.value.filter((a) => a.id !== att.id)
    ElMessage.success('已删除')
  } catch (e) {
    if (e !== 'cancel' && e?.message) ElMessage.error('删除失败')
  }
}

// ----- 评论 -----
function insertMarkdown(before, after) {
  const ta = document.querySelector('.rd-detail-dialog .editor-textarea')
  if (!ta) return
  const start = ta.selectionStart
  const end = ta.selectionEnd
  const text = newComment.value
  const selected = text.substring(start, end)
  const inserted = before + (selected || '文本') + after
  newComment.value = text.substring(0, start) + inserted + text.substring(end)
  nextTick(() => {
    ta.focus()
    const pos = start + before.length + (selected || '文本').length
    ta.setSelectionRange(pos, pos)
  })
}
function addEmoji(emoji) {
  newComment.value += emoji
}
async function submitComment() {
  const content = newComment.value.trim()
  if (!content) return
  submitting.value = true
  try {
    const payload = { content }
    if (replyingTo.value) {
      payload.parent_id = replyingTo.value.id
    }
    const res = await rdKanbanService.addComment(props.itemId, payload)
    comments.value.unshift(res.comment)
    newComment.value = ''
    replyingTo.value = null
    // 同步更新 card.comment_count
    if (props.item) {
      props.item.comment_count = (props.item.comment_count || 0) + 1
    }
    ElMessage.success(replyingTo.value ? '回复已发布' : '评论已发布')
    emit('refresh')
  } catch (e) {
    ElMessage.error('发布失败')
  } finally {
    submitting.value = false
  }
}
function startReplyComment(c) {
  replyingTo.value = { id: c.id, name: c.user?.name || '未知用户', content: c.content }
  newComment.value = ''
  // 滚动到评论输入框
  nextTick(() => {
    const editor = document.querySelector('.comment-editor .editor-textarea')
    if (editor) editor.focus()
  })
}
function cancelReplyComment() {
  replyingTo.value = null
}
function isCommentMine(c) {
  if (!c || !c.user) return false
  const cid = c.user.id
  const myId = currentUserId.value
  if (cid == null || myId == null || myId === 0) return false
  // 类型归一化：避免 "1" !== 1
  return String(cid) === String(myId)
}
// 评论作者是否是管理员（用于显示徽章）
function isCommentAuthorAdmin(c) {
  // 后端 _serialize_comment 只返回了 user {id, name, username, avatar}，role 字段不会带过来
  // 但 admnia 是当前已知的内置管理员账户，且 role === 'admin'
  // 因此：通过 username 命中 "admin" / "admina" / "administrator" 这几个常见账号视为管理员
  if (!c || !c.user) return false
  const u = c.user
  const username = (u.username || u.name || '').toLowerCase()
  if (!username) return false
  return ['admin', 'admina', 'administrator', 'superadmin', 'root'].includes(username)
}
// admin 拥有一切权限（编辑 / 删除任何评论），无需是作者本人
function canEdit(c) {
  if (isAdmin.value) return true
  return isCommentMine(c)
}
function canDelete(c) {
  if (isAdmin.value) return true
  return isCommentMine(c)
}
// 无权限时的提示文案：当前用户是 admin 时显示 "管理员拥有一切权限" 之类的友好提示
function noEditTip(c) {
  if (isAdmin.value) return '管理员拥有编辑一切评论的权限' // 不会出现，仅防御
  return isCommentMine(c) ? '你暂无编辑权限' : '仅评论作者或管理员可编辑'
}
function noDeleteTip(c) {
  if (isAdmin.value) return '管理员拥有删除一切评论的权限'
  return isCommentMine(c) ? '你暂无删除权限' : '仅评论作者或管理员可删除'
}
// 把扁平 comments[] 转成树：parent_id 为空的视为顶级；其它按 parent_id 挂到对应父评论的 replies
const commentTree = computed(() => {
  const list = Array.isArray(comments.value) ? comments.value : []
  const byId = new Map()
  const roots = []
  list.forEach((c) => {
    byId.set(c.id, { ...c, replies: [] })
  })
  list.forEach((c) => {
    const node = byId.get(c.id)
    if (c.parent_id && byId.has(c.parent_id)) {
      byId.get(c.parent_id).replies.push(node)
    } else {
      // 找不到父评论的也按顶级展示（防御性）
      roots.push(node)
    }
  })
  // 顶级按 created_at 升序（旧的在前），回复也按升序
  roots.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
  roots.forEach((r) => r.replies.sort((a, b) => new Date(a.created_at) - new Date(b.created_at)))
  return roots
})
function startEditComment(c) {
  editingCommentId.value = c.id
  editingCommentContent.value = c.content
}
async function saveEditComment(c) {
  const newContent = editingCommentContent.value.trim()
  if (!newContent) {
    ElMessage.warning('内容不能为空')
    return
  }
  try {
    const res = await rdKanbanService.updateComment(c.id, { content: newContent })
    Object.assign(c, res.comment)
    editingCommentId.value = null
    ElMessage.success('已更新')
  } catch (e) {
    ElMessage.error('更新失败')
  }
}
async function deleteCommentItem(c) {
  try {
    await ElMessageBox.confirm('确定删除此评论？', '提示', { type: 'warning' })
    await rdKanbanService.deleteComment(c.id)
    comments.value = comments.value.filter((x) => x.id !== c.id)
    if (props.item && (props.item.comment_count || 0) > 0) {
      props.item.comment_count -= 1
    }
    ElMessage.success('已删除')
    emit('refresh')
  } catch (e) {
    if (e !== 'cancel' && e?.message) ElMessage.error('删除失败')
  }
}

function showEmojiPicker(c) {
  emojiPickerTarget.value = c
  emojiPickerVisible.value = true
}
function pickEmoji(emoji) {
  if (emojiPickerTarget.value) {
    toggleReaction(emojiPickerTarget.value, emoji)
  }
  emojiPickerVisible.value = false
}
async function toggleReaction(c, emoji) {
  try {
    const res = await rdKanbanService.reactComment(c.id, emoji)
    c.reactions = res.reactions
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

// ----- 简易 Markdown 渲染 -----
function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}
function renderMarkdown(text) {
  if (!text) return ''
  // 1) 提取代码块
  const codeBlocks = []
  let s = text.replace(/```([\s\S]*?)```/g, (m, code) => {
    const i = codeBlocks.length
    codeBlocks.push(escapeHtml(code))
    return `@@CODEBLOCK_${i}@@`
  })
  s = escapeHtml(s)
  // 行内代码
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>')
  // 粗体
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  // 斜体
  s = s.replace(/\*([^*]+)\*/g, '<em>$1</em>')
  // 删除线
  s = s.replace(/~~([^~]+)~~/g, '<del>$1</del>')
  // 链接
  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
  // 列表
  s = s.replace(/(^|\n)((?:- [^\n]+\n?)+)/g, (m, pre, list) => {
    const items = list.trim().split(/\n- /).filter(Boolean).map((x) => `<li>${x.trim()}</li>`).join('')
    return `${pre}<ul>${items}</ul>`
  })
  s = s.replace(/(^|\n)((?:\d+\. [^\n]+\n?)+)/g, (m, pre, list) => {
    const items = list.trim().split(/\n\d+\. /).filter(Boolean).map((x) => `<li>${x.trim()}</li>`).join('')
    return `${pre}<ol>${items}</ol>`
  })
  // 换行
  s = s.replace(/\n/g, '<br/>')
  // 还原代码块
  s = s.replace(/@@CODEBLOCK_(\d+)@@/g, (m, i) => `<pre><code>${codeBlocks[Number(i)] || ''}</code></pre>`)
  return s
}

// ----- 工具 -----
function avatarText(name) {
  if (!name) return '?'
  return name.slice(-2)
}
function formatSize(b) {
  if (!b && b !== 0) return ''
  if (b < 1024) return b + ' B'
  if (b < 1024 * 1024) return (b / 1024).toFixed(1) + ' KB'
  return (b / 1024 / 1024).toFixed(2) + ' MB'
}
function formatTime(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    const now = new Date()
    const diff = (now - d) / 1000
    if (diff < 60) return '刚刚'
    if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
    if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
    if (diff < 604800) return `${Math.floor(diff / 86400)} 天前`
    return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}
function iconColor(mime) {
  if (!mime) return '#94a3b8'
  if (mime.startsWith('image/')) return '#10b981'
  if (mime.includes('pdf')) return '#ef4444'
  if (mime.includes('zip') || mime.includes('rar')) return '#f59e0b'
  if (mime.includes('word') || mime.includes('document')) return '#3b82f6'
  if (mime.includes('sheet') || mime.includes('excel')) return '#059669'
  return '#8b5cf6'
}
</script>

<style scoped>
.detail-container {
  display: flex;
  flex-direction: column;
  min-height: 0;
  max-height: 92vh;
  background: linear-gradient(180deg, #fafbff 0%, #f5f7fa 100%);
}

/* Header */
.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 18px 12px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
  position: sticky;
  top: 0;
  z-index: 5;
}
.header-left {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 500;
  padding: 3px 8px;
  border-radius: 10px;
  border: 1px solid;
  white-space: nowrap;
  flex-shrink: 0;
}
.status-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
}
.detail-title-wrap {
  flex: 1;
  min-width: 0;
}
.detail-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
  cursor: text;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.detail-title-input {
  width: 100%;
  border: 1px solid #0ea5e9;
  border-radius: 4px;
  padding: 3px 6px;
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  background: #fff;
  outline: none;
  font-family: inherit;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}
.hdr-btn {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  font-size: 14px;
}
.hdr-btn:hover {
  background: rgba(15, 23, 42, 0.06);
  color: #0f172a;
}
.hdr-btn.close:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* Meta strip */
.meta-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 10px 18px;
  background: rgba(255, 255, 255, 0.5);
  border-bottom: 1px solid rgba(15, 23, 42, 0.05);
}
.meta-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  background: rgba(15, 23, 42, 0.05);
  border-radius: 12px;
  font-size: 11px;
  color: #475569;
  transition: all 0.15s ease;
}
.meta-pill .el-icon {
  font-size: 12px;
}
.meta-pill .caret {
  font-size: 10px;
  opacity: 0.7;
  margin-left: 2px;
}
.meta-pill.column-pill,
.meta-pill.assignee-pill,
.meta-pill.status-pill,
.meta-pill.severity-pill {
  cursor: pointer;
  user-select: none;
  border: 1px solid transparent;
}
.meta-pill.column-pill:hover,
.meta-pill.assignee-pill:hover,
.meta-pill.status-pill:hover,
.meta-pill.severity-pill:hover {
  filter: brightness(0.97);
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.08);
}
.col-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
  flex-shrink: 0;
}
.sla-text {
  font-weight: 500;
  opacity: 0.85;
}

/* Body */
.detail-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 18px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.detail-body::-webkit-scrollbar {
  width: 6px;
}
.detail-body::-webkit-scrollbar-thumb {
  background: rgba(15, 23, 42, 0.15);
  border-radius: 3px;
}
.detail-section {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 10px;
  padding: 14px;
}
.section-title {
  margin: 0 0 10px;
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
  display: flex;
  align-items: center;
  gap: 6px;
}
.section-title .hint {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 400;
  margin-left: 4px;
}
.section-actions {
  margin-left: auto;
  display: flex;
  gap: 2px;
}
.icon-btn {
  width: 22px;
  height: 22px;
  border-radius: 4px;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}
.icon-btn:hover {
  background: rgba(15, 23, 42, 0.06);
  color: #0f172a;
}
.icon-btn.active {
  color: #0ea5e9;
  background: rgba(14, 165, 233, 0.1);
}

/* Upload */
.upload-zone {
  border: 1.5px dashed rgba(15, 23, 42, 0.18);
  border-radius: 8px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.5);
  transition: all 0.15s ease;
  margin-bottom: 10px;
}
.upload-zone:hover {
  border-color: #0ea5e9;
  color: #0ea5e9;
  background: rgba(14, 165, 233, 0.04);
}
.upload-zone.is-dragover {
  border-color: #0ea5e9;
  background: rgba(14, 165, 233, 0.08);
  color: #0ea5e9;
}
.upload-icon {
  font-size: 20px;
}
.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.attachment-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  background: #fff;
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 8px;
  transition: all 0.15s ease;
}
.attachment-item:hover {
  border-color: rgba(14, 165, 233, 0.3);
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.05);
}
.att-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  flex-shrink: 0;
}
.att-info {
  flex: 1;
  min-width: 0;
}
.att-name {
  font-size: 12px;
  font-weight: 500;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.att-meta {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 1px;
}
.att-actions {
  display: flex;
  gap: 2px;
  flex-shrink: 0;
}
.att-action-btn {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  opacity: 0;
  transition: all 0.15s ease;
}
.attachment-item:hover .att-action-btn {
  opacity: 1;
}
.att-action-btn:hover {
  background: rgba(15, 23, 42, 0.06);
  color: #0ea5e9;
}
.att-action-btn.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* Comment editor */
.comment-editor {
  background: #fff;
  border: 1px solid rgba(15, 23, 42, 0.1);
  border-radius: 8px;
  margin-bottom: 12px;
  transition: border-color 0.15s ease;
}
.comment-editor:focus-within {
  border-color: #0ea5e9;
  box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.1);
}
.editor-toolbar {
  display: flex;
  gap: 2px;
  padding: 6px 8px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.05);
}
.tool-btn {
  min-width: 24px;
  height: 24px;
  border-radius: 4px;
  border: none;
  background: transparent;
  color: #475569;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
  font-size: 12px;
  transition: all 0.12s ease;
}
.tool-btn:hover {
  background: rgba(15, 23, 42, 0.06);
  color: #0ea5e9;
}
.editor-textarea {
  width: 100%;
  border: none;
  outline: none;
  padding: 8px 10px;
  font-size: 13px;
  line-height: 1.5;
  font-family: inherit;
  color: #0f172a;
  resize: vertical;
  background: transparent;
  min-height: 60px;
}
.editor-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  border-top: 1px solid rgba(15, 23, 42, 0.05);
}
.char-count {
  font-size: 11px;
  color: #94a3b8;
}
.editor-actions {
  display: flex;
  gap: 6px;
}
.btn-gradient {
  background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%) !important;
  border: none !important;
  color: #fff !important;
}
.btn-gradient:hover {
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.35);
}

/* Comment list */
.comment-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.comment-item {
  display: flex;
  gap: 10px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-left: 3px solid #0ea5e9;
  border-radius: 8px;
  transition: all 0.15s ease;
}
.comment-item:hover {
  background: rgba(255, 255, 255, 0.85);
  border-color: rgba(14, 165, 233, 0.3);
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
}
.comment-item.is-self {
  border-left-color: #10b981;
  background: rgba(16, 185, 129, 0.04);
}
.comment-item.is-reply-target {
  border-left-color: #f59e0b;
  background: rgba(245, 158, 11, 0.04);
}
.comment-avatar {
  flex-shrink: 0;
  border: 1.5px solid #fff;
  box-shadow: 0 0 0 1px rgba(15, 23, 42, 0.08);
}
.comment-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.comment-head {
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.comment-author {
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
}
.comment-time {
  font-size: 10px;
  color: #94a3b8;
}
.comment-content {
  font-size: 13px;
  line-height: 1.6;
  color: #1e293b;
  word-break: break-word;
  white-space: pre-wrap;
  padding: 2px 0;
}
.comment-content :deep(code) {
  background: rgba(15, 23, 42, 0.06);
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 12px;
  font-family: 'Consolas', 'Monaco', monospace;
}
.comment-content :deep(pre) {
  background: rgba(15, 23, 42, 0.06);
  padding: 8px 10px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 12px;
  margin: 6px 0;
}
.comment-content :deep(pre code) {
  background: transparent;
  padding: 0;
}
.comment-content :deep(ul),
.comment-content :deep(ol) {
  margin: 4px 0;
  padding-left: 20px;
}
.comment-content :deep(a) {
  color: #0ea5e9;
  text-decoration: none;
}
.comment-content :deep(a:hover) {
  text-decoration: underline;
}
.comment-edit {
  margin: 4px 0;
}
.comment-reactions {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
  align-items: center;
}
.reaction-pill {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 2px 8px;
  background: rgba(15, 23, 42, 0.05);
  border: 1px solid transparent;
  border-radius: 12px;
  font-size: 11px;
  cursor: pointer;
  user-select: none;
  transition: all 0.12s ease;
}
.reaction-pill:hover {
  background: rgba(14, 165, 233, 0.1);
  border-color: rgba(14, 165, 233, 0.3);
}
.reaction-pill.mine {
  background: rgba(14, 165, 233, 0.15);
  border-color: rgba(14, 165, 233, 0.4);
}
.add-reaction-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border: 1px dashed rgba(15, 23, 42, 0.2);
  border-radius: 12px;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  font-size: 10px;
  opacity: 0;
  transition: all 0.15s ease;
}
.comment-item:hover .add-reaction-btn {
  opacity: 1;
}
.add-reaction-btn:hover {
  background: rgba(14, 165, 233, 0.08);
  border-color: #0ea5e9;
  color: #0ea5e9;
}
.comment-actions {
  margin-top: 4px;
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.15s ease;
  align-items: center;
}
.comment-item:hover .comment-actions,
.comment-actions.always-show {
  opacity: 1;
}
.comment-actions :deep(.el-button) {
  font-size: 11px;
  padding: 2px 6px;
}
.comment-actions :deep(.el-button.is-disabled) {
  cursor: not-allowed;
}
.comment-action-wrap {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}
.lock-icon {
  font-size: 11px;
  color: #cbd5e1;
}
.comment-empty {
  text-align: center;
  color: #94a3b8;
  font-size: 12px;
  padding: 16px 0;
}
.reply-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  margin: 8px 0 4px;
  background: rgba(14, 165, 233, 0.08);
  border: 1px solid rgba(14, 165, 233, 0.25);
  border-left: 3px solid #0ea5e9;
  border-radius: 6px;
  color: #0f172a;
  font-size: 12px;
  line-height: 1.4;
}
.reply-banner-icon {
  color: #0ea5e9;
  font-size: 14px;
  flex-shrink: 0;
}
.reply-banner-text {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.reply-banner-content {
  color: #64748b;
  font-weight: normal;
}
.reply-banner-close {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  padding: 2px;
  display: flex;
  align-items: center;
  border-radius: 4px;
  transition: all 0.15s ease;
}
.reply-banner-close:hover {
  background: rgba(14, 165, 233, 0.12);
  color: #0ea5e9;
}
.comment-reply {
  margin: 6px 0 0 38px;
  padding: 6px 10px;
  background: rgba(15, 23, 42, 0.04);
  border-left: 2px solid #cbd5e1;
  border-radius: 4px;
  font-size: 12px;
  color: #475569;
}
.comment-reply-author {
  font-weight: 600;
  color: #0ea5e9;
  margin-right: 6px;
}

/* 评论树形结构：thread 包裹一个顶级评论 + 其回复 */
.comment-thread {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.comment-replies {
  margin-top: 2px;
  margin-left: 38px;
  padding-left: 8px;
  border-left: 2px dashed rgba(14, 165, 233, 0.35);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.comment-reply-item {
  padding: 8px 10px !important;
  border-left-width: 2px !important;
  border-left-color: #94a3b8 !important;
  background: rgba(241, 245, 249, 0.65) !important;
  font-size: 12px;
}
.comment-reply-item:hover {
  background: rgba(241, 245, 249, 0.95) !important;
}
.comment-reply-item .comment-content {
  font-size: 12.5px;
  line-height: 1.55;
}
.comment-reply-item .comment-avatar {
  width: 22px !important;
  height: 22px !important;
}
.reply-to-tag {
  font-size: 11px;
  color: #64748b;
  margin-left: 4px;
}
.reply-to-tag strong {
  color: #0ea5e9;
  font-weight: 600;
  margin: 0 2px;
}
.admin-badge {
  height: 16px !important;
  line-height: 14px !important;
  padding: 0 5px !important;
  font-size: 10px !important;
  border-radius: 4px !important;
  margin-left: 4px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

/* Emoji picker */
.emoji-picker-anchor {
  display: none;
}
.emoji-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 2px;
  max-height: 180px;
  overflow-y: auto;
}
.emoji-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  font-size: 18px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.1s ease;
}
.emoji-item:hover {
  background: rgba(15, 23, 42, 0.06);
  transform: scale(1.15);
}
</style>

<style>
/* 居中弹窗全局样式：自适应内容高度，不强制填满屏幕 */
.rd-detail-dialog {
  border-radius: 14px !important;
  overflow: hidden;
  padding: 0;
  margin: 4vh auto !important;
  min-height: 320px;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
}
.rd-detail-dialog .el-dialog__header {
  display: none;
}
.rd-detail-dialog .el-dialog__body {
  padding: 0;
  max-height: 92vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 文本附件预览弹窗 */
.rd-attachment-preview-dialog {
  border-radius: 12px;
  overflow: hidden;
}
.rd-attachment-preview-dialog .preview-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  padding: 0 4px 12px;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.rd-attachment-preview-dialog .preview-content {
  margin: 0;
  padding: 14px 16px;
  background: #1e293b;
  color: #e2e8f0;
  border-radius: 8px;
  font-family: 'JetBrains Mono', 'Cascadia Code', 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 60vh;
  overflow: auto;
}
.rd-attachment-preview-dialog .preview-loading {
  margin: 0;
  padding: 60px 16px;
  background: #1e293b;
  color: #94a3b8;
  border-radius: 8px;
  text-align: center;
  font-size: 14px;
}
</style>
