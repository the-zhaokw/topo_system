<template>
  <div class="skeleton-grid">
    <div
      v-for="i in count"
      :key="i"
      class="skeleton-stat-card"
      :class="{ 'skeleton-animated': animated }"
    >
      <div class="skeleton-icon"></div>
      <div class="skeleton-content">
        <div class="skeleton-line skeleton-value"></div>
        <div class="skeleton-line skeleton-label"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  count: { type: Number, default: 4 },
  animated: { type: Boolean, default: true }
})
</script>

<style scoped>
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.skeleton-stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.skeleton-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: linear-gradient(90deg, #f1f5f9 0%, #e2e8f0 50%, #f1f5f9 100%);
  background-size: 200% 100%;
  flex-shrink: 0;
}

.skeleton-content {
  flex: 1;
}

.skeleton-line {
  height: 12px;
  background: linear-gradient(90deg, #f1f5f9 0%, #e2e8f0 50%, #f1f5f9 100%);
  background-size: 200% 100%;
  border-radius: 4px;
  margin-bottom: 6px;
}

.skeleton-value {
  width: 60%;
  height: 18px;
}

.skeleton-label {
  width: 80%;
  height: 10px;
}

.skeleton-animated .skeleton-icon,
.skeleton-animated .skeleton-line {
  animation: shimmer 1.5s ease-in-out infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media screen and (max-width: 768px) {
  .skeleton-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  .skeleton-stat-card {
    padding: 12px;
  }
}
</style>
