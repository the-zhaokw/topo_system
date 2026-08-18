<template>
  <el-drawer
    :model-value="visible"
    :title="null"
    direction="rtl"
    size="520px"
    :with-header="false"
    :destroy-on-close="false"
    :modal="true"
    custom-class="rd-detail-drawer"
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

      <!-- 元信息条 -->
      <div class="meta-strip" v-if="item">
        <div class="meta-pill">
          <el-icon><Folder /></el-icon>
          <span>{{ columnName || '—' }}</span>
        </div>
        <div class="meta-pill" v-if="item.assignee">
          <el-avatar :size="18" :src="item.assignee.avatar">
            {{ avatarText(item.assignee.name) }}
          </el-avatar>
          <span>{{ item.assignee.name }}</span>
        </div>
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
            <div v-for="att in attachments" :key="att.id" class="attachment-item">
              <div class="att-icon" :style="{ background: iconColor(att.mime_type) }">
                <el-icon><Document /></el-icon>
              </div>
              <div class="att-info">
                <div class="att-name" :title="att.original_name">{{ att.original_name }}</div>
                <div class="att-meta">
                  {{ formatSize(att.file_size) }} ·
                  <span v-if="att.uploader">{{ att.uploader.name }}</span>
                  <span v-else>匿名</span>
                  · {{ formatTime(att.uploaded_at) }}
                </div>
              </div>
              <div class="att-actions">
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
            <textarea
              v-model="newComment"
              class="editor-textarea"
              :placeholder="mdMode ? '支持 Markdown 语法（**加粗** *斜体* [链接](url) - 列表）...' : '发表评论...'"
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
            <div v-for="c in comments" :key="c.id" class="comment-item">
              <el-avatar :size="28" :src="c.user?.avatar" class="comment-avatar">
                {{ avatarText(c.user?.name) }}
              </el-avatar>
              <div class="comment-body">
                <div class="comment-head">
                  <span class="comment-author">{{ c.user?.name || '未知用户' }}</span>
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
                <!-- 操作 -->
                <div class="comment-actions" v-if="canEdit(c) || canDelete(c)">
                  <el-button v-if="canEdit(c)" text size="small" @click="startEditComment(c)">编辑</el-button>
                  <el-button v-if="canDelete(c)" text size="small" type="danger" @click="deleteCommentItem(c)">删除</el-button>
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
  </el-drawer>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Link, FullScreen, MoreFilled, Flag, User, EditPen, Delete, Close,
  Folder, Clock, ChatDotRound, Paperclip, Plus, Document, Download,
  List, Sunny, CopyDocument,
} from '@element-plus/icons-vue'
import rdKanbanService from '@/services/rdKanbanService'
import { useUserStore } from '@/stores/user'

const props = defineProps({
  visible: { type: Boolean, default: false },
  itemId: { type: [Number, String], default: null },
  item: { type: Object, default: null },
  columns: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:visible', 'refresh', 'maximize', 'delete'])

const userStore = useUserStore()
const currentUserId = computed(() => userStore.user?.id || 0)
const currentUserName = computed(() => userStore.user?.username || '')

const loading = ref(false)
const submitting = ref(false)

// 详情
const comments = ref([])
const attachments = ref([])

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
  return props.item.status
})

watch(
  () => [props.visible, props.itemId],
  async ([vis, id]) => {
    if (vis && id) {
      await loadDetail()
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

onMounted(() => {
  if (props.visible && props.itemId) {
    loadDetail()
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
  } else if (cmd === 'status' || cmd === 'assignee') {
    ElMessage.info('请在卡片右键菜单中操作（' + (cmd === 'status' ? '状态' : '指派') + '）')
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
  const ta = document.querySelector('.rd-detail-drawer .editor-textarea')
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
    const res = await rdKanbanService.addComment(props.itemId, { content })
    comments.value.unshift(res.comment)
    newComment.value = ''
    // 同步更新 card.comment_count
    if (props.item) {
      props.item.comment_count = (props.item.comment_count || 0) + 1
    }
    ElMessage.success('评论已发布')
    emit('refresh')
  } catch (e) {
    ElMessage.error('发布失败')
  } finally {
    submitting.value = false
  }
}
function canEdit(c) {
  return c.user?.id === currentUserId.value || userStore.user?.role === 'admin'
}
function canDelete(c) {
  return c.user?.id === currentUserId.value || userStore.user?.role === 'admin'
}
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
  height: 100%;
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
}
.meta-pill .el-icon {
  font-size: 12px;
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
  gap: 14px;
}
.comment-item {
  display: flex;
  gap: 10px;
}
.comment-avatar {
  flex-shrink: 0;
  border: 1.5px solid #fff;
  box-shadow: 0 0 0 1px rgba(15, 23, 42, 0.08);
}
.comment-body {
  flex: 1;
  min-width: 0;
}
.comment-head {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 4px;
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
  line-height: 1.55;
  color: #1e293b;
  word-break: break-word;
  white-space: pre-wrap;
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
}
.comment-actions :deep(.el-button) {
  font-size: 11px;
  padding: 2px 6px;
}
.comment-empty {
  text-align: center;
  color: #94a3b8;
  font-size: 12px;
  padding: 16px 0;
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
/* 抽屉全局样式 */
.rd-detail-drawer {
  border-top-left-radius: 14px !important;
  border-bottom-left-radius: 14px !important;
  overflow: hidden;
}
.rd-detail-drawer .el-drawer__body {
  padding: 0;
  height: 100%;
  overflow: hidden;
}
.rd-detail-drawer .el-drawer__header {
  display: none;
}
</style>
