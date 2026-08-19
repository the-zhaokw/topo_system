<template>
  <div class="rd-management">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Operation /></el-icon>
          </div>
          <div class="title-text">
            <h1>项目研发管理</h1>
            <p class="subtitle">以看板方式管理项目需求、研发进度与客户问题</p>
          </div>
        </div>
        <div class="header-actions">
          <el-select
            v-model="currentProjectId"
            placeholder="选择项目"
            class="project-selector"
            popper-class="project-selector-popper"
            @change="handleProjectChange"
            filterable
          >
            <el-option
              v-for="p in projectOptions"
              :key="p.id"
              :label="p.name"
              :value="p.id"
            />
          </el-select>
          <el-select
            v-model="filterAssignee"
            placeholder="按指派人筛选"
            class="filter-selector"
            clearable
            filterable
            @change="loadData"
          >
            <el-option
              v-for="u in userOptions"
              :key="u.id"
              :label="u.name"
              :value="u.id"
            />
          </el-select>
          <el-input
            v-model="filterKeyword"
            placeholder="搜索卡片..."
            class="keyword-input"
            clearable
            @keyup.enter="loadData"
            @clear="loadData"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-button class="btn-gradient" @click="loadData" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button class="btn-outline" @click="openWeeklySummary">
            <el-icon><Document /></el-icon>
            周报汇总
          </el-button>
          <el-button class="btn-outline" @click="openStats">
            <el-icon><DataAnalysis /></el-icon>
            数据统计
          </el-button>
        </div>
      </div>
    </div>

    <!-- 看板主体 -->
    <div class="kanban-container" v-loading="loading">
      <div class="kanban-board-scroll">
        <div class="kanban-columns">
          <div
            v-for="col in columns"
            :key="col.key"
            class="kanban-column"
            :class="{ 'drag-over': dragOverColumn === col.key }"
            @dragover.prevent="handleDragOver(col.key, $event)"
            @dragleave="handleDragLeave(col.key)"
            @drop.prevent="handleDrop(col.key, $event)"
          >
            <div class="column-header" :style="{ '--col-color': col.color }">
              <div class="column-title">
                <span class="column-dot"></span>
                <span class="column-name">{{ col.name }}</span>
                <el-badge
                  :value="getItemsByColumn(col.key).length"
                  :max="99"
                  class="column-count"
                />
              </div>
              <div class="column-actions">
                <el-tooltip content="新增卡片" placement="top">
                  <button class="column-action-btn" @click="openCreateDialog(col.key)">
                    <el-icon><Plus /></el-icon>
                  </button>
                </el-tooltip>
              </div>
            </div>

            <div class="column-body">
              <transition-group name="card" tag="div" class="card-list">
                <div
                  v-for="item in getItemsByColumn(col.key)"
                  :key="item.id"
                  class="kanban-card"
                  :class="{
                    'is-dragging': draggingId === item.id,
                    'is-overdue': isOverdue(item),
                    'is-resolved': !!item.resolved_at,
                    'severity-critical': item.severity === 'critical',
                    'severity-high': item.severity === 'high',
                    'severity-medium': item.severity === 'medium',
                    'severity-low': item.severity === 'low',
                  }"
                  draggable="true"
                  @click="openDetail(item)"
                  @dragstart="handleDragStart(item, $event)"
                  @dragend="handleDragEnd"
                >
                  <!-- 状态徽章 -->
                  <div
                    v-if="item.status"
                    class="card-status-badge"
                    :style="{
                      background: (item.status_color || '#94a3b8') + '22',
                      color: item.status_color || '#94a3b8',
                      borderColor: (item.status_color || '#94a3b8') + '55',
                    }"
                  >
                    <span class="status-dot" :style="{ background: item.status_color || '#94a3b8' }"></span>
                    {{ statusLabel(item.status) }}
                  </div>

                  <!-- 严重度徽章（客户问题） -->
                  <div
                    v-if="item.severity"
                    class="severity-badge"
                    :style="severityStyle(item.severity)"
                  >
                    {{ severityLabel(item.severity) }}
                    <span v-if="isOverdue(item)" class="overdue-tag">逾期</span>
                    <span v-else-if="item.resolved_at" class="resolved-tag">已解决</span>
                  </div>

                  <!-- 标题 -->
                  <div class="card-title-wrap">
                    <div class="card-title" :title="item.title">
                      {{ item.title }}
                    </div>
                  </div>

                  <!-- 标签 -->
                  <div v-if="item.tags && item.tags.length" class="card-tags">
                    <span v-for="t in item.tags.slice(0,3)" :key="t" class="tag-chip">#{{ t }}</span>
                  </div>

                  <!-- 卡片底部 -->
                  <div class="card-footer">
                    <div class="card-meta">
                      <span
                        class="meta-item meta-comments"
                        :title="`${item.comment_count || 0} 条评论，点击查看`"
                        @click.stop="openDetail(item)"
                      >
                        <el-icon><ChatDotRound /></el-icon>
                        <span>{{ item.comment_count || 0 }}</span>
                      </span>
                      <span v-if="item.due_at && !item.resolved_at" class="meta-due" :class="{ 'is-overdue': isOverdue(item) }">
                        <el-icon><AlarmClock /></el-icon>
                        <span>{{ formatDue(item.due_at) }}</span>
                      </span>
                      <span class="meta-time" :title="item.updated_at">
                        {{ formatTime(item.updated_at) }}
                      </span>
                    </div>
                    <div class="card-right">
                      <el-avatar
                        v-if="item.assignee"
                        :size="22"
                        :src="item.assignee.avatar"
                        class="assignee-avatar"
                        :title="item.assignee.name"
                      >
                        {{ avatarText(item.assignee.name) }}
                      </el-avatar>
                      <el-dropdown
                        trigger="click"
                        @command="(cmd) => handleCardCommand(cmd, item)"
                        @click.stop
                      >
                        <button class="card-menu-btn" @click.stop>
                          <el-icon><MoreFilled /></el-icon>
                        </button>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item command="status">
                              <el-icon><Flag /></el-icon>设置状态
                            </el-dropdown-item>
                            <el-dropdown-item command="assignee">
                              <el-icon><User /></el-icon>指派负责人
                            </el-dropdown-item>
                            <el-dropdown-item v-if="item.column === 'customer_issue' && !item.resolved_at" command="resolve">
                              <el-icon style="color:#10b981"><Check /></el-icon>
                              <span style="color:#10b981">标记已解决</span>
                            </el-dropdown-item>
                            <el-dropdown-item v-if="item.column === 'customer_issue' && item.resolved_at" command="reopen">
                              <el-icon><RefreshLeft /></el-icon>重新打开
                            </el-dropdown-item>
                            <el-dropdown-item command="comment" divided>
                              <el-icon><ChatDotRound /></el-icon>添加评论 ({{ item.comment_count || 0 }})
                            </el-dropdown-item>
                            <el-dropdown-item command="delete" divided>
                              <el-icon style="color: #ef4444"><Delete /></el-icon>
                              <span style="color: #ef4444">删除卡片</span>
                            </el-dropdown-item>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </div>
                  </div>

                  <div class="drag-handle" title="拖动换列">
                    <el-icon><Rank /></el-icon>
                  </div>
                </div>
              </transition-group>

              <button class="add-card-btn" @click="openCreateDialog(col.key)">
                <el-icon><Plus /></el-icon>
                <span>添加卡片</span>
              </button>

              <div v-if="getItemsByColumn(col.key).length === 0" class="empty-tip">
                暂无内容，点击 + 添加
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增卡片对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      :title="`新增卡片 - ${currentColumnName}`"
      width="500px"
      :close-on-click-modal="false"
      custom-class="rd-kanban-dialog"
    >
      <el-form :model="createForm" label-position="top">
        <el-form-item label="标题" required>
          <el-input
            v-model="createForm.title"
            placeholder="请输入卡片标题"
            maxlength="200"
            show-word-limit
            @keydown.enter="submitCreate"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="createForm.status" placeholder="可选" clearable style="width: 100%">
            <el-option
              v-for="opt in statusOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            >
              <span style="float: left">{{ opt.label }}</span>
              <span
                style="float: right; width: 10px; height: 10px; border-radius: 50%; background: #fff"
                :style="{ background: opt.color, marginTop: '7px' }"
              ></span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item v-if="createForm.column === 'customer_issue'" label="严重度">
          <el-select v-model="createForm.severity" placeholder="选择严重度" style="width: 100%">
            <el-option
              v-for="s in issueSeverity"
              :key="s.value"
              :label="s.label"
              :value="s.value"
            >
              <span style="float: left">{{ s.label }}</span>
              <span :style="{ float: 'right', width: '10px', height: '10px', borderRadius: '50%', background: s.color, marginTop: '7px' }"></span>
            </el-option>
          </el-select>
          <div class="form-hint">系统将根据严重度自动计算 SLA 截止时间（致命 4h / 严重 24h / 一般 72h / 轻微 7d）</div>
        </el-form-item>
        <el-form-item label="负责人">
          <el-select
            v-model="createForm.assignee_id"
            placeholder="可选"
            clearable
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="u in userOptions"
              :key="u.id"
              :label="u.name"
              :value="u.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-input
            v-model="createForm.tagsInput"
            placeholder="多个标签用英文逗号分隔"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" class="btn-gradient" @click="submitCreate" :loading="submitting">
          确定新增
        </el-button>
      </template>
    </el-dialog>

    <!-- 设置状态对话框 -->
    <el-dialog
      v-model="statusDialogVisible"
      title="设置状态"
      width="400px"
      custom-class="rd-kanban-dialog"
    >
      <el-radio-group v-model="pendingStatus" class="status-radio-group">
        <el-radio
          v-for="opt in statusOptions"
          :key="opt.value"
          :value="opt.value"
          border
          class="status-radio"
        >
          <span class="status-dot" :style="{ background: opt.color }"></span>
          {{ opt.label }}
        </el-radio>
      </el-radio-group>
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" class="btn-gradient" @click="submitStatus">保存</el-button>
      </template>
    </el-dialog>

    <!-- 指派负责人对话框 -->
    <el-dialog
      v-model="assigneeDialogVisible"
      title="指派负责人"
      width="420px"
      custom-class="rd-kanban-dialog"
    >
      <el-select
        v-model="pendingAssigneeId"
        placeholder="选择负责人"
        filterable
        clearable
        style="width: 100%"
      >
        <el-option
          v-for="u in userOptions"
          :key="u.id"
          :label="u.name"
          :value="u.id"
        />
      </el-select>
      <template #footer>
        <el-button @click="assigneeDialogVisible = false">取消</el-button>
        <el-button type="primary" class="btn-gradient" @click="submitAssignee">保存</el-button>
      </template>
    </el-dialog>

    <!-- 周报汇总对话框 -->
    <el-dialog
      v-model="weeklyDialogVisible"
      :title="`周报汇总`"
      width="780px"
      top="5vh"
      custom-class="weekly-summary-dialog"
    >
      <div class="weekly-toolbar">
        <div class="weekly-toolbar-left">
          <el-date-picker
            v-model="weeklyDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            size="default"
            style="width: 280px"
            @change="loadWeeklySummary"
          />
          <el-button size="default" @click="selectThisWeek" class="btn-outline">本周</el-button>
          <el-button size="default" @click="selectLastWeek" class="btn-outline">上周</el-button>
          <el-button size="default" @click="loadWeeklySummary" :loading="weeklyLoading" class="btn-outline">查询</el-button>
        </div>
        <el-button size="default" @click="copyWeeklyMarkdown" :disabled="!weeklyMarkdown">
          <el-icon><CopyDocument /></el-icon>复制 Markdown
        </el-button>
      </div>
      <div class="weekly-summary-info" v-if="weeklyRangeLabel">
        <span class="weekly-range-label">{{ weeklyRangeLabel }}</span>
        <el-tag size="small" type="info" effect="plain">共 {{ weeklyItems.length }} 篇</el-tag>
      </div>
      <div class="weekly-card-list" v-loading="weeklyLoading">
        <div v-if="weeklyItems.length === 0 && !weeklyLoading" class="weekly-empty">
          <el-empty description="该时间段暂无周报" />
        </div>
        <WeeklyReportCard
          v-for="item in weeklyItems"
          :key="item.id"
          :item="item"
        />
      </div>
    </el-dialog>

    <!-- 数据统计对话框 -->
    <el-dialog
      v-model="statsDialogVisible"
      :title="`项目数据统计 - ${currentProject?.name || ''}`"
      width="640px"
      custom-class="rd-kanban-dialog"
    >
      <div v-if="stats" class="stats-body">
        <div class="stat-cards">
          <div class="stat-card">
            <div class="stat-label">总卡片</div>
            <div class="stat-value">{{ stats.total }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">客户问题 - 未解决</div>
            <div class="stat-value" style="color:#f59e0b">{{ stats.open_issues.total }}</div>
          </div>
          <div class="stat-card" :class="{ 'is-warn': stats.open_issues.overdue.length }">
            <div class="stat-label">客户问题 - 逾期</div>
            <div class="stat-value" style="color:#ef4444">{{ stats.open_issues.overdue.length }}</div>
          </div>
        </div>

        <h4 class="stats-section-title">各列分布</h4>
        <div class="stats-columns">
          <div v-for="c in columns" :key="c.key" class="stats-col-row">
            <span class="col-name" :style="{ color: c.color }">● {{ c.name }}</span>
            <el-progress :percentage="stats.total ? Math.round((stats.by_column[c.key] || 0) / stats.total * 100) : 0" :stroke-width="10" :show-text="false" :color="c.color" />
            <span class="col-count">{{ stats.by_column[c.key] || 0 }}</span>
          </div>
        </div>

        <h4 class="stats-section-title">按指派人</h4>
        <div v-if="stats.by_assignee.length" class="stats-assignee">
          <div v-for="a in stats.by_assignee" :key="a.id" class="assignee-row">
            <span class="assignee-name">{{ a.name }}</span>
            <el-progress :percentage="stats.total ? Math.round(a.count / stats.total * 100) : 0" :stroke-width="8" :format="() => `${a.count} 张`" />
          </div>
        </div>
        <el-empty v-else description="尚无指派" :image-size="60" />

        <h4 v-if="stats.open_issues.overdue.length" class="stats-section-title" style="color:#ef4444">逾期客户问题</h4>
        <div v-if="stats.open_issues.overdue.length" class="stats-overdue">
          <div v-for="o in stats.open_issues.overdue" :key="o.id" class="overdue-row">
            <span class="overdue-title">{{ o.title }}</span>
            <span class="overdue-meta">{{ o.severity }} · 逾期 {{ o.overdue_hours }}h</span>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 卡片详情抽屉 -->
    <CardDetailDrawer
      v-if="detailItem"
      v-model:visible="detailVisible"
      :item-id="detailItem.id"
      :item="detailItem"
      :columns="columns"
      :status-options="statusOptions"
      :user-options="userOptions"
      @refresh="onDetailRefresh"
      @delete="onDetailDelete"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, ChatDotRound, MoreFilled, Flag, User, Delete, Rank, Check, RefreshLeft, Search, Document, DataAnalysis, CopyDocument, AlarmClock, Operation } from '@element-plus/icons-vue'
import rdKanbanService from '@/services/rdKanbanService'
import { apiService } from '@/services/api'
import CardDetailDrawer from './rd-kanban/CardDetailDrawer.vue'
import WeeklyReportCard from './rd-kanban/WeeklyReportCard.vue'

const loading = ref(false)
const submitting = ref(false)

const columns = ref([])
const statusOptions = ref([])
const issueSeverity = ref([])
const allItems = ref([])
const projectOptions = ref([])
const userOptions = ref([])

const currentProjectId = ref(null)
const currentProject = ref(null)
const columnCounts = ref({})
const filterAssignee = ref(null)
const filterKeyword = ref('')

const createDialogVisible = ref(false)
const createForm = reactive({
  title: '',
  column: null,
  status: null,
  assignee_id: null,
  severity: null,
  tagsInput: '',
})
const editingItem = ref(null)

const dragOverColumn = ref(null)
const draggingId = ref(null)
let draggedItem = null

const detailVisible = ref(false)
const detailItem = ref(null)

const statusDialogVisible = ref(false)
const pendingStatus = ref(null)

const assigneeDialogVisible = ref(false)
const pendingAssigneeId = ref(null)

const weeklyDialogVisible = ref(false)
const weeklyMarkdown = ref('')
const weeklyDateRange = ref([])
const weeklyItems = ref([])
const weeklyRangeLabel = ref('')
const weeklyLoading = ref(false)

const statsDialogVisible = ref(false)
const stats = ref(null)

const currentColumnName = computed(() => {
  const col = columns.value.find((c) => c.key === createForm.column)
  return col ? col.name : ''
})

function getItemsByColumn(key) {
  return allItems.value
    .filter((it) => it.column === key)
    .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
}

function statusLabel(value) {
  const opt = statusOptions.value.find((s) => s.value === value)
  return opt ? opt.label : value
}
function severityLabel(value) {
  const opt = issueSeverity.value.find((s) => s.value === value)
  return opt ? opt.label : value
}
function severityStyle(value) {
  const opt = issueSeverity.value.find((s) => s.value === value)
  const color = opt ? opt.color : '#94a3b8'
  return {
    background: color + '22',
    color,
    borderColor: color + '55',
  }
}
function isOverdue(item) {
  if (!item.due_at || item.resolved_at) return false
  return new Date(item.due_at) < new Date()
}
function formatDue(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diff = (d - now) / 1000
  if (diff < 0) return '已逾期'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分后`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 时后`
  if (diff < 604800) return `${Math.floor(diff / 86400)} 天后`
  return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}
function avatarText(name) {
  if (!name) return '?'
  return name.slice(-2)
}
function formatTime(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    const now = new Date()
    const diff = (now - d) / 1000
    if (diff < 60) return '刚刚'
    if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
    if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
    if (diff < 604800) return `${Math.floor(diff / 86400)} 天前`
    return `${d.getMonth() + 1}/${d.getDate()}`
  } catch {
    return ''
  }
}

async function loadProjects() {
  try {
    const res = await apiService.projects.getList({ page: 1, per_page: 200 })
    const list = res.projects || res.data || res.items || res || []
    projectOptions.value = list.map((p) => ({
      id: p.id,
      name: p.name,
      code: p.code,
    }))
    if (!currentProjectId.value && projectOptions.value.length) {
      currentProjectId.value = projectOptions.value[0].id
    }
  } catch (e) {
    console.error('加载项目列表失败', e)
  }
}
async function loadUsers() {
  try {
    const res = await apiService.users.getList()
    const list = res.users || res.data || res.items || res || []
    userOptions.value = list.map((u) => ({
      id: u.id,
      name: (u.first_name || '') + (u.last_name || '') || u.username || u.name || `#${u.id}`,
      username: u.username,
    }))
  } catch (e) {
    console.error('加载用户列表失败', e)
  }
}
async function loadData() {
  if (!currentProjectId.value) return
  loading.value = true
  try {
    const params = {}
    if (filterAssignee.value) params.assignee_id = filterAssignee.value
    if (filterKeyword.value.trim()) params.keyword = filterKeyword.value.trim()
    const res = await rdKanbanService.list(currentProjectId.value, params)
    columns.value = res.columns || []
    statusOptions.value = res.status_options || []
    issueSeverity.value = res.issue_severity || []
    allItems.value = res.items || []
    columnCounts.value = res.column_counts || {}
    currentProject.value = res.project || null
  } catch (e) {
    console.error('加载看板数据失败', e)
    ElMessage.error('加载看板数据失败')
  } finally {
    loading.value = false
  }
}
function handleProjectChange() {
  loadData()
}

// ----- 新增卡片 -----
function openCreateDialog(columnKey) {
  createForm.column = columnKey
  createForm.title = ''
  createForm.status = null
  createForm.assignee_id = null
  createForm.severity = columnKey === 'customer_issue' ? 'medium' : null
  createForm.tagsInput = ''
  createDialogVisible.value = true
  nextTick(() => {
    const input = document.querySelector('.rd-kanban-dialog .el-input__inner')
    if (input) input.focus()
  })
}
async function submitCreate() {
  if (!createForm.title || !createForm.title.trim()) {
    ElMessage.warning('请输入标题')
    return
  }
  if (!currentProjectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  submitting.value = true
  try {
    const status = createForm.status
    const statusOpt = statusOptions.value.find((s) => s.value === status)
    const tags = createForm.tagsInput
      ? createForm.tagsInput.split(',').map((s) => s.trim()).filter(Boolean)
      : []
    await rdKanbanService.create({
      project_id: currentProjectId.value,
      column: createForm.column,
      title: createForm.title.trim(),
      status: status || null,
      status_color: statusOpt ? statusOpt.color : null,
      assignee_id: createForm.assignee_id || null,
      severity: createForm.severity || null,
      tags,
    })
    ElMessage.success('已新增卡片')
    createDialogVisible.value = false
    await loadData()
  } catch (e) {
    console.error(e)
    ElMessage.error('新增失败：' + (e?.response?.data?.error || e.message))
  } finally {
    submitting.value = false
  }
}

// ----- 卡片菜单 -----
async function handleCardCommand(cmd, item) {
  if (cmd === 'delete') {
    try {
      await ElMessageBox.confirm('确定要删除这张卡片吗？', '提示', {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        confirmButtonClass: 'el-button--danger',
      })
      await rdKanbanService.remove(item.id)
      ElMessage.success('已删除')
      allItems.value = allItems.value.filter((it) => it.id !== item.id)
    } catch (e) {
      if (e !== 'cancel' && e?.message) ElMessage.error('删除失败')
    }
  } else if (cmd === 'status') {
    editingItem.value = item
    pendingStatus.value = item.status || null
    statusDialogVisible.value = true
  } else if (cmd === 'assignee') {
    editingItem.value = item
    pendingAssigneeId.value = item.assignee?.id || null
    assigneeDialogVisible.value = true
  } else if (cmd === 'resolve') {
    try {
      await rdKanbanService.resolveIssue(item.id)
      ElMessage.success('已标记为已解决')
      await loadData()
    } catch (e) {
      ElMessage.error('操作失败')
    }
  } else if (cmd === 'reopen') {
    try {
      await rdKanbanService.reopenIssue(item.id)
      ElMessage.success('已重新打开')
      await loadData()
    } catch (e) {
      ElMessage.error('操作失败')
    }
  } else if (cmd === 'comment') {
    try {
      const { value } = await ElMessageBox.prompt(
        '发表评论（同步写入评论库，打开详情抽屉可见）',
        '添加评论',
        {
          inputPlaceholder: '请输入评论内容...',
          inputType: 'textarea',
          confirmButtonText: '提交',
          cancelButtonText: '取消',
          inputValidator: (val) => {
            if (!val || !val.trim()) return '评论内容不能为空'
            if (val.length > 2000) return '评论内容最多 2000 字'
            return true
          },
        }
      )
      if (value && value.trim()) {
        await rdKanbanService.addComment(item.id, { content: value.trim() })
        const newCount = (item.comment_count || 0) + 1
        item.comment_count = newCount
        ElMessage.success('评论已添加')
      }
    } catch (e) {
      if (e === 'cancel') return
      if (typeof e === 'string') return
      const msg = e?.response?.data?.error || e?.message || '评论失败'
      ElMessage.error(msg)
    }
  }
}
async function submitStatus() {
  if (!editingItem.value) return
  const status = pendingStatus.value
  const opt = statusOptions.value.find((s) => s.value === status)
  try {
    await rdKanbanService.update(editingItem.value.id, {
      status: status || null,
      status_color: opt ? opt.color : null,
    })
    ElMessage.success('已更新状态')
    statusDialogVisible.value = false
    await loadData()
  } catch (e) {
    ElMessage.error('更新失败')
  }
}
async function submitAssignee() {
  if (!editingItem.value) return
  try {
    await rdKanbanService.update(editingItem.value.id, { assignee_id: pendingAssigneeId.value || null })
    ElMessage.success('已更新负责人')
    assigneeDialogVisible.value = false
    await loadData()
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

// ----- 拖拽换列 -----
function handleDragStart(item, event) {
  draggingId.value = item.id
  draggedItem = item
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', String(item.id))
  }
}
function handleDragEnd() {
  draggingId.value = null
  draggedItem = null
  dragOverColumn.value = null
}
function handleDragOver(columnKey, event) {
  event.preventDefault()
  if (event.dataTransfer) event.dataTransfer.dropEffect = 'move'
  dragOverColumn.value = columnKey
}
function handleDragLeave(columnKey) {
  if (dragOverColumn.value === columnKey) {
    dragOverColumn.value = null
  }
}
async function handleDrop(targetColumn, event) {
  event.preventDefault()
  dragOverColumn.value = null
  const itemId = Number(event.dataTransfer?.getData('text/plain')) || draggingId.value
  if (!itemId) return
  const item = allItems.value.find((it) => it.id === itemId)
  if (!item) return
  if (item.column === targetColumn) return
  const oldColumn = item.column
  item.column = targetColumn
  const targetItems = getItemsByColumn(targetColumn)
  const maxOrder = targetItems.reduce((m, it) => Math.max(m, it.sort_order || 0), 0)
  item.sort_order = maxOrder + 10
  try {
    await rdKanbanService.sort([
      { id: item.id, column: targetColumn, sort_order: item.sort_order },
    ])
    ElMessage.success(`已移至「${columns.value.find((c) => c.key === targetColumn)?.name}」`)
  } catch (e) {
    item.column = oldColumn
    ElMessage.error('移动失败')
  }
}

// ----- 周报汇总 -----
function getLastWeekRange() {
  const today = new Date()
  const dayOfWeek = today.getDay() || 7
  const thisMonday = new Date(today)
  thisMonday.setDate(today.getDate() - dayOfWeek + 1)
  const lastMonday = new Date(thisMonday)
  lastMonday.setDate(thisMonday.getDate() - 7)
  const lastSunday = new Date(thisMonday)
  lastSunday.setDate(thisMonday.getDate() - 1)
  const fmt = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  return [fmt(lastMonday), fmt(lastSunday)]
}
function getThisWeekRange() {
  const today = new Date()
  const dayOfWeek = today.getDay() || 7
  const thisMonday = new Date(today)
  thisMonday.setDate(today.getDate() - dayOfWeek + 1)
  const thisSunday = new Date(thisMonday)
  thisSunday.setDate(thisMonday.getDate() + 6)
  const fmt = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  return [fmt(thisMonday), fmt(thisSunday)]
}
async function openWeeklySummary() {
  if (!currentProjectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  if (!weeklyDateRange.value || weeklyDateRange.value.length !== 2) {
    weeklyDateRange.value = getLastWeekRange()
  }
  weeklyDialogVisible.value = true
  await loadWeeklySummary()
}
async function loadWeeklySummary() {
  if (!weeklyDateRange.value || weeklyDateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }
  weeklyLoading.value = true
  try {
    const [start, end] = weeklyDateRange.value
    const r = await rdKanbanService.weeklySummary(currentProjectId.value, {
      start_date: start,
      end_date: end,
    })
    weeklyMarkdown.value = r.markdown || ''
    weeklyItems.value = r.items || []
    weeklyRangeLabel.value = r.range_label || `${start} ~ ${end}`
  } catch (e) {
    ElMessage.error('周报加载失败')
  } finally {
    weeklyLoading.value = false
  }
}
function selectLastWeek() {
  weeklyDateRange.value = getLastWeekRange()
  loadWeeklySummary()
}
function selectThisWeek() {
  weeklyDateRange.value = getThisWeekRange()
  loadWeeklySummary()
}
async function copyWeeklyMarkdown() {
  if (!weeklyMarkdown.value) return
  try {
    await navigator.clipboard.writeText(weeklyMarkdown.value)
    ElMessage.success('已复制 Markdown')
  } catch {
    ElMessage.warning('复制失败')
  }
}

// ----- 数据统计 -----
async function openStats() {
  if (!currentProjectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  statsDialogVisible.value = true
  try {
    const r = await rdKanbanService.stats(currentProjectId.value)
    stats.value = r
  } catch (e) {
    ElMessage.error('统计加载失败')
  }
}

onMounted(async () => {
  await loadProjects()
  await loadUsers()
  await loadData()
})

// ----- 详情抽屉 -----
function openDetail(item) {
  if (draggingId.value) return
  detailItem.value = item
  detailVisible.value = true
}
function onDetailRefresh() {
  loadData()
}
async function onDetailDelete(item) {
  if (!item) return
  allItems.value = allItems.value.filter((it) => it.id !== item.id)
  ElMessage.success('已删除卡片')
  detailItem.value = null
  detailVisible.value = false
}
</script>

<style scoped>
.rd-management {
  --bg-primary: #f5f7fa;
  --glass-bg: rgba(255, 255, 255, 0.75);
  --glass-border: rgba(255, 255, 255, 0.45);
  --shadow-soft: 0 4px 16px rgba(15, 23, 42, 0.06);
  --shadow-card: 0 2px 8px rgba(15, 23, 42, 0.08);
  --shadow-hover: 0 6px 20px rgba(15, 23, 42, 0.12);
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
  --gradient-1: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
  --gradient-2: linear-gradient(135deg, #ec4899 0%, #f59e0b 100%);
  padding: 0;
  min-height: calc(100vh - 60px);
  background: var(--bg-primary);
}

/* 页面头部 */
.page-header {
  position: relative;
  padding: 20px 24px 18px;
  background: var(--glass-bg);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid var(--glass-border);
  overflow: hidden;
}
.header-bg-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}
.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.4;
}
.orb-1 {
  width: 240px;
  height: 240px;
  background: var(--gradient-1);
  top: -100px;
  left: -60px;
}
.orb-2 {
  width: 200px;
  height: 200px;
  background: var(--gradient-2);
  top: -80px;
  right: 5%;
}
.header-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.header-title {
  display: flex;
  align-items: center;
  gap: 14px;
}
.title-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--gradient-1);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(14, 165, 233, 0.35);
}
.title-icon {
  color: #ffffff;
  font-size: 26px;
}
.title-svg-icon {
  width: 30px;
  height: 30px;
}
.title-svg-icon .kanban-board {
  fill: rgba(255, 255, 255, 0.2);
  stroke: rgba(255, 255, 255, 0.9);
  stroke-width: 1.5;
}
.title-svg-icon .kanban-col {
  fill: rgba(255, 255, 255, 0.18);
}
.title-svg-icon .kanban-card {
  fill: rgba(255, 255, 255, 0.7);
  animation: card-pulse 2.4s ease-in-out infinite;
}
.title-svg-icon .card-2 {
  animation-delay: 0.4s;
}
.title-svg-icon .card-3 {
  animation-delay: 0.8s;
}
.title-svg-icon .card-4 {
  animation-delay: 1.2s;
}
@keyframes card-pulse {
  0%, 100% { opacity: 0.55; }
  50% { opacity: 1; }
}
.title-text h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}
.title-text .subtitle {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--text-secondary);
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.project-selector {
  width: 220px;
}
.project-selector :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(8px);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.btn-gradient {
  background: var(--gradient-1) !important;
  border: none !important;
  color: #fff !important;
  font-weight: 500;
  border-radius: 8px;
  padding: 8px 16px;
  transition: all 0.2s ease;
}
.btn-gradient:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(14, 165, 233, 0.4);
}

/* 看板容器 */
.kanban-container {
  padding: 18px 20px 24px;
}
.kanban-board-scroll {
  overflow-x: auto;
  padding-bottom: 12px;
  scrollbar-width: thin;
}
.kanban-board-scroll::-webkit-scrollbar {
  height: 10px;
}
.kanban-board-scroll::-webkit-scrollbar-thumb {
  background: rgba(15, 23, 42, 0.15);
  border-radius: 6px;
}
.kanban-columns {
  display: flex;
  gap: 14px;
  min-width: max-content;
  align-items: flex-start;
}
.kanban-column {
  width: 256px;
  min-width: 256px;
  background: var(--glass-bg);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 220px);
  transition: all 0.2s ease;
  box-shadow: var(--shadow-soft);
}
.kanban-column.drag-over {
  border-color: #0ea5e9;
  background: rgba(14, 165, 233, 0.06);
  box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.25);
}
.column-header {
  padding: 12px 14px 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}
.column-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}
.column-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--col-color, #0ea5e9);
  box-shadow: 0 0 8px var(--col-color, #0ea5e9);
}
.column-name {
  letter-spacing: 0.3px;
}
.column-count :deep(.el-badge__content) {
  background: rgba(15, 23, 42, 0.08);
  color: var(--text-secondary);
  border: none;
  font-weight: 600;
  height: 18px;
  line-height: 18px;
  padding: 0 6px;
}
.column-actions {
  display: flex;
  gap: 4px;
}
.column-action-btn {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  border: none;
  background: rgba(15, 23, 42, 0.05);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}
.column-action-btn:hover {
  background: rgba(14, 165, 233, 0.15);
  color: #0ea5e9;
  transform: scale(1.08);
}
.column-body {
  flex: 1;
  overflow-y: auto;
  padding: 10px 10px 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.column-body::-webkit-scrollbar {
  width: 6px;
}
.column-body::-webkit-scrollbar-thumb {
  background: rgba(15, 23, 42, 0.12);
  border-radius: 3px;
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 卡片 */
.kanban-card {
  position: relative;
  background: #fff;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 10px;
  padding: 10px 10px 8px;
  box-shadow: var(--shadow-card);
  cursor: grab;
  transition: all 0.18s ease;
  user-select: none;
}
.kanban-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-1px);
  border-color: rgba(14, 165, 233, 0.35);
}
.kanban-card.is-dragging {
  opacity: 0.5;
  transform: scale(0.97) rotate(-1deg);
  cursor: grabbing;
}
.kanban-card:active {
  cursor: grabbing;
}
/* 卡片状态徽章：与其他页面的 el-tag / status-pill 风格保持一致（浅色背景 + 边框 + 主色文字） */
.card-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 10px;
  border: 1px solid;
  margin-bottom: 6px;
  white-space: nowrap;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}
.status-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.card-title-wrap {
  margin-bottom: 8px;
}
.card-title {
  font-size: 13px;
  line-height: 1.45;
  color: var(--text-primary);
  font-weight: 500;
  word-break: break-word;
  white-space: pre-wrap;
  cursor: text;
  min-height: 19px;
}
.card-title:hover {
  background: rgba(14, 165, 233, 0.06);
  border-radius: 4px;
}
.card-title-input {
  width: 100%;
  border: 1px solid #0ea5e9;
  border-radius: 4px;
  padding: 3px 6px;
  font-size: 13px;
  line-height: 1.45;
  color: var(--text-primary);
  background: #fff;
  outline: none;
  font-family: inherit;
  font-weight: 500;
}
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 4px;
}
.card-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 11px;
  color: var(--text-muted);
  min-width: 0;
}
.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}
.meta-item .el-icon {
  font-size: 12px;
}
.meta-comments {
  cursor: pointer;
  padding: 1px 4px;
  border-radius: 4px;
  transition: all 0.15s ease;
}
.meta-comments:hover {
  background: rgba(14, 165, 233, 0.12);
  color: #0ea5e9;
}
.meta-time {
  font-size: 10px;
  color: var(--text-muted);
  white-space: nowrap;
}
.card-right {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}
.assignee-avatar {
  border: 1.5px solid #fff;
  box-shadow: 0 0 0 1px rgba(15, 23, 42, 0.08);
}
.card-menu-btn {
  width: 22px;
  height: 22px;
  border-radius: 4px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.15s ease;
}
.kanban-card:hover .card-menu-btn,
.card-menu-btn:focus {
  opacity: 1;
}
.card-menu-btn:hover {
  background: rgba(15, 23, 42, 0.08);
  color: var(--text-primary);
}
.drag-handle {
  position: absolute;
  top: 8px;
  right: 6px;
  color: var(--text-muted);
  opacity: 0;
  transition: opacity 0.15s ease;
  pointer-events: none;
  font-size: 12px;
}
.kanban-card:hover .drag-handle {
  opacity: 0.6;
}

/* 新增占位按钮 */
.add-card-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px;
  border-radius: 8px;
  border: 1px dashed rgba(15, 23, 42, 0.15);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 12px;
  transition: all 0.15s ease;
  margin-top: 4px;
}
.add-card-btn:hover {
  border-color: #0ea5e9;
  color: #0ea5e9;
  background: rgba(14, 165, 233, 0.05);
}
.empty-tip {
  text-align: center;
  color: var(--text-muted);
  font-size: 12px;
  padding: 18px 0;
  opacity: 0.7;
}

/* 卡片动画 */
.card-enter-active,
.card-leave-active {
  transition: all 0.25s ease;
}
.card-enter-from {
  opacity: 0;
  transform: translateY(-6px);
}
.card-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
.card-move {
  transition: transform 0.25s ease;
}

/* 状态单选 */
.status-radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}
.status-radio-group :deep(.el-radio) {
  width: 100%;
  margin-right: 0;
  padding: 10px 14px;
  border-radius: 8px;
}
.status-radio :deep(.el-radio__label) {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

/* 响应式 */
@media (max-width: 768px) {
  .project-selector {
    width: 100%;
  }
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
}

/* ---------- 新增：筛选、按钮、严重度、统计等样式 ---------- */
.filter-selector {
  width: 160px;
}
.keyword-input {
  width: 180px;
}
.btn-outline {
  background: rgba(255, 255, 255, 0.8) !important;
  border: 1px solid rgba(15, 23, 42, 0.12) !important;
  color: #0f172a !important;
  border-radius: 8px !important;
  font-weight: 500;
}
.btn-outline:hover {
  background: rgba(14, 165, 233, 0.08) !important;
  border-color: #0ea5e9 !important;
  color: #0ea5e9 !important;
}

.form-hint {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
  line-height: 1.4;
}

.severity-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 10px;
  border: 1px solid;
  margin-bottom: 4px;
  white-space: nowrap;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}
.overdue-tag,
.resolved-tag {
  display: inline-block;
  margin-left: 4px;
  padding: 0 5px;
  border-radius: 6px;
  font-size: 10px;
  background: rgba(255, 255, 255, 0.6);
}
.kanban-card.is-overdue {
  border-color: rgba(239, 68, 68, 0.5);
  background: linear-gradient(180deg, #fff 0%, #fef2f2 100%);
}
.kanban-card.is-resolved {
  opacity: 0.65;
}
.kanban-card.severity-critical {
  border-left: 3px solid #dc2626;
}
.kanban-card.severity-high {
  border-left: 3px solid #ef4444;
}
.kanban-card.severity-medium {
  border-left: 3px solid #f59e0b;
}
.kanban-card.severity-low {
  border-left: 3px solid #10b981;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
  margin-bottom: 6px;
}
.tag-chip {
  font-size: 10px;
  padding: 1px 6px;
  background: rgba(14, 165, 233, 0.08);
  color: #0284c7;
  border-radius: 8px;
  font-weight: 500;
}

.meta-due {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  color: #94a3b8;
}
.meta-due.is-overdue {
  color: #ef4444;
  font-weight: 600;
}
.meta-due .el-icon {
  font-size: 12px;
}

/* 周报汇总对话框 - body 可滚动 */
:deep(.weekly-summary-dialog) .el-dialog__body {
  max-height: calc(100vh - 180px);
  overflow-y: auto;
  padding: 16px 20px;
}
:deep(.weekly-summary-dialog) .el-dialog__header {
  padding-bottom: 12px;
}

/* 周报汇总 */
.weekly-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}
.weekly-toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.weekly-summary-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  padding: 8px 14px;
  background: rgba(59, 130, 246, 0.06);
  border-radius: 8px;
}
.weekly-range-label {
  font-size: 13px;
  font-weight: 600;
  color: #1e40af;
}
.weekly-card-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.weekly-empty {
  padding: 20px 0;
}

/* 数据统计 */
.stats-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.stat-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
.stat-card {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.06) 0%, rgba(99, 102, 241, 0.06) 100%);
  border: 1px solid rgba(14, 165, 233, 0.15);
  border-radius: 10px;
  padding: 12px 14px;
}
.stat-card.is-warn {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(220, 38, 38, 0.08) 100%);
  border-color: rgba(239, 68, 68, 0.3);
}
.stat-label {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}
.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #0ea5e9;
}
.stats-section-title {
  margin: 4px 0 8px;
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
}
.stats-columns {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.stats-col-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.stats-col-row .col-name {
  width: 160px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}
.stats-col-row .el-progress {
  flex: 1;
}
.stats-col-row .col-count {
  font-size: 12px;
  color: #475569;
  min-width: 32px;
  text-align: right;
  font-weight: 600;
}
.stats-assignee {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.assignee-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.assignee-name {
  width: 100px;
  font-size: 12px;
  color: #0f172a;
  font-weight: 500;
}
.assignee-row .el-progress {
  flex: 1;
}
.stats-overdue {
  background: rgba(239, 68, 68, 0.05);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.overdue-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}
.overdue-title {
  color: #0f172a;
  font-weight: 500;
}
.overdue-meta {
  color: #ef4444;
  font-weight: 600;
}
</style>

<style>
/* 弹窗全局样式（scoped 限制无法影响 dialog） */
.rd-kanban-dialog {
  border-radius: 14px !important;
  overflow: hidden;
}
.rd-kanban-dialog .el-dialog__header {
  background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
  color: #fff;
  margin: 0;
  padding: 16px 20px;
}
.rd-kanban-dialog .el-dialog__title {
  color: #fff !important;
  font-weight: 600;
}
.rd-kanban-dialog .el-dialog__headerbtn .el-dialog__close {
  color: #fff !important;
}
.rd-kanban-dialog .el-dialog__body {
  padding: 20px 22px;
}
.rd-kanban-dialog .el-dialog__footer {
  padding: 12px 22px 18px;
  border-top: 1px solid rgba(15, 23, 42, 0.06);
}

/* 项目选择器下拉弹窗 — 浅色主题，覆盖 Login.vue 中的黑色全局样式 */
.project-selector-popper.el-popper {
  background: rgba(255, 255, 255, 0.98) !important;
  border: 1px solid rgba(226, 232, 240, 0.8) !important;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12) !important;
}
.project-selector-popper .el-select-dropdown__item {
  color: #1e293b !important;
}
.project-selector-popper .el-select-dropdown__item.hover,
.project-selector-popper .el-select-dropdown__item:hover {
  background: rgba(56, 189, 248, 0.1) !important;
  color: #0ea5e9 !important;
}
.project-selector-popper .el-select-dropdown__item.selected {
  background: rgba(56, 189, 248, 0.15) !important;
  color: #0284c7 !important;
  font-weight: 600;
}
.project-selector-popper .el-popper__arrow::before {
  background: rgba(255, 255, 255, 0.98) !important;
  border-color: rgba(226, 232, 240, 0.8) !important;
}
</style>
