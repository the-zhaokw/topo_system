<template>
  <div class="contract-detail">
    <div class="page-header">
      <el-button @click="goBack">返回</el-button>
      <h2>{{ contract.contract_no }} - {{ contract.title }}</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleEdit">编辑</el-button>
        <el-button type="success" @click="handleApprove" v-if="canApprove">审批</el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="基本信息" name="basic">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="合同编号">{{ contract.contract_no }}</el-descriptions-item>
          <el-descriptions-item label="合同名称">{{ contract.title }}</el-descriptions-item>
          <el-descriptions-item label="合同类型">{{ getTypeName(contract.contract_type) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTag(contract.status)">{{ getStatusName(contract.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="风险等级">
            <el-tag :type="getRiskTag(contract.risk_level)">{{ getRiskName(contract.risk_level) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="甲方">{{ contract.party_a_name }}</el-descriptions-item>
          <el-descriptions-item label="乙方">{{ contract.party_b_name }}</el-descriptions-item>
          <el-descriptions-item label="签约日期">{{ formatDate(contract.signing_date) }}</el-descriptions-item>
          <el-descriptions-item label="生效日期">{{ formatDate(contract.effective_date) }}</el-descriptions-item>
          <el-descriptions-item label="到期日期">{{ formatDate(contract.expiration_date) }}</el-descriptions-item>
          <el-descriptions-item label="金额">
            {{ formatAmount(contract.total_amount, contract.currency) }}
          </el-descriptions-item>
          <el-descriptions-item label="区域">{{ contract.region }}</el-descriptions-item>
          <el-descriptions-item label="国家">{{ contract.country }}</el-descriptions-item>
          <el-descriptions-item label="知识产权保护">
            <el-tag :type="contract.ip_protection_required ? 'warning' : 'info'">
              {{ contract.ip_protection_required ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="出口管制">
            <el-tag :type="contract.export_control_applicable ? 'danger' : 'info'">
              {{ contract.export_control_applicable ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider>技术要求</el-divider>
        <div class="content-box">{{ contract.technical_requirements || '无' }}</div>

        <el-divider>交付要求</el-divider>
        <div class="content-box">{{ contract.delivery_requirements || '无' }}</div>

        <el-divider>验收标准</el-divider>
        <div class="content-box">{{ contract.acceptance_criteria || '无' }}</div>

        <el-divider>SLA要求</el-divider>
        <div class="content-box">{{ contract.sla_requirements || '无' }}</div>
      </el-tab-pane>

      <el-tab-pane label="交付管理" name="delivery">
        <div class="tab-header">
          <el-button type="primary" @click="showDeliveryDialog = true">添加交付记录</el-button>
        </div>
        <el-table :data="deliveries" stripe v-loading="deliveryLoading">
          <el-table-column prop="delivery_no" label="交付编号" width="150" />
          <el-table-column prop="site_name" label="站点名称" width="150" />
          <el-table-column prop="site_code" label="站点编号" width="120" />
          <el-table-column prop="equipment_type" label="设备类型" width="120" />
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column prop="planned_date" label="计划日期" width="120">
            <template #default="{ row }">{{ formatDate(row.planned_date) }}</template>
          </el-table-column>
          <el-table-column prop="actual_date" label="实际日期" width="120">
            <template #default="{ row }">{{ formatDate(row.actual_date) }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getDeliveryStatusTag(row.status)">{{ getDeliveryStatusName(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="location" label="位置" show-overflow-tooltip />
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button link type="primary" @click="updateDeliveryStatus(row)">更新状态</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="付款计划" name="payment">
        <div class="tab-header">
          <el-button type="primary" @click="showPaymentDialog = true">添加付款计划</el-button>
        </div>
        <el-table :data="payments" stripe v-loading="paymentLoading">
          <el-table-column prop="payment_no" label="付款编号" width="150" />
          <el-table-column prop="payment_stage" label="付款阶段" width="150" />
          <el-table-column prop="planned_amount" label="计划金额" width="120">
            <template #default="{ row }">{{ formatAmount(row.planned_amount, row.currency) }}</template>
          </el-table-column>
          <el-table-column prop="actual_amount" label="实际金额" width="120">
            <template #default="{ row }">{{ formatAmount(row.actual_amount, row.currency) }}</template>
          </el-table-column>
          <el-table-column prop="planned_date" label="计划日期" width="120">
            <template #default="{ row }">{{ formatDate(row.planned_date) }}</template>
          </el-table-column>
          <el-table-column prop="actual_date" label="实际日期" width="120">
            <template #default="{ row }">{{ formatDate(row.actual_date) }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getPaymentStatusTag(row.status)">{{ getPaymentStatusName(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="invoice_no" label="发票号" width="120" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="变更记录" name="changes">
        <div class="tab-header">
          <el-button type="primary" @click="showChangeDialog = true">发起变更</el-button>
        </div>
        <el-table :data="changes" stripe v-loading="changeLoading">
          <el-table-column prop="change_no" label="变更编号" width="150" />
          <el-table-column prop="change_type" label="变更类型" width="120" />
          <el-table-column prop="change_description" label="变更描述" show-overflow-tooltip />
          <el-table-column label="金额变更" width="150">
            <template #default="{ row }">
              {{ formatAmount(row.original_value, 'CNY') }} → {{ formatAmount(row.new_value, 'CNY') }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getChangeStatusTag(row.status)">{{ getChangeStatusName(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="申请日期" width="120">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="风险管理" name="risk">
        <div class="tab-header">
          <el-button type="primary" @click="showRiskDialog = true">添加风险</el-button>
        </div>
        <el-table :data="risks" stripe v-loading="riskLoading">
          <el-table-column prop="risk_type" label="风险类型" width="120" />
          <el-table-column prop="risk_description" label="风险描述" show-overflow-tooltip />
          <el-table-column prop="risk_level" label="风险等级" width="100">
            <template #default="{ row }">
              <el-tag :type="getRiskTag(row.risk_level)">{{ getRiskName(row.risk_level) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="mitigation_measures" label="缓解措施" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'resolved' ? 'success' : 'danger'">
                {{ row.status === 'resolved' ? '已解决' : '已识别' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button link type="primary" @click="resolveRisk(row)" v-if="row.status !== 'resolved'">标记解决</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="审批记录" name="approval">
        <el-table :data="approvals" stripe v-loading="approvalLoading">
          <el-table-column prop="approval_level" label="审批级别" width="100" />
          <el-table-column prop="approver_role" label="审批角色" width="120" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getApprovalStatusTag(row.status)">{{ getApprovalStatusName(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="comments" label="审批意见" show-overflow-tooltip />
          <el-table-column prop="approval_date" label="审批日期" width="180">
            <template #default="{ row }">{{ formatDate(row.approval_date) }}</template>
          </el-table-column>
        </el-table>
        <div class="tab-header" style="margin-top: 20px">
          <el-button type="primary" @click="handleApprove">提交审批</el-button>
        </div>
      </el-tab-pane>

      <el-tab-pane label="附件" name="attachments">
        <div class="tab-header">
          <el-button type="primary" @click="showAttachmentDialog = true">上传附件</el-button>
        </div>
        <el-table :data="attachments" stripe v-loading="attachmentLoading">
          <el-table-column prop="file_name" label="文件名" show-overflow-tooltip />
          <el-table-column prop="file_type" label="文件类型" width="100" />
          <el-table-column prop="attachment_type" label="附件类型" width="120" />
          <el-table-column prop="description" label="描述" show-overflow-tooltip />
          <el-table-column prop="uploaded_by" label="上传人" width="100" />
          <el-table-column prop="created_at" label="上传时间" width="180">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showDeliveryDialog" title="添加交付记录" width="500px">
      <el-form :model="deliveryForm" label-width="100px">
        <el-form-item label="站点名称">
          <el-input v-model="deliveryForm.site_name" />
        </el-form-item>
        <el-form-item label="站点编号">
          <el-input v-model="deliveryForm.site_code" />
        </el-form-item>
        <el-form-item label="设备类型">
          <el-input v-model="deliveryForm.equipment_type" />
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="deliveryForm.quantity" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="计划日期">
          <el-date-picker v-model="deliveryForm.planned_date" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="deliveryForm.location" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDeliveryDialog = false">取消</el-button>
        <el-button type="primary" @click="submitDelivery">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showPaymentDialog" title="添加付款计划" width="500px">
      <el-form :model="paymentForm" label-width="100px">
        <el-form-item label="付款阶段">
          <el-input v-model="paymentForm.payment_stage" />
        </el-form-item>
        <el-form-item label="计划金额">
          <el-input-number v-model="paymentForm.planned_amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="币种">
          <el-select v-model="paymentForm.currency" style="width: 100%">
            <el-option label="人民币 (CNY)" value="CNY" />
            <el-option label="美元 (USD)" value="USD" />
            <el-option label="欧元 (EUR)" value="EUR" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划日期">
          <el-date-picker v-model="paymentForm.planned_date" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="付款方式">
          <el-input v-model="paymentForm.payment_method" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPaymentDialog = false">取消</el-button>
        <el-button type="primary" @click="submitPayment">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showChangeDialog" title="发起变更" width="500px">
      <el-form :model="changeForm" label-width="100px">
        <el-form-item label="变更类型">
          <el-select v-model="changeForm.change_type" style="width: 100%">
            <el-option label="数量变更" value="quantity_change" />
            <el-option label="价格变更" value="price_change" />
            <el-option label="交付时间变更" value="delivery_change" />
            <el-option label="技术变更" value="technical_change" />
          </el-select>
        </el-form-item>
        <el-form-item label="变更描述">
          <el-input v-model="changeForm.change_description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="原值">
          <el-input-number v-model="changeForm.original_value" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="新值">
          <el-input-number v-model="changeForm.new_value" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="影响评估">
          <el-input v-model="changeForm.impact_assessment" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showChangeDialog = false">取消</el-button>
        <el-button type="primary" @click="submitChange">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showRiskDialog" title="添加风险" width="500px">
      <el-form :model="riskForm" label-width="100px">
        <el-form-item label="风险类型">
          <el-select v-model="riskForm.risk_type" style="width: 100%">
            <el-option label="知识产权风险" value="ip_risk" />
            <el-option label="交付风险" value="delivery_risk" />
            <el-option label="合规风险" value="compliance_risk" />
            <el-option label="财务风险" value="financial_risk" />
            <el-option label="汇率风险" value="exchange_risk" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险描述">
          <el-input v-model="riskForm.risk_description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="风险等级">
          <el-select v-model="riskForm.risk_level" style="width: 100%">
            <el-option label="低风险" value="low" />
            <el-option label="中风险" value="medium" />
            <el-option label="高风险" value="high" />
            <el-option label="重大风险" value="critical" />
          </el-select>
        </el-form-item>
        <el-form-item label="缓解措施">
          <el-input v-model="riskForm.mitigation_measures" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRiskDialog = false">取消</el-button>
        <el-button type="primary" @click="submitRisk">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showAttachmentDialog" title="上传附件" width="500px">
      <el-form :model="attachmentForm" label-width="100px">
        <el-form-item label="文件名">
          <el-input v-model="attachmentForm.file_name" />
        </el-form-item>
        <el-form-item label="附件类型">
          <el-select v-model="attachmentForm.attachment_type" style="width: 100%">
            <el-option label="合同正文" value="contract_body" />
            <el-option label="技术附件" value="technical_attachment" />
            <el-option label="商务附件" value="business_attachment" />
            <el-option label="验收报告" value="acceptance_report" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="attachmentForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAttachmentDialog = false">取消</el-button>
        <el-button type="primary" @click="submitAttachment">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showApproveDialog" title="合同审批" width="500px">
      <el-form :model="approveForm" label-width="100px">
        <el-form-item label="审批决定">
          <el-radio-group v-model="approveForm.status">
            <el-radio label="approved">批准</el-radio>
            <el-radio label="rejected">拒绝</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审批意见">
          <el-input v-model="approveForm.comments" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showApproveDialog = false">取消</el-button>
        <el-button type="primary" @click="submitApproval">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const contractId = route.params.id
const activeTab = ref('basic')

const contract = ref({})
const approvals = ref([])
const deliveries = ref([])
const changes = ref([])
const risks = ref([])
const payments = ref([])
const attachments = ref([])

const deliveryLoading = ref(false)
const paymentLoading = ref(false)
const changeLoading = ref(false)
const riskLoading = ref(false)
const approvalLoading = ref(false)
const attachmentLoading = ref(false)

const showDeliveryDialog = ref(false)
const showPaymentDialog = ref(false)
const showChangeDialog = ref(false)
const showRiskDialog = ref(false)
const showAttachmentDialog = ref(false)
const showApproveDialog = ref(false)

const deliveryForm = reactive({
  site_name: '',
  site_code: '',
  equipment_type: '',
  quantity: 0,
  planned_date: null,
  location: ''
})

const paymentForm = reactive({
  payment_stage: '',
  planned_amount: 0,
  currency: 'CNY',
  planned_date: null,
  payment_method: ''
})

const changeForm = reactive({
  change_type: '',
  change_description: '',
  original_value: 0,
  new_value: 0,
  impact_assessment: ''
})

const riskForm = reactive({
  risk_type: '',
  risk_description: '',
  risk_level: 'medium',
  mitigation_measures: ''
})

const attachmentForm = reactive({
  file_name: '',
  attachment_type: '',
  description: ''
})

const approveForm = reactive({
  status: 'approved',
  comments: ''
})

const canApprove = ref(true)

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

const getTypeTag = (type) => ''
const getStatusTag = (status) => {
  const map = { draft: 'info', pending_review: 'warning', pending_approval: 'warning', active: 'success', expired: 'danger', terminated: 'danger' }
  return map[status] || ''
}
const getRiskTag = (risk) => {
  const map = { low: 'success', medium: 'warning', high: 'danger', critical: 'danger' }
  return map[risk] || ''
}

const getDeliveryStatusName = (status) => {
  const map = { pending: '待处理', in_production: '生产中', shipped: '已发货', in_transit: '运输中', customs_clearance: '清关中', installation: '安装中', commissioning: '调试中', acceptance_testing: '验收中', accepted: '已验收', rejected: '已拒绝' }
  return map[status] || status
}
const getDeliveryStatusTag = (status) => {
  const map = { pending: 'info', in_production: 'warning', shipped: '', in_transit: '', customs_clearance: 'warning', installation: 'warning', commissioning: 'warning', acceptance_testing: 'warning', accepted: 'success', rejected: 'danger' }
  return map[status] || ''
}

const getPaymentStatusName = (status) => {
  const map = { pending: '待付款', paid: '已付款', overdue: '逾期' }
  return map[status] || status
}
const getPaymentStatusTag = (status) => {
  const map = { pending: 'warning', paid: 'success', overdue: 'danger' }
  return map[status] || ''
}

const getChangeStatusName = (status) => {
  const map = { pending: '待审批', approved: '已批准', rejected: '已拒绝' }
  return map[status] || status
}
const getChangeStatusTag = (status) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || ''
}

const getApprovalStatusName = (status) => {
  const map = { pending: '待审批', approved: '已批准', rejected: '已拒绝' }
  return map[status] || status
}
const getApprovalStatusTag = (status) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || ''
}

const formatAmount = (amount, currency) => {
  if (!amount) return '0.00'
  const symbol = currency === 'USD' ? '$' : currency === 'EUR' ? '€' : '¥'
  return `${symbol}${parseFloat(amount).toLocaleString('en-US', { minimumFractionDigits: 2 })}`
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const fetchContract = async () => {
  try {
    const response = await axios.get(`/api/contracts/${contractId}`)
    contract.value = response.data.contract
  } catch (error) {
    ElMessage.error('获取合同详情失败')
  }
}

const fetchDeliveries = async () => {
  deliveryLoading.value = true
  try {
    const response = await axios.get(`/api/contracts/${contractId}/deliveries`)
    deliveries.value = response.data.deliveries
  } catch (error) {
    ElMessage.error('获取交付记录失败')
  } finally {
    deliveryLoading.value = false
  }
}

const fetchPayments = async () => {
  paymentLoading.value = true
  try {
    const response = await axios.get(`/api/contracts/${contractId}/payments`)
    payments.value = response.data.payments
  } catch (error) {
    ElMessage.error('获取付款计划失败')
  } finally {
    paymentLoading.value = false
  }
}

const fetchChanges = async () => {
  changeLoading.value = true
  try {
    const response = await axios.get(`/api/contracts/${contractId}/changes`)
    changes.value = response.data.changes
  } catch (error) {
    ElMessage.error('获取变更记录失败')
  } finally {
    changeLoading.value = false
  }
}

const fetchRisks = async () => {
  riskLoading.value = true
  try {
    const response = await axios.get(`/api/contracts/${contractId}/risks`)
    risks.value = response.data.risks
  } catch (error) {
    ElMessage.error('获取风险记录失败')
  } finally {
    riskLoading.value = false
  }
}

const fetchApprovals = async () => {
  approvalLoading.value = true
  try {
    const response = await axios.get(`/api/contracts/${contractId}/approvals`)
    approvals.value = response.data.approvals
  } catch (error) {
    ElMessage.error('获取审批记录失败')
  } finally {
    approvalLoading.value = false
  }
}

const fetchAttachments = async () => {
  attachmentLoading.value = true
  try {
    const response = await axios.get(`/api/contracts/${contractId}/attachments`)
    attachments.value = response.data.attachments
  } catch (error) {
    ElMessage.error('获取附件失败')
  } finally {
    attachmentLoading.value = false
  }
}

const goBack = () => {
  router.push('/contracts/list')
}

const handleEdit = () => {
  router.push(`/contracts/edit/${contractId}`)
}

const handleApprove = () => {
  showApproveDialog.value = true
}

const submitApproval = async () => {
  try {
    await axios.post(`/api/contracts/${contractId}/approvals`, approveForm)
    ElMessage.success('审批提交成功')
    showApproveDialog.value = false
    fetchApprovals()
    fetchContract()
  } catch (error) {
    ElMessage.error('审批提交失败')
  }
}

const submitDelivery = async () => {
  try {
    await axios.post(`/api/contracts/${contractId}/deliveries`, deliveryForm)
    ElMessage.success('添加成功')
    showDeliveryDialog.value = false
    fetchDeliveries()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const updateDeliveryStatus = async (row) => {
  const status = row.status === 'pending' ? 'accepted' : 'pending'
  try {
    await axios.put(`/api/contracts/${contractId}/deliveries/${row.id}`, { status })
    ElMessage.success('状态更新成功')
    fetchDeliveries()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const submitPayment = async () => {
  try {
    await axios.post(`/api/contracts/${contractId}/payments`, paymentForm)
    ElMessage.success('添加成功')
    showPaymentDialog.value = false
    fetchPayments()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const submitChange = async () => {
  try {
    await axios.post(`/api/contracts/${contractId}/changes`, changeForm)
    ElMessage.success('变更申请已提交')
    showChangeDialog.value = false
    fetchChanges()
  } catch (error) {
    ElMessage.error('提交失败')
  }
}

const submitRisk = async () => {
  try {
    await axios.post(`/api/contracts/${contractId}/risks`, riskForm)
    ElMessage.success('添加成功')
    showRiskDialog.value = false
    fetchRisks()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const resolveRisk = async (row) => {
  try {
    await axios.put(`/api/contracts/${contractId}/risks/${row.id}`, { status: 'resolved' })
    ElMessage.success('风险已解决')
    fetchRisks()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const submitAttachment = async () => {
  try {
    await axios.post(`/api/contracts/${contractId}/attachments`, attachmentForm)
    ElMessage.success('上传成功')
    showAttachmentDialog.value = false
    fetchAttachments()
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

onMounted(() => {
  fetchContract()
  fetchDeliveries()
  fetchPayments()
  fetchChanges()
  fetchRisks()
  fetchApprovals()
  fetchAttachments()
})
</script>

<style scoped>
.contract-detail {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  flex: 1;
  margin: 0 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.content-box {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  min-height: 40px;
}

.tab-header {
  margin-bottom: 15px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .contract-detail {
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

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 80px;
    font-size: 12px;
    padding: 8px 12px;
  }

  .info-section {
    margin-bottom: 16px;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .info-item {
    padding: 10px;
  }

  .info-label {
    font-size: 12px;
  }

  .info-value {
    font-size: 14px;
  }

  .tab-header {
    margin-bottom: 12px;
  }

  .el-tabs__nav {
    width: 100%;
  }

  .el-tabs__item {
    flex: 1;
    text-align: center;
    font-size: 13px;
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

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
  }
}

@media screen and (max-width: 480px) {
  .contract-detail {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .el-tabs__item {
    font-size: 12px;
    padding: 0 8px;
  }

  .el-table {
    font-size: 10px !important;
  }
}
</style>
