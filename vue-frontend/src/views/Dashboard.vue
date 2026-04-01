<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h2>TOPO系统 - 个人工作台</h2>
      <p>组织架构管理与工作协同平台</p>
    </div>
    
    <!-- 个人参与的项目和工作统计 -->
    <div class="organization-section">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="org-card project-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>个人参与的项目</span>
              </div>
            </template>
            <div class="org-content">
              <div v-for="project in userProjects" :key="project.id" class="org-item">
                <el-button type="primary" link @click="$router.push(`/projects/${project.id}`)">
                  {{ project.name }}
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card class="nav-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>功能导航</span>
              </div>
            </template>
            <div class="navigation-grid">
              <div class="nav-item" @click="goToMyTasks">
                <el-icon><Document /></el-icon>
                <span class="nav-text">待办事项</span>
                <span v-if="todoCount > 0" class="todo-badge">{{ todoCount > 99 ? '99+' : todoCount }}</span>
              </div>
              <div class="nav-item" @click="$router.push('/tasks')">
                <el-icon><List /></el-icon>
                <span class="nav-text">工作计划</span>
              </div>
              <div class="nav-item" @click="$router.push('/activities')">
                <el-icon><DataLine /></el-icon>
                <span class="nav-text">活动记录</span>
              </div>
              <div class="nav-item" @click="$router.push('/work-logs')">
                <el-icon><Notebook /></el-icon>
                <span class="nav-text">我的日志</span>
              </div>
              <div v-if="isDepartmentManager" class="nav-item" @click="$router.push('/work-logs?view=all')">
                <el-icon><Notebook /></el-icon>
                <span class="nav-text">员工日志</span>
              </div>
              <div class="nav-item" @click="$router.push('/my-department')">
                <el-icon><OfficeBuilding /></el-icon>
                <span class="nav-text">我的部门</span>
              </div>
              <div class="nav-item" @click="$router.push('/profile')">
                <el-icon><User /></el-icon>
                <span class="nav-text">帐号</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 项目进度概览 -->
    <div class="project-progress-section">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>项目进度概览</span>
          </div>
        </template>
        <div class="project-progress-grid">
          <div v-for="project in statistics.project_progress || []" :key="project.id" class="project-item">
            <div class="project-name">
              <el-button type="primary" link @click="$router.push(`/projects/${project.id}`)">
                {{ project.name }}
              </el-button>
            </div>
            <div class="project-status">
              <el-tag :type="project.status === 'active' ? 'success' : 'warning'">
                {{ project.status === 'active' ? '活跃' : '进行中' }}
              </el-tag>
            </div>
            <div class="project-progress">
              <el-progress 
                :percentage="project.progress || 0" 
                :stroke-width="8"
                :color="project.progress >= 80 ? '#67C23A' : project.progress >= 50 ? '#E6A23C' : '#F56C6C'"
              />
            </div>
            <div class="project-percentage">{{ project.progress || 0 }}%</div>
          </div>
          <div v-if="!statistics.project_progress || statistics.project_progress.length === 0" class="no-projects">
            暂无项目数据
          </div>
        </div>
      </el-card>
    </div>

    <!-- 快速入口 -->
    <div class="quick-access-section">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>快速入口</span>
          </div>
        </template>
        <div class="quick-access-grid">
          <div class="access-item" @click="$router.push('/tasks')">
            <i class="el-icon-s-order"></i>
            <span>任务管理</span>
          </div>
          <div class="access-item" @click="$router.push('/bugs')">
            <i class="el-icon-warning-outline"></i>
            <span>缺陷管理</span>
          </div>
          <div class="access-item" @click="$router.push('/projects')">
            <i class="el-icon-s-management"></i>
            <span>项目管理</span>
          </div>
          <div class="access-item" @click="$router.push('/users')" v-if="isAdmin">
            <i class="el-icon-user"></i>
            <span>用户管理</span>
          </div>
          <div class="access-item" @click="$router.push('/activities')">
            <i class="el-icon-s-data"></i>
            <span>活动记录</span>
          </div>
          <div class="access-item" @click="$router.push('/reports/bug-statistics')">
            <i class="el-icon-pie-chart"></i>
            <span>Bug统计</span>
          </div>
          <div class="access-item" @click="$router.push('/profile')">
            <i class="el-icon-setting"></i>
            <span>个人设置</span>
          </div>
          <div class="access-item" @click="$router.push('/settings')" v-if="isAdmin">
            <i class="el-icon-tools"></i>
            <span>系统设置</span>
          </div>
          <div class="access-item" @click="$router.push('/attendance/records')">
            <i class="el-icon-time"></i>
            <span>考勤打卡</span>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 活动记录 -->
    <div class="activity-section">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>我的活动记录</span>
              </div>
            </template>
            <div class="activity-list">
              <div v-for="activity in activities" :key="activity.id" class="activity-item">
                <div class="activity-time">{{ activity.time }}</div>
                <div class="activity-content">
                  <span class="activity-user">{{ activity.user }}</span>
                  <span class="activity-action">{{ activity.action }}</span>
                  <el-link 
                    v-if="activity.target_type === 'task' && activity.target_id" 
                    type="primary" 
                    @click="$router.push(`/tasks/${activity.target_id}`)"
                    style="cursor: pointer;"
                    class="activity-details"
                  >
                    {{ activity.details }}
                  </el-link>
                  <el-link 
                    v-else-if="activity.target_type === 'bug' && activity.target_id" 
                    type="primary" 
                    @click="$router.push(`/bugs/${activity.target_id}`)"
                    style="cursor: pointer;"
                    class="activity-details"
                  >
                    {{ activity.details }}
                  </el-link>
                  <el-link 
                    v-else-if="activity.target_type === 'project' && activity.target_id" 
                    type="primary" 
                    @click="$router.push(`/projects/${activity.target_id}`)"
                    style="cursor: pointer;"
                    class="activity-details"
                  >
                    {{ activity.details }}
                  </el-link>
                  <span v-else class="activity-details">{{ activity.details }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card class="stats-card" shadow="hover">
            <template #header>
              <div class="card-header stats-header">
                <span>工作统计概览</span>
                <el-button type="primary" text @click="$router.push('/work-statistics')">
                  查看详情 &gt;
                </el-button>
              </div>
            </template>
            <div class="stats-icon-grid">
              <div class="stat-icon-item" @click="$router.push('/tasks')">
                <div class="stat-icon-wrapper" style="background: #E3F2FD;">
                  <i class="el-icon-s-order stat-icon" style="color: #2196F3;"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.summary?.my_tasks || 0 }}</div>
                  <div class="stat-desc">我的任务</div>
                </div>
              </div>
              <div class="stat-icon-item" @click="$router.push('/tasks?status=overdue')">
                <div class="stat-icon-wrapper" style="background: #FFEBEE;">
                  <i class="el-icon-warning-outline stat-icon" style="color: #F44336;"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.summary?.overdue_tasks || 0 }}</div>
                  <div class="stat-desc">逾期任务</div>
                </div>
              </div>
              <div class="stat-icon-item" @click="$router.push('/bugs?assignee=me&status=open,in_progress')">
                <div class="stat-icon-wrapper" style="background: #FFF3E0;">
                  <i class="el-icon-bug stat-icon" style="color: #FF9800;"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.summary?.my_bugs || 0 }}</div>
                  <div class="stat-desc">待修复Bug</div>
                </div>
              </div>
              <div class="stat-icon-item" @click="$router.push('/bugs?creator=me')">
                <div class="stat-icon-wrapper" style="background: #E8F5E9;">
                  <i class="el-icon-circle-plus stat-icon" style="color: #4CAF50;"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.summary?.bugs_created_by_me || 0 }}</div>
                  <div class="stat-desc">我创建的Bug</div>
                </div>
              </div>
              <div class="stat-icon-item" @click="$router.push('/bugs?status=open')">
                <div class="stat-icon-wrapper" style="background: #F3E5F5;">
                  <i class="el-icon-info stat-icon" style="color: #9C27B0;"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.summary?.new_bugs || 0 }}</div>
                  <div class="stat-desc">新增Bug</div>
                </div>
              </div>
              <div class="stat-icon-item" @click="$router.push('/bugs?status=closed,resolved')">
                <div class="stat-icon-wrapper" style="background: #E0F7FA;">
                  <i class="el-icon-circle-check stat-icon" style="color: #00BCD4;"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.summary?.fixed_bugs || 0 }}</div>
                  <div class="stat-desc">已修复Bug</div>
                </div>
              </div>
              <div class="stat-icon-item" @click="$router.push('/projects')">
                <div class="stat-icon-wrapper" style="background: #FBE9E7;">
                  <i class="el-icon-folder-opened stat-icon" style="color: #FF5722;"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.summary?.active_projects || 0 }}</div>
                  <div class="stat-desc">活跃项目</div>
                </div>
              </div>
              <div class="stat-icon-item">
                <div class="stat-icon-wrapper" style="background: #EDE7F6;">
                  <i class="el-icon-data-line stat-icon" style="color: #673AB7;"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.summary?.my_completion_rate || 0 }}%</div>
                  <div class="stat-desc">完成率</div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 图表区域 -->
    <div class="charts-section">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="chart-header">
                <span>Bug严重程度分布</span>
              </div>
            </template>
            <div ref="severityChart" class="chart-container"></div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="chart-header">
                <span>Bug优先级分布</span>
              </div>
            </template>
            <div ref="priorityChart" class="chart-container"></div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="chart-header">
                <span>活动趋势</span>
              </div>
            </template>
            <div ref="activityChart" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 最近Bug列表 -->
    <div class="recent-bugs">
      <el-card shadow="hover">
        <template #header>
          <div class="recent-bugs-header">
            <span>最近Bug</span>
            <el-button type="primary" text @click="$router.push('/bugs')">查看全部</el-button>
          </div>
        </template>
        
        <el-table :data="recentBugs" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="title" label="标题" min-width="200">
            <template #default="{ row }">
              <router-link :to="`/bugs/${row.id}`" class="bug-title-link">
                {{ row.title }}
              </router-link>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="severity" label="严重程度" width="100">
            <template #default="{ row }">
              <el-tag :type="getSeverityType(row.severity)" size="small">
                {{ getSeverityText(row.severity) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Document, List, DataLine, Notebook, User, OfficeBuilding } from '@element-plus/icons-vue'
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
      activities.value = response.activities.map(activity => ({
        id: activity.id,
        time: activity.created_at,
        user: currentUser.username,
        action: activity.action,
        details: activity.resource_name || activity.description,
        target_type: activity.target_type,
        target_id: activity.target_id
      }))
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
      (summary.tasks?.total || 0) +
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
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '严重程度',
          type: 'pie',
          radius: '70%',
          data: [
            { value: statistics.value.severity_distribution?.low || 0, name: '低' },
            { value: statistics.value.severity_distribution?.medium || 0, name: '中' },
            { value: statistics.value.severity_distribution?.high || 0, name: '高' },
            { value: statistics.value.severity_distribution?.critical || 0, name: '严重' }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
    severityChartInstance.setOption(severityOption)
  }
  
  if (priorityChartInstance) {
    const priorityOption = {
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: ['低', '中', '高']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          data: [
            statistics.value.priority_distribution?.low || 0,
            statistics.value.priority_distribution?.medium || 0,
            statistics.value.priority_distribution?.high || 0
          ],
          type: 'bar',
          itemStyle: {
            color: '#409EFF'
          }
        }
      ]
    }
    priorityChartInstance.setOption(priorityOption)
  }
  
  if (activityChartInstance) {
    const activityOption = {
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['任务活动', '缺陷活动']
      },
      xAxis: {
        type: 'category',
        data: statistics.value.activity_chart?.dates || []
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '任务活动',
          type: 'line',
          data: statistics.value.activity_chart?.task_activity || [],
          itemStyle: {
            color: '#67C23A'
          }
        },
        {
          name: '缺陷活动',
          type: 'line',
          data: statistics.value.activity_chart?.bug_activity || [],
          itemStyle: {
            color: '#E6A23C'
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
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.dashboard-header {
  margin-bottom: 24px;
}

.dashboard-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
}

.dashboard-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.organization-section {
  margin-bottom: 24px;
}

.org-card, .stats-card {
  border-radius: 8px;
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
  max-height: 200px;
  padding: 10px 0;
}

.nav-card {
  display: flex;
  flex-direction: column;
}

.nav-card :deep(.el-card__body) {
  flex: 1;
}

.card-header {
  font-weight: 600;
  color: #303133;
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.org-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.org-item:last-child {
  border-bottom: none;
}

.org-label {
  color: #606266;
  font-weight: 500;
}

.org-value {
  color: #303133;
  font-weight: 600;
}



/* 图标统计卡片布局 */
.stats-icon-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 8px;
  background: #fafafa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.stat-icon-item:hover {
  background: #f0f0f0;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.stat-icon {
  font-size: 18px;
}

.stat-info {
  text-align: center;
}

.stat-number {
  font-size: 20px;
  font-weight: bold;
  color: #2196F3;
  margin-bottom: 4px;
}

.stat-desc {
  font-size: 12px;
  color: #606266;
}

/* 项目进度概览 */
.project-progress-section {
  margin-bottom: 24px;
}

.project-progress-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.project-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fafafa;
}

.project-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  font-size: 14px;
}

.project-status {
  margin-bottom: 12px;
}

.project-progress {
  margin-bottom: 8px;
}

.project-percentage {
  text-align: right;
  font-weight: 600;
  color: #409EFF;
  font-size: 13px;
}

.no-projects {
  text-align: center;
  color: #909399;
  padding: 20px;
  font-style: italic;
}

.quick-access-section {
  margin-bottom: 24px;
}

.quick-access-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.access-item {
  padding: 16px 12px;
  text-align: center;
  background: #f5f7fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  color: #409EFF;
  font-weight: 500;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.access-item:hover {
  background: #409EFF;
  color: white;
  transform: translateY(-2px);
}

.access-item i {
  font-size: 20px;
}

.access-item span {
  font-size: 13px;
}

.activity-section {
  margin-bottom: 24px;
}

.activity-list {
  max-height: 300px;
  overflow-y: auto;
}

.activity-item {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-time {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.activity-content {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.activity-user {
  color: #409EFF;
  font-weight: 500;
}

.activity-action {
  color: #67C23A;
  font-size: 12px;
}

.activity-details {
  flex: 1;
}

.navigation-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.nav-item {
  padding: 12px;
  text-align: center;
  background: #f5f7fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  color: #606266;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  position: relative;
}

.nav-item:hover {
  background: #ecf5ff;
}

.nav-item .el-icon {
  font-size: 24px;
  color: #409eff;
}

.nav-item .nav-text {
  font-size: 13px;
  color: #409eff;
}

.todo-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background: #F56C6C;
  color: white;
  font-size: 10px;
  font-weight: bold;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.charts-section {
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 8px;
}

.chart-header {
  font-weight: 600;
  color: #303133;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.recent-bugs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bug-title-link {
  color: #409EFF;
  text-decoration: none;
}

.bug-title-link:hover {
  text-decoration: underline;
}

@media screen and (max-width: 768px) {
  .dashboard {
    padding: 0;
  }

  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 16px;
    padding: 12px;
  }

  .dashboard-header h2 {
    font-size: 18px;
  }

  .dashboard-header p {
    font-size: 12px;
  }

  .quick-actions {
    flex-wrap: wrap;
    gap: 8px;
    width: 100%;
  }

  .quick-actions .el-button {
    flex: 1;
    min-width: 80px;
    max-width: calc(50% - 4px);
    font-size: 12px;
    padding: 8px 12px;
  }

  .organization-section {
    margin-bottom: 16px;
  }

  .org-content {
    max-height: 120px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .org-item {
    padding: 6px 0;
    margin-bottom: 8px;
  }

  .org-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .org-name {
    font-size: 13px;
  }

  .org-stats {
    font-size: 11px;
    flex-wrap: wrap;
    gap: 4px;
  }

  .navigation-grid {
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 8px;
  }

  .nav-item {
    padding: 12px 8px;
    flex-direction: column;
    gap: 6px;
  }

  .nav-item .el-icon {
    font-size: 22px;
  }

  .nav-item .nav-text {
    font-size: 12px;
  }

  .todo-badge {
    min-width: 14px;
    height: 14px;
    font-size: 9px;
  }

  .project-progress-section {
    margin-bottom: 16px;
  }

  .project-progress-grid {
    grid-template-columns: 1fr !important;
    gap: 12px;
  }

  .project-item {
    padding: 12px;
  }

  .project-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .project-name {
    font-size: 13px;
  }

  .project-meta {
    font-size: 11px;
    flex-wrap: wrap;
    gap: 4px;
  }

  .project-percentage {
    font-size: 12px;
  }

  .quick-access-section {
    margin-bottom: 16px;
  }

  .quick-access-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 12px;
  }

  .quick-access-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
  }

  .access-item {
    padding: 12px 8px;
    flex-direction: column;
    gap: 6px;
  }

  .access-item i {
    font-size: 18px;
  }

  .access-item span {
    font-size: 11px;
  }

  .activity-section {
    margin-bottom: 16px;
  }

  .activity-list {
    max-height: 200px;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }

  .activity-item {
    padding: 8px 0;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .activity-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }

  .activity-time {
    font-size: 11px;
  }

  .activity-action {
    font-size: 11px;
  }

  .activity-meta {
    font-size: 10px;
  }

  .stats-icon-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .stat-icon-item {
    padding: 10px 6px;
    flex-direction: column;
    gap: 6px;
  }

  .stat-icon-wrapper {
    width: 36px;
    height: 36px;
    margin-bottom: 0;
  }

  .stat-icon {
    font-size: 18px;
  }

  .stat-number {
    font-size: 16px;
  }

  .stat-desc {
    font-size: 11px;
  }

  .charts-section {
    margin-bottom: 16px;
  }

  .chart-container {
    height: 200px;
    min-height: 200px;
  }

  .chart-header {
    font-size: 14px;
    margin-bottom: 8px;
  }

  .recent-bugs {
    margin-bottom: 16px;
  }

  .recent-bugs-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .recent-bugs-header .el-button {
    width: 100%;
    font-size: 12px;
  }

  .recent-bugs-table {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
  }
}

@media screen and (max-width: 480px) {
  .dashboard {
    padding: 0;
  }

  .dashboard-header {
    padding: 10px;
  }

  .dashboard-header h2 {
    font-size: 16px;
  }

  .quick-actions .el-button {
    font-size: 11px;
    padding: 6px 10px;
    min-width: 70px;
  }

  .quick-access-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .navigation-grid {
    gap: 6px;
  }

  .nav-item {
    padding: 10px 6px;
  }

  .nav-item .el-icon {
    font-size: 20px;
  }

  .nav-item .nav-text {
    font-size: 11px;
  }

  .project-item {
    padding: 10px;
  }

  .project-name {
    font-size: 12px;
  }

  .access-item {
    padding: 10px 6px;
  }

  .access-item i {
    font-size: 16px;
  }

  .access-item span {
    font-size: 10px;
  }

  .stat-icon-item {
    padding: 8px 4px;
  }

  .stat-icon-wrapper {
    width: 32px;
    height: 32px;
  }

  .stat-icon {
    font-size: 16px;
  }

  .stat-number {
    font-size: 14px;
  }

  .chart-container {
    height: 180px;
  }

  .activity-list {
    max-height: 150px;
  }

  .el-descriptions {
    font-size: 11px;
  }

  .el-descriptions-item {
    display: block !important;
    padding: 4px !important;
  }
}
</style>