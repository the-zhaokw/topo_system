<template>
  <div class="share-manager">
    <div class="share-header">
      <h3>分享管理</h3>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon> 创建分享
      </el-button>
    </div>
    
    <!-- 分享列表 -->
    <el-table :data="shares" v-loading="loading">
      <el-table-column prop="share_token" label="分享链接" width="200">
        <template #default="{ row }">
          <el-link type="primary" @click="copyLink(row)">
            {{ row.share_token.substring(0, 16) }}...
          </el-link>
        </template>
      </el-table-column>
      
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      
      <el-table-column prop="expire_at" label="过期时间" width="180">
        <template #default="{ row }">
          <el-tag v-if="row.is_expired" type="danger">已过期</el-tag>
          <span v-else-if="row.expire_at">{{ formatDate(row.expire_at) }}</span>
          <el-tag v-else type="success">永久有效</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="has_password" label="密码保护" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.has_password" type="warning">有密码</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      
      <el-table-column prop="view_count" label="访问次数" width="100" />
      
      <el-table-column prop="allow_download" label="允许下载" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.allow_download" type="success">是</el-tag>
          <el-tag v-else type="info">否</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="copyLink(row)">复制链接</el-button>
          <el-button size="small" type="danger" @click="deleteShare(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 创建分享对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建分享" width="500px">
      <el-form :model="shareForm" label-width="100px">
        <el-form-item label="密码保护">
          <el-switch v-model="shareForm.enablePassword" />
        </el-form-item>
        
        <el-form-item label="访问密码" v-if="shareForm.enablePassword">
          <el-input v-model="shareForm.password" placeholder="设置访问密码" show-password />
        </el-form-item>
        
        <el-form-item label="过期时间">
          <el-radio-group v-model="shareForm.expireType">
            <el-radio label="never">永久有效</el-radio>
            <el-radio label="custom">自定义</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="选择时间" v-if="shareForm.expireType === 'custom'">
          <el-date-picker
            v-model="shareForm.expireAt"
            type="datetime"
            placeholder="选择过期时间"
            :disabled-date="disabledDate"
          />
        </el-form-item>
        
        <el-form-item label="允许下载">
          <el-switch v-model="shareForm.allowDownload" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createShare">创建</el-button>
      </template>
    </el-dialog>
    
    <!-- 分享成功对话框 -->
    <el-dialog v-model="showSuccessDialog" title="分享创建成功" width="500px">
      <div class="share-success">
        <el-result icon="success" title="分享链接已创建">
          <template #sub-title>
            <div class="share-link">
              <el-input v-model="createdShare.url" readonly>
                <template #append>
                  <el-button @click="copyToClipboard(createdShare.url)">复制</el-button>
                </template>
              </el-input>
            </div>
            <div v-if="createdShare.password" class="share-password">
              访问密码: <el-tag>{{ createdShare.password }}</el-tag>
            </div>
          </template>
        </el-result>
        
        <div class="share-qrcode" v-if="createdShare.url">
          <p>扫描二维码访问</p>
          <!-- 这里可以集成二维码生成组件 -->
          <div class="qrcode-placeholder">
            <el-icon><FullScreen /></el-icon>
            <span>二维码区域</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  articleId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['refresh'])

const loading = ref(false)
const shares = ref([])
const showCreateDialog = ref(false)
const showSuccessDialog = ref(false)
const isMounted = ref(true)

const shareForm = reactive({
  enablePassword: false,
  password: '',
  expireType: 'never',
  expireAt: null,
  allowDownload: true
})

const createdShare = reactive({
  url: '',
  password: ''
})

// 加载分享列表
const loadShares = async () => {
  if (!props.articleId || !isMounted.value) {
    return
  }
  loading.value = true
  try {
    const res = await fetch(`/api/knowledge/articles/${props.articleId}/shares`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    const data = await res.json()
    if (isMounted.value) {
      shares.value = (data.items || []).map(item => ({
        ...item,
        is_expired: item.expire_at && new Date(item.expire_at) < new Date()
      }))
    }
  } catch (error) {
    if (isMounted.value) {
      ElMessage.error('加载分享列表失败')
    }
  } finally {
    if (isMounted.value) {
      loading.value = false
    }
  }
}

// 创建分享
const createShare = async () => {
  if (!props.articleId || !isMounted.value) {
    ElMessage.error('文章信息不完整')
    return
  }
  try {
    const body = {
      allow_download: shareForm.allowDownload
    }
    
    if (shareForm.enablePassword && shareForm.password) {
      body.password = shareForm.password
    }
    
    if (shareForm.expireType === 'custom' && shareForm.expireAt) {
      body.expire_at = shareForm.expireAt.toISOString()
    }
    
    const res = await fetch(`/api/knowledge/articles/${props.articleId}/shares`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(body)
    })
    
    if (res.ok) {
      const data = await res.json()
      // 使用 hash 模式的路由格式生成分享链接
      createdShare.url = `${window.location.origin}/#${data.share_url}`
      createdShare.password = shareForm.enablePassword ? shareForm.password : ''
      
      showCreateDialog.value = false
      showSuccessDialog.value = true
      
      // 重置表单
      shareForm.enablePassword = false
      shareForm.password = ''
      shareForm.expireType = 'never'
      shareForm.expireAt = null
      
      loadShares()
      emit('refresh')
    } else {
      const errorData = await res.json()
      ElMessage.error(errorData.error || '创建分享失败')
    }
  } catch (error) {
    ElMessage.error('创建分享失败')
  }
}

// 删除分享
const deleteShare = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个分享链接吗？', '确认删除', {
      type: 'warning'
    })
    
    const res = await fetch(`/api/knowledge/shares/${row.id}`, { 
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (res.ok) {
      ElMessage.success('删除成功')
      loadShares()
      emit('refresh')
    } else {
      const data = await res.json()
      ElMessage.error(data.error || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 复制链接
const copyLink = (row) => {
  // 使用 hash 模式的路由格式生成分享链接
  const url = `${window.location.origin}/#/knowledge/share/${row.share_token}`
  copyToClipboard(url)
}

const copyToClipboard = (text) => {
  if (!text) {
    ElMessage.error('没有可复制的内容')
    return
  }
  
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      ElMessage.success('链接已复制到剪贴板')
    }).catch(() => {
      fallbackCopyToClipboard(text)
    })
  } else {
    fallbackCopyToClipboard(text)
  }
}

const fallbackCopyToClipboard = (text) => {
  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.select()
  try {
    const successful = document.execCommand('copy')
    if (successful) {
      ElMessage.success('链接已复制到剪贴板')
    } else {
      ElMessage.error('复制失败')
    }
  } catch (err) {
    ElMessage.error('复制失败')
  }
  document.body.removeChild(textarea)
}

// 禁用过去的日期
const disabledDate = (date) => {
  return date < new Date()
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

// 组件卸载时标记为未挂载
onUnmounted(() => {
  isMounted.value = false
})

// 初始化
loadShares()
</script>

<style scoped>
.share-manager {
  padding: 20px;
}

.share-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.share-header h3 {
  margin: 0;
}

.share-success {
  text-align: center;
}

.share-link {
  margin: 20px 0;
}

.share-password {
  margin-top: 10px;
  font-size: 14px;
}

.share-qrcode {
  margin-top: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.share-qrcode p {
  margin: 0 0 10px 0;
  color: #606266;
}

.qrcode-placeholder {
  width: 200px;
  height: 200px;
  margin: 0 auto;
  border: 2px dashed #dcdfe6;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.qrcode-placeholder .el-icon {
  font-size: 48px;
  margin-bottom: 10px;
}
</style>
