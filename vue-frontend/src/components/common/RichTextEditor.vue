<template>
  <div class="rich-text-editor">
    <div class="advanced-editor">
      <div class="editor-toolbar">
        <div class="toolbar-row">
          <el-space :size="4">
            <!-- 撤销/重做 -->
            <el-tooltip content="撤销" placement="bottom">
              <el-button size="small" @click="execCommand('undo')">
                <el-icon><RefreshLeft /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="重做" placement="bottom">
              <el-button size="small" @click="execCommand('redo')">
                <el-icon><RefreshRight /></el-icon>
              </el-button>
            </el-tooltip>
            <el-divider direction="vertical" />
            
            <!-- 字体 -->
            <el-select v-model="fontFamily" size="small" style="width: 140px" @change="changeFontFamily" placeholder="字体">
              <el-option label="宋体" value="SimSun" />
              <el-option label="微软雅黑" value="Microsoft YaHei" />
              <el-option label="黑体" value="SimHei" />
              <el-option label="楷体" value="KaiTi" />
              <el-option label="仿宋" value="FangSong" />
              <el-option label="Arial" value="Arial" />
              <el-option label="Times New Roman" value="Times New Roman" />
              <el-option label="Courier New" value="Courier New" />
            </el-select>
            
            <!-- 字号 -->
            <el-select v-model="fontSize" size="small" style="width: 80px" @change="changeFontSize" placeholder="字号">
              <el-option label="10" value="1" />
              <el-option label="12" value="2" />
              <el-option label="14" value="3" />
              <el-option label="16" value="4" />
              <el-option label="18" value="5" />
              <el-option label="22" value="6" />
              <el-option label="28" value="7" />
            </el-select>
            
            <el-divider direction="vertical" />
            
            <!-- 加粗/斜体/下划线 -->
            <el-tooltip content="加粗" placement="bottom">
              <el-button size="small" @click="execCommand('bold')" :type="states.bold ? 'primary' : ''">
                <strong>B</strong>
              </el-button>
            </el-tooltip>
            <el-tooltip content="斜体" placement="bottom">
              <el-button size="small" @click="execCommand('italic')" :type="states.italic ? 'primary' : ''">
                <em>I</em>
              </el-button>
            </el-tooltip>
            <el-tooltip content="下划线" placement="bottom">
              <el-button size="small" @click="execCommand('underline')" :type="states.underline ? 'primary' : ''">
                <u>U</u>
              </el-button>
            </el-tooltip>
            <el-tooltip content="删除线" placement="bottom">
              <el-button size="small" @click="execCommand('strikeThrough')">
                <s>S</s>
              </el-button>
            </el-tooltip>
            
            <el-divider direction="vertical" />
            
            <!-- 文字颜色 -->
            <el-popover placement="bottom" :width="200" trigger="click">
              <template #reference>
                <el-button size="small">
                  <el-icon><EditPen /></el-icon>
                </el-button>
              </template>
              <div class="color-picker">
                <div class="color-title">文字颜色</div>
                <el-color-picker v-model="foreColor" size="small" @change="changeForeColor" show-alpha />
                <div class="color-grid">
                  <span
                    v-for="color in colors"
                    :key="color"
                    class="color-swatch"
                    :style="{ backgroundColor: color }"
                    @click="applyColor(color, 'fore')"
                  ></span>
                </div>
              </div>
            </el-popover>
            
            <!-- 背景颜色 -->
            <el-popover placement="bottom" :width="200" trigger="click">
              <template #reference>
                <el-button size="small">
                  <el-icon><MagicStick /></el-icon>
                </el-button>
              </template>
              <div class="color-picker">
                <div class="color-title">背景颜色</div>
                <el-color-picker v-model="backColor" size="small" @change="changeBackColor" show-alpha />
                <div class="color-grid">
                  <span
                    v-for="color in colors"
                    :key="color"
                    class="color-swatch"
                    :style="{ backgroundColor: color }"
                    @click="applyColor(color, 'back')"
                  ></span>
                </div>
              </div>
            </el-popover>
            
            <el-divider direction="vertical" />
            
            <!-- 对齐方式 -->
            <el-tooltip content="左对齐" placement="bottom">
              <el-button size="small" @click="execCommand('justifyLeft')">
                <el-icon><DArrowLeft /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="居中" placement="bottom">
              <el-button size="small" @click="execCommand('justifyCenter')">
                <el-icon><DArrowLeft style="transform: rotate(180deg);" /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="右对齐" placement="bottom">
              <el-button size="small" @click="execCommand('justifyRight')">
                <el-icon><DArrowLeft style="transform: rotate(90deg);" /></el-icon>
              </el-button>
            </el-tooltip>
            
            <el-divider direction="vertical" />
            
            <!-- 列表 -->
            <el-tooltip content="无序列表" placement="bottom">
              <el-button size="small" @click="execCommand('insertUnorderedList')">
                <el-icon><Menu /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="有序列表" placement="bottom">
              <el-button size="small" @click="execCommand('insertOrderedList')">
                <el-icon><Rank /></el-icon>
              </el-button>
            </el-tooltip>
            
            <el-divider direction="vertical" />
            
            <!-- 链接和图片 -->
            <el-tooltip content="插入链接" placement="bottom">
              <el-button size="small" @click="showLinkDialog = true">
                <el-icon><Link /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="插入图片" placement="bottom">
              <el-button size="small" @click="showImageDialog = true">
                <el-icon><Picture /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="上传图片" placement="bottom">
              <el-upload
                ref="imageUploadRef"
                :auto-upload="false"
                :limit="1"
                accept="image/*"
                :on-change="handleImageFileChange"
                :show-file-list="false"
              >
                <el-button size="small">
                  <el-icon><Upload /></el-icon>
                </el-button>
              </el-upload>
            </el-tooltip>
            
            <el-divider direction="vertical" />
            
            <!-- 清除格式 -->
            <el-tooltip content="清除格式" placement="bottom">
              <el-button size="small" @click="execCommand('removeFormat')">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </el-space>
        </div>
      </div>
      <div
        ref="editorRef"
        class="editor-content"
        contenteditable="true"
        :placeholder="placeholder"
        @input="handleAdvancedInput"
        @blur="handleBlur"
        @keydown="handleKeydown"
        @click="updateStates"
        @keyup="updateStates"
        @mouseup="handleMouseUp"
      ></div>
    </div>

    <el-dialog v-model="showLinkDialog" title="插入链接" width="450px">
      <el-form :model="linkForm" label-width="80px">
        <el-form-item label="链接文本">
          <el-input v-model="linkForm.text" placeholder="显示的文本" />
        </el-form-item>
        <el-form-item label="链接地址">
          <el-input v-model="linkForm.url" placeholder="https://" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLinkDialog = false">取消</el-button>
        <el-button type="primary" @click="insertLinkConfirm">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showImageDialog" title="插入图片" width="550px">
      <el-form :model="imageForm" label-width="90px">
        <el-form-item label="图片地址">
          <el-input v-model="imageForm.url" placeholder="https://" />
        </el-form-item>
        <el-form-item label="或者上传">
          <el-upload
            ref="dialogImageUploadRef"
            :auto-upload="false"
            :limit="1"
            accept="image/*"
            :on-change="handleDialogImageChange"
            :show-file-list="false"
          >
            <el-button>选择图片</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="图片宽度">
          <el-input-number v-model="imageForm.width" :min="50" :max="1200" :step="50" placeholder="自动" style="width: 150px;" />
          <span style="margin-left: 10px; color: #909399; font-size: 12px;">像素（px），留空则自动</span>
        </el-form-item>
        <el-form-item label="预览">
          <div v-if="imageForm.url" class="image-preview">
            <img :src="imageForm.url" :style="{ width: imageForm.width ? imageForm.width + 'px' : '100%', maxWidth: '100%' }" />
          </div>
          <div v-else class="no-preview">暂无预览</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showImageDialog = false">取消</el-button>
        <el-button type="primary" @click="insertImageConfirm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  RefreshLeft, RefreshRight, EditPen, MagicStick, DArrowLeft, 
  Menu, Rank, Link, Picture, Upload, Delete
} from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '请输入内容...'
  },
  rows: {
    type: Number,
    default: 6
  }
})

const emit = defineEmits(['update:modelValue', 'change', 'blur'])

const editorRef = ref(null)
const imageUploadRef = ref(null)
const dialogImageUploadRef = ref(null)
const showLinkDialog = ref(false)
const showImageDialog = ref(false)

const fontFamily = ref('')
const fontSize = ref('')
const foreColor = ref('#000000')
const backColor = ref('#ffffff')

const colors = [
  '#000000', '#434343', '#666666', '#999999', '#C0C0C0',
  '#FF0000', '#FF9900', '#FFFF00', '#00FF00', '#00FFFF',
  '#0000FF', '#FF00FF', '#FFFFFF', '#F4CCCC', '#FCE5CD', '#FFF2CC',
  '#D9EAD3', '#D0DFE3', '#CFE2F3', '#E4D7F5', '#FAD1D2',
  '#990000', '#B45F06', '#BF9000', '#6AA84F', '#0B5394',
  '#351C75', '#741B47', '#CC0000', '#E69138', '#F1C232',
  '#93C47D', '#6FA8DC', '#9FC5E8', '#B4A7D6', '#F6B26B',
  '#740000', '#806402', '#8F7F00', '#38761D', '#124F5C',
  '#20124D', '#4C1130', '#850000', '#853803', '#7E6E00',
  '#274E13', '#0C343D', '#1C4587', '#350F47', '#430000'
]

const states = ref({
  bold: false,
  italic: false,
  underline: false
})

const linkForm = ref({
  text: '',
  url: ''
})

const imageForm = ref({
  url: '',
  width: null
})

watch(() => props.modelValue, (newVal) => {
  if (editorRef.value && editorRef.value.innerHTML !== newVal) {
    editorRef.value.innerHTML = newVal || ''
  }
})

const handleAdvancedInput = () => {
  if (editorRef.value) {
    const html = editorRef.value.innerHTML
    emit('update:modelValue', html)
    emit('change', html)
  }
}

const handleBlur = () => {
  emit('blur', props.modelValue)
}

const execCommand = (command, value = null) => {
  document.execCommand(command, false, value)
  editorRef.value?.focus()
  updateStates()
}

const updateStates = () => {
  states.value.bold = document.queryCommandState('bold')
  states.value.italic = document.queryCommandState('italic')
  states.value.underline = document.queryCommandState('underline')
}

const changeFontFamily = (font) => {
  if (font) {
    execCommand('fontName', font)
  }
}

const changeFontSize = (size) => {
  if (size) {
    execCommand('fontSize', size)
  }
}

const changeForeColor = (color) => {
  execCommand('foreColor', color)
}

const changeBackColor = (color) => {
  execCommand('hiliteColor', color)
}

const applyColor = (color, type) => {
  if (type === 'fore') {
    execCommand('foreColor', color)
    foreColor.value = color
  } else {
    execCommand('hiliteColor', color)
    backColor.value = color
  }
}

const showLinkDialogMethod = () => {
  const selection = window.getSelection()
  if (selection.rangeCount > 0) {
    linkForm.value.text = selection.toString()
  }
  showLinkDialog.value = true
}

const insertLinkConfirm = () => {
  if (!linkForm.value.url) {
    ElMessage.warning('请输入链接地址')
    return
  }
  const linkHtml = `<a href="${linkForm.value.url}" target="_blank" style="color: #409EFF; text-decoration: underline;">${linkForm.value.text || linkForm.value.url}</a>`
  execCommand('insertHTML', linkHtml)
  showLinkDialog.value = false
  linkForm.value = { text: '', url: '' }
}

const handleImageFileChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const imgHtml = `<img src="${e.target.result}" style="max-width: 100%; height: auto;" />`
    execCommand('insertHTML', imgHtml)
  }
  reader.readAsDataURL(file.raw)
}

const handleDialogImageChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    imageForm.value.url = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

const insertImageConfirm = () => {
  if (!imageForm.value.url) {
    ElMessage.warning('请输入图片地址或上传图片')
    return
  }
  let imgHtml
  if (imageForm.value.width) {
    imgHtml = `<img src="${imageForm.value.url}" style="width: ${imageForm.value.width}px; height: auto; max-width: 100%;" />`
  } else {
    imgHtml = `<img src="${imageForm.value.url}" style="max-width: 100%; height: auto;" />`
  }
  execCommand('insertHTML', imgHtml)
  showImageDialog.value = false
  imageForm.value = { url: '', width: null }
}

const handleKeydown = (e) => {
  if (e.key === 'Tab') {
    e.preventDefault()
    execCommand('insertHTML', '&nbsp;&nbsp;&nbsp;&nbsp;')
  }
}

const handleMouseUp = (e) => {
  if (e.target.tagName === 'IMG') {
    showImageResizeDialog(e.target)
  }
}

const showImageResizeDialog = (img) => {
  const currentWidth = img.width
  imageForm.value.url = img.src
  imageForm.value.width = currentWidth
  
  ElMessageBox.confirm({
    title: '调整图片大小',
    message: `
      <div style="display: flex; flex-direction: column; gap: 12px;">
        <div>
          <label style="display: block; margin-bottom: 8px;">图片宽度（px）：</label>
          <el-input-number 
            id="resize-width-input" 
            value="${currentWidth}" 
            :min="50" 
            :max="1200" 
            :step="50"
            style="width: 100%;"
          />
        </div>
        <div>
          <img src="${img.src}" style="max-width: 100%; height: auto; border: 1px solid #dcdfe6; border-radius: 4px;" />
        </div>
      </div>
    `,
    dangerouslyUseHTMLString: true,
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    beforeClose: async (action, instance, done) => {
      if (action === 'confirm') {
        const widthInput = document.getElementById('resize-width-input')
        if (widthInput) {
          const newWidth = parseInt(widthInput.value)
          if (newWidth && newWidth >= 50 && newWidth <= 1200) {
            img.style.width = `${newWidth}px`
            img.style.height = 'auto'
            img.style.maxWidth = '100%'
            handleAdvancedInput()
            ElMessage.success('图片大小已调整')
            done()
          } else {
            ElMessage.warning('请输入有效的宽度值（50-1200px）')
          }
        }
      } else {
        done()
      }
    }
  }).catch(() => {
    // 取消操作
  })
  
  setTimeout(() => {
    const widthInput = document.getElementById('resize-width-input')
    if (widthInput) {
      widthInput.focus()
    }
  }, 100)
}

onMounted(() => {
  if (editorRef.value) {
    editorRef.value.innerHTML = props.modelValue || ''
  }
})
</script>

<style scoped>
.rich-text-editor {
  width: 100%;
}

.advanced-editor {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.editor-toolbar {
  padding: 8px;
  background: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
}

.toolbar-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.editor-content {
  min-height: 300px;
  padding: 12px;
  outline: none;
  background: #fff;
  font-size: 14px;
  line-height: 1.6;
}

.editor-content:empty:before {
  content: attr(placeholder);
  color: #c0c4cc;
  pointer-events: none;
}

.editor-content:focus {
  outline: none;
}

.editor-content a {
  color: #409EFF;
  text-decoration: underline;
}

.editor-content img {
  max-width: 100%;
  height: auto;
  margin: 8px 0;
  cursor: pointer;
  transition: opacity 0.2s;
}

.editor-content img:hover {
  opacity: 0.8;
}

.color-picker {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.color-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  text-align: center;
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 4px;
}

.color-swatch {
  width: 20px;
  height: 20px;
  border-radius: 3px;
  cursor: pointer;
  border: 1px solid #dcdfe6;
  transition: transform 0.2s;
}

.color-swatch:hover {
  transform: scale(1.1);
  border-color: #409EFF;
}

.image-preview {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  text-align: center;
}

.image-preview img {
  max-width: 100%;
  height: auto;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.no-preview {
  color: #c0c4cc;
  text-align: center;
  padding: 20px;
}

:deep(.el-button) {
  padding: 6px 8px;
}

:deep(.el-select) {
  --el-select-size: 28px;
}
</style>