<template>
  <div class="attachment-list">
    <div class="attachment-header" v-if="editable">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :file-list="fileList"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        :before-upload="beforeUpload"
        :limit="maxFiles"
        :accept="accept"
        multiple
      >
        <el-button type="primary" size="small">
          <el-icon><Upload /></el-icon>
          上传附件
        </el-button>
        <template #tip>
          <div class="el-upload__tip">
            {{ tipText }}
          </div>
        </template>
      </el-upload>
    </div>

    <div v-if="attachments.length > 0" class="attachment-table">
      <el-table :data="attachments" stripe style="width: 100%;">
        <el-table-column prop="name" label="文件名" min-width="200">
          <template #default="{ row }">
            <div class="file-name-cell">
              <el-icon :size="20" :class="getFileIconClass(row.name)">
                <Document />
              </el-icon>
              <span class="file-name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="100">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="uploader_name" label="上传人" width="100" />
        <el-table-column prop="created_at" label="上传时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column v-if="editable" label="操作" width="150" align="center">
          <template #default="{ row, $index }">
            <el-button type="primary" link size="small" @click="handleDownload(row)">
              <el-icon><Download /></el-icon>
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row, $index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
        <el-table-column v-else label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleDownload(row)">
              <el-icon><Download /></el-icon>
              下载
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-empty v-else-if="!loading" description="暂无附件" />

    <div v-if="loading" class="loading-mask">
      <el-icon class="is-loading"><Loading /></el-icon>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Download, Delete, Document, Loading } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const props = defineProps({
  attachments: {
    type: Array,
    default: () => []
  },
  editable: {
    type: Boolean,
    default: true
  },
  accept: {
    type: String,
    default: '.doc,.docx,.xls,.xlsx,.pdf,.txt,.zip,.rar,.png,.jpg,.jpeg'
  },
  maxFiles: {
    type: Number,
    default: 10
  },
  maxSize: {
    type: Number,
    default: 10
  },
  tipText: {
    type: String,
    default: '支持上传文档、图片、压缩包等文件，单个文件不超过10MB'
  },
  entityType: {
    type: String,
    default: 'test_case'
  },
  entityId: {
    type: [Number, String],
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:attachments', 'upload', 'delete', 'download'])

const uploadRef = ref(null)
const fileList = ref([])

const handleFileChange = (file, files) => {
  fileList.value = files
}

const handleFileRemove = (file, files) => {
  fileList.value = files
}

const beforeUpload = (file) => {
  const isValidSize = file.size / 1024 / 1024 < props.maxSize
  if (!isValidSize) {
    ElMessage.error(`文件大小不能超过 ${props.maxSize}MB`)
    return false
  }
  return true
}

const handleUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  const uploadPromises = fileList.value.map(async (file) => {
    try {
      const formData = new FormData()
      formData.append('file', file.raw)
      formData.append('entity_type', props.entityType)
      if (props.entityId) {
        formData.append('entity_id', props.entityId)
      }

      const response = await apiService.common.uploadFile(formData)
      return response?.data || response
    } catch (error) {
      console.error(`上传文件 ${file.name} 失败:`, error)
      throw error
    }
  })

  try {
    const results = await Promise.all(uploadPromises)
    emit('upload', results)
    ElMessage.success('上传成功')
    fileList.value = []
    return results
  } catch (error) {
    ElMessage.error('部分文件上传失败')
    throw error
  }
}

const handleDelete = async (attachment, index) => {
  try {
    await ElMessageBox.confirm('确定要删除这个附件吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    emit('delete', attachment, index)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleDownload = (attachment) => {
  emit('download', attachment)
}

const getFileIconClass = (fileName) => {
  const ext = fileName.split('.').pop()?.toLowerCase()
  const iconClass = {
    pdf: 'file-icon-pdf',
    doc: 'file-icon-doc',
    docx: 'file-icon-doc',
    xls: 'file-icon-xls',
    xlsx: 'file-icon-xls',
    png: 'file-icon-image',
    jpg: 'file-icon-image',
    jpeg: 'file-icon-image',
    gif: 'file-icon-image',
    zip: 'file-icon-archive',
    rar: 'file-icon-archive',
    '7z': 'file-icon-archive',
    txt: 'file-icon-text'
  }
  return iconClass[ext] || 'file-icon-default'
}

const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

defineExpose({
  upload: handleUpload
})
</script>

<style scoped>
.attachment-list {
  position: relative;
  width: 100%;
}

.attachment-header {
  margin-bottom: 16px;
}

.attachment-table {
  margin-top: 16px;
}

.file-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-icon-pdf {
  color: #e74c3c;
}

.file-icon-doc {
  color: #3498db;
}

.file-icon-xls {
  color: #27ae60;
}

.file-icon-image {
  color: #9b59b6;
}

.file-icon-archive {
  color: #f39c12;
}

.file-icon-text {
  color: #95a5a6;
}

.file-icon-default {
  color: #7f8c8d;
}

.loading-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.loading-mask .el-icon {
  font-size: 32px;
  color: #409EFF;
}
</style>