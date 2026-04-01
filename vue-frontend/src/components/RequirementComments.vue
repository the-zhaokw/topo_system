<template>
  <div class="requirement-comments">
    <!-- 评论输入框 -->
    <div class="comment-input-wrapper">
      <el-input
        v-model="newComment"
        type="textarea"
        :rows="3"
        placeholder="发表评论..."
        maxlength="500"
        show-word-limit
      />
      <div class="comment-actions">
        <el-button type="primary" size="small" @click="submitComment" :disabled="!newComment.trim()">
          发表评论
        </el-button>
      </div>
    </div>

    <!-- 评论列表 -->
    <div class="comments-list" v-if="comments.length > 0">
      <div v-for="comment in comments" :key="comment.id" class="comment-item">
        <div class="comment-header">
          <span class="comment-author">{{ comment.creator_name }}</span>
          <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
          <el-button 
            type="danger" 
            link 
            size="small" 
            @click="deleteComment(comment)"
            v-if="canDelete(comment)"
          >
            删除
          </el-button>
        </div>
        <div class="comment-content">{{ comment.content }}</div>
      </div>
    </div>

    <el-empty v-else description="暂无评论" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import api from '@/services/api'

const props = defineProps({
  targetType: {
    type: String,
    required: true
  },
  targetId: {
    type: Number,
    required: true
  }
})

const userStore = useUserStore()
const comments = ref([])
const newComment = ref('')
const loading = ref(false)

const fetchComments = async () => {
  try {
    let response
    if (props.targetType === 'document') {
      response = await api.get(`/requirement-documents/${props.targetId}/comments`)
    } else {
      response = await api.get(`/requirement-items/${props.targetId}/comments`)
    }
    
    if (response.success) {
      comments.value = response.comments || []
    }
  } catch (error) {
    console.error('获取评论失败:', error)
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) return
  
  try {
    const data = {
      target_type: props.targetType,
      target_id: props.targetId,
      content: newComment.value.trim()
    }
    
    const response = await api.post('/requirement-comments', data)
    if (response.success) {
      ElMessage.success('评论发表成功')
      newComment.value = ''
      fetchComments()
    }
  } catch (error) {
    console.error('发表评论失败:', error)
    ElMessage.error(error.response?.data?.error || '发表评论失败')
  }
}

const deleteComment = async (comment) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评论吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const response = await api.delete(`/requirement-comments/${comment.id}`)
    if (response.success) {
      ElMessage.success('评论删除成功')
      fetchComments()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除评论失败:', error)
      ElMessage.error(error.response?.data?.error || '删除失败')
    }
  }
}

const canDelete = (comment) => {
  const user = userStore.currentUser
  if (!user) return false
  return comment.created_by === user.id || user.role === 'admin' || user.role === 'manager' || user.role === 'project_manager'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchComments()
})
</script>

<style scoped>
.requirement-comments {
  padding: 0;
}

.comment-input-wrapper {
  margin-bottom: 16px;
}

.comment-actions {
  margin-top: 8px;
  text-align: right;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-item {
  padding: 12px;
  background-color: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.comment-author {
  font-weight: 600;
  color: #303133;
}

.comment-time {
  color: #909399;
  font-size: 12px;
}

.comment-content {
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
}
</style>
