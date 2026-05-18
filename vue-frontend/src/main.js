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
      message.includes('message channel closed')) {
    return
  }
  originalConsoleError.apply(console, args)
}

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