<template>
  <div class="user-detail">
    <div class="user-detail-header">
      <h2>{{ pageTitle }}</h2>
      <div class="header-actions">
        <el-button type="primary" @click="$router.push('/users')">
          返回用户列表
        </el-button>
        <el-button v-if="canEdit" type="success" @click="showEditDialog = true">
          编辑用户信息
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="isAdminView ? 8 : 12">
        <el-card shadow="never" class="user-card">
          <template #header>
            <div class="card-header">
              <span>用户信息</span>
              <el-tag v-if="isSelf" type="success" size="small">本人</el-tag>
            </div>
          </template>
          
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="6" animated />
          </div>
          
          <div v-else-if="userData" class="user-info">
            <div class="avatar-section">
              <el-avatar :size="80" :src="userData.avatar || avatarPlaceholder">
                {{ userData.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <div class="user-name">
                <h3>{{ userData.last_name || '' }}{{ userData.first_name || userData.username }}</h3>
                <el-tag v-if="userData.position" type="info" size="small">
                  {{ userData.position }}
                </el-tag>
              </div>
            </div>
            
            <el-divider />
            
            <div class="info-row">
              <div class="info-label">用户名</div>
              <div class="info-value">{{ userData.username }}</div>
            </div>
            
            <div class="info-row">
              <div class="info-label">邮箱</div>
              <div class="info-value">{{ userData.email }}</div>
            </div>
            
            <div class="info-row">
              <div class="info-label">职位</div>
              <div class="info-value">{{ userData.position || '-' }}</div>
            </div>
            
            <div class="info-row">
              <div class="info-label">部门</div>
              <div class="info-value">{{ userData.department || '-' }}</div>
            </div>
            
            <div class="info-row">
              <div class="info-label">公司电话</div>
              <div class="info-value">{{ userData.company_phone || '-' }}</div>
            </div>
            
            <div class="info-row">
              <div class="info-label">手机号码</div>
              <div class="info-value">{{ userData.phone || '-' }}</div>
            </div>
            
            <div v-if="isAdminView" class="info-row">
              <div class="info-label">生日</div>
              <div class="info-value">{{ userData.birthday ? new Date(userData.birthday).toLocaleDateString('zh-CN') : '-' }}</div>
            </div>
            
            <div v-if="isAdminView" class="info-row">
              <div class="info-label">性别</div>
              <div class="info-value">{{ userData.gender || '-' }}</div>
            </div>
            
            <div v-if="isAdminView" class="info-row">
              <div class="info-label">工号</div>
              <div class="info-value">{{ userData.employee_id || '-' }}</div>
            </div>
            
            <div v-if="isAdminView" class="info-row">
              <div class="info-label">状态</div>
              <div class="info-value">
                <el-tag :type="userData.is_active ? 'success' : 'danger'" size="small">
                  {{ userData.is_active ? '激活' : '禁用' }}
                </el-tag>
              </div>
            </div>
            
            <div v-if="isAdminView" class="info-row">
              <div class="info-label">创建时间</div>
              <div class="info-value">{{ formatDate(userData.created_at) }}</div>
            </div>
            
            <div v-if="isAdminView" class="info-row">
              <div class="info-label">最后登录</div>
              <div class="info-value">{{ formatDate(userData.last_login) }}</div>
            </div>
          </div>
          
          <div v-else class="no-data">
            <el-empty description="未找到用户信息" />
          </div>
        </el-card>
        
        <el-card v-if="statistics && Object.keys(statistics).length > 0" shadow="never" class="stats-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>统计信息</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-value clickable-link" @click="goToBugList">{{ statistics.total_bugs || 0 }}</div>
                <div class="stat-label">负责Bug</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-value clickable-link" @click="goToProjectList">{{ statistics.total_projects || 0 }}</div>
                <div class="stat-label">参与项目</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-value clickable-link" @click="goToTaskList">{{ statistics.total_tasks || 0 }}</div>
                <div class="stat-label">负责任务</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
      
      <el-col :span="isAdminView ? 16 : 12">
        <el-card shadow="never" class="activity-card">
          <template #header>
            <div class="card-header">
              <span>活动记录</span>
              <el-badge :value="activityCount" :max="99" type="primary" />
            </div>
          </template>
          
          <div v-if="loadingActivities" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>
          
          <div v-else-if="activities.length > 0" class="activity-list">
            <el-timeline>
              <el-timeline-item
                v-for="activity in activities"
                :key="activity.id"
                :timestamp="formatDate(activity.created_at)"
                placement="top"
                :type="getActivityType(activity.action)"
              >
                <div class="activity-item">
                  <div class="activity-action">
                    <el-tag :type="getActivityType(activity.action)" size="small">
                      {{ getActionText(activity.action) }}
                    </el-tag>
                  </div>
                  <div class="activity-description">{{ activity.description }}</div>
                  <div class="activity-resource">
                    <span class="clickable-link" @click="goToResource(activity)">
                      {{ activity.resource_name || activity.target_type + ' #' + activity.target_id }}
                    </span>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
            
            <div v-if="activities.length >= 10" class="load-more">
              <el-button link type="primary" @click="viewAllActivities">
                查看全部活动记录
              </el-button>
            </div>
          </div>
          
          <el-empty v-else description="暂无活动记录" />
        </el-card>
      </el-col>
    </el-row>

    <el-dialog 
      v-model="showEditDialog" 
      title="编辑用户" 
      width="500px"
    >
      <el-form 
        ref="userFormRef" 
        :model="userForm" 
        :rules="userRules" 
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="姓" prop="last_name">
          <el-input v-model="userForm.last_name" placeholder="请输入姓" />
        </el-form-item>
        
        <el-form-item label="名" prop="first_name">
          <el-input v-model="userForm.first_name" placeholder="请输入名" />
        </el-form-item>
        
        <el-form-item label="职位" prop="position">
          <el-input v-model="userForm.position" placeholder="请输入职位" />
        </el-form-item>
        
        <el-form-item label="部门" prop="department">
          <el-input v-model="userForm.department" placeholder="请输入部门" />
        </el-form-item>
        
        <el-form-item label="工作语言" prop="work_language">
          <el-input v-model="userForm.work_language" placeholder="请输入工作语言" />
        </el-form-item>
        
        <el-form-item label="工号" prop="employee_id">
          <el-input v-model="userForm.employee_id" placeholder="请输入工号" />
        </el-form-item>

        <el-form-item label="公司电话" prop="company_phone">
          <el-input v-model="userForm.company_phone" placeholder="请输入公司电话" />
        </el-form-item>
        
        <el-form-item label="手机号码" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号码" />
        </el-form-item>
        
        <el-form-item v-if="canEdit" label="生日" prop="birthday">
          <el-date-picker 
            v-model="userForm.birthday" 
            type="date" 
            placeholder="请选择生日" 
            style="width: 100%" 
            format="YYYY/MM/DD" 
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item v-if="canEdit" label="性别" prop="gender">
          <el-select v-model="userForm.gender" placeholder="请选择性别">
            <el-option label="男" value="男" />
            <el-option label="女" value="女" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="canEdit" label="职位" prop="position">
          <el-select v-model="userForm.position" placeholder="请选择职位">
            <el-option v-for="pos in positions" :key="pos" :label="pos" :value="pos" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="canEdit" label="状态" prop="is_active">
          <el-switch 
            v-model="userForm.is_active" 
            active-text="激活" 
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
    
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="submitUserForm">
            更新
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { apiService as api } from '@/services/api'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const loadingActivities = ref(false)
const userData = ref(null)
const activities = ref([])
const activityCount = ref(0)
const statistics = ref(null)
const isAdminView = ref(false)
const isSelf = ref(false)
const showEditDialog = ref(false)
const userFormRef = ref(null)
const positions = ref([])

const avatarPlaceholder = '/avatar-placeholder.png'

const pageTitle = computed(() => {
  if (isSelf.value) {
    return '我的主页'
  }
  return '用户主页'
})

const canEdit = computed(() => {
  const user = userStore.currentUser
  if (!user) return false
  if (isSelf.value) return true
  if (user.is_super_admin) return true
  if (user.is_admin) return true
  return user.position === '系统管理员' ||
         user.position === '管理员' ||
         user.position === '经理' ||
         user.position === '项目经理' ||
         user.position === '部门经理' ||
         user.position === '人事专员' ||
         user.position?.includes('经理')
})

const userForm = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  position: '',
  department: '',
  work_language: '',
  company_phone: '',
  phone: '',
  birthday: '',
  gender: '',
  is_active: true,
  employee_id: ''
})

const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

const fetchUserHome = async (userId) => {
  loading.value = true
  try {
    const response = await api.users.getUserHome(userId)
    userData.value = response.user
    isAdminView.value = response.is_admin_view
    isSelf.value = response.is_self
    
    if (response.activities) {
      activities.value = response.activities
      activityCount.value = response.activity_count || 0
    }
    
    if (response.statistics) {
      statistics.value = response.statistics
    }
    
    if (canEdit.value) {
      initUserForm()
    }
  } catch (error) {
    console.error('获取用户主页信息失败:', error)
    if (error.response?.status === 403) {
      ElMessage.error('权限不足，无法查看用户主页')
    } else if (error.response?.status === 404) {
      ElMessage.error('用户不存在')
    } else {
      ElMessage.error('获取用户主页信息失败')
    }
  } finally {
    loading.value = false
  }
}

const initUserForm = () => {
  if (!userData.value) return
  userForm.username = userData.value.username || ''
  userForm.email = userData.value.email || ''
  userForm.first_name = userData.value.first_name || ''
  userForm.last_name = userData.value.last_name || ''
  userForm.position = userData.value.position || ''
  userForm.department = userData.value.department || ''
  userForm.work_language = userData.value.work_language || ''
  userForm.company_phone = userData.value.company_phone || ''
  userForm.phone = userData.value.phone || ''
  userForm.birthday = userData.value.birthday || ''
  userForm.gender = userData.value.gender || ''
  userForm.is_active = userData.value.is_active
  userForm.employee_id = userData.value.employee_id || ''
}

const updateUser = async (id, data) => {
  if (!canEdit.value) {
    ElMessage.error('权限不足，无法更新用户')
    return
  }
  
  try {
    await api.users.update(id, data)
    ElMessage.success('用户更新成功')
    showEditDialog.value = false
    fetchUserHome(id)
  } catch (error) {
    console.error('更新用户失败:', error)
    const errorMessage = error.response?.data?.error || error.response?.data?.message || '更新用户失败'
    if (error.response?.status === 403) {
      ElMessage.error('权限不足，无法更新用户')
    } else if (error.response?.status === 400) {
      ElMessage.error(errorMessage)
    } else {
      ElMessage.error('更新用户失败')
    }
  }
}

const submitUserForm = async () => {
  if (!userFormRef.value) return
  
  try {
    await userFormRef.value.validate()
    const formData = { ...userForm }
    await updateUser(userData.value.id, formData)
  } catch (error) {
    
  }
}

const getRoleType = (role) => {
  return 'info'
}

const getRoleText = (role) => {
  if (!role) return ''
  return role
}

const getActivityType = (action) => {
  const typeMap = {
    'create': 'success',
    'update': 'primary',
    'delete': 'danger',
    'login': 'info',
    'logout': 'warning',
    'assign': 'warning',
    'close': 'danger',
    'reopen': 'warning'
  }
  return typeMap[action] || 'info'
}

const getActionText = (action) => {
  const textMap = {
    'create': '创建',
    'update': '更新',
    'delete': '删除',
    'login': '登录',
    'logout': '登出',
    'assign': '分配',
    'close': '关闭',
    'reopen': '重新打开'
  }
  return textMap[action] || action
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const viewAllActivities = () => {
  router.push({
    path: '/activities',
    query: { user_id: route.params.id }
  })
}

const goToResource = (activity) => {
  if (!activity.target_type || !activity.target_id) return
  
  switch (activity.target_type) {
    case 'bug':
      router.push(`/bugs/${activity.target_id}`)
      break
    case 'project':
      router.push(`/projects/${activity.target_id}`)
      break
    case 'task':
      router.push(`/tasks/${activity.target_id}`)
      break
    default:
      break
  }
}

const goToBugList = () => {
  router.push({
    path: '/bugs',
    query: { user_id: route.params.id }
  })
}

const goToProjectList = () => {
  router.push({
    path: '/projects/list',
    query: { user_id: route.params.id }
  })
}

const goToTaskList = () => {
  router.push({
    path: '/tasks',
    query: { assignee: route.params.id }
  })
}

watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchUserHome(Number(newId))
  }
})

onMounted(async () => {
  const userId = Number(route.params.id)
  if (userId) {
    await fetchUserHome(userId)
  }
  try {
    const positionRes = await api.users.getPositions()
    positions.value = positionRes.positions || []
  } catch (e) {
    console.error('获取职位列表失败:', e)
  }
})
</script>

<style scoped>
.user-detail {
  padding: 0;
}

.user-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.user-detail-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-card {
  margin-bottom: 20px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.avatar-section .user-name {
  margin-top: 16px;
  text-align: center;
}

.avatar-section .user-name h3 {
  margin: 0 0 8px 0;
  color: #303133;
}

.loading-container {
  padding: 20px 0;
}

.user-info {
  padding: 10px 0;
}

.info-row {
  display: flex;
  margin-bottom: 16px;
  align-items: center;
}

.info-label {
  width: 100px;
  font-weight: bold;
  color: #606266;
  flex-shrink: 0;
}

.info-value {
  flex: 1;
  color: #303133;
  word-break: break-all;
}

.no-data {
  padding: 40px 0;
}

.activity-card {
  margin-bottom: 20px;
}

.activity-list {
  max-height: 500px;
  overflow-y: auto;
}

.activity-item {
  padding: 8px 0;
}

.activity-action {
  margin-bottom: 4px;
}

.activity-description {
  color: #303133;
  font-size: 14px;
}

.activity-resource {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

.load-more {
  text-align: center;
  padding: 16px 0;
}

.stats-card .stat-item {
  text-align: center;
  padding: 16px 0;
}

.stats-card .stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
}

.stats-card .stat-label {
  font-size: 14px;
  color: #606266;
  margin-top: 8px;
}

.clickable-link {
  color: #409eff;
  cursor: pointer;
  text-decoration: none;
}

.clickable-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .user-detail {
    padding: 12px;
  }

  .user-detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  .user-detail-header h2 {
    font-size: 18px;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 80px;
    font-size: 12px;
    padding: 8px 12px;
  }

  .user-info-card {
    margin-bottom: 16px;
  }

  .user-info-card :deep(.el-card__body) {
    padding: 16px;
  }

  .user-avatar-section {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 12px;
  }

  .user-avatar {
    width: 80px;
    height: 80px;
  }

  .user-name {
    font-size: 18px;
  }

  .user-title {
    font-size: 14px;
  }

  .stats-row .el-col {
    width: 50%;
    max-width: 50%;
    flex: 0 0 50%;
    margin-bottom: 8px;
    padding: 0 6px;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-label {
    font-size: 12px;
  }

  .info-section {
    margin-bottom: 16px;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .info-item {
    padding: 10px;
  }

  .info-label {
    font-size: 12px;
  }

  .info-value {
    font-size: 14px;
  }

  .activity-card,
  .todos-card {
    margin-bottom: 16px;
  }

  .activity-timeline {
    padding: 12px;
  }

  .timeline-item {
    padding: 12px;
  }

  .activity-content {
    font-size: 13px;
  }

  .activity-time {
    font-size: 11px;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
    max-height: 90vh !important;
  }

  .el-dialog__header,
  .el-dialog__body,
  .el-dialog__footer {
    padding: 12px !important;
  }

  .el-dialog__title {
    font-size: 16px !important;
  }
}

@media screen and (max-width: 480px) {
  .user-detail {
    padding: 8px;
  }

  .user-detail-header h2 {
    font-size: 16px;
  }

  .user-avatar {
    width: 60px;
    height: 60px;
  }

  .user-name {
    font-size: 16px;
  }

  .stats-row .el-col {
    width: 100%;
    max-width: 100%;
    flex: 0 0 100%;
  }

  .stat-value {
    font-size: 18px;
  }

  .activity-content {
    font-size: 12px;
  }
}
</style>
