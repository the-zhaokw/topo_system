<template>
  <div class="skeleton-wrapper" :class="{ 'skeleton-animated': animated }">
    <slot>
      <!-- 默认骨架：列表卡片 -->
      <div v-for="i in count" :key="i" class="skeleton-list-card">
        <div class="skeleton-line skeleton-title"></div>
        <div class="skeleton-line skeleton-text"></div>
        <div class="skeleton-line skeleton-text short"></div>
        <div class="skeleton-row">
          <div class="skeleton-block"></div>
          <div class="skeleton-block small"></div>
        </div>
      </div>
    </slot>
  </div>
</template>

<script setup>
defineProps({
  count: { type: Number, default: 5 },
  animated: { type: Boolean, default: true }
})
</script>

<style scoped>
.skeleton-wrapper {
  width: 100%;
}

.skeleton-list-card,
.skeleton-stat-card,
.skeleton-detail-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.skeleton-line {
  height: 14px;
  background: linear-gradient(90deg, #f1f5f9 0%, #e2e8f0 50%, #f1f5f9 100%);
  background-size: 200% 100%;
  border-radius: 6px;
  margin-bottom: 10px;
}

.skeleton-title {
  width: 60%;
  height: 18px;
}

.skeleton-text {
  width: 100%;
}

.skeleton-text.short {
  width: 40%;
}

.skeleton-row {
  display: flex;
  gap: 12px;
  margin-top: 14px;
  align-items: center;
}

.skeleton-block {
  height: 32px;
  width: 80px;
  background: linear-gradient(90deg, #f1f5f9 0%, #e2e8f0 50%, #f1f5f9 100%);
  background-size: 200% 100%;
  border-radius: 6px;
}

.skeleton-block.small {
  width: 60px;
  height: 24px;
}

.skeleton-animated .skeleton-line,
.skeleton-animated .skeleton-block {
  animation: skeletonShimmer 1.5s ease-in-out infinite;
}

@keyframes skeletonShimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
