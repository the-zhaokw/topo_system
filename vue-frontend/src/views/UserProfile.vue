<template>
  <div class="user-profile">
    <div class="profile-header">
      <h2>个人配置</h2>
      <el-button type="primary" @click="saveProfile">保存</el-button>
    </div>
    
    <el-card shadow="never" class="profile-card">
      <div class="profile-content">
        <!-- 基本信息区域 -->
        <div class="basic-info">
          <h3>用户基本信息</h3>
          
          <!-- 头像上传 -->
          <div class="avatar-section">
            <div class="avatar-upload">
              <div class="avatar-wrapper">
                <el-avatar :size="100" :src="avatarUrl" />
                <span class="profile-status-indicator" :class="userStatusStore.status" :title="userStatusStore.statusText"></span>
              </div>
              <div class="avatar-actions">
                <el-button type="primary" size="small" @click="triggerFileSelect">修改</el-button>
                <el-button type="danger" size="small" @click="handleAvatarRemove" :disabled="!profileForm.avatar">移除</el-button>
                <input
                  ref="fileInput"
                  type="file"
                  accept="image/*"
                  style="display: none"
                  @change="handleAvatarChange"
                />
              </div>
            </div>
          </div>

          <!-- 状态设置 -->
          <div class="status-section">
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
          
          <!-- 基本信息表单 -->
          <el-form 
            ref="profileFormRef" 
            :model="profileForm" 
            :rules="profileRules" 
            label-width="120px"
            class="profile-form"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="编号" prop="employee_id">
                  <el-input v-model="profileForm.employee_id" placeholder="请输入工号" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="profileForm.username" disabled />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="姓" prop="last_name">
                  <el-input v-model="profileForm.last_name" placeholder="请输入姓" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="名" prop="first_name">
                  <el-input v-model="profileForm.first_name" placeholder="请输入名" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="职位" prop="position">
                  <el-input v-model="profileForm.position" placeholder="请输入职位" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="公司电话" prop="company_phone">
                  <el-input v-model="profileForm.company_phone" placeholder="请输入公司电话" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="手机号码" prop="mobile_phone">
                  <el-input v-model="profileForm.mobile_phone" placeholder="请输入手机号码" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="生日" prop="birthday">
                  <el-date-picker
                    v-model="profileForm.birthday"
                    type="date"
                    placeholder="选择生日"
                    format="YYYY/MM/DD"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="性别" prop="gender">
                  <el-select v-model="profileForm.gender" placeholder="请选择性别" style="width: 100%">
                    <el-option label="男" value="男" />
                    <el-option label="女" value="女" />
                    <el-option label="其他" value="其他" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="工作语言" prop="work_language">
                  <el-select v-model="profileForm.work_language" placeholder="请选择工作语言" style="width: 100%">
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
        
        <!-- 密码重置区域 -->
        <div class="password-section">
          <h3>重设密码</h3>
          <el-form 
            ref="passwordFormRef" 
            :model="passwordForm" 
            :rules="passwordRules" 
            label-width="120px"
            class="password-form"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="当前密码" prop="currentPassword">
                  <el-input 
                    v-model="passwordForm.currentPassword" 
                    type="password" 
                    placeholder="请输入当前密码"
                    show-password
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="新密码" prop="newPassword">
                  <el-input 
                    v-model="passwordForm.newPassword" 
                    type="password" 
                    placeholder="请输入新密码"
                    show-password
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="确认密码" prop="confirmPassword">
                  <el-input 
                    v-model="passwordForm.confirmPassword" 
                    type="password" 
                    placeholder="请确认新密码"
                    show-password
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item>
              <el-button type="warning" @click="resetPassword">重设密码</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useUserStatusStore } from '@/stores/userStatus'
import { apiService } from '@/services/api'

const userStore = useUserStore()
const userStatusStore = useUserStatusStore()
const profileFormRef = ref(null)
const passwordFormRef = ref(null)
const fileInput = ref(null)

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
.user-profile {
  padding: 0;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.profile-header h2 {
  margin: 0;
  color: #303133;
}

.profile-card {
  min-height: 600px;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.basic-info h3,
.password-section h3 {
  margin-bottom: 24px;
  color: #303133;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 12px;
}

.avatar-section {
  margin-bottom: 24px;
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
}

.profile-status-indicator {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 3px solid #fff;
  background-color: #67c23a;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
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
  gap: 8px;
}

/* 状态区域样式 */
.status-section {
  margin-bottom: 24px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.status-section h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.status-display {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding: 8px 12px;
  background-color: #fff;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.status-text {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.status-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.status-option {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  font-size: 13px;
  color: #606266;
}

.status-option:hover {
  border-color: #409eff;
  color: #409eff;
}

.status-option.active {
  background-color: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
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

.profile-form,
.password-form {
  max-width: 800px;
}

.password-section {
  border-top: 1px solid #e4e7ed;
  padding-top: 24px;
}

@media screen and (max-width: 768px) {
  .user-profile {
    padding: 12px;
  }

  .profile-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  .profile-header h2 {
    font-size: 18px;
  }

  .profile-form,
  .password-form {
    max-width: 100%;
  }

  .password-section h3 {
    font-size: 16px;
  }

  .avatar-section {
    margin-bottom: 16px;
  }

  .avatar-upload {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .avatar-actions {
    width: 100%;
  }

  :deep(.el-form-item__label) {
    width: 100% !important;
    text-align: left !important;
    margin-bottom: 4px !important;
  }

  :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }
}

@media screen and (max-width: 480px) {
  .user-profile {
    padding: 8px;
  }

  .profile-header h2 {
    font-size: 16px;
  }
}
</style>