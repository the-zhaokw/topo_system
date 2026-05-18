# 移动端适配快速参考指南

## 🎯 核心文件位置

```
vue-frontend/src/
├── styles/
│   ├── mobile-responsive.css    # 全局响应式样式 (2532行)
│   ├── mobile-utils.css         # 增强工具类 (新建)
│   └── design-system.css        # 设计系统
├── composables/
│   └── useResponsive.js         # 响应式Composable
├── components/
│   └── mobile/
│       └── MobileMenu.vue       # 移动端菜单
├── views/
│   └── (所有页面组件)            # 已包含响应式布局
└── App.vue                      # 主布局已适配
```

## ⚡ 快速使用

### 1. 在页面中使用响应式Composable

```vue
<template>
  <div>
    <!-- 根据屏幕宽度显示不同内容 -->
    <DesktopContent v-if="!isMobile" />
    <MobileContent v-else />
    
    <!-- 或使用CSS工具类 -->
    <div class="hidden-mobile">仅桌面端显示</div>
    <div class="hidden-desktop">仅移动端显示</div>
  </div>
</template>

<script setup>
import { useResponsive } from '@/composables/useResponsive'

const { isMobile } = useResponsive()
</script>
```

### 2. Element Plus栅格系统

```vue
<el-row :gutter="20">
  <el-col :xs="24" :sm="12" :md="8" :lg="6">
    <!-- 移动端占满一行 -->
    <!-- 平板占2列 -->
    <!-- 桌面占3列 -->
    <!-- 大屏占4列 -->
  </el-col>
</el-row>
```

### 3. 常用工具类

```vue
<!-- 隐藏/显示 -->
<div class="hidden-mobile">桌面端可见</div>
<div class="hidden-desktop">移动端可见</div>

<!-- 布局 -->
<div class="flex-mobile-column">移动端垂直布局</div>
<div class="flex-mobile-wrap">移动端换行</div>

<!-- 间距 -->
<div class="m-4">边距16px</div>
<div class="p-3">内边距12px</div>

<!-- 文本 -->
<span class="text-xs">12px文字</span>
<span class="text-center">居中</span>
<span class="text-truncate">超长省略</span>

<!-- 宽度 -->
<div class="w-full">100%宽度</div>
```

### 4. 移动端卡片

```vue
<div class="mobile-card">
  <div class="mobile-card-header">
    <span>标题</span>
    <el-tag>状态</el-tag>
  </div>
  <div class="mobile-card-body">
    内容区域
  </div>
  <div class="mobile-card-footer">
    <el-button>取消</el-button>
    <el-button type="primary">确认</el-button>
  </div>
</div>
```

### 5. 移动端列表

```vue
<div class="mobile-list">
  <div class="mobile-list-item">
    <div class="item-content">列表项内容</div>
    <el-icon><ArrowRight /></el-icon>
  </div>
</div>
```

### 6. 移动端表单

```vue
<div class="mobile-form">
  <div class="mobile-form-item">
    <label class="mobile-form-label">用户名</label>
    <el-input v-model="form.username" />
  </div>
</div>
```

### 7. 移动端按钮组

```vue
<div class="mobile-button-group">
  <el-button>按钮1</el-button>
  <el-button type="primary">按钮2</el-button>
</div>
<!-- 移动端自动垂直排列 -->
```

## 🎨 设计规范

### 字号规范
```css
移动端基准: 14px
超小屏: 12px
小屏: 13px
中屏: 14px
大屏: 15px
```

### 间距规范
```css
小间距: 8px
中间距: 12px
大间距: 16px
```

### 圆角规范
```css
卡片: 8px → 移动端6px
按钮: 4px
输入框: 4px
对话框: 4px
```

### 触摸区域
```css
最小点击区域: 44px × 44px
按钮高度: 36px (移动端)
图标大小: 20px (移动端)
```

## 📱 响应式断点

| 断点 | 最小宽度 | 最大宽度 | 典型设备 |
|------|---------|---------|---------|
| 超小屏 | 0px | 480px | iPhone SE |
| 小屏 | 481px | 768px | iPhone 12 |
| 中屏 | 769px | 1024px | iPad |
| 大屏 | 1025px | ∞ | 桌面 |

## 🔧 常用响应式属性

```vue
<template>
  <!-- 隐藏/显示 -->
  <div class="hidden-mobile">桌面端</div>
  <div class="hidden-desktop">移动端</div>
  
  <!-- Flex布局 -->
  <div class="flex-mobile-column">
    <div>垂直排列</div>
  </div>
  
  <!-- 网格布局 -->
  <div class="mobile-grid">
    <div>自适应列</div>
  </div>
  
  <!-- 滚动 -->
  <div class="mobile-scroll">垂直滚动</div>
  <div class="mobile-scroll-x">水平滚动</div>
</template>
```

## ⚙️ 移动端配置

### 在页面组件中使用

```vue
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useResponsive } from '@/composables/useResponsive'

const { isMobile, isMobileRef } = useResponsive()

// 根据移动端状态做特殊处理
onMounted(() => {
  if (isMobileRef.value) {
    // 移动端初始化
  }
})
</script>
```

### 在JavaScript中判断

```javascript
// 方式1: 使用Composable
import { useResponsive } from '@/composables/useResponsive'
const { isMobile } = useResponsive()

// 方式2: 直接检查
const isMobileDevice = window.innerWidth < 768

// 方式3: 监听resize
window.addEventListener('resize', () => {
  const isMobile = window.innerWidth < 768
  console.log('Is mobile:', isMobile)
})
```

## 🎯 最佳实践

### ✅ 推荐做法

1. **使用栅格系统**
   ```vue
   <el-col :xs="24" :sm="12" :md="8">
   ```

2. **使用工具类**
   ```vue
   <div class="hidden-mobile">桌面端内容</div>
   ```

3. **移动端优先设计**
   ```css
   .my-component {
     /* 移动端样式 */
     @media (min-width: 768px) {
       /* 桌面端增强 */
     }
   }
   ```

4. **使用flex布局**
   ```vue
   <div style="display: flex; flex-wrap: wrap;">
   ```

5. **表格横向滚动**
   ```vue
   <div style="overflow-x: auto;">
     <el-table>
   ```

### ❌ 避免做法

1. **固定宽度**
   ```vue
   <!-- 避免 -->
   <div style="width: 1200px;">
   
   <!-- 推荐 -->
   <div class="w-full">
   ```

2. **隐藏溢出**
   ```vue
   <!-- 避免 -->
   <div style="overflow: hidden;">
   
   <!-- 推荐 -->
   <div class="mobile-scroll">
   ```

3. **过小点击区域**
   ```vue
   <!-- 避免 -->
   <button style="padding: 2px;">点击</button>
   
   <!-- 推荐 -->
   <button class="el-button">点击</button>
   ```

4. **复杂嵌套**
   ```vue
   <!-- 避免过多嵌套 -->
   <div>
     <div>
       <div>
         <div>内容</div>
       </div>
     </div>
   </div>
   ```

## 📦 常用组件适配示例

### 表格组件
```vue
<el-table :data="tableData" class="mobile-table">
  <el-table-column prop="name" label="名称" />
  <el-table-column prop="status" label="状态" />
  <el-table-column label="操作" width="120">
    <template #default>
      <el-button size="small">编辑</el-button>
    </template>
  </el-table-column>
</el-table>

<style>
.mobile-table {
  @media screen and (max-width: 768px) {
    font-size: 12px;
  }
}
</style>
```

### 表单组件
```vue
<el-form label-position="top" class="mobile-form">
  <el-form-item label="用户名">
    <el-input v-model="form.username" />
  </el-form-item>
</el-form>
```

### 卡片列表
```vue
<el-row :gutter="16">
  <el-col :xs="24" :sm="12" :md="8" v-for="item in items" :key="item.id">
    <el-card class="mobile-card">
      {{ item.title }}
    </el-card>
  </el-col>
</el-row>
```

## 🐛 常见问题

### Q: 移动端样式不生效？
A: 检查是否正确导入了 `mobile-utils.css`

### Q: 表格横向滚动不工作？
A: 确保表格容器有 `overflow-x: auto` 或使用 `.mobile-scroll-x` 类

### Q: 移动端字体变大？
A: iOS Safari会自动调整字体，使用16px基准可防止缩放

### Q: 固定定位在iOS失效？
A: 使用 `.ios-fixed-fix` 类或添加 `-webkit-transform: translateZ(0)`

### Q: 100vh在iOS不正确？
A: 使用 `height: 100vh; height: -webkit-fill-available;`

## 🎨 主题定制

### 修改移动端配色
```css
:root {
  @media screen and (max-width: 768px) {
    --primary-color: #409EFF;
  }
}
```

### 自定义断点
```css
/* 添加新的断点 */
@media screen and (max-width: 360px) {
  /* 超小屏样式 */
}
```

## 📞 获取帮助

- 查看 `MOBILE_CHECKLIST.md` 获取完整检查清单
- 查看 `mobile-responsive.css` 查看所有响应式规则
- 查看 `mobile-utils.css` 查看所有工具类
- 查看 `useResponsive.js` 了解响应式Composable

## 🚀 性能优化

### 懒加载图片
```vue
<img v-lazy="imageSrc" />
```

### 减少动画
```vue
<div class="reduce-motion">
  动画内容
</div>
```

### 简化阴影
```vue
<div class="simplified-shadows">
  卡片内容
</div>
```

## ✅ 测试清单

- [ ] 桌面端显示正常
- [ ] 平板显示正常
- [ ] 移动端显示正常
- [ ] 表格横向滚动正常
- [ ] 表单输入正常
- [ ] 导航菜单正常
- [ ] 触摸反馈正常
- [ ] 滚动流畅
- [ ] 性能达标

## 🎯 下一步

1. 运行开发服务器测试
2. 使用Chrome DevTools模拟设备测试
3. 在真实设备上测试
4. 使用Lighthouse检查性能
5. 根据实际使用反馈优化
