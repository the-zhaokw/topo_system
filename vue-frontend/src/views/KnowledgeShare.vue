<template>
  <div class="knowledge-share-page">
    <!-- 密码验证 -->
    <el-card v-if="requirePassword" class="password-card">
      <template #header>
        <div class="password-header">
          <el-icon><Lock /></el-icon>
          <span>此文章需要密码访问</span>
        </div>
      </template>
      <el-input
        v-model="password"
        type="password"
        placeholder="请输入访问密码"
        @keyup.enter="verifyPassword"
      >
        <template #append>
          <el-button @click="verifyPassword">进入</el-button>
        </template>
      </el-input>
    </el-card>
    
    <!-- 文章内容 -->
    <template v-else-if="article">
      <el-card class="article-card">
        <template #header>
          <div class="article-header">
            <h1>{{ article.title }}</h1>
            <div class="article-meta">
              <span><el-icon><User /></el-icon> {{ article.author }}</span>
              <span><el-icon><Folder /></el-icon> {{ article.category }}</span>
              <span><el-icon><Timer /></el-icon> {{ formatDate(article.updated_at) }}</span>
            </div>
          </div>
        </template>
        
        <div class="article-content" v-html="renderedContent"></div>
        
        <el-divider />
        
        <div class="article-footer">
          <p class="share-notice">
            <el-icon><InfoFilled /></el-icon>
            此文章通过分享链接访问，内容由作者提供
          </p>
          <el-button v-if="allowDownload" @click="downloadArticle">
            <el-icon><Download /></el-icon> 下载原文
          </el-button>
        </div>
      </el-card>
    </template>
    
    <!-- 加载中 -->
    <el-skeleton v-else :rows="10" animated />
    
    <!-- 错误提示 -->
    <el-result
      v-if="error"
      icon="error"
      :title="error.title"
      :sub-title="error.message"
    >
      <template #extra>
        <el-button @click="$router.push('/knowledge')">返回知识库</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()

const API_BASE_URL = import.meta.env.DEV ? 'http://localhost:5000' : 'http://172.18.36.249:5000'

const article = ref(null)
const requirePassword = ref(false)
const password = ref('')
const allowDownload = ref(false)
const error = ref(null)

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
.knowledge-share-page {
  max-width: 900px;
  margin: 40px auto;
  padding: 0 20px;
}

.password-card {
  max-width: 400px;
  margin: 100px auto;
}

.password-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
}

.article-card {
  margin-bottom: 20px;
}

.article-header {
  text-align: center;
}

.article-header h1 {
  margin: 0 0 16px 0;
  font-size: 28px;
  color: #303133;
}

.article-meta {
  display: flex;
  justify-content: center;
  gap: 20px;
  color: #909399;
  font-size: 14px;
}

.article-meta span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.article-content {
  line-height: 1.8;
  color: #303133;
  font-size: 16px;
}

.article-content :deep(h1),
.article-content :deep(h2),
.article-content :deep(h3) {
  margin-top: 32px;
  margin-bottom: 16px;
}

.article-content :deep(p) {
  margin-bottom: 16px;
}

.article-content :deep(pre) {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
}

.article-content :deep(code) {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.article-content :deep(blockquote) {
  border-left: 4px solid #409eff;
  margin: 0;
  padding-left: 16px;
  color: #606266;
}

.article-content :deep(img) {
  max-width: 100%;
  border-radius: 4px;
}

.article-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.article-content :deep(th),
.article-content :deep(td) {
  border: 1px solid #dcdfe6;
  padding: 12px;
  text-align: left;
}

.article-content :deep(th) {
  background: #f5f7fa;
}

.article-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
}

.share-notice {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 14px;
  margin: 0;
}

@media screen and (max-width: 768px) {
  .knowledge-share-page {
    margin: 20px auto;
    padding: 0 12px;
  }

  .password-card {
    max-width: 100%;
    margin: 40px auto;
  }

  .password-header {
    font-size: 15px;
  }

  .article-card {
    margin-bottom: 12px;
  }

  .article-header h1 {
    font-size: 22px;
    margin-bottom: 12px;
  }

  .article-meta {
    flex-wrap: wrap;
    gap: 12px;
    font-size: 13px;
  }

  .article-content {
    font-size: 14px;
    line-height: 1.6;
  }

  .article-content :deep(h1) {
    font-size: 20px;
    margin-top: 24px;
    margin-bottom: 12px;
  }

  .article-content :deep(h2) {
    font-size: 18px;
    margin-top: 20px;
    margin-bottom: 10px;
  }

  .article-content :deep(h3) {
    font-size: 16px;
    margin-top: 16px;
    margin-bottom: 8px;
  }

  .article-content :deep(p) {
    margin-bottom: 12px;
  }

  .article-content :deep(pre) {
    padding: 12px;
    font-size: 12px;
  }

  .article-content :deep(code) {
    font-size: 12px;
    padding: 2px 4px;
  }

  .article-content :deep(blockquote) {
    padding-left: 12px;
  }

  .article-content :deep(table) {
    font-size: 13px;
  }

  .article-content :deep(th),
  .article-content :deep(td) {
    padding: 8px;
  }

  .article-footer {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
    padding: 16px 0;
  }

  .share-notice {
    font-size: 13px;
  }
}

@media screen and (max-width: 480px) {
  .knowledge-share-page {
    margin: 12px auto;
    padding: 0 8px;
  }

  .password-card {
    margin: 20px auto;
  }

  .password-header {
    font-size: 14px;
  }

  .article-header h1 {
    font-size: 18px;
    margin-bottom: 8px;
  }

  .article-meta {
    gap: 8px;
    font-size: 12px;
  }

  .article-content {
    font-size: 13px;
  }

  .article-content :deep(h1) {
    font-size: 18px;
  }

  .article-content :deep(h2) {
    font-size: 16px;
  }

  .article-content :deep(h3) {
    font-size: 14px;
  }

  .article-content :deep(pre) {
    padding: 8px;
    font-size: 11px;
  }

  .article-content :deep(code) {
    font-size: 11px;
  }

  .article-content :deep(th),
  .article-content :deep(td) {
    padding: 6px;
    font-size: 12px;
  }

  .share-notice {
    font-size: 12px;
  }
}
</style>
