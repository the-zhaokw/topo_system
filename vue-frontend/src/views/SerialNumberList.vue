<template>
  <div class="serial-number-list-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Ticket /></el-icon>
          </div>
          <div class="title-text">
            <h1>序列号管理</h1>
            <p class="subtitle">管理物料序列号，追踪库存状态</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="openCreateDialog" class="btn-gradient">
            <el-icon><Plus /></el-icon>
            新增序列号
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
              <el-icon><Collection /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ totalCount }}</div>
              <div class="stat-label">序列号总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-used">
            <div class="stat-icon-wrapper stat-icon-wrapper-used">
              <el-icon><Check /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ usedCount }}</div>
              <div class="stat-label">已使用</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-unused">
            <div class="stat-icon-wrapper stat-icon-wrapper-unused">
              <el-icon><Box /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ unusedCount }}</div>
              <div class="stat-label">未使用</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-scraped">
            <div class="stat-icon-wrapper stat-icon-wrapper-scraped">
              <el-icon><Delete /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ scrapedCount }}</div>
              <div class="stat-label">已报废</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索条件 -->
    <div class="filter-section animate-fade-in-up delay-200">
      <el-card class="filter-card glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Filter /></el-icon>
              筛选条件
            </span>
          </div>
        </template>
        <el-form :model="searchForm" :inline="true" label-width="80px" class="filter-form">
          <el-form-item label="物料">
            <el-select v-model="searchForm.material_id" placeholder="请选择物料" clearable filterable class="filter-select">
              <el-option
                v-for="material in materials"
                :key="material.id"
                :label="`${material.material_code} - ${material.name}`"
                :value="material.id">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.status" placeholder="请选择状态" clearable class="filter-select">
              <el-option label="在库待用" value="in_stock"></el-option>
              <el-option label="已领用" value="in_use"></el-option>
              <el-option label="已安装" value="installed"></el-option>
              <el-option label="已报废" value="scraped"></el-option>
            </el-select>
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

    <!-- 序列号列表 -->
    <div class="content-section animate-fade-in-up delay-300">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="table-header">
            <div class="table-title">
              <el-icon><List /></el-icon>
              <h3>序列号列表</h3>
              <span class="total-count">共 {{ filteredSerialNumbers.length }} 条记录</span>
            </div>
          </div>
        </template>

        <el-table :data="paginatedSerialNumbers" stripe v-loading="loading" class="custom-table">
          <el-table-column prop="serial_number" label="序列号" width="180">
            <template #default="scope">
              <span class="serial-badge">{{ scope.row.serial_number }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="material_info.material_code" label="物料编码" width="150">
            <template #default="scope">
              <span class="code-badge">{{ scope.row.material_info.material_code }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="material_info.name" label="物料名称" min-width="200">
            <template #default="scope">
              <span class="material-name">{{ scope.row.material_info.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="current_status" label="当前状态" width="120" align="center">
            <template #default="scope">
              <el-tag :type="getStatusTagType(scope.row.current_status)" effect="light" class="status-tag">
                {{ getStatusText(scope.row.current_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="current_location" label="当前位置" width="150">
            <template #default="scope">
              <span class="location-text">{{ scope.row.current_location || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180" align="center">
            <template #default="scope">
              <div class="timestamp">
                <div class="time-main">{{ formatDate(scope.row.created_at) }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right" align="center">
            <template #default="scope">
              <el-button type="primary" link size="small" @click="openEditDialog(scope.row)" class="action-btn">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button type="danger" link size="small" @click="deleteSerialNumber(scope.row.id)" class="action-btn">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-section">
          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="currentPage"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredSerialNumbers.length">
          </el-pagination>
        </div>
      </el-card>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="500px" @close="resetForm" class="custom-dialog">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="序列号" prop="serial_number">
          <el-input v-model="form.serial_number" :disabled="!!form.id" placeholder="请输入序列号"></el-input>
        </el-form-item>
        <el-form-item label="物料" prop="material_id">
          <el-select v-model="form.material_id" placeholder="请选择物料" filterable class="form-select">
            <el-option
              v-for="material in materials"
              :key="material.id"
              :label="`${material.material_code} - ${material.name}`"
              :value="material.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="初始状态" prop="current_status">
          <el-select v-model="form.current_status" placeholder="请选择初始状态" class="form-select">
            <el-option label="在库待用" value="in_stock"></el-option>
            <el-option label="已领用" value="in_use"></el-option>
            <el-option label="已安装" value="installed"></el-option>
            <el-option label="已报废" value="scraped"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remarks" type="textarea" :rows="3" placeholder="请输入备注信息"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false" class="btn-secondary">取 消</el-button>
          <el-button type="primary" @click="submitForm" class="btn-gradient">确 定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Ticket, Collection, Check, Box, Delete, Filter, Search, Refresh, List, Edit } from '@element-plus/icons-vue'
import materialsService from '@/services/materials'

// 数据响应式变量
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = computed(() => form.id ? '编辑序列号' : '新增序列号')

// 表单数据
const form = reactive({
  id: null,
  serial_number: '',
  material_id: null,
  current_status: 'in_stock',
  remarks: ''
})

// 搜索表单
const searchForm = reactive({
  material_id: null,
  status: null
})

// 分页数据
const currentPage = ref(1)
const pageSize = ref(20)

// 列表数据
const serialNumbers = ref([])
const materials = ref([])

// 表单验证规则
const rules = {
  serial_number: [
    { required: true, message: '请输入序列号', trigger: 'blur' }
  ],
  material_id: [
    { required: true, message: '请选择物料', trigger: 'change' }
  ],
  current_status: [
    { required: true, message: '请选择初始状态', trigger: 'change' }
  ]
}

// 计算属性 - 过滤后的序列号列表
const filteredSerialNumbers = computed(() => {
  return serialNumbers.value.filter(serial => {
    return (
      (!searchForm.material_id || serial.material_id === searchForm.material_id) &&
      (!searchForm.status || serial.current_status === searchForm.status)
    )
  })
})

// 计算属性 - 分页后的序列号列表
const paginatedSerialNumbers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredSerialNumbers.value.slice(start, end)
})

// 统计数据
const totalCount = computed(() => serialNumbers.value.length)
const usedCount = computed(() => serialNumbers.value.filter(s => s.current_status === 'in_use' || s.current_status === 'installed').length)
const unusedCount = computed(() => serialNumbers.value.filter(s => s.current_status === 'in_stock').length)
const scrapedCount = computed(() => serialNumbers.value.filter(s => s.current_status === 'scraped').length)

// 状态文本映射
const getStatusText = (status) => {
  const statusMap = {
    'in_stock': '在库待用',
    'in_use': '已领用',
    'installed': '已安装',
    'scraped': '已报废'
  }
  return statusMap[status] || status
}

// 状态标签类型映射
const getStatusTagType = (status) => {
  const typeMap = {
    'in_stock': 'success',
    'in_use': 'warning',
    'installed': 'primary',
    'scraped': 'danger'
  }
  return typeMap[status] || 'info'
}

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

// 加载序列号列表
const loadSerialNumbers = async () => {
  try {
    loading.value = true
    const data = await materialsService.getSerialNumbers()
    serialNumbers.value = data.map(sn => ({
      ...sn,
      material_info: {
        material_code: sn.material?.material_code || '',
        name: sn.material?.name || ''
      }
    }))
  } catch (error) {
    ElMessage.error('加载序列号列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 加载物料列表
const loadMaterials = async () => {
  try {
    const data = await materialsService.getMaterials()
    materials.value = data
  } catch (error) {
    ElMessage.error('加载物料列表失败: ' + error.message)
  }
}

// 打开创建对话框
const openCreateDialog = () => {
  resetForm()
  dialogVisible.value = true
}

// 打开编辑对话框
const openEditDialog = (row) => {
  Object.assign(form, {
    id: row.id,
    serial_number: row.serial_number,
    material_id: row.material_id,
    current_status: row.current_status,
    remarks: row.remarks || ''
  })
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
        serial_number: form.serial_number,
        material_id: form.material_id,
        current_status: form.current_status,
        remarks: form.remarks
      }

      if (form.id) {
        // 编辑操作
        await materialsService.updateSerialNumber(form.id, formData)
        ElMessage.success('序列号更新成功')
      } else {
        // 创建操作
        await materialsService.createSerialNumber(formData)
        ElMessage.success('序列号创建成功')
      }

      dialogVisible.value = false
      loadSerialNumbers()
    } catch (error) {
      ElMessage.error((form.id ? '更新' : '创建') + '序列号失败: ' + error.message)
    }
  })
}

// 删除序列号
const deleteSerialNumber = async (id) => {
  try {
    await ElMessageBox.confirm('确认删除该序列号吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await materialsService.deleteSerialNumber(id)
    ElMessage.success('序列号删除成功')
    loadSerialNumbers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除序列号失败: ' + error.message)
    }
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
}

// 重置搜索
const resetSearch = () => {
  searchForm.material_id = null
  searchForm.status = null
  currentPage.value = 1
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    id: null,
    serial_number: '',
    material_id: null,
    current_status: 'in_stock',
    remarks: ''
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
  loadSerialNumbers()
  loadMaterials()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.serial-number-list-container {
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
.stat-card-used::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-unused::before { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.stat-card-scraped::before { background: linear-gradient(90deg, #ef4444, #f87171); }

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

.stat-icon-wrapper-used {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-unused {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #2563eb;
  box-shadow: 0 4px 15px -3px rgba(59, 130, 246, 0.4);
}

.stat-icon-wrapper-scraped {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
  box-shadow: 0 4px 15px -3px rgba(239, 68, 68, 0.4);
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

.stat-card-used .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-unused .stat-value {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-scraped .stat-value {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
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

.filter-select {
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

.serial-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  font-weight: 600;
  color: #7dd3fc;
  background: rgba(56, 189, 248, 0.1);
  padding: 6px 12px;
  border-radius: 8px;
}

.code-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
}

.material-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.status-tag {
  font-weight: 500;
  border-radius: 6px;
  padding: 4px 10px;
}

.location-text {
  color: #475569;
  font-size: 13px;
}

.timestamp {
  line-height: 1.4;
}

.time-main {
  font-size: 13px;
  color: #475569;
}

.action-btn {
  opacity: 0;
  transition: all 0.3s;
}

.custom-table :deep(.el-table__row:hover) .action-btn {
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
  padding: 20px 24px;
  margin-right: 0;
}

.custom-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.custom-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

.custom-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.form-select {
  width: 100%;
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
  .serial-number-list-container {
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

  .filter-select,
  .filter-form .el-input {
    width: 100% !important;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .action-btn {
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
