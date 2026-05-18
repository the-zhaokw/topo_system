<template>
  <div class="system-settings">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><Setting /></el-icon>
          </div>
          <div class="title-text">
            <h1>系统设置</h1>
            <p class="subtitle">管理系统配置、备份与数据库维护</p>
          </div>
        </div>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="settings-tabs animate-fade-in-up delay-100">
      <!-- 备份管理 -->
      <el-tab-pane label="备份管理" name="backup">
        <el-card class="glass-card settings-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="card-title">
                <el-icon><DocumentCopy /></el-icon>
                <span>数据库备份</span>
              </div>
              <el-button class="btn-gradient" @click="handleCreateBackup" :loading="backupLoading">
                <el-icon><Refresh /></el-icon>
                创建备份
              </el-button>
            </div>
          </template>

          <el-table :data="backups" v-loading="backupsLoading" class="custom-table">
            <el-table-column prop="filename" label="文件名" min-width="200">
              <template #default="{ row }">
                <div class="filename-cell">
                  <el-icon class="file-icon"><Document /></el-icon>
                  <span>{{ row.filename }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="size" label="大小" width="120" align="center">
              <template #default="{ row }">
                <span class="size-badge">{{ formatSize(row.size) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180" align="center">
              <template #default="{ row }">
                <span class="time-text">{{ formatDate(row.created_at) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" align="center" fixed="right">
              <template #default="{ row }">
                <el-button size="small" class="btn-download" @click="handleDownloadBackup(row.filename)">
                  <el-icon><Download /></el-icon>
                  下载
                </el-button>
                <el-button size="small" class="btn-delete" @click="handleDeleteBackup(row.filename)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="backups.length === 0 && !backupsLoading" description="暂无备份文件" class="custom-empty" />
        </el-card>
      </el-tab-pane>

      <!-- 系统配置 -->
      <el-tab-pane label="系统配置" name="config">
        <el-card class="glass-card settings-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="card-title">
                <el-icon><Tools /></el-icon>
                <span>系统参数配置</span>
              </div>
              <el-button class="btn-gradient" @click="handleSaveConfig" :loading="configSaving">
                <el-icon><Check /></el-icon>
                保存配置
              </el-button>
            </div>
          </template>

          <!-- 时间显示卡片 -->
          <div class="time-display-card">
            <div class="time-display-content">
              <div class="time-info">
                <div class="time-label">
                  <el-icon><Clock /></el-icon>
                  系统当前时间
                </div>
                <div class="time-value">{{ currentTime }}</div>
              </div>
              <el-button class="btn-update-time" @click="handleUpdateTime" :loading="timeUpdating">
                <el-icon><Refresh /></el-icon>
                更新时间
              </el-button>
            </div>
          </div>

          <el-form :model="config" label-width="160px" class="settings-form">
            <!-- 上传配置 -->
            <div class="config-section animate-fade-in-up delay-200">
              <div class="section-header">
                <div class="section-icon-wrapper upload-icon">
                  <el-icon><Upload /></el-icon>
                </div>
                <span class="section-title">上传配置</span>
              </div>
              <div class="section-content">
                <el-row :gutter="24">
                  <el-col :span="12">
                    <el-form-item label="最大文件大小(MB)">
                      <el-input-number v-model="config.upload.max_file_size" :min="1" :max="100" class="custom-input-number" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-form-item label="允许的文件类型">
                  <el-checkbox-group v-model="config.upload.allowed_extensions" class="custom-checkbox-group">
                    <el-checkbox label="jpg" class="custom-checkbox">JPG</el-checkbox>
                    <el-checkbox label="jpeg" class="custom-checkbox">JPEG</el-checkbox>
                    <el-checkbox label="png" class="custom-checkbox">PNG</el-checkbox>
                    <el-checkbox label="gif" class="custom-checkbox">GIF</el-checkbox>
                    <el-checkbox label="pdf" class="custom-checkbox">PDF</el-checkbox>
                    <el-checkbox label="doc" class="custom-checkbox">DOC</el-checkbox>
                    <el-checkbox label="docx" class="custom-checkbox">DOCX</el-checkbox>
                    <el-checkbox label="xls" class="custom-checkbox">XLS</el-checkbox>
                    <el-checkbox label="xlsx" class="custom-checkbox">XLSX</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
              </div>
            </div>

            <!-- 备份配置 -->
            <div class="config-section animate-fade-in-up delay-300">
              <div class="section-header">
                <div class="section-icon-wrapper backup-icon">
                  <el-icon><FolderOpened /></el-icon>
                </div>
                <span class="section-title">备份配置</span>
              </div>
              <div class="section-content">
                <el-row :gutter="24">
                  <el-col :span="12">
                    <el-form-item label="自动备份">
                      <el-switch v-model="config.backup.auto_backup" class="custom-switch" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="备份时间" v-if="config.backup.auto_backup">
                      <el-time-picker
                        v-model="config.backup.backup_time"
                        format="HH:mm"
                        value-format="HH:mm"
                        placeholder="选择时间"
                        class="custom-time-picker"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-form-item label="保留天数">
                  <el-input-number v-model="config.backup.retention_days" :min="1" :max="90" class="custom-input-number" />
                </el-form-item>
              </div>
            </div>

            <!-- 邮件服务器配置 -->
            <div class="config-section animate-fade-in-up delay-400">
              <div class="section-header">
                <div class="section-icon-wrapper mail-icon">
                  <el-icon><Message /></el-icon>
                </div>
                <span class="section-title">邮件服务器配置</span>
              </div>
              <div class="section-content">
                <el-row :gutter="20" class="status-row">
                  <el-col :span="24">
                    <el-alert
                      :title="mailConfigStatus.text"
                      :type="mailConfigStatus.type"
                      :closable="false"
                      show-icon
                      class="custom-alert"
                    />
                  </el-col>
                </el-row>
                <el-row :gutter="24">
                  <el-col :span="12">
                    <el-form-item label="启用邮件服务">
                      <el-switch v-model="config.mail_server.enabled" class="custom-switch" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <template v-if="config.mail_server.enabled">
                <el-row :gutter="20" class="test-email-row">
                  <el-col :span="12">
                    <el-form-item label="测试收件人">
                      <UserSelector
                        v-model="testEmailToUserId"
                        :multiple="false"
                        placeholder="选择用户"
                        :show-avatar="true"
                        :show-role="false"
                        :filterable="true"
                        :remote="false"
                        @select="handleTestEmailUserSelect"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12" class="test-btn-col">
                    <el-button class="btn-test" size="default" @click="handleTestEmail" :loading="testEmailLoading" :disabled="!mailConfigComplete || !testEmailTo">
                      <el-icon><Promotion /></el-icon>
                      发送测试邮件
                    </el-button>
                  </el-col>
                </el-row>
                <el-row :gutter="24">
                  <el-col :span="12">
                    <el-form-item label="SMTP服务器">
                      <el-select v-model="config.mail_server.host" placeholder="选择邮件服务商" class="custom-select">
                        <el-option label="网易免费邮箱 (smtp.163.com)" value="smtp.163.com" />
                        <el-option label="网易邮箱 (smtp.vip.163.com)" value="smtp.vip.163.com" />
                        <el-option label="QQ邮箱 (smtp.qq.com)" value="smtp.qq.com" />
                        <el-option label="企业邮箱" value="" />
                      </el-select>
                      <el-input
                        v-if="!config.mail_server.host || config.mail_server.host === ''"
                        v-model="config.mail_server.host"
                        placeholder="手动输入SMTP服务器地址"
                        class="custom-input mt-2"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="端口">
                      <el-input-number v-model="config.mail_server.port" :min="1" :max="65535" class="custom-input-number" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row :gutter="24">
                  <el-col :span="12">
                    <el-form-item label="用户名">
                      <el-input v-model="config.mail_server.username" placeholder="yourname@163.com" class="custom-input" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="密码/授权码">
                      <el-input v-model="config.mail_server.password" type="password" placeholder="不修改请留空" show-password class="custom-input" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row :gutter="24">
                  <el-col :span="12">
                    <el-form-item label="加密方式">
                      <el-radio-group v-model="config.mail_server.use_ssl" @change="handleEncryptionChange" class="custom-radio-group">
                        <el-radio :label="true">SSL (推荐，端口465)</el-radio>
                        <el-radio :label="false">TLS (端口587)</el-radio>
                      </el-radio-group>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="发件人地址">
                      <el-input v-model="config.mail_server.from_address" placeholder="yourname@163.com" class="custom-input" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row :gutter="24">
                  <el-col :span="12">
                    <el-form-item label="发件人名称">
                      <el-input v-model="config.mail_server.from_name" placeholder="TOPO系统" class="custom-input" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <div class="subsection-header">
                  <el-icon><Lock /></el-icon>
                  <span>发送限制</span>
                </div>
                <el-row :gutter="24">
                  <el-col :span="8">
                    <el-form-item label="每日上限">
                      <el-input-number v-model="config.mail_server.max_daily_limit" :min="1" :max="500" class="custom-input-number" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="每小时上限">
                      <el-input-number v-model="config.mail_server.max_hourly_limit" :min="1" :max="100" class="custom-input-number" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="每分钟上限">
                      <el-input-number v-model="config.mail_server.max_per_minute" :min="1" :max="20" class="custom-input-number" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-alert
                  title="配置说明"
                  type="info"
                  :closable="false"
                  class="custom-alert info-alert"
                >
                  <template #default>
                    <div class="alert-content">
                      <strong>网易邮箱：</strong>推荐使用SSL加密(端口465)，或TLS加密(端口587)。<br>
                      <strong>授权码：</strong>强烈建议使用客户端授权码，授权码需在邮箱网页端设置中生成。<br>
                      <strong>发送限制：</strong>163邮箱有严格发送限制，建议：每日≤80封，每小时≤30封，每分钟≤5封。
                    </div>
                  </template>
                </el-alert>
                </template>
              </div>
            </div>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 数据库维护 -->
      <el-tab-pane label="数据库维护" name="maintenance">
        <el-card class="glass-card settings-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="card-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>数据库完整性检查</span>
              </div>
              <el-button class="btn-warning" @click="handleIntegrityCheck" :loading="integrityLoading">
                <el-icon><Refresh /></el-icon>
                执行检查
              </el-button>
            </div>
          </template>

          <div v-if="integrityResult" class="integrity-result animate-fade-in-up">
            <el-alert
              :title="integrityResult.status === 'ok' ? '数据库状态正常' : '发现数据库问题'"
              :type="integrityResult.status === 'ok' ? 'success' : 'error'"
              :closable="false"
              show-icon
              class="custom-alert"
            >
              <template #default>
                <div class="alert-content">共检查 {{ integrityResult.tables?.length || 0 }} 个数据表</div>
              </template>
            </el-alert>

            <el-table :data="integrityResult.tables" class="custom-table result-table">
              <el-table-column prop="name" label="表名" min-width="200">
                <template #default="{ row }">
                  <div class="table-name-cell">
                    <el-icon class="table-icon"><Grid /></el-icon>
                    <span>{{ row.name }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="record_count" label="记录数" width="150" align="center">
                <template #default="{ row }">
                  <span class="count-badge">{{ row.record_count }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="120" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'ok' ? 'success' : 'danger'" effect="light" class="status-tag">
                    <el-icon v-if="row.status === 'ok'"><CircleCheck /></el-icon>
                    <el-icon v-else><CircleClose /></el-icon>
                    {{ row.status === 'ok' ? '正常' : '异常' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>

            <div v-if="integrityResult.issues?.length > 0" class="issues-section">
              <el-alert
                title="发现以下问题"
                type="error"
                :closable="false"
                show-icon
                class="custom-alert"
              >
                <div v-for="(issue, index) in integrityResult.issues" :key="index" class="issue-item">
                  <el-icon><Warning /></el-icon>
                  <span>{{ issue.table }}: {{ issue.issue }}</span>
                </div>
              </el-alert>
            </div>
          </div>

          <el-empty v-else description="点击上方按钮执行数据库完整性检查" class="custom-empty">
            <template #image>
              <div class="empty-icon-wrapper">
                <el-icon><DataAnalysis /></el-icon>
              </div>
            </template>
          </el-empty>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiService } from '@/services/api'
import { systemTimeService } from '@/services/systemTimeService'
import UserSelector from '@/components/common/UserSelector.vue'
import { 
  Setting, Refresh, DocumentCopy, Tools, Check, Clock, Upload, 
  FolderOpened, Message, Promotion, Lock, DataAnalysis, Grid,
  CircleCheck, CircleClose, Warning, Document, Download, Delete
} from '@element-plus/icons-vue'

const activeTab = ref('backup')

const backups = ref([])
const backupsLoading = ref(false)
const backupLoading = ref(false)

const config = ref({
  mail_server: {
    enabled: true,
    host: 'smtp.163.com',
    port: 465,
    use_tls: false,
    use_ssl: true,
    username: 'zhaokangwei0123@163.com',
    password: 'JAenQ39NreJhjF8r',
    from_address: 'zhaokangwei0123@163.com',
    from_name: 'TOPO系统',
    max_daily_limit: 80,
    max_hourly_limit: 30,
    max_per_minute: 5
  },
  upload: {
    max_file_size: 16,
    allowed_extensions: ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx']
  },
  backup: {
    auto_backup: false,
    backup_time: '02:00',
    retention_days: 7
  }
})
const configLoading = ref(false)
const configSaving = ref(false)

const testEmailLoading = ref(false)
const testEmailTo = ref('')
const testEmailToUserId = ref(null)

const handleTestEmailUserSelect = (user) => {
  if (user && user.email) {
    testEmailTo.value = user.email
    testEmailToUserId.value = user.id
  }
}

const mailConfigComplete = computed(() => {
  const mail = config.value.mail_server
  return mail.enabled && mail.host && mail.username && mail.from_address
})

const mailConfigStatus = computed(() => {
  const mail = config.value.mail_server
  if (!mail.enabled) return { status: 'disabled', text: '邮件服务未启用', type: 'info' }
  if (!mail.host) return { status: 'incomplete', text: 'SMTP服务器未配置', type: 'warning' }
  if (!mail.username) return { status: 'incomplete', text: '用户名未配置', type: 'warning' }
  if (!mail.from_address) return { status: 'incomplete', text: '发件人地址未配置', type: 'warning' }
  if (!mail.password) return { status: 'incomplete', text: '密码未配置', type: 'warning' }
  return { status: 'complete', text: '邮件配置完整', type: 'success' }
})

const integrityLoading = ref(false)
const integrityResult = ref(null)

const currentTime = ref('')
const timeUpdating = ref(false)

const updateTime = () => {
  const now = systemTimeService.getServerTime()
  currentTime.value = now.toLocaleString('zh-CN')
}

const handleEncryptionChange = (useSsl) => {
  if (useSsl) {
    config.value.mail_server.port = 465
    config.value.mail_server.use_tls = false
  } else {
    config.value.mail_server.port = 587
    config.value.mail_server.use_tls = true
  }
}

const handleUpdateTime = async () => {
  timeUpdating.value = true
  try {
    const response = await apiService.system.getSystemTime()
    currentTime.value = response.server_time ? new Date(response.server_time).toLocaleString('zh-CN') : systemTimeService.getServerTime().toLocaleString('zh-CN')
    ElMessage.success('时间已更新')
  } catch (error) {
    updateTime()
    ElMessage.warning('获取服务器时间失败，已更新为本地时间')
  } finally {
    timeUpdating.value = false
  }
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const fetchBackups = async () => {
  backupsLoading.value = true
  try {
    const response = await apiService.system.getBackups()
    backups.value = response.backups || []
  } catch (error) {
    ElMessage.error('获取备份列表失败')
  } finally {
    backupsLoading.value = false
  }
}

const handleCreateBackup = async () => {
  backupLoading.value = true
  try {
    const response = await apiService.system.createBackup()
    ElMessage.success('备份创建成功')
    fetchBackups()
  } catch (error) {
    ElMessage.error('备份创建失败: ' + (error.message || '未知错误'))
  } finally {
    backupLoading.value = false
  }
}

const handleDownloadBackup = async (filename) => {
  try {
    const response = await apiService.system.downloadBackup(filename)
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const handleDeleteBackup = async (filename) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除备份文件 "${filename}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await apiService.system.deleteBackup(filename)
    ElMessage.success('删除成功')
    fetchBackups()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const fetchConfig = async () => {
  configLoading.value = true
  try {
    const response = await apiService.system.getConfig()
    config.value = { ...config.value, ...response }
  } catch (error) {
    ElMessage.error('获取配置失败')
  } finally {
    configLoading.value = false
  }
}

const handleSaveConfig = async () => {
  configSaving.value = true
  try {
    await apiService.system.updateConfig(config.value)
    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error('保存配置失败')
  } finally {
    configSaving.value = false
  }
}

const handleTestEmail = async () => {
  if (!testEmailTo.value) {
    ElMessage.warning('请输入测试收件人邮箱地址')
    return
  }

  const mailConfig = config.value.mail_server
  if (!mailConfig.enabled) {
    ElMessage.warning('请先启用邮件服务')
    return
  }
  if (!mailConfig.host || !mailConfig.username) {
    ElMessage.warning('请完善邮件配置（SMTP服务器和用户名不能为空）')
    return
  }
  if (!mailConfig.from_address) {
    ElMessage.warning('请填写发件人地址')
    return
  }

  testEmailLoading.value = true
  try {
    const response = await apiService.system.testEmail(testEmailTo.value)
    ElMessage.success(response.message || '测试邮件发送成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '发送测试邮件失败')
  } finally {
    testEmailLoading.value = false
  }
}

const handleIntegrityCheck = async () => {
  integrityLoading.value = true
  integrityResult.value = null
  try {
    const response = await apiService.system.integrityCheck()
    integrityResult.value = response
    if (response.status === 'ok') {
      ElMessage.success('数据库完整性检查通过')
    } else {
      ElMessage.warning('发现数据库问题，请查看详情')
    }
  } catch (error) {
    ElMessage.error('检查失败')
  } finally {
    integrityLoading.value = false
  }
}

onMounted(() => {
  fetchBackups()
  fetchConfig()
  updateTime()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.system-settings {
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  min-height: 100%;
}

/* 页面头部 - 玻璃拟态风格 */
.page-header {
  position: relative;
  margin-bottom: 24px;
  padding: 28px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px -10px rgba(102, 126, 234, 0.4);
}

.page-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at top right, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse at bottom left, rgba(118, 75, 162, 0.3) 0%, transparent 50%);
  pointer-events: none;
}

.page-header::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.5;
  pointer-events: none;
}

.header-bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.3;
}

.orb-1 {
  width: 200px;
  height: 200px;
  background: #f093fb;
  top: -50px;
  right: 10%;
  animation: float 6s ease-in-out infinite;
}

.orb-2 {
  width: 150px;
  height: 150px;
  background: #4facfe;
  bottom: -30px;
  right: 30%;
  animation: float 8s ease-in-out infinite reverse;
}

.header-content {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 20px;
}

.title-icon-wrapper {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.title-icon {
  font-size: 32px;
  color: white;
}

.title-text h1 {
  margin: 0 0 6px 0;
  color: white;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.subtitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 400;
}

/* 设置标签页 */
.settings-tabs {
  background: transparent;
}

.settings-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
  border-bottom: none;
}

.settings-tabs :deep(.el-tabs__nav-wrap) {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 8px 16px;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.settings-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.settings-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
  color: #64748b;
  padding: 0 24px;
  height: 40px;
  line-height: 40px;
  border-radius: 8px;
  transition: all 0.3s;
}

.settings-tabs :deep(.el-tabs__item:hover) {
  color: #667eea;
}

.settings-tabs :deep(.el-tabs__item.is-active) {
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 15px -3px rgba(102, 126, 234, 0.4);
}

.settings-tabs :deep(.el-tabs__active-bar) {
  display: none;
}

/* 玻璃拟态卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  transition: all 0.4s;
}

.glass-card:hover {
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.12), 0 10px 20px -5px rgba(0, 0, 0, 0.08);
}

.settings-card :deep(.el-card__header) {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.settings-card :deep(.el-card__body) {
  padding: 24px;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: #1e293b;
  font-size: 16px;
}

.card-title .el-icon {
  color: #667eea;
  font-size: 20px;
}

/* 按钮样式 */
.btn-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(102, 126, 234, 0.5);
}

.btn-warning {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  border: none;
  color: white;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-warning:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(245, 158, 11, 0.5);
}

.btn-download {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-download:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px -5px rgba(16, 185, 129, 0.4);
}

.btn-delete {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-delete:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px -5px rgba(239, 68, 68, 0.4);
}

.btn-test {
  background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
  border: none;
  color: white;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-test:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(139, 92, 246, 0.5);
}

.btn-test:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-update-time {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  border: none;
  color: white;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-update-time:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(245, 158, 11, 0.5);
}

/* 时间显示卡片 */
.time-display-card {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 32px;
}

.time-display-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.time-info {
  flex: 1;
}

.time-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #64748b;
  margin-bottom: 8px;
}

.time-label .el-icon {
  color: #667eea;
}

.time-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  font-family: 'Monaco', 'Menlo', monospace;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 配置分区 */
.config-section {
  margin-bottom: 32px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(226, 232, 240, 0.6);
  transition: all 0.3s;
}

.config-section:hover {
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 8px 25px -5px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.section-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  transition: all 0.3s;
}

.section-icon-wrapper.upload-icon {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #3b82f6;
}

.section-icon-wrapper.backup-icon {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #10b981;
}

.section-icon-wrapper.mail-icon {
  background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
  color: #ec4899;
}

.config-section:hover .section-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: #1e293b;
}

.subsection-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 20px 0 16px 0;
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
}

.subsection-header .el-icon {
  color: #f59e0b;
}

/* 自定义表单元素 */
.custom-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
  transition: all 0.3s;
}

.custom-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.04);
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
}

.custom-select :deep(.el-input__wrapper) {
  border-radius: 10px;
}

.custom-input-number :deep(.el-input__wrapper) {
  border-radius: 10px;
}

.custom-time-picker :deep(.el-input__wrapper) {
  border-radius: 10px;
}

/* 自定义开关 */
.custom-switch :deep(.el-switch__core) {
  border-radius: 20px;
  background: #e2e8f0;
}

.custom-switch.is-checked :deep(.el-switch__core) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.custom-switch :deep(.el-switch__action) {
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 自定义复选框 */
.custom-checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.custom-checkbox :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
}

.custom-checkbox :deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #667eea;
  font-weight: 500;
}

/* 自定义单选框 */
.custom-radio-group :deep(.el-radio__input.is-checked .el-radio__inner) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
}

.custom-radio-group :deep(.el-radio__input.is-checked + .el-radio__label) {
  color: #667eea;
  font-weight: 500;
}

/* 自定义表格 */
.custom-table {
  --el-table-header-bg-color: rgba(241, 245, 249, 0.8);
  --el-table-row-hover-bg-color: rgba(102, 126, 234, 0.05);
}

.custom-table :deep(.el-table__header th) {
  font-weight: 600;
  color: #1e293b;
  background: rgba(241, 245, 249, 0.8);
}

.custom-table :deep(.el-table__row) {
  transition: all 0.3s;
}

.filename-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-icon {
  color: #667eea;
  font-size: 18px;
}

.size-badge {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.time-text {
  color: #64748b;
  font-size: 13px;
}

.table-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-icon {
  color: #667eea;
  font-size: 18px;
}

.count-badge {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.status-tag {
  font-weight: 500;
  border-radius: 20px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* 自定义警告框 */
.custom-alert {
  border-radius: 12px;
}

.custom-alert :deep(.el-alert__title) {
  font-weight: 600;
}

.alert-content {
  font-size: 13px;
  line-height: 1.6;
}

.info-alert {
  margin-top: 16px;
}

/* 状态行 */
.status-row {
  margin-bottom: 20px;
}

.test-email-row {
  margin-bottom: 16px;
}

.test-btn-col {
  display: flex;
  align-items: flex-end;
  padding-bottom: 18px;
}

/* 完整性检查结果 */
.integrity-result {
  animation: fadeInUp 0.5s ease-out;
}

.result-table {
  margin-top: 20px;
}

.issues-section {
  margin-top: 20px;
}

.issue-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  font-size: 13px;
  color: #dc2626;
}

.issue-item .el-icon {
  color: #dc2626;
}

/* 自定义空状态 */
.custom-empty :deep(.el-empty__description) {
  color: #94a3b8;
}

.empty-icon-wrapper {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.empty-icon-wrapper .el-icon {
  font-size: 40px;
  color: #667eea;
}

/* 间距工具类 */
.mt-2 {
  margin-top: 8px;
}

/* 动画 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-fade-in-down {
  animation: fadeInDown 0.6s ease-out;
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s ease-out;
  animation-fill-mode: both;
}

.delay-100 { animation-delay: 100ms; }
.delay-200 { animation-delay: 200ms; }
.delay-300 { animation-delay: 300ms; }
.delay-400 { animation-delay: 400ms; }

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .page-header {
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 16px;
  }

  .header-title {
    gap: 14px;
  }

  .title-icon-wrapper {
    width: 48px;
    height: 48px;
    border-radius: 14px;
  }

  .title-icon {
    font-size: 24px;
  }

  .title-text h1 {
    font-size: 22px;
  }

  .subtitle {
    font-size: 13px;
  }

  .settings-tabs :deep(.el-tabs__nav-wrap) {
    padding: 6px 12px;
  }

  .settings-tabs :deep(.el-tabs__item) {
    font-size: 13px;
    padding: 0 16px;
    height: 36px;
    line-height: 36px;
  }

  .settings-card :deep(.el-card__header),
  .settings-card :deep(.el-card__body) {
    padding: 16px;
  }

  .time-display-card {
    padding: 16px;
  }

  .time-display-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .time-value {
    font-size: 20px;
  }

  .config-section {
    padding: 16px;
    margin-bottom: 20px;
  }

  .section-header {
    margin-bottom: 16px;
    padding-bottom: 12px;
  }

  .section-icon-wrapper {
    width: 36px;
    height: 36px;
    font-size: 18px;
  }

  .section-title {
    font-size: 15px;
  }

  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .test-btn-col {
    padding-bottom: 0;
    padding-top: 8px;
  }

  .custom-checkbox-group {
    gap: 8px;
  }

  .custom-checkbox {
    margin-right: 0;
  }
}

@media screen and (max-width: 480px) {
  .page-header {
    padding: 16px;
  }

  .title-text h1 {
    font-size: 20px;
  }

  .time-value {
    font-size: 16px;
  }

  .btn-gradient,
  .btn-warning {
    width: 100%;
    justify-content: center;
  }
}
</style>
