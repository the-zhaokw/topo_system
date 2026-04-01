<template>
  <div class="article-form">
    <el-form :model="form" label-position="top" ref="formRef">
      <el-row :gutter="24">
        <el-col :span="16">
          <!-- 标题 -->
          <el-form-item label="文章标题" required>
            <el-input
              v-model="form.title"
              placeholder="请输入文章标题"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>

          <!-- 摘要 -->
          <el-form-item label="文章摘要">
            <el-input
              v-model="form.summary"
              type="textarea"
              :rows="2"
              placeholder="请输入文章摘要（可选），如不填写将自动提取正文前200字"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <!-- 内容编辑器 -->
          <el-form-item label="文章内容" required>
            <RichTextEditor
              ref="contentEditorRef"
              v-model="form.content"
              placeholder="请输入文章内容，支持富文本编辑和图片上传"
              :rows="8"
            />
          </el-form-item>

          <!-- 附件上传 -->
          <el-form-item label="附件">
            <el-upload
              action="/api/knowledge/upload"
              multiple
              :on-success="handleUploadSuccess"
              :on-remove="handleRemove"
              :file-list="fileList"
              class="upload-area"
            >
              <el-button type="primary" plain>
                <el-icon><Upload /></el-icon>
                上传附件
              </el-button>
              <template #tip>
                <div class="upload-tip">支持上传文档、图片等文件，单个文件不超过 50MB</div>
              </template>
            </el-upload>
          </el-form-item>
        </el-col>

        <el-col :span="8">
          <!-- 分类 -->
          <el-form-item label="所属分类">
            <CategoryManager
              v-model="form.category_id"
              :categories="categories"
              @change="handleCategoryChange"
              @refresh="$emit('refresh-categories')"
            />
          </el-form-item>

          <!-- 标签 -->
          <el-form-item label="标签">
            <el-select
              v-model="form.tags"
              multiple
              filterable
              allow-create
              placeholder="添加标签"
              style="width: 100%"
            >
              <el-option
                v-for="tag in availableTags"
                :key="tag"
                :label="tag"
                :value="tag"
              />
            </el-select>
          </el-form-item>

          <!-- 文章设置 -->
          <el-form-item label="文章设置">
            <div class="settings-group">
              <el-checkbox v-model="form.is_public">公开可见</el-checkbox>
              <el-checkbox v-model="form.allow_comment">允许评论</el-checkbox>
              <el-checkbox v-model="form.is_pinned">置顶文章</el-checkbox>
            </div>
          </el-form-item>

          <!-- 作者（仅管理员可见，可编辑） -->
          <el-form-item v-if="isAdmin" label="文章作者">
            <div class="author-selector">
              <el-avatar :size="24" :src="selectedAuthor?.avatar" />
              <span class="author-name">{{ selectedAuthor?.username || '请选择作者' }}</span>
              <el-button size="small" @click="showUserSelector = true">选择</el-button>
            </div>
          </el-form-item>

          <!-- 非管理员显示真实作者（不可编辑） -->
          <el-form-item v-else label="文章作者">
            <div class="author-display">
              <el-avatar :size="24" :src="article?.author_avatar" />
              <span class="author-name">{{ article?.author_name || userStore.currentUser?.username }}</span>
            </div>
          </el-form-item>

          <!-- 用户选择弹窗 -->
          <el-dialog v-model="showUserSelector" title="选择作者" width="500px">
            <el-input v-model="userSearchKeyword" placeholder="搜索用户名..." clearable class="mb-3" />
            <el-table
              :data="filteredUserList"
              style="width: 100%"
              max-height="400"
              @row-click="handleSelectAuthor"
              highlight-current-row
            >
              <el-table-column label="用户" min-width="150">
                <template #default="{ row }">
                  <div class="user-option">
                    <el-avatar :size="32" :src="row.avatar" />
                    <span>{{ row.username }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="role" label="职位" width="100" />
              <el-table-column label="操作" width="80" align="center">
                <template #default="{ row }">
                  <el-button v-if="row.id === form.author_id" type="primary" size="small" disabled>已选</el-button>
                  <el-button v-else size="small" @click.stop="handleSelectAuthor(row)">选择</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-dialog>

          <!-- 封面图片 -->
          <el-form-item label="封面图片">
            <el-upload
              class="cover-uploader"
              action="/api/knowledge/upload"
              :show-file-list="false"
              :on-success="handleCoverSuccess"
              accept="image/*"
            >
              <img v-if="form.cover_image" :src="form.cover_image" class="cover-image" />
              <div v-else class="cover-placeholder">
                <el-icon><Plus /></el-icon>
                <span>上传封面</span>
              </div>
            </el-upload>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <!-- 底部操作栏 -->
    <div class="form-actions">
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button type="info" @click="saveDraft">保存草稿</el-button>
      <el-button type="primary" @click="publishArticle">发布文章</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Upload } from '@element-plus/icons-vue'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import CategoryManager from './CategoryManager.vue'
import { useUserStore } from '@/stores/user'

const props = defineProps({
  article: {
    type: Object,
    default: null
  },
  categories: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['save', 'cancel', 'refresh-categories'])

const userStore = useUserStore()

// API 基础 URL
const API_BASE_URL = import.meta.env.DEV ? '' : 'http://172.18.36.249:5000'

// 表单引用
const formRef = ref(null)

// 表单数据
const form = reactive({
  title: '',
  summary: '',
  content: '',
  category_id: null,
  tags: [],
  is_public: true,
  allow_comment: true,
  is_pinned: false,
  cover_image: '',
  attachments: [],
  author_id: null
})

// 文件列表
const fileList = ref([])

// 用户列表
const userList = ref([])
const showUserSelector = ref(false)
const userSearchKeyword = ref('')

// 判断是否为管理员
const isAdmin = computed(() => {
  const user = userStore.currentUser
  if (!user) return false
  if (user.is_super_admin) return true
  return user.position === '管理员' || user.position?.includes('经理')
})

// 当前选中的作者
const selectedAuthor = computed(() => {
  return userList.value.find(u => u.id === form.author_id) || null
})

// 过滤后的用户列表
const filteredUserList = computed(() => {
  if (!userSearchKeyword.value) return userList.value
  const keyword = userSearchKeyword.value.toLowerCase()
  return userList.value.filter(u =>
    u.username?.toLowerCase().includes(keyword)
  )
})

// 选择作者
const handleSelectAuthor = (user) => {
  form.author_id = user.id
  showUserSelector.value = false
}

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

// 加载用户列表
const loadUsers = async () => {
  if (!isAdmin.value) return
  try {
    const response = await apiRequest('/api/users')
    userList.value = response.users || response.data || []
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

// 可用标签
const availableTags = ref(['教程', '文档', '笔记', '分享', '问题', '解决方案'])

// 初始化表单数据
onMounted(() => {
  if (props.article) {
    form.title = props.article.title || ''
    form.summary = props.article.summary || ''
    form.content = props.article.content || ''
    form.category_id = props.article.category_id || null
    form.tags = props.article.tags || []
    form.is_public = props.article.is_public !== false
    form.allow_comment = props.article.allow_comment !== false
    form.is_pinned = props.article.is_pinned || false
    form.cover_image = props.article.cover_image || ''
    form.attachments = props.article.attachments || []
    form.author_id = props.article.author_id || null
    fileList.value = props.article.attachments?.map(att => ({
      name: att.filename,
      url: att.file_path,
      ...att
    })) || []
  } else {
    form.author_id = userStore.currentUser?.id
  }
  loadUsers()
})

// 处理封面上传成功
const handleCoverSuccess = (response) => {
  form.cover_image = response.url || response.data?.url
  ElMessage.success('封面上传成功')
}

// 处理附件上传成功
const handleUploadSuccess = (response, file) => {
  const attachment = {
    id: response.id || Date.now(),
    filename: file.name,
    file_path: response.url || response.data?.url,
    file_size: file.size
  }
  form.attachments.push(attachment)
  ElMessage.success('附件上传成功')
}

// 处理附件移除
const handleRemove = (file, fileList) => {
  const index = form.attachments.findIndex(att => att.filename === file.name)
  if (index > -1) {
    form.attachments.splice(index, 1)
  }
}

// 处理分类变化
const handleCategoryChange = (value) => {
  form.category_id = value
}

// 验证表单
const validateForm = () => {
  if (!form.title.trim()) {
    ElMessage.warning('请输入文章标题')
    return false
  }
  if (!form.content.trim()) {
    ElMessage.warning('请输入文章内容')
    return false
  }
  return true
}

// 保存草稿
const saveDraft = () => {
  if (!validateForm()) return
  emit('save', {
    ...form,
    status: 'draft'
  })
}

// 发布文章
const publishArticle = () => {
  if (!validateForm()) return
  emit('save', {
    ...form,
    status: 'published'
  })
}
</script>

<style scoped>
.article-form {
  padding: 20px;
}

.editor-wrapper {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  min-height: 400px;
}

.settings-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 封面上传 */
.cover-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
  width: 100%;
  height: 160px;
}

.cover-uploader:hover {
  border-color: #409EFF;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #8c939d;
  gap: 8px;
}

.cover-placeholder .el-icon {
  font-size: 28px;
}

/* 上传区域 */
.upload-area {
  width: 100%;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

/* 底部操作栏 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

/* 作者显示（非管理员） */
.author-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  color: #606266;
}

/* 作者选择器（管理员） */
.author-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.author-selector .author-name {
  flex: 1;
  color: #606266;
}

.mb-3 {
  margin-bottom: 12px;
}

.user-option {
  display: flex;
  align-items: center;
  gap: 10px;
}

</style>
