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
                  <div class="attachment-icon-wrapper" :style="{ background: getAttachmentIconBg(att.filename) }">
                    <el-icon class="attachment-icon"><Document /></el-icon>
                  </div>
                  <div class="attachment-info">
                    <span class="attachment-name">{{ att.filename }}</span>
                    <span class="attachment-meta">{{ formatFileSize(att.file_size) }} · {{ getFileExtLabel(att.filename) }}</span>
                  </div>
                  <div class="attachment-actions">
                    <el-button
                      v-if="canInlinePreview(att.filename)"
                      type="primary"
                      link
                      size="small"
                      @click="previewAttachment(att)"
                      class="preview-btn"
                    >
                      <el-icon><ZoomIn /></el-icon>
                      预览
                    </el-button>
                    <el-button
                      type="primary"
                      link
                      size="small"
                      @click="downloadAttachment(att)"
                      class="download-btn"
                    >
                      <el-icon><Download /></el-icon>
                      下载
                    </el-button>
                    <el-popconfirm
                      v-if="canEdit"
                      title="确定要删除这个附件吗？"
                      confirm-button-text="删除"
                      cancel-button-text="取消"
                      confirm-button-type="danger"
                      @confirm="deleteAttachment(att)"
                    >
                      <template #reference>
                        <el-button
                          type="danger"
                          link
                          size="small"
                          class="delete-btn"
                        >
                          <el-icon><Delete /></el-icon>
                          删除
                        </el-button>
                      </template>
                    </el-popconfirm>
                  </div>
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


      </div>
    </template>

    <!-- 文章不存在 -->
    <el-empty v-else description="文章不存在或已被删除" class="custom-empty animate-fade-in-up">
      <el-button type="primary" @click="goBack" class="btn-gradient">返回知识库</el-button>
    </el-empty>

    <!-- 附件预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      :title="previewFileName"
      width="85%"
      top="5vh"
      class="attachment-preview-dialog"
      destroy-on-close
      @closed="cleanupPreview"
    >
      <div class="preview-container">
        <!-- 图片预览 -->
        <img
          v-if="previewFileType === 'image'"
          :src="previewFileBlobUrl"
          :alt="previewFileName"
          class="preview-image"
        />
        <!-- PDF 预览 -->
        <iframe
          v-else-if="previewFileType === 'pdf'"
          :src="previewFileBlobUrl"
          class="preview-frame"
          frameborder="0"
        />
        <!-- 文本 / 代码预览：深色主题等宽字体 + 语法高亮 -->
        <pre
          v-else-if="previewFileType === 'text'"
          class="preview-text"
          ><code>{{ previewTextContent }}</code></pre>
        <!-- 视频预览 -->
        <video
          v-else-if="previewFileType === 'video'"
          :src="previewFileBlobUrl"
          controls
          class="preview-video"
        ></video>
        <!-- 音频预览 -->
        <audio
          v-else-if="previewFileType === 'audio'"
          :src="previewFileBlobUrl"
          controls
          class="preview-audio"
        ></audio>
        <!-- 不支持预览的类型（Office 等） -->
        <div v-else class="preview-unsupported">
          <el-icon class="unsupported-icon"><Document /></el-icon>
          <p>该文件类型暂不支持浏览器内在线预览</p>
          <p class="unsupported-tip">点击下方按钮下载后本地查看（Word / Excel / PPT）</p>
          <el-button type="primary" @click="downloadAttachment(previewingAttachment)">
            <el-icon><Download /></el-icon>
            下载文件
          </el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewDialogVisible = false">关闭</el-button>
        <el-button
          v-if="previewingAttachment && canInlinePreview(previewingAttachment.filename)"
          type="primary"
          @click="downloadAttachment(previewingAttachment)"
        >
          <el-icon><Download /></el-icon>
          下载
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import { useUserStore } from '@/stores/user'
import { parseUTCDate } from '@/utils/dateUtils'
import {
  ArrowLeft, User, Folder, Clock, View, Star, StarFilled,
  ChatDotRound, Paperclip, Edit, Share, Download, Document, ZoomIn, Delete
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const API_BASE_URL = import.meta.env.DEV ? '' : 'http://172.18.36.249:5000'

// 状态
const loading = ref(true)
const article = ref(null)
const comments = ref([])
const newComment = ref('')
const isLiked = ref(false)

// 附件预览状态
const previewDialogVisible = ref(false)
const previewFileName = ref('')
const previewFileType = ref('')
const previewFileBlobUrl = ref('')
const previewTextContent = ref('')
const previewingAttachment = ref(null)

// 清理预览资源
const cleanupPreview = () => {
  if (previewFileBlobUrl.value) {
    window.URL.revokeObjectURL(previewFileBlobUrl.value)
    previewFileBlobUrl.value = ''
  }
  previewTextContent.value = ''
}

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

// 删除附件（仅作者 / 超级管理员可删）
const deleteAttachment = async (att) => {
  if (!att?.id || !article.value?.id) return
  try {
    const res = await apiRequest(`/api/knowledge/articles/${article.value.id}/attachments/${att.id}`, {
      method: 'DELETE'
    })
    if (res.success) {
      // 从本地数组里删掉，无需重新拉整页
      const idx = article.value.attachments?.findIndex(a => a.id === att.id)
      if (idx > -1) article.value.attachments.splice(idx, 1)
      ElMessage.success(`已删除附件「${att.filename}」`)
    } else {
      ElMessage.error(res.error || '删除失败')
    }
  } catch (error) {
    console.error('删除附件失败:', error)
    ElMessage.error(error.message || '删除失败')
  }
}

// 下载附件（带 JWT token，避免 401）
const downloadAttachment = async (att) => {
  if (!att?.id) return
  try {
    const token = localStorage.getItem('token')
    const url = `${API_BASE_URL}/api/knowledge/articles/${att.article_id || article.value?.id}/attachments/${att.id}`
    const response = await fetch(url, {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    })
    if (!response.ok) throw new Error('下载失败')
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = att.filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载附件失败:', error)
    ElMessage.error('下载失败')
  }
}

// 获取文件扩展名（小写，不含点）
const getFileExtension = (filename) => {
  if (!filename) return ''
  const parts = filename.split('.')
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : ''
}

// 判断文件类型：image / pdf / text / video / audio / office / other
const getFileType = (filename) => {
  const ext = getFileExtension(filename)
  const imageExts = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'ico']
  if (imageExts.includes(ext)) return 'image'
  if (ext === 'pdf') return 'pdf'
  // 文本类（浏览器原生可读）
  const textExts = ['txt', 'md', 'markdown', 'csv', 'json', 'xml', 'yaml', 'yml',
                    'ini', 'conf', 'cfg', 'log', 'lua', 'py', 'js', 'ts',
                    'html', 'htm', 'css', 'sql', 'sh', 'bat', 'ps1', 'java',
                    'c', 'cpp', 'h', 'go', 'rs', 'rb', 'php', 'r', 'toml',
                    'properties', 'gitignore']
  if (textExts.includes(ext)) return 'text'
  // 视频类
  const videoExts = ['mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv', 'flv', 'wmv']
  if (videoExts.includes(ext)) return 'video'
  // 音频类
  const audioExts = ['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a']
  if (audioExts.includes(ext)) return 'audio'
  // Office（浏览器原生不支持预览，需走外部服务）
  if (['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'].includes(ext)) return 'office'
  return 'other'
}

// 是否支持浏览器内联预览（图片/PDF/文本/视频/音频）
const canInlinePreview = (filename) => {
  const type = getFileType(filename)
  return ['image', 'pdf', 'text', 'video', 'audio'].includes(type)
}

// 获取扩展名标签（大写）
const getFileExtLabel = (filename) => {
  const ext = getFileExtension(filename)
  return ext ? ext.toUpperCase() : '未知'
}

// 根据扩展名返回图标背景色
const getAttachmentIconBg = (filename) => {
  const type = getFileType(filename)
  switch (type) {
    case 'image':  return 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)'
    case 'pdf':    return 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)'
    case 'text':   return 'linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%)'   // 靛蓝（代码/文本）
    case 'video':  return 'linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%)'   // 粉
    case 'audio':  return 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)'   // 绿
    case 'office': return 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)'   // 蓝（MS Office 主色）
    default:       return 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)'
  }
}

// 预览附件（文本类拉 text()，图片/PDF/音视频走 blob URL）
const previewAttachment = async (att) => {
  if (!att?.id) return
  // 清理上一次预览的 blob URL / 文本
  cleanupPreview()

  previewingAttachment.value = att
  previewFileName.value = att.filename
  previewFileType.value = getFileType(att.filename)
  previewDialogVisible.value = true

  if (!canInlinePreview(att.filename)) return

  try {
    const token = localStorage.getItem('token')
    const url = `${API_BASE_URL}/api/knowledge/articles/${att.article_id || article.value?.id}/attachments/${att.id}?inline=1`
    const response = await fetch(url, {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    })
    if (!response.ok) throw new Error('加载预览失败')

    // 文本类：直接取 text()，避免大文件被当作二进制
    if (previewFileType.value === 'text') {
      previewTextContent.value = await response.text()
      return
    }
    // 图片 / PDF / 视频 / 音频：blob URL
    const blob = await response.blob()
    previewFileBlobUrl.value = window.URL.createObjectURL(blob)
  } catch (error) {
    console.error('预览附件失败:', error)
    ElMessage.error('加载预览失败')
    previewDialogVisible.value = false
  }
}

// 编辑文章
const editArticle = () => {
  // 复用知识库主页的编辑弹窗，携带 edit 参数由主页自动打开
  router.push(`/knowledge?edit=${article.value.id}`)
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
  return parseUTCDate(date).toLocaleString('zh-CN')
}

// 格式化相对时间
const formatRelativeTime = (date) => {
  if (!date) return ''
  const now = new Date()
  const past = parseUTCDate(date)
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
  max-width: 900px;
  margin: 0 auto;
}

.main-content {
  min-width: 0;
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
  background: rgba(56, 189, 248, 0.1);
  color: #0ea5e9;
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
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
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
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.article-content :deep(h2) {
  font-size: 24px;
  border-bottom: 2px solid rgba(56, 189, 248, 0.2);
  padding-bottom: 8px;
}

.article-content :deep(h3) {
  font-size: 20px;
}

.article-content :deep(p) {
  margin-bottom: 16px;
}

.article-content :deep(code) {
  background: rgba(56, 189, 248, 0.1);
  padding: 2px 8px;
  border-radius: 6px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  color: #0ea5e9;
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
  border-left: 4px solid #7dd3fc;
  padding: 16px 20px;
  margin: 20px 0;
  background: rgba(56, 189, 248, 0.05);
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
  color: #0ea5e9;
  background: rgba(56, 189, 248, 0.1);
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
  color: #0ea5e9;
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
  flex-shrink: 0;
}

.attachment-icon {
  font-size: 22px;
  color: #0ea5e9;
}

.attachment-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.attachment-name {
  color: #1e293b;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-meta {
  color: #94a3b8;
  font-size: 12px;
  font-weight: 500;
}

.attachment-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.preview-btn,
.download-btn,
.delete-btn {
  font-weight: 500;
}

.preview-btn .el-icon,
.download-btn .el-icon,
.delete-btn .el-icon {
  margin-right: 2px;
}

/* 附件预览对话框样式 */
.attachment-preview-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border-radius: 16px 16px 0 0;
  padding: 18px 24px;
}

.attachment-preview-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: calc(100% - 40px);
}

.attachment-preview-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

.preview-container {
  min-height: 300px;
  max-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border-radius: 12px;
  overflow: hidden;
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
}

.preview-frame {
  width: 100%;
  height: 70vh;
  border: none;
}

/* 文本 / 代码预览：深色主题 + 等宽字体 + 横向滚动 */
.preview-text {
  width: 100%;
  height: 70vh;
  margin: 0;
  padding: 20px 24px;
  background: #0f172a;                    /* slate-900 深色 */
  color: #e2e8f0;
  font-family: 'Cascadia Code', 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.65;
  overflow: auto;
  border-radius: 12px;
  white-space: pre-wrap;
  word-break: break-all;
  tab-size: 2;
}
.preview-text code {
  background: transparent;
  padding: 0;
  font-family: inherit;
  font-size: inherit;
  color: inherit;
  white-space: inherit;
}

/* 视频预览：宽高自适应，居中显示 */
.preview-video {
  max-width: 100%;
  max-height: 70vh;
  background: #000;
  border-radius: 8px;
}

/* 音频预览：水平撑满 */
.preview-audio {
  width: 100%;
  padding: 24px;
}

.preview-unsupported {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  color: #64748b;
}

.unsupported-icon {
  font-size: 64px;
  color: #94a3b8;
}

.preview-unsupported p {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.unsupported-tip {
  font-size: 13px !important;
  color: #94a3b8 !important;
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
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.1);
}

.comment-actions {
  margin-top: 16px;
  text-align: right;
}

.btn-gradient {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border: none;
  color: white;
  border-radius: 10px;
  padding: 12px 24px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.5);
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
