<template>
  <div class="version-history">
    <el-timeline>
      <el-timeline-item
        v-for="version in versions"
        :key="version.id"
        :timestamp="formatDate(version.created_at)"
        :type="version.version_number === currentVersion ? 'primary' : ''"
      >
        <el-card :class="{ 'current-version': version.version_number === currentVersion }">
          <template #header>
            <div class="version-header">
              <div class="version-info">
                <el-tag :type="version.version_number === currentVersion ? 'success' : 'info'">
                  v{{ version.version_number }}
                </el-tag>
                <span class="version-author">{{ version.created_by }}</span>
              </div>
              <div class="version-actions">
                <el-button
                  v-if="version.version_number !== currentVersion"
                  size="small"
                  @click="restoreVersion(version)"
                >
                  恢复此版本
                </el-button>
                <el-button size="small" @click="viewVersion(version)">
                  查看
                </el-button>
                <el-button
                  size="small"
                  @click="compareVersion(version)"
                  :disabled="!compareBase"
                >
                  {{ compareBase?.id === version.id ? '取消对比' : '对比' }}
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="version-content">
            <h4>{{ version.title }}</h4>
            <p class="content-preview">{{ version.content_preview }}</p>
            <p v-if="version.change_summary" class="change-summary">
              <el-icon><InfoFilled /></el-icon>
              {{ version.change_summary }}
            </p>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>
    
    <!-- 版本对比对话框 -->
    <el-dialog
      v-model="compareDialog.visible"
      title="版本对比"
      width="80%"
      top="5vh"
    >
      <div class="version-compare">
        <div class="compare-header">
          <div class="compare-version">
            <el-tag>v{{ compareDialog.version1?.version_number }}</el-tag>
            <span>{{ formatDate(compareDialog.version1?.created_at) }}</span>
          </div>
          <el-icon><Right /></el-icon>
          <div class="compare-version">
            <el-tag type="success">v{{ compareDialog.version2?.version_number }}</el-tag>
            <span>{{ formatDate(compareDialog.version2?.created_at) }}</span>
          </div>
        </div>
        
        <div class="diff-content">
          <pre>{{ compareDialog.diff }}</pre>
        </div>
      </div>
    </el-dialog>
    
    <!-- 版本详情对话框 -->
    <el-dialog
      v-model="detailDialog.visible"
      title="版本详情"
      width="70%"
    >
      <div class="version-detail">
        <h3>{{ detailDialog.version?.title }}</h3>
        <div class="version-meta">
          <span>版本: v{{ detailDialog.version?.version_number }}</span>
          <span>作者: {{ detailDialog.version?.created_by }}</span>
          <span>时间: {{ formatDate(detailDialog.version?.created_at) }}</span>
        </div>
        <el-divider />
        <div class="version-full-content" v-html="renderedContent"></div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'

const props = defineProps({
  articleId: {
    type: Number,
    required: true
  },
  currentVersion: {
    type: Number,
    default: 1
  }
})

const emit = defineEmits(['restore', 'refresh'])

const versions = ref([])
const compareBase = ref(null)
const isMounted = ref(true)
const compareDialog = ref({
  visible: false,
  version1: null,
  version2: null,
  diff: ''
})

const detailDialog = ref({
  visible: false,
  version: null
})

const renderedContent = computed(() => {
  if (!detailDialog.value.version?.content) return ''
  return marked(detailDialog.value.version.content)
})

// 加载版本历史
const loadVersions = async () => {
  if (!props.articleId || !isMounted.value) {
    return
  }
  try {
    const res = await fetch(`/api/knowledge/articles/${props.articleId}/versions`)
    const data = await res.json()
    if (isMounted.value) {
      versions.value = data.items || []
    }
  } catch (error) {
    if (isMounted.value) {
      ElMessage.error('加载版本历史失败')
    }
  }
}

// 恢复版本
const restoreVersion = async (version) => {
  if (!props.articleId || !isMounted.value) {
    ElMessage.error('文章信息不完整')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定要恢复到 v${version.version_number} 吗？当前内容将被保存为新版本。`,
      '确认恢复',
      { type: 'warning' }
    )

    const res = await fetch(
      `/api/knowledge/articles/${props.articleId}/versions/${version.id}/restore`,
      { method: 'POST' }
    )

    if (res.ok) {
      ElMessage.success('恢复成功')
      emit('restore')
      emit('refresh')
      if (isMounted.value) {
        loadVersions()
      }
    }
  } catch (error) {
    if (error !== 'cancel' && isMounted.value) {
      ElMessage.error('恢复失败')
    }
  }
}

// 查看版本
const viewVersion = (version) => {
  detailDialog.value.version = version
  detailDialog.value.visible = true
}

// 对比版本
const compareVersion = async (version) => {
  if (!props.articleId) {
    ElMessage.error('文章信息不完整')
    return
  }
  if (compareBase.value?.id === version.id) {
    compareBase.value = null
    return
  }

  if (!compareBase.value) {
    compareBase.value = version
    ElMessage.info('请选择另一个版本进行对比')
    return
  }

  try {
    const res = await fetch(
      `/api/knowledge/articles/${props.articleId}/versions/compare`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          version_id_1: compareBase.value.id,
          version_id_2: version.id
        })
      }
    )
    
    const data = await res.json()
    compareDialog.value = {
      visible: true,
      version1: data.version_1,
      version2: data.version_2,
      diff: data.diff
    }
    compareBase.value = null
  } catch (error) {
    ElMessage.error('对比失败')
  }
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

onUnmounted(() => {
  isMounted.value = false
})

// 初始化
loadVersions()
</script>

<style scoped>
.version-history {
  padding: 20px;
}

.current-version {
  border: 2px solid #67c23a;
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.version-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.version-author {
  color: #606266;
  font-size: 14px;
}

.version-actions {
  display: flex;
  gap: 8px;
}

.version-content h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.content-preview {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.change-summary {
  margin: 10px 0 0 0;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 6px;
}

.version-compare {
  padding: 20px;
}

.compare-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

.compare-version {
  display: flex;
  align-items: center;
  gap: 10px;
}

.diff-content {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
  overflow-x: auto;
}

.diff-content pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.version-detail {
  padding: 20px;
}

.version-detail h3 {
  margin: 0 0 16px 0;
}

.version-meta {
  display: flex;
  gap: 20px;
  color: #909399;
  font-size: 14px;
  margin-bottom: 16px;
}

.version-full-content {
  line-height: 1.8;
}
</style>
