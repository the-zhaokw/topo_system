<template>
  <div class="personal-plan-container">
    <!-- 页面头部工具栏 -->
    <header class="page-header">
      <div class="header-left">
        <div class="search-wrapper">
          <el-input
            v-model="searchQuery"
            placeholder="搜索任务、成员或文件..."
            class="global-search"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </div>

      <div class="header-center">
        <div class="view-switcher">
          <el-radio-group v-model="currentView" size="default">
            <el-radio-button value="kanban">
              <el-icon><Grid /></el-icon>
              <span>看板</span>
            </el-radio-button>
            <el-radio-button value="list">
              <el-icon><List /></el-icon>
              <span>列表</span>
            </el-radio-button>
            <el-radio-button value="timeline">
              <el-icon><TrendCharts /></el-icon>
              <span>时间线</span>
            </el-radio-button>
            <el-radio-button value="calendar">
              <el-icon><Calendar /></el-icon>
              <span>日历</span>
            </el-radio-button>
          </el-radio-group>
        </div>
      </div>

      <div class="header-right">
        <el-button type="primary" class="quick-create-btn" @click="showQuickCreate = true">
          <el-icon><Plus /></el-icon>
          快速创建
        </el-button>
      </div>
    </header>

    <div class="main-wrapper">
      <!-- 主内容区 -->
      <main class="main-content">
        <!-- 看板视图 -->
        <div v-show="currentView === 'kanban'" class="kanban-view">
          <div class="kanban-board">
            <div
              v-for="column in kanbanColumns"
              :key="column.status"
              class="kanban-column"
              @dragover.prevent
              @drop="handleKanbanDrop($event, column.status)"
            >
              <div class="column-header">
                <div class="column-title">
                  <span class="column-dot" :class="column.status"></span>
                  {{ column.title }}
                  <span class="column-count">{{ getColumnTasks(column.status).length }}</span>
                </div>
              </div>

              <div class="column-content">
                <div
                  v-for="task in getColumnTasks(column.status)"
                  :key="task.id"
                  class="task-card"
                  draggable="true"
                  @dragstart="handleKanbanDragStart($event, task)"
                  @dragend="handleKanbanDragEnd"
                  @click="openTaskDetail(task)"
                >
                  <div class="card-header">
                    <span class="card-priority" :class="task.priority"></span>
                    <span class="card-title">{{ task.title }}</span>
                  </div>

                  <div class="card-meta">
                    <div class="meta-left">
                      <span v-if="task.due_date" class="card-due" :class="{ overdue: isOverdue(task) }">
                        <el-icon><Clock /></el-icon>
                        {{ formatDate(task.due_date) }}
                      </span>
                      <span v-if="task.subtasks?.length" class="card-subtasks">
                        <el-icon><Tickets /></el-icon>
                        {{ task.subtasks.filter(s => s.completed).length }}/{{ task.subtasks.length }}
                      </span>
                    </div>
                    <el-avatar
                      v-if="task.assignee"
                      :size="24"
                      :src="task.assigneeAvatar"
                      class="card-assignee"
                    >
                      {{ task.assigneeName?.charAt(0) }}
                    </el-avatar>
                  </div>

                  <div class="card-footer" v-if="task.tags?.length">
                    <el-tag
                      v-for="tag in task.tags.slice(0, 2)"
                      :key="tag"
                      size="small"
                      type="info"
                      class="card-tag"
                    >
                      #{{ tag }}
                    </el-tag>
                    <span v-if="task.tags.length > 2" class="more-tags">+{{ task.tags.length - 2 }}</span>
                  </div>

                  <div class="card-actions">
                    <el-button text size="small" @click.stop="editTask(task)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button text size="small" @click.stop="copyTask(task)">
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                    <el-button text size="small" type="danger" @click.stop="deleteTask(task)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>

                <div class="add-card" @click="addTaskToColumn(column.status)">
                  <el-icon><Plus /></el-icon>
                  添加任务
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 列表视图 -->
        <div v-show="currentView === 'list'" class="list-view">
          <el-table
            :data="filteredTasks"
            row-key="id"
            :tree-props="{ children: 'subtasks', hasChildren: 'hasSubtasks' }"
            default-expand-all
            @row-dblclick="handleRowDblClick"
            class="task-table"
            :row-class-name="getRowClassName"
          >
            <el-table-column width="40">
              <template #default="{ row }">
                <el-checkbox
                  :model-value="row.completed"
                  @change="toggleTaskComplete(row)"
                />
              </template>
            </el-table-column>

            <el-table-column prop="title" label="任务名称" min-width="300">
              <template #default="{ row }">
                <div class="task-title-cell">
                  <span v-if="row.priority === 'urgent'" class="priority-indicator urgent">!</span>
                  <span v-else-if="row.priority === 'high'" class="priority-indicator high">!!</span>
                  <span class="task-title" :class="{ completed: row.completed }">{{ row.title }}</span>
                  <el-tag v-if="row.subtasks?.length" size="small" type="info">
                    {{ row.subtasks.filter(s => s.completed).length }}/{{ row.subtasks.length }}
                  </el-tag>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column prop="priority" label="优先级" width="100">
              <template #default="{ row }">
                <span class="priority-dot" :class="row.priority"></span>
              </template>
            </el-table-column>

            <el-table-column prop="due_date" label="截止时间" width="140">
              <template #default="{ row }">
                <span v-if="row.due_date" class="due-date" :class="{ overdue: isOverdue(row) }">
                  {{ formatDate(row.due_date) }}
                </span>
                <span v-else class="no-date">未设置</span>
              </template>
            </el-table-column>

            <el-table-column prop="assignee" label="负责人" width="100">
              <template #default="{ row }">
                <el-avatar v-if="row.assignee" :size="28" :src="row.assigneeAvatar">
                  {{ row.assigneeName?.charAt(0) }}
                </el-avatar>
                <span v-else class="no-assignee">未分配</span>
              </template>
            </el-table-column>

            <el-table-column prop="tags" label="标签" width="150">
              <template #default="{ row }">
                <el-tag
                  v-for="tag in (row.tags || '').split(',').filter(t => t).slice(0, 2)"
                  :key="tag"
                  size="small"
                  type="info"
                  class="task-tag"
                >
                  #{{ tag }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button text size="small" @click="editTask(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button text size="small" @click="copyTask(row)">
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
                <el-button text size="small" type="danger" @click="deleteTask(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 时间线视图 -->
        <div v-show="currentView === 'timeline'" class="timeline-view">
          <GanttView :tasks="tasks" @refresh="loadTasks" />
        </div>

        <!-- 日历视图 -->
        <div v-show="currentView === 'calendar'" class="calendar-view-wrapper">
          <CalendarView :tasks="tasks" @refresh="loadTasks" />
        </div>
      </main>

      <!-- 右侧面板 -->
      <aside class="right-panel" :class="{ hidden: isRightPanelHidden }">
        <div class="panel-header">
          <span class="panel-title">概览</span>
          <el-button text size="small" @click="isRightPanelHidden = true">
            <el-icon><DArrowRight /></el-icon>
          </el-button>
        </div>

        <div class="panel-content">
          <div class="progress-section">
            <div class="section-title">项目进度</div>
            <div class="progress-ring">
              <el-progress
                type="circle"
                :percentage="projectProgress"
                :stroke-width="10"
                :width="120"
              />
              <div class="progress-info">
                <span class="progress-label">完成率</span>
                <span class="progress-value">{{ completedTasks }}/{{ totalTasks }}</span>
              </div>
            </div>
          </div>

          <el-divider />

          <div class="stats-section">
            <div class="stat-item">
              <span class="stat-value overdue">{{ overdueTasksCount }}</span>
              <span class="stat-label">延期任务</span>
            </div>
            <div class="stat-item">
              <span class="stat-value new">{{ weekNewTasks }}</span>
              <span class="stat-label">本周新增</span>
            </div>
            <div class="stat-item">
              <span class="stat-value completed">{{ todayCompleted }}</span>
              <span class="stat-label">今日完成</span>
            </div>
          </div>

          <el-divider />

          <div class="member-load-section">
            <div class="section-title">成员负载</div>
            <div class="member-list">
              <div v-for="member in teamMembers" :key="member.id" class="member-item">
                <div class="member-info">
                  <el-avatar :size="28" :src="member.avatar">
                    {{ member.name.charAt(0) }}
                  </el-avatar>
                  <span class="member-name">{{ member.name }}</span>
                </div>
                <div class="load-bar">
                  <div
                    class="load-fill"
                    :class="getLoadLevel(member.taskCount)"
                    :style="{ width: Math.min(member.taskCount * 10, 100) + '%' }"
                  ></div>
                </div>
                <span class="load-count">{{ member.taskCount }}</span>
              </div>
            </div>
          </div>

          <el-divider />

          <div class="activity-section">
            <div class="section-title">近期动态</div>
            <div class="activity-list">
              <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
                <el-avatar :size="24" :src="activity.userAvatar">
                  {{ activity.userName?.charAt(0) }}
                </el-avatar>
                <div class="activity-content">
                  <p class="activity-text">
                    <span class="user-name">{{ activity.userName }}</span>
                    {{ activity.action }}
                    <span class="task-name">{{ activity.taskTitle }}</span>
                  </p>
                  <span class="activity-time">{{ activity.time }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="panel-footer">
          <el-button text size="small" @click="isRightPanelHidden = false" v-if="isRightPanelHidden">
            <el-icon><DArrowLeft /></el-icon>
            显示面板
          </el-button>
        </div>
      </aside>
    </div>

    <!-- 任务详情弹窗 -->
    <el-dialog
      v-model="taskDetailVisible"
      :title="selectedTask?.title || '任务详情'"
      width="700px"
      class="task-detail-dialog"
    >
      <div class="task-detail" v-if="selectedTask">
        <div class="detail-header">
          <div class="task-status">
            <el-tag :type="getStatusType(selectedTask.status)" size="large">
              {{ getStatusLabel(selectedTask.status) }}
            </el-tag>
            <el-tag v-if="selectedTask.priority" :type="getPriorityType(selectedTask.priority)" size="large">
              {{ getPriorityLabel(selectedTask.priority) }}
            </el-tag>
          </div>
        </div>

        <el-form :model="selectedTask" label-width="100px" class="detail-form">
          <el-form-item label="任务描述">
            <el-input
              v-model="selectedTask.description"
              type="textarea"
              :rows="3"
              placeholder="添加任务描述..."
            />
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="负责人">
                <el-select v-model="selectedTask.assignee" placeholder="选择负责人">
                  <el-option
                    v-for="member in teamMembers"
                    :key="member.id"
                    :label="member.name"
                    :value="member.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="截止日期">
                <el-date-picker
                  v-model="selectedTask.due_date"
                  type="date"
                  value-format="YYYY-MM-DD"
                  placeholder="选择日期"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="开始日期">
                <el-date-picker
                  v-model="selectedTask.start_date"
                  type="date"
                  value-format="YYYY-MM-DD"
                  placeholder="选择日期"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="预估时长">
                <el-input-number
                  v-model="selectedTask.estimated_minutes"
                  :min="5"
                  :step="5"
                  :max="480"
                />
                <span class="ml-2">分钟</span>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="标签">
            <el-input v-model="selectedTask.tags" placeholder="多个标签用逗号分隔" />
          </el-form-item>

          <el-form-item label="子任务">
            <div class="subtask-list">
              <div v-for="(subtask, index) in selectedTask.subtasks" :key="index" class="subtask-item">
                <el-checkbox v-model="subtask.completed" @change="updateSubtaskProgress" />
                <el-input v-model="subtask.title" size="small" />
                <el-button text type="danger" size="small" @click="removeSubtask(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
              <el-button text size="small" @click="addSubtask">
                <el-icon><Plus /></el-icon> 添加子任务
              </el-button>
            </div>
          </el-form-item>

          <el-form-item label="进度">
            <div class="progress-control">
              <el-slider v-model="selectedTask.progress" :min="0" :max="100" :step="10" />
              <span class="progress-text">{{ selectedTask.progress || 0 }}%</span>
            </div>
          </el-form-item>
        </el-form>

        <el-divider />



        <div class="time-records" v-if="selectedTask.timeRecords?.length">
          <div class="section-title">时间记录</div>
          <div class="time-list">
            <div v-for="record in selectedTask.timeRecords" :key="record.id" class="time-item">
              <span class="time-date">{{ record.date }}</span>
              <span class="time-duration">{{ record.hours }}小时</span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="taskDetailVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTaskDetail">保存</el-button>
      </template>
    </el-dialog>

    <!-- 快速创建弹窗 -->
    <el-dialog v-model="showQuickCreate" title="快速创建" width="500px" class="quick-create-dialog">
      <el-form :model="quickForm" label-width="80px">
        <el-form-item label="任务内容">
          <el-input
            v-model="quickForm.content"
            type="textarea"
            :rows="3"
            placeholder="输入任务内容，支持 @标签 !紧急 明天下午3点 30分钟 等格式"
          />
        </el-form-item>
        <el-form-item label="智能解析">
          <div class="parse-preview" v-if="parsedResult.title">
            <div class="preview-item">
              <span class="label">标题:</span>
              <span class="value">{{ parsedResult.title }}</span>
            </div>
            <div class="preview-item" v-if="parsedResult.priority">
              <span class="label">优先级:</span>
              <el-tag :type="getPriorityType(parsedResult.priority)" size="small">
                {{ getPriorityLabel(parsedResult.priority) }}
              </el-tag>
            </div>
            <div class="preview-item" v-if="parsedResult.scheduled_date">
              <span class="label">日期:</span>
              <span class="value">{{ parsedResult.scheduled_date }}</span>
            </div>
            <div class="preview-item" v-if="parsedResult.tags?.length">
              <span class="label">标签:</span>
              <el-tag v-for="tag in parsedResult.tags" :key="tag" size="small" class="tag-item">
                #{{ tag }}
              </el-tag>
            </div>
          </div>
          <div v-else class="parse-tips">
            <p>快捷键提示：</p>
            <div class="tips-list">
              <span class="tip-item"><code>@标签</code> 添加标签</span>
              <span class="tip-item"><code>!</code> 紧急</span>
              <span class="tip-item"><code>!!</code> 高优</span>
              <span class="tip-item"><code>30分钟</code> 预估时长</span>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showQuickCreate = false">取消</el-button>
        <el-button type="primary" @click="handleQuickCreate" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 任务编辑弹窗 -->
    <el-dialog v-model="taskDialogVisible" :title="editingTask ? '编辑任务' : '新建任务'" width="600px">
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="任务标题">
          <el-input v-model="taskForm.title" placeholder="请输入任务标题" />
        </el-form-item>
        <el-form-item label="任务描述">
          <el-input v-model="taskForm.description" type="textarea" :rows="3" placeholder="请输入任务描述" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-select v-model="taskForm.priority" placeholder="选择优先级">
                <el-option label="紧急" value="urgent" />
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="负责人">
              <el-select v-model="taskForm.assignee" placeholder="选择负责人">
                <el-option v-for="member in teamMembers" :key="member.id" :label="member.name" :value="member.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期">
              <el-date-picker v-model="taskForm.start_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="截止日期">
              <el-date-picker v-model="taskForm.due_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="预估时长">
          <el-input-number v-model="taskForm.estimated_minutes" :min="5" :step="5" :max="480" />
          <span class="ml-2">分钟</span>
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="taskForm.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveTask">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Plus, Grid, List, TrendCharts, Calendar as CalendarIcon,
  Clock, Tickets, Edit, Delete, CopyDocument
} from '@element-plus/icons-vue'
import { apiService } from '@/services/api'
import GanttView from './personalplan/GanttView.vue'
import CalendarView from './personalplan/CalendarView.vue'

// 当前视图
const currentView = ref('kanban')
const isRightPanelHidden = ref(false)

// 搜索
const searchQuery = ref('')

// 快速创建
const showQuickCreate = ref(false)
const creating = ref(false)
const quickForm = reactive({
  content: ''
})
const parsedResult = reactive({
  title: '',
  priority: '',
  scheduled_date: '',
  tags: []
})

// 筛选
const filterStatus = ref('')
const filterPriority = ref('')
const filterAssignee = ref('')
const selectedTags = ref([])

// 标签
const myTags = ref([
  { name: '高优先级', type: 'danger' },
  { name: '沟通', type: 'warning' },
  { name: '开发', type: 'success' },
  { name: '文档', type: 'info' }
])

// 团队成员
const teamMembers = ref([
  { id: 1, name: '张三', avatar: '', taskCount: 5 },
  { id: 2, name: '李四', avatar: '', taskCount: 3 },
  { id: 3, name: '王五', avatar: '', taskCount: 7 }
])

// 任务数据
const tasks = ref([])
const draggedTask = ref(null)

// 统计数据
const totalTasks = computed(() => tasks.value.length)
const completedTasks = computed(() => tasks.value.filter(t => t.status === 'done').length)
const projectProgress = computed(() => {
  if (totalTasks.value === 0) return 0
  return Math.round((completedTasks.value / totalTasks.value) * 100)
})
const overdueTasksCount = computed(() => tasks.value.filter(t => isOverdue(t)).length)
const todayCompleted = ref(3)
const weekNewTasks = ref(12)

// 近期动态
const recentActivities = ref([
  { id: 1, userName: '张三', userAvatar: '', action: '完成了', taskTitle: '完成Q2预算报告', time: '10分钟前' },
  { id: 2, userName: '李四', userAvatar: '', action: '评论了', taskTitle: '产品需求评审', time: '30分钟前' },
  { id: 3, userName: '王五', userAvatar: '', action: '创建了', taskTitle: '技术方案设计', time: '1小时前' }
])

// 看板列
const kanbanColumns = [
  { title: '待处理', status: 'todo' },
  { title: '进行中', status: 'in_progress' },
  { title: '待审核', status: 'review' },
  { title: '已完成', status: 'done' }
]

// 任务编辑
const taskDialogVisible = ref(false)
const editingTask = ref(null)
const taskForm = reactive({
  title: '',
  description: '',
  priority: 'medium',
  assignee: null,
  start_date: '',
  due_date: '',
  estimated_minutes: 30,
  tags: ''
})

// 任务详情
const taskDetailVisible = ref(false)
const selectedTask = ref(null)

// 过滤后的任务
const filteredTasks = computed(() => {
  let result = tasks.value

  if (filterStatus.value) {
    result = result.filter(t => t.status === filterStatus.value)
  }

  if (filterPriority.value) {
    result = result.filter(t => t.priority === filterPriority.value)
  }

  if (filterAssignee.value) {
    result = result.filter(t => t.assignee === filterAssignee.value)
  }

  if (selectedTags.value.length > 0) {
    result = result.filter(t => {
      const taskTags = t.tags ? t.tags.split(',') : []
      return selectedTags.value.some(tag => taskTags.includes(tag))
    })
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(t =>
      t.title.toLowerCase().includes(query) ||
      t.description?.toLowerCase().includes(query)
    )
  }

  return result
})

// 监听快速输入内容变化，智能解析
watch(() => quickForm.content, (content) => {
  if (content) {
    parseTaskContent(content)
  } else {
    Object.assign(parsedResult, { title: '', priority: '', scheduled_date: '', tags: [] })
  }
})

const parseTaskContent = (content) => {
  let title = content
  let priority = ''
  let scheduled_date = ''
  let tags = []

  if (content.includes('!!!') || content.includes('!紧急')) {
    priority = 'urgent'
    title = title.replace(/!!!|!紧急/g, '')
  } else if (content.includes('!!') || content.includes('!高优')) {
    priority = 'high'
    title = title.replace(/!!|!高优/g, '')
  } else if (content.includes('!')) {
    priority = 'medium'
    title = title.replace(/!/g, '')
  }

  const tagMatches = content.match(/@(\w+)/g)
  if (tagMatches) {
    tags = tagMatches.map(t => t.replace('@', ''))
    title = title.replace(/@\w+/g, '')
  }

  if (content.includes('明天')) {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    scheduled_date = tomorrow.toISOString().split('T')[0]
    title = title.replace('明天', '')
  }

  Object.assign(parsedResult, {
    title: title.trim(),
    priority,
    scheduled_date,
    tags
  })
}

const getPriorityType = (priority) => {
  const types = { urgent: 'danger', high: 'warning', medium: 'primary', low: 'success' }
  return types[priority] || 'info'
}

const getPriorityLabel = (priority) => {
  const labels = { urgent: '紧急', high: '高', medium: '中', low: '低' }
  return labels[priority] || priority
}

const getStatusType = (status) => {
  const types = { todo: 'info', in_progress: 'primary', review: 'warning', done: 'success' }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = { todo: '待处理', in_progress: '进行中', review: '待审核', done: '已完成' }
  return labels[status] || status
}

const handleQuickCreate = async () => {
  if (!quickForm.content.trim()) {
    ElMessage.warning('请输入任务内容')
    return
  }

  creating.value = true
  try {
    await apiService.personalPlan.createTask({ content: quickForm.content })
    ElMessage.success('任务创建成功')
    showQuickCreate.value = false
    quickForm.content = ''
    loadTasks()
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

const loadTasks = async () => {
  try {
    const data = await apiService.personalPlan.getTasks()
    tasks.value = Array.isArray(data?.tasks) ? data.tasks : []
  } catch (error) {
    console.error('加载任务失败:', error)
    tasks.value = []
  }
}

const toggleTag = (tagName) => {
  const index = selectedTags.value.indexOf(tagName)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  } else {
    selectedTags.value.push(tagName)
  }
}

const getColumnTasks = (status) => {
  return filteredTasks.value.filter(t => t.status === status)
}

const isOverdue = (task) => {
  if (!task.due_date) return false
  const now = new Date()
  const due = new Date(task.due_date)
  return due < now && task.status !== 'done'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

const getRowClassName = ({ row }) => {
  if (isOverdue(row)) return 'overdue-row'
  if (row.at_risk) return 'at-risk-row'
  return ''
}

const getLoadLevel = (count) => {
  if (count >= 8) return 'high'
  if (count >= 4) return 'medium'
  return 'low'
}

const handleKanbanDragStart = (event, task) => {
  draggedTask.value = task
  event.dataTransfer.effectAllowed = 'move'
}

const handleKanbanDragEnd = () => {
  draggedTask.value = null
}

const handleKanbanDrop = async (event, status) => {
  if (!draggedTask.value) return

  try {
    await apiService.personalPlan.updateTask(draggedTask.value.id, { status })
    ElMessage.success('任务状态已更新')
    loadTasks()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const openTaskDetail = (task) => {
  selectedTask.value = { ...task }
  taskDetailVisible.value = true
}

const handleRowDblClick = (row) => {
  openTaskDetail(row)
}

const toggleTaskComplete = async (task) => {
  try {
    await apiService.personalPlan.toggleTaskComplete(task.id)
    ElMessage.success(task.completed ? '任务已取消完成' : '任务已完成')
    loadTasks()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const editTask = (task) => {
  editingTask.value = task
  taskForm.title = task.title
  taskForm.description = task.description || ''
  taskForm.priority = task.priority || 'medium'
  taskForm.assignee = task.assignee
  taskForm.start_date = task.start_date || ''
  taskForm.due_date = task.due_date || ''
  taskForm.estimated_minutes = task.estimated_minutes || 30
  taskForm.tags = task.tags || ''
  taskDialogVisible.value = true
}

const copyTask = async (task) => {
  try {
    await apiService.personalPlan.createTask({
      title: task.title + ' (副本)',
      description: task.description,
      priority: task.priority,
      estimated_minutes: task.estimated_minutes,
      tags: task.tags
    })
    ElMessage.success('任务已复制')
    loadTasks()
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const deleteTask = async (task) => {
  try {
    await ElMessageBox.confirm('确定要删除这个任务吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await apiService.personalPlan.deleteTask(task.id)
    ElMessage.success('任务已删除')
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const addTaskToColumn = (status) => {
  editingTask.value = null
  Object.assign(taskForm, {
    title: '',
    description: '',
    priority: 'medium',
    assignee: null,
    start_date: '',
    due_date: '',
    estimated_minutes: 30,
    tags: ''
  })
  taskForm.status = status
  taskDialogVisible.value = true
}

const handleSaveTask = async () => {
  try {
    if (editingTask.value) {
      await apiService.personalPlan.updateTask(editingTask.value.id, taskForm)
      ElMessage.success('任务已更新')
    } else {
      await apiService.personalPlan.createTask(taskForm)
      ElMessage.success('任务已创建')
    }
    taskDialogVisible.value = false
    editingTask.value = null
    loadTasks()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const saveTaskDetail = async () => {
  try {
    await apiService.personalPlan.updateTask(selectedTask.value.id, selectedTask.value)
    ElMessage.success('任务已更新')
    taskDetailVisible.value = false
    loadTasks()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const addSubtask = () => {
  if (!selectedTask.value.subtasks) {
    selectedTask.value.subtasks = []
  }
  selectedTask.value.subtasks.push({ title: '', completed: false })
}

const removeSubtask = (index) => {
  selectedTask.value.subtasks.splice(index, 1)
}

const updateSubtaskProgress = () => {
  if (!selectedTask.value.subtasks?.length) return
  const completed = selectedTask.value.subtasks.filter(s => s.completed).length
  selectedTask.value.progress = Math.round((completed / selectedTask.value.subtasks.length) * 100)
}



onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.personal-plan-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

/* 页面头部工具栏 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.header-left {
  flex: 1;
}

.header-center {
  flex: 0 0 auto;
}

.header-right {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.search-wrapper {
  width: 300px;
}

.global-search :deep(.el-input__wrapper) {
  border-radius: 20px;
  background: #f5f7fa;
  box-shadow: none;
}

.view-switcher :deep(.el-radio-button__inner) {
  display: flex;
  align-items: center;
  gap: 4px;
}

.quick-create-btn {
  border-radius: 20px;
}

/* 主布局 */
.main-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 主内容区 */
.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f5f7fa;
}

/* 看板视图 */
.kanban-view {
  height: 100%;
}

.kanban-board {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 20px;
}

.kanban-column {
  flex: 0 0 300px;
  background: #f5f7fa;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 180px);
}

.column-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.column-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.column-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.column-dot.todo {
  background: #909399;
}

.column-dot.in_progress {
  background: #409eff;
}

.column-dot.review {
  background: #e6a23c;
}

.column-dot.done {
  background: #67c23a;
}

.column-count {
  background: #e6e6e6;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: normal;
  color: #909399;
}

.column-content {
  flex: 1;
  padding: 12px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-card {
  background: #fff;
  border-radius: 8px;
  padding: 14px;
  cursor: grab;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  position: relative;
}

.task-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.task-card:hover .card-actions {
  opacity: 1;
}

.task-card:active {
  cursor: grabbing;
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 10px;
}

.card-priority {
  width: 4px;
  height: 18px;
  border-radius: 2px;
  flex-shrink: 0;
}

.card-priority.urgent {
  background: #f56c6c;
}

.card-priority.high {
  background: #e6a23c;
}

.card-priority.medium {
  background: #409eff;
}

.card-priority.low {
  background: #67c23a;
}

.card-title {
  font-size: 14px;
  color: #303133;
  flex: 1;
  word-break: break-word;
  line-height: 1.4;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.meta-left {
  display: flex;
  gap: 12px;
}

.card-due, .card-subtasks {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.card-due.overdue {
  color: #f56c6c;
}

.card-assignee {
  border: 2px solid #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-footer {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  align-items: center;
}

.card-tag {
  font-size: 11px;
}

.more-tags {
  font-size: 11px;
  color: #909399;
}

.card-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
  background: rgba(255, 255, 255, 0.95);
  padding: 2px;
  border-radius: 4px;
}

.add-card {
  padding: 16px;
  text-align: center;
  color: #909399;
  cursor: pointer;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  transition: all 0.2s;
  font-size: 14px;
}

.add-card:hover {
  border-color: #409eff;
  color: #409eff;
  background: rgba(64, 158, 255, 0.05);
}

/* 列表视图 */
.list-view {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.task-table {
  width: 100%;
}

.task-title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.priority-indicator {
  font-weight: bold;
  font-size: 12px;
}

.priority-indicator.urgent {
  color: #f56c6c;
}

.priority-indicator.high {
  color: #e6a23c;
}

.task-title {
  font-size: 14px;
}

.task-title.completed {
  text-decoration: line-through;
  color: #909399;
}

.task-tag {
  margin-right: 4px;
}

.priority-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.priority-dot.urgent {
  background: #f56c6c;
}

.priority-dot.high {
  background: #e6a23c;
}

.priority-dot.medium {
  background: #409eff;
}

.priority-dot.low {
  background: #67c23a;
}

.due-date {
  font-size: 13px;
  color: #606266;
}

.due-date.overdue {
  color: #f56c6c;
  font-weight: 500;
}

.no-date {
  color: #c0c4cc;
  font-size: 13px;
}

.no-assignee {
  color: #c0c4cc;
  font-size: 12px;
}

:deep(.overdue-row) {
  background: #fef0f0 !important;
}

:deep(.at-risk-row) {
  background: #fdf6ec !important;
}

/* 右侧面板 */
.right-panel {
  width: 280px;
  background: #fff;
  border-left: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  transition: width 0.3s, transform 0.3s;
}

.right-panel.hidden {
  width: 0;
  overflow: hidden;
  transform: translateX(100%);
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.progress-section {
  text-align: center;
}

.progress-ring {
  position: relative;
  display: inline-block;
  margin-top: 16px;
}

.progress-info {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.progress-label {
  display: block;
  font-size: 12px;
  color: #909399;
}

.progress-value {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.stats-section {
  display: flex;
  justify-content: space-around;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 600;
}

.stat-value.overdue {
  color: #f56c6c;
}

.stat-value.new {
  color: #409eff;
}

.stat-value.completed {
  color: #67c23a;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.member-load-section .section-title {
  margin-bottom: 16px;
}

.member-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.member-info {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 80px;
}

.member-name {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.load-bar {
  flex: 1;
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.load-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.load-fill.high {
  background: #f56c6c;
}

.load-fill.medium {
  background: #e6a23c;
}

.load-fill.low {
  background: #67c23a;
}

.load-count {
  font-size: 12px;
  color: #909399;
  width: 20px;
  text-align: right;
}

.activity-section .section-title {
  margin-bottom: 16px;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  gap: 10px;
}

.activity-content {
  flex: 1;
}

.activity-text {
  margin: 0 0 4px 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
}

.user-name {
  font-weight: 500;
  color: #303133;
}

.task-name {
  color: #409eff;
}

.activity-time {
  font-size: 11px;
  color: #909399;
}

.panel-footer {
  padding: 12px;
  border-top: 1px solid #e4e7ed;
}

/* 任务详情弹窗 */
.task-detail-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.task-detail {
  padding: 20px;
}

.detail-header {
  margin-bottom: 20px;
}

.task-status {
  display: flex;
  gap: 8px;
}

.detail-form {
  margin-top: 20px;
}

.subtask-list {
  width: 100%;
}

.subtask-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.subtask-item .el-input {
  flex: 1;
}

.progress-control {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.progress-control .el-slider {
  flex: 1;
}

.progress-text {
  min-width: 40px;
  color: #606266;
}

.time-records {
  margin-top: 20px;
}

.time-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.time-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.time-date {
  font-size: 13px;
  color: #606266;
}

.time-duration {
  font-size: 13px;
  font-weight: 500;
  color: #409eff;
}

/* 快速创建弹窗 */
.quick-create-dialog :deep(.el-dialog__body) {
  padding-top: 10px;
}

.parse-preview {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.preview-item:last-child {
  margin-bottom: 0;
}

.preview-item .label {
  color: #909399;
  font-size: 13px;
  min-width: 60px;
}

.preview-item .value {
  color: #303133;
  font-size: 14px;
}

.tag-item {
  margin-right: 4px;
}

.parse-tips {
  color: #909399;
  font-size: 13px;
}

.parse-tips p {
  margin: 0 0 8px 0;
  font-weight: 500;
}

.tips-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tip-item code {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  color: #409eff;
}

.ml-2 {
  margin-left: 8px;
}

/* 响应式 */
@media screen and (max-width: 1200px) {
  .right-panel {
    display: none;
  }
}

@media screen and (max-width: 768px) {
  .page-header {
    padding: 12px 16px;
    flex-wrap: wrap;
    gap: 12px;
  }

  .header-left,
  .header-center,
  .header-right {
    flex: 1 1 100%;
    justify-content: center;
  }

  .search-wrapper {
    width: 100%;
  }

  .view-switcher :deep(.el-radio-button__inner span) {
    display: none;
  }

  .main-content {
    padding: 16px;
  }

  .kanban-column {
    flex: 0 0 260px;
  }
}
</style>
