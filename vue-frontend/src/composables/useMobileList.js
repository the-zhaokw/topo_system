import { ref, onMounted, onUnmounted, nextTick } from 'vue'

/**
 * 移动端下拉刷新 + 上拉加载 composable
 * 用法：
 *   const { containerRef, isRefreshing, isLoadingMore, hasMore, onRefresh, onLoadMore } = useMobileList({
 *     onRefresh: async () => { ... },
 *     onLoadMore: async () => { ... }
 *   })
 *   <div ref="containerRef" class="scroll-container">
 *     <!-- 内容 -->
 *   </div>
 */
export function useMobileList(options = {}) {
  const {
    onRefresh,
    onLoadMore,
    threshold = 80, // 触发刷新的下拉距离
    loadMoreThreshold = 200, // 触发加载更多的底部距离
    isMobile = true
  } = options

  const containerRef = ref(null)
  const isRefreshing = ref(false)
  const isLoadingMore = ref(false)
  const hasMore = ref(true)
  const pullDistance = ref(0)
  const isPulling = ref(false)

  let startY = 0
  let currentY = 0
  let isDragging = false
  let scrollEl = null

  const onTouchStart = (e) => {
    if (!isMobile || isRefreshing.value || isLoadingMore.value) return
    if (!scrollEl) return
    // 仅在容器顶部时启用下拉
    if (scrollEl.scrollTop > 0) {
      isDragging = false
      return
    }
    isDragging = true
    startY = e.touches[0].clientY
    currentY = startY
  }

  const onTouchMove = (e) => {
    if (!isDragging || isRefreshing.value) return
    currentY = e.touches[0].clientY
    const diff = currentY - startY
    if (diff <= 0) {
      pullDistance.value = 0
      return
    }
    // 阻尼效果
    const damped = Math.min(diff * 0.45, threshold * 1.6)
    pullDistance.value = damped
    isPulling.value = true
  }

  const onTouchEnd = async () => {
    if (!isDragging) return
    isDragging = false
    isPulling.value = false
    if (pullDistance.value >= threshold) {
      pullDistance.value = threshold
      await doRefresh()
    } else {
      pullDistance.value = 0
    }
  }

  const onScroll = () => {
    if (!scrollEl || isLoadingMore.value || !hasMore.value) return
    const { scrollTop, scrollHeight, clientHeight } = scrollEl
    if (scrollHeight - (scrollTop + clientHeight) < loadMoreThreshold) {
      doLoadMore()
    }
  }

  const doRefresh = async () => {
    if (!onRefresh) {
      pullDistance.value = 0
      return
    }
    isRefreshing.value = true
    try {
      await onRefresh()
    } catch (e) {
      console.error('Refresh failed:', e)
    } finally {
      isRefreshing.value = false
      pullDistance.value = 0
    }
  }

  const doLoadMore = async () => {
    if (!onLoadMore) return
    isLoadingMore.value = true
    try {
      const result = await onLoadMore()
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

  return {
    containerRef,
    isRefreshing,
    isLoadingMore,
    hasMore,
    pullDistance,
    isPulling,
    onRefresh: doRefresh,
    onLoadMore: doLoadMore,
    rebind: bind
  }
}
