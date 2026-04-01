<template>
  <div class="contract-list">
    <div class="page-header">
      <h2>合同管理</h2>
      <el-button type="primary" @click="handleCreate">新建合同</el-button>
    </div>

    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="合同编号/名称/客户" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="合同状态">
          <el-select v-model="filterForm.status" placeholder="请选择" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="待审核" value="pending_review" />
            <el-option label="待审批" value="pending_approval" />
            <el-option label="执行中" value="active" />
            <el-option label="已过期" value="expired" />
            <el-option label="已终止" value="terminated" />
          </el-select>
        </el-form-item>
        <el-form-item label="合同类型">
          <el-select v-model="filterForm.contract_type" placeholder="请选择" clearable>
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
          <el-select v-model="filterForm.risk_level" placeholder="请选择" clearable>
            <el-option label="低风险" value="low" />
            <el-option label="中风险" value="medium" />
            <el-option label="高风险" value="high" />
            <el-option label="重大风险" value="critical" />
          </el-select>
        </el-form-item>
        <el-form-item label="区域">
          <el-input v-model="filterForm.region" placeholder="区域" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table :data="contracts" v-loading="loading" stripe>
        <el-table-column prop="contract_no" label="合同编号" width="150" />
        <el-table-column prop="title" label="合同名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="contract_type" label="合同类型" width="140">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.contract_type)">{{ getTypeName(row.contract_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">{{ getStatusName(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="risk_level" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskTag(row.risk_level)">{{ getRiskName(row.risk_level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="party_b_name" label="客户/供应商" width="150" show-overflow-tooltip />
        <el-table-column prop="total_amount" label="金额" width="120">
          <template #default="{ row }">
            {{ formatAmount(row.total_amount, row.currency) }}
          </template>
        </el-table-column>
        <el-table-column prop="region" label="区域" width="100" />
        <el-table-column prop="expiration_date" label="到期日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.expiration_date) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="70%" destroy-on-close>
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
              <el-select v-model="form.contract_type" placeholder="请选择">
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
              <el-select v-model="form.risk_level" placeholder="请选择">
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
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios'

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
.contract-list {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  margin-bottom: 0;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .contract-list {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  .page-header h2 {
    font-size: 18px;
  }

  .page-header .el-button {
    width: 100%;
  }

  .filter-card {
    margin-bottom: 16px;
  }

  .filter-form {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .filter-form .el-form-item {
    margin-right: 0;
    margin-bottom: 8px;
    width: 100%;
  }

  .filter-form .el-input,
  .filter-form .el-select {
    width: 100% !important;
  }

  .filter-form .el-form-item__label {
    font-size: 12px;
  }

  .table-card {
    margin-bottom: 16px;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
  }

  .pagination-container {
    justify-content: center;
    margin-top: 16px;
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

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
    max-height: 90vh !important;
  }

  .el-dialog__header {
    padding: 12px !important;
  }

  .el-dialog__title {
    font-size: 16px !important;
  }

  .el-dialog__body {
    padding: 12px !important;
    max-height: 60vh !important;
    overflow-y: auto !important;
  }

  .el-dialog__footer {
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
  .contract-list {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .el-table {
    font-size: 10px !important;
  }

  .el-dialog {
    width: 98% !important;
    margin: 5px auto !important;
  }
}
</style>
