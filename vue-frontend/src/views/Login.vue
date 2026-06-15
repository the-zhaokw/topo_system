<template>
  <div class="login-container">
    <!-- 赛博朋克网格背景 -->
    <div class="cyber-grid"></div>
    
    <!-- 动态几何图形 -->
    <div class="geometric-shapes">
      <div class="hexagon hexagon-1"></div>
      <div class="hexagon hexagon-2"></div>
      <div class="hexagon hexagon-3"></div>
      <div class="triangle triangle-1"></div>
      <div class="triangle triangle-2"></div>
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
    </div>
    
    <!-- 霓虹光球 -->
    <div class="neon-orb neon-orb-1"></div>
    <div class="neon-orb neon-orb-2"></div>
    <div class="neon-orb neon-orb-3"></div>
    
    <!-- 扫描线效果 -->
    <div class="scanlines"></div>
    
    <!-- 代码雨背景 -->
    <canvas ref="matrixCanvas" class="matrix-rain"></canvas>
    
    <!-- 登录卡片 - 3D悬浮效果 -->
    <div class="login-card" ref="loginCard">
      <div class="card-glow"></div>
      <div class="card-border"></div>
      
      <!-- 装饰性角落 -->
      <div class="corner corner-tl"></div>
      <div class="corner corner-tr"></div>
      <div class="corner corner-bl"></div>
      <div class="corner corner-br"></div>
      
      <div class="login-header">
        <div class="logo-container">
          <div class="logo-ring"></div>
          <div class="logo-core">
            <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="neonGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#7dd3fc"/>
                  <stop offset="50%" style="stop-color:#38bdf8"/>
                  <stop offset="100%" style="stop-color:#0ea5e9"/>
                </linearGradient>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              <path d="M32 4L4 20v24l28 16 28-16V20L32 4z" stroke="url(#neonGrad)" stroke-width="2" fill="none" filter="url(#glow)"/>
              <path d="M32 12L12 24v16l20 12 20-12V24L32 12z" fill="url(#neonGrad)" opacity="0.3"/>
              <circle cx="32" cy="28" r="6" fill="url(#neonGrad)" filter="url(#glow)"/>
              <path d="M32 34v14" stroke="url(#neonGrad)" stroke-width="3" stroke-linecap="round" filter="url(#glow)"/>
            </svg>
          </div>
          <div class="logo-particles">
            <span v-for="i in 8" :key="i" class="logo-particle"></span>
          </div>
        </div>
        
        <h2 class="title glitch" data-text="TOPO系统">TOPO系统</h2>
        <div class="subtitle-wrapper">
          <span class="subtitle-text">请登录您的账户</span>
          <span class="cursor">|</span>
        </div>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
      >
        <el-form-item prop="username" class="form-item-animated">
          <div class="input-container">
            <div class="input-line"></div>
            <el-input
              v-model="loginForm.username"
              placeholder="用户名"
              size="large"
              class="cyber-input"
            >
              <template #prefix>
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
              </template>
            </el-input>
            <div class="input-glow"></div>
          </div>
        </el-form-item>
        
        <el-form-item prop="password" class="form-item-animated">
          <div class="input-container">
            <div class="input-line"></div>
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="密码"
              size="large"
              show-password
              class="cyber-input"
            >
              <template #prefix>
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </template>
            </el-input>
            <div class="input-glow"></div>
          </div>
        </el-form-item>
        
        <el-form-item class="btn-container">
          <button
            type="button"
            class="cyber-btn"
            :class="{ 'loading': loading }"
            :disabled="loading"
            @click="handleLogin"
          >
            <span class="btn-text">{{ loading ? '登录中...' : '登录' }}</span>
            <span class="btn-glitch"></span>
            <span class="btn-caret">▶</span>
            <div class="btn-particles">
              <span v-for="i in 6" :key="i"></span>
            </div>
          </button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <div class="divider">
          <span class="divider-line"></span>
          <span class="divider-text">OR</span>
          <span class="divider-line"></span>
        </div>
        <p class="footer-text">
          还没有账户？ 
          <span class="link" @click="showRegister = true">立即注册</span>
        </p>
      </div>
    </div>
    
    <!-- 装饰性底部线条 -->
    <div class="bottom-bar">
      <span class="version">v2.0.0</span>
      <span class="status">
        <span class="status-dot"></span>
        System Online
      </span>
    </div>
    
    <!-- 注册对话框 -->
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
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref()
const registerFormRef = ref()
const loginCard = ref()
const matrixCanvas = ref()
const loading = ref(false)
const registerLoading = ref(false)
const showRegister = ref(false)

let matrixAnimationId = null

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

const initMatrixEffect = () => {
  if (!matrixCanvas.value) return
  
  const canvas = matrixCanvas.value
  const ctx = canvas.getContext('2d')
  
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  
  const chars = 'TOPO01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン'
  const charArray = chars.split('')
  const fontSize = 14
  const columns = canvas.width / fontSize
  const drops = []
  
  for (let i = 0; i < columns; i++) {
    drops[i] = Math.random() * canvas.height
  }
  
  const draw = () => {
    ctx.fillStyle = 'rgba(13, 17, 23, 0.05)'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    ctx.fillStyle = '#38bdf8'
    ctx.font = fontSize + 'px monospace'
    
    for (let i = 0; i < drops.length; i++) {
      const text = charArray[Math.floor(Math.random() * charArray.length)]
      ctx.fillText(text, i * fontSize, drops[i] * fontSize)
      
      if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
        drops[i] = 0
      }
      
      drops[i]++
    }
    
    matrixAnimationId = requestAnimationFrame(draw)
  }
  
  draw()
}

const handleMouseMove = (e) => {
  if (!loginCard.value) return
  
  const rect = loginCard.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  
  const centerX = rect.width / 2
  const centerY = rect.height / 2
  
  const rotateX = (y - centerY) / 30
  const rotateY = (centerX - x) / 30
  
  loginCard.value.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`
}

const handleMouseLeave = () => {
  if (!loginCard.value) return
  loginCard.value.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateZ(0)'
}

onMounted(() => {
  initMatrixEffect()
  
  if (loginCard.value) {
    loginCard.value.addEventListener('mousemove', handleMouseMove)
    loginCard.value.addEventListener('mouseleave', handleMouseLeave)
  }
})

onUnmounted(() => {
  if (matrixAnimationId) {
    cancelAnimationFrame(matrixAnimationId)
  }
  
  if (loginCard.value) {
    loginCard.value.removeEventListener('mousemove', handleMouseMove)
    loginCard.value.removeEventListener('mouseleave', handleMouseLeave)
  }
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.login-container {
  min-height: 100vh;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  overflow: hidden;
  background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0f0f1a 100%);
  font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* 赛博朋克网格背景 */
.cyber-grid {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(56, 189, 248, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(56, 189, 248, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  animation: gridMove 20s linear infinite;
}

@keyframes gridMove {
  0% { transform: perspective(500px) rotateX(60deg) translateY(0); }
  100% { transform: perspective(500px) rotateX(60deg) translateY(60px); }
}

/* 动态几何图形 */
.geometric-shapes {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.hexagon {
  position: absolute;
  width: 100px;
  height: 115px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.1), rgba(14, 165, 233, 0.1));
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
  animation: rotateHex 20s linear infinite;
}

.hexagon-1 { left: 10%; top: 20%; animation-delay: 0s; }
.hexagon-2 { right: 15%; bottom: 30%; animation-delay: -5s; transform: scale(1.5); }
.hexagon-3 { left: 70%; top: 60%; animation-delay: -10s; transform: scale(0.8); }

.triangle {
  position: absolute;
  width: 0;
  height: 0;
  border-left: 40px solid transparent;
  border-right: 40px solid transparent;
  border-bottom: 70px solid rgba(125, 211, 252, 0.08);
  animation: floatTriangle 15s ease-in-out infinite;
}

.triangle-1 { left: 20%; bottom: 20%; animation-delay: -3s; }
.triangle-2 { right: 25%; top: 15%; animation-delay: -8s; transform: rotate(180deg); }

.circle {
  position: absolute;
  border-radius: 50%;
  border: 2px solid rgba(56, 189, 248, 0.2);
  animation: pulseCircle 8s ease-in-out infinite;
}

.circle-1 { width: 200px; height: 200px; left: -50px; top: -50px; }
.circle-2 { width: 150px; height: 150px; right: -30px; bottom: -30px; animation-delay: -4s; }

@keyframes rotateHex {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes floatTriangle {
  0%, 100% { transform: translateY(0) rotate(180deg); }
  50% { transform: translateY(-30px) rotate(180deg); }
}

@keyframes pulseCircle {
  0%, 100% { transform: scale(1); opacity: 0.3; }
  50% { transform: scale(1.1); opacity: 0.6; }
}

/* 霓虹光球 */
.neon-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.4;
  mix-blend-mode: screen;
  pointer-events: none;
  animation: orbFloat 12s ease-in-out infinite;
}

.neon-orb-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.8) 0%, transparent 70%);
  left: -20%;
  top: -20%;
  animation-duration: 15s;
}

.neon-orb-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(14, 165, 233, 0.6) 0%, transparent 70%);
  right: -15%;
  bottom: -15%;
  animation-duration: 18s;
  animation-delay: -5s;
}

.neon-orb-3 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(125, 211, 252, 0.5) 0%, transparent 70%);
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  animation-duration: 20s;
  animation-delay: -10s;
}

@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(50px, -50px) scale(1.1); }
  50% { transform: translate(-30px, 30px) scale(0.9); }
  75% { transform: translate(-50px, -30px) scale(1.05); }
}

/* 扫描线效果 */
.scanlines {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, 0.1) 2px,
    rgba(0, 0, 0, 0.1) 4px
  );
  pointer-events: none;
  animation: scanlineMove 10s linear infinite;
  opacity: 0.3;
}

@keyframes scanlineMove {
  0% { transform: translateY(0); }
  100% { transform: translateY(4px); }
}

/* 代码雨 */
.matrix-rain {
  position: absolute;
  inset: 0;
  opacity: 0.15;
  pointer-events: none;
}

/* 登录卡片 */
.login-card {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 480px;
  background: rgba(10, 10, 15, 0.8);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 4px;
  padding: 48px 40px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  animation: cardEntrance 1s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes cardEntrance {
  0% {
    opacity: 0;
    transform: translateY(100px) scale(0.9);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.card-glow {
  position: absolute;
  inset: -2px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.5), rgba(14, 165, 233, 0.5));
  border-radius: 6px;
  z-index: -1;
  filter: blur(20px);
  opacity: 0.5;
  animation: glowPulse 3s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

.card-border {
  position: absolute;
  inset: 0;
  border-radius: 4px;
  padding: 2px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.8), rgba(14, 165, 233, 0.8), rgba(125, 211, 252, 0.8));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  animation: borderRotate 4s linear infinite;
}

@keyframes borderRotate {
  0% { filter: hue-rotate(0deg); }
  100% { filter: hue-rotate(360deg); }
}

/* 装饰性角落 */
.corner {
  position: absolute;
  width: 20px;
  height: 20px;
  border-color: rgba(56, 189, 248, 0.8);
  border-style: solid;
}

.corner-tl { top: 8px; left: 8px; border-width: 2px 0 0 2px; }
.corner-tr { top: 8px; right: 8px; border-width: 2px 2px 0 0; }
.corner-bl { bottom: 8px; left: 8px; border-width: 0 0 2px 2px; }
.corner-br { bottom: 8px; right: 8px; border-width: 0 2px 2px 0; }

/* 登录头部 */
.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-container {
  position: relative;
  display: inline-block;
  margin-bottom: 24px;
}

.logo-ring {
  position: absolute;
  inset: -15px;
  border: 2px solid rgba(56, 189, 248, 0.3);
  border-radius: 50%;
  animation: ringPulse 2s ease-in-out infinite;
}

@keyframes ringPulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 0; }
}

.logo-core {
  width: 80px;
  height: 80px;
  position: relative;
  z-index: 1;
  animation: logoFloat 4s ease-in-out infinite;
  filter: drop-shadow(0 0 20px rgba(56, 189, 248, 0.5));
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.logo-particles {
  position: absolute;
  inset: 0;
}

.logo-particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: rgba(56, 189, 248, 0.8);
  border-radius: 50%;
  animation: particleOrbit 3s linear infinite;
}

.logo-particle:nth-child(1) { animation-delay: 0s; }
.logo-particle:nth-child(2) { animation-delay: -0.375s; }
.logo-particle:nth-child(3) { animation-delay: -0.75s; }
.logo-particle:nth-child(4) { animation-delay: -1.125s; }
.logo-particle:nth-child(5) { animation-delay: -1.5s; }
.logo-particle:nth-child(6) { animation-delay: -1.875s; }
.logo-particle:nth-child(7) { animation-delay: -2.25s; }
.logo-particle:nth-child(8) { animation-delay: -2.625s; }

@keyframes particleOrbit {
  0% { transform: rotate(0deg) translateX(45px) scale(1); opacity: 0.8; }
  50% { transform: rotate(180deg) translateX(45px) scale(0.5); opacity: 0.4; }
  100% { transform: rotate(360deg) translateX(45px) scale(1); opacity: 0.8; }
}

/* 标题 - 故障效果 */
.title {
  margin: 0 0 12px 0;
  font-size: 36px;
  font-weight: 900;
  color: #ffffff;
  letter-spacing: 4px;
  text-transform: uppercase;
  position: relative;
  animation: glitchText 5s infinite;
}

.title::before,
.title::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.title::before {
  left: 2px;
  text-shadow: -2px 0 #0ea5e9;
  clip: rect(24px, 550px, 90px, 0);
  animation: glitchAnim1 3s infinite linear alternate-reverse;
}

.title::after {
  left: -2px;
  text-shadow: -2px 0 #00ffff;
  clip: rect(85px, 550px, 140px, 0);
  animation: glitchAnim2 2s infinite linear alternate-reverse;
}

@keyframes glitchText {
  0%, 90%, 100% { opacity: 1; }
  91% { opacity: 0.8; transform: skewX(0deg); }
  92% { opacity: 0.9; transform: skewX(-1deg); }
  93% { opacity: 1; transform: skewX(0deg); }
}

@keyframes glitchAnim1 {
  0% { clip: rect(31px, 9999px, 94px, 0); }
  20% { clip: rect(62px, 9999px, 42px, 0); }
  40% { clip: rect(16px, 9999px, 78px, 0); }
  60% { clip: rect(89px, 9999px, 13px, 0); }
  80% { clip: rect(45px, 9999px, 56px, 0); }
  100% { clip: rect(23px, 9999px, 82px, 0); }
}

@keyframes glitchAnim2 {
  0% { clip: rect(65px, 9999px, 19px, 0); }
  20% { clip: rect(34px, 9999px, 67px, 0); }
  40% { clip: rect(91px, 9999px, 28px, 0); }
  60% { clip: rect(48px, 9999px, 73px, 0); }
  80% { clip: rect(12px, 9999px, 91px, 0); }
  100% { clip: rect(56px, 9999px, 34px, 0); }
}

/* 副标题 - 打字机效果 */
.subtitle-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.subtitle-text {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  letter-spacing: 1px;
}

.cursor {
  color: #38bdf8;
  font-weight: bold;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* 表单样式 */
.login-form {
  margin-bottom: 24px;
}

.form-item-animated {
  margin-bottom: 28px;
  animation: formItemSlide 0.6s ease-out backwards;
}

.form-item-animated:nth-child(1) { animation-delay: 0.3s; }
.form-item-animated:nth-child(2) { animation-delay: 0.4s; }
.form-item-animated:nth-child(3) { animation-delay: 0.5s; }

@keyframes formItemSlide {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.input-container {
  position: relative;
}

.input-line {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #38bdf8, #0ea5e9, #7dd3fc);
  transition: width 0.4s ease;
  z-index: 1;
}

.input-container:hover .input-line,
.input-container:focus-within .input-line {
  width: 100%;
}

.input-glow {
  position: absolute;
  inset: 0;
  background: rgba(56, 189, 248, 0.1);
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.input-container:focus-within .input-glow {
  opacity: 1;
  animation: inputGlowPulse 2s ease-in-out infinite;
}

@keyframes inputGlowPulse {
  0%, 100% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.3); }
  50% { box-shadow: 0 0 20px rgba(56, 189, 248, 0.5); }
}

/* 输入框样式 */
.cyber-input {
  position: relative;
}

.cyber-input :deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.4) !important;
  border: 1px solid rgba(56, 189, 248, 0.2) !important;
  border-radius: 4px !important;
  box-shadow: none !important;
  padding: 12px 16px !important;
  transition: all 0.3s ease !important;
}

.cyber-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(56, 189, 248, 0.4) !important;
}

.cyber-input :deep(.el-input__wrapper.is-focus) {
  background: rgba(56, 189, 248, 0.05) !important;
  border-color: #38bdf8 !important;
  box-shadow: 0 0 15px rgba(56, 189, 248, 0.3) !important;
}

.cyber-input :deep(.el-input__inner) {
  color: #ffffff !important;
  font-size: 15px !important;
  font-family: 'Outfit', sans-serif !important;
}

.cyber-input :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.3) !important;
}

.input-icon {
  width: 20px;
  height: 20px;
  color: rgba(56, 189, 248, 0.6);
  transition: all 0.3s ease;
}

.cyber-input :deep(.el-input__wrapper.is-focus) .input-icon {
  color: #38bdf8;
  filter: drop-shadow(0 0 5px rgba(56, 189, 248, 0.5));
}

.cyber-input :deep(.el-form-item__error) {
  color: #ff4757 !important;
  font-size: 12px;
  padding-top: 4px;
}

/* 按钮容器 */
.btn-container {
  margin-top: 32px;
  margin-bottom: 0;
}

.btn-container :deep(.el-form-item__content) {
  justify-content: center;
}

/* 赛博朋克按钮 */
.cyber-btn {
  position: relative;
  width: 100%;
  height: 54px;
  border: none;
  border-radius: 4px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(14, 165, 233, 0.2));
  color: #ffffff;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 3px;
  text-transform: uppercase;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  animation: btnSlide 0.6s ease-out 0.6s backwards;
}

@keyframes btnSlide {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.cyber-btn::before {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  right: 2px;
  bottom: 2px;
  background: linear-gradient(135deg, #38bdf8, #0ea5e9);
  border-radius: 2px;
  z-index: -1;
  opacity: 0.8;
}

.cyber-btn::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.3), rgba(14, 165, 233, 0.3));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.cyber-btn:hover::after {
  opacity: 1;
}

.cyber-btn:hover {
  transform: translateY(-3px);
  box-shadow: 
    0 10px 30px rgba(56, 189, 248, 0.3),
    0 0 60px rgba(14, 165, 233, 0.2);
  letter-spacing: 4px;
}

.cyber-btn:active {
  transform: translateY(-1px);
}

.cyber-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-text {
  position: relative;
  z-index: 1;
}

.btn-glitch {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.6s ease;
}

.cyber-btn:hover .btn-glitch {
  left: 100%;
}

.btn-caret {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0;
  transition: all 0.3s ease;
}

.cyber-btn:hover .btn-caret {
  opacity: 1;
  right: 30px;
}

.btn-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.btn-particles span {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #38bdf8;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s;
}

.btn-particles span:nth-child(1) { top: 10%; left: 10%; }
.btn-particles span:nth-child(2) { top: 20%; right: 20%; }
.btn-particles span:nth-child(3) { bottom: 15%; left: 30%; }
.btn-particles span:nth-child(4) { bottom: 25%; right: 10%; }
.btn-particles span:nth-child(5) { top: 50%; left: 5%; }
.btn-particles span:nth-child(6) { top: 40%; right: 5%; }

.cyber-btn:hover .btn-particles span {
  opacity: 1;
  animation: particleFade 1s ease-out infinite;
}

.btn-particles span:nth-child(1) { animation-delay: 0s; }
.btn-particles span:nth-child(2) { animation-delay: 0.15s; }
.btn-particles span:nth-child(3) { animation-delay: 0.3s; }
.btn-particles span:nth-child(4) { animation-delay: 0.45s; }
.btn-particles span:nth-child(5) { animation-delay: 0.6s; }
.btn-particles span:nth-child(6) { animation-delay: 0.75s; }

@keyframes particleFade {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(0); opacity: 0; }
}

/* 登录底部 */
.login-footer {
  margin-top: 32px;
  animation: fadeInUp 0.6s ease-out 0.7s backwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.divider {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.3), transparent);
}

.divider-text {
  color: rgba(255, 255, 255, 0.3);
  font-size: 12px;
  letter-spacing: 2px;
}

.footer-text {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}

.link {
  color: #38bdf8;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 1px;
  background: #38bdf8;
  transition: width 0.3s ease;
}

.link:hover::after {
  width: 100%;
}

.link:hover {
  color: #00ffff;
  text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
}

/* 底部状态栏 */
.bottom-bar {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 24px;
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
  letter-spacing: 1px;
  z-index: 10;
}

.version {
  opacity: 0.6;
}

.status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 6px;
  height: 6px;
  background: #7dd3fc;
  border-radius: 50%;
  animation: statusPulse 2s ease-in-out infinite;
}

@keyframes statusPulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 5px #7dd3fc; }
  50% { opacity: 0.5; box-shadow: 0 0 15px #7dd3fc; }
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .login-container {
    padding: 12px;
    align-items: flex-start;
    padding-top: 60px;
  }

  .login-card {
    padding: 32px 24px !important;
    max-width: 100%;
  }

  .title {
    font-size: 28px !important;
    letter-spacing: 2px;
  }

  .logo-core {
    width: 64px;
    height: 64px;
  }

  .cyber-btn {
    height: 50px;
    font-size: 14px;
  }

  .bottom-bar {
    display: none;
  }

  .hexagon, .triangle, .circle {
    transform: scale(0.6);
  }

  .neon-orb {
    opacity: 0.3;
  }
}

@media screen and (max-width: 480px) {
  .login-card {
    padding: 24px 20px !important;
  }

  .title {
    font-size: 24px !important;
  }

  .subtitle-text {
    font-size: 13px !important;
  }

  .cyber-btn {
    height: 48px;
    font-size: 13px;
    letter-spacing: 2px;
  }
}
</style>

<style>
/* 注册对话框样式 - 全局作用域 */
body .register-dialog {
  background: rgba(10, 10, 15, 0.98) !important;
  backdrop-filter: blur(30px) !important;
  -webkit-backdrop-filter: blur(30px) !important;
  border: 1px solid rgba(56, 189, 248, 0.3) !important;
  border-radius: 4px !important;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8) !important;
}

body .register-dialog::before {
  content: '';
  position: absolute;
  inset: -2px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.5), rgba(14, 165, 233, 0.5));
  border-radius: 6px;
  z-index: -1;
  filter: blur(10px);
  opacity: 0.5;
}

body .register-dialog .el-dialog__header {
  padding: 24px 28px 16px !important;
  border-bottom: 1px solid rgba(56, 189, 248, 0.2) !important;
  margin: 0 !important;
}

body .register-dialog .el-dialog__title {
  color: #ffffff !important;
  font-weight: 700;
  font-size: 20px !important;
  letter-spacing: 2px;
  background: linear-gradient(135deg, #38bdf8, #0ea5e9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

body .register-dialog .el-dialog__close {
  color: rgba(56, 189, 248, 0.6) !important;
}

body .register-dialog .el-dialog__close:hover {
  color: #38bdf8 !important;
  text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
}

body .register-dialog .el-dialog__body {
  padding: 24px 28px !important;
}

body .register-dialog .el-dialog__footer {
  padding: 16px 28px 24px !important;
  border-top: 1px solid rgba(56, 189, 248, 0.2) !important;
}

body .register-dialog .el-form-item__label {
  color: rgba(255, 255, 255, 0.8) !important;
  font-weight: 500;
  font-size: 13px;
  margin-bottom: 6px !important;
}

body .register-dialog .el-form-item__error {
  color: #ff4757 !important;
}

body .register-dialog .el-input__wrapper {
  background: rgba(0, 0, 0, 0.4) !important;
  border: 1px solid rgba(56, 189, 248, 0.2) !important;
  border-radius: 4px !important;
  box-shadow: none !important;
  transition: all 0.3s !important;
}

body .register-dialog .el-input__wrapper:hover {
  border-color: rgba(56, 189, 248, 0.4) !important;
}

body .register-dialog .el-input__wrapper.is-focus {
  background: rgba(56, 189, 248, 0.05) !important;
  border-color: #38bdf8 !important;
  box-shadow: 0 0 15px rgba(56, 189, 248, 0.3) !important;
}

body .register-dialog .el-input__inner {
  color: #ffffff !important;
}

body .register-dialog .el-input__inner::placeholder {
  color: rgba(255, 255, 255, 0.3) !important;
}

body .register-dialog .el-select {
  width: 100%;
}

body .register-dialog .el-select .el-input__wrapper {
  background: rgba(0, 0, 0, 0.4) !important;
  border-color: rgba(56, 189, 248, 0.2) !important;
}

body .register-dialog .dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

body .register-dialog .dialog-btn {
  min-width: 100px;
  height: 42px;
  border-radius: 4px !important;
  border: 1px solid rgba(56, 189, 248, 0.3) !important;
  background: rgba(0, 0, 0, 0.4) !important;
  color: rgba(255, 255, 255, 0.8) !important;
  font-weight: 600;
  letter-spacing: 1px;
  transition: all 0.3s !important;
}

body .register-dialog .dialog-btn:hover {
  background: rgba(56, 189, 248, 0.1) !important;
  border-color: rgba(56, 189, 248, 0.5) !important;
  color: #ffffff !important;
  transform: translateY(-2px);
}

body .register-dialog .dialog-btn-primary {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.3), rgba(14, 165, 233, 0.3)) !important;
  border: 1px solid #38bdf8 !important;
  color: #ffffff !important;
  box-shadow: 0 0 20px rgba(56, 189, 248, 0.3) !important;
}

body .register-dialog .dialog-btn-primary:hover {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.5), rgba(14, 165, 233, 0.5)) !important;
  box-shadow: 0 0 30px rgba(56, 189, 248, 0.5) !important;
  transform: translateY(-3px);
}

body .register-dialog .form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

body .register-dialog .full-width {
  width: 100%;
}

/* 下拉菜单样式 */
body .el-select-dropdown {
  background: rgba(10, 10, 15, 0.98) !important;
  backdrop-filter: blur(20px) !important;
  border: 1px solid rgba(56, 189, 248, 0.3) !important;
  border-radius: 4px !important;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5) !important;
}

body .el-select-dropdown__item {
  color: rgba(255, 255, 255, 0.8) !important;
  transition: all 0.2s !important;
}

body .el-select-dropdown__item.hover,
body .el-select-dropdown__item:hover {
  background: rgba(56, 189, 248, 0.2) !important;
  color: #38bdf8 !important;
}

body .el-select-dropdown__item.selected {
  background: rgba(56, 189, 248, 0.3) !important;
  color: #00ffff !important;
  font-weight: 600;
}

/* 遮罩层 */
body .el-overlay {
  background: rgba(10, 10, 15, 0.8) !important;
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
