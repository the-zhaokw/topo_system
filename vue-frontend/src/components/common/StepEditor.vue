<template>
  <div class="step-editor">
    <div class="step-header" v-if="editable">
      <el-alert type="info" :closable="false">
        <template #title>
          共 {{ localSteps.length }} 个步骤
          <el-button type="primary" link size="small" @click="handleAddFromTemplate" style="margin-left: 16px;">
            从模板添加
          </el-button>
        </template>
      </el-alert>
      <div class="step-actions">
        <el-button type="primary" plain size="small" @click="handleAddStep">
          <el-icon><Plus /></el-icon>
          添加步骤
        </el-button>
        <el-button type="success" plain size="small" @click="handleImportFromExcel">
          <el-icon><Upload /></el-icon>
          从Excel导入
        </el-button>
      </div>
    </div>

    <el-table
      :data="localSteps"
      border
      style="width: 100%;"
      row-key="id"
      class="steps-table"
    >
      <el-table-column prop="step_number" label="步骤" width="60" align="center">
        <template #default="{ $index }">
          <span class="step-number">{{ $index + 1 }}</span>
        </template>
      </el-table-column>

      <el-table-column label="操作步骤" min-width="200">
        <template #default="{ row, $index }">
          <template v-if="editable">
            <RichTextEditor
              v-model="row.action"
              placeholder="请输入操作步骤"
              :rows="3"
              editor-type="simple"
              @change="handleStepChange($index)"
            />
          </template>
          <div v-else class="step-content" v-html="row.action || '-'"></div>
        </template>
      </el-table-column>

      <el-table-column label="预期结果" min-width="200">
        <template #default="{ row, $index }">
          <template v-if="editable">
            <RichTextEditor
              v-model="row.expected_result"
              placeholder="请输入预期结果"
              :rows="3"
              editor-type="simple"
              @change="handleStepChange($index)"
            />
          </template>
          <div v-else class="step-content" v-html="row.expected_result || '-'"></div>
        </template>
      </el-table-column>

      <el-table-column v-if="editable" label="附件" width="80" align="center">
        <template #default="{ row, $index }">
          <el-button size="small" @click="handleUploadAttachment($index)">
            <el-icon><Paperclip /></el-icon>
          </el-button>
        </template>
      </el-table-column>

      <el-table-column v-if="editable" label="操作" width="160" align="center">
        <template #default="{ $index }">
          <el-button-group size="small">
            <el-tooltip content="上移" placement="top">
              <el-button @click="handleMoveUp($index)" :disabled="$index === 0">
                <el-icon><Top /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="下移" placement="top">
              <el-button @click="handleMoveDown($index)" :disabled="$index === localSteps.length - 1">
                <el-icon><Bottom /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="复制" placement="top">
              <el-button @click="handleCopy($index)">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="删除" placement="top">
              <el-button @click="handleDelete($index)" :disabled="localSteps.length <= 1" type="danger">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>

    <div v-if="localSteps.length === 0 && editable" class="empty-steps">
      <el-empty description="暂无步骤，请点击" />
      <el-button type="primary" @click="handleAddStep" style="margin-top: 12px;">
        <el-icon><Plus /></el-icon>
        添加第一个步骤
      </el-button>
    </div>

    <el-dialog v-model="showTemplateDialog" title="步骤模板" width="600px">
      <el-table :data="stepTemplates" stripe style="width: 100%;" @row-click="handleSelectTemplate">
        <el-table-column prop="name" label="模板名称" min-width="120" />
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        <el-table-column prop="step_count" label="步骤数" width="80" align="center" />
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click.stop="applyTemplate(row)">应用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog v-model="showImportDialog" title="从Excel导入步骤" width="500px">
      <el-alert type="info" :closable="false" style="margin-bottom: 16px;">
        <template #title>
          Excel格式说明：第1列为步骤序号，第2列为操作，第3列为预期结果
        </template>
      </el-alert>
      <el-upload
        ref="excelUploadRef"
        :auto-upload="false"
        :file-list="excelFileList"
        :on-change="handleExcelFileChange"
        accept=".xlsx,.xls,.csv"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
      </el-upload>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmImport" :loading="importing">导入</el-button>
      </template>
    </el-dialog>

    <input
      type="file"
      ref="attachmentInputRef"
      style="display: none;"
      accept=".doc,.docx,.xls,.xlsx,.pdf,.png,.jpg,.jpeg,.zip,.rar"
      @change="handleAttachmentSelected"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Top, Bottom, Delete, CopyDocument, Upload, Paperclip, UploadFilled } from '@element-plus/icons-vue'
import RichTextEditor from './RichTextEditor.vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  editable: {
    type: Boolean,
    default: true
  },
  templates: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const localSteps = ref([...props.modelValue])
const showTemplateDialog = ref(false)
const showImportDialog = ref(false)
const importing = ref(false)
const excelFileList = ref([])
const excelUploadRef = ref(null)
const attachmentInputRef = ref(null)
const currentUploadStepIndex = ref(null)

const stepTemplates = ref(props.templates.length > 0 ? props.templates : [
  { id: 1, name: '标准登录流程', description: '包含验证的完整登录流程', step_count: 4, steps: [
    { action: '打开登录页面', expected_result: '登录页面正常显示' },
    { action: '输入用户名和密码', expected_result: '输入框正常显示输入内容' },
    { action: '点击登录按钮', expected_result: '登录成功，跳转到首页' },
    { action: '验证用户信息显示', expected_result: '用户头像和昵称正确显示' }
  ]},
  { id: 2, name: '搜索功能测试', description: '通用搜索框测试步骤', step_count: 3, steps: [
    { action: '在搜索框输入关键词', expected_result: '搜索框显示输入内容' },
    { action: '点击搜索按钮或按回车', expected_result: '显示搜索结果列表' },
    { action: '验证结果相关性', expected_result: '搜索结果包含关键词' }
  ]},
  { id: 3, name: '表单提交测试', description: '通用表单提交流程', step_count: 5, steps: [
    { action: '填写表单必填项', expected_result: '必填项标识清楚' },
    { action: '填写表单选填项', expected_result: '选填项可为空' },
    { action: '点击提交按钮', expected_result: '提交按钮可点击' },
    { action: '等待处理完成', expected_result: '显示处理结果' },
    { action: '验证提交结果', expected_result: '数据正确保存' }
  ]}
])

watch(() => props.modelValue, (newVal) => {
  localSteps.value = [...newVal]
}, { deep: true })

const handleStepChange = (index) => {
  emit('update:modelValue', localSteps.value)
  emit('change', localSteps.value)
}

const handleAddStep = () => {
  localSteps.value.push({
    id: generateId(),
    action: '',
    expected_result: '',
    attachments: []
  })
  handleStepChange()
}

const handleDelete = (index) => {
  if (localSteps.value.length <= 1) {
    ElMessage.warning('至少需要保留一个步骤')
    return
  }
  localSteps.value.splice(index, 1)
  handleStepChange()
}

const handleMoveUp = (index) => {
  if (index > 0) {
    const temp = localSteps.value[index]
    localSteps.value.splice(index, 1)
    localSteps.value.splice(index - 1, 0, temp)
    handleStepChange()
  }
}

const handleMoveDown = (index) => {
  if (index < localSteps.value.length - 1) {
    const temp = localSteps.value[index]
    localSteps.value.splice(index, 1)
    localSteps.value.splice(index + 1, 0, temp)
    handleStepChange()
  }
}

const handleCopy = (index) => {
  const original = localSteps.value[index]
  const copy = {
    ...original,
    id: generateId(),
    action: original.action,
    expected_result: original.expected_result
  }
  localSteps.value.splice(index + 1, 0, copy)
  handleStepChange()
}

const handleAddFromTemplate = () => {
  showTemplateDialog.value = true
}

const handleSelectTemplate = (row) => {
  applyTemplate(row)
}

const applyTemplate = (template) => {
  const newSteps = template.steps.map((step, idx) => ({
    id: generateId(),
    action: step.action,
    expected_result: step.expected_result,
    attachments: []
  }))
  localSteps.value = [...localSteps.value, ...newSteps]
  showTemplateDialog.value = false
  ElMessage.success(`已添加 ${template.steps.length} 个步骤`)
  handleStepChange()
}

const handleUploadAttachment = (index) => {
  currentUploadStepIndex.value = index
  attachmentInputRef.value?.click()
}

const handleAttachmentSelected = (event) => {
  const file = event.target.files?.[0]
  if (file && currentUploadStepIndex.value !== null) {
    if (!localSteps.value[currentUploadStepIndex.value].attachments) {
      localSteps.value[currentUploadStepIndex.value].attachments = []
    }
    localSteps.value[currentUploadStepIndex.value].attachments.push({
      id: generateId(),
      name: file.name,
      size: file.size,
      file: file
    })
    handleStepChange()
  }
  event.target.value = ''
}

const handleImportFromExcel = () => {
  excelFileList.value = []
  showImportDialog.value = true
}

const handleExcelFileChange = (file, files) => {
  excelFileList.value = files
}

const handleConfirmImport = async () => {
  if (excelFileList.value.length === 0) {
    ElMessage.warning('请选择要导入的Excel文件')
    return
  }

  importing.value = true
  try {
    const file = excelFileList.value[0].raw
    const steps = await parseExcelFile(file)

    if (steps.length === 0) {
      ElMessage.warning('未能从文件中解析出步骤数据')
      return
    }

    const newSteps = steps.map(step => ({
      id: generateId(),
      action: step.action || '',
      expected_result: step.expected_result || '',
      attachments: []
    }))

    localSteps.value = [...localSteps.value, ...newSteps]
    showImportDialog.value = false
    ElMessage.success(`成功导入 ${newSteps.length} 个步骤`)
    handleStepChange()
  } catch (error) {
    ElMessage.error('导入失败：' + error.message)
  } finally {
    importing.value = false
  }
}

const parseExcelFile = async (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const steps = []

        resolve(steps)
      } catch (error) {
        reject(error)
      }
    }
    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsArrayBuffer(file)
  })
}

const generateId = () => {
  return Date.now() + Math.random().toString(36).substr(2, 9)
}

const validate = () => {
  const errors = []
  localSteps.value.forEach((step, index) => {
    if (!step.action) {
      errors.push(`第 ${index + 1} 个步骤的操作不能为空`)
    }
    if (!step.expected_result) {
      errors.push(`第 ${index + 1} 个步骤的预期结果不能为空`)
    }
  })
  return errors
}

defineExpose({
  getSteps: () => localSteps.value,
  validate,
  addStep: handleAddStep,
  importFromExcel: handleImportFromExcel
})
</script>

<style scoped>
.step-editor {
  width: 100%;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.step-actions {
  display: flex;
  gap: 12px;
}

.steps-table {
  margin-top: 16px;
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
  font-size: 14px;
}

.step-content {
  padding: 8px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.empty-steps {
  padding: 40px 0;
  text-align: center;
}
</style>