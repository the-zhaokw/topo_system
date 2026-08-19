<template>
  <div class="weekly-report-card" :class="{ 'is-pinned': item.is_pinned, 'is-expanded': expanded }">
    <!-- 卡片头部 -->
    <div class="wr-card-header" @click="toggleExpand">
      <div class="wr-card-pin" v-if="item.is_pinned">
        <el-icon><Flag /></el-icon>
      </div>
      <div class="wr-card-main">
        <div class="wr-card-title-row">
          <span class="wr-card-title">{{ item.title }}</span>
          <el-icon class="wr-expand-icon" :class="{ rotated: expanded }"><ArrowDown /></el-icon>
        </div>
        <div class="wr-card-meta">
          <span class="wr-meta-item">
            <el-icon><AlarmClock /></el-icon>
            {{ item.created_at ? item.created_at.slice(0, 10) : '未知日期' }}
          </span>
          <span class="wr-meta-item wr-author" v-if="item.assignee">
            <el-icon><User /></el-icon>
            {{ item.assignee.name || item.assignee.username || '未指派' }}
          </span>
          <el-tag
            v-if="item.status"
            size="small"
            effect="light"
          >
            {{ statusLabel }}
          </el-tag>
          <span class="wr-meta-item wr-comment-count" v-if="item.comment_count > 0">
            <el-icon><ChatDotRound /></el-icon>
            {{ item.comment_count }}
          </span>
        </div>
      </div>
    </div>

    <!-- 展开内容 -->
    <div class="wr-card-body" v-if="expanded" v-loading="loading">
      <!-- 周报内容 -->
      <div class="wr-report-content" v-html="renderMarkdown(item.title)" />

      <el-divider content-position="left">
        <span class="wr-comment-section-title">
          <el-icon><ChatDotRound /></el-icon>
          评论 {{ comments.length }}
        </span>
      </el-divider>

      <!-- 评论输入区 -->
      <div class="comment-editor">
        <div class="editor-toolbar">
          <button class="tool-btn" @click="insertMarkdown('**', '**')" title="加粗"><strong>B</strong></button>
          <button class="tool-btn" @click="insertMarkdown('*', '*')" title="斜体"><em>I</em></button>
          <button class="tool-btn" @click="insertMarkdown('~~', '~~')" title="删除线"><s>S</s></button>
          <button class="tool-btn" @click="insertMarkdown('\n- ', '')" title="列表"><el-icon><List /></el-icon></button>
          <button class="tool-btn" @click="insertMarkdown('\n1. ', '')" title="有序列表"><span style="font-weight:600">1.</span></button>
          <button class="tool-btn" @click="insertMarkdown('\n```\n', '\n```\n')" title="代码块"><span>{ }</span></button>
          <button class="tool-btn" @click="insertMarkdown('[', '](url)')" title="链接"><el-icon><Link /></el-icon></button>
          <button class="tool-btn" @click="addEmoji('😊')" title="表情"><el-icon><Sunny /></el-icon></button>
        </div>
        <div v-if="replyingTo" class="reply-banner">
          <el-icon class="reply-banner-icon"><ChatDotRound /></el-icon>
          <span class="reply-banner-text">
            正在回复 <strong>@{{ replyingTo.name }}</strong>
            <span class="reply-banner-content">：{{ replyingTo.content }}</span>
          </span>
          <button class="reply-banner-close" @click="cancelReplyComment">
            <el-icon><Close /></el-icon>
          </button>
        </div>
        <textarea
          ref="editorRef"
          v-model="newComment"
          class="editor-textarea"
          :placeholder="replyingTo ? `回复 @${replyingTo.name} ...` : '支持 Markdown 语法...'"
          rows="3"
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

      <!-- 表情选择器 -->
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
              <!-- 操作按钮 -->
              <div class="comment-actions always-show">
                <el-button text size="small" @click="startReplyComment(c)">回复</el-button>
                <el-tooltip v-if="!canEdit(c)" :content="noEditTip(c)" placement="top">
                  <span class="comment-action-wrap">
                    <el-icon class="lock-icon"><Lock /></el-icon>
                    <el-button text size="small" disabled>编辑</el-button>
                  </span>
                </el-tooltip>
                <el-button v-else text size="small" @click="startEditComment(c)">编辑</el-button>
                <el-tooltip v-if="!canDelete(c)" :content="noDeleteTip(c)" placement="top">
                  <span class="comment-action-wrap">
                    <el-icon class="lock-icon"><Lock /></el-icon>
                    <el-button text size="small" type="danger" disabled>删除</el-button>
                  </span>
                </el-tooltip>
                <el-button v-else text size="small" type="danger" @click="deleteCommentItem(c)">删除</el-button>
              </div>
            </div>
          </div>

          <!-- 回复子列表 -->
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
                <div class="comment-reactions" v-if="r.reactions && Object.keys(r.reactions).length">
                  <span
                    v-for="(uids, emoji) in r.reactions"
                    :key="emoji"
                    class="reaction-pill"
                    :class="{ mine: uids.includes(currentUserId) }"
                    @click="toggleReaction(r, emoji)"
                  >
                    {{ emoji }} {{ uids.length }}
                  </span>
                  <button class="add-reaction-btn" @click="showEmojiPicker(r)" title="添加反应">
                    <el-icon><Sunny /></el-icon>
                  </button>
                </div>
                <div v-else class="comment-reactions">
                  <button class="add-reaction-btn" @click="showEmojiPicker(r)" title="添加反应">
                    <el-icon><Sunny /></el-icon>
                  </button>
                </div>
                <div class="comment-actions always-show">
                  <el-button text size="small" @click="startReplyComment(r)">回复</el-button>
                  <el-tooltip v-if="!canEdit(r)" :content="noEditTip(r)" placement="top">
                    <span class="comment-action-wrap">
                      <el-icon class="lock-icon"><Lock /></el-icon>
                      <el-button text size="small" disabled>编辑</el-button>
                    </span>
                  </el-tooltip>
                  <el-button v-else text size="small" @click="startEditComment(r)">编辑</el-button>
                  <el-tooltip v-if="!canDelete(r)" :content="noDeleteTip(r)" placement="top">
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
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Flag, User, ChatDotRound, AlarmClock, ArrowDown, Close,
  List, Sunny, Link, Lock,
} from '@element-plus/icons-vue'
import rdKanbanService from '@/services/rdKanbanService'
import { useUserStore } from '@/stores/user'

const props = defineProps({
  item: { type: Object, required: true },
})

const emit = defineEmits(['comment-change'])

const userStore = useUserStore()
const currentUserId = computed(() => userStore.currentUser?.id || 0)
const isAdmin = computed(() => {
  const u = userStore.currentUser
  if (!u) return false
  if (u.is_super_admin === true || u.isAdmin === true) return true
  if (u.is_admin === true) return true
  if (typeof u.role === 'string' && u.role.toLowerCase() === 'admin') return true
  if (Array.isArray(u.roles) && u.roles.some((r) => String(r).toLowerCase() === 'admin')) return true
  return false
})

const STATUS_MAP = {
  completed: '完成',
  in_progress: '正在备战中...',
  priority: '优先',
  paused: '暂停',
  pending_discuss: '待讨论',
  not_supported: '不支持',
  test_completed: '测试完成',
  partially_support: '部分支持',
}
const statusLabel = computed(() => STATUS_MAP[props.item.status] || props.item.status || '')

// 展开/收起
const expanded = ref(false)
const loading = ref(false)
const editorRef = ref(null)

// 评论数据
const comments = ref([])
const newComment = ref('')
const submitting = ref(false)
const replyingTo = ref(null)
const editingCommentId = ref(null)
const editingCommentContent = ref('')
const emojiPickerVisible = ref(false)
const emojiPickerTarget = ref(null)
const EMOJI_LIST = ['👍', '❤️', '🎉', '😊', '😄', '😢', '😂', '🔥', '✨', '👏', '🙏', '💯', '🚀', '💪', '🤔', '👀', '✅', '❌', '⭐', '🎯']

const commentTree = computed(() => {
  const list = Array.isArray(comments.value) ? comments.value : []
  const byId = new Map()
  const roots = []
  list.forEach((c) => { byId.set(c.id, { ...c, replies: [] }) })
  list.forEach((c) => {
    const node = byId.get(c.id)
    if (c.parent_id && byId.has(c.parent_id)) {
      byId.get(c.parent_id).replies.push(node)
    } else {
      roots.push(node)
    }
  })
  roots.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
  roots.forEach((r) => r.replies.sort((a, b) => new Date(a.created_at) - new Date(b.created_at)))
  return roots
})

async function toggleExpand() {
  expanded.value = !expanded.value
  if (expanded.value && comments.value.length === 0) {
    await loadComments()
  }
}

async function loadComments() {
  if (!props.item.id) return
  loading.value = true
  try {
    const res = await rdKanbanService.listComments(props.item.id)
    comments.value = res.comments || res || []
  } catch (e) {
    console.error('加载评论失败', e)
  } finally {
    loading.value = false
  }
}

// 评论编辑器
function insertMarkdown(before, after) {
  const ta = editorRef.value
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
    const res = await rdKanbanService.addComment(props.item.id, payload)
    comments.value.unshift(res.comment)
    newComment.value = ''
    const wasReplying = !!replyingTo.value
    replyingTo.value = null
    props.item.comment_count = (props.item.comment_count || 0) + 1
    ElMessage.success(wasReplying ? '回复已发布' : '评论已发布')
    emit('comment-change', props.item.id, props.item.comment_count)
  } catch (e) {
    ElMessage.error('发布失败')
  } finally {
    submitting.value = false
  }
}

function startReplyComment(c) {
  replyingTo.value = { id: c.id, name: c.user?.name || '未知用户', content: c.content }
  newComment.value = ''
  nextTick(() => {
    if (editorRef.value) editorRef.value.focus()
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
  return String(cid) === String(myId)
}
function isCommentAuthorAdmin(c) {
  if (!c || !c.user) return false
  const u = c.user
  const username = (u.username || u.name || '').toLowerCase()
  if (!username) return false
  return ['admin', 'admina', 'administrator', 'superadmin', 'root'].includes(username)
}
function canEdit(c) {
  if (isAdmin.value) return true
  return isCommentMine(c)
}
function canDelete(c) {
  if (isAdmin.value) return true
  return isCommentMine(c)
}
function noEditTip(c) {
  if (isAdmin.value) return '管理员拥有编辑一切评论的权限'
  return isCommentMine(c) ? '你暂无编辑权限' : '仅评论作者或管理员可编辑'
}
function noDeleteTip(c) {
  if (isAdmin.value) return '管理员拥有删除一切评论的权限'
  return isCommentMine(c) ? '你暂无删除权限' : '仅评论作者或管理员可删除'
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
    if ((props.item.comment_count || 0) > 0) {
      props.item.comment_count -= 1
    }
    ElMessage.success('已删除')
    emit('comment-change', props.item.id, props.item.comment_count)
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

// Markdown 渲染
function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}
function renderMarkdown(text) {
  if (!text) return ''
  const codeBlocks = []
  let s = text.replace(/```([\s\S]*?)```/g, (m, code) => {
    const i = codeBlocks.length
    codeBlocks.push(escapeHtml(code))
    return `@@CODEBLOCK_${i}@@`
  })
  s = escapeHtml(s)
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>')
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  s = s.replace(/\*([^*]+)\*/g, '<em>$1</em>')
  s = s.replace(/~~([^~]+)~~/g, '<del>$1</del>')
  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
  s = s.replace(/(^|\n)((?:- [^\n]+\n?)+)/g, (m, pre, list) => {
    const items = list.trim().split(/\n- /).filter(Boolean).map((x) => `<li>${x.trim()}</li>`).join('')
    return `${pre}<ul>${items}</ul>`
  })
  s = s.replace(/(^|\n)((?:\d+\. [^\n]+\n?)+)/g, (m, pre, list) => {
    const items = list.trim().split(/\n\d+\. /).filter(Boolean).map((x) => `<li>${x.trim()}</li>`).join('')
    return `${pre}<ol>${items}</ol>`
  })
  s = s.replace(/\n/g, '<br/>')
  s = s.replace(/@@CODEBLOCK_(\d+)@@/g, (m, i) => `<pre><code>${codeBlocks[Number(i)] || ''}</code></pre>`)
  return s
}

function avatarText(name) {
  if (!name) return '?'
  return name.slice(-2)
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

// 监听 comment_count 变化（外部更新时增量拉取）
let lastCommentCount = props.item.comment_count || 0
watch(
  () => props.item.comment_count,
  async (count) => {
    if (!expanded.value) return
    if (typeof count !== 'number') return
    if (count > lastCommentCount) {
      try {
        const res = await rdKanbanService.listComments(props.item.id)
        const list = res.comments || res || []
        const existingIds = new Set(comments.value.map((c) => c.id))
        list.forEach((c) => {
          if (!existingIds.has(c.id)) comments.value.unshift(c)
        })
      } catch (e) {
        console.error('增量拉取评论失败', e)
      }
    }
    lastCommentCount = count
  }
)
</script>

<style scoped>
.weekly-report-card {
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-left: 3px solid #3b82f6;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.8);
  transition: box-shadow 0.2s, transform 0.15s;
  overflow: hidden;
}
.weekly-report-card:hover {
  box-shadow: 0 2px 12px rgba(59, 130, 246, 0.12);
  transform: translateY(-1px);
}
.weekly-report-card.is-pinned {
  border-left-color: #f59e0b;
  background: rgba(245, 158, 11, 0.04);
}
.weekly-report-card.is-expanded {
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.15);
}

.wr-card-header {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 16px;
  cursor: pointer;
  user-select: none;
}
.wr-card-pin {
  color: #f59e0b;
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 2px;
}
.wr-card-main {
  flex: 1;
  min-width: 0;
}
.wr-card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.wr-card-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.5;
  word-break: break-word;
  flex: 1;
  min-width: 0;
}
.wr-expand-icon {
  font-size: 14px;
  color: #94a3b8;
  transition: transform 0.25s ease;
  flex-shrink: 0;
}
.wr-expand-icon.rotated {
  transform: rotate(180deg);
}
.wr-card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #64748b;
  margin-top: 6px;
  flex-wrap: wrap;
}
.wr-meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.wr-meta-item .el-icon {
  font-size: 13px;
}

.wr-card-body {
  padding: 0 16px 16px;
  border-top: 1px solid rgba(15, 23, 42, 0.06);
  margin-top: 0;
}
.wr-report-content {
  padding: 12px 0;
  font-size: 13px;
  line-height: 1.7;
  color: #1e293b;
  word-break: break-word;
}
.wr-report-content :deep(code) {
  background: rgba(15, 23, 42, 0.06);
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 12px;
  font-family: 'Consolas', 'Monaco', monospace;
}
.wr-report-content :deep(pre) {
  background: rgba(15, 23, 42, 0.06);
  padding: 8px 10px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 12px;
  margin: 6px 0;
}
.wr-report-content :deep(pre code) {
  background: transparent;
  padding: 0;
}
.wr-report-content :deep(ul),
.wr-report-content :deep(ol) {
  margin: 4px 0;
  padding-left: 20px;
}
.wr-report-content :deep(a) {
  color: #0ea5e9;
  text-decoration: none;
}
.wr-report-content :deep(a:hover) {
  text-decoration: underline;
}
.wr-comment-section-title {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

/* 评论编辑器 */
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
  min-height: 50px;
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

/* 回复提示条 */
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

/* 评论列表 */
.comment-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.comment-thread {
  display: flex;
  flex-direction: column;
  gap: 6px;
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

/* 回复子列表 */
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

/* 表情选择器 */
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

/* 管理员徽章 */
.admin-badge {
  margin-left: 0;
}
</style>
