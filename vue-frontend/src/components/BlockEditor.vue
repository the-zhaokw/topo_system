<template>
  <div class="block-editor">
    <!-- 工具栏 -->
    <div class="editor-toolbar">
      <el-button-group>
        <el-button size="small" @click="addBlock('text')">
          <el-icon><Document /></el-icon>
        </el-button>
        <el-button size="small" @click="addBlock('heading')">
          <el-icon><Edit /></el-icon>
        </el-button>
        <el-button size="small" @click="addBlock('code')">
          <el-icon><Cpu /></el-icon>
        </el-button>
        <el-button size="small" @click="addBlock('image')">
          <el-icon><Picture /></el-icon>
        </el-button>
        <el-button size="small" @click="addBlock('table')">
          <el-icon><Grid /></el-icon>
        </el-button>
        <el-button size="small" @click="addBlock('quote')">
          <el-icon><ChatLineSquare /></el-icon>
        </el-button>
        <el-button size="small" @click="addBlock('divider')">
          <el-icon><Minus /></el-icon>
        </el-button>
      </el-button-group>
      
      <el-divider direction="vertical" />
      
      <el-button-group>
        <el-button size="small" @click="formatText('bold')">
          <el-icon><EditPen /></el-icon>
        </el-button>
        <el-button size="small" @click="formatText('italic')">
          <el-icon><ChatLineSquare /></el-icon>
        </el-button>
        <el-button size="small" @click="formatText('strike')">
          <el-icon><Delete /></el-icon>
        </el-button>
      </el-button-group>

      <el-divider direction="vertical" />

      <el-button-group>
        <el-button size="small" @click="undo" :disabled="!canUndo">
          <el-icon><RefreshLeft /></el-icon>
        </el-button>
        <el-button size="small" @click="redo" :disabled="!canRedo">
          <el-icon><RefreshRight /></el-icon>
        </el-button>
      </el-button-group>

      <el-divider direction="vertical" />

      <el-button size="small" @click="insertLink">
        <el-icon><Link /></el-icon> 链接
      </el-button>
      
      <el-button size="small" @click="showImageUpload = true">
        <el-icon><Upload /></el-icon> 上传图片
      </el-button>
    </div>
    
    <!-- 编辑器内容区 -->
    <div class="editor-content" ref="editorContent">
      <div
        v-for="(block, index) in blocks"
        :key="block.id"
        class="editor-block"
        :class="{ 'is-active': activeBlockIndex === index }"
        @click="setActiveBlock(index)"
      >
        <!-- 拖拽手柄 -->
        <div class="block-handle">
          <el-icon><Rank /></el-icon>
        </div>
        
        <!-- 块类型图标 -->
        <div class="block-type-icon">
          <el-icon v-if="block.type === 'text'"><Document /></el-icon>
          <el-icon v-else-if="block.type === 'heading'"><Edit /></el-icon>
          <el-icon v-else-if="block.type === 'code'"><Cpu /></el-icon>
          <el-icon v-else-if="block.type === 'image'"><Picture /></el-icon>
          <el-icon v-else-if="block.type === 'table'"><Grid /></el-icon>
          <el-icon v-else-if="block.type === 'quote'"><ChatLineSquare /></el-icon>
        </div>
        
        <!-- 文本块 -->
        <div v-if="block.type === 'text'" class="block-text">
          <el-input
            v-model="block.content"
            type="textarea"
            :rows="3"
            placeholder="输入文本..."
            @focus="setActiveBlock(index)"
          />
        </div>
        
        <!-- 标题块 -->
        <div v-else-if="block.type === 'heading'" class="block-heading">
          <el-select v-model="block.level" size="small" style="width: 80px">
            <el-option label="H1" :value="1" />
            <el-option label="H2" :value="2" />
            <el-option label="H3" :value="3" />
            <el-option label="H4" :value="4" />
          </el-select>
          <el-input
            v-model="block.content"
            placeholder="标题"
            @focus="setActiveBlock(index)"
          />
        </div>
        
        <!-- 代码块 -->
        <div v-else-if="block.type === 'code'" class="block-code">
          <el-select v-model="block.language" size="small" style="width: 120px">
            <el-option label="JavaScript" value="javascript" />
            <el-option label="Python" value="python" />
            <el-option label="Java" value="java" />
            <el-option label="SQL" value="sql" />
            <el-option label="HTML" value="html" />
            <el-option label="CSS" value="css" />
            <el-option label="JSON" value="json" />
            <el-option label="Markdown" value="markdown" />
            <el-option label="Plain Text" value="text" />
          </el-select>
          <el-input
            v-model="block.content"
            type="textarea"
            :rows="6"
            placeholder="输入代码..."
            @focus="setActiveBlock(index)"
          />
        </div>
        
        <!-- 图片块 -->
        <div v-else-if="block.type === 'image'" class="block-image">
          <img v-if="block.url" :src="block.url" :alt="block.alt" />
          <div v-else class="image-placeholder">
            <el-icon><Picture /></el-icon>
            <span>点击上传图片</span>
          </div>
          <el-input v-model="block.alt" placeholder="图片描述" size="small" />
        </div>
        
        <!-- 表格块 -->
        <div v-else-if="block.type === 'table'" class="block-table">
          <el-table :data="block.data" border size="small">
            <el-table-column
              v-for="(col, colIndex) in block.columns"
              :key="colIndex"
              :prop="col.prop"
              :label="col.label"
            />
          </el-table>
          <el-button size="small" @click="addTableRow(index)">添加行</el-button>
          <el-button size="small" @click="addTableColumn(index)">添加列</el-button>
        </div>
        
        <!-- 引用块 -->
        <div v-else-if="block.type === 'quote'" class="block-quote">
          <el-input
            v-model="block.content"
            type="textarea"
            :rows="3"
            placeholder="引用内容..."
            @focus="setActiveBlock(index)"
          />
          <el-input
            v-model="block.source"
            placeholder="引用来源"
            size="small"
          />
        </div>
        
        <!-- 分隔线 -->
        <div v-else-if="block.type === 'divider'" class="block-divider">
          <el-divider />
        </div>
        
        <!-- 块操作菜单 -->
        <div class="block-actions">
          <el-dropdown trigger="click">
            <el-button size="small" circle>
              <el-icon><More /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="moveBlock(index, -1)">
                  <el-icon><ArrowUp /></el-icon> 上移
                </el-dropdown-item>
                <el-dropdown-item @click="moveBlock(index, 1)">
                  <el-icon><ArrowDown /></el-icon> 下移
                </el-dropdown-item>
                <el-dropdown-item @click="duplicateBlock(index)">
                  <el-icon><CopyDocument /></el-icon> 复制
                </el-dropdown-item>
                <el-dropdown-item divided @click="deleteBlock(index)">
                  <el-icon><Delete /></el-icon> 删除
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>
    
    <!-- 图片上传对话框 -->
    <el-dialog v-model="showImageUpload" title="上传图片" width="500px">
      <el-upload
        drag
        action="/api/knowledge/enhanced/upload/image"
        :on-success="handleImageUploadSuccess"
        :on-error="handleImageUploadError"
        accept="image/*"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽图片到此处或 <em>点击上传</em>
        </div>
      </el-upload>
    </el-dialog>
    
    <!-- 链接插入对话框 -->
    <el-dialog v-model="showLinkDialog" title="插入链接" width="400px">
      <el-form :model="linkForm">
        <el-form-item label="链接文本">
          <el-input v-model="linkForm.text" />
        </el-form-item>
        <el-form-item label="链接地址">
          <el-input v-model="linkForm.url" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLinkDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmInsertLink">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document, Edit, Cpu, Picture, Grid, ChatLineSquare, Minus,
  EditPen, RefreshLeft, RefreshRight, Link,
  Upload, Rank, ArrowUp, ArrowDown, More, CopyDocument,
  UploadFilled
} from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

// 块数据
const blocks = ref([
  { id: 1, type: 'text', content: '' }
])

const activeBlockIndex = ref(0)
const showImageUpload = ref(false)
const showLinkDialog = ref(false)
const linkForm = ref({ text: '', url: '' })

// 撤消/重做历史记录
const history = ref([])
const historyIndex = ref(-1)
const maxHistorySize = 50

// 保存历史记录
const saveHistory = () => {
  const currentState = JSON.stringify(blocks.value)
  if (historyIndex.value < history.value.length - 1) {
    history.value = history.value.slice(0, historyIndex.value + 1)
  }
  history.value.push(currentState)
  if (history.value.length > maxHistorySize) {
    history.value.shift()
  } else {
    historyIndex.value++
  }
}

// 撤消
const undo = () => {
  if (historyIndex.value > 0) {
    historyIndex.value--
    blocks.value = JSON.parse(history.value[historyIndex.value])
    emit('update:modelValue', exportMarkdown())
  }
}

// 重做
const redo = () => {
  if (historyIndex.value < history.value.length - 1) {
    historyIndex.value++
    blocks.value = JSON.parse(history.value[historyIndex.value])
    emit('update:modelValue', exportMarkdown())
  }
}

// 检查是否可以撤消/重做
const canUndo = computed(() => historyIndex.value > 0)
const canRedo = computed(() => historyIndex.value < history.value.length - 1)

// 监听 modelValue 变化，初始化 blocks
watch(() => props.modelValue, (newVal) => {
  if (newVal && newVal.trim()) {
    importMarkdown(newVal)
    history.value = [JSON.stringify(blocks.value)]
    historyIndex.value = 0
  }
}, { immediate: true })

// 设置活动块
const setActiveBlock = (index) => {
  activeBlockIndex.value = index
}

// 添加块
const addBlock = (type) => {
  saveHistory()
  const newBlock = {
    id: Date.now(),
    type,
    content: ''
  }

  if (type === 'heading') {
    newBlock.level = 2
  } else if (type === 'code') {
    newBlock.language = 'javascript'
  } else if (type === 'image') {
    newBlock.url = ''
    newBlock.alt = ''
  } else if (type === 'table') {
    newBlock.columns = [{ prop: 'col1', label: '列1' }]
    newBlock.data = [{ col1: '' }]
  } else if (type === 'quote') {
    newBlock.source = ''
  }

  const index = activeBlockIndex.value + 1
  blocks.value.splice(index, 0, newBlock)
  activeBlockIndex.value = index
}

// 删除块
const deleteBlock = (index) => {
  saveHistory()
  if (blocks.value.length > 1) {
    blocks.value.splice(index, 1)
    if (activeBlockIndex.value >= index) {
      activeBlockIndex.value = Math.max(0, activeBlockIndex.value - 1)
    }
  }
}

// 移动块
const moveBlock = (index, direction) => {
  saveHistory()
  const newIndex = index + direction
  if (newIndex >= 0 && newIndex < blocks.value.length) {
    const temp = blocks.value[index]
    blocks.value[index] = blocks.value[newIndex]
    blocks.value[newIndex] = temp
    activeBlockIndex.value = newIndex
  }
}

// 复制块
const duplicateBlock = (index) => {
  saveHistory()
  const block = blocks.value[index]
  const newBlock = { ...block, id: Date.now() }
  blocks.value.splice(index + 1, 0, newBlock)
}

// 格式化文本
const formatText = (format) => {
  const block = blocks.value[activeBlockIndex.value]
  if (block && block.content) {
    const selection = window.getSelection()
    const selectedText = selection.toString()
    
    if (selectedText) {
      let formatted = selectedText
      switch (format) {
        case 'bold':
          formatted = `**${selectedText}**`
          break
        case 'italic':
          formatted = `*${selectedText}*`
          break
        case 'strike':
          formatted = `~~${selectedText}~~`
          break
      }
      block.content = block.content.replace(selectedText, formatted)
    }
  }
}

// 插入链接
const insertLink = () => {
  linkForm.value = { text: '', url: '' }
  showLinkDialog.value = true
}

const confirmInsertLink = () => {
  const block = blocks.value[activeBlockIndex.value]
  if (block) {
    const linkMarkdown = `[${linkForm.value.text}](${linkForm.value.url})`
    block.content += linkMarkdown
  }
  showLinkDialog.value = false
}

// 图片上传
const handleImageUploadSuccess = (response) => {
  const block = blocks.value[activeBlockIndex.value]
  if (block && block.type === 'image') {
    block.url = response.url
  } else {
    addBlock('image')
    blocks.value[blocks.value.length - 1].url = response.url
  }
  showImageUpload.value = false
  ElMessage.success('图片上传成功')
}

const handleImageUploadError = () => {
  ElMessage.error('图片上传失败')
}

// 表格操作
const addTableRow = (blockIndex) => {
  const block = blocks.value[blockIndex]
  const newRow = {}
  block.columns.forEach(col => {
    newRow[col.prop] = ''
  })
  block.data.push(newRow)
}

const addTableColumn = (blockIndex) => {
  const block = blocks.value[blockIndex]
  const colIndex = block.columns.length + 1
  const newCol = { prop: `col${colIndex}`, label: `列${colIndex}` }
  block.columns.push(newCol)
  block.data.forEach(row => {
    row[newCol.prop] = ''
  })
}

// 导出 Markdown
const exportMarkdown = () => {
  let markdown = ''
  
  blocks.value.forEach(block => {
    switch (block.type) {
      case 'text':
        markdown += block.content + '\n\n'
        break
      case 'heading':
        markdown += '#'.repeat(block.level) + ' ' + block.content + '\n\n'
        break
      case 'code':
        markdown += '```' + block.language + '\n' + block.content + '\n```\n\n'
        break
      case 'image':
        markdown += `![${block.alt}](${block.url})\n\n`
        break
      case 'quote':
        markdown += '> ' + block.content.replace(/\n/g, '\n> ') + '\n\n'
        if (block.source) {
          markdown += '> —— ' + block.source + '\n\n'
        }
        break
      case 'divider':
        markdown += '---\n\n'
        break
    }
  })
  
  return markdown
}

// 监听变化，导出 Markdown
watch(blocks, () => {
  emit('update:modelValue', exportMarkdown())
}, { deep: true })

// 导入 Markdown
const importMarkdown = (markdown) => {
  // 简单的 Markdown 解析
  const lines = markdown.split('\n')
  const newBlocks = []
  let currentText = ''
  
  lines.forEach(line => {
    if (line.startsWith('#')) {
      if (currentText) {
        newBlocks.push({ id: Date.now() + Math.random(), type: 'text', content: currentText.trim() })
        currentText = ''
      }
      const level = line.match(/^#+/)[0].length
      newBlocks.push({ id: Date.now() + Math.random(), type: 'heading', level, content: line.replace(/^#+\s*/, '') })
    } else if (line.startsWith('```')) {
      if (currentText) {
        newBlocks.push({ id: Date.now() + Math.random(), type: 'text', content: currentText.trim() })
        currentText = ''
      }
      // 代码块处理简化版
      newBlocks.push({ id: Date.now() + Math.random(), type: 'code', language: 'text', content: '' })
    } else if (line.startsWith('>')) {
      if (currentText) {
        newBlocks.push({ id: Date.now() + Math.random(), type: 'text', content: currentText.trim() })
        currentText = ''
      }
      newBlocks.push({ id: Date.now() + Math.random(), type: 'quote', content: line.replace(/^>\s*/, '') })
    } else if (line.startsWith('---')) {
      if (currentText) {
        newBlocks.push({ id: Date.now() + Math.random(), type: 'text', content: currentText.trim() })
        currentText = ''
      }
      newBlocks.push({ id: Date.now() + Math.random(), type: 'divider' })
    } else {
      currentText += line + '\n'
    }
  })
  
  if (currentText) {
    newBlocks.push({ id: Date.now() + Math.random(), type: 'text', content: currentText.trim() })
  }
  
  if (newBlocks.length > 0) {
    blocks.value = newBlocks
  }
}

// 暴露方法
defineExpose({
  exportMarkdown,
  importMarkdown,
  undo,
  redo
})
</script>

<style scoped>
.block-editor {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
}

.editor-toolbar {
  padding: 10px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 10px;
}

.editor-content {
  padding: 20px;
  min-height: 400px;
}

.editor-block {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px;
  margin-bottom: 5px;
  border-radius: 4px;
  transition: background 0.2s;
}

.editor-block:hover {
  background: #f5f7fa;
}

.editor-block.is-active {
  background: #ecf5ff;
  border-left: 3px solid #409eff;
}

.block-handle {
  cursor: grab;
  color: #909399;
  padding: 5px;
}

.block-type-icon {
  color: #909399;
  padding: 5px;
  width: 30px;
  text-align: center;
}

.block-text,
.block-heading,
.block-code,
.block-image,
.block-table,
.block-quote {
  flex: 1;
}

.block-heading {
  display: flex;
  gap: 10px;
}

.block-code {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.block-image img {
  max-width: 100%;
  border-radius: 4px;
}

.image-placeholder {
  width: 100%;
  height: 150px;
  border: 2px dashed #dcdfe6;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  cursor: pointer;
}

.block-quote {
  border-left: 4px solid #409eff;
  padding-left: 15px;
}

.block-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.editor-block:hover .block-actions {
  opacity: 1;
}
</style>
