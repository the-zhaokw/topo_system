<template>
  <div class="plan-layout">
    <div class="plan-sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <el-icon><Calendar /></el-icon>
          <span>工作计划</span>
        </div>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        background-color="#1a1a2e"
        text-color="#a0a0a0"
        active-text-color="#409EFF"
        :collapse="isCollapsed"
        @select="handleMenuSelect"
      >
        <el-menu-item index="dashboard">
          <el-icon><House /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>

        <el-menu-item index="plans">
          <el-icon><List /></el-icon>
          <template #title>计划列表</template>
        </el-menu-item>

        <el-menu-item index="gantt">
          <el-icon><TrendCharts /></el-icon>
          <template #title>甘特图</template>
        </el-menu-item>

        <el-menu-item index="review">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>复盘报告</template>
        </el-menu-item>

        <el-menu-item index="settings">
          <el-icon><Setting /></el-icon>
          <template #title>设置</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-tags" v-if="!isCollapsed">
        <div class="tags-header">
          <span>我的标签</span>
          <el-button text size="small" @click="showTagDialog = true">
            <el-icon><Plus /></el-icon>
          </el-button>
        </div>
        <div class="tags-list">
          <el-tag
            v-for="tag in myTags"
            :key="tag.name"
            :type="tag.type"
            size="small"
            class="tag-item"
            @click="filterByTag(tag.name)"
          >
            #{{ tag.name }}
          </el-tag>
        </div>
      </div>

      <div class="sidebar-footer">
        <el-button text @click="isCollapsed = !isCollapsed" class="collapse-btn">
          <el-icon v-if="isCollapsed"><DArrowRight /></el-icon>
          <el-icon v-else><DArrowLeft /></el-icon>
        </el-button>
      </div>
    </div>

    <div class="plan-main">
      <div class="main-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/personal-plan' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ pageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <el-input
            v-model="globalSearch"
            placeholder="自然语言搜索..."
            class="global-search"
            size="default"
            @keyup.enter="handleGlobalSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-dropdown trigger="click" @command="handleQuickCreate">
            <el-button type="primary">
              <el-icon><Plus /></el-icon>
              快速创建
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="natural">
                  <el-icon><Edit /></el-icon>
                  自然语言创建
                </el-dropdown-item>
                <el-dropdown-item command="form">
                  <el-icon><Document /></el-icon>
                  表单创建
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <el-badge :value="notificationCount" :hidden="notificationCount === 0" class="notification-badge">
            <el-button :icon="Bell" circle />
          </el-badge>

          <el-dropdown trigger="click">
            <div class="user-avatar">
              <el-avatar :size="32" :src="userAvatar" />
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="$router.push('/profile')">
                  <el-icon><User /></el-icon>
                  个人设置
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  退出
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <div class="main-content">
        <router-view />
      </div>
    </div>

    <el-dialog v-model="quickCreateDialogVisible" title="快速创建任务" width="500px">
      <div class="quick-create-content" v-if="quickCreateType === 'natural'">
        <el-input
          v-model="naturalLanguageInput"
          type="textarea"
          :rows="3"
          placeholder="例如：明天下午3点前完成竞品分析 #高优先级"
          @input="parseNaturalLanguage"
        />
        <div class="parse-result" v-if="parseResult">
          <el-descriptions :column="2" size="small" border>
            <el-descriptions-item label="任务名">{{ parseResult.title }}</el-descriptions-item>
            <el-descriptions-item label="截止时间">{{ parseResult.deadline }}</el-descriptions-item>
            <el-descriptions-item label="标签">{{ parseResult.tags }}</el-descriptions-item>
            <el-descriptions-item label="优先级">{{ parseResult.priority }}</el-descriptions-item>
            <el-descriptions-item label="预估时长" v-if="parseResult.estimated_minutes">{{ parseResult.estimated_minutes }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

      <el-form v-else :model="taskForm" label-width="100px">
        <el-form-item label="任务标题">
          <el-input v-model="taskForm.title" placeholder="请输入任务标题" />
        </el-form-item>
        <el-form-item label="任务描述">
          <el-input v-model="taskForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-select v-model="taskForm.priority">
                <el-option label="紧急" value="urgent" />
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预估时长">
              <el-input-number v-model="taskForm.estimated_minutes" :min="5" :step="5" :max="480" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期">
              <el-date-picker v-model="taskForm.start_date" type="date" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="截止日期">
              <el-date-picker v-model="taskForm.due_date" type="date" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="标签">
          <el-input v-model="taskForm.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
        <el-form-item label="依赖任务">
          <el-select v-model="taskForm.dependencies" multiple placeholder="选择依赖任务">
            <el-option v-for="t in availableTasks" :key="t.id" :label="t.title" :value="t.id" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="quickCreateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmQuickCreate">确认创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showTagDialog" title="管理标签" width="400px">
      <el-form :model="tagForm" inline>
        <el-form-item label="新标签">
          <el-input v-model="tagForm.name" placeholder="标签名" />
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="tagForm.color" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="addTag">添加</el-button>
        </el-form-item>
      </el-form>
      <el-divider />
      <div class="tag-list-management">
        <el-tag
          v-for="tag in myTags"
          :key="tag.name"
          :type="tag.type"
          closable
          @close="removeTag(tag.name)"
        >
          #{{ tag.name }}
        </el-tag>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  House, List, TrendCharts, DataAnalysis, Setting, Plus, DArrowLeft, DArrowRight,
  Search, Bell, Edit, Document, User, SwitchButton, Calendar
} from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const route = useRoute()
const router = useRouter()

const isCollapsed = ref(false)
const activeMenu = ref('dashboard')
const globalSearch = ref('')
const notificationCount = ref(0)
const userAvatar = ref('')
const showTagDialog = ref(false)

const quickCreateDialogVisible = ref(false)
const quickCreateType = ref('natural')
const naturalLanguageInput = ref('')
const parseResult = ref(null)

const taskForm = ref({
  title: '',
  description: '',
  priority: 'medium',
  estimated_minutes: 30,
  start_date: '',
  due_date: '',
  tags: '',
  dependencies: []
})

const availableTasks = ref([])

const myTags = ref([
  { name: '高优先级', type: 'danger' },
  { name: '沟通', type: 'warning' },
  { name: '开发', type: 'success' },
  { name: '文档', type: 'info' }
])

const tagForm = ref({
  name: '',
  color: '#409EFF'
})

const pageTitleMap = {
  dashboard: '工作台',
  plans: '计划列表',
  gantt: '甘特图',
  review: '复盘报告',
  settings: '设置'
}

const pageTitle = computed(() => pageTitleMap[activeMenu.value] || '工作台')

watch(() => route.path, (newPath) => {
  const pathMap = {
    '/personal-plan/dashboard': 'dashboard',
    '/personal-plan/plans': 'plans',
    '/personal-plan/gantt': 'gantt',
    '/personal-plan/review': 'review',
    '/personal-plan/settings': 'settings'
  }
  activeMenu.value = pathMap[newPath] || 'dashboard'
}, { immediate: true })

const handleMenuSelect = (index) => {
  router.push(`/personal-plan/${index}`)
}

const handleGlobalSearch = () => {
  if (!globalSearch.value.trim()) return
  ElMessage.info(`搜索: ${globalSearch.value}`)
}

const handleQuickCreate = (command) => {
  quickCreateType.value = command
  quickCreateDialogVisible.value = true
  if (command === 'form') {
    loadAvailableTasks()
  }
}

const loadAvailableTasks = async () => {
  try {
    const data = await apiService.personalPlan.getTasks({ status: 'todo,in_progress' })
    availableTasks.value = data.tasks || []
  } catch (error) {
    console.error('加载任务失败:', error)
  }
}

const parseNaturalLanguage = () => {
  const text = naturalLanguageInput.value
  if (!text) {
    parseResult.value = null
    return
  }

  const result = {
    title: text,
    deadline: null,
    tags: null,
    priority: '中',
    estimated_minutes: null
  }

  const timePatterns = [
    /明天下午(\d+)点前?/,
    /今天下午(\d+)点前?/,
    /今天(\d+)点/,
    /明天(\d+)点/,
    /(\d+)分钟/,
    /半小时/
  ]

  for (const pattern of timePatterns) {
    const match = text.match(pattern)
    if (match) {
      if (pattern.toString().includes('分钟')) {
        result.estimated_minutes = parseInt(match[1])
      } else if (pattern.toString().includes('半小时')) {
        result.estimated_minutes = 30
      } else {
        const hour = parseInt(match[1])
        const isTomorrow = text.includes('明天')
        const baseDate = new Date()
        if (isTomorrow) {
          baseDate.setDate(baseDate.getDate() + 1)
        }
        baseDate.setHours(hour, 0, 0, 0)
        result.deadline = baseDate.toLocaleString('zh-CN')
      }
      break
    }
  }

  if (text.includes('#高优先级') || text.includes('!!')) {
    result.priority = '高'
  } else if (text.includes('#紧急') || text.includes('!')) {
    result.priority = '紧急'
  }

  const tagMatch = text.match(/#(\S+)/g)
  if (tagMatch) {
    result.tags = tagMatch.map(t => t.replace('#', '')).join(', ')
  }

  parseResult.value = result
}

const confirmQuickCreate = async () => {
  try {
    let taskData
    if (quickCreateType.value === 'natural' && parseResult.value) {
      taskData = {
        title: parseResult.value.title,
        deadline: parseResult.value.deadline,
        tags: parseResult.value.tags,
        priority: parseResult.value.priority,
        estimated_minutes: parseResult.value.estimated_minutes
      }
    } else {
      taskData = { ...taskForm.value }
    }

    await apiService.personalPlan.createTask(taskData)
    ElMessage.success('任务创建成功')
    quickCreateDialogVisible.value = false
    naturalLanguageInput.value = ''
    parseResult.value = null
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

const filterByTag = (tagName) => {
  router.push({ path: '/personal-plan/plans', query: { tag: tagName } })
}

const addTag = () => {
  if (!tagForm.value.name) return
  myTags.value.push({
    name: tagForm.value.name,
    type: 'primary'
  })
  tagForm.value.name = ''
  ElMessage.success('标签添加成功')
}

const removeTag = (tagName) => {
  myTags.value = myTags.value.filter(t => t.name !== tagName)
}

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

onMounted(() => {
  userAvatar.value = '/avatar-placeholder.png'
})
</script>

<style scoped>
.plan-layout {
  display: flex;
  height: 100vh;
  background: #f5f7fa;
}

.plan-sidebar {
  width: 240px;
  background: #1a1a2e;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
}

.plan-sidebar:not(.collapsed) {
  width: 240px;
}

.plan-sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #2a2a4a;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
}

.logo .el-icon {
  font-size: 20px;
}

.sidebar-menu {
  flex: 1;
  border: none;
}

.sidebar-tags {
  padding: 12px 16px;
  border-top: 1px solid #2a2a4a;
}

.tags-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  color: #a0a0a0;
  font-size: 12px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag-item {
  cursor: pointer;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid #2a2a4a;
}

.collapse-btn {
  width: 100%;
  color: #a0a0a0;
}

.plan-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.main-header {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.global-search {
  width: 280px;
}

.notification-badge :deep(.el-badge__content) {
  top: -2px;
  right: -2px;
}

.user-avatar {
  cursor: pointer;
}

.main-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.quick-create-content {
  padding: 12px 0;
}

.parse-result {
  margin-top: 16px;
}

.tag-list-management {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

:deep(.el-menu--collapse) {
  width: 64px;
}
</style>
