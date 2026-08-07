<!--
  LiquidGlassCard - 高级液态玻璃面板组件
  封装 Apple 风格的液态玻璃效果：
  - 弹性悬停回弹 (Elastic Hover)
  - 点击波纹涟漪 (Click Ripple)
  - 光泽流动效果 (Light Shimmer)
  - 立体层次感 (3D Depth)
-->
<template>
  <div
    ref="cardRef"
    :class="[
      'liquid-glass-panel',
      `theme-${theme}`,
      { 'is-pressed': isPressed, 'animate-enter': animate, [`animate-enter-${enterFrom}`]: enterFrom },
      delayClass
    ]"
    :style="cssVars"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
    @mousedown="handleMouseDown"
    @mouseup="handleMouseUp"
    @click="handleClick"
  >
    <!-- 顶部高光层（CSS ::before） -->
    <!-- 底部反光层（CSS ::after） -->

    <!-- 鼠标移动时的光泽流动 -->
    <div class="liquid-glass-shimmer"></div>

    <!-- 浮动光晕 -->
    <div class="liquid-glow"></div>

    <!-- 点击波纹 -->
    <div
      v-for="ripple in ripples"
      :key="ripple.id"
      class="liquid-glass-ripple"
      :style="{
        left: ripple.x + 'px',
        top: ripple.y + 'px',
        width: ripple.size + 'px',
        height: ripple.size + 'px'
      }"
    ></div>

    <!-- 内容插槽 -->
    <div class="liquid-glass-content">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
/**
 * LiquidGlassCard 组件
 * @prop {String} theme - 主题色: default|blue|purple|cyan|green|warm
 * @prop {Boolean} animate - 是否启用进场动画
 * @prop {String} enterFrom - 进场方向: left|right|null
 * @prop {Number} delay - 进场延迟 (1-5)
 * @prop {Boolean} ripple - 是否启用点击波纹
 */
import { ref, computed } from 'vue'

const props = defineProps({
  theme: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'blue', 'purple', 'cyan', 'green', 'warm'].includes(v)
  },
  animate: {
    type: Boolean,
    default: false
  },
  enterFrom: {
    type: String,
    default: null,
    validator: (v) => v === null || ['left', 'right'].includes(v)
  },
  delay: {
    type: Number,
    default: 0
  },
  ripple: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click'])

const cardRef = ref(null)
const isPressed = ref(false)
const mousePos = ref({ x: 50, y: 50 })
const ripples = ref([])
let rippleIdCounter = 0

// CSS 变量 - 用于光泽流动层定位
const cssVars = computed(() => ({
  '--mouse-x': mousePos.value.x + '%',
  '--mouse-y': mousePos.value.y + '%'
}))

// 延迟类
const delayClass = computed(() => {
  if (props.delay > 0 && props.delay <= 5) {
    return `delay-${props.delay}`
  }
  return ''
})

// 鼠标移动 - 更新光泽位置
const handleMouseMove = (e) => {
  if (!cardRef.value) return
  const rect = cardRef.value.getBoundingClientRect()
  const x = ((e.clientX - rect.left) / rect.width) * 100
  const y = ((e.clientY - rect.top) / rect.height) * 100
  mousePos.value = { x, y }
}

const handleMouseLeave = () => {
  mousePos.value = { x: 50, y: 50 }
  isPressed.value = false
}

// 按下时 - 弹性回弹效果
const handleMouseDown = () => {
  isPressed.value = true
}

const handleMouseUp = () => {
  isPressed.value = false
}

// 点击时 - 触发波纹
const handleClick = (e) => {
  if (props.ripple && cardRef.value) {
    const rect = cardRef.value.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    // 波纹大小 = 容器最长边的 1.2 倍，确保覆盖整个面板
    const size = Math.max(rect.width, rect.height) * 1.2

    const id = ++rippleIdCounter
    ripples.value.push({ id, x, y, size })

    // 800ms 后清理 DOM 节点（与 CSS 动画时长一致）
    setTimeout(() => {
      ripples.value = ripples.value.filter(r => r.id !== id)
    }, 850)
  }

  emit('click', e)
}
</script>

<style scoped>
.liquid-glass-content {
  position: relative;
  z-index: 4;
  width: 100%;
  height: 100%;
}
</style>
