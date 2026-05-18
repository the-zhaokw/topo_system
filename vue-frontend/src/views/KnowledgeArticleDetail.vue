<template>
  <div class="article-detail-page">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Document /></el-icon>
          </div>
          <div class="title-text">
            <h1>知识库文章</h1>
            <p class="subtitle">阅读、分享与协作</p>
          </div>
        </div>
        <!-- 返回按钮 -->
        <el-button class="back-btn" @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回知识库
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container animate-fade-in-up">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 文章内容 -->
    <template v-else-if="article">
      <div class="article-layout animate-fade-in-up delay-100">
        <!-- 主内容区 -->
        <div class="main-content">
          <el-card shadow="never" class="article-card glass-card">
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
                <el-tag v-if="article.status === 'draft'" type="info" size="small" class="status-tag">草稿</el-tag>
                <el-tag v-if="article.is_pinned" type="danger" size="small" effect="dark" class="status-tag">置顶</el-tag>
              </div>
              <div class="article-tags" v-if="article.tags && article.tags.length">
                <el-tag
                  v-for="tag in article.tags"
                  :key="tag"
                  size="small"
                  effect="light"
                  class="tag-item"
                >
                  {{ tag }}
                </el-tag>
              </div>
              <!-- 操作按钮 -->
              <div class="article-actions">
                <el-button-group>
                  <el-button v-if="canEdit" @click="editArticle" class="action-btn">
                    <el-icon><Edit /></el-icon> 编辑
                  </el-button>
                  <el-button @click="handleShare" class="action-btn">
                    <el-icon><Share /></el-icon> 分享
                  </el-button>
                  <el-button @click="handleFavorite" :class="['action-btn', { 'is-favorited-btn': article.is_favorited }]">
                    <el-icon><Star :class="{ 'is-favorited': article.is_favorited }" /></el-icon>
                    {{ article.is_favorited ? '已收藏' : '收藏' }}
                  </el-button>
                  <el-dropdown trigger="click" @command="handleExport">
                    <el-button class="action-btn">
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

            <el-divider class="custom-divider" />

            <!-- 文章内容 -->
            <div class="article-content" v-html="renderedContent"></div>

            <!-- 统计信息 -->
            <div class="article-stats-bar">
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
            <div v-if="article.attachments?.length" class="article-attachments">
              <el-divider class="custom-divider" />
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
                  <div class="attachment-icon-wrapper">
                    <el-icon class="attachment-icon"><Document /></el-icon>
                  </div>
                  <span class="attachment-name">{{ att.filename }}</span>
                  <span class="attachment-size">{{ formatFileSize(att.file_size) }}</span>
                  <el-button type="primary" link size="small" @click="downloadAttachment(att)" class="download-btn">
                    <el-icon><Download /></el-icon>
                    下载
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 评论区 -->
          <el-card shadow="never" class="comments-card glass-card animate-fade-in-up delay-200">
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
                class="comment-input"
              />
              <div class="comment-actions">
                <el-button type="primary" @click="submitComment" :disabled="!newComment.trim()" class="btn-gradient">
                  <el-icon><ChatDotRound /></el-icon>
                  发表评论
                </el-button>
              </div>
            </div>

            <!-- 评论列表 -->
            <div class="comment-list" v-if="comments.length">
              <div v-for="comment in comments" :key="comment.id" class="comment-item">
                <div class="comment-header">
                  <div class="comment-author">
                    <el-avatar :size="36" :src="getUserAvatar(comment.user_avatar)" class="comment-avatar" />
                    <div class="author-info">
                      <span class="author-name">{{ comment.user_name }}</span>
                      <span class="comment-time">{{ formatRelativeTime(comment.created_at) }}</span>
                    </div>
                  </div>
                </div>
                <div class="comment-content">{{ comment.content }}</div>
              </div>
            </div>
            <el-empty v-else description="暂无评论，快来发表第一条评论吧" class="custom-empty" />
          </el-card>
        </div>

        <!-- 侧边栏 -->
        <div class="sidebar animate-fade-in-up delay-300">
          <!-- 文章目录 -->
          <el-card shadow="never" class="toc-card glass-card">
            <template #header>
              <div class="card-header">
                <el-icon><List /></el-icon>
                <span>文章目录</span>
              </div>
            </template>
            <div class="toc-content">
              <div class="toc-placeholder">
                <el-icon><Document /></el-icon>
                <span>目录功能开发中</span>
              </div>
            </div>
          </el-card>

          <!-- 相关文章推荐 -->
          <el-card shadow="never" class="related-card glass-card">
            <template #header>
              <div class="card-header">
                <el-icon><Link /></el-icon>
                <span>相关推荐</span>
              </div>
            </template>
            <div class="related-content">
              <div class="related-placeholder">
                <el-icon><Collection /></el-icon>
                <span>相关文章推荐开发中</span>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </template>

    <!-- 文章不存在 -->
    <el-empty v-else description="文章不存在或已被删除" class="custom-empty animate-fade-in-up">
      <el-button type="primary" @click="goBack" class="btn-gradient">返回知识库</el-button>
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
  ArrowLeft, User, Folder, Clock, View, Star, StarFilled,
  ChatDotRound, Paperclip, Edit, Share, Download, Document,
  List, Link, Collection
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const API_BASE_URL = import.meta.env.DEV ? 'http://localhost:5000' : 'http://172.18.36.249:5000'

// 状态
const loading = ref(true)
const article = ref(null)
const comments = ref([])
const newComment = ref('')
const isLiked = ref(false)

const isAdmin = computed(() => {
  const user = userStore.currentUser
  if (!user) return false
  if (user.is_super_admin) return true
  return user.position === '管理员' || user.position?.includes('经理')
})

const canEdit = computed(() => {
  if (isAdmin.value) return true
  return userStore.currentUser?.id === article.value?.author_id
})

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

// 编辑文章
const editArticle = () => {
  router.push(`/knowledge/articles/${article.value.id}/edit`)
}

// 点赞
const handleLike = async () => {
  if (!article.value?.id) return
  try {
    await apiRequest(`/api/knowledge/articles/${article.value.id}/like`, {
      method: 'POST'
    })
    isLiked.value = !isLiked.value
    article.value.like_count = (article.value.like_count || 0) + (isLiked.value ? 1 : -1)
    ElMessage.success(isLiked.value ? '点赞成功' : '取消点赞')
  } catch (error) {
    console.error('点赞失败:', error)
  }
}

// 收藏
const handleFavorite = async () => {
  if (!article.value?.id) return
  try {
    await apiRequest(`/api/knowledge/articles/${article.value.id}/favorite`, {
      method: article.value.is_favorited ? 'DELETE' : 'POST'
    })
    article.value.is_favorited = !article.value.is_favorited
    ElMessage.success(article.value.is_favorited ? '收藏成功' : '取消收藏')
  } catch (error) {
    console.error('收藏失败:', error)
  }
}

// 分享
const handleShare = async () => {
  if (!article.value?.id) return
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.warning('请先登录')
      return
    }

    // 创建分享链接
    const response = await fetch(
      `${API_BASE_URL}/api/knowledge/articles/${article.value.id}/shares`,
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
  if (!article.value?.id) return
  try {
    const token = localStorage.getItem('token')
    const url = `${API_BASE_URL}/api/knowledge/articles/${article.value.id}/export/${type}`
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
    link.download = `${article.value.title}.${type === 'pdf' ? 'pdf' : 'docx'}`
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
/* 导入设计系统 */
@import '@/styles/design-system.css';

.article-detail-page {
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  min-height: 100%;
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

.back-btn {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  border-radius: 12px;
  padding: 12px 20px;
  font-weight: 500;
  transition: all 0.3s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

/* 文章布局 */
.article-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
}

.main-content {
  min-width: 0;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

.article-card {
  margin-bottom: 20px;
}

.article-card :deep(.el-card__body) {
  padding: 32px;
}

/* 文章头部 */
.article-header {
  margin-bottom: 24px;
}

.article-title {
  font-size: 32px;
  font-weight: 800;
  margin: 0 0 20px 0;
  line-height: 1.3;
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  color: #64748b;
  font-size: 14px;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(241, 245, 249, 0.8);
  border-radius: 20px;
  transition: all 0.3s;
}

.meta-item:hover {
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
}

.meta-item .el-icon {
  font-size: 16px;
}

.status-tag {
  border-radius: 20px;
  font-weight: 500;
}

.article-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.tag-item {
  margin-right: 0;
  border-radius: 20px;
  font-weight: 500;
  transition: all 0.3s;
}

.tag-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.article-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(226, 232, 240, 0.8);
}

.action-btn {
  transition: all 0.3s;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.is-favorited-btn {
  color: #f56c6c;
  border-color: #f56c6c;
}

.is-favorited-btn:hover {
  background: rgba(245, 108, 108, 0.1);
}

.custom-divider {
  margin: 24px 0;
  border-color: rgba(226, 232, 240, 0.8);
}

/* 文章内容 */
.article-content {
  line-height: 1.8;
  font-size: 16px;
  color: #334155;
}

.article-content :deep(h1),
.article-content :deep(h2),
.article-content :deep(h3),
.article-content :deep(h4) {
  margin-top: 32px;
  margin-bottom: 16px;
  color: #1e293b;
  font-weight: 700;
}

.article-content :deep(h1) {
  font-size: 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.article-content :deep(h2) {
  font-size: 24px;
  border-bottom: 2px solid rgba(99, 102, 241, 0.2);
  padding-bottom: 8px;
}

.article-content :deep(h3) {
  font-size: 20px;
}

.article-content :deep(p) {
  margin-bottom: 16px;
}

.article-content :deep(code) {
  background: rgba(99, 102, 241, 0.1);
  padding: 2px 8px;
  border-radius: 6px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  color: #6366f1;
}

.article-content :deep(pre) {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  padding: 20px;
  border-radius: 12px;
  overflow-x: auto;
  margin-bottom: 20px;
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
}

.article-content :deep(pre code) {
  background: transparent;
  padding: 0;
  color: #e2e8f0;
}

.article-content :deep(ul),
.article-content :deep(ol) {
  margin-bottom: 16px;
  padding-left: 28px;
}

.article-content :deep(li) {
  margin-bottom: 8px;
}

.article-content :deep(blockquote) {
  border-left: 4px solid #667eea;
  padding: 16px 20px;
  margin: 20px 0;
  background: rgba(99, 102, 241, 0.05);
  border-radius: 0 12px 12px 0;
  color: #475569;
  font-style: italic;
}

.article-content :deep(img) {
  max-width: 100%;
  border-radius: 12px;
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.2);
  margin: 20px 0;
}

.article-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.article-content :deep(th),
.article-content :deep(td) {
  border: 1px solid #e2e8f0;
  padding: 12px 16px;
  text-align: left;
}

.article-content :deep(th) {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  font-weight: 600;
  color: #1e293b;
}

.article-content :deep(tr:nth-child(even)) {
  background: rgba(241, 245, 249, 0.5);
}

/* 统计栏 */
.article-stats-bar {
  display: flex;
  gap: 32px;
  padding: 20px 0;
  border-top: 1px solid rgba(226, 232, 240, 0.8);
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  margin: 28px 0;
}

.article-stats-bar .stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s;
  padding: 8px 16px;
  border-radius: 12px;
  background: rgba(241, 245, 249, 0.5);
}

.article-stats-bar .stat-item:hover {
  color: #6366f1;
  background: rgba(99, 102, 241, 0.1);
  transform: translateY(-2px);
}

.article-stats-bar .is-liked {
  color: #f56c6c;
}

.is-favorited {
  color: #f56c6c;
}

/* 附件 */
.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 16px;
}

.section-title .el-icon {
  color: #6366f1;
  font-size: 22px;
}

.article-attachments {
  margin-top: 24px;
}

.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: rgba(241, 245, 249, 0.8);
  border-radius: 12px;
  transition: all 0.3s;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.attachment-item:hover {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 8px 20px -5px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.attachment-icon-wrapper {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.attachment-icon {
  font-size: 22px;
  color: #6366f1;
}

.attachment-name {
  flex: 1;
  color: #1e293b;
  font-weight: 500;
}

.attachment-size {
  color: #94a3b8;
  font-size: 13px;
  font-weight: 500;
}

.download-btn {
  font-weight: 500;
}

/* 评论区 */
.comments-card {
  margin-top: 20px;
}

.comments-card :deep(.el-card__body) {
  padding: 28px;
}

.comment-input-area {
  margin-bottom: 24px;
}

.comment-input :deep(.el-textarea__inner) {
  border-radius: 12px;
  padding: 16px;
  font-size: 15px;
  border-color: #e2e8f0;
  transition: all 0.3s;
}

.comment-input :deep(.el-textarea__inner:focus) {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.comment-actions {
  margin-top: 16px;
  text-align: right;
}

.btn-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  border-radius: 10px;
  padding: 12px 24px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(102, 126, 234, 0.5);
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  padding: 20px;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 16px;
  transition: all 0.3s;
  border: 1px solid rgba(226, 232, 240, 0.4);
}

.comment-item:hover {
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 8px 20px -5px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 12px;
}

.comment-avatar {
  border: 2px solid white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.author-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
}

.comment-time {
  color: #94a3b8;
  font-size: 13px;
}

.comment-content {
  color: #475569;
  line-height: 1.7;
  padding-left: 48px;
  font-size: 15px;
}

.custom-empty :deep(.el-empty__description) {
  color: #94a3b8;
}

/* 侧边栏 */
.toc-card,
.related-card {
  position: sticky;
  top: 20px;
}

.toc-card :deep(.el-card__header),
.related-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
  background: rgba(241, 245, 249, 0.5);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
}

.card-header .el-icon {
  color: #6366f1;
  font-size: 18px;
}

.toc-content,
.related-content {
  padding: 20px;
}

.toc-placeholder,
.related-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 32px 20px;
  color: #94a3b8;
  text-align: center;
}

.toc-placeholder .el-icon,
.related-placeholder .el-icon {
  font-size: 40px;
  color: #cbd5e1;
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

/* 加载状态 */
.loading-container {
  padding: 40px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

/* 响应式 */
@media screen and (max-width: 1024px) {
  .article-layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    flex-direction: row;
    gap: 20px;
  }

  .toc-card,
  .related-card {
    position: static;
    flex: 1;
  }
}

@media screen and (max-width: 768px) {
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

  .back-btn {
    padding: 8px 14px;
    font-size: 13px;
  }

  .article-card :deep(.el-card__body),
  .comments-card :deep(.el-card__body) {
    padding: 20px;
  }

  .article-title {
    font-size: 24px;
  }

  .article-meta {
    gap: 10px;
  }

  .meta-item {
    padding: 4px 10px;
    font-size: 13px;
  }

  .article-stats-bar {
    gap: 16px;
    flex-wrap: wrap;
  }

  .article-stats-bar .stat-item {
    padding: 6px 12px;
    font-size: 13px;
  }

  .attachment-item {
    padding: 12px 16px;
    flex-wrap: wrap;
  }

  .comment-content {
    padding-left: 0;
    margin-top: 12px;
  }

  .sidebar {
    flex-direction: column;
  }

  .article-content :deep(h1) {
    font-size: 22px;
  }

  .article-content :deep(h2) {
    font-size: 20px;
  }

  .article-content :deep(h3) {
    font-size: 18px;
  }
}

@media screen and (max-width: 480px) {
  .page-header {
    padding: 16px;
  }

  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .title-text h1 {
    font-size: 20px;
  }

  .article-title {
    font-size: 20px;
  }

  .article-card :deep(.el-card__body),
  .comments-card :deep(.el-card__body) {
    padding: 16px;
  }

  .article-actions .el-button-group {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .article-actions .el-button {
    flex: 1;
    min-width: 80px;
  }
}
</style>
