<template>
  <div class="article-detail">
    <!-- 文章头部信息 -->
    <div class="detail-header">
      <div class="detail-meta">
        <div class="meta-item">
          <router-link :to="`/users/${article.author_id}`" class="detail-author-link">
            <el-avatar :size="32" :src="article.author_avatar" />
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

    <!-- 相关文章 -->
    <div class="detail-section" v-if="relatedArticles.length">
      <h3 class="section-title">
        <el-icon><Link /></el-icon>
        相关文章
      </h3>
      <div class="related-list">
        <div
          v-for="rel in relatedArticles"
          :key="rel.id"
          class="related-item"
          @click="loadRelatedArticle(rel.id)"
        >
          <el-icon><Document /></el-icon>
          <span>{{ rel.title }}</span>
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
import { useUserStore } from '@/stores/user'
import {
  Folder, Clock, Edit, Share, Star, StarFilled,
  View, ChatDotRound, Paperclip, Document, Link, Download
} from '@element-plus/icons-vue'

const userStore = useUserStore()

const props = defineProps({
  article: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['edit', 'close'])

const API_BASE_URL = import.meta.env.DEV ? '' : 'http://172.18.36.249:5000'

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
const relatedArticles = ref([])

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

// 加载相关文章
const loadRelatedArticles = async () => {
  try {
    const response = await apiRequest(`/api/knowledge/articles/${props.article.id}/related`)
    relatedArticles.value = response.data?.items || response.data || []
  } catch (error) {
    console.error('加载相关文章失败:', error)
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

// 分享
const handleShare = () => {
  // TODO: 实现分享功能
  ElMessage.info('分享功能开发中')
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

// 加载相关文章详情
const loadRelatedArticle = (id) => {
  emit('close')
  // 通过路由跳转到相关文章
  window.location.href = `#/knowledge/articles/${id}`
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
  if (!avatar) return '/avatar-placeholder.png'
  if (avatar.startsWith('http://') || avatar.startsWith('https://')) {
    return avatar
  }
  return `${API_BASE_URL}/uploads/${avatar}`
}

onMounted(() => {
  loadComments()
  loadRelatedArticles()
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

/* 相关文章 */
.related-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.related-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  color: #606266;
}

.related-item:hover {
  background: #ecf5ff;
  color: #409EFF;
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
</style>
