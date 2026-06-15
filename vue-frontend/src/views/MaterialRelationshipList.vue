<template>
  <div class="relationship-list-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Connection /></el-icon>
          </div>
          <div class="title-text">
            <h1>物料关系管理</h1>
            <p class="subtitle">管理物料之间的父子、替代、组合等关系</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="openCreateDialog" class="btn-gradient">
            <el-icon><Plus /></el-icon>
            新增关系
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-total">
            <div class="stat-icon-wrapper stat-icon-wrapper-total">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ totalCount }}</div>
              <div class="stat-label">关系总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-parent">
            <div class="stat-icon-wrapper stat-icon-wrapper-parent">
              <el-icon><Share /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ parentChildCount }}</div>
              <div class="stat-label">父子关系</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-alternative">
            <div class="stat-icon-wrapper stat-icon-wrapper-alternative">
              <el-icon><Switch /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ alternativeCount }}</div>
              <div class="stat-label">替代关系</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-combination">
            <div class="stat-icon-wrapper stat-icon-wrapper-combination">
              <el-icon><Grid /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ combinationCount }}</div>
              <div class="stat-label">组合关系</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索筛选区域 -->
    <div class="filter-section animate-fade-in-up delay-200">
      <el-card class="filter-card glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Search /></el-icon>
              搜索条件
            </span>
          </div>
        </template>
        <el-form :model="searchForm" inline class="filter-form">
          <el-form-item label="父项序列号">
            <el-input v-model="searchForm.parent_sn" placeholder="请输入父项序列号" clearable class="filter-input"></el-input>
          </el-form-item>
          <el-form-item label="子项序列号">
            <el-input v-model="searchForm.child_sn" placeholder="请输入子项序列号" clearable class="filter-input"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch" class="btn-gradient">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="resetSearch" class="btn-secondary">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 关系列表区域 -->
    <div class="content-section animate-fade-in-up delay-300">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="table-header">
            <div class="table-title">
              <el-icon><List /></el-icon>
              <h3>关系列表</h3>
              <span class="total-count">共 {{ filteredRelationships.length }} 条记录</span>
            </div>
          </div>
        </template>

        <el-table :data="paginatedRelationships" v-loading="loading" stripe class="custom-table" style="width: 100%">
          <el-table-column prop="parent_sn" label="父项序列号" width="180">
            <template #default="{ row }">
              <div class="item-info">
                <div class="item-name">{{ row.parent_sn }}</div>
                <el-tag size="small" :type="getTypeTag(row.parent_type)" effect="light" class="type-tag">
                  {{ getTypeText(row.parent_type) }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="child_sn" label="子项序列号" width="180">
            <template #default="{ row }">
              <div class="item-info">
                <div class="item-name">{{ row.child_sn }}</div>
                <el-tag size="small" :type="getTypeTag(row.child_type)" effect="light" class="type-tag">
                  {{ getTypeText(row.child_type) }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="slot_port_info" label="槽位/端口信息" width="150" align="center">
            <template #default="{ row }">
              <span class="slot-info">{{ row.slot_port_info || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180" align="center">
            <template #default="{ row }">
              <div class="timestamp">
                <div class="time-main">{{ formatDate(row.created_at) }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="danger" link size="small" @click="deleteRelationship(row.id)" class="delete-btn">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-section">
          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="currentPage"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredRelationships.length">
          </el-pagination>
        </div>
      </el-card>
    </div>

    <!-- 新增关系对话框 -->
    <el-dialog title="新增物料关系" v-model="dialogVisible" width="500px" @close="resetForm" class="custom-dialog">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" class="dialog-form">
        <el-form-item label="父项序列号" prop="parent_sn">
          <el-input v-model="form.parent_sn" placeholder="请输入父项序列号" prefix-icon="Connection"></el-input>
        </el-form-item>
        <el-form-item label="父项类型" prop="parent_type">
          <el-select v-model="form.parent_type" placeholder="请选择父项类型" style="width: 100%">
            <el-option label="设备" value="equipment"></el-option>
            <el-option label="板卡" value="board"></el-option>
            <el-option label="模块" value="module"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="子项序列号" prop="child_sn">
          <el-input v-model="form.child_sn" placeholder="请输入子项序列号" prefix-icon="Connection"></el-input>
        </el-form-item>
        <el-form-item label="子项类型" prop="child_type">
          <el-select v-model="form.child_type" placeholder="请选择子项类型" style="width: 100%">
            <el-option label="板卡" value="board"></el-option>
            <el-option label="模块" value="module"></el-option>
            <el-option label="光模块" value="optical_module"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="槽位/端口信息">
          <el-input v-model="form.slot_port_info" placeholder="请输入槽位或端口信息" prefix-icon="Location"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitForm" class="btn-gradient">确 定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Connection, Plus, Search, Refresh, List, Delete, Share, Switch, Grid } from '@element-plus/icons-vue'
import materialsService from '@/services/materials'

// 数据响应式变量
const loading = ref(false)
const dialogVisible = ref(false)

// 表单数据
const form = reactive({
  parent_sn: '',
  parent_type: '',
  child_sn: '',
  child_type: '',
  slot_port_info: ''
})

// 搜索表单
const searchForm = reactive({
  parent_sn: '',
  child_sn: ''
})

// 分页数据
const currentPage = ref(1)
const pageSize = ref(20)

// 列表数据
const relationships = ref([])

// 计算属性 - 统计数据
const totalCount = computed(() => relationships.value.length)
const parentChildCount = computed(() => {
  return relationships.value.filter(r => r.relationship_type === 'parent_child' || !r.relationship_type).length
})
const alternativeCount = computed(() => {
  return relationships.value.filter(r => r.relationship_type === 'alternative').length
})
const combinationCount = computed(() => {
  return relationships.value.filter(r => r.relationship_type === 'combination').length
})

// 表单验证规则
const rules = {
  parent_sn: [
    { required: true, message: '请输入父项序列号', trigger: 'blur' }
  ],
  parent_type: [
    { required: true, message: '请选择父项类型', trigger: 'change' }
  ],
  child_sn: [
    { required: true, message: '请输入子项序列号', trigger: 'blur' }
  ],
  child_type: [
    { required: true, message: '请选择子项类型', trigger: 'change' }
  ]
}

// 获取类型标签样式
const getTypeTag = (type) => {
  const types = {
    'equipment': 'primary',
    'board': 'success',
    'module': 'warning',
    'optical_module': 'info'
  }
  return types[type] || 'info'
}

// 获取类型文本
const getTypeText = (type) => {
  const texts = {
    'equipment': '设备',
    'board': '板卡',
    'module': '模块',
    'optical_module': '光模块'
  }
  return texts[type] || type
}

// 计算属性 - 过滤后的关系列表
const filteredRelationships = computed(() => {
  if (!Array.isArray(relationships.value)) return []
  return relationships.value.filter(rel => {
    return (
      (!searchForm.parent_sn || (rel.parent_sn && rel.parent_sn.includes(searchForm.parent_sn))) &&
      (!searchForm.child_sn || (rel.child_sn && rel.child_sn.includes(searchForm.child_sn)))
    )
  })
})

// 计算属性 - 分页后的关系列表
const paginatedRelationships = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRelationships.value.slice(start, end)
})

// 日期格式化
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).replace(/\//g, '-')
}

// 加载关系列表
const loadRelationships = async () => {
  try {
    loading.value = true
    const data = await materialsService.getRelationships()
    relationships.value = Array.isArray(data) ? data : []
  } catch (error) {
    ElMessage.error('加载物料关系列表失败: ' + error.message)
    relationships.value = []
  } finally {
    loading.value = false
  }
}

// 打开创建对话框
const openCreateDialog = () => {
  resetForm()
  dialogVisible.value = true
}

// 提交表单
const formRef = ref(null)
const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      const formData = {
        parent_sn: form.parent_sn,
        parent_type: form.parent_type,
        child_sn: form.child_sn,
        child_type: form.child_type,
        slot_port_info: form.slot_port_info
      }
      
      await materialsService.createRelationship(formData)
      ElMessage.success('物料关系创建成功')
      dialogVisible.value = false
      loadRelationships()
    } catch (error) {
      ElMessage.error('创建物料关系失败: ' + error.message)
    }
  })
}

// 删除关系
const deleteRelationship = async (id) => {
  try {
    await ElMessageBox.confirm('确认删除该物料关系吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await materialsService.deleteRelationship(id)
    ElMessage.success('物料关系删除成功')
    loadRelationships()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除物料关系失败: ' + error.message)
    }
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
}

// 重置搜索
const resetSearch = () => {
  searchForm.parent_sn = ''
  searchForm.child_sn = ''
  currentPage.value = 1
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    parent_sn: '',
    parent_type: '',
    child_sn: '',
    child_type: '',
    slot_port_info: ''
  })
  
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 组件挂载时加载数据
onMounted(() => {
  loadRelationships()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.relationship-list-container {
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  min-height: 100%;
}

/* 页面头部 - 玻璃拟态风格 */
.page-header {
  position: relative;
  margin-bottom: 24px;
  padding: 28px 32px;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px -10px rgba(56, 189, 248, 0.4);
}

.page-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at top right, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse at bottom left, rgba(14, 165, 233, 0.3) 0%, transparent 50%);
  pointer-events: none;
}

.page-header::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.5;
  pointer-events: none;
}

.header-bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.3;
}

.orb-1 {
  width: 200px;
  height: 200px;
  background: #f093fb;
  top: -50px;
  right: 10%;
  animation: float 6s ease-in-out infinite;
}

.orb-2 {
  width: 150px;
  height: 150px;
  background: #4facfe;
  bottom: -30px;
  right: 30%;
  animation: float 8s ease-in-out infinite reverse;
}

.header-content {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 20px;
}

.title-icon-wrapper {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.title-icon {
  font-size: 32px;
  color: white;
}

.title-text h1 {
  margin: 0 0 6px 0;
  color: white;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.subtitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 400;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 统计卡片区域 */
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.stat-card::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  transform: scaleX(0);
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.15), 0 10px 20px -5px rgba(0, 0, 0, 0.1);
}

.stat-card:hover::before {
  transform: scaleX(1);
}

.stat-card-total::before { background: linear-gradient(90deg, #7dd3fc, #38bdf8); }
.stat-card-parent::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-alternative::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-combination::before { background: linear-gradient(90deg, #ec4899, #f472b6); }

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: all 0.4s;
}

.stat-card:hover .stat-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.stat-icon-wrapper-total {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #7dd3fc;
  box-shadow: 0 4px 15px -3px rgba(56, 189, 248, 0.4);
}

.stat-icon-wrapper-parent {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-alternative {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-combination {
  background: linear-gradient(135deg, #fce7f3 0%, #f9a8d4 100%);
  color: #db2777;
  box-shadow: 0 4px 15px -3px rgba(236, 72, 153, 0.4);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 26px;
  font-weight: 800;
  line-height: 1.2;
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-card-total .stat-value {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-parent .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-alternative .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-combination .stat-value {
  background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
}

/* 玻璃拟态卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  transition: all 0.4s;
}

.glass-card:hover {
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.12), 0 10px 20px -5px rgba(0, 0, 0, 0.08);
}

/* 筛选区域 */
.filter-section {
  margin-bottom: 24px;
}

.filter-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
}

.card-title .el-icon {
  color: #0ea5e9;
  font-size: 18px;
}

.filter-form {
  padding: 10px 0;
}

.filter-input {
  width: 200px;
}

/* 按钮样式 */
.btn-gradient {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.5);
}

.btn-secondary {
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(56, 189, 248, 0.1);
  border-color: #0ea5e9;
  color: #0ea5e9;
}

/* 内容区域 */
.content-section {
  margin-bottom: 20px;
}

/* 表格头部 */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-title .el-icon {
  color: #0ea5e9;
  font-size: 20px;
}

.table-title h3 {
  margin: 0;
  font-size: 16px;
  color: #1e293b;
  font-weight: 600;
}

.total-count {
  font-size: 13px;
  color: #64748b;
  margin-left: 8px;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 12px;
  border-radius: 20px;
}

/* 自定义表格 */
.custom-table {
  --el-table-header-bg-color: rgba(241, 245, 249, 0.8);
  --el-table-row-hover-bg-color: rgba(56, 189, 248, 0.05);
}

.custom-table :deep(.el-table__header th) {
  font-weight: 600;
  color: #1e293b;
  background: rgba(241, 245, 249, 0.8);
}

.custom-table :deep(.el-table__row) {
  transition: all 0.3s;
}

.item-info {
  line-height: 1.4;
}

.item-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
  margin-bottom: 4px;
}

.type-tag {
  font-weight: 500;
  border-radius: 6px;
}

.slot-info {
  font-size: 13px;
  color: #475569;
  font-family: 'Monaco', 'Menlo', monospace;
}

.timestamp {
  line-height: 1.4;
}

.time-main {
  font-size: 13px;
  color: #475569;
}

.delete-btn {
  opacity: 0;
  transition: all 0.3s;
}

.custom-table :deep(.el-table__row:hover) .delete-btn {
  opacity: 1;
}

/* 分页 */
.pagination-section {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

/* 对话框样式 */
.custom-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  padding: 20px;
  margin-right: 0;
}

.custom-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.custom-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: rgba(255, 255, 255, 0.8);
}

.custom-dialog :deep(.el-dialog__headerbtn:hover .el-dialog__close) {
  color: white;
}

.dialog-form {
  padding: 20px 10px;
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

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-fade-in-down {
  animation: fadeInDown 0.6s ease-out;
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s ease-out;
  animation-fill-mode: both;
}

.delay-100 { animation-delay: 100ms; }
.delay-200 { animation-delay: 200ms; }
.delay-300 { animation-delay: 300ms; }

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .relationship-list-container {
    padding: 0;
  }

  .page-header {
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 16px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-title {
    gap: 14px;
  }

  .title-icon-wrapper {
    width: 48px;
    height: 48px;
    border-radius: 14px;
  }

  .title-icon {
    font-size: 24px;
  }

  .title-text h1 {
    font-size: 22px;
  }

  .subtitle {
    font-size: 13px;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .el-button {
    flex: 1;
    width: 100%;
  }

  .stats-row {
    margin-bottom: 20px;
  }

  .stat-card {
    padding: 16px;
    gap: 12px;
    margin-bottom: 12px;
  }

  .stat-icon-wrapper {
    width: 44px;
    height: 44px;
    border-radius: 12px;
  }

  .stat-value {
    font-size: 22px;
  }

  .stat-label {
    font-size: 12px;
  }

  .filter-form {
    flex-direction: column;
  }

  .filter-form .el-form-item {
    margin-right: 0;
    margin-bottom: 12px;
    width: 100%;
  }

  .filter-input {
    width: 100% !important;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .delete-btn {
    opacity: 1;
  }

  .el-table {
    font-size: 12px !important;
  }

  .el-table th,
  .el-table td {
    padding: 8px 6px !important;
  }

  .pagination-section {
    justify-content: center;
  }

  .custom-dialog :deep(.el-dialog) {
    width: 95% !important;
    margin: 10px auto !important;
  }
}

@media screen and (max-width: 480px) {
  .page-header {
    padding: 16px;
  }

  .title-text h1 {
    font-size: 20px;
  }

  .stat-card {
    padding: 14px;
  }

  .stat-value {
    font-size: 20px;
  }

  .el-table {
    font-size: 11px !important;
  }
}
</style>
