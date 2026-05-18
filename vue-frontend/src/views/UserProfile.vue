<template>
  <div class="user-profile-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><User /></el-icon>
          </div>
          <div class="title-text">
            <h1>个人配置</h1>
            <p class="subtitle">管理您的个人信息和账户设置</p>
          </div>
        </div>
        <el-button type="primary" @click="saveProfile" class="btn-gradient btn-save">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-projects">
            <div class="stat-icon-wrapper stat-icon-wrapper-projects">
              <el-icon><FolderOpened /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.projects }}</div>
              <div class="stat-label">参与项目</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-bugs">
            <div class="stat-icon-wrapper stat-icon-wrapper-bugs">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.submittedBugs }}</div>
              <div class="stat-label">提交Bug</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-resolved">
            <div class="stat-icon-wrapper stat-icon-wrapper-resolved">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.resolvedBugs }}</div>
              <div class="stat-label">解决Bug</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-activities">
            <div class="stat-icon-wrapper stat-icon-wrapper-activities">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.activities }}</div>
              <div class="stat-label">活动次数</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 个人信息卡片 -->
    <div class="profile-section animate-fade-in-up delay-200">
      <el-card class="glass-card profile-card" shadow="hover">
        <div class="profile-content">
          <!-- 头像和基本信息区域 -->
          <div class="profile-top-section">
            <!-- 头像上传 -->
            <div class="avatar-section">
              <div class="avatar-wrapper-glow">
                <div class="avatar-border">
                  <el-avatar :size="120" :src="avatarUrl" class="profile-avatar" />
                </div>
                <span class="profile-status-indicator" :class="userStatusStore.status" :title="userStatusStore.statusText"></span>
              </div>
              <div class="avatar-actions">
                <el-button type="primary" size="small" @click="triggerFileSelect" class="btn-gradient-sm">
                  <el-icon><Edit /></el-icon>
                  修改头像
                </el-button>
                <el-button type="danger" size="small" @click="handleAvatarRemove" :disabled="!profileForm.avatar" class="btn-danger-sm">
                  <el-icon><Delete /></el-icon>
                  移除
                </el-button>
                <input
                  ref="fileInput"
                  type="file"
                  accept="image/*"
                  style="display: none"
                  @change="handleAvatarChange"
                />
              </div>
            </div>

            <!-- 状态设置 -->
            <div class="status-section glass-status">
              <h4>当前状态</h4>
              <div class="status-display">
                <span class="status-dot" :class="userStatusStore.status"></span>
                <span class="status-text">{{ userStatusStore.statusText }}</span>
              </div>
              <div class="status-options">
                <div
                  v-for="status in userStatusStore.statusOptions"
                  :key="status.value"
                  class="status-option"
                  :class="{ active: userStatusStore.status === status.value }"
                  @click="userStatusStore.setStatus(status.value)"
                >
                  <span class="status-dot" :class="status.value"></span>
                  <span>{{ status.label }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 基本信息表单 -->
          <div class="basic-info-section">
            <h3 class="section-title">
              <el-icon><UserFilled /></el-icon>
              用户基本信息
            </h3>

            <el-form
              ref="profileFormRef"
              :model="profileForm"
              :rules="profileRules"
              label-width="120px"
              class="profile-form"
            >
              <el-row :gutter="24">
                <el-col :xs="24" :sm="12">
                  <el-form-item label="编号" prop="employee_id">
                    <el-input v-model="profileForm.employee_id" placeholder="请输入工号" class="gradient-input" />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12">
                  <el-form-item label="用户名" prop="username">
                    <el-input v-model="profileForm.username" disabled class="disabled-input" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :xs="24" :sm="12">
                  <el-form-item label="姓" prop="last_name">
                    <el-input v-model="profileForm.last_name" placeholder="请输入姓" class="gradient-input" />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12">
                  <el-form-item label="名" prop="first_name">
                    <el-input v-model="profileForm.first_name" placeholder="请输入名" class="gradient-input" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :xs="24" :sm="12">
                  <el-form-item label="邮箱" prop="email">
                    <el-input v-model="profileForm.email" placeholder="请输入邮箱" class="gradient-input" />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12">
                  <el-form-item label="职位" prop="position">
                    <el-input v-model="profileForm.position" placeholder="请输入职位" class="gradient-input" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :xs="24" :sm="12">
                  <el-form-item label="公司电话" prop="company_phone">
                    <el-input v-model="profileForm.company_phone" placeholder="请输入公司电话" class="gradient-input" />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12">
                  <el-form-item label="手机号码" prop="mobile_phone">
                    <el-input v-model="profileForm.mobile_phone" placeholder="请输入手机号码" class="gradient-input" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :xs="24" :sm="12">
                  <el-form-item label="生日" prop="birthday">
                    <el-date-picker
                      v-model="profileForm.birthday"
                      type="date"
                      placeholder="选择生日"
                      format="YYYY/MM/DD"
                      value-format="YYYY-MM-DD"
                      style="width: 100%"
                      class="gradient-date-picker"
                    />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12">
                  <el-form-item label="性别" prop="gender">
                    <el-select v-model="profileForm.gender" placeholder="请选择性别" style="width: 100%" class="gradient-select">
                      <el-option label="男" value="男" />
                      <el-option label="女" value="女" />
                      <el-option label="其他" value="其他" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :xs="24" :sm="12">
                  <el-form-item label="工作语言" prop="work_language">
                    <el-select v-model="profileForm.work_language" placeholder="请选择工作语言" style="width: 100%" class="gradient-select">
                      <el-option label="中文" value="中文" />
                      <el-option label="英文" value="英文" />
                      <el-option label="日文" value="日文" />
                      <el-option label="其他" value="其他" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 密码重置区域 -->
    <div class="password-section animate-fade-in-up delay-300">
      <el-card class="glass-card password-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <h3 class="section-title">
              <el-icon><Lock /></el-icon>
              重设密码
            </h3>
          </div>
        </template>

        <el-form
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="passwordRules"
          label-width="120px"
          class="password-form"
        >
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12">
              <el-form-item label="当前密码" prop="currentPassword">
                <el-input
                  v-model="passwordForm.currentPassword"
                  type="password"
                  placeholder="请输入当前密码"
                  show-password
                  class="gradient-input"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :xs="24" :sm="12">
              <el-form-item label="新密码" prop="newPassword">
                <el-input
                  v-model="passwordForm.newPassword"
                  type="password"
                  placeholder="请输入新密码"
                  show-password
                  class="gradient-input"
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item label="确认密码" prop="confirmPassword">
                <el-input
                  v-model="passwordForm.confirmPassword"
                  type="password"
                  placeholder="请确认新密码"
                  show-password
                  class="gradient-input"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item>
            <el-button type="warning" @click="resetPassword" class="btn-warning-gradient">
              <el-icon><Key /></el-icon>
              重设密码
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useUserStatusStore } from '@/stores/userStatus'
import { apiService } from '@/services/api'
import { User, Check, Edit, Delete, UserFilled, Lock, Key, FolderOpened, Warning, CircleCheck, TrendCharts } from '@element-plus/icons-vue'

const userStore = useUserStore()
const userStatusStore = useUserStatusStore()
const profileFormRef = ref(null)
const passwordFormRef = ref(null)
const fileInput = ref(null)

// 统计数据
const stats = reactive({
  projects: 12,
  submittedBugs: 48,
  resolvedBugs: 35,
  activities: 156
})

// 个人信息表单
const profileForm = reactive({
  username: '',
  email: '',
  employee_id: '',
  first_name: '',
  last_name: '',
  position: '',
  department: '',
  company_phone: '',
  mobile_phone: '',
  birthday: '',
  gender: '',
  work_language: '',
  avatar: ''
})

// 计算完整的头像URL
const avatarUrl = computed(() => {
  if (!profileForm.avatar) {
    return '/avatar-placeholder.png'
  }
  // 如果头像URL已经是完整URL，直接返回
  if (profileForm.avatar.startsWith('http')) {
    return profileForm.avatar
  }
  // 拼接完整的API基础URL
  const baseURL = import.meta.env.PROD ? 'http://localhost:5000' : ''
  return `${baseURL}${profileForm.avatar}`
})

// 密码重置表单
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 表单验证规则
const profileRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  employee_id: [
    { required: true, message: '请输入工号', trigger: 'blur' }
  ]
}

const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 加载用户信息
const loadUserProfile = async () => {
  try {
    console.log('开始加载用户信息...')
    const response = await apiService.auth.getCurrentUser()
    console.log('获取用户信息响应:', response)

    // 确保response是对象格式
    let userData
    if (typeof response === 'object' && response !== null) {
      // 如果response直接是user对象，而不是{user: {...}}格式，直接使用
      if (response.id && response.username) {
        userData = response
      }
      // 如果response是{user: {...}}格式，使用response.user
      else if (response.user) {
        userData = response.user
      }
      // 否则，抛出错误
      else {
        throw new Error('Invalid response format')
      }
    } else {
      throw new Error('Invalid response format')
    }

    console.log('提取到的用户数据:', userData)

    // 填充表单数据
    Object.keys(profileForm).forEach(key => {
      if (userData[key] !== undefined) {
        profileForm[key] = userData[key]
      }
    })

    console.log('表单数据填充完成')
  } catch (error) {
    console.error('加载用户信息失败:', error)
    ElMessage.error(`加载用户信息失败: ${error.message || '未知错误'}`)
  }
}

// 保存个人信息
const saveProfile = async () => {
  try {
    console.log('开始保存个人信息...')

    if (!profileFormRef.value) {
      throw new Error('表单引用未找到')
    }

    // 验证表单
    await profileFormRef.value.validate()
    console.log('表单验证通过')

    // 准备更新数据
    const updateData = {
      email: profileForm.email,
      employee_id: profileForm.employee_id,
      first_name: profileForm.first_name,
      last_name: profileForm.last_name,
      position: profileForm.position,
      department: profileForm.department,
      company_phone: profileForm.company_phone,
      mobile_phone: profileForm.mobile_phone,
      birthday: profileForm.birthday,
      gender: profileForm.gender,
      work_language: profileForm.work_language,
      avatar: profileForm.avatar
    }

    console.log('准备发送的更新数据:', updateData)

    const response = await apiService.auth.updateProfile(updateData)
    console.log('更新个人信息响应:', response)

    // 确保response是对象格式
    let userData
    if (typeof response === 'object' && response !== null) {
      // 如果response直接是user对象，而不是{user: {...}}格式，直接使用
      if (response.id && response.username) {
        userData = response
      }
      // 如果response是{user: {...}}格式，使用response.user
      else if (response.user) {
        userData = response.user
      }
      // 否则，抛出错误
      else {
        throw new Error('Invalid response format')
      }
    } else {
      throw new Error('Invalid response format')
    }

    console.log('更新后的用户数据:', userData)

    // 更新store中的用户信息
    userStore.setUser(userData)

    // 保存成功后重新加载用户信息
    await loadUserProfile()

    ElMessage.success('个人信息保存成功')
    console.log('个人信息保存成功')
  } catch (error) {
    console.error('保存个人信息失败:', error)
    ElMessage.error(`保存个人信息失败: ${error.message || '未知错误'}`)
  }
}

// 重置密码
const resetPassword = async () => {
  if (!passwordFormRef.value) return

  try {
    await passwordFormRef.value.validate()

    await ElMessageBox.confirm(
      '确定要重置密码吗？',
      '确认重置密码',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await apiService.auth.changePassword({
      current_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword
    })

    // 清空密码表单
    Object.keys(passwordForm).forEach(key => {
      passwordForm[key] = ''
    })

    ElMessage.success('密码重置成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重置密码失败:', error)
      ElMessage.error('重置密码失败')
    }
  }
}

// 触发文件选择
const triggerFileSelect = () => {
  fileInput.value?.click()
}

// 头像上传处理
const handleAvatarChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 检查文件类型
  const validTypes = ['image/jpeg', 'image/png', 'image/gif']
  if (!validTypes.includes(file.type)) {
    ElMessage.error('只支持JPG、PNG、GIF格式的图片')
    return
  }

  // 检查文件大小
  const maxSize = 2 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过2MB')
    return
  }

  try {
    // 创建FormData对象
    const formData = new FormData()
    formData.append('avatar', file)

    // 调用上传API
    const response = await apiService.auth.uploadAvatar(formData)

    // 更新头像URL
        if (response?.avatar_url) {
          profileForm.avatar = response.avatar_url
        } else if (response?.user?.avatar) {
          profileForm.avatar = response.user.avatar
        }

        // 更新用户store中的信息
    await userStore.fetchCurrentUser()

    ElMessage.success('头像上传成功')
  } catch (error) {
    console.error('头像上传失败:', error)
    ElMessage.error('头像上传失败，请重试')
  } finally {
    // 清空文件输入，以便能再次选择同一文件
    event.target.value = ''
  }
}

// 头像删除处理
    const handleAvatarRemove = async () => {
      if (!profileForm.avatar) return

      try {
        await ElMessageBox.confirm(
          '确定要删除头像吗？',
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        // 调用删除API
        const response = await apiService.auth.removeAvatar()

        // 更新头像URL
        profileForm.avatar = null

        // 更新用户store中的信息
        await userStore.fetchCurrentUser()

        ElMessage.success('头像删除成功')
      } catch (error) {
        if (error !== 'cancel') {
          console.error('头像删除失败:', error)
          ElMessage.error('头像删除失败，请重试')
        }
      }
    }

onMounted(() => {
  loadUserProfile()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.user-profile-container {
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

/* 按钮样式 */
.btn-gradient {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
  padding: 12px 24px;
  font-weight: 600;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%);
}

.btn-save {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-gradient-sm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-gradient-sm:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px -5px rgba(102, 126, 234, 0.5);
}

.btn-danger-sm {
  transition: all 0.3s;
}

.btn-danger-sm:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px -5px rgba(245, 108, 108, 0.4);
}

.btn-warning-gradient {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  border: none;
  color: white;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-warning-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(245, 158, 11, 0.5);
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

/* 统计卡片不同配色 */
.stat-card-projects::before { background: linear-gradient(90deg, #667eea, #764ba2); }
.stat-card-bugs::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-resolved::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-activities::before { background: linear-gradient(90deg, #ec4899, #f472b6); }

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

.stat-icon-wrapper-projects {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #667eea;
  box-shadow: 0 4px 15px -3px rgba(102, 126, 234, 0.4);
}

.stat-icon-wrapper-bugs {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-resolved {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-activities {
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

.stat-card-projects .stat-value {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-bugs .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-resolved .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-activities .stat-value {
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

/* 个人信息区域 */
.profile-section {
  margin-bottom: 24px;
}

.profile-card {
  padding: 32px;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.profile-top-section {
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
  align-items: flex-start;
}

/* 头像区域 - 渐变边框和发光效果 */
.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.avatar-wrapper-glow {
  position: relative;
  display: inline-block;
  padding: 6px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  border-radius: 50%;
  box-shadow: 0 0 30px rgba(102, 126, 234, 0.4), 0 0 60px rgba(118, 75, 162, 0.2);
  animation: glow-pulse 3s ease-in-out infinite;
}

.avatar-border {
  background: white;
  border-radius: 50%;
  padding: 4px;
}

.profile-avatar {
  border-radius: 50%;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

@keyframes glow-pulse {
  0%, 100% {
    box-shadow: 0 0 30px rgba(102, 126, 234, 0.4), 0 0 60px rgba(118, 75, 162, 0.2);
  }
  50% {
    box-shadow: 0 0 40px rgba(102, 126, 234, 0.6), 0 0 80px rgba(118, 75, 162, 0.3);
  }
}

.profile-status-indicator {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 3px solid white;
  background-color: #67c23a;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 10;
}

.profile-status-indicator.online {
  background-color: #67c23a;
}

.profile-status-indicator.busy {
  background-color: #f56c6c;
}

.profile-status-indicator.away {
  background-color: #e6a23c;
}

.profile-status-indicator.offline {
  background-color: #909399;
}

.avatar-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

/* 状态区域 - 玻璃拟态 */
.status-section {
  flex: 1;
  min-width: 280px;
  padding: 24px;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 16px;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.glass-status {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.status-section h4 {
  margin: 0 0 16px 0;
  color: #1e293b;
  font-size: 16px;
  font-weight: 600;
}

.status-display {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.status-text {
  font-size: 14px;
  color: #334155;
  font-weight: 600;
}

.status-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.status-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.3s;
  background-color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(203, 213, 225, 0.5);
  font-size: 13px;
  color: #475569;
  font-weight: 500;
}

.status-option:hover {
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.status-option.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

/* 状态点样式 */
.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #67c23a;
}

.status-dot.online {
  background-color: #67c23a;
}

.status-dot.busy {
  background-color: #f56c6c;
}

.status-dot.away {
  background-color: #e6a23c;
}

.status-dot.offline {
  background-color: #909399;
}

/* 基本信息区域 */
.basic-info-section {
  padding-top: 8px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 24px 0;
  color: #1e293b;
  font-size: 18px;
  font-weight: 700;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(226, 232, 240, 0.6);
}

.section-title .el-icon {
  color: #667eea;
  font-size: 22px;
}

/* 表单样式 */
.profile-form,
.password-form {
  max-width: 100%;
}

/* 输入框渐变边框效果 */
.gradient-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px rgba(203, 213, 225, 0.5) inset;
  transition: all 0.3s;
}

.gradient-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(102, 126, 234, 0.5) inset;
}

.gradient-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3) inset, 0 0 0 1px #667eea inset;
}

.disabled-input :deep(.el-input__wrapper) {
  background: rgba(241, 245, 249, 0.8);
}

.gradient-select :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px rgba(203, 213, 225, 0.5) inset;
  transition: all 0.3s;
}

.gradient-select :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(102, 126, 234, 0.5) inset;
}

.gradient-select :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3) inset, 0 0 0 1px #667eea inset;
}

.gradient-date-picker :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px rgba(203, 213, 225, 0.5) inset;
  transition: all 0.3s;
}

.gradient-date-picker :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(102, 126, 234, 0.5) inset;
}

.gradient-date-picker :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3) inset, 0 0 0 1px #667eea inset;
}

/* 密码区域 */
.password-section {
  margin-bottom: 20px;
}

.password-card :deep(.el-card__header) {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.card-header {
  display: flex;
  align-items: center;
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
  .user-profile-container {
    padding: 0;
  }

  .page-header {
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 16px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
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

  .btn-save {
    width: 100%;
    justify-content: center;
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

  .profile-card {
    padding: 20px;
  }

  .profile-top-section {
    flex-direction: column;
    align-items: center;
    gap: 24px;
  }

  .avatar-section {
    width: 100%;
  }

  .avatar-actions {
    flex-direction: row;
    justify-content: center;
  }

  .status-section {
    width: 100%;
    min-width: auto;
  }

  .section-title {
    font-size: 16px;
  }

  .profile-form :deep(.el-form-item__label) {
    width: 100% !important;
    text-align: left !important;
    margin-bottom: 6px !important;
  }

  .profile-form :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }

  .password-form :deep(.el-form-item__label) {
    width: 100% !important;
    text-align: left !important;
    margin-bottom: 6px !important;
  }

  .password-form :deep(.el-form-item__content) {
    margin-left: 0 !important;
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

  .profile-card {
    padding: 16px;
  }

  .avatar-wrapper-glow {
    padding: 4px;
  }

  .profile-avatar {
    width: 100px !important;
    height: 100px !important;
  }

  .section-title {
    font-size: 15px;
  }
}
</style>
