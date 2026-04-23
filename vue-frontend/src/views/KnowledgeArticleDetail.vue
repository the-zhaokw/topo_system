<template>
  <div class="article-detail-page">
    <!-- 返回按钮 -->
    <div class="page-header">
      <el-button link @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回知识库
      </el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 文章内容 -->
    <template v-else-if="article">
      <el-card shadow="never" class="article-card">
        <!-- 文章头部 -->
        <div class="article-header">
          <h1 class="article-title">{{ article.title }}</h1>
          <div class="article-meta">
            <span class="meta-item">
              <el-icon><User /></el-icon>
              {{ article.author_name }}
            </span>
            <span class="meta-item">
              <el-icon><Folder /></el-icon>
              {{ article.category_name }}
            </span>
            <span class="meta-item">
              <el-icon><Clock /></el-icon>
              {{ formatDate(article.created_at) }}
            </span>
            <span class="meta-item">
              <el-icon><View /></el-icon>
              {{ article.view_count || 0 }} 浏览
            </span>
            <span class="meta-item">
              <el-icon><Star /></el-icon>
              {{ article.like_count || 0 }} 点赞
            </span>
            <el-tag v-if="article.status === 'draft'" type="info" size="small">草稿</el-tag>
            <el-tag v-if="article.is_pinned" type="danger" size="small" effect="dark">置顶</el-tag>
          </div>
          <div class="article-tags" v-if="article.tags && article.tags.length">
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
        </div>

        <el-divider />

        <!-- 文章内容 -->
        <div class="article-content" v-html="renderedContent"></div>

        <!-- 附件 -->
        <div v-if="article.attachments?.length" class="article-attachments">
          <el-divider />
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
        <div v-if="relatedArticles.length > 0" class="article-related">
          <el-divider />
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
      </el-card>

      <!-- 评论区 -->
      <el-card shadow="never" class="comments-card">
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
      </el-card>
    </template>

    <!-- 文章不存在 -->
    <el-empty v-else description="文章不存在或已被删除">
      <el-button type="primary" @click="goBack">返回知识库</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import { useUserStore } from '@/stores/user'
import {
  ArrowLeft, User, Folder, Clock, View, Star,
  ChatDotRound, Paperclip, Document, Link
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const API_BASE_URL = import.meta.env.DEV ? 'http://localhost:5000' : 'http://172.18.36.249:5000'

// 状态
const loading = ref(true)
const article = ref(null)
const comments = ref([])
const relatedArticles = ref([])
const newComment = ref('')

// 渲染 Markdown 内容
const renderedContent = computed(() => {
  if (!article.value?.content) return ''
  return marked(article.value.content, { sanitize: true })
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

// 加载文章详情
const loadArticle = async () => {
  const id = route.params.id
  if (!id) {
    ElMessage.error('文章ID不存在')
    return
  }

  loading.value = true
  try {
    const response = await apiRequest(`/api/knowledge/articles/${id}`)
    article.value = response?.data || response || null
    if (article.value) {
      loadComments()
      loadRelatedArticles()
    }
  } catch (error) {
    console.error('加载文章失败:', error)
    ElMessage.error('加载文章失败')
  } finally {
    loading.value = false
  }
}

// 加载评论
const loadComments = async () => {
  if (!article.value?.id) return
  try {
    const response = await apiRequest(`/api/knowledge/articles/${article.value.id}/comments`)
    comments.value = response.data?.comments || response.data || []
  } catch (error) {
    console.error('加载评论失败:', error)
  }
}

// 加载相关文章
const loadRelatedArticles = async () => {
  if (!article.value?.id) return
  try {
    const response = await apiRequest(`/api/knowledge/articles/${article.value.id}/related`)
    relatedArticles.value = response.data?.items || response.data || []
  } catch (error) {
    console.error('加载相关文章失败:', error)
  }
}

// 提交评论
const submitComment = async () => {
  if (!newComment.value.trim() || !article.value?.id) return
  try {
    await apiRequest(`/api/knowledge/articles/${article.value.id}/comments`, {
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

// 下载附件
const downloadAttachment = (att) => {
  if (!article.value?.id) return
  window.open(`${API_BASE_URL}/api/knowledge/articles/${article.value.id}/attachments/${att.id}`)
}

// 加载相关文章详情
const loadRelatedArticle = (id) => {
  router.push(`/knowledge/articles/${id}`)
}

// 返回知识库
const goBack = () => {
  router.push('/knowledge')
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
    return `${window.location.origin}/avatar-placeholder.png`
  }
  if (avatar.startsWith('http://') || avatar.startsWith('https://')) {
    return avatar
  }
  return `${API_BASE_URL}${avatar}`
}

onMounted(() => {
  loadArticle()
})
</script>

<style scoped>
.article-detail-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
}

.loading-container {
  padding: 40px;
}

.article-card {
  margin-bottom: 20px;
}

.article-header {
  margin-bottom: 20px;
}

.article-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
  line-height: 1.4;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  color: #909399;
  font-size: 14px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.article-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-item {
  margin-right: 0;
}

.article-content {
  line-height: 1.8;
  font-size: 15px;
  color: #303133;
}

.article-content :deep(h1),
.article-content :deep(h2),
.article-content :deep(h3),
.article-content :deep(h4) {
  margin-top: 24px;
  margin-bottom: 16px;
  color: #303133;
}

.article-content :deep(p) {
  margin-bottom: 16px;
}

.article-content :deep(code) {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
}

.article-content :deep(pre) {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
  margin-bottom: 16px;
}

.article-content :deep(pre code) {
  background: transparent;
  padding: 0;
}

.article-content :deep(ul),
.article-content :deep(ol) {
  margin-bottom: 16px;
  padding-left: 24px;
}

.article-content :deep(li) {
  margin-bottom: 8px;
}

.article-content :deep(blockquote) {
  border-left: 4px solid #409EFF;
  padding-left: 16px;
  margin-left: 0;
  color: #606266;
}

.article-content :deep(img) {
  max-width: 100%;
  border-radius: 4px;
}

.article-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
}

.article-content :deep(th),
.article-content :deep(td) {
  border: 1px solid #dcdfe6;
  padding: 8px 12px;
  text-align: left;
}

.article-content :deep(th) {
  background: #f5f7fa;
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
.article-attachments {
  margin-top: 24px;
}

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
.article-related {
  margin-top: 24px;
}

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

/* 评论区 */
.comments-card {
  margin-top: 20px;
}

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

/* 响应式 */
@media screen and (max-width: 768px) {
  .article-detail-page {
    padding: 12px;
  }

  .article-title {
    font-size: 22px;
  }

  .article-meta {
    gap: 12px;
  }
}
</style>
