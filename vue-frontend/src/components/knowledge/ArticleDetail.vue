<template>
  <div class="article-detail">
    <!-- 文章头部信息 -->
    <div class="detail-header">
      <div class="detail-meta">
        <div class="meta-item">
          <router-link :to="`/users/${article.author_id}`" class="detail-author-link">
            <el-avatar :size="32" :src="getUserAvatar(article.author_avatar)" />
            <span class="meta-text">{{ article.author_name }}</span>
          </router-link>
        </div>
        <div class="meta-divider">|</div>
        <div class="meta-item">
          <el-icon><Folder /></el-icon>
          <span class="meta-text">{{ article.category_name }}</span>
        </div>
        <div class="meta-divider">|</div>
        <div class="meta-item">
          <el-icon><Clock /></el-icon>
          <span class="meta-text">{{ formatDate(article.created_at) }}</span>
        </div>
        <div class="meta-divider">|</div>
        <div class="meta-item">
          <span class="version-tag">v{{ article.version || 1 }}</span>
        </div>
      </div>
      <div class="detail-actions">
        <el-button-group>
          <el-button v-if="canEdit" @click="$emit('edit')">
            <el-icon><Edit /></el-icon> 编辑
          </el-button>
          <el-button @click="handleShare">
            <el-icon><Share /></el-icon> 分享
          </el-button>
          <el-button @click="handleFavorite">
            <el-icon><Star :class="{ 'is-favorited': article.is_favorited }" /></el-icon>
            {{ article.is_favorited ? '已收藏' : '收藏' }}
          </el-button>
          <el-dropdown trigger="click" @command="handleExport">
            <el-button>
              <el-icon><Download /></el-icon> 导出
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="pdf">导出为 PDF</el-dropdown-item>
                <el-dropdown-item command="docx">导出为 Word</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-button-group>
      </div>
    </div>

    <!-- 标签 -->
    <div class="detail-tags" v-if="article.tags && article.tags.length">
      <el-tag
        v-for="tag in article.tags"
        :key="tag"
        size="small"
        effect="plain"
        class="tag-item"
      >
        {{ tag }}
      </el-tag>
    </div>

    <!-- 文章内容 -->
    <div class="detail-content" v-html="renderedContent"></div>

    <!-- 统计信息 -->
    <div class="detail-stats">
      <div class="stat-item" @click="handleLike">
        <el-icon :class="{ 'is-liked': isLiked }"><StarFilled /></el-icon>
        <span>{{ article.like_count || 0 }} 点赞</span>
      </div>
      <div class="stat-item">
        <el-icon><View /></el-icon>
        <span>{{ article.view_count || 0 }} 浏览</span>
      </div>
      <div class="stat-item">
        <el-icon><ChatDotRound /></el-icon>
        <span>{{ comments.length }} 评论</span>
      </div>
    </div>

    <!-- 附件 -->
    <div class="detail-section" v-if="article.attachments?.length">
      <h3 class="section-title">
        <el-icon><Paperclip /></el-icon>
        附件 ({{ article.attachments.length }})
      </h3>
      <div class="attachment-list">
        <div
          v-for="att in article.attachments"
          :key="att.id"
          class="attachment-item"
        >
          <el-icon class="attachment-icon"><Document /></el-icon>
          <span class="attachment-name">{{ att.filename }}</span>
          <span class="attachment-size">{{ formatFileSize(att.file_size) }}</span>
          <el-button type="primary" link size="small" @click="downloadAttachment(att)">
            下载
          </el-button>
        </div>
      </div>
    </div>

    <!-- 评论区 -->
    <div class="detail-section">
      <h3 class="section-title">
        <el-icon><ChatDotRound /></el-icon>
        评论 ({{ comments.length }})
      </h3>

      <!-- 评论输入 -->
      <div class="comment-input-area">
        <el-input
          v-model="newComment"
          type="textarea"
          :rows="3"
          placeholder="发表评论..."
          maxlength="500"
          show-word-limit
        />
        <div class="comment-actions">
          <el-button type="primary" @click="submitComment" :disabled="!newComment.trim()">
            发表评论
          </el-button>
        </div>
      </div>

      <!-- 评论列表 -->
      <div class="comment-list" v-if="comments.length">
        <div v-for="comment in comments" :key="comment.id" class="comment-item">
          <div class="comment-header">
            <div class="comment-author">
              <el-avatar :size="28" :src="getUserAvatar(comment.user_avatar)" />
              <span class="author-name">{{ comment.user_name }}</span>
            </div>
            <span class="comment-time">{{ formatRelativeTime(comment.created_at) }}</span>
          </div>
          <div class="comment-content">{{ comment.content }}</div>
        </div>
      </div>
      <el-empty v-else description="暂无评论，快来发表第一条评论吧" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  Folder, Clock, Edit, Share, Star, StarFilled,
  View, ChatDotRound, Paperclip, Download
} from '@element-plus/icons-vue'

const userStore = useUserStore()
const router = useRouter()

const props = defineProps({
  article: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['edit', 'close'])

const API_BASE_URL = import.meta.env.DEV ? 'http://localhost:5000' : 'http://172.18.36.249:5000'

const isAdmin = computed(() => {
  const user = userStore.currentUser
  if (!user) return false
  if (user.is_super_admin) return true
  return user.position === '管理员' || user.position?.includes('经理')
})

const canEdit = computed(() => {
  if (isAdmin.value) return true
  return userStore.currentUser?.id === props.article.author_id
})

// 状态
const isLiked = ref(false)
const newComment = ref('')
const comments = ref([])

// 渲染 Markdown 内容
const renderedContent = computed(() => {
  if (!props.article.content) return ''
  return marked(props.article.content, { sanitize: true })
})

// API 请求
const apiRequest = async (url, options = {}) => {
  const token = localStorage.getItem('token')
  const headers = {
    ...options.headers,
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  }
  const response = await fetch(`${API_BASE_URL}${url}`, { ...options, headers })
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  return response.json()
}

// 加载评论
const loadComments = async () => {
  try {
    const response = await apiRequest(`/api/knowledge/articles/${props.article.id}/comments`)
    comments.value = response.data?.comments || response.data || []
  } catch (error) {
    console.error('加载评论失败:', error)
  }
}

// 提交评论
const submitComment = async () => {
  if (!newComment.value.trim()) return
  try {
    await apiRequest(`/api/knowledge/articles/${props.article.id}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: newComment.value })
    })
    ElMessage.success('评论成功')
    newComment.value = ''
    loadComments()
  } catch (error) {
    console.error('发表评论失败:', error)
    ElMessage.error('发表评论失败')
  }
}

// 点赞
const handleLike = async () => {
  try {
    await apiRequest(`/api/knowledge/articles/${props.article.id}/like`, {
      method: 'POST'
    })
    isLiked.value = !isLiked.value
    props.article.like_count = (props.article.like_count || 0) + (isLiked.value ? 1 : -1)
    ElMessage.success(isLiked.value ? '点赞成功' : '取消点赞')
  } catch (error) {
    console.error('点赞失败:', error)
  }
}

// 收藏
const handleFavorite = async () => {
  try {
    await apiRequest(`/api/knowledge/articles/${props.article.id}/favorite`, {
      method: props.article.is_favorited ? 'DELETE' : 'POST'
    })
    props.article.is_favorited = !props.article.is_favorited
    ElMessage.success(props.article.is_favorited ? '收藏成功' : '取消收藏')
  } catch (error) {
    console.error('收藏失败:', error)
  }
}

// 分享 - 直接创建分享链接并复制
const handleShare = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.warning('请先登录')
      return
    }

    // 创建分享链接
    const response = await fetch(
      `${API_BASE_URL}/api/knowledge/articles/${props.article.id}/shares`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          allow_download: true
        })
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || '创建分享失败')
    }

    const data = await response.json()
    // 使用 hash 模式的路由格式生成分享链接
    const shareUrl = `${window.location.origin}/#${data.share_url}`

    // 复制到剪贴板
    const copyToClipboard = async (text) => {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text)
      } else {
        const textarea = document.createElement('textarea')
        textarea.value = text
        textarea.style.position = 'fixed'
        textarea.style.opacity = '0'
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
      }
    }

    await copyToClipboard(shareUrl)
    ElMessage.success('分享链接已复制到剪贴板')
  } catch (error) {
    console.error('分享失败:', error)
    ElMessage.error(error.message || '分享失败')
  }
}

// 导出
const handleExport = async (type) => {
  try {
    const token = localStorage.getItem('token')
    const url = `${API_BASE_URL}/api/knowledge/articles/${props.article.id}/export/${type}`
    const response = await fetch(url, {
      headers: {
        Authorization: token ? `Bearer ${token}` : ''
      }
    })
    if (!response.ok) {
      throw new Error('导出失败')
    }
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `${props.article.title}.${type === 'pdf' ? 'pdf' : 'docx'}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 下载附件
const downloadAttachment = (att) => {
  window.open(`${API_BASE_URL}/api/knowledge/articles/${props.article.id}/attachments/${att.id}`)
}

// 格式化文件大小
const formatFileSize = (size) => {
  if (!size) return ''
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  return (size / (1024 * 1024)).toFixed(1) + ' MB'
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

// 格式化相对时间
const formatRelativeTime = (date) => {
  if (!date) return ''
  const now = new Date()
  const past = new Date(date)
  const diff = (now - past) / 1000

  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  if (diff < 604800) return `${Math.floor(diff / 86400)}天前`
  return formatDate(date)
}

// 获取用户头像URL
const getUserAvatar = (avatar) => {
  if (!avatar) {
    // 使用绝对路径确保头像能正确显示
    return `${window.location.origin}/avatar-placeholder.png`
  }
  if (avatar.startsWith('http://') || avatar.startsWith('https://')) {
    return avatar
  }
  return `${API_BASE_URL}${avatar}`
}

onMounted(() => {
  loadComments()
})
</script>

<style scoped>
.article-detail {
  padding: 20px;
}

/* 头部信息 */
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.detail-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #606266;
  font-size: 14px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-text {
  color: #606266;
}

.meta-divider {
  color: #dcdfe6;
}

.detail-author-link {
  display: flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
  color: inherit;
  transition: opacity 0.3s;
}

.detail-author-link:hover {
  opacity: 0.7;
}

.detail-author-link .meta-text {
  color: #409EFF;
}

.version-tag {
  background: #f0f2f5;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #909399;
}

/* 标签 */
.detail-tags {
  margin-bottom: 20px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-item {
  margin-right: 0;
}

/* 文章内容 */
.detail-content {
  line-height: 1.8;
  font-size: 15px;
  color: #303133;
  margin-bottom: 24px;
}

.detail-content :deep(h1),
.detail-content :deep(h2),
.detail-content :deep(h3),
.detail-content :deep(h4) {
  margin-top: 24px;
  margin-bottom: 16px;
  color: #303133;
}

.detail-content :deep(p) {
  margin-bottom: 16px;
}

.detail-content :deep(code) {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
}

.detail-content :deep(pre) {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
  margin-bottom: 16px;
}

.detail-content :deep(pre code) {
  background: transparent;
  padding: 0;
}

.detail-content :deep(ul),
.detail-content :deep(ol) {
  margin-bottom: 16px;
  padding-left: 24px;
}

.detail-content :deep(li) {
  margin-bottom: 8px;
}

.detail-content :deep(blockquote) {
  border-left: 4px solid #409EFF;
  padding-left: 16px;
  margin-left: 0;
  color: #606266;
}

.detail-content :deep(img) {
  max-width: 100%;
  border-radius: 4px;
}

.detail-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
}

.detail-content :deep(th),
.detail-content :deep(td) {
  border: 1px solid #dcdfe6;
  padding: 8px 12px;
  text-align: left;
}

.detail-content :deep(th) {
  background: #f5f7fa;
}

/* 统计信息 */
.detail-stats {
  display: flex;
  gap: 24px;
  padding: 16px 0;
  border-top: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 24px;
}

.detail-stats .stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  cursor: pointer;
  transition: color 0.3s;
}

.detail-stats .stat-item:hover {
  color: #409EFF;
}

.detail-stats .is-liked {
  color: #f56c6c;
}

/* 区块 */
.detail-section {
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

/* 附件 */
.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.attachment-icon {
  font-size: 20px;
  color: #409EFF;
}

.attachment-name {
  flex: 1;
  color: #303133;
}

.attachment-size {
  color: #909399;
  font-size: 12px;
}

/* 评论 */
.comment-input-area {
  margin-bottom: 20px;
}

.comment-actions {
  margin-top: 12px;
  text-align: right;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-name {
  font-weight: 500;
  color: #303133;
}

.comment-time {
  color: #909399;
  font-size: 12px;
}

.comment-content {
  color: #606266;
  line-height: 1.6;
  padding-left: 36px;
}

.is-favorited {
  color: #f56c6c;
}

/* ========================================
   移动端响应式适配
   ======================================== */
@media screen and (max-width: 768px) {
  .article-detail {
    padding: 12px;
  }

  /* 头部信息 - 移动端优化 */
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-light, #e5e7eb);
  }

  .detail-meta {
    flex-wrap: wrap;
    gap: 8px 12px;
    font-size: 13px;
    width: 100%;
    padding: 8px 0;
    background: var(--bg-secondary, #f9fafb);
    border-radius: 8px;
    padding: 8px 12px;
  }

  .meta-item {
    gap: 4px;
    white-space: nowrap;
  }

  .meta-divider {
    display: none;
  }

  .meta-text {
    font-size: 12px;
  }

  .detail-author-link .meta-text {
    color: var(--color-primary, #0ea5e9);
    max-width: 80px;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .version-tag {
    font-size: 11px;
    padding: 2px 6px;
  }

  /* 操作按钮 - 移动端优化 */
  .detail-actions {
    width: 100%;
  }

  .detail-actions .el-button-group {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    width: 100%;
  }

  .detail-actions .el-button {
    flex: 1;
    min-width: calc(50% - 3px);
    font-size: 12px;
    padding: 8px 12px;
  }

  .detail-actions .el-button .el-icon {
    margin-right: 4px;
  }

  .detail-actions .el-dropdown {
    width: 100%;
  }

  .detail-actions .el-dropdown .el-button {
    width: 100%;
  }

  /* 标签 - 移动端优化 */
  .detail-tags {
    margin-bottom: 16px;
    gap: 6px;
  }

  .detail-tags .el-tag {
    font-size: 11px;
    padding: 0 8px;
    height: 24px;
    line-height: 22px;
  }

  /* 文章内容 - 移动端优化 */
  .detail-content {
    font-size: 14px;
    line-height: 1.7;
    margin-bottom: 20px;
    padding: 12px;
    background: var(--bg-primary, #fff);
    border-radius: 8px;
    border: 1px solid var(--border-light, #e5e7eb);
  }

  .detail-content :deep(h1) {
    font-size: 20px;
    margin-top: 20px;
    margin-bottom: 12px;
  }

  .detail-content :deep(h2) {
    font-size: 18px;
    margin-top: 18px;
    margin-bottom: 10px;
  }

  .detail-content :deep(h3) {
    font-size: 16px;
    margin-top: 16px;
    margin-bottom: 8px;
  }

  .detail-content :deep(h4) {
    font-size: 15px;
    margin-top: 14px;
    margin-bottom: 8px;
  }

  .detail-content :deep(p) {
    margin-bottom: 12px;
  }

  .detail-content :deep(code) {
    font-size: 13px;
    padding: 2px 4px;
  }

  .detail-content :deep(pre) {
    padding: 12px;
    margin-bottom: 12px;
    border-radius: 6px;
    font-size: 12px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .detail-content :deep(pre code) {
    font-size: 12px;
    line-height: 1.5;
  }

  .detail-content :deep(ul),
  .detail-content :deep(ol) {
    padding-left: 20px;
    margin-bottom: 12px;
  }

  .detail-content :deep(li) {
    margin-bottom: 6px;
  }

  .detail-content :deep(blockquote) {
    border-left: 3px solid var(--color-primary, #0ea5e9);
    padding-left: 12px;
    margin-left: 0;
    margin-bottom: 12px;
  }

  .detail-content :deep(img) {
    max-width: 100%;
    height: auto;
    border-radius: 6px;
    margin: 8px 0;
  }

  .detail-content :deep(table) {
    font-size: 12px;
    display: block;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    margin-bottom: 12px;
  }

  .detail-content :deep(th),
  .detail-content :deep(td) {
    padding: 6px 8px;
    white-space: nowrap;
  }

  /* 统计信息 - 移动端优化 */
  .detail-stats {
    flex-wrap: wrap;
    gap: 12px;
    padding: 12px 0;
    margin-bottom: 20px;
  }

  .detail-stats .stat-item {
    flex: 1;
    min-width: calc(33.33% - 8px);
    justify-content: center;
    padding: 10px 8px;
    background: var(--bg-secondary, #f9fafb);
    border-radius: 8px;
    font-size: 12px;
  }

  .detail-stats .stat-item .el-icon {
    font-size: 16px;
  }

  .detail-stats .stat-item:hover {
    background: rgba(56, 189, 248, 0.08);
  }

  /* 区块 - 移动端优化 */
  .detail-section {
    margin-bottom: 20px;
  }

  .section-title {
    font-size: 15px;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-light, #e5e7eb);
  }

  /* 附件 - 移动端优化 */
  .attachment-list {
    gap: 8px;
  }

  .attachment-item {
    flex-wrap: wrap;
    padding: 10px;
    gap: 8px;
  }

  .attachment-icon {
    font-size: 18px;
    color: var(--color-primary, #0ea5e9);
  }

  .attachment-name {
    flex: 1 1 100%;
    font-size: 13px;
    order: 3;
    padding-left: 26px;
  }

  .attachment-size {
    font-size: 11px;
    order: 2;
    margin-left: auto;
  }

  .attachment-item .el-button {
    order: 1;
    font-size: 11px;
    padding: 4px 8px;
  }

  /* 评论输入 - 移动端优化 */
  .comment-input-area {
    margin-bottom: 16px;
  }

  .comment-input-area .el-textarea {
    font-size: 14px;
  }

  .comment-input-area .el-textarea__inner {
    padding: 10px 12px;
  }

  .comment-actions {
    margin-top: 8px;
    text-align: right;
  }

  .comment-actions .el-button {
    width: 100%;
    font-size: 13px;
  }

  /* 评论列表 - 移动端优化 */
  .comment-list {
    gap: 12px;
  }

  .comment-item {
    padding: 12px;
    border-radius: 8px;
  }

  .comment-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
    margin-bottom: 8px;
  }

  .comment-author {
    gap: 6px;
  }

  .author-name {
    font-size: 13px;
  }

  .comment-time {
    font-size: 11px;
    margin-left: 0;
  }

  .comment-content {
    font-size: 13px;
    line-height: 1.5;
    padding-left: 0;
    color: var(--text-secondary, #4b5563);
  }

  /* 空状态 - 移动端优化 */
  .el-empty {
    padding: 24px 16px;
  }

  .el-empty__image {
    width: 80px !important;
    height: 80px !important;
  }

  .el-empty__description {
    font-size: 13px;
  }
}

/* 超小屏幕额外适配 */
@media screen and (max-width: 480px) {
  .article-detail {
    padding: 8px;
  }

  .detail-meta {
    font-size: 12px;
    padding: 6px 10px;
  }

  .detail-actions .el-button {
    min-width: calc(50% - 3px);
    font-size: 11px;
    padding: 6px 10px;
  }

  .detail-actions .el-button span {
    display: inline;
  }

  .detail-content {
    padding: 10px;
    font-size: 13px;
  }

  .detail-content :deep(pre) {
    padding: 10px;
    font-size: 11px;
  }

  .detail-stats .stat-item {
    min-width: calc(33.33% - 6px);
    padding: 8px 6px;
    font-size: 11px;
  }

  .detail-stats .stat-item .el-icon {
    font-size: 14px;
  }

  .section-title {
    font-size: 14px;
  }

  .attachment-item {
    padding: 8px;
  }

  .comment-item {
    padding: 10px;
  }

  .comment-content {
    font-size: 12px;
  }
}

/* 触摸友好优化 */
@media (pointer: coarse) {
  .detail-stats .stat-item,
  .detail-actions .el-button,
  .attachment-item,
  .comment-item {
    transition: all 0.15s ease;
  }

  .detail-stats .stat-item:active,
  .detail-actions .el-button:active,
  .attachment-item:active,
  .comment-item:active {
    opacity: 0.8;
    transform: scale(0.98);
  }
}

/* 横屏模式适配 */
@media screen and (max-height: 500px) and (orientation: landscape) {
  .article-detail {
    padding: 8px 16px;
  }

  .detail-header {
    flex-direction: row;
    justify-content: space-between;
  }

  .detail-meta {
    flex-wrap: nowrap;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .detail-actions .el-button {
    min-width: auto;
    padding: 6px 12px;
  }

  .detail-content {
    max-height: 50vh;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }
}
</style>
