<template>
  <div class="knowledge-share-page">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Share /></el-icon>
          </div>
          <div class="title-text">
            <h1>知识分享</h1>
            <p class="subtitle">安全、便捷的知识共享平台</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-total">
            <div class="stat-icon-wrapper stat-icon-wrapper-total">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.totalShares }}</div>
              <div class="stat-label">分享总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-month">
            <div class="stat-icon-wrapper stat-icon-wrapper-month">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.monthShares }}</div>
              <div class="stat-label">本月分享</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-likes">
            <div class="stat-icon-wrapper stat-icon-wrapper-likes">
              <el-icon><Star /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.totalLikes }}</div>
              <div class="stat-label">获赞数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-favorites">
            <div class="stat-icon-wrapper stat-icon-wrapper-favorites">
              <el-icon><Collection /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.totalFavorites }}</div>
              <div class="stat-label">被收藏数</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 密码验证 -->
    <el-card v-if="requirePassword" class="password-card glass-card animate-fade-in-up delay-200">
      <template #header>
        <div class="password-header">
          <div class="password-icon-wrapper">
            <el-icon><Lock /></el-icon>
          </div>
          <div class="password-title">
            <h3>此文章需要密码访问</h3>
            <p class="password-subtitle">请输入访问密码以查看内容</p>
          </div>
        </div>
      </template>
      <div class="password-form">
        <el-input
          v-model="password"
          type="password"
          placeholder="请输入访问密码"
          @keyup.enter="verifyPassword"
          size="large"
          class="password-input"
        >
          <template #prefix>
            <el-icon><Key /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="verifyPassword" size="large" class="btn-gradient">
          <el-icon><Right /></el-icon>
          进入
        </el-button>
      </div>
    </el-card>

    <!-- 文章内容 -->
    <template v-else-if="article">
      <el-card class="article-card glass-card animate-fade-in-up delay-200" shadow="hover">
        <template #header>
          <div class="article-header">
            <div class="article-category-badge" v-if="article.category">
              <el-icon><Folder /></el-icon>
              {{ article.category }}
            </div>
            <h1 class="article-title">{{ article.title }}</h1>
            <div class="article-meta">
              <div class="meta-item meta-author">
                <div class="meta-icon-wrapper">
                  <el-icon><User /></el-icon>
                </div>
                <div class="meta-content">
                  <span class="meta-label">作者</span>
                  <span class="meta-value">{{ article.author }}</span>
                </div>
              </div>
              <div class="meta-divider"></div>
              <div class="meta-item meta-time">
                <div class="meta-icon-wrapper">
                  <el-icon><Timer /></el-icon>
                </div>
                <div class="meta-content">
                  <span class="meta-label">更新时间</span>
                  <span class="meta-value">{{ formatDate(article.updated_at) }}</span>
                </div>
              </div>
              <div class="meta-divider"></div>
              <div class="meta-item meta-views">
                <div class="meta-icon-wrapper">
                  <el-icon><View /></el-icon>
                </div>
                <div class="meta-content">
                  <span class="meta-label">阅读</span>
                  <span class="meta-value">{{ article.views || 0 }}</span>
                </div>
              </div>
            </div>
          </div>
        </template>

        <div class="article-content" v-html="renderedContent"></div>

        <el-divider class="article-divider" />

        <div class="article-footer">
          <div class="share-notice">
            <div class="notice-icon">
              <el-icon><InfoFilled /></el-icon>
            </div>
            <div class="notice-content">
              <span class="notice-title">安全提示</span>
              <span class="notice-text">此文章通过分享链接访问，内容由作者提供</span>
            </div>
          </div>
          <el-button v-if="allowDownload" @click="downloadArticle" class="btn-download">
            <el-icon><Download /></el-icon>
            下载原文
          </el-button>
        </div>
      </el-card>
    </template>

    <!-- 加载中 -->
    <el-skeleton v-else :rows="10" animated class="loading-skeleton animate-fade-in-up delay-200" />

    <!-- 错误提示 -->
    <el-result
      v-if="error"
      icon="error"
      :title="error.title"
      :sub-title="error.message"
      class="error-result animate-fade-in-up"
    >
      <template #extra>
        <el-button @click="$router.push('/knowledge')" class="btn-gradient">
          <el-icon><Back /></el-icon>
          返回知识库
        </el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import { Lock, User, Folder, Timer, InfoFilled, Download, Share, Document, Calendar, Star, Collection, Key, Right, View, Back } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const API_BASE_URL = import.meta.env.DEV ? 'http://localhost:5000' : 'http://172.18.36.249:5000'

const article = ref(null)
const requirePassword = ref(false)
const password = ref('')
const allowDownload = ref(false)
const error = ref(null)

// 统计数据（模拟数据，实际应从API获取）
const stats = ref({
  totalShares: 128,
  monthShares: 24,
  totalLikes: 356,
  totalFavorites: 89
})

const shareToken = route.params.token

const renderedContent = computed(() => {
  if (!article.value?.content) return ''
  return marked(article.value.content)
})

// 加载分享内容
const loadShare = async (pwd = null) => {
  try {
    let url = `${API_BASE_URL}/api/knowledge/enhanced/share/${shareToken}`
    if (pwd) {
      url += `?password=${encodeURIComponent(pwd)}`
    }

    const res = await fetch(url)
    const data = await res.json()

    if (res.ok) {
      article.value = data.article
      allowDownload.value = data.allow_download
      requirePassword.value = false
    } else if (res.status === 403 && data.require_password) {
      requirePassword.value = true
    } else if (res.status === 410) {
      error.value = { title: '链接已过期', message: '此分享链接已过期，请联系作者获取新的链接' }
    } else {
      error.value = { title: '访问失败', message: data.error || '无法访问此文章' }
    }
  } catch (e) {
    error.value = { title: '加载失败', message: '网络错误，请稍后重试' }
  }
}

// 验证密码
const verifyPassword = () => {
  if (!password.value) {
    ElMessage.warning('请输入密码')
    return
  }
  loadShare(password.value)
}

// 下载文章
const downloadArticle = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/api/knowledge/enhanced/share/${shareToken}/download`)
    if (res.ok) {
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url

      // 从响应头中获取文件名
      const contentDisposition = res.headers.get('Content-Disposition')
      let filename = `${article.value.title}.md`
      if (contentDisposition) {
        // 优先尝试匹配 filename* (RFC 5987)
        const filenameStarMatch = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i)
        if (filenameStarMatch && filenameStarMatch[1]) {
          filename = decodeURIComponent(filenameStarMatch[1])
        } else {
          // 回退到普通 filename
          const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
          if (filenameMatch && filenameMatch[1]) {
            filename = decodeURIComponent(filenameMatch[1].replace(/['"]/g, ''))
          }
        }
      }
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      ElMessage.success('下载成功')
    } else {
      const data = await res.json().catch(() => ({}))
      ElMessage.error(data.error || '下载失败')
    }
  } catch (e) {
    ElMessage.error('下载失败：网络错误')
  }
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  loadShare()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.knowledge-share-page {
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

/* 统计卡片区域 */
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.stat-card::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  transform: scaleX(0);
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.15), 0 10px 20px -5px rgba(0, 0, 0, 0.1);
}

.stat-card:hover::before {
  transform: scaleX(1);
}

.stat-card-total::before { background: linear-gradient(90deg, #7dd3fc, #38bdf8); }
.stat-card-month::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-likes::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-favorites::before { background: linear-gradient(90deg, #ec4899, #f472b6); }

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: all 0.4s;
}

.stat-card:hover .stat-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.stat-icon-wrapper-total {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #7dd3fc;
  box-shadow: 0 4px 15px -3px rgba(56, 189, 248, 0.4);
}

.stat-icon-wrapper-month {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-likes {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-favorites {
  background: linear-gradient(135deg, #fce7f3 0%, #f9a8d4 100%);
  color: #db2777;
  box-shadow: 0 4px 15px -3px rgba(236, 72, 153, 0.4);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 26px;
  font-weight: 800;
  line-height: 1.2;
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-card-total .stat-value {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-month .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-likes .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-favorites .stat-value {
  background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
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

/* 密码卡片 */
.password-card {
  max-width: 480px;
  margin: 40px auto;
}

.password-card :deep(.el-card__header) {
  padding: 24px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.password-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.password-icon-wrapper {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
  box-shadow: 0 8px 20px -5px rgba(56, 189, 248, 0.4);
}

.password-title h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.password-subtitle {
  margin: 0;
  font-size: 13px;
  color: #64748b;
}

.password-form {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.password-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* 文章卡片 */
.article-card {
  margin-bottom: 24px;
}

.article-card :deep(.el-card__header) {
  padding: 28px 32px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.article-header {
  text-align: center;
}

.article-category-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #7dd3fc;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 16px;
}

.article-title {
  margin: 0 0 24px 0;
  font-size: 32px;
  font-weight: 800;
  color: #1e293b;
  line-height: 1.3;
  letter-spacing: -0.5px;
}

.article-meta {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.meta-icon-wrapper {
  width: 40px;
  height: 40px;
  background: rgba(241, 245, 249, 0.8);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-size: 18px;
}

.meta-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.meta-label {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.meta-value {
  font-size: 14px;
  color: #1e293b;
  font-weight: 600;
}

.meta-divider {
  width: 1px;
  height: 40px;
  background: linear-gradient(180deg, transparent, #e2e8f0, transparent);
}

/* 文章内容 */
.article-content {
  padding: 32px;
  line-height: 1.8;
  color: #334155;
  font-size: 16px;
}

.article-content :deep(h1),
.article-content :deep(h2),
.article-content :deep(h3) {
  margin-top: 40px;
  margin-bottom: 20px;
  color: #1e293b;
  font-weight: 700;
}

.article-content :deep(h1) {
  font-size: 28px;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 12px;
}

.article-content :deep(h2) {
  font-size: 24px;
}

.article-content :deep(h3) {
  font-size: 20px;
}

.article-content :deep(p) {
  margin-bottom: 20px;
}

.article-content :deep(pre) {
  background: #f8fafc;
  padding: 20px;
  border-radius: 12px;
  overflow-x: auto;
  border: 1px solid #e2e8f0;
  margin: 20px 0;
}

.article-content :deep(code) {
  background: #f1f5f9;
  padding: 3px 8px;
  border-radius: 6px;
  font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  font-size: 14px;
  color: #ec4899;
}

.article-content :deep(pre code) {
  background: none;
  padding: 0;
  color: #334155;
}

.article-content :deep(blockquote) {
  border-left: 4px solid #7dd3fc;
  margin: 24px 0;
  padding: 16px 24px;
  background: rgba(56, 189, 248, 0.05);
  border-radius: 0 12px 12px 0;
  color: #475569;
}

.article-content :deep(img) {
  max-width: 100%;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin: 20px 0;
}

.article-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 24px 0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.article-content :deep(th),
.article-content :deep(td) {
  border: 1px solid #e2e8f0;
  padding: 14px 16px;
  text-align: left;
}

.article-content :deep(th) {
  background: #f8fafc;
  font-weight: 600;
  color: #1e293b;
}

.article-content :deep(tr:nth-child(even)) {
  background: #fafafa;
}

.article-content :deep(ul),
.article-content :deep(ol) {
  margin: 16px 0;
  padding-left: 24px;
}

.article-content :deep(li) {
  margin: 8px 0;
}

.article-divider {
  margin: 0 32px;
}

/* 文章底部 */
.article-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  flex-wrap: wrap;
  gap: 16px;
}

.share-notice {
  display: flex;
  align-items: center;
  gap: 14px;
}

.notice-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #d97706;
  font-size: 20px;
}

.notice-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.notice-title {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

.notice-text {
  font-size: 12px;
  color: #64748b;
}

.btn-download {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 10px;
  transition: all 0.3s;
}

.btn-download:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.5);
  color: white;
}

/* 按钮样式 */
.btn-gradient {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border: none;
  color: white;
  transition: all 0.3s;
  border-radius: 10px;
  padding: 12px 24px;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.5);
  color: white;
}

/* 加载骨架屏 */
.loading-skeleton {
  padding: 32px;
}

/* 错误结果 */
.error-result {
  margin-top: 60px;
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
  .knowledge-share-page {
    padding: 0;
  }

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

  .stats-row {
    margin-bottom: 20px;
  }

  .stat-card {
    padding: 16px;
    gap: 12px;
    margin-bottom: 12px;
  }

  .stat-icon-wrapper {
    width: 44px;
    height: 44px;
    border-radius: 12px;
  }

  .stat-value {
    font-size: 22px;
  }

  .stat-label {
    font-size: 12px;
  }

  .password-card {
    max-width: 100%;
    margin: 20px auto;
  }

  .password-header {
    gap: 12px;
  }

  .password-icon-wrapper {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    font-size: 24px;
  }

  .password-title h3 {
    font-size: 16px;
  }

  .article-card :deep(.el-card__header) {
    padding: 20px;
  }

  .article-title {
    font-size: 24px;
    margin-bottom: 20px;
  }

  .article-category-badge {
    font-size: 12px;
    padding: 5px 12px;
  }

  .article-meta {
    gap: 16px;
  }

  .meta-item {
    gap: 10px;
  }

  .meta-icon-wrapper {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    font-size: 16px;
  }

  .meta-value {
    font-size: 13px;
  }

  .meta-divider {
    display: none;
  }

  .article-content {
    padding: 20px;
    font-size: 15px;
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

  .article-content :deep(pre) {
    padding: 16px;
  }

  .article-divider {
    margin: 0 20px;
  }

  .article-footer {
    flex-direction: column;
    padding: 20px;
    align-items: flex-start;
  }

  .share-notice {
    gap: 12px;
  }

  .notice-icon {
    width: 40px;
    height: 40px;
  }

  .btn-download {
    width: 100%;
  }
}

@media screen and (max-width: 480px) {
  .page-header {
    padding: 16px;
  }

  .title-text h1 {
    font-size: 20px;
  }

  .stat-card {
    padding: 14px;
  }

  .stat-value {
    font-size: 20px;
  }

  .article-title {
    font-size: 20px;
  }

  .article-content {
    padding: 16px;
    font-size: 14px;
  }

  .article-content :deep(h1) {
    font-size: 20px;
  }

  .article-content :deep(h2) {
    font-size: 18px;
  }

  .article-content :deep(h3) {
    font-size: 16px;
  }

  .article-content :deep(pre) {
    padding: 12px;
  }

  .article-content :deep(code) {
    font-size: 12px;
  }
}
</style>
