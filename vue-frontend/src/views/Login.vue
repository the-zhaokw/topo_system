<template>
  <div class="login-container">
    <div class="bg-gradient"></div>
    <div class="bg-orb bg-orb-1"></div>
    <div class="bg-orb bg-orb-2"></div>
    <div class="bg-orb bg-orb-3"></div>
    <div class="bg-grid"></div>
    
    <div class="particles">
      <span v-for="i in 20" :key="i" class="particle" :style="getParticleStyle(i)"></span>
    </div>
    
    <div class="login-card glass-card">
      <div class="card-accent"></div>
      
      <div class="login-header">
        <div class="logo-wrapper">
          <div class="logo-glow"></div>
          <svg class="logo-icon" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#6366f1"/>
                <stop offset="100%" style="stop-color:#a855f7"/>
              </linearGradient>
            </defs>
            <path d="M32 4L4 20v24l28 16 28-16V20L32 4z" fill="url(#logoGrad)"/>
            <path d="M32 12L12 24v16l20 12 20-12V24L32 12z" fill="rgba(255,255,255,0.2)"/>
            <circle cx="32" cy="28" r="6" fill="white"/>
            <path d="M32 34v14" stroke="white" stroke-width="3" stroke-linecap="round"/>
          </svg>
        </div>
        <h2 class="title">TOPO系统</h2>
        <p class="subtitle">请登录您的账户</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form-content"
      >
        <el-form-item prop="username">
          <div class="input-wrapper">
            <el-input
              v-model="loginForm.username"
              placeholder="用户名"
              size="large"
            >
              <template #prefix>
                <svg class="custom-input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
              </template>
            </el-input>
          </div>
        </el-form-item>
        
        <el-form-item prop="password">
          <div class="input-wrapper">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="密码"
              size="large"
              show-password
            >
              <template #prefix>
                <svg class="custom-input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </template>
            </el-input>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            <span class="btn-text">登录</span>
            <div class="btn-shimmer"></div>
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <p>还没有账户？ <el-link type="primary" class="register-link" @click="showRegister = true">立即注册</el-link></p>
      </div>
    </div>
    
    <el-dialog
      v-model="showRegister"
      title="用户注册"
      width="450px"
      class="register-dialog"
      :show-close="true"
      :close-on-click-modal="false"
      append-to-body
    >
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-position="top"
        class="register-form"
      >
        <div class="form-grid">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="registerForm.username" placeholder="请输入用户名" />
          </el-form-item>
          
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="registerForm.email" placeholder="请输入邮箱地址" />
          </el-form-item>
        </div>
        
        <div class="form-grid">
          <el-form-item label="密码" prop="password">
            <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" show-password />
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input v-model="registerForm.confirmPassword" type="password" placeholder="再次输入密码" show-password />
          </el-form-item>
        </div>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="registerForm.role" placeholder="请选择您的角色" class="full-width">
            <el-option label="软件工程师" value="software_engineer" />
            <el-option label="测试工程师" value="test_engineer" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button class="dialog-btn" @click="showRegister = false">取消</el-button>
          <el-button type="primary" class="dialog-btn dialog-btn-primary" :loading="registerLoading" @click="handleRegister">
            注册
          </el-button>
        </div>
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
  if (!loginFormRef.value) return
  
  try {
    const valid = await loginFormRef.value.validate()
    if (!valid) return
    
    loading.value = true
    const result = await userStore.login(loginForm)
    
    if (result.success) {
      ElMessage.success('登录成功')
      router.push('/dashboard')
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}

onMounted(() => {})

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

const getParticleStyle = (index) => {
  const delay = (index * 0.2) % 10
  const duration = 8 + (index % 5) * 2
  const size = 2 + (index % 3) * 2
  const left = (index * 5) % 100
  const top = (index * 7) % 100
  return {
    '--delay': `${delay}s`,
    '--duration': `${duration}s`,
    '--size': `${size}px`,
    '--left': `${left}%`,
    '--top': `${top}%`,
    '--opacity': 0.3 + (index % 4) * 0.15
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  overflow: hidden;
  background: #0f172a;
  font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(ellipse 120% 80% at 20% 80%, rgba(99, 102, 241, 0.4) 0%, transparent 60%),
    radial-gradient(ellipse 100% 100% at 80% 20%, rgba(168, 85, 247, 0.4) 0%, transparent 60%),
    radial-gradient(ellipse 80% 60% at 50% 50%, rgba(59, 130, 246, 0.3) 0%, transparent 50%);
  animation: gradientShift 15s ease-in-out infinite;
}

@keyframes gradientShift {
  0%, 100% {
    background: 
      radial-gradient(ellipse 120% 80% at 20% 80%, rgba(99, 102, 241, 0.4) 0%, transparent 60%),
      radial-gradient(ellipse 100% 100% at 80% 20%, rgba(168, 85, 247, 0.4) 0%, transparent 60%),
      radial-gradient(ellipse 80% 60% at 50% 50%, rgba(59, 130, 246, 0.3) 0%, transparent 50%);
  }
  50% {
    background: 
      radial-gradient(ellipse 100% 80% at 70% 30%, rgba(99, 102, 241, 0.4) 0%, transparent 60%),
      radial-gradient(ellipse 120% 100% at 30% 70%, rgba(168, 85, 247, 0.4) 0%, transparent 60%),
      radial-gradient(ellipse 90% 60% at 60% 40%, rgba(59, 130, 246, 0.3) 0%, transparent 50%);
  }
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  mix-blend-mode: screen;
}

.bg-orb-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.8) 0%, rgba(99, 102, 241, 0) 70%);
  left: -10%;
  top: -10%;
  animation: floatSlow 12s ease-in-out infinite;
}

.bg-orb-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(168, 85, 247, 0.8) 0%, rgba(168, 85, 247, 0) 70%);
  right: -5%;
  bottom: -5%;
  animation: floatSlow 15s ease-in-out infinite reverse;
}

.bg-orb-3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.7) 0%, rgba(59, 130, 246, 0) 70%);
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  animation: float 10s ease-in-out infinite;
}

@keyframes floatSlow {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30px, -30px) scale(1.1); }
  50% { transform: translate(-20px, 20px) scale(0.9); }
  75% { transform: translate(15px, 15px) scale(1.05); }
}

@keyframes float {
  0%, 100% { transform: translate(-50%, -50%) scale(1); }
  50% { transform: translate(-50%, calc(-50% - 40px)) scale(1.15); }
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  -webkit-mask-image: radial-gradient(ellipse at center, black 30%, transparent 70%);
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 70%);
}

.particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.particle {
  position: absolute;
  width: var(--size);
  height: var(--size);
  background: rgba(255, 255, 255, var(--opacity));
  border-radius: 50%;
  left: var(--left);
  top: var(--top);
  animation: particleFloat var(--duration) ease-in-out infinite;
  animation-delay: var(--delay);
  box-shadow: 0 0 calc(var(--size) * 2) rgba(255, 255, 255, calc(var(--opacity) * 0.5));
}

@keyframes particleFloat {
  0%, 100% { 
    transform: translateY(0) translateX(0) scale(1); 
    opacity: 0;
  }
  10% { opacity: var(--opacity); }
  50% { 
    transform: translateY(-100px) translateX(20px) scale(1.2); 
    opacity: var(--opacity);
  }
  90% { opacity: var(--opacity); }
  100% { 
    transform: translateY(-200px) translateX(-10px) scale(0.8); 
    opacity: 0;
  }
}

.glass-card {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 24px;
  padding: 48px 40px;
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset,
    0 1px 1px rgba(255, 255, 255, 0.1) inset;
  animation: fadeInUp 0.8s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.card-accent {
  position: absolute;
  top: 0;
  left: 20%;
  right: 20%;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
  border-radius: 1px;
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.logo-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.logo-glow {
  position: absolute;
  inset: -20px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.4) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulseGlow 3s ease-in-out infinite;
  filter: blur(10px);
}

@keyframes pulseGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

.logo-icon {
  width: 64px;
  height: 64px;
  position: relative;
  z-index: 1;
  animation: float 4s ease-in-out infinite;
  filter: drop-shadow(0 4px 12px rgba(99, 102, 241, 0.5));
}

.title {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.subtitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  font-weight: 300;
  letter-spacing: 0.5px;
}

.login-form-content {
  margin-bottom: 24px;
}

.input-wrapper {
  position: relative;
}

.input-wrapper :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  border-radius: 14px !important;
  box-shadow: none !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  padding: 8px 16px !important;
}

.input-wrapper :deep(.el-input__wrapper:hover) {
  background: rgba(255, 255, 255, 0.12) !important;
  border-color: rgba(255, 255, 255, 0.25) !important;
}

.input-wrapper :deep(.el-input__wrapper.is-focus) {
  background: rgba(255, 255, 255, 0.15) !important;
  border-color: rgba(99, 102, 241, 0.6) !important;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
}

.input-wrapper :deep(.el-input__inner) {
  color: #ffffff !important;
  font-size: 15px !important;
  font-weight: 400;
}

.input-wrapper :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.4) !important;
}

.custom-input-icon {
  width: 18px;
  height: 18px;
  color: rgba(255, 255, 255, 0.5);
  transition: color 0.3s;
}

.input-wrapper :deep(.el-input__wrapper.is-focus) .custom-input-icon {
  color: rgba(255, 255, 255, 0.9);
}

.input-wrapper :deep(.el-form-item__error) {
  color: #fb7185 !important;
}

.login-btn {
  width: 100%;
  height: 48px;
  border: none !important;
  border-radius: 14px !important;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%) !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  letter-spacing: 0.5px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4) !important;
}

.login-btn:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 30px rgba(99, 102, 241, 0.6) !important;
}

.login-btn:active {
  transform: translateY(0) scale(0.98) !important;
}

.btn-shimmer {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s;
}

.login-btn:hover .btn-shimmer {
  left: 100%;
}

.login-footer {
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

.login-footer p {
  margin: 0;
}

.login-footer :deep(.el-link) {
  color: #a5b4fc !important;
  font-weight: 600;
  transition: all 0.3s;
}

.login-footer :deep(.el-link:hover) {
  color: #818cf8 !important;
  text-decoration: underline;
}

@media screen and (max-width: 768px) {
  .login-container {
    padding: 12px;
    align-items: flex-start;
    padding-top: 80px;
  }

  .glass-card {
    padding: 36px 24px !important;
    border-radius: 20px !important;
  }

  .logo-icon {
    width: 52px;
    height: 52px;
  }

  .title {
    font-size: 24px !important;
  }

  .subtitle {
    font-size: 13px !important;
  }

  .login-form-content {
    margin-bottom: 20px;
  }

  .login-btn {
    height: 44px !important;
    font-size: 15px !important;
  }

  .bg-orb-1 {
    width: 300px;
    height: 300px;
  }

  .bg-orb-2 {
    width: 250px;
    height: 250px;
  }

  .bg-orb-3 {
    width: 200px;
    height: 200px;
  }
}

@media screen and (max-width: 480px) {
  .glass-card {
    padding: 28px 20px !important;
    border-radius: 16px !important;
  }

  .title {
    font-size: 20px !important;
  }

  .login-btn {
    height: 42px !important;
    font-size: 14px !important;
  }
}
</style>

<style>
/* Register Dialog Styles - Global scope for append-to-body */
body .register-dialog {
  background: rgba(15, 23, 42, 0.95) !important;
  backdrop-filter: blur(30px) !important;
  -webkit-backdrop-filter: blur(30px) !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  border-radius: 24px !important;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5) !important;
}

body .register-dialog .el-dialog__header {
  padding: 24px 28px 16px !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
  margin: 0 !important;
}

body .register-dialog .el-dialog__title {
  color: #ffffff !important;
  font-weight: 600;
  font-size: 20px !important;
}

body .register-dialog .el-dialog__close {
  color: rgba(255, 255, 255, 0.6) !important;
}

body .register-dialog .el-dialog__close:hover {
  color: rgba(255, 255, 255, 0.9) !important;
}

body .register-dialog .el-dialog__body {
  padding: 24px 28px !important;
}

body .register-dialog .el-dialog__footer {
  padding: 16px 28px 24px !important;
  border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
}

body .register-dialog .el-form-item__label {
  color: rgba(255, 255, 255, 0.8) !important;
  font-weight: 500;
  font-size: 13px;
  margin-bottom: 6px !important;
}

body .register-dialog .el-form-item__error {
  color: #fb7185 !important;
}

body .register-dialog .el-input__wrapper {
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  transition: all 0.3s !important;
}

body .register-dialog .el-input__wrapper:hover {
  background: rgba(255, 255, 255, 0.12) !important;
  border-color: rgba(255, 255, 255, 0.25) !important;
}

body .register-dialog .el-input__wrapper.is-focus {
  background: rgba(255, 255, 255, 0.15) !important;
  border-color: rgba(99, 102, 241, 0.6) !important;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
}

body .register-dialog .el-input__inner {
  color: #ffffff !important;
}

body .register-dialog .el-input__inner::placeholder {
  color: rgba(255, 255, 255, 0.4) !important;
}

body .register-dialog .el-select {
  width: 100%;
}

body .register-dialog .el-select .el-input__wrapper {
  background: rgba(255, 255, 255, 0.08) !important;
}

body .register-dialog .dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

body .register-dialog .dialog-btn {
  min-width: 80px;
  height: 38px;
  border-radius: 10px !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  background: rgba(255, 255, 255, 0.08) !important;
  color: rgba(255, 255, 255, 0.8) !important;
  transition: all 0.3s !important;
}

body .register-dialog .dialog-btn:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  border-color: rgba(255, 255, 255, 0.25) !important;
  transform: translateY(-1px) !important;
}

body .register-dialog .dialog-btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%) !important;
  border: none !important;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
  color: #ffffff !important;
}

body .register-dialog .dialog-btn-primary:hover {
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
}

body .register-dialog .form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

body .register-dialog .full-width {
  width: 100%;
}

/* Dropdown styles */
body .el-select-dropdown {
  background: rgba(15, 23, 42, 0.98) !important;
  backdrop-filter: blur(20px) !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  border-radius: 12px !important;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4) !important;
}

body .el-select-dropdown__item {
  color: rgba(255, 255, 255, 0.8) !important;
}

body .el-select-dropdown__item.hover,
body .el-select-dropdown__item.selected {
  background: rgba(99, 102, 241, 0.2) !important;
  color: #a5b4fc !important;
}

/* Overlay */
body .el-overlay {
  background: rgba(15, 23, 42, 0.5) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
}

@media screen and (max-width: 768px) {
  body .register-dialog {
    width: 95% !important;
    margin: 10px auto !important;
  }

  body .register-dialog .form-grid {
    grid-template-columns: 1fr;
    gap: 0;
  }
}
</style>
