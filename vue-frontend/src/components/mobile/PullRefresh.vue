<template>
  <div
    ref="containerRef"
    class="mobile-pull-container"
    :class="{ 'is-pulling': isPulling, 'is-refreshing': isRefreshing }"
    :style="{ '--pull-distance': pullDistance + 'px' }"
  >
    <!-- 下拉刷新指示器 -->
    <div class="pull-indicator" :style="{ height: pullDistance + 'px' }">
      <div class="pull-content">
        <el-icon
          class="pull-icon"
          :class="{ spinning: isRefreshing }"
          :size="20"
        >
          <Loading v-if="isRefreshing" />
          <ArrowDown v-else />
        </el-icon>
        <span class="pull-text">{{ refreshText }}</span>
      </div>
    </div>

    <!-- 加载更多指示器 -->
    <div v-if="isLoadingMore" class="load-more-indicator">
      <el-icon class="spinning" :size="16"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
    <div v-else-if="!hasMore" class="load-more-end">
      <span>没有更多了</span>
    </div>

    <slot />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { Loading, ArrowDown } from '@element-plus/icons-vue'

const props = defineProps({
  onRefresh: { type: Function, default: null },
  onLoadMore: { type: Function, default: null },
  threshold: { type: Number, default: 70 },
  loadMoreThreshold: { type: Number, default: 200 },
  hasMore: { type: Boolean, default: true }
})

const emit = defineEmits(['refresh', 'load-more'])

const containerRef = ref(null)
const isRefreshing = ref(false)
const isLoadingMore = ref(false)
const hasMore = ref(props.hasMore)
const pullDistance = ref(0)
const isPulling = ref(false)

const refreshText = computed(() => {
  if (isRefreshing.value) return '正在刷新...'
  if (pullDistance.value >= props.threshold) return '释放立即刷新'
  if (isPulling.value) return '下拉刷新'
  return ''
})

let startY = 0
let isDragging = false
let scrollEl = null

watch(() => props.hasMore, (val) => {
  hasMore.value = val
})

const onTouchStart = (e) => {
  if (isRefreshing.value || isLoadingMore.value) return
  if (!scrollEl || scrollEl.scrollTop > 0) {
    isDragging = false
    return
  }
  isDragging = true
  startY = e.touches[0].clientY
}

const onTouchMove = (e) => {
  if (!isDragging || isRefreshing.value) return
  const diff = e.touches[0].clientY - startY
  if (diff <= 0) {
    pullDistance.value = 0
    return
  }
  const damped = Math.min(diff * 0.45, props.threshold * 1.6)
  pullDistance.value = damped
  isPulling.value = true
}

const onTouchEnd = async () => {
  if (!isDragging) return
  isDragging = false
  if (pullDistance.value >= props.threshold) {
    pullDistance.value = props.threshold
    await doRefresh()
  } else {
    pullDistance.value = 0
  }
  isPulling.value = false
}

const onScroll = () => {
  if (!scrollEl || isLoadingMore.value || !hasMore.value || !props.onLoadMore) return
  const { scrollTop, scrollHeight, clientHeight } = scrollEl
  if (scrollHeight - (scrollTop + clientHeight) < props.loadMoreThreshold) {
    doLoadMore()
  }
}

const doRefresh = async () => {
  isRefreshing.value = true
  emit('refresh')
  try {
    if (props.onRefresh) {
      await props.onRefresh()
    }
  } catch (e) {
    console.error('Refresh failed:', e)
  } finally {
    isRefreshing.value = false
    pullDistance.value = 0
  }
}

const doLoadMore = async () => {
  if (!props.onLoadMore) return
  isLoadingMore.value = true
  emit('load-more')
  try {
    const result = await props.onLoadMore()
    if (result === false || result?.hasMore === false) {
      hasMore.value = false
    }
  } catch (e) {
    console.error('Load more failed:', e)
  } finally {
    isLoadingMore.value = false
  }
}

const bind = () => {
  scrollEl = containerRef.value
  if (!scrollEl) return
  scrollEl.addEventListener('touchstart', onTouchStart, { passive: true })
  scrollEl.addEventListener('touchmove', onTouchMove, { passive: true })
  scrollEl.addEventListener('touchend', onTouchEnd)
  scrollEl.addEventListener('scroll', onScroll, { passive: true })
}

const unbind = () => {
  if (!scrollEl) return
  scrollEl.removeEventListener('touchstart', onTouchStart)
  scrollEl.removeEventListener('touchmove', onTouchMove)
  scrollEl.removeEventListener('touchend', onTouchEnd)
  scrollEl.removeEventListener('scroll', onScroll)
  scrollEl = null
}

onMounted(() => {
  nextTick(bind)
})

onUnmounted(() => {
  unbind()
})

defineExpose({ refresh: doRefresh, loadMore: doLoadMore })
</script>

<style scoped>
.mobile-pull-container {
  position: relative;
  height: 100%;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  touch-action: pan-y;
}

.pull-indicator {
  position: relative;
  width: 100%;
  overflow: hidden;
  transition: height 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mobile-pull-container.is-refreshing .pull-indicator {
  height: 50px;
  transition: height 0.2s ease;
}

.pull-content {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 13px;
  padding: 12px;
}

.pull-icon {
  transition: transform 0.2s;
}

.mobile-pull-container.is-pulling .pull-icon {
  transform: rotate(180deg);
}

.mobile-pull-container.is-pulling:not(.is-refreshing) .pull-icon {
  transform: rotate(180deg);
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.load-more-indicator,
.load-more-end {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 16px;
  color: #94a3b8;
  font-size: 12px;
}
</style>
