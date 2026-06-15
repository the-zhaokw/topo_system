<template>
  <div class="location-list-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Location /></el-icon>
          </div>
          <div class="title-text">
            <h1>库位管理</h1>
            <p class="subtitle">管理仓库中的库位信息，支持增删改查</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="openCreateDialog" class="btn-gradient">
            <el-icon><Plus /></el-icon>
            新增库位
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
              <el-icon><Grid /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ total }}</div>
              <div class="stat-label">库位总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-occupied">
            <div class="stat-icon-wrapper stat-icon-wrapper-occupied">
              <el-icon><Box /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ occupiedCount }}</div>
              <div class="stat-label">已占用</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-available">
            <div class="stat-icon-wrapper stat-icon-wrapper-available">
              <el-icon><Check /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ availableCount }}</div>
              <div class="stat-label">空闲中</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-rate">
            <div class="stat-icon-wrapper stat-icon-wrapper-rate">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ occupancyRate }}%</div>
              <div class="stat-label">使用率</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选区域 -->
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
        <el-form :model="searchForm" inline class="filter-form">
          <el-form-item label="仓库">
            <el-select v-model="searchForm.warehouse_id" placeholder="请选择仓库" clearable @change="handleSearch" class="filter-select">
              <el-option
                v-for="warehouse in warehouses"
                :key="warehouse.id"
                :label="warehouse.name"
                :value="warehouse.id">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="库位编码">
            <el-input v-model="searchForm.code" placeholder="请输入库位编码" clearable @clear="handleSearch" @keyup.enter="handleSearch" class="filter-input"></el-input>
          </el-form-item>
          <el-form-item label="库位名称">
            <el-input v-model="searchForm.name" placeholder="请输入库位名称" clearable @clear="handleSearch" @keyup.enter="handleSearch" class="filter-input"></el-input>
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

    <!-- 内容区域 -->
    <div class="content-section animate-fade-in-up delay-300">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="table-header">
            <div class="table-title">
              <el-icon><List /></el-icon>
              <h3>库位列表</h3>
              <span class="total-count">共 {{ total }} 条记录</span>
            </div>
          </div>
        </template>

        <el-table
          :data="locations"
          v-loading="loading"
          stripe
          class="custom-table"
          style="width: 100%">
          <el-table-column prop="id" label="ID" width="70" align="center">
            <template #default="{ row }">
              <span class="id-badge">{{ row.id }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="warehouse_name" label="所属仓库" width="150">
            <template #default="{ row }">
              <div class="warehouse-info">
                <el-icon class="warehouse-icon"><OfficeBuilding /></el-icon>
                <span>{{ row.warehouse_name }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="code" label="库位编码" width="140">
            <template #default="{ row }">
              <span class="code-badge">{{ row.code }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="name" label="库位名称" width="180">
            <template #default="{ row }">
              <span class="location-name">{{ row.name }}</span>
            </template>
          </el-table-column>

          <el-table-column label="位置信息" width="200">
            <template #default="{ row }">
              <div class="location-info">
                <el-tag size="small" effect="light" class="location-tag" v-if="row.area">
                  <el-icon><MapLocation /></el-icon>
                  {{ row.area }}
                </el-tag>
                <el-tag size="small" effect="light" type="info" class="location-tag" v-if="row.zone">
                  {{ row.zone }}
                </el-tag>
                <el-tag size="small" effect="light" type="warning" class="location-tag" v-if="row.rack">
                  <el-icon><FirstAidKit /></el-icon>
                  {{ row.rack }}
                </el-tag>
                <el-tag size="small" effect="light" type="success" class="location-tag" v-if="row.level">
                  L{{ row.level }}
                </el-tag>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="capacity" label="容量" width="100" align="center">
            <template #default="{ row }">
              <span class="capacity-value">{{ row.capacity || '-' }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="创建时间" width="160" align="center">
            <template #default="{ row }">
              <div class="timestamp">
                <div class="time-main">{{ formatDate(row.created_at) }}</div>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="150" align="center" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link size="small" @click="openEditDialog(row)" class="action-btn">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-popconfirm
                  title="确定要删除这个库位吗？"
                  @confirm="deleteLocation(row.id)"
                  confirm-button-type="danger"
                >
                  <template #reference>
                    <el-button type="danger" link size="small" class="action-btn">
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
                  </template>
                </el-popconfirm>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-section">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange">
          </el-pagination>
        </div>
      </el-card>
    </div>

    <!-- 新增/编辑库位对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="500px"
      @close="resetForm"
      class="location-dialog"
    >
      <el-form :model="locationForm" :rules="formRules" ref="locationFormRef" label-width="100px">
        <el-form-item label="所属仓库" prop="warehouse_id">
          <el-select v-model="locationForm.warehouse_id" placeholder="请选择仓库" style="width: 100%">
            <el-option
              v-for="warehouse in warehouses"
              :key="warehouse.id"
              :label="warehouse.name"
              :value="warehouse.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="库位编码" prop="code">
          <el-input v-model="locationForm.code" placeholder="请输入库位编码"></el-input>
        </el-form-item>
        <el-form-item label="库位名称" prop="name">
          <el-input v-model="locationForm.name" placeholder="请输入库位名称"></el-input>
        </el-form-item>
        <el-form-item label="区域">
          <el-input v-model="locationForm.area" placeholder="请输入区域"></el-input>
        </el-form-item>
        <el-form-item label="分区">
          <el-input v-model="locationForm.zone" placeholder="请输入分区"></el-input>
        </el-form-item>
        <el-form-item label="货架">
          <el-input v-model="locationForm.rack" placeholder="请输入货架"></el-input>
        </el-form-item>
        <el-form-item label="层级">
          <el-input v-model="locationForm.level" placeholder="请输入层级"></el-input>
        </el-form-item>
        <el-form-item label="容量">
          <el-input-number v-model="locationForm.capacity" :min="0" controls-position="right" style="width: 100%"></el-input-number>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="locationForm.description" type="textarea" :rows="3" placeholder="请输入描述"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitLoading" class="btn-gradient">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import materialsService from '@/services/materials'
import { format } from 'date-fns'
import {
  Location, Plus, Filter, Search, Refresh, List, Edit, Delete,
  Grid, Box, Check, TrendCharts, OfficeBuilding, MapLocation,
  FirstAidKit
} from '@element-plus/icons-vue'

// 响应式数据
const locations = ref([])
const warehouses = ref([])
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEditMode = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 表单引用
const locationFormRef = ref(null)

// 搜索表单
const searchForm = reactive({
  warehouse_id: '',
  code: '',
  name: ''
})

// 库位表单
const locationForm = reactive({
  id: null,
  warehouse_id: '',
  code: '',
  name: '',
  area: '',
  zone: '',
  rack: '',
  level: '',
  capacity: 0,
  description: ''
})

// 表单验证规则
const formRules = {
  warehouse_id: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  code: [{ required: true, message: '请输入库位编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入库位名称', trigger: 'blur' }]
}

// 计算属性
const dialogTitle = computed(() => {
  return isEditMode.value ? '编辑库位' : '新增库位'
})

// 统计计算属性（模拟数据，实际应根据业务逻辑计算）
const occupiedCount = computed(() => {
  // 这里可以根据实际业务逻辑计算已占用的库位数量
  return Math.floor(total.value * 0.6)
})

const availableCount = computed(() => {
  return total.value - occupiedCount.value
})

const occupancyRate = computed(() => {
  if (total.value === 0) return 0
  return Math.round((occupiedCount.value / total.value) * 100)
})

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  return format(new Date(dateString), 'yyyy-MM-dd HH:mm')
}

// 加载仓库列表
const loadWarehouses = async () => {
  try {
    warehouses.value = await materialsService.getWarehouses()
  } catch (error) {
    ElMessage.error('加载仓库列表失败: ' + error.message)
  }
}

// 加载库位列表
const loadLocations = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      warehouse_id: searchForm.warehouse_id,
      code: searchForm.code,
      name: searchForm.name
    }

    const response = await materialsService.getLocations()
    // 过滤数据
    let filteredData = response

    if (searchForm.warehouse_id) {
      filteredData = filteredData.filter(item => item.warehouse_id === searchForm.warehouse_id)
    }

    if (searchForm.code) {
      filteredData = filteredData.filter(item => item.code.includes(searchForm.code))
    }

    if (searchForm.name) {
      filteredData = filteredData.filter(item => item.name.includes(searchForm.name))
    }

    // 分页处理
    total.value = filteredData.length
    const startIndex = (currentPage.value - 1) * pageSize.value
    locations.value = filteredData.slice(startIndex, startIndex + pageSize.value)
  } catch (error) {
    ElMessage.error('加载库位列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  loadLocations()
}

// 重置搜索
const resetSearch = () => {
  searchForm.warehouse_id = ''
  searchForm.code = ''
  searchForm.name = ''
  currentPage.value = 1
  loadLocations()
}

// 打开创建对话框
const openCreateDialog = () => {
  isEditMode.value = false
  dialogVisible.value = true
}

// 打开编辑对话框
const openEditDialog = (row) => {
  isEditMode.value = true
  Object.assign(locationForm, row)
  dialogVisible.value = true
}

// 提交表单
const submitForm = async () => {
  try {
    await locationFormRef.value.validate()

    submitLoading.value = true
    const formData = { ...locationForm }

    if (isEditMode.value) {
      await materialsService.updateLocation(locationForm.id, formData)
      ElMessage.success('库位更新成功')
    } else {
      await materialsService.createLocation(formData)
      ElMessage.success('库位创建成功')
    }

    dialogVisible.value = false
    loadLocations()
  } catch (error) {
    ElMessage.error((isEditMode.value ? '更新' : '创建') + '库位失败: ' + error.message)
  } finally {
    submitLoading.value = false
  }
}

// 删除库位
const deleteLocation = async (id) => {
  try {
    await materialsService.deleteLocation(id)
    ElMessage.success('库位删除成功')
    loadLocations()
  } catch (error) {
    ElMessage.error('删除库位失败: ' + error.message)
  }
}

// 重置表单
const resetForm = () => {
  locationFormRef.value?.resetFields()
  locationForm.id = null
  locationForm.warehouse_id = ''
  locationForm.code = ''
  locationForm.name = ''
  locationForm.area = ''
  locationForm.zone = ''
  locationForm.rack = ''
  locationForm.level = ''
  locationForm.capacity = 0
  locationForm.description = ''
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  loadLocations()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadLocations()
}

// 组件挂载时加载数据
onMounted(() => {
  loadWarehouses()
  loadLocations()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.location-list-container {
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

/* 统计卡片渐变配色 */
.stat-card-total::before { background: linear-gradient(90deg, #7dd3fc, #38bdf8); }
.stat-card-occupied::before { background: linear-gradient(90deg, #f093fb, #f5576c); }
.stat-card-available::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-rate::before { background: linear-gradient(90deg, #00c6ff, #0072ff); }

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

.stat-icon-wrapper-occupied {
  background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
  color: #db2777;
  box-shadow: 0 4px 15px -3px rgba(236, 72, 153, 0.4);
}

.stat-icon-wrapper-available {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-rate {
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  color: #0284c7;
  box-shadow: 0 4px 15px -3px rgba(14, 165, 233, 0.4);
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

.stat-card-occupied .stat-value {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-available .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-rate .stat-value {
  background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
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

.filter-select,
.filter-input {
  width: 160px;
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

.id-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
}

.warehouse-info {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #475569;
  font-weight: 500;
}

.warehouse-icon {
  color: #0ea5e9;
  font-size: 16px;
}

.code-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  font-weight: 600;
  color: #7dd3fc;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  padding: 4px 10px;
  border-radius: 6px;
}

.location-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.location-info {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.location-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.location-tag .el-icon {
  font-size: 12px;
}

.capacity-value {
  font-weight: 600;
  color: #475569;
  font-size: 14px;
}

.timestamp {
  line-height: 1.4;
}

.time-main {
  font-size: 13px;
  color: #475569;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 8px;
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

/* 对话框样式 */
:deep(.location-dialog .el-dialog__header) {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  padding: 20px;
  margin-right: 0;
}

:deep(.location-dialog .el-dialog__title) {
  color: white;
  font-weight: 600;
}

:deep(.location-dialog .el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

:deep(.location-dialog .el-dialog__body) {
  padding: 24px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .location-list-container {
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
  .filter-input {
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

  :deep(.location-dialog) {
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
