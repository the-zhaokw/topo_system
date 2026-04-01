<template>
  <div class="user-selector">
    <el-select
      v-model="selectedUsers"
      :multiple="multiple"
      :placeholder="placeholder"
      :filterable="filterable"
      :remote="remote"
      :remote-method="handleRemoteSearch"
      :loading="loading"
      :clearable="clearable"
      :disabled="disabled"
      style="width: 100%;"
      @change="handleChange"
      @focus="handleFocus"
    >
      <el-option
        v-for="user in userList"
        :key="user.id"
        :label="getUserLabel(user)"
        :value="user.id"
      >
        <div class="user-option">
          <el-avatar v-if="showAvatar" :size="24" :src="user.avatar">
            {{ user.username?.charAt(0)?.toUpperCase() }}
          </el-avatar>
          <span class="user-info">
            <span class="user-name">{{ user.username }}</span>
            <span v-if="showRole && user.role" class="user-role">{{ user.role }}</span>
          </span>
        </div>
      </el-option>
    </el-select>

    <div v-if="showRecent && recentUsers.length > 0" class="recent-users">
      <span class="recent-label">最近使用：</span>
      <el-tag
        v-for="user in recentUsers"
        :key="user.id"
        size="small"
        class="recent-tag"
        @click="handleSelectRecent(user)"
      >
        {{ user.username }}
      </el-tag>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { apiService } from '@/services/api'

const props = defineProps({
  modelValue: {
    type: [Number, String, Array],
    default: null
  },
  projectId: {
    type: [Number, String],
    default: null
  },
  multiple: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: '请选择用户'
  },
  filterable: {
    type: Boolean,
    default: true
  },
  remote: {
    type: Boolean,
    default: true
  },
  clearable: {
    type: Boolean,
    default: true
  },
  disabled: {
    type: Boolean,
    default: false
  },
  showAvatar: {
    type: Boolean,
    default: true
  },
  showRole: {
    type: Boolean,
    default: true
  },
  showRecent: {
    type: Boolean,
    default: true
  },
  excludeUserIds: {
    type: Array,
    default: () => []
  },
  minUsers: {
    type: Number,
    default: 0
  },
  maxUsers: {
    type: Number,
    default: Infinity
  }
})

const emit = defineEmits(['update:modelValue', 'change', 'select'])

const selectedUsers = ref(props.multiple ? [] : null)
const selectedUser = ref(null)
const userList = ref([])
const loading = ref(false)
const recentUsers = ref([])

const getUserLabel = (user) => {
  return `${user.username}${user.email ? ` (${user.email})` : ''}`
}

const handleFocus = async () => {
  if (userList.value.length === 0) {
    await loadUsers()
  }
}

const handleRemoteSearch = async (query) => {
  if (!query) {
    await loadUsers()
    return
  }

  loading.value = true
  try {
    const response = await apiService.users.getList({
      search: query,
      project_id: props.projectId,
      per_page: 20
    })
    const users = response?.users || response?.data || []
    userList.value = users.filter(u => !props.excludeUserIds.includes(u.id))
  } catch (error) {
    console.error('搜索用户失败:', error)
  } finally {
    loading.value = false
  }
}

const loadUsers = async () => {
  loading.value = true
  try {
    const params = { per_page: 50 }
    if (props.projectId) {
      params.project_id = props.projectId
    }
    const response = await apiService.users.getList(params)
    const users = response?.users || response?.data || []
    userList.value = users.filter(u => !props.excludeUserIds.includes(u.id))
  } catch (error) {
    console.error('加载用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

const loadRecentUsers = () => {
  try {
    const recent = localStorage.getItem('recent_selected_users')
    if (recent) {
      recentUsers.value = JSON.parse(recent).slice(0, 5)
    }
  } catch (error) {
    console.error('加载最近使用用户失败:', error)
  }
}

const handleSelectRecent = (user) => {
  if (props.multiple) {
    if (!selectedUsers.value.includes(user.id)) {
      if (selectedUsers.value.length >= props.maxUsers) {
        return
      }
      selectedUsers.value.push(user.id)
      handleChange(selectedUsers.value)
    }
  } else {
    selectedUsers.value = user.id
    handleChange(user.id)
  }
}

const handleChange = (value) => {
  emit('update:modelValue', value)

  const user = userList.value.find(u => u.id === value)
  if (user) {
    selectedUser.value = user
    emit('select', user)
  }

  emit('change', value)

  if (props.multiple && value.length > 0) {
    saveRecentUsers(value)
  }
}

const saveRecentUsers = (userIds) => {
  try {
    const selected = userList.value.filter(u => userIds.includes(u.id))
    const recent = JSON.parse(localStorage.getItem('recent_selected_users') || '[]')
    const updated = [...new Map([...selected, ...recent].map(u => [u.id, u])).values()]
    localStorage.setItem('recent_selected_users', JSON.stringify(updated.slice(0, 20)))
  } catch (error) {
    console.error('保存最近使用用户失败:', error)
  }
}

watch(() => props.modelValue, (newVal) => {
  selectedUsers.value = newVal
}, { immediate: true })

onMounted(async () => {
  await loadUsers()
  loadRecentUsers()
})
</script>

<style scoped>
.user-selector {
  width: 100%;
}

.user-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
}

.user-role {
  font-size: 12px;
  color: #909399;
}

.recent-users {
  margin-top: 8px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.recent-label {
  font-size: 12px;
  color: #909399;
}

.recent-tag {
  cursor: pointer;
}
</style>