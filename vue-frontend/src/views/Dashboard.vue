<template>
  <div class="dashboard">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-gradient-orb orb-1"></div>
      <div class="bg-gradient-orb orb-2"></div>
      <div class="bg-gradient-orb orb-3"></div>
    </div>

    <div class="dashboard-header animate-fade-in-down">
      <div class="header-content">
        <div class="header-icon">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="header-text">
          <h2>TOPO系统</h2>
          <p>个人工作台 · 组织架构管理与工作协同平台</p>
        </div>
      </div>
      <div class="header-stats">
        <div class="header-stat-item">
          <span class="header-stat-value">{{ todoCount }}</span>
          <span class="header-stat-label">待办事项</span>
        </div>
        <div class="header-stat-divider"></div>
        <div class="header-stat-item">
          <span class="header-stat-value">{{ statistics.summary?.active_projects || 0 }}</span>
          <span class="header-stat-label">活跃项目</span>
        </div>
      </div>
    </div>
    
    <!-- 个人参与的项目和工作统计 -->
    <div class="organization-section">
      <el-row :gutter="20">
        <el-col :span="12" :xs="24" class="animate-fade-in-up delay-100">
          <el-card class="org-card project-card glass-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <div class="card-icon-wrapper card-icon-blue">
                    <el-icon><Folder /></el-icon>
                  </div>
                  <span>个人参与的项目</span>
                </div>
                <el-tag type="info" effect="plain" round>{{ userProjects.length }}个项目</el-tag>
              </div>
            </template>
            <div class="org-content">
              <div v-for="(project, index) in userProjects" :key="project.id" 
                   class="org-item" 
                   :style="{ animationDelay: `${index * 50}ms` }"
                   @click="$router.push(`/projects/${project.id}`)">
                <div class="project-info">
                  <div class="project-avatar">
                    {{ project.name.charAt(0).toUpperCase() }}
                  </div>
                  <div class="project-details">
                    <span class="project-name">{{ project.name }}</span>
                    <span class="project-manager">
                      <el-icon><User /></el-icon>
                      {{ project.manager }}
                    </span>
                  </div>
                </div>
                <el-button type="primary" link class="project-link">
                  <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
              <el-empty v-if="userProjects.length === 0" description="暂无参与的项目" :image-size="60" />
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="12" :xs="24" class="animate-fade-in-up delay-200">
          <el-card class="nav-card glass-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <div class="card-icon-wrapper card-icon-purple">
                    <el-icon><Grid /></el-icon>
                  </div>
                  <span>功能导航</span>
                </div>
              </div>
            </template>
            <div class="navigation-grid">
              <div class="nav-item" @click="goToMyTasks" :class="{ 'has-badge': todoCount > 0 }">
                <div class="nav-icon-wrapper nav-icon-todo">
                  <el-icon><Document /></el-icon>
                </div>
                <span class="nav-text">待办事项</span>
                <span v-if="todoCount > 0" class="todo-badge">{{ todoCount > 99 ? '99+' : todoCount }}</span>
              </div>
              <div class="nav-item" @click="$router.push('/personal-plan')">
                <div class="nav-icon-wrapper nav-icon-plan">
                  <el-icon><List /></el-icon>
                </div>
                <span class="nav-text">工作计划</span>
              </div>
              <div class="nav-item" @click="$router.push('/activities')">
                <div class="nav-icon-wrapper nav-icon-activity">
                  <el-icon><DataLine /></el-icon>
                </div>
                <span class="nav-text">活动记录</span>
              </div>
              <div class="nav-item" @click="$router.push('/work-logs')">
                <div class="nav-icon-wrapper nav-icon-log">
                  <el-icon><Notebook /></el-icon>
                </div>
                <span class="nav-text">我的日志</span>
              </div>
              <div v-if="isDepartmentManager" class="nav-item" @click="$router.push('/work-logs?view=all')">
                <div class="nav-icon-wrapper nav-icon-team">
                  <el-icon><Management /></el-icon>
                </div>
                <span class="nav-text">员工日志</span>
              </div>
              <div class="nav-item" @click="$router.push('/my-department')">
                <div class="nav-icon-wrapper nav-icon-dept">
                  <el-icon><OfficeBuilding /></el-icon>
                </div>
                <span class="nav-text">我的部门</span>
              </div>
              <div class="nav-item" @click="$router.push('/my-attendance')">
                <div class="nav-icon-wrapper nav-icon-attendance">
                  <el-icon><AlarmClock /></el-icon>
                </div>
                <span class="nav-text">我的考勤</span>
              </div>
              <div class="nav-item" @click="$router.push('/profile')">
                <div class="nav-icon-wrapper nav-icon-profile">
                  <el-icon><User /></el-icon>
                </div>
                <span class="nav-text">个人中心</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 快速入口 -->
    <div class="quick-access-section animate-fade-in-up delay-300">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <div class="card-icon-wrapper card-icon-orange">
                <el-icon><Promotion /></el-icon>
              </div>
              <span>快速入口</span>
            </div>
          </div>
        </template>
        <div class="quick-access-grid">
          <div class="access-item access-bug" @click="$router.push('/bugs')">
            <div class="access-icon-wrapper">
              <el-icon><Warning /></el-icon>
            </div>
            <span>缺陷管理</span>
          </div>
          <div class="access-item access-project" @click="$router.push('/projects')">
            <div class="access-icon-wrapper">
              <el-icon><FolderOpened /></el-icon>
            </div>
            <span>项目管理</span>
          </div>
          <div class="access-item access-user" @click="$router.push('/users')" v-if="isAdmin">
            <div class="access-icon-wrapper">
              <el-icon><UserFilled /></el-icon>
            </div>
            <span>用户管理</span>
          </div>
          <div class="access-item access-activity" @click="$router.push('/activities')">
            <div class="access-icon-wrapper">
              <el-icon><Histogram /></el-icon>
            </div>
            <span>活动记录</span>
          </div>
          <div class="access-item access-stats" @click="$router.push('/reports/bug-statistics')">
            <div class="access-icon-wrapper">
              <el-icon><PieChart /></el-icon>
            </div>
            <span>Bug统计</span>
          </div>
          <div class="access-item access-settings" @click="$router.push('/profile')">
            <div class="access-icon-wrapper">
              <el-icon><Setting /></el-icon>
            </div>
            <span>个人设置</span>
          </div>
          <div class="access-item access-system" @click="$router.push('/settings')" v-if="isAdmin">
            <div class="access-icon-wrapper">
              <el-icon><Tools /></el-icon>
            </div>
            <span>系统设置</span>
          </div>
          <div class="access-item access-attendance" @click="$router.push('/attendance/records')">
            <div class="access-icon-wrapper">
              <el-icon><Clock /></el-icon>
            </div>
            <span>考勤打卡</span>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 活动记录 -->
    <div class="activity-section">
      <el-row :gutter="20">
        <el-col :span="12" :xs="24" class="animate-fade-in-up delay-400">
          <el-card class="glass-card activity-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <div class="card-icon-wrapper card-icon-cyan">
                    <el-icon><Bell /></el-icon>
                  </div>
                  <span>我的活动记录</span>
                </div>
              </div>
            </template>
            <div class="activity-list">
              <div v-for="(activity, index) in activities" :key="activity.id" 
                   class="activity-item"
                   :style="{ animationDelay: `${index * 100}ms` }">
                <div class="activity-time">
                  <el-icon><Timer /></el-icon>
                  {{ formatTimeAgo(activity.time) }}
                </div>
                <div class="activity-content">
                  <span class="activity-user">{{ activity.user }}</span>
                  <span class="activity-action">{{ getActionText(activity.action) }}</span>
                  <el-link 
                    v-if="activity.target_type === 'bug' && activity.target_id" 
                    type="primary" 
                    @click="$router.push(`/bugs/${activity.target_id}`)"
                    class="activity-details"
                  >
                    {{ activity.details }}
                  </el-link>
                  <el-link 
                    v-else-if="activity.target_type === 'project' && activity.target_id" 
                    type="primary" 
                    @click="$router.push(`/projects/${activity.target_id}`)"
                    class="activity-details"
                  >
                    {{ activity.details }}
                  </el-link>
                  <el-link 
                    v-else-if="activity.target_type === 'work_log' && activity.target_id"
                    type="primary"
                    @click="$router.push(`/work-logs?highlight=${activity.target_id}`)"
                    class="activity-details"
                  >
                    {{ activity.details }}
                  </el-link>
                  <el-link 
                    v-else-if="activity.target_type === 'leave_application' && activity.target_id"
                    type="primary"
                    @click="$router.push(`/attendance/leave-application`)"
                    class="activity-details"
                  >
                    {{ activity.details }}
                  </el-link>
                  <el-link 
                    v-else-if="activity.target_type === 'overtime_application' && activity.target_id"
                    type="primary"
                    @click="$router.push(`/attendance/overtime-application`)"
                    class="activity-details"
                  >
                    {{ activity.details }}
                  </el-link>
                  <span v-else class="activity-details">{{ activity.details }}</span>
                </div>
              </div>
              <el-empty v-if="activities.length === 0" description="暂无活动记录" :image-size="60" />
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="12" :xs="24" class="animate-fade-in-up delay-500">
          <el-card class="stats-card glass-card" shadow="hover">
            <template #header>
              <div class="card-header stats-header">
                <div class="card-title">
                  <div class="card-icon-wrapper card-icon-green">
                    <el-icon><TrendCharts /></el-icon>
                  </div>
                  <span>工作统计概览</span>
                </div>
                <el-button type="primary" text @click="$router.push('/work-statistics')" class="view-more-btn">
                  查看详情 <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </template>
            <div class="stats-icon-grid">
              <div class="stat-icon-item stat-bug" @click="$router.push('/bugs?assignee=me&status=open,in_progress')">
                <div class="stat-icon-wrapper">
                  <el-icon><WarningFilled /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.summary?.my_bugs || 0 }}</div>
                  <div class="stat-desc">待修复Bug</div>
                </div>
                <div class="stat-glow"></div>
              </div>
              <div class="stat-icon-item stat-created" @click="$router.push('/bugs?creator=me')">
                <div class="stat-icon-wrapper">
                  <el-icon><CirclePlusFilled /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.summary?.bugs_created_by_me || 0 }}</div>
                  <div class="stat-desc">我创建的Bug</div>
                </div>
                <div class="stat-glow"></div>
              </div>
              <div class="stat-icon-item stat-new" @click="$router.push('/bugs?status=open')">
                <div class="stat-icon-wrapper">
                  <el-icon><InfoFilled /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.summary?.new_bugs || 0 }}</div>
                  <div class="stat-desc">新增Bug</div>
                </div>
                <div class="stat-glow"></div>
              </div>
              <div class="stat-icon-item stat-fixed" @click="$router.push('/bugs?status=closed,resolved')">
                <div class="stat-icon-wrapper">
                  <el-icon><CircleCheckFilled /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.summary?.fixed_bugs || 0 }}</div>
                  <div class="stat-desc">已修复Bug</div>
                </div>
                <div class="stat-glow"></div>
              </div>
              <div class="stat-icon-item stat-project" @click="$router.push('/projects')">
                <div class="stat-icon-wrapper">
                  <el-icon><FolderOpened /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.summary?.active_projects || 0 }}</div>
                  <div class="stat-desc">活跃项目</div>
                </div>
                <div class="stat-glow"></div>
              </div>
              <div class="stat-icon-item stat-rate">
                <div class="stat-icon-wrapper">
                  <el-icon><DataLine /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.summary?.my_completion_rate || 0 }}%</div>
                  <div class="stat-desc">完成率</div>
                </div>
                <div class="stat-glow"></div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 图表区域 -->
    <div class="charts-section animate-fade-in-up delay-600">
      <el-row :gutter="20">
        <el-col :span="8" :xs="24">
          <el-card class="chart-card glass-card" shadow="hover">
            <template #header>
              <div class="chart-header">
                <div class="chart-title">
                  <div class="chart-icon-wrapper chart-icon-purple">
                    <el-icon><PieChart /></el-icon>
                  </div>
                  <span>Bug严重程度分布</span>
                </div>
              </div>
            </template>
            <div ref="severityChart" class="chart-container"></div>
          </el-card>
        </el-col>
        
        <el-col :span="8" :xs="24">
          <el-card class="chart-card glass-card" shadow="hover">
            <template #header>
              <div class="chart-header">
                <div class="chart-title">
                  <div class="chart-icon-wrapper chart-icon-orange">
                    <el-icon><Histogram /></el-icon>
                  </div>
                  <span>Bug优先级分布</span>
                </div>
              </div>
            </template>
            <div ref="priorityChart" class="chart-container"></div>
          </el-card>
        </el-col>
        
        <el-col :span="8" :xs="24">
          <el-card class="chart-card glass-card" shadow="hover">
            <template #header>
              <div class="chart-header">
                <div class="chart-title">
                  <div class="chart-icon-wrapper chart-icon-blue">
                    <el-icon><TrendCharts /></el-icon>
                  </div>
                  <span>活动趋势</span>
                </div>
              </div>
            </template>
            <div ref="activityChart" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 最近Bug列表 -->
    <div class="recent-bugs animate-fade-in-up delay-700">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="recent-bugs-header">
            <div class="card-title">
              <div class="card-icon-wrapper card-icon-red">
                <el-icon><Warning /></el-icon>
              </div>
              <span>最近Bug</span>
            </div>
            <el-button type="primary" text @click="$router.push('/bugs')" class="view-more-btn">
              查看全部 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </template>
        
        <el-table :data="recentBugs" style="width: 100%" class="custom-table">
          <el-table-column prop="id" label="ID" width="80">
            <template #default="{ row }">
              <span class="bug-id">{{ row.id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="200">
            <template #default="{ row }">
              <router-link :to="`/bugs/${row.id}`" class="bug-title-link">
                {{ row.title }}
              </router-link>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small" effect="light" class="status-tag">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="severity" label="严重程度" width="100">
            <template #default="{ row }">
              <el-tag :type="getSeverityType(row.severity)" size="small" effect="light" class="severity-tag">
                {{ getSeverityText(row.severity) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              <span class="time-text">
                <el-icon><Clock /></el-icon> {{ formatDate(row.created_at) }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { 
  Document, List, DataLine, Notebook, User, OfficeBuilding, 
  Folder, ArrowRight, Grid, Promotion, Warning, FolderOpened, 
  UserFilled, Histogram, PieChart, Setting, Tools, Clock,
  Bell, Timer, TrendCharts, WarningFilled, CirclePlusFilled,
  InfoFilled, CircleCheckFilled, Monitor, Management, AlarmClock
} from '@element-plus/icons-vue'
import { formatDate } from '@/utils/dateUtils'
import { apiService } from '@/services/api'

const router = useRouter()
const userStore = useUserStore()

const currentUser = computed(() => userStore.currentUser)
const isAdmin = computed(() => {
  const user = currentUser.value
  if (!user) return false
  if (user.is_super_admin) return true
  return user.position === '管理员' || user.position?.includes('经理')
})
const isDepartmentManager = computed(() => {
  const user = currentUser.value
  if (!user) return false
  return user.position?.includes('经理') || user.position?.includes('主管')
})

const statistics = ref({})
const recentBugs = ref([])
const todoCount = ref(0)
const severityChart = ref(null)
const priorityChart = ref(null)
const activityChart = ref(null)

// 跳转到我的待办
const goToMyTasks = () => {
  router.push('/my-todos')
}

// 用户参与的项目数据
const userProjects = ref([])

// 获取用户参与的项目
const fetchUserProjects = async () => {
  try {
    const currentUser = userStore.currentUser
    if (!currentUser) {
      console.warn('用户未登录，无法获取项目列表')
      return
    }
    
    // 获取项目列表，API会自动根据当前用户权限返回相应的项目
    const response = await apiService.projects.getList()
    const projectsData = response.projects || []
    
    // 处理项目数据，提取项目名称和经理信息
    userProjects.value = projectsData.map(project => {
      // 从项目成员中查找项目经理的用户名
      let managerName = project.manager_name || '未知'
      
      // 如果没有 manager_name 字段，尝试从成员中查找
      if (managerName === '未知' && project.members && Array.isArray(project.members)) {
        const managerMember = project.members.find(member => member.position === '项目经理' || member.position?.includes('经理'))
        if (managerMember && managerMember.username) {
          managerName = managerMember.username
        } else if (project.manager_id) {
          // 如果有 manager_id 但没有找到对应的成员信息，显示用户 ID
          managerName = `用户${project.manager_id}`
        }
      }
      
      return {
        id: project.id,
        name: project.name,
        manager: managerName
      }
    })
    
    console.log('用户参与的项目:', userProjects.value)
  } catch (error) {
    console.error('获取用户参与的项目失败:', error)
    // 如果获取失败，显示空列表而不是硬编码数据
    userProjects.value = []
  }
}

// 活动记录数据
const activities = ref([])

// 格式化相对时间
const formatTimeAgo = (timeString) => {
  if (!timeString) return ''
  const date = new Date(timeString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`
  return formatDate(timeString)
}

// 获取我的活动记录
const fetchMyActivities = async () => {
  try {
    const currentUser = userStore.currentUser
    if (!currentUser) {
      console.warn('用户未登录，无法获取活动记录')
      return
    }

    const response = await apiService.users.getUserHome(currentUser.id)
    if (response && response.activities) {
      activities.value = response.activities.map(activity => {
        // 处理标题显示：将英文类型转换为中文
        let details = activity.resource_name || activity.description
        if (details) {
          // 将各种英文类型替换为中文
          details = details.replace(/^work_log/i, '工作日志')
          details = details.replace(/^overtime_application/i, '加班申请')
          details = details.replace(/^leave_application/i, '请假申请')
        }
        return {
          id: activity.id,
          time: activity.created_at,
          user: currentUser.username,
          action: activity.action,
          details: details,
          target_type: activity.target_type,
          target_id: activity.target_id
        }
      })
    }
  } catch (error) {
    console.error('获取活动记录失败:', error)
  }
}

let severityChartInstance = null
let priorityChartInstance = null
let activityChartInstance = null

// 获取统计信息
const fetchStatistics = async () => {
  try {
    console.log('开始获取统计信息...')
    const response = await apiService.statistics.getDashboardData()
    console.log('获取统计信息响应:', response)
    // API响应拦截器已经返回了response.data，所以直接使用response
    statistics.value = response
    console.log('统计信息数据:', statistics.value)
  } catch (error) {
    console.error('获取统计信息失败:', error)
    ElMessage.error(`获取统计信息失败: ${error.message || '未知错误'}`)
  }
}

// 获取最近Bug（只显示当前用户参与的Bug：创建者、验证者、解决者、分配给）
const fetchRecentBugs = async () => {
  try {
    const currentUser = userStore.currentUser
    if (!currentUser) {
      console.warn('用户未登录，无法获取最近Bug')
      recentBugs.value = []
      return
    }

    const response = await apiService.bugs.getList({
      page: 1,
      per_page: 5,
      sort: 'created_at',
      order: 'desc',
      user_id: currentUser.id
    })
    // API响应拦截器已经返回了response.data，所以直接使用response.bugs
    recentBugs.value = response.bugs || []
  } catch (error) {
    console.error('获取最近Bug失败:', error)
    recentBugs.value = []
  }
}

// 获取待办事项数量
const fetchTodoCount = async () => {
  try {
    const response = await apiService.todos.getSummary()
    const summary = response || {}
    todoCount.value = (summary.approvals?.total || 0) +
      (summary.bugs?.total || 0) +
      (summary.reviews?.total || 0) +
      (summary.contracts?.total || 0)
  } catch (error) {
    console.error('获取待办数量失败:', error)
    todoCount.value = 0
  }
}

// 初始化图表
const initCharts = () => {
  const severityEl = severityChart.value
  const priorityEl = priorityChart.value
  const activityEl = activityChart.value
  
  if (severityEl && severityEl.clientWidth > 0 && severityEl.clientHeight > 0) {
    severityChartInstance = echarts.init(severityEl)
  }
  if (priorityEl && priorityEl.clientWidth > 0 && priorityEl.clientHeight > 0) {
    priorityChartInstance = echarts.init(priorityEl)
  }
  if (activityEl && activityEl.clientWidth > 0 && activityEl.clientHeight > 0) {
    activityChartInstance = echarts.init(activityEl)
  }
  
  if (severityChartInstance || priorityChartInstance || activityChartInstance) {
    updateCharts()
  }
}

// 更新图表
const updateCharts = () => {
  if (severityChartInstance) {
    const severityOption = {
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#e2e8f0',
        borderWidth: 1,
        textStyle: { color: '#1e293b' },
        padding: [12, 16],
        extraCssText: 'box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); border-radius: 12px;'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        textStyle: { color: '#64748b', fontSize: 11 },
        itemGap: 10
      },
      series: [
        {
          name: '严重程度',
          type: 'pie',
          radius: ['45%', '75%'],
          center: ['60%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 3
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 16,
              fontWeight: 'bold',
              color: '#1e293b'
            },
            itemStyle: {
              shadowBlur: 20,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.15)'
            }
          },
          labelLine: { show: false },
          data: [
            { value: statistics.value.severity_distribution?.low || 0, name: '低', itemStyle: { color: '#22c55e' } },
            { value: statistics.value.severity_distribution?.medium || 0, name: '中', itemStyle: { color: '#3b82f6' } },
            { value: statistics.value.severity_distribution?.high || 0, name: '高', itemStyle: { color: '#f59e0b' } },
            { value: statistics.value.severity_distribution?.critical || 0, name: '严重', itemStyle: { color: '#ef4444' } }
          ]
        }
      ]
    }
    severityChartInstance.setOption(severityOption)
  }
  
  if (priorityChartInstance) {
    const priorityOption = {
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#e2e8f0',
        borderWidth: 1,
        textStyle: { color: '#1e293b' },
        padding: [12, 16],
        extraCssText: 'box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); border-radius: 12px;'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '8%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['低', '中', '高'],
        axisLine: { lineStyle: { color: '#e2e8f0' } },
        axisLabel: { color: '#64748b', fontSize: 12 },
        axisTick: { show: false }
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
        axisLabel: { color: '#64748b', fontSize: 11 }
      },
      series: [
        {
          data: [
            statistics.value.priority_distribution?.low || 0,
            statistics.value.priority_distribution?.medium || 0,
            statistics.value.priority_distribution?.high || 0
          ],
          type: 'bar',
          barWidth: '50%',
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#5b6df5' },
              { offset: 1, color: '#0284c7' }
            ]),
            borderRadius: [8, 8, 0, 0]
          }
        }
      ]
    }
    priorityChartInstance.setOption(priorityOption)
  }
  
  if (activityChartInstance) {
    const activityOption = {
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#e2e8f0',
        borderWidth: 1,
        textStyle: { color: '#1e293b' },
        padding: [12, 16],
        extraCssText: 'box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); border-radius: 12px;'
      },
      legend: {
        data: ['缺陷活动'],
        textStyle: { color: '#64748b', fontSize: 11 }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '8%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: statistics.value.activity_chart?.dates || [],
        axisLine: { lineStyle: { color: '#e2e8f0' } },
        axisLabel: { color: '#64748b', fontSize: 11 },
        axisTick: { show: false }
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
        axisLabel: { color: '#64748b', fontSize: 11 }
      },
      series: [
        {
          name: '缺陷活动',
          type: 'line',
          data: statistics.value.activity_chart?.bug_activity || [],
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: {
            color: '#f59e0b',
            width: 3,
            shadowColor: 'rgba(245, 158, 11, 0.3)',
            shadowBlur: 10
          },
          itemStyle: {
            color: '#f59e0b',
            borderWidth: 2,
            borderColor: '#fff'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(245, 158, 11, 0.3)' },
              { offset: 1, color: 'rgba(245, 158, 11, 0.02)' }
            ])
          }
        }
      ]
    }
    activityChartInstance.setOption(activityOption)
  }
}

// 状态类型映射
const getStatusType = (status) => {
  const typeMap = {
    'open': 'danger',
    'in_progress': 'warning',
    'closed': 'success'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'open': '打开',
    'in_progress': '进行中',
    'closed': '已关闭'
  }
  return textMap[status] || status
}

// 严重程度类型映射
const getSeverityType = (severity) => {
  const typeMap = {
    'low': 'success',
    'medium': 'info',
    'high': 'warning',
    'critical': 'danger',
    'Low': 'success',
    'Medium': 'info',
    'High': 'warning',
    'Critical': 'danger'
  }
  return typeMap[severity] || 'info'
}

const getSeverityText = (severity) => {
  const textMap = {
    'low': '低',
    'medium': '中',
    'high': '高',
    'critical': '严重',
    'Low': '低',
    'Medium': '中',
    'High': '高',
    'Critical': '严重'
  }
  return textMap[severity] || severity
}

// 响应式调整图表大小
const handleResize = () => {
  if (severityChartInstance) {
    severityChartInstance.resize()
  }
  if (priorityChartInstance) {
    priorityChartInstance.resize()
  }
  if (activityChartInstance) {
    activityChartInstance.resize()
  }
}

onMounted(async () => {
  await Promise.all([
    fetchStatistics(),
    fetchRecentBugs(),
    fetchUserProjects(),
    fetchMyActivities(),
    fetchTodoCount()
  ])
  
  await nextTick()
  setTimeout(() => {
    initCharts()
  }, 100)
  
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (severityChartInstance) {
    severityChartInstance.dispose()
  }
  if (priorityChartInstance) {
    priorityChartInstance.dispose()
  }
  if (activityChartInstance) {
    activityChartInstance.dispose()
  }
})

// 监听统计数据变化，更新图表
watch(statistics, () => {
  updateCharts()
}, { deep: true })

// 获取操作类型文本
const getActionText = (action) => {
  const texts = {
    'create': '创建',
    'create_bug': '创建Bug',
    'create_work_log': '创建工作日志',
    'create_leave_application': '创建请假申请',
    'apply_leave': '提交请假',
    'apply_overtime': '提交加班',
    'update': '更新',
    'update_bug': '更新Bug',
    'update_work_log': '更新工作日志',
    'delete': '删除',
    'delete_work_log': '删除工作日志',
    'status_change': '状态变更',
    'bug_status_update': 'Bug状态更新',
    'bug_status_transition': 'Bug状态转换',
    'assign': '分配',
    'assign_bug': '分配Bug',
    'approve': '审批',
    'approve_leave_application': '审批请假',
    'approve_overtime_application': '审批加班',
    'approve_exception': '审批异常',
    'clock_in': '上班打卡',
    'clock_out': '下班打卡',
    'upload_attachment': '上传附件',
    'delete_attachment': '删除附件'
  }
  return texts[action] || action
}
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.dashboard {
  padding: 24px;
  background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 50%, #eef1f5 100%);
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.bg-gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  animation: float-slow 20s ease-in-out infinite;
}

.orb-1 {
  width: 600px;
  height: 600px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.3) 0%, rgba(14, 165, 233, 0.2) 100%);
  top: -200px;
  right: -100px;
  animation-delay: 0s;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(14, 165, 233, 0.15) 100%);
  bottom: 10%;
  left: -100px;
  animation-delay: -5s;
}

.orb-3 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(249, 112, 102, 0.15) 100%);
  top: 40%;
  right: 10%;
  animation-delay: -10s;
}

@keyframes float-slow {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(2deg); }
}

/* 头部样式 */
.dashboard-header {
  margin-bottom: 24px;
  padding: 28px 32px;
  background: linear-gradient(135deg, #bae6fd 0%, #7dd3fc 50%, #38bdf8 100%);
  border-radius: 20px;
  color: #0c4a6e;
  position: relative;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(56, 189, 248, 0.35);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 1;
}

.dashboard-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at 30% 20%, rgba(255, 255, 255, 0.4) 0%, transparent 50%),
              radial-gradient(ellipse at 70% 80%, rgba(56, 189, 248, 0.4) 0%, transparent 50%);
  pointer-events: none;
}

.dashboard-header::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.08'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.5;
  pointer-events: none;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
  z-index: 1;
}

.header-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(14, 165, 233, 0.3);
}

.header-icon .el-icon {
  font-size: 32px;
  color: #ffffff;
}

.header-text h2 {
  margin: 0 0 6px 0;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #0c4a6e;
  -webkit-text-fill-color: #0c4a6e;
}

.header-text p {
  margin: 0;
  font-size: 14px;
  color: #075985;
  opacity: 0.85;
  font-weight: 500;
}

.header-stats {
  display: flex;
  align-items: center;
  gap: 24px;
  position: relative;
  z-index: 1;
}

.header-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.header-stat-value {
  font-size: 28px;
  font-weight: 800;
  color: #0c4a6e;
  -webkit-text-fill-color: #0c4a6e;
}

.header-stat-label {
  font-size: 12px;
  color: #075985;
  opacity: 0.8;
  font-weight: 500;
}

.header-stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(14, 165, 233, 0.4);
}

/* 玻璃拟态卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.08);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
  box-shadow: 0 12px 48px rgba(31, 38, 135, 0.12);
  border-color: rgba(255, 255, 255, 0.8);
  transform: translateY(-4px);
}

.organization-section {
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 700;
  color: #1e293b;
  font-size: 16px;
}

.card-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-icon-wrapper .el-icon {
  font-size: 20px;
}

.card-icon-blue {
  background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 100%);
  color: #2563eb;
}

.card-icon-purple {
  background: linear-gradient(135deg, #f3e8ff 0%, #d8b4fe 100%);
  color: #0284c7;
}

.card-icon-orange {
  background: linear-gradient(135deg, #ffedd5 0%, #fed7aa 100%);
  color: #ea580c;
}

.card-icon-cyan {
  background: linear-gradient(135deg, #ccfbf1 0%, #99f6e4 100%);
  color: #0d9488;
}

.card-icon-green {
  background: linear-gradient(135deg, #d1fae5 0%, #6ee7b7 100%);
  color: #059669;
}

.card-icon-red {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
}

.org-card, .stats-card, .activity-card {
  height: 100%;
}

.project-card {
  display: flex;
  flex-direction: column;
}

.project-card :deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.org-content {
  flex: 1;
  overflow-y: auto;
  max-height: 280px;
  padding: 8px 0;
}

.nav-card {
  display: flex;
  flex-direction: column;
}

.nav-card :deep(.el-card__body) {
  flex: 1;
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.view-more-btn {
  transition: all 0.3s ease;
}

.view-more-btn:hover {
  transform: translateX(4px);
}

/* 项目列表项 */
.org-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 14px;
  border-radius: 14px;
  background: rgba(241, 245, 249, 0.6);
  transition: all 0.3s ease;
  cursor: pointer;
  animation: fadeInUp 0.5s ease-out both;
  border: 1px solid transparent;
}

.org-item:hover {
  background: white;
  transform: translateX(6px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  border-color: rgba(56, 189, 248, 0.15);
}

.org-item:last-child {
  margin-bottom: 0;
}

.project-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.project-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #5b6df5 0%, #0284c7 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
}

.project-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.project-name {
  color: #1e293b;
  font-weight: 600;
  font-size: 14px;
}

.project-manager {
  color: #64748b;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.project-manager .el-icon {
  font-size: 12px;
}

.project-link {
  opacity: 0;
  transition: all 0.3s ease;
}

.org-item:hover .project-link {
  opacity: 1;
}

/* 导航网格 */
.navigation-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  max-height: 280px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 4px;
}

.navigation-grid::-webkit-scrollbar {
  width: 6px;
}

.navigation-grid::-webkit-scrollbar-track {
  background: rgba(241, 245, 249, 0.6);
  border-radius: 3px;
}

.navigation-grid::-webkit-scrollbar-thumb {
  background: rgba(91, 109, 245, 0.3);
  border-radius: 3px;
}

.navigation-grid::-webkit-scrollbar-thumb:hover {
  background: rgba(91, 109, 245, 0.5);
}

.nav-item {
  padding: 20px 10px;
  text-align: center;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  position: relative;
  border: 1px solid transparent;
}

.nav-item:hover {
  background: white;
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
  border-color: rgba(56, 189, 248, 0.15);
}

.nav-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.nav-icon-wrapper .el-icon {
  font-size: 24px;
}

.nav-icon-todo {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 12px rgba(217, 119, 6, 0.2);
}

.nav-icon-plan {
  background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 100%);
  color: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.nav-icon-activity {
  background: linear-gradient(135deg, #fce7f3 0%, #f9a8d4 100%);
  color: #db2777;
  box-shadow: 0 4px 12px rgba(219, 39, 119, 0.2);
}

.nav-icon-log {
  background: linear-gradient(135deg, #d1fae5 0%, #6ee7b7 100%);
  color: #059669;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.2);
}

.nav-icon-team {
  background: linear-gradient(135deg, #e0e7ff 0%, #a5b4fc 100%);
  color: #0284c7;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
}

.nav-icon-dept {
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  color: #0284c7;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2);
}

.nav-icon-attendance {
  background: linear-gradient(135deg, #ffedd5 0%, #fdba74 100%);
  color: #ea580c;
  box-shadow: 0 4px 12px rgba(234, 88, 12, 0.2);
}

.nav-icon-profile {
  background: linear-gradient(135deg, #ccfbf1 0%, #5eead4 100%);
  color: #0d9488;
  box-shadow: 0 4px 12px rgba(13, 148, 136, 0.2);
}

.nav-item:hover .nav-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.nav-item .nav-text {
  font-size: 13px;
  color: #475569;
  font-weight: 600;
}

.nav-item:hover .nav-text {
  color: #5b6df5;
}

.todo-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  color: white;
  font-size: 10px;
  font-weight: 700;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.35);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* 快速入口 */
.quick-access-section {
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

.quick-access-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.access-item {
  padding: 24px 14px;
  text-align: center;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  border: 1px solid transparent;
}

.access-item:hover {
  background: white;
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.1);
  border-color: rgba(56, 189, 248, 0.15);
}

.access-icon-wrapper {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.access-icon-wrapper .el-icon {
  font-size: 26px;
}

.access-bug .access-icon-wrapper {
  background: linear-gradient(135deg, #fef3c7 0%, #fbbf24 100%);
  color: #b45309;
  box-shadow: 0 4px 16px rgba(251, 191, 36, 0.25);
}

.access-project .access-icon-wrapper {
  background: linear-gradient(135deg, #dbeafe 0%, #60a5fa 100%);
  color: #1d4ed8;
  box-shadow: 0 4px 16px rgba(96, 165, 250, 0.25);
}

.access-user .access-icon-wrapper {
  background: linear-gradient(135deg, #fce7f3 0%, #f472b6 100%);
  color: #be185d;
  box-shadow: 0 4px 16px rgba(244, 114, 182, 0.25);
}

.access-activity .access-icon-wrapper {
  background: linear-gradient(135deg, #f3e8ff 0%, #c084fc 100%);
  color: #0284c7;
  box-shadow: 0 4px 16px rgba(192, 132, 252, 0.25);
}

.access-stats .access-icon-wrapper {
  background: linear-gradient(135deg, #ccfbf1 0%, #2dd4bf 100%);
  color: #0f766e;
  box-shadow: 0 4px 16px rgba(45, 212, 191, 0.25);
}

.access-settings .access-icon-wrapper {
  background: linear-gradient(135deg, #e0e7ff 0%, #818cf8 100%);
  color: #0369a1;
  box-shadow: 0 4px 16px rgba(129, 140, 248, 0.25);
}

.access-system .access-icon-wrapper {
  background: linear-gradient(135deg, #fee2e2 0%, #f87171 100%);
  color: #b91c1c;
  box-shadow: 0 4px 16px rgba(248, 113, 113, 0.25);
}

.access-attendance .access-icon-wrapper {
  background: linear-gradient(135deg, #d1fae5 0%, #34d399 100%);
  color: #047857;
  box-shadow: 0 4px 16px rgba(52, 211, 153, 0.25);
}

.access-item:hover .access-icon-wrapper {
  transform: scale(1.1) rotate(-5deg);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.access-item span {
  font-size: 14px;
  color: #475569;
  font-weight: 600;
}

.access-item:hover span {
  color: #1e293b;
}

/* 活动区域 */
.activity-section {
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

.activity-list {
  max-height: 320px;
  overflow-y: auto;
}

.activity-item {
  padding: 16px 0;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
  animation: fadeInUp 0.5s ease-out both;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-time {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.activity-time .el-icon {
  font-size: 12px;
}

.activity-content {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.activity-user {
  color: #5b6df5;
  font-weight: 700;
  font-size: 14px;
}

.activity-action {
  color: #22c55e;
  font-size: 12px;
  font-weight: 600;
  background: rgba(34, 197, 94, 0.1);
  padding: 4px 10px;
  border-radius: 8px;
}

.activity-details {
  flex: 1;
  color: #475569;
  font-size: 13px;
  font-weight: 500;
}

/* 统计图标网格 */
.stats-icon-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 10px;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  border: 1px solid transparent;
}

.stat-icon-item:hover {
  background: white;
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
  border-color: rgba(56, 189, 248, 0.15);
}

.stat-icon-item:hover .stat-glow {
  opacity: 1;
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.stat-icon-wrapper .el-icon {
  font-size: 24px;
}

.stat-bug .stat-icon-wrapper {
  background: linear-gradient(135deg, #fef3c7 0%, #fbbf24 100%);
  color: #b45309;
  box-shadow: 0 4px 12px rgba(251, 191, 36, 0.25);
}

.stat-created .stat-icon-wrapper {
  background: linear-gradient(135deg, #d1fae5 0%, #34d399 100%);
  color: #047857;
  box-shadow: 0 4px 12px rgba(52, 211, 153, 0.25);
}

.stat-new .stat-icon-wrapper {
  background: linear-gradient(135deg, #fce7f3 0%, #f472b6 100%);
  color: #be185d;
  box-shadow: 0 4px 12px rgba(244, 114, 182, 0.25);
}

.stat-fixed .stat-icon-wrapper {
  background: linear-gradient(135deg, #dbeafe 0%, #60a5fa 100%);
  color: #1d4ed8;
  box-shadow: 0 4px 12px rgba(96, 165, 250, 0.25);
}

.stat-project .stat-icon-wrapper {
  background: linear-gradient(135deg, #f3e8ff 0%, #c084fc 100%);
  color: #0284c7;
  box-shadow: 0 4px 12px rgba(192, 132, 252, 0.25);
}

.stat-rate .stat-icon-wrapper {
  background: linear-gradient(135deg, #ccfbf1 0%, #2dd4bf 100%);
  color: #0f766e;
  box-shadow: 0 4px 12px rgba(45, 212, 191, 0.25);
}

.stat-icon-item:hover .stat-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.stat-info {
  text-align: center;
  position: relative;
  z-index: 1;
}

.stat-number {
  font-size: 22px;
  font-weight: 800;
  background: linear-gradient(135deg, #5b6df5 0%, #0284c7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
}

.stat-desc {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
  font-weight: 500;
}

.stat-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.12) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
}

/* 图表区域 */
.charts-section {
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

.chart-card {
  height: 100%;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.chart-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(31, 38, 135, 0.12);
}

.chart-card :deep(.el-card__body) {
  padding: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 700;
  color: #1e293b;
  font-size: 15px;
}

.chart-icon-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-icon-wrapper .el-icon {
  font-size: 18px;
}

.chart-icon-purple {
  background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%);
  color: #0284c7;
  box-shadow: 0 4px 10px rgba(14, 165, 233, 0.2);
}

.chart-icon-orange {
  background: linear-gradient(135deg, #ffedd5 0%, #fed7aa 100%);
  color: #ea580c;
  box-shadow: 0 4px 10px rgba(234, 88, 12, 0.2);
}

.chart-icon-blue {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #2563eb;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
}

.chart-container {
  height: 260px;
  width: 100%;
}

/* 最近Bug */
.recent-bugs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recent-bugs {
  position: relative;
  z-index: 1;
}

.bug-id {
  font-family: 'Monaco', 'Menlo', 'SF Mono', monospace;
  font-size: 12px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 8px;
  font-weight: 500;
}

.bug-title-link {
  color: #5b6df5;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.bug-title-link:hover {
  color: #0284c7;
  text-decoration: underline;
}

.status-tag, .severity-tag {
  font-weight: 600;
  border-radius: 8px;
}

.time-text {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #64748b;
  font-size: 13px;
}

.time-text .el-icon {
  font-size: 13px;
}

/* 自定义表格 */
.custom-table :deep(.el-table__header) {
  background: rgba(241, 245, 249, 0.5);
}

.custom-table :deep(.el-table__row) {
  transition: all 0.3s ease;
}

.custom-table :deep(.el-table__row:hover) {
  background: rgba(56, 189, 248, 0.04);
}

/* 动画 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-down {
  animation: fadeInDown 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.animate-fade-in-up {
  animation: fadeInUp 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  animation-fill-mode: both;
}

.delay-100 { animation-delay: 100ms; }
.delay-200 { animation-delay: 200ms; }
.delay-300 { animation-delay: 300ms; }
.delay-400 { animation-delay: 400ms; }
.delay-500 { animation-delay: 500ms; }
.delay-600 { animation-delay: 600ms; }
.delay-700 { animation-delay: 700ms; }

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }

  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
    padding: 20px;
  }

  .header-content {
    gap: 16px;
  }

  .header-icon {
    width: 52px;
    height: 52px;
  }

  .header-icon .el-icon {
    font-size: 24px;
  }

  .header-text h2 {
    font-size: 22px;
  }

  .header-text p {
    font-size: 13px;
  }

  .header-stats {
    width: 100%;
    justify-content: flex-start;
    gap: 20px;
  }

  .organization-section {
    margin-bottom: 16px;
  }

  .org-content {
    max-height: 200px;
  }

  .navigation-grid {
    gap: 12px;
    max-height: 240px;
  }

  .nav-item {
    padding: 16px 8px;
  }

  .nav-icon-wrapper {
    width: 40px;
    height: 40px;
  }

  .nav-icon-wrapper .el-icon {
    font-size: 20px;
  }

  .nav-item .nav-text {
    font-size: 11px;
  }

  .quick-access-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .access-item {
    padding: 18px 10px;
  }

  .access-icon-wrapper {
    width: 44px;
    height: 44px;
  }

  .access-icon-wrapper .el-icon {
    font-size: 22px;
  }

  .access-item span {
    font-size: 13px;
  }

  .stats-icon-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .stat-icon-item {
    padding: 16px 8px;
  }

  .stat-icon-wrapper {
    width: 40px;
    height: 40px;
  }

  .stat-icon-wrapper .el-icon {
    font-size: 20px;
  }

  .stat-number {
    font-size: 20px;
  }

  .stat-desc {
    font-size: 11px;
  }

  .chart-container {
    height: 220px;
  }

  .activity-list {
    max-height: 280px;
  }

  .activity-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .bg-gradient-orb {
    filter: blur(60px);
    opacity: 0.3;
  }
}

@media screen and (max-width: 480px) {
  .navigation-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .quick-access-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-icon-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .header-stats {
    flex-wrap: wrap;
  }
}
</style>
