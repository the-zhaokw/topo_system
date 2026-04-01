<template>
  <div class="test-case-detail">
    <div class="detail-header">
      <div class="header-left">
        <el-button @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2 v-if="testCase">{{ testCase.identifier }} - {{ testCase.title }}</h2>
      </div>
      <div class="header-actions" v-if="testCase">
        <el-button type="success" @click="handleExecute">
          <el-icon><VideoPlay /></el-icon>
          执行
        </el-button>
        <el-button @click="handleCopy">
          <el-icon><CopyDocument /></el-icon>
          复制
        </el-button>
        <el-button type="warning" @click="handleLinkBug" v-if="testCase.status === 'pending_review' || testCase.status === 'reviewed'">
          <el-icon><Link /></el-icon>
          关联缺陷
        </el-button>
        <el-button type="warning" @click="showReviewDialog = true" v-if="testCase.status === 'pending_review'">
          <el-icon><Select /></el-icon>
          提交评审
        </el-button>
        <el-button @click="showHistoryDialog = true">
          <el-icon><Clock /></el-icon>
          版本历史
        </el-button>
        <el-button type="primary" @click="handleEdit">
          <el-icon><Edit /></el-icon>
          编辑
        </el-button>
      </div>
      <div class="header-actions" v-else>
        <el-button type="primary" @click="handleSave">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
      </div>
    </div>

    <div v-if="testCase" class="detail-content">
      <!-- 新建/编辑模式：显示表单 -->
      <el-row v-if="isCreateMode || isEditing" :gutter="20">
        <el-col :span="24">
          <el-card class="edit-card">
            <template #header>
              <span>{{ isCreateMode ? '新建测试用例' : '编辑测试用例' }}</span>
            </template>
            <el-form :model="testCase" label-width="100px" :rules="caseRules">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="标题" prop="title">
                    <el-input v-model="testCase.title" placeholder="请输入用例标题" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="优先级">
                    <el-select v-model="testCase.priority" placeholder="请选择优先级" style="width: 100%;">
                      <el-option label="P0 - 最高" :value="0" />
                      <el-option label="P1 - 高" :value="1" />
                      <el-option label="P2 - 中" :value="2" />
                      <el-option label="P3 - 低" :value="3" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="类型">
                    <el-select v-model="testCase.type" placeholder="请选择类型" style="width: 100%;">
                      <el-option label="功能测试" value="functional" />
                      <el-option label="性能测试" value="performance" />
                      <el-option label="安全测试" value="security" />
                      <el-option label="其他" value="other" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="预计时长">
                    <el-input v-model.number="testCase.estimated_duration" type="number" placeholder="分钟">
                      <template #append>分钟</template>
                    </el-input>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="描述">
                <el-input v-model="testCase.description" type="textarea" :rows="3" placeholder="请输入用例描述" />
              </el-form-item>
              <el-form-item label="前提条件">
                <el-input v-model="testCase.precondition" type="textarea" :rows="2" placeholder="请输入前提条件" />
              </el-form-item>
              <el-form-item label="测试数据">
                <el-input v-model="testCase.test_data" type="textarea" :rows="2" placeholder="请输入测试数据" />
              </el-form-item>
              <el-form-item label="环境要求">
                <el-input v-model="testCase.environment" type="textarea" :rows="2" placeholder="请输入环境要求" />
              </el-form-item>
              <el-form-item label="自动化">
                <el-switch v-model="testCase.is_automated" active-text="是" inactive-text="否" />
              </el-form-item>
              <el-form-item label="脚本路径" v-if="testCase.is_automated">
                <el-input v-model="testCase.automation_script" placeholder="请输入自动化脚本路径" />
              </el-form-item>
            </el-form>
          </el-card>

          <el-card class="steps-card" style="margin-top: 20px;">
            <template #header>
              <div class="steps-header">
                <span>测试步骤</span>
                <el-button type="primary" size="small" @click="addStepToTestCase">
                  <el-icon><Plus /></el-icon>添加步骤
                </el-button>
              </div>
            </template>
            <div v-if="testCase.steps && testCase.steps.length > 0">
              <div v-for="(step, index) in testCase.steps" :key="index" class="step-edit-item">
                <div class="step-number">{{ index + 1 }}</div>
                <div class="step-inputs">
                  <el-input v-model="step.action" type="textarea" :rows="2" placeholder="操作步骤" />
                  <el-input v-model="step.expected_result" type="textarea" :rows="2" placeholder="预期结果" style="margin-top: 8px;" />
                </div>
                <el-button type="danger" link @click="removeStepFromTestCase(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            <el-empty v-else description="暂无测试步骤，请点击上方按钮添加" />
          </el-card>
        </el-col>
      </el-row>

      <!-- 查看模式：显示详情 -->
      <el-row v-else :gutter="20">
        <el-col :span="16">
          <el-card class="main-info">
            <template #header>
              <span>基本信息</span>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="标识符">{{ testCase.identifier }}</el-descriptions-item>
              <el-descriptions-item label="优先级">
                <el-tag v-if="testCase.priority === 0" type="danger" size="small">P0</el-tag>
                <el-tag v-else-if="testCase.priority === 1" type="warning" size="small">P1</el-tag>
                <el-tag v-else-if="testCase.priority === 2" size="small">P2</el-tag>
                <el-tag v-else type="info" size="small">P3</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="类型">
                <el-tag v-if="testCase.type === 'functional'" size="small">功能测试</el-tag>
                <el-tag v-else-if="testCase.type === 'performance'" type="success" size="small">性能测试</el-tag>
                <el-tag v-else-if="testCase.type === 'security'" type="warning" size="small">安全测试</el-tag>
                <el-tag v-else size="small">{{ testCase.type }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag v-if="testCase.status === 'designing'" type="info" size="small">设计</el-tag>
                <el-tag v-else-if="testCase.status === 'pending_review'" type="warning" size="small">待评审</el-tag>
                <el-tag v-else-if="testCase.status === 'reviewed'" type="success" size="small">已评审</el-tag>
                <el-tag v-else-if="testCase.status === 'approved'" type="success" size="small">已批准</el-tag>
                <el-tag v-else-if="testCase.status === 'deprecated'" type="danger" size="small">废弃</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="可自动化">
                <el-tag v-if="testCase.is_automated" type="success" size="small">是</el-tag>
                <el-tag v-else type="info" size="small">否</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="预计时长">{{ testCase.estimated_duration || 0 }}分钟</el-descriptions-item>
              <el-descriptions-item label="设计人">{{ testCase.designer_name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="评审人">{{ testCase.reviewer_name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ formatDate(testCase.created_at) }}</el-descriptions-item>
              <el-descriptions-item label="更新时间">{{ formatDate(testCase.updated_at) }}</el-descriptions-item>
            </el-descriptions>

            <el-divider />

            <div class="description-section">
              <h4>描述</h4>
              <p v-if="testCase.description">{{ testCase.description }}</p>
              <p v-else class="empty-text">暂无描述</p>
            </div>

            <div class="description-section">
              <h4>前提条件</h4>
              <p v-if="testCase.precondition">{{ testCase.precondition }}</p>
              <p v-else class="empty-text">暂无前提条件</p>
            </div>

            <div class="description-section">
              <h4>测试数据</h4>
              <p v-if="testCase.test_data">{{ testCase.test_data }}</p>
              <p v-else class="empty-text">暂无测试数据</p>
            </div>

            <div class="description-section">
              <h4>环境要求</h4>
              <p v-if="testCase.environment">{{ testCase.environment }}</p>
              <p v-else class="empty-text">暂无环境要求</p>
            </div>

            <div v-if="testCase.tags" class="description-section">
              <h4>标签</h4>
              <el-tag v-for="tag in testCase.tags.split(',')" :key="tag" size="small" style="margin-right: 8px;">
                {{ tag.trim() }}
              </el-tag>
            </div>
          </el-card>

          <el-card class="steps-card" style="margin-top: 20px;">
            <template #header>
              <span>测试步骤</span>
            </template>
            <div v-if="testCase.steps && testCase.steps.length > 0">
              <el-table :data="testCase.steps" stripe>
                <el-table-column prop="step_number" label="步骤" width="60" align="center" />
                <el-table-column prop="action" label="操作" min-width="200">
                  <template #default="{ row }">
                    <div class="step-content">{{ row.action || '-' }}</div>
                  </template>
                </el-table-column>
                <el-table-column prop="expected_result" label="预期结果" min-width="200">
                  <template #default="{ row }">
                    <div class="step-content">{{ row.expected_result || '-' }}</div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <el-empty v-else description="暂无测试步骤" />
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="sidebar">
            <template #header>
              <span>关联需求</span>
            </template>
            <div v-if="linkedRequirements.length > 0">
              <div v-for="link in linkedRequirements" :key="link.id" class="requirement-item">
                <span class="req-identifier">{{ link.requirement_identifier }}</span>
                <span class="req-title">{{ link.requirement_title }}</span>
                <el-button type="danger" link size="small" @click="handleUnlinkRequirement(link.id)">解除</el-button>
              </div>
            </div>
            <el-empty v-else description="暂无关联需求" />
            <el-button type="primary" plain size="small" style="margin-top: 12px; width: 100%;" @click="showLinkDialog = true">
              关联需求
            </el-button>
          </el-card>

          <el-card class="sidebar" style="margin-top: 20px;">
            <template #header>
              <div class="execution-header">
                <span>执行历史</span>
                <el-tag v-if="latestExecutionResult" :type="getResultType(latestExecutionResult.result)" size="small" effect="dark">
                  {{ getResultLabel(latestExecutionResult.result) }}
                </el-tag>
              </div>
            </template>
            <div v-if="executionHistory.length > 0">
              <div v-for="result in executionHistory.slice(0, 5)" :key="result.id" class="execution-item" @click="handleViewExecution(result)">
                <div class="execution-info">
                  <el-tag :type="getResultType(result.result)" size="small">{{ getResultLabel(result.result) }}</el-tag>
                  <span class="execution-date">{{ formatDate(result.executed_at) }}</span>
                </div>
                <div class="execution-executor">{{ result.executor_name }}</div>
              </div>
              <el-button v-if="executionHistory.length > 5" type="primary" link size="small" style="margin-top: 8px;" @click="showExecutionHistoryDialog = true">
                查看全部 ({{ executionHistory.length }})
              </el-button>
            </div>
            <el-empty v-else description="暂无执行记录" />
            <el-button type="success" plain size="small" style="margin-top: 12px; width: 100%;" @click="handleExecute">
              <el-icon><VideoPlay /></el-icon>
              立即执行
            </el-button>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-dialog v-model="showEditDialog" title="编辑测试用例" width="800px" @closed="handleEditClosed">
      <el-form :model="caseForm" label-width="100px" :rules="caseRules" ref="caseFormRef">
        <el-form-item label="用例标题" prop="title">
          <el-input v-model="caseForm.title" placeholder="请输入用例标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="caseForm.description" type="textarea" :rows="3" placeholder="请输入用例描述" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-select v-model="caseForm.priority" placeholder="请选择">
                <el-option label="P0 - 最高" :value="0" />
                <el-option label="P1 - 高" :value="1" />
                <el-option label="P2 - 中" :value="2" />
                <el-option label="P3 - 低" :value="3" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="类型">
              <el-select v-model="caseForm.type" placeholder="请选择">
                <el-option label="功能测试" value="functional" />
                <el-option label="性能测试" value="performance" />
                <el-option label="安全测试" value="security" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="caseForm.status" placeholder="请选择">
                <el-option label="设计" value="designing" />
                <el-option label="待评审" value="pending_review" />
                <el-option label="已评审" value="reviewed" />
                <el-option label="已批准" value="approved" />
                <el-option label="废弃" value="deprecated" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="可自动化">
              <el-switch v-model="caseForm.is_automated" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="前提条件">
          <el-input v-model="caseForm.precondition" type="textarea" :rows="2" placeholder="请输入前提条件" />
        </el-form-item>
        <el-form-item label="测试数据">
          <el-input v-model="caseForm.test_data" type="textarea" :rows="2" placeholder="请输入测试数据" />
        </el-form-item>
        <el-form-item label="环境要求">
          <el-input v-model="caseForm.environment" placeholder="请输入环境要求" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="caseForm.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>

        <el-divider>测试步骤</el-divider>

        <div class="steps-container">
          <div v-for="(step, index) in caseForm.steps" :key="index" class="step-item">
            <el-row :gutter="10" align="middle">
              <el-col :span="2">
                <span class="step-number">{{ index + 1 }}</span>
              </el-col>
              <el-col :span="10">
                <el-input v-model="step.action" placeholder="操作步骤" type="textarea" :rows="2" />
              </el-col>
              <el-col :span="10">
                <el-input v-model="step.expected_result" placeholder="预期结果" type="textarea" :rows="2" />
              </el-col>
              <el-col :span="2">
                <el-button type="danger" circle @click="removeStep(index)" :disabled="caseForm.steps.length <= 1">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-col>
            </el-row>
          </div>
          <el-button type="primary" plain @click="addStep" style="margin-top: 10px;">
            <el-icon><Plus /></el-icon>
            添加步骤
          </el-button>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveCase" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showLinkDialog" title="关联需求" width="500px">
      <el-form :model="linkForm" label-width="100px">
        <el-form-item label="需求">
          <el-select v-model="linkForm.requirement_id" placeholder="请选择需求" filterable style="width: 100%;">
            <el-option v-for="req in availableRequirements" :key="req.id" :label="`${req.identifier} - ${req.title}`" :value="req.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLinkDialog = false">取消</el-button>
        <el-button type="primary" @click="handleLinkRequirement" :loading="linking">关联</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showReviewDialog" title="提交评审" width="500px">
      <el-form :model="reviewForm" label-width="100px">
        <el-form-item label="评审结论">
          <el-radio-group v-model="reviewForm.conclusion">
            <el-radio label="approved">通过</el-radio>
            <el-radio label="needs_modification">需要修改</el-radio>
            <el-radio label="rejected">拒绝</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="评审意见">
          <el-input v-model="reviewForm.comment" type="textarea" :rows="4" placeholder="请输入评审意见" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReviewDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitReview" :loading="reviewing">提交评审</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showHistoryDialog" title="版本历史" width="700px">
      <div v-loading="historyLoading">
        <el-timeline v-if="versionHistory.length > 0">
          <el-timeline-item
            v-for="(version, index) in versionHistory"
            :key="version.id"
            :timestamp="version.created_at"
            placement="top"
            :type="index === 0 ? 'primary' : 'info'"
          >
            <el-card>
              <div class="version-header">
                <h4>版本 {{ version.version }}</h4>
                <el-tag size="small" v-if="index === 0">当前版本</el-tag>
              </div>
              <p class="version-info">
                <span>修改人：{{ version.created_by_name }}</span>
                <span v-if="version.change_summary">，变更说明：{{ version.change_summary }}</span>
              </p>
              <div class="version-content" v-if="version.changes && expandedVersions.includes(version.id)">
                <el-divider content-position="left">变更内容</el-divider>
                <div v-if="version.changes.title" class="change-item">
                  <strong>标题：</strong>{{ version.changes.title }}
                </div>
                <div v-if="version.changes.description" class="change-item">
                  <strong>描述：</strong>{{ version.changes.description }}
                </div>
                <div v-if="version.changes.steps" class="change-item">
                  <strong>步骤变更：</strong>修改了 {{ version.changes.steps.added || 0 }} 个步骤，删除了 {{ version.changes.steps.removed || 0 }} 个步骤
                </div>
              </div>
              <div class="version-actions">
                <el-button type="primary" link size="small" @click="handleViewVersion(version)" v-if="version.changes">
                  {{ expandedVersions.includes(version.id) ? '收起详情' : '查看详情' }}
                </el-button>
                <el-button type="warning" link size="small" @click="handleRestoreVersion(version)" v-if="canRestore && index !== 0">
                  恢复到此版本
                </el-button>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无版本历史" />
      </div>
    </el-dialog>

    <el-dialog v-model="showBugLinkDialog" title="关联缺陷" width="500px">
      <el-form :model="bugLinkForm" label-width="100px">
        <el-form-item label="缺陷ID" required>
          <el-input v-model="bugLinkForm.bug_id" placeholder="请输入缺陷ID" />
        </el-form-item>
        <el-form-item label="缺陷标题">
          <el-input v-model="bugLinkForm.bug_title" placeholder="请输入缺陷标题（可选）" />
        </el-form-item>
        <el-form-item label="关联类型">
          <el-select v-model="bugLinkForm.link_type" style="width: 100%;">
            <el-option label="导致失败" value="caused_failure" />
            <el-option label="阻塞执行" value="blocked" />
            <el-option label="相关缺陷" value="related" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="bugLinkForm.remark" type="textarea" :rows="2" placeholder="请输入备注（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBugLinkDialog = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmBugLink" :loading="linkingBug">确认关联</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showExecutionHistoryDialog" title="执行历史" width="800px">
      <el-table :data="executionHistory" stripe style="width: 100%;">
        <el-table-column prop="result" label="结果" width="100">
          <template #default="{ row }">
            <el-tag :type="getResultType(row.result)" size="small">{{ getResultLabel(row.result) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="actual_result" label="实际结果" min-width="150" show-overflow-tooltip />
        <el-table-column prop="executor_name" label="执行人" width="100" />
        <el-table-column prop="executed_at" label="执行时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.executed_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="execution_name" label="所属执行" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleViewExecutionDetail(row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Plus, Delete, Select, Clock, CopyDocument, VideoPlay, Link, Edit, Check } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const router = useRouter()
const route = useRoute()

const suiteId = ref(null)
const projectId = ref(null)
const caseId = ref(null)
const testCase = ref(null)
const linkedRequirements = ref([])
const executionHistory = ref([])
const availableRequirements = ref([])
const showEditDialog = ref(false)
const showLinkDialog = ref(false)
const showReviewDialog = ref(false)
const showHistoryDialog = ref(false)
const showBugLinkDialog = ref(false)
const showExecutionHistoryDialog = ref(false)
const historyLoading = ref(false)
const linkingBug = ref(false)
const expandedVersions = ref([])

const bugLinkForm = reactive({
  bug_id: '',
  bug_title: '',
  link_type: 'caused_failure',
  remark: ''
})

const latestExecutionResult = computed(() => {
  if (!executionHistory.value || executionHistory.value.length === 0) return null
  return executionHistory.value[0]
})
const saving = ref(false)
const linking = ref(false)
const reviewing = ref(false)
const caseFormRef = ref(null)
const versionHistory = ref([])
const canRestore = ref(false)
const isEditing = ref(false)

const reviewForm = reactive({
  conclusion: 'approved',
  comment: ''
})

const caseForm = reactive({
  title: '',
  description: '',
  priority: 2,
  type: 'functional',
  status: 'designing',
  precondition: '',
  test_data: '',
  environment: '',
  is_automated: false,
  tags: '',
  estimated_duration: 0,
  steps: []
})

const linkForm = reactive({
  requirement_id: null
})

const caseRules = {
  title: [{ required: true, message: '请输入用例标题', trigger: 'blur' }]
}

const loadTestCase = async () => {
  try {
    const response = await apiService.tests.getCaseById(caseId.value, { include_steps: true, include_links: true })
    testCase.value = response?.data || response
    linkedRequirements.value = testCase.value?.linked_requirements || []
  } catch (error) {
    console.error('加载用例详情失败:', error)
    ElMessage.error('加载用例详情失败')
  }
}

const loadExecutionHistory = async () => {
  try {
    const response = await apiService.tests.getResultsByCase(caseId.value, { per_page: 10 })
    executionHistory.value = response?.data?.results || []
  } catch (error) {
    console.error('加载执行历史失败:', error)
  }
}

const canGoBack = ref(false)

const handleBack = () => {
  if (canGoBack.value && window.history.length > 1) {
    router.go(-1)
  } else if (projectId.value) {
    router.push(`/projects/${projectId.value}/tests/cases/${suiteId.value}`)
  } else {
    router.push('/projects/list')
  }
}

const handleEdit = () => {
  if (!testCase.value) return
  Object.assign(caseForm, {
    title: testCase.value.title,
    description: testCase.value.description,
    priority: testCase.value.priority,
    type: testCase.value.type,
    status: testCase.value.status,
    precondition: testCase.value.precondition,
    test_data: testCase.value.test_data,
    environment: testCase.value.environment,
    is_automated: testCase.value.is_automated,
    tags: testCase.value.tags,
    estimated_duration: testCase.value.estimated_duration,
    steps: testCase.value.steps?.length > 0
      ? testCase.value.steps.map(s => ({ action: s.action, expected_result: s.expected_result }))
      : [{ action: '', expected_result: '' }]
  })
  showEditDialog.value = true
}

const handleEditClosed = () => {
  caseForm.steps = []
}

const handleSaveCase = async () => {
  if (!caseForm.title) {
    ElMessage.warning('请输入用例标题')
    return
  }

  saving.value = true
  try {
    const data = {
      ...caseForm,
      suite_id: suiteId.value,
      steps: caseForm.steps.filter(s => s.action || s.expected_result)
    }

    if (isCreateMode.value) {
      // 新建用例
      const response = await apiService.tests.createCase(data)
      ElMessage.success('创建成功')
      isEditing.value = false
      // 跳转到新创建的用例详情页
      if (response?.id) {
        router.push(`/projects/${projectId.value}/tests/suites/${suiteId.value}/cases/${response.id}`)
      }
    } else {
      // 更新用例
      await apiService.tests.updateCase(caseId.value, data)
      ElMessage.success('更新成功')
      showEditDialog.value = false
      await loadTestCase()
    }
  } catch (error) {
    ElMessage.error(isCreateMode.value ? '创建失败' : '更新失败')
  } finally {
    saving.value = false
  }
}

// 新建/编辑页面的保存方法
const handleSave = () => {
  // 将 testCase 的数据同步到 caseForm
  Object.assign(caseForm, {
    title: testCase.value.title,
    description: testCase.value.description,
    priority: testCase.value.priority,
    type: testCase.value.type,
    status: testCase.value.status,
    precondition: testCase.value.precondition,
    test_data: testCase.value.test_data,
    environment: testCase.value.environment,
    is_automated: testCase.value.is_automated,
    automation_script: testCase.value.automation_script,
    estimated_duration: testCase.value.estimated_duration,
    steps: testCase.value.steps || []
  })
  handleSaveCase()
}

const addStep = () => {
  caseForm.steps.push({ action: '', expected_result: '' })
}

const removeStep = (index) => {
  caseForm.steps.splice(index, 1)
}

// 新建/编辑模式下操作步骤的方法
const addStepToTestCase = () => {
  if (!testCase.value.steps) {
    testCase.value.steps = []
  }
  testCase.value.steps.push({
    step_number: testCase.value.steps.length + 1,
    action: '',
    expected_result: ''
  })
}

const removeStepFromTestCase = (index) => {
  if (testCase.value.steps) {
    testCase.value.steps.splice(index, 1)
    // 重新编号
    testCase.value.steps.forEach((step, i) => {
      step.step_number = i + 1
    })
  }
}

const handleLinkRequirement = async () => {
  if (!linkForm.requirement_id) {
    ElMessage.warning('请选择需求')
    return
  }

  linking.value = true
  try {
    await apiService.tests.createRequirementLink({
      test_case_id: caseId.value,
      requirement_id: linkForm.requirement_id
    })
    ElMessage.success('关联成功')
    showLinkDialog.value = false
    linkForm.requirement_id = null
    await loadTestCase()
  } catch (error) {
    ElMessage.error('关联失败')
  } finally {
    linking.value = false
  }
}

const handleUnlinkRequirement = async (linkId) => {
  try {
    await apiService.tests.deleteRequirementLink(linkId)
    ElMessage.success('解除关联成功')
    await loadTestCase()
  } catch (error) {
    ElMessage.error('解除关联失败')
  }
}

const handleSubmitReview = async () => {
  reviewing.value = true
  try {
    await apiService.tests.submitCaseReview(caseId.value, {
      conclusion: reviewForm.conclusion,
      comment: reviewForm.comment
    })
    ElMessage.success('评审提交成功')
    showReviewDialog.value = false
    reviewForm.conclusion = 'approved'
    reviewForm.comment = ''
    await loadTestCase()
  } catch (error) {
    ElMessage.error('评审提交失败')
  } finally {
    reviewing.value = false
  }
}

const handleCopy = async () => {
  try {
    const response = await apiService.tests.copyCase(caseId.value, {
      target_suite_id: suiteId.value
    })
    ElMessage.success('用例复制成功')
    if (response?.id) {
      router.push(`/projects/${projectId.value}/tests/cases/${suiteId.value}/${response.id}`)
    }
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const handleExecute = () => {
  router.push(`/projects/${projectId.value}/tests/executions?case_id=${caseId.value}&suite_id=${suiteId.value}`)
}

const handleLinkBug = () => {
  bugLinkForm.bug_id = ''
  bugLinkForm.bug_title = ''
  bugLinkForm.link_type = 'caused_failure'
  bugLinkForm.remark = ''
  showBugLinkDialog.value = true
}

const handleConfirmBugLink = async () => {
  if (!bugLinkForm.bug_id) {
    ElMessage.warning('请输入缺陷ID')
    return
  }
  linkingBug.value = true
  try {
    await apiService.bugs.create({
      title: bugLinkForm.bug_title || `用例 ${testCase.value.identifier} 关联缺陷`,
      case_id: caseId.value,
      link_type: bugLinkForm.link_type,
      remark: bugLinkForm.remark
    })
    ElMessage.success('缺陷关联成功')
    showBugLinkDialog.value = false
  } catch (error) {
    ElMessage.error('关联失败')
  } finally {
    linkingBug.value = false
  }
}

const handleViewExecution = (result) => {
  if (result.execution_id) {
    router.push(`/projects/${projectId.value}/tests/executions?execution_id=${result.execution_id}`)
  }
}

const handleViewExecutionDetail = (result) => {
  if (result.execution_id) {
    router.push(`/projects/${projectId.value}/tests/executions/${result.execution_id}`)
  }
  showExecutionHistoryDialog.value = false
}

const handleViewVersion = (version) => {
  const index = expandedVersions.value.indexOf(version.id)
  if (index === -1) {
    expandedVersions.value.push(version.id)
  } else {
    expandedVersions.value.splice(index, 1)
  }
}

const loadVersionHistory = async () => {
  showHistoryDialog.value = true
  historyLoading.value = true
  try {
    const response = await apiService.tests.getCaseHistory(caseId.value)
    if (response.success) {
      versionHistory.value = response.history || []
      canRestore.value = response.history?.length > 1
    }
  } catch (error) {
    ElMessage.error('加载版本历史失败')
  } finally {
    historyLoading.value = false
  }
}

const handleRestoreVersion = async (version) => {
  try {
    await apiService.tests.restoreCaseVersion(caseId.value, version.id)
    ElMessage.success('版本恢复成功')
    showHistoryDialog.value = false
    await loadTestCase()
  } catch (error) {
    ElMessage.error('版本恢复失败')
  }
}

const getResultType = (result) => {
  switch (result) {
    case 'passed': return 'success'
    case 'failed': return 'danger'
    case 'blocked': return 'warning'
    case 'skipped': return 'info'
    default: return 'info'
  }
}

const getResultLabel = (result) => {
  switch (result) {
    case 'passed': return '通过'
    case 'failed': return '失败'
    case 'blocked': return '阻塞'
    case 'skipped': return '跳过'
    default: return result
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

watch(showHistoryDialog, (newVal) => {
  if (newVal && caseId.value) {
    loadVersionHistory()
  }
})

// 判断是否为新建模式
const isCreateMode = computed(() => {
  return route.params.caseId === 'new' || !route.params.caseId
})

onMounted(async () => {
  canGoBack.value = window.history.length > 1
  projectId.value = route.params.projectId ? parseInt(route.params.projectId) : null
  suiteId.value = parseInt(route.params.suiteId)
  
  if (isCreateMode.value) {
    // 新建模式：初始化空用例数据
    testCase.value = {
      title: '',
      description: '',
      priority: 2,
      type: 'functional',
      status: 'designing',
      precondition: '',
      test_data: '',
      environment: '',
      is_automated: false,
      automation_script: '',
      estimated_duration: 0,
      steps: []
    }
    isEditing.value = true
  } else {
    caseId.value = parseInt(route.params.caseId)
    await loadTestCase()
    await loadExecutionHistory()
  }
})
</script>

<style scoped>
.test-case-detail {
  padding: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
}

.main-info, .sidebar {
  margin-bottom: 0;
}

.description-section {
  margin-bottom: 20px;
}

.description-section h4 {
  margin-bottom: 8px;
  color: #606266;
  font-size: 14px;
}

.description-section p {
  margin: 0;
  color: #303133;
  line-height: 1.6;
}

.empty-text {
  color: #909399;
  font-style: italic;
}

.step-content {
  white-space: pre-wrap;
  word-break: break-word;
}

.requirement-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.req-identifier {
  color: #409EFF;
  font-weight: 500;
  min-width: 80px;
}

.req-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.execution-item {
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.execution-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.execution-date {
  color: #909399;
  font-size: 12px;
}

.execution-executor {
  color: #606266;
  font-size: 12px;
}

.execution-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.execution-item {
  cursor: pointer;
  transition: background-color 0.2s;
  border-radius: 4px;
  padding: 8px;
  margin: -8px;
}

.execution-item:hover {
  background-color: #f5f7fa;
}

.version-content {
  margin-top: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.change-item {
  margin-bottom: 8px;
  color: #606266;
  font-size: 14px;
}

.change-item:last-child {
  margin-bottom: 0;
}

.version-actions {
  margin-top: 8px;
  display: flex;
  gap: 12px;
}

.steps-container {
  max-height: 300px;
  overflow-y: auto;
}

.step-item {
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: #409EFF;
  color: #fff;
  border-radius: 50%;
  font-weight: bold;
}

/* 编辑模式样式 */
.edit-card {
  margin-bottom: 20px;
}

.steps-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step-edit-item {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
}

.step-edit-item .step-number {
  flex-shrink: 0;
}

.step-edit-item .step-inputs {
  flex: 1;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .test-case-detail {
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

  .steps-section,
  .attachments-section,
  .history-section {
    margin-bottom: 16px;
  }

  .el-steps {
    flex-direction: column;
  }

  .el-step {
    width: 100%;
  }

  .attachment-list {
    max-height: 200px;
    overflow-y: auto;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
  }
}

@media screen and (max-width: 480px) {
  .test-case-detail {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .info-label {
    font-size: 11px;
  }

  .info-value {
    font-size: 13px;
  }
}
</style>
