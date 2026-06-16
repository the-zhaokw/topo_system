import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import './assets/mobile-responsive.css'
import './styles/design-system.css'
import './styles/mobile-utils.css'

import App from './App.vue'
import router from './router'

// 抑制 Chrome 扩展的非关键错误
const originalConsoleError = console.error
console.error = function(...args) {
  const message = args[0]?.toString() || ''
  // 过滤掉 Chrome 扩展相关的运行时错误
  if (message.includes('runtime.lastError') || 
      message.includes('message channel closed') ||
      message.includes('Unchecked runtime')) {
    return
  }
  originalConsoleError.apply(console, args)
}

// 抑制 Chrome 扩展的未捕获错误
window.addEventListener('error', (event) => {
  if (event.message && (
    event.message.includes('runtime.lastError') ||
    event.message.includes('message channel closed')
  )) {
    event.preventDefault()
  }
})

window.addEventListener('unhandledrejection', (event) => {
  if (event.reason && event.reason.message && (
    event.reason.message.includes('runtime.lastError') ||
    event.reason.message.includes('message channel closed')
  )) {
    event.preventDefault()
  }
})

const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
})

app.mount('#app')

// 注册 Service Worker (PWA)
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js')
      .then((reg) => {
        console.log('SW registered:', reg.scope)
      })
      .catch((err) => {
        console.log('SW registration failed:', err)
      })
  })
}