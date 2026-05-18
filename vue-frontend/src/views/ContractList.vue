<template>
  <div class="contract-list-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Document /></el-icon>
          </div>
          <div class="title-text">
            <h1>合同管理</h1>
            <p class="subtitle">管理所有合同信息，包括创建、编辑和查看</p>
          </div>
        </div>
        <el-button type="primary" @click="handleCreate" class="btn-gradient">
          <el-icon><Plus /></el-icon>
          新建合同
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-total">
            <div class="stat-icon-wrapper stat-icon-wrapper-total">
              <el-icon><DocumentChecked /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ pagination.total }}</div>
              <div class="stat-label">合同总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-active">
            <div class="stat-icon-wrapper stat-icon-wrapper-active">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ activeCount }}</div>
              <div class="stat-label">进行中</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-completed">
            <div class="stat-icon-wrapper stat-icon-wrapper-completed">
              <el-icon><SuccessFilled /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ completedCount }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-amount">
            <div class="stat-icon-wrapper stat-icon-wrapper-amount">
              <el-icon><Money /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ formatTotalAmount }}</div>
              <div class="stat-label">总金额(万元)</div>
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
        <el-form :inline="true" :model="filterForm" class="filter-form">
          <el-form-item label="关键词">
            <el-input v-model="filterForm.keyword" placeholder="合同编号/名称/客户" clearable @keyup.enter="handleSearch" class="filter-input" />
          </el-form-item>
          <el-form-item label="合同状态">
            <el-select v-model="filterForm.status" placeholder="请选择" clearable class="filter-select">
              <el-option label="草稿" value="draft" />
              <el-option label="待审核" value="pending_review" />
              <el-option label="待审批" value="pending_approval" />
              <el-option label="执行中" value="active" />
              <el-option label="已过期" value="expired" />
              <el-option label="已终止" value="terminated" />
            </el-select>
          </el-form-item>
          <el-form-item label="合同类型">
            <el-select v-model="filterForm.contract_type" placeholder="请选择" clearable class="filter-select">
              <el-option label="设备销售合同" value="equipment_sales" />
              <el-option label="软件许可合同" value="software_license" />
              <el-option label="框架协议" value="framework_agreement" />
              <el-option label="采购订单" value="purchase_order" />
              <el-option label="工程服务合同" value="engineering_service" />
              <el-option label="维护服务合同" value="maintenance_service" />
              <el-option label="专利许可合同" value="patent_license" />
              <el-option label="OEM代工协议" value="oem_agreement" />
              <el-option label="供应协议" value="supply_agreement" />
              <el-option label="国际项目合同" value="international_project" />
            </el-select>
          </el-form-item>
          <el-form-item label="风险等级">
            <el-select v-model="filterForm.risk_level" placeholder="请选择" clearable class="filter-select">
              <el-option label="低风险" value="low" />
              <el-option label="中风险" value="medium" />
              <el-option label="高风险" value="high" />
              <el-option label="重大风险" value="critical" />
            </el-select>
          </el-form-item>
          <el-form-item label="区域">
            <el-input v-model="filterForm.region" placeholder="区域" clearable class="filter-input" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch" class="btn-gradient">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset" class="btn-secondary">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 表格区域 -->
    <div class="content-section animate-fade-in-up delay-300">
      <el-card class="glass-card" shadow="hover">
        <template #header>
          <div class="table-header">
            <div class="table-title">
              <el-icon><List /></el-icon>
              <h3>合同列表</h3>
              <span class="total-count">共 {{ pagination.total }} 条记录</span>
            </div>
          </div>
        </template>

        <el-table :data="contracts" v-loading="loading" class="custom-table" style="width: 100%">
          <el-table-column prop="contract_no" label="合同编号" width="150">
            <template #default="{ row }">
              <span class="contract-no-badge">{{ row.contract_no }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="合同名称" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="contract-title">{{ row.title }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="contract_type" label="合同类型" width="140">
            <template #default="{ row }">
              <el-tag :type="getTypeTag(row.contract_type)" size="small" effect="light" class="type-tag">
                {{ getTypeName(row.contract_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusTag(row.status)" size="small" effect="light" class="status-tag">
                {{ getStatusName(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="risk_level" label="风险等级" width="100">
            <template #default="{ row }">
              <el-tag :type="getRiskTag(row.risk_level)" size="small" effect="light" class="risk-tag">
                {{ getRiskName(row.risk_level) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="party_b_name" label="客户/供应商" width="150" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="party-name">{{ row.party_b_name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="total_amount" label="金额" width="130">
            <template #default="{ row }">
              <span class="amount-value">{{ formatAmount(row.total_amount, row.currency) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="region" label="区域" width="100">
            <template #default="{ row }">
              <span class="region-text">{{ row.region || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="expiration_date" label="到期日期" width="120">
            <template #default="{ row }">
              <div class="date-info">
                <div class="date-main">{{ formatDate(row.expiration_date) }}</div>
                <div class="date-remaining" v-if="row.expiration_date">{{ getDaysRemaining(row.expiration_date) }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="handleView(row)" class="action-btn">
                <el-icon><View /></el-icon>
                查看
              </el-button>
              <el-button link type="primary" @click="handleEdit(row)" class="action-btn">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button link type="danger" @click="handleDelete(row)" class="action-btn">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-section">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.perPage"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-card>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="70%" destroy-on-close class="contract-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="合同编号" prop="contract_no">
              <el-input v-model="form.contract_no" placeholder="自动生成，如需手动输入请填写" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="合同名称" prop="title">
              <el-input v-model="form.title" placeholder="请输入合同名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="合同类型" prop="contract_type">
              <el-select v-model="form.contract_type" placeholder="请选择" style="width: 100%">
                <el-option label="设备销售合同" value="equipment_sales" />
                <el-option label="软件许可合同" value="software_license" />
                <el-option label="框架协议" value="framework_agreement" />
                <el-option label="采购订单" value="purchase_order" />
                <el-option label="工程服务合同" value="engineering_service" />
                <el-option label="维护服务合同" value="maintenance_service" />
                <el-option label="专利许可合同" value="patent_license" />
                <el-option label="OEM代工协议" value="oem_agreement" />
                <el-option label="供应协议" value="supply_agreement" />
                <el-option label="国际项目合同" value="international_project" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="风险等级" prop="risk_level">
              <el-select v-model="form.risk_level" placeholder="请选择" style="width: 100%">
                <el-option label="低风险" value="low" />
                <el-option label="中风险" value="medium" />
                <el-option label="高风险" value="high" />
                <el-option label="重大风险" value="critical" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="甲方" prop="party_a_name">
              <el-input v-model="form.party_a_name" placeholder="我方公司名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="乙方" prop="party_b_name">
              <el-input v-model="form.party_b_name" placeholder="客户/供应商名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="签约日期">
              <el-date-picker v-model="form.signing_date" type="datetime" placeholder="选择日期" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="生效日期">
              <el-date-picker v-model="form.effective_date" type="datetime" placeholder="选择日期" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="到期日期">
              <el-date-picker v-model="form.expiration_date" type="datetime" placeholder="选择日期" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="合同金额" prop="total_amount">
              <el-input-number v-model="form.total_amount" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="币种">
              <el-select v-model="form.currency" style="width: 100%">
                <el-option label="人民币 (CNY)" value="CNY" />
                <el-option label="美元 (USD)" value="USD" />
                <el-option label="欧元 (EUR)" value="EUR" />
                <el-option label="英镑 (GBP)" value="GBP" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option label="草稿" value="draft" />
                <el-option label="待审核" value="pending_review" />
                <el-option label="待审批" value="pending_approval" />
                <el-option label="执行中" value="active" />
                <el-option label="已过期" value="expired" />
                <el-option label="已终止" value="terminated" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="区域">
              <el-input v-model="form.region" placeholder="如：亚太、欧洲、北美" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="国家">
              <el-input v-model="form.country" placeholder="如：中国、美国、德国" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="技术要求">
          <el-input v-model="form.technical_requirements" type="textarea" :rows="3" placeholder="请输入技术要求" />
        </el-form-item>
        <el-form-item label="交付要求">
          <el-input v-model="form.delivery_requirements" type="textarea" :rows="3" placeholder="请输入交付要求" />
        </el-form-item>
        <el-form-item label="验收标准">
          <el-input v-model="form.acceptance_criteria" type="textarea" :rows="3" placeholder="请输入验收标准" />
        </el-form-item>
        <el-form-item label="SLA要求">
          <el-input v-model="form.sla_requirements" type="textarea" :rows="2" placeholder="请输入服务等级要求" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item>
              <el-checkbox v-model="form.ip_protection_required">知识产权保护要求</el-checkbox>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item>
              <el-checkbox v-model="form.export_control_applicable">适用出口管制</el-checkbox>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading" class="btn-gradient">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Document, Plus, Filter, Search, Refresh, List, View, Edit, Delete, DocumentChecked, CircleCheck, SuccessFilled, Money } from '@element-plus/icons-vue'

const router = useRouter()

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新建合同')
const isEdit = ref(false)

const contracts = ref([])
const filterForm = reactive({
  keyword: '',
  status: '',
  contract_type: '',
  risk_level: '',
  region: ''
})

const pagination = reactive({
  page: 1,
  perPage: 20,
  total: 0
})

const formRef = ref(null)
const form = reactive({
  id: null,
  contract_no: '',
  title: '',
  contract_type: 'equipment_sales',
  status: 'draft',
  risk_level: 'low',
  party_a_name: '',
  party_b_name: '',
  signing_date: null,
  effective_date: null,
  expiration_date: null,
  total_amount: 0,
  currency: 'CNY',
  region: '',
  country: '',
  technical_requirements: '',
  delivery_requirements: '',
  acceptance_criteria: '',
  sla_requirements: '',
  ip_protection_required: false,
  export_control_applicable: false
})

const rules = {
  title: [{ required: true, message: '请输入合同名称', trigger: 'blur' }],
  contract_type: [{ required: true, message: '请选择合同类型', trigger: 'change' }]
}

const typeMap = {
  equipment_sales: '设备销售合同',
  software_license: '软件许可合同',
  framework_agreement: '框架协议',
  purchase_order: '采购订单',
  engineering_service: '工程服务合同',
  maintenance_service: '维护服务合同',
  patent_license: '专利许可合同',
  oem_agreement: 'OEM代工协议',
  supply_agreement: '供应协议',
  international_project: '国际项目合同'
}

const statusMap = {
  draft: '草稿',
  pending_review: '待审核',
  pending_approval: '待审批',
  active: '执行中',
  expired: '已过期',
  terminated: '已终止',
  cancelled: '已取消',
  rejected: '已拒绝'
}

const riskMap = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
  critical: '重大风险'
}

const getTypeName = (type) => typeMap[type] || type
const getStatusName = (status) => statusMap[status] || status
const getRiskName = (risk) => riskMap[risk] || risk

const getTypeTag = (type) => {
  const map = {
    equipment_sales: '',
    software_license: 'success',
    framework_agreement: 'warning',
    purchase_order: 'info',
    engineering_service: '',
    maintenance_service: 'success',
    patent_license: 'danger',
    oem_agreement: 'warning',
    supply_agreement: 'info',
    international_project: 'danger'
  }
  return map[type] || ''
}

const getStatusTag = (status) => {
  const map = {
    draft: 'info',
    pending_review: 'warning',
    pending_approval: 'warning',
    active: 'success',
    expired: 'danger',
    terminated: 'danger',
    cancelled: 'info',
    rejected: 'danger'
  }
  return map[status] || ''
}

const getRiskTag = (risk) => {
  const map = {
    low: 'success',
    medium: 'warning',
    high: 'danger',
    critical: 'danger'
  }
  return map[risk] || ''
}

const formatAmount = (amount, currency) => {
  if (!amount) return '0.00'
  const symbol = currency === 'USD' ? '$' : currency === 'EUR' ? '€' : currency === 'GBP' ? '£' : '¥'
  return `${symbol}${parseFloat(amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const getDaysRemaining = (date) => {
  if (!date) return ''
  const today = new Date()
  const expDate = new Date(date)
  const diffTime = expDate - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  if (diffDays < 0) return '已过期'
  if (diffDays === 0) return '今天到期'
  if (diffDays <= 30) return `${diffDays}天后到期`
  return ''
}

// 统计计算
const activeCount = computed(() => {
  return contracts.value.filter(c => c.status === 'active').length
})

const completedCount = computed(() => {
  return contracts.value.filter(c => ['expired', 'terminated'].includes(c.status)).length
})

const formatTotalAmount = computed(() => {
  const total = contracts.value.reduce((sum, c) => sum + (parseFloat(c.total_amount) || 0), 0)
  return (total / 10000).toFixed(1)
})

const fetchContracts = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.perPage,
      ...filterForm
    }
    Object.keys(params).forEach(key => {
      if (!params[key]) delete params[key]
    })
    const response = await axios.get('/api/contracts/', { params })
    contracts.value = response.data.contracts
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('获取合同列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchContracts()
}

const handleReset = () => {
  Object.assign(filterForm, {
    keyword: '',
    status: '',
    contract_type: '',
    risk_level: '',
    region: ''
  })
  handleSearch()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchContracts()
}

const handleSizeChange = (size) => {
  pagination.perPage = size
  fetchContracts()
}

const handleCreate = () => {
  isEdit.value = false
  dialogTitle.value = '新建合同'
  Object.assign(form, {
    id: null,
    contract_no: '',
    title: '',
    contract_type: 'equipment_sales',
    status: 'draft',
    risk_level: 'low',
    party_a_name: '',
    party_b_name: '',
    signing_date: null,
    effective_date: null,
    expiration_date: null,
    total_amount: 0,
    currency: 'CNY',
    region: '',
    country: '',
    technical_requirements: '',
    delivery_requirements: '',
    acceptance_criteria: '',
    sla_requirements: '',
    ip_protection_required: false,
    export_control_applicable: false
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑合同'
  Object.assign(form, {
    id: row.id,
    contract_no: row.contract_no,
    title: row.title,
    contract_type: row.contract_type,
    status: row.status,
    risk_level: row.risk_level,
    party_a_name: row.party_a_name,
    party_b_name: row.party_b_name,
    signing_date: row.signing_date,
    effective_date: row.effective_date,
    expiration_date: row.expiration_date,
    total_amount: row.total_amount,
    currency: row.currency,
    region: row.region,
    country: row.country,
    technical_requirements: row.technical_requirements,
    delivery_requirements: row.delivery_requirements,
    acceptance_criteria: row.acceptance_criteria,
    sla_requirements: row.sla_requirements,
    ip_protection_required: row.ip_protection_required,
    export_control_applicable: row.export_control_applicable
  })
  dialogVisible.value = true
}

const handleView = (row) => {
  router.push(`/contracts/${row.id}`)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await axios.put(`/api/contracts/${form.id}`, form)
          ElMessage.success('更新成功')
        } else {
          await axios.post('/api/contracts/', form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchContracts()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这条合同吗？', '提示', {
      type: 'warning'
    })
    await axios.delete(`/api/contracts/${row.id}`)
    ElMessage.success('删除成功')
    fetchContracts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchContracts()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.contract-list-container {
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  min-height: 100%;
}

/* 页面头部 - 玻璃拟态风格 */
.page-header {
  position: relative;
  margin-bottom: 24px;
  padding: 28px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px -10px rgba(102, 126, 234, 0.4);
}

.page-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at top right, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse at bottom left, rgba(118, 75, 162, 0.3) 0%, transparent 50%);
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

.stat-card-total::before { background: linear-gradient(90deg, #667eea, #764ba2); }
.stat-card-active::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-completed::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-amount::before { background: linear-gradient(90deg, #ec4899, #f472b6); }

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
  color: #667eea;
  box-shadow: 0 4px 15px -3px rgba(102, 126, 234, 0.4);
}

.stat-icon-wrapper-active {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-completed {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-amount {
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-active .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-completed .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-amount .stat-value {
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
  color: #6366f1;
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(102, 126, 234, 0.5);
}

.btn-secondary {
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(99, 102, 241, 0.1);
  border-color: #6366f1;
  color: #6366f1;
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
  color: #6366f1;
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
  --el-table-row-hover-bg-color: rgba(99, 102, 241, 0.05);
}

.custom-table :deep(.el-table__header th) {
  font-weight: 600;
  color: #1e293b;
  background: rgba(241, 245, 249, 0.8);
}

.custom-table :deep(.el-table__row) {
  transition: all 0.3s;
}

.contract-no-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
}

.contract-title {
  font-weight: 600;
  color: #1e293b;
}

.type-tag,
.status-tag,
.risk-tag {
  font-weight: 500;
  border-radius: 6px;
}

.party-name {
  color: #475569;
  font-size: 13px;
}

.amount-value {
  font-family: 'Monaco', 'Menlo', monospace;
  font-weight: 600;
  color: #059669;
  font-size: 13px;
}

.region-text {
  color: #64748b;
  font-size: 13px;
}

.date-info {
  line-height: 1.4;
}

.date-main {
  font-size: 13px;
  color: #475569;
}

.date-remaining {
  font-size: 11px;
  color: #f59e0b;
  margin-top: 2px;
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

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .contract-list-container {
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

  .btn-gradient {
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

  :deep(.el-pagination) {
    font-size: 11px;
    flex-wrap: wrap;
    gap: 4px;
  }

  :deep(.el-pagination__sizes),
  :deep(.el-pagination__jump) {
    display: none !important;
  }

  :deep(.el-pagination button),
  :deep(.el-pager li) {
    min-width: 28px !important;
    height: 28px !important;
    line-height: 28px !important;
  }

  .contract-dialog {
    width: 95% !important;
    margin: 10px auto !important;
    max-height: 90vh !important;
  }

  .contract-dialog :deep(.el-dialog__header) {
    padding: 12px !important;
  }

  .contract-dialog :deep(.el-dialog__title) {
    font-size: 16px !important;
  }

  .contract-dialog :deep(.el-dialog__body) {
    padding: 12px !important;
    max-height: 60vh !important;
    overflow-y: auto !important;
  }

  .contract-dialog :deep(.el-dialog__footer) {
    padding: 12px !important;
  }

  .el-form-item {
    margin-bottom: 12px !important;
  }

  .el-form-item__label {
    font-size: 12px !important;
    padding-bottom: 4px !important;
  }

  .el-input__inner,
  .el-textarea__inner {
    font-size: 14px !important;
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

  .contract-dialog {
    width: 98% !important;
    margin: 5px auto !important;
  }
}
</style>
