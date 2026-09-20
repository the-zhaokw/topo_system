<template>
  <div class="contract-detail">
    <div class="page-header">
      <el-button @click="goBack">返回</el-button>
      <h2>{{ contract.contract_no }} - {{ contract.title }}</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleEdit">编辑</el-button>
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

      <el-tab-pane label="审批流程" name="approval">
        <div class="tab-header">
          <el-button
            v-if="!activeReview && canInitiateReview"
            type="success"
            @click="openInitiateReviewDialog"
          >
            <el-icon><Promotion /></el-icon>
            发起审批
          </el-button>
        </div>

        <div v-if="approvalLoading" v-loading="true" style="min-height: 200px"></div>
        <template v-else>
          <el-empty
            v-if="!contractReviews.length"
            description="暂无审批流程"
            :image-size="60"
          />
          <div
            v-for="review in contractReviews"
            :key="review.id"
            class="review-block"
            :class="{ 'review-active': review.status === 'pending' }"
          >
            <div class="review-header">
              <el-tag :type="getReviewStatusType(review.status)" size="small">
                {{ review.status_text }}
              </el-tag>
              <span class="review-meta">
                发起人：{{ review.initiator_name }} ｜ {{ formatDate(review.created_at) }}
                <template v-if="review.deadline"> ｜ 截止：{{ formatDate(review.deadline) }}</template>
              </span>
              <el-button
                v-if="review.status === 'pending' && canCancelReview(review)"
                type="danger"
                link
                size="small"
                @click="handleCancelReview(review)"
              >撤销审批</el-button>
            </div>
            <div v-if="review.comment" class="review-comment">发起说明：{{ review.comment }}</div>

            <!-- 审批节点链 -->
            <div class="review-steps">
              <div
                v-for="step in review.steps"
                :key="step.id"
                class="review-step"
                :class="getStepClass(review, step)"
              >
                <div class="step-indicator">
                  <el-icon v-if="step.status === 'approved'" class="icon-approved"><CircleCheckFilled /></el-icon>
                  <el-icon v-else-if="step.status === 'rejected'" class="icon-rejected"><CircleCloseFilled /></el-icon>
                  <el-icon v-else-if="review.status === 'pending' && review.current_step === step.step_order" class="icon-current"><Loading /></el-icon>
                  <el-icon v-else class="icon-waiting"><Clock /></el-icon>
                </div>
                <div class="step-body">
                  <div class="step-title">
                    <span class="step-name">{{ step.name }}</span>
                    <el-tag size="small" :type="getStepStatusType(step.status)">{{ step.status_text }}</el-tag>
                    <span class="step-reviewer">审批人：{{ step.reviewer_name }}</span>
                  </div>
                  <div v-if="step.comment" class="step-comment">{{ step.comment }}</div>
                  <div v-if="step.acted_at" class="step-time">处理时间：{{ formatDate(step.acted_at) }}</div>
                </div>
              </div>
            </div>

            <!-- 当前节点审批人操作区 -->
            <div v-if="review.status === 'pending' && canActReview(review)" class="review-actions">
              <el-input
                v-model="reviewActionComments[review.id]"
                type="textarea"
                :rows="2"
                placeholder="请输入审批意见（通过时可选，驳回时必填）"
              />
              <div class="review-action-btns">
                <el-button type="success" size="small" :loading="reviewActing" @click="handleApproveReview(review)">
                  <el-icon><Check /></el-icon>
                  通过
                </el-button>
                <el-button type="danger" size="small" :loading="reviewActing" @click="handleRejectReview(review)">
                  <el-icon><Close /></el-icon>
                  驳回
                </el-button>
              </div>
            </div>
          </div>
        </template>
      </el-tab-pane>

      <el-tab-pane label="附件" name="attachments">
        <div class="tab-header">
          <el-button type="primary" @click="openAttachmentDialog">上传附件</el-button>
        </div>
        <el-table :data="attachments" stripe v-loading="attachmentLoading">
          <el-table-column prop="file_name" label="文件名" show-overflow-tooltip />
          <el-table-column label="文件大小" width="120">
            <template #default="{ row }">{{ formatFileSize(row.file_size) }}</template>
          </el-table-column>
          <el-table-column prop="file_type" label="文件类型" width="160" show-overflow-tooltip />
          <el-table-column prop="attachment_type" label="附件类型" width="120">
            <template #default="{ row }">{{ getAttachmentTypeName(row.attachment_type) }}</template>
          </el-table-column>
          <el-table-column prop="description" label="描述" show-overflow-tooltip />
          <el-table-column prop="uploaded_by" label="上传人" width="100" />
          <el-table-column prop="created_at" label="上传时间" width="180">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="previewAttachment(row)">在线查看</el-button>
              <el-button link type="success" @click="downloadAttachment(row)">下载</el-button>
              <el-button link type="danger" @click="deleteAttachment(row)">删除</el-button>
            </template>
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

    <el-dialog v-model="showAttachmentDialog" title="上传附件" width="560px" @close="resetAttachmentForm">
      <el-form :model="attachmentForm" label-width="100px">
        <el-form-item label="选择文件" required>
          <el-upload
            ref="attachmentUploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleAttachmentFileChange"
            :on-exceed="handleAttachmentExceed"
            :on-remove="handleAttachmentRemove"
            accept="*/*"
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">将文件拖到此处，或<em>点击选择</em></div>
            <template #tip>
              <div class="el-upload__tip">支持任意类型文件，单个文件最大 50MB</div>
            </template>
          </el-upload>
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
        <el-button type="primary" :loading="attachmentSubmitting" @click="submitAttachment">上传</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showInitiateDialog" title="发起合同审批" width="550px">
      <el-form :model="initiateForm" label-width="100px">
        <el-form-item label="审批人员" required>
          <el-select
            v-model="initiateForm.reviewers"
            multiple
            filterable
            placeholder="选择审批人员，按选择顺序逐级审批"
            style="width: 100%"
          >
            <el-option
              v-for="u in availableReviewers"
              :key="u.id"
              :label="u.username"
              :value="u.id"
            />
          </el-select>
          <div class="form-tip">按选择顺序逐级审批，全部通过后合同变为"执行中"；任一人驳回则退回。</div>
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker
            v-model="initiateForm.deadline"
            type="datetime"
            placeholder="可选"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="发起说明">
          <el-input v-model="initiateForm.comment" type="textarea" :rows="3" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showInitiateDialog = false">取消</el-button>
        <el-button type="primary" :loading="initiatingReview" @click="handleInitiateReview">发起审批</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Promotion, CircleCheckFilled, CircleCloseFilled, Loading, Clock, Check, Close
} from '@element-plus/icons-vue'
import api from '@/services/api'
import { parseUTCDate } from '@/utils/dateUtils'
import { useUserStore } from '@/stores/user'
import { useAllUsers } from '@/composables/useAllUsers'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { allUsers, fetchAll } = useAllUsers()

const contractId = route.params.id
const activeTab = ref('basic')

const contract = ref({})
const contractReviews = ref([])
const activeReview = computed(() => contractReviews.value.find(r => r.status === 'pending') || null)
const reviewActionComments = ref({})
const reviewActing = ref(false)
const initiatingReview = ref(false)

const canApprove = computed(() => {
  const u = userStore.currentUser
  if (!u) return false
  if (u.is_super_admin) return true
  return u.position === '管理员' || u.position?.includes('经理')
})

const canInitiateReview = computed(() => {
  const u = userStore.currentUser
  if (!u) return false
  if (contract.value.status === 'active' || contract.value.status === 'expired' || contract.value.status === 'terminated') return false
  return u.is_super_admin || canApprove.value || contract.value.created_by === u.id
})

const availableReviewers = computed(() => allUsers.value)

const canCancelReview = (review) => {
  const u = userStore.currentUser
  if (!u || !review) return false
  if (u.is_super_admin || canApprove.value) return true
  return review.initiator_id === u.id
}

const canActReview = (review) => {
  const u = userStore.currentUser
  if (!u || !review || review.status !== 'pending') return false
  if (u.is_super_admin || canApprove.value) return true
  const currentStep = (review.steps || []).find(
    s => s.step_order === review.current_step && s.status === 'pending'
  )
  return currentStep && currentStep.reviewer_id === u.id
}

const getReviewStatusType = (status) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger', cancelled: 'info' }
  return map[status] || 'info'
}

const getStepStatusType = (status) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

const getStepClass = (review, step) => {
  if (step.status === 'approved') return 'step-approved'
  if (step.status === 'rejected') return 'step-rejected'
  if (review.status === 'pending' && review.current_step === step.step_order) return 'step-current'
  return 'step-waiting'
}

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
const showInitiateDialog = ref(false)
const attachmentSubmitting = ref(false)
const attachmentUploadRef = ref(null)
const attachmentSelectedFile = ref(null)

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
  attachment_type: 'other',
  description: ''
})

const initiateForm = reactive({
  reviewers: [],
  deadline: null,
  comment: ''
})

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

const attachmentTypeMap = {
  contract_body: '合同正文',
  technical_attachment: '技术附件',
  business_attachment: '商务附件',
  acceptance_report: '验收报告',
  other: '其他'
}

const getTypeName = (type) => typeMap[type] || type
const getStatusName = (status) => statusMap[status] || status
const getRiskName = (risk) => riskMap[risk] || risk
const getAttachmentTypeName = (type) => attachmentTypeMap[type] || type || '其他'

// 文件大小友好展示
const formatFileSize = (bytes) => {
  if (!bytes && bytes !== 0) return '-'
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = Number(bytes)
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }
  return `${size.toFixed(i === 0 ? 0 : 1)} ${units[i]}`
}

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
  return parseUTCDate(date).toLocaleDateString('zh-CN')
}

const fetchContract = async () => {
  try {
    const response = await api.get(`/contracts/${contractId}`)
    contract.value = response.contract
  } catch (error) {
    ElMessage.error('获取合同详情失败')
  }
}

const fetchDeliveries = async () => {
  deliveryLoading.value = true
  try {
    const response = await api.get(`/contracts/${contractId}/deliveries`)
    deliveries.value = response.deliveries
  } catch (error) {
    ElMessage.error('获取交付记录失败')
  } finally {
    deliveryLoading.value = false
  }
}

const fetchPayments = async () => {
  paymentLoading.value = true
  try {
    const response = await api.get(`/contracts/${contractId}/payments`)
    payments.value = response.payments
  } catch (error) {
    ElMessage.error('获取付款计划失败')
  } finally {
    paymentLoading.value = false
  }
}

const fetchChanges = async () => {
  changeLoading.value = true
  try {
    const response = await api.get(`/contracts/${contractId}/changes`)
    changes.value = response.changes
  } catch (error) {
    ElMessage.error('获取变更记录失败')
  } finally {
    changeLoading.value = false
  }
}

const fetchRisks = async () => {
  riskLoading.value = true
  try {
    const response = await api.get(`/contracts/${contractId}/risks`)
    risks.value = response.risks
  } catch (error) {
    ElMessage.error('获取风险记录失败')
  } finally {
    riskLoading.value = false
  }
}

const fetchReviews = async () => {
  approvalLoading.value = true
  try {
    const response = await api.get(`/contracts/${contractId}/reviews`)
    contractReviews.value = response.reviews || []
  } catch (error) {
    console.error('获取审批流程失败:', error)
  } finally {
    approvalLoading.value = false
  }
}

const openInitiateReviewDialog = () => {
  initiateForm.reviewers = []
  initiateForm.deadline = null
  initiateForm.comment = ''
  showInitiateDialog.value = true
}

const handleInitiateReview = async () => {
  if (!initiateForm.reviewers.length) {
    ElMessage.warning('请至少选择一名审批人')
    return
  }
  initiatingReview.value = true
  try {
    const response = await api.post(`/contracts/${contractId}/reviews`, {
      reviewers: initiateForm.reviewers,
      deadline: initiateForm.deadline,
      comment: initiateForm.comment
    })
    if (response.success) {
      ElMessage.success(response.message || '审批流程已发起')
      showInitiateDialog.value = false
      await fetchContract()
      await fetchReviews()
    } else {
      ElMessage.error(response.error || '发起审批失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '发起审批失败')
  } finally {
    initiatingReview.value = false
  }
}

const handleApproveReview = async (review) => {
  try {
    await ElMessageBox.confirm('确认通过当前审批节点？', '审批确认', {
      confirmButtonText: '确定通过',
      cancelButtonText: '取消',
      type: 'success'
    })
  } catch (e) {
    return
  }
  reviewActing.value = true
  try {
    await api.post(`/contracts/reviews/${review.id}/approve`, {
      comment: reviewActionComments.value[review.id] || ''
    })
    ElMessage.success('审批已通过')
    reviewActionComments.value = { ...reviewActionComments.value, [review.id]: '' }
    await Promise.all([fetchContract(), fetchReviews()])
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '审批通过失败')
  } finally {
    reviewActing.value = false
  }
}

const handleRejectReview = async (review) => {
  let reason = reviewActionComments.value[review.id] || ''
  try {
    const { value } = await ElMessageBox.prompt('请填写驳回原因（必填）', '驳回审批', {
      confirmButtonText: '确定驳回',
      cancelButtonText: '取消',
      inputType: 'textarea',
      inputPlaceholder: '请说明驳回原因，将通知发起人',
      inputValue: reason,
      inputValidator: (val) => (val && val.trim()) ? true : '驳回原因不能为空'
    })
    reason = value
  } catch (e) {
    return
  }
  reviewActing.value = true
  try {
    await api.post(`/contracts/reviews/${review.id}/reject`, { comment: reason })
    ElMessage.success('已驳回')
    reviewActionComments.value = { ...reviewActionComments.value, [review.id]: '' }
    await Promise.all([fetchContract(), fetchReviews()])
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '驳回失败')
  } finally {
    reviewActing.value = false
  }
}

const handleCancelReview = async (review) => {
  try {
    await ElMessageBox.confirm('撤销后审批流程终止，合同退回草稿状态。确认撤销？', '撤销审批', {
      confirmButtonText: '确定撤销',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch (e) {
    return
  }
  try {
    await api.post(`/contracts/reviews/${review.id}/cancel`)
    ElMessage.success('审批已撤销')
    await Promise.all([fetchContract(), fetchReviews()])
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '撤销失败')
  }
}

const fetchAttachments = async () => {
  attachmentLoading.value = true
  try {
    const response = await api.get(`/contracts/${contractId}/attachments`)
    attachments.value = response.attachments
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
  router.push(`/contracts/list?edit=${contractId}`)
}

const submitDelivery = async () => {
  try {
    await api.post(`/contracts/${contractId}/deliveries`, deliveryForm)
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
    await api.put(`/contracts/${contractId}/deliveries/${row.id}`, { status })
    ElMessage.success('状态更新成功')
    fetchDeliveries()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const submitPayment = async () => {
  try {
    await api.post(`/contracts/${contractId}/payments`, paymentForm)
    ElMessage.success('添加成功')
    showPaymentDialog.value = false
    fetchPayments()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const submitChange = async () => {
  try {
    await api.post(`/contracts/${contractId}/changes`, changeForm)
    ElMessage.success('变更申请已提交')
    showChangeDialog.value = false
    fetchChanges()
  } catch (error) {
    ElMessage.error('提交失败')
  }
}

const submitRisk = async () => {
  try {
    await api.post(`/contracts/${contractId}/risks`, riskForm)
    ElMessage.success('添加成功')
    showRiskDialog.value = false
    fetchRisks()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const resolveRisk = async (row) => {
  try {
    await api.put(`/contracts/${contractId}/risks/${row.id}`, { status: 'resolved' })
    ElMessage.success('风险已解决')
    fetchRisks()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// ============ 附件相关 ============
const openAttachmentDialog = () => {
  resetAttachmentForm()
  showAttachmentDialog.value = true
}

const resetAttachmentForm = () => {
  attachmentForm.attachment_type = 'other'
  attachmentForm.description = ''
  attachmentSelectedFile.value = null
  // 清空 el-upload 的文件列表
  if (attachmentUploadRef.value) {
    attachmentUploadRef.value.clearFiles()
  }
}

const handleAttachmentFileChange = (file) => {
  // 单文件模式：每次选择都以最新文件为准
  attachmentSelectedFile.value = file.raw
}

const handleAttachmentExceed = () => {
  ElMessage.warning('一次只能上传一个文件，请先移除已选文件')
}

const handleAttachmentRemove = () => {
  attachmentSelectedFile.value = null
}

const submitAttachment = async () => {
  if (!attachmentSelectedFile.value) {
    ElMessage.warning('请先选择要上传的文件')
    return
  }
  // 前端大小校验（50MB）
  if (attachmentSelectedFile.value.size > 50 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 50MB')
    return
  }

  const formData = new FormData()
  formData.append('file', attachmentSelectedFile.value)
  formData.append('attachment_type', attachmentForm.attachment_type || 'other')
  if (attachmentForm.description) {
    formData.append('description', attachmentForm.description)
  }

  attachmentSubmitting.value = true
  try {
    await api.post(`/contracts/${contractId}/attachments`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success('上传成功')
    showAttachmentDialog.value = false
    fetchAttachments()
  } catch (error) {
    // 错误消息已由响应拦截器统一处理
  } finally {
    attachmentSubmitting.value = false
  }
}

// 以 blob 方式获取附件内容（携带 JWT），返回 Blob
const fetchAttachmentBlob = async (row, asDownload = false) => {
  const url = `/contracts/${contractId}/attachments/${row.id}${asDownload ? '?mode=download' : ''}`
  const response = await api.get(url, { responseType: 'blob' })
  return response
}

// 在线查看：拉取 blob 并在新标签页打开
const previewAttachment = async (row) => {
  try {
    const response = await fetchAttachmentBlob(row, false)
    const blob = response.data
    // 浏览器无法直接预览的，回退为下载
    const contentType = row.file_type || response.headers?.['content-type'] || blob.type
    const downloadableTypes = ['application/octet-stream', '']
    const url = URL.createObjectURL(blob)
    // 文本/图片/PDF/视频/音频等可内嵌预览
    const inlineRegex = /^(image\/|video\/|audio\/|text\/|application\/pdf|application\/vnd\.|application\/ms|application\/x-)/i
    if (inlineRegex.test(contentType) && !downloadableTypes.includes(contentType)) {
      window.open(url, '_blank')
    } else if (contentType === 'text/plain' || row.file_name?.toLowerCase().match(/\.(txt|log|csv|json|md)$/)) {
      window.open(url, '_blank')
    } else {
      // 不支持预览时直接触发下载
      triggerBlobDownload(blob, row.file_name)
      URL.revokeObjectURL(url)
      ElMessage.info('该文件类型不支持在线预览，已开始下载')
    }
  } catch (error) {
    ElMessage.error('获取附件失败')
  }
}

// 下载
const downloadAttachment = async (row) => {
  try {
    const response = await fetchAttachmentBlob(row, true)
    triggerBlobDownload(response.data, row.file_name)
  } catch (error) {
    ElMessage.error('下载附件失败')
  }
}

// 触发浏览器下载
const triggerBlobDownload = (blob, filename) => {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename || 'download'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  // 稍延迟释放，避免某些浏览器下载未启动
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

// 删除附件
const deleteAttachment = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除附件「${row.file_name}」吗？该操作不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
  } catch (e) {
    return
  }
  try {
    await api.delete(`/contracts/${contractId}/attachments/${row.id}`)
    ElMessage.success('附件已删除')
    fetchAttachments()
  } catch (error) {
    ElMessage.error('删除附件失败')
  }
}

onMounted(() => {
  fetchContract()
  fetchDeliveries()
  fetchPayments()
  fetchChanges()
  fetchRisks()
  fetchReviews()
  fetchAttachments()
  fetchAll()
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

/* ===== 审批流程样式（与需求审批同款） ===== */
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}

.review-block {
  border: 1px solid #ebeef5;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 16px;
  background: #fafbfc;
  transition: all 0.3s;
}

.review-block.review-active {
  border-color: #e6a23c;
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.06) 0%, #fafbfc 100%);
}

.review-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.review-meta {
  color: #909399;
  font-size: 12px;
  flex: 1;
}

.review-comment {
  color: #606266;
  font-size: 13px;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.review-steps {
  padding: 8px 0;
}

.review-step {
  display: flex;
  gap: 14px;
  position: relative;
  padding-bottom: 16px;
}

.review-step:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 32px;
  width: 2px;
  bottom: 0;
  background: #e4e7ed;
}

.review-step.step-approved:not(:last-child)::before {
  background: #67c23a;
}

.review-step.step-rejected:not(:last-child)::before {
  background: #f56c6c;
}

.step-indicator {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f4f4f5;
  color: #909399;
  z-index: 1;
}

.step-indicator .icon-approved {
  color: #67c23a;
  background: rgba(103, 194, 58, 0.15);
  border-radius: 50%;
}

.step-indicator .icon-rejected {
  color: #f56c6c;
  background: rgba(245, 108, 108, 0.15);
  border-radius: 50%;
}

.step-indicator .icon-current {
  color: #e6a23c;
  background: rgba(230, 162, 60, 0.15);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.step-indicator .icon-waiting {
  color: #c0c4cc;
}

.step-body {
  flex: 1;
  min-width: 0;
  padding-top: 4px;
}

.step-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 2px;
}

.step-name {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.step-reviewer {
  color: #909399;
  font-size: 12px;
}

.step-comment {
  color: #606266;
  font-size: 13px;
  margin-top: 4px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 4px;
}

.step-time {
  color: #b1b3b8;
  font-size: 12px;
  margin-top: 2px;
}

.review-actions {
  margin-top: 12px;
  padding: 14px;
  background: rgba(230, 162, 60, 0.08);
  border-radius: 8px;
  border: 1px dashed rgba(230, 162, 60, 0.4);
}

.review-action-btns {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  justify-content: flex-end;
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
