<template>
  <div class="permission-wrapper">
    <slot v-if="hasPermission" />
    <slot v-else-if="fallback" name="fallback" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/store/user'

const props = defineProps({
  roles: {
    type: Array,
    default: () => []
  },
  permission: {
    type: String,
    default: null
  },
  requireAll: {
    type: Boolean,
    default: false
  },
  fallbackSlot: {
    type: Boolean,
    default: false
  }
})

const userStore = useUserStore()

const hasPermission = computed(() => {
  if (props.roles.length === 0 && !props.permission) {
    return true
  }

  const userRoles = userStore.userInfo?.roles || []
  const userPermissions = userStore.userInfo?.permissions || []

  if (props.roles.length > 0) {
    if (props.requireAll) {
      return props.roles.every(role => userRoles.includes(role))
    } else {
      return props.roles.some(role => userRoles.includes(role))
    }
  }

  if (props.permission) {
    return userPermissions.includes(props.permission)
  }

  return true
})

const fallback = computed(() => props.fallbackSlot)
</script>

<style scoped>
.permission-wrapper {
  width: 100%;
}
</style>