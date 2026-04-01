<template>
  <div class="login-container">
    <div class="login-form">
      <div class="login-header">
        <h2>TOPO系统</h2>
        <p>请登录您的账户</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form-content"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <p>还没有账户？ <el-link type="primary" @click="showRegister = true">立即注册</el-link></p>
      </div>
    </div>
    
    <!-- 注册对话框 -->
    <el-dialog
      v-model="showRegister"
      title="用户注册"
      width="400px"
    >
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="registerForm.role" placeholder="请选择角色">
            <el-option label="软件工程师" value="software_engineer" />
            <el-option label="测试工程师" value="test_engineer" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showRegister = false">取消</el-button>
        <el-button type="primary" :loading="registerLoading" @click="handleRegister">
          注册
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref()
const registerFormRef = ref()
const loading = ref(false)
const registerLoading = ref(false)
const showRegister = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  role: 'software_engineer'
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const handleLogin = async () => {
  console.log('handleLogin called, loginForm:', loginForm)
  if (!loginFormRef.value) return
  
  try {
    const valid = await loginFormRef.value.validate()
    if (!valid) return
    
    loading.value = true
    console.log('calling userStore.login...')
    const result = await userStore.login(loginForm)
    console.log('userStore.login result:', result)
    
    if (result.success) {
      ElMessage.success('登录成功')
      router.push('/dashboard')
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('handleLogin error:', error)
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}

// 在组件挂载时，我们不立即重定向，让用户可以看到登录界面
// 只有当用户明确点击登录按钮或有token+user信息时才跳转
onMounted(() => {
  // 这里不做任何自动跳转，让用户手动操作
})

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    const valid = await registerFormRef.value.validate()
    if (!valid) return
    
    registerLoading.value = true
    const result = await userStore.register(registerForm)
    
    if (result.success) {
      ElMessage.success('注册成功')
      showRegister.value = false
      registerFormRef.value.resetFields()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('注册失败')
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.login-form {
  background: #fff;
  border-radius: 8px;
  padding: 40px;
  width: 400px;
  max-width: 100%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo-icon {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 16px;
}

.login-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.login-header p {
  margin: 0;
  color: #909399;
}

.login-form-content {
  margin-bottom: 20px;
}

.login-btn {
  width: 100%;
}

.login-footer {
  text-align: center;
  color: #909399;
}

.login-footer p {
  margin: 0;
}

@media screen and (max-width: 768px) {
  .login-container {
    padding: 12px;
    align-items: flex-start;
    padding-top: 60px;
  }

  .login-form {
    width: 100% !important;
    max-width: 100% !important;
    padding: 24px 16px !important;
    border-radius: 12px !important;
  }

  .login-header {
    margin-bottom: 20px;
  }

  .login-header h2 {
    font-size: 20px !important;
  }

  .login-header p {
    font-size: 13px !important;
  }

  .login-form-content {
    margin-bottom: 16px;
  }

  :deep(.el-input__inner) {
    font-size: 16px !important;
    height: 44px !important;
    line-height: 44px !important;
  }

  :deep(.el-input__prefix) {
    font-size: 18px !important;
  }

  :deep(.el-button--large) {
    height: 44px !important;
    font-size: 16px !important;
  }

  .login-btn {
    height: 44px !important;
    font-size: 16px !important;
  }

  .login-footer {
    font-size: 13px;
  }

  :deep(.el-dialog) {
    width: 95% !important;
    margin: 10px auto !important;
  }

  :deep(.el-dialog__body) {
    padding: 16px !important;
  }
}

@media screen and (max-width: 480px) {
  .login-container {
    padding: 8px;
    padding-top: 40px;
  }

  .login-form {
    padding: 20px 12px !important;
    border-radius: 8px !important;
  }

  .login-header h2 {
    font-size: 18px !important;
  }

  .login-header p {
    font-size: 12px !important;
  }

  .login-form-content {
    margin-bottom: 12px;
  }

  :deep(.el-form-item) {
    margin-bottom: 16px !important;
  }

  :deep(.el-input__inner) {
    font-size: 15px !important;
    height: 40px !important;
    line-height: 40px !important;
  }

  :deep(.el-button--large) {
    height: 40px !important;
    font-size: 15px !important;
  }

  .login-btn {
    height: 40px !important;
    font-size: 15px !important;
  }
}
</style>