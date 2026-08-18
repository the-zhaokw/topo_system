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
            <svg class="title-svg-icon" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
              <rect class="kanban-board" x="6" y="10" width="52" height="44" rx="4" />
              <rect class="kanban-col" x="10" y="14" width="14" height="36" rx="2" />
              <rect class="kanban-col" x="26" y="14" width="14" height="36" rx="2" />
              <rect class="kanban-col" x="42" y="14" width="14" height="36" rx="2" />
              <rect class="kanban-card card-1" x="11" y="17" width="12" height="6" rx="1" />
              <rect class="kanban-card card-2" x="11" y="25" width="12" height="6" rx="1" />
              <rect class="kanban-card card-3" x="27" y="17" width="12" height="6" rx="1" />
              <rect class="kanban-card card-4" x="43" y="17" width="12" height="6" rx="1" />
            </svg>
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
            @change="handleProjectChange"
            filterable
          >
            <el-option
              v-for="p in projectOptions"
              :key="p.id"
              :label="`${p.code ? '[' + p.code + '] ' : ''}${p.name}`"
              :value="p.id"
            />
          </el-select>
          <el-button class="btn-gradient" @click="loadData" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
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
                  :class="{ 'is-dragging': draggingId === item.id }"
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

                  <!-- 标题 -->
                  <div class="card-title-wrap">
                    <div
                      class="card-title"
                      :title="item.title"
                    >
                      {{ item.title }}
                    </div>
                  </div>

                  <!-- 卡片底部 -->
                  <div class="card-footer">
                    <div class="card-meta">
                      <span class="meta-item" :title="`${item.comment_count || 0} 条评论`">
                        <el-icon><ChatDotRound /></el-icon>
                        <span>{{ item.comment_count || 0 }}</span>
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

                  <!-- 拖拽手柄 -->
                  <div class="drag-handle" title="拖动换列">
                    <el-icon><Rank /></el-icon>
                  </div>
                </div>
              </transition-group>

              <!-- 新增占位按钮 -->
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
      width="460px"
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
    <!-- 卡片详情抽屉 -->
    <CardDetailDrawer
      v-if="detailItem"
      v-model:visible="detailVisible"
      :item-id="detailItem.id"
      :item="detailItem"
      :columns="columns"
      @refresh="onDetailRefresh"
      @delete="onDetailDelete"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, ChatDotRound, MoreFilled, Flag, User, Delete, Rank } from '@element-plus/icons-vue'
import rdKanbanService from '@/services/rdKanbanService'
import { apiService } from '@/services/api'
import CardDetailDrawer from './rd-kanban/CardDetailDrawer.vue'

const loading = ref(false)
const submitting = ref(false)

const columns = ref([])
const statusOptions = ref([])
const allItems = ref([])
const projectOptions = ref([])
const userOptions = ref([])

const currentProjectId = ref(null)
const currentProject = ref(null)

const createDialogVisible = ref(false)
const createForm = reactive({
  title: '',
  column: null,
  status: null,
  assignee_id: null,
})

const editingItem = ref(null)

const dragOverColumn = ref(null)
const draggingId = ref(null)
let draggedItem = null

// 详情抽屉
const detailVisible = ref(false)
const detailItem = ref(null)

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
      name:
        (u.first_name || '') + (u.last_name || '') || u.username || u.name || `#${u.id}`,
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
    const res = await rdKanbanService.list(currentProjectId.value)
    columns.value = res.columns || []
    statusOptions.value = res.status_options || []
    allItems.value = res.items || []
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
    await rdKanbanService.create({
      project_id: currentProjectId.value,
      column: createForm.column,
      title: createForm.title.trim(),
      status: status || null,
      status_color: statusOpt ? statusOpt.color : null,
      assignee_id: createForm.assignee_id || null,
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
    // 简单实现：弹窗让用户选择
    try {
      const { value } = await ElMessageBox.prompt(
        '请输入负责人用户 ID（留空清除）',
        '指派负责人',
        {
          inputValue: item.assignee?.id ? String(item.assignee.id) : '',
          inputPattern: /^$|^\d+$/,
          inputErrorMessage: '请输入数字用户 ID',
        }
      )
      const newId = value ? Number(value) : null
      await rdKanbanService.update(item.id, { assignee_id: newId })
      ElMessage.success('已更新负责人')
      await loadData()
    } catch (e) {
      if (e !== 'cancel' && e?.message) {
        console.error(e)
      }
    }
  } else if (cmd === 'comment') {
    try {
      const { value } = await ElMessageBox.prompt('添加评论（仅计数 +1）', '评论', {
        inputPlaceholder: '评论内容...',
        confirmButtonText: '提交',
      })
      if (value && value.trim()) {
        const newCount = (item.comment_count || 0) + 1
        await rdKanbanService.update(item.id, { comment_count: newCount })
        item.comment_count = newCount
        ElMessage.success('评论已添加')
      }
    } catch (e) {
      if (e !== 'cancel' && e?.message) console.error(e)
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
  // 计算新列 sort_order
  const targetItems = getItemsByColumn(targetColumn)
  const maxOrder = targetItems.reduce((m, it) => Math.max(m, it.sort_order || 0), 0)
  item.sort_order = maxOrder + 10
  try {
    await rdKanbanService.sort([
      { id: item.id, column: targetColumn, sort_order: item.sort_order },
    ])
    ElMessage.success(`已移至「${columns.value.find((c) => c.key === targetColumn)?.name}」`)
  } catch (e) {
    // 回滚
    item.column = oldColumn
    ElMessage.error('移动失败')
  }
}

onMounted(async () => {
  await loadProjects()
  await loadUsers()
  await loadData()
})

// ----- 详情抽屉 -----
function openDetail(item) {
  // 不在拖拽中才打开（避免拖完误触发）
  if (draggingId.value) return
  detailItem.value = item
  detailVisible.value = true
}
function onDetailRefresh() {
  // 局部刷新：从后端重新拉取项目数据以同步评论数等
  loadData()
}
async function onDetailDelete(item) {
  // 由抽屉触发的删除：直接同步移除
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
</style>
