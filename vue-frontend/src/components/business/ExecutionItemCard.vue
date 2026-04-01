<template>
  <div class="execution-item-card" :class="{ 'is-completed': currentResult }">
    <div class="card-header">
      <div class="case-info">
        <span class="case-identifier">{{ testCase.identifier }}</span>
        <el-tag v-if="testCase.priority === 0" type="danger" size="small">P0</el-tag>
        <el-tag v-else-if="testCase.priority === 1" type="warning" size="small">P1</el-tag>
        <el-tag v-else size="small">P2</el-tag>
      </div>
      <TestCaseResultBadge
        v-if="currentResult"
        :case-id="testCase.id"
        :result="currentResult"
        :last-executed-at="executedAt"
        size="small"
      />
    </div>

    <div class="card-body">
      <h4 class="case-title">{{ testCase.title }}</h4>
      <div v-if="showSteps && testCase.steps?.length > 0" class="steps-preview">
        <div class="steps-label">步骤预览：</div>
        <div class="steps-list">
          <div v-for="(step, index) in previewSteps" :key="index" class="step-item">
            <span class="step-num">{{ index + 1 }}.</span>
            <span class="step-action">{{ step.action }}</span>
          </div>
          <div v-if="testCase.steps.length > 3" class="steps-more">
            ... 共 {{ testCase.steps.length }} 个步骤
          </div>
        </div>
      </div>
    </div>

    <div class="card-footer">
      <div class="result-selector">
        <span class="selector-label">执行结果：</span>
        <el-radio-group v-model="selectedResult" size="small" @change="handleResultChange">
          <el-radio-button label="passed">通过</el-radio-button>
          <el-radio-button label="failed">失败</el-radio-button>
          <el-radio-button label="blocked">阻塞</el-radio-button>
          <el-radio-button label="skipped">跳过</el-radio-button>
        </el-radio-group>
      </div>

      <div v-if="selectedResult === 'failed'" class="failure-form">
        <el-input
          v-model="actualResult"
          type="textarea"
          :rows="2"
          placeholder="请输入实际结果"
          @change="handleActualResultChange"
        />
        <el-button type="primary" size="small" @click="showDefectDialog = true" style="margin-top: 8px;">
          关联缺陷
        </el-button>
      </div>

      <div class="action-buttons">
        <el-button type="primary" size="small" @click="handleSubmit" :disabled="!selectedResult">
          提交
        </el-button>
        <el-button size="small" @click="handleViewDetails">
          查看详情
        </el-button>
      </div>
    </div>

    <el-dialog v-model="showDefectDialog" title="关联缺陷" width="500px">
      <el-form :model="defectForm" label-width="80px">
        <el-form-item label="缺陷标识">
          <el-input v-model="defectForm.defect_id" placeholder="请输入缺陷标识" />
        </el-form-item>
        <el-form-item label="缺陷标题">
          <el-input v-model="defectForm.title" placeholder="请输入缺陷标题" />
        </el-form-item>
        <el-form-item label="严重程度">
          <el-select v-model="defectForm.severity" placeholder="请选择">
            <el-option label="致命" value="fatal" />
            <el-option label="严重" value="serious" />
            <el-option label="一般" value="normal" />
            <el-option label="轻微" value="minor" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDefectDialog = false">取消</el-button>
        <el-button type="primary" @click="handleLinkDefect">关联</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import TestCaseResultBadge from '@/components/common/TestCaseResultBadge.vue'

const props = defineProps({
  testCase: {
    type: Object,
    required: true
  },
  executionId: {
    type: [Number, String],
    required: true
  },
  initialResult: {
    type: String,
    default: null
  },
  initialActualResult: {
    type: String,
    default: ''
  },
  showSteps: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['result-change', 'submit', 'view-details', 'link-defect'])

const selectedResult = ref(props.initialResult)
const actualResult = ref(props.initialActualResult)
const showDefectDialog = ref(false)
const defectForm = ref({
  defect_id: '',
  title: '',
  severity: 'normal'
})

const currentResult = computed(() => props.initialResult)
const executedAt = computed(() => null)

const previewSteps = computed(() => {
  if (!props.testCase.steps) return []
  return props.testCase.steps.slice(0, 3)
})

watch(() => props.initialResult, (newVal) => {
  selectedResult.value = newVal
})

watch(() => props.initialActualResult, (newVal) => {
  actualResult.value = newVal
})

const handleResultChange = (value) => {
  emit('result-change', {
    caseId: props.testCase.id,
    result: value,
    actualResult: actualResult.value
  })
}

const handleActualResultChange = () => {
  emit('result-change', {
    caseId: props.testCase.id,
    result: selectedResult.value,
    actualResult: actualResult.value
  })
}

const handleSubmit = () => {
  if (!selectedResult.value) {
    ElMessage.warning('请选择执行结果')
    return
  }
  emit('submit', {
    caseId: props.testCase.id,
    result: selectedResult.value,
    actualResult: actualResult.value,
    defectId: defectForm.value.defect_id
  })
}

const handleViewDetails = () => {
  emit('view-details', props.testCase)
}

const handleLinkDefect = () => {
  emit('link-defect', {
    caseId: props.testCase.id,
    defect: defectForm.value
  })
  showDefectDialog.value = false
  ElMessage.success('缺陷关联成功')
}
</script>

<style scoped>
.execution-item-card {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 16px;
  margin-bottom: 12px;
  background: #fff;
  transition: all 0.3s;
}

.execution-item-card.is-completed {
  border-left: 4px solid #67C23A;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.case-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.case-identifier {
  font-weight: bold;
  color: #409EFF;
}

.case-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #303133;
}

.steps-preview {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 12px;
}

.steps-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.steps-list {
  font-size: 13px;
}

.step-item {
  display: flex;
  gap: 8px;
  padding: 4px 0;
}

.step-num {
  color: #409EFF;
  font-weight: bold;
}

.step-action {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.steps-more {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.card-footer {
  border-top: 1px solid #ebeef5;
  padding-top: 12px;
}

.result-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.selector-label {
  font-size: 14px;
  color: #606266;
}

.failure-form {
  background: #fef0f0;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 12px;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>