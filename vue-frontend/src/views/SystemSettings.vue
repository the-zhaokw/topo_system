<template>
  <div class="system-settings">
    <div class="header">
      <h1>系统设置</h1>
      <p>管理系统配置、备份与数据库维护</p>
    </div>

    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- 备份管理 -->
      <el-tab-pane label="备份管理" name="backup">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>数据库备份</span>
              <el-button type="primary" @click="handleCreateBackup" :loading="backupLoading">
                <el-icon><Refresh /></el-icon>
                创建备份
              </el-button>
            </div>
          </template>

          <el-table :data="backups" v-loading="backupsLoading">
            <el-table-column prop="filename" label="文件名" />
            <el-table-column prop="size" label="大小">
              <template #default="{ row }">
                {{ formatSize(row.size) }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="handleDownloadBackup(row.filename)">
                  下载
                </el-button>
                <el-button size="small" type="danger" @click="handleDeleteBackup(row.filename)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 系统配置 -->
      <el-tab-pane label="系统配置" name="config">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统参数配置</span>
              <el-button type="primary" @click="handleSaveConfig" :loading="configSaving">
                保存配置
              </el-button>
            </div>
          </template>

          <div class="time-display-card">
            <el-row :gutter="20" align="middle">
              <el-col :span="12">
                <div class="time-label">系统当前时间</div>
                <div class="time-value">{{ currentTime }}</div>
              </el-col>
              <el-col :span="12" style="text-align: right;">
                <el-button type="warning" @click="handleUpdateTime" :loading="timeUpdating">
                  <el-icon><Refresh /></el-icon>
                  更新时间
                </el-button>
              </el-col>
            </el-row>
          </div>

          <el-form :model="config" label-width="140px">
            <!-- 上传配置 -->
            <el-divider content-position="left">上传配置</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="最大文件大小(MB)">
                  <el-input-number v-model="config.upload.max_file_size" :min="1" :max="100" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="允许的文件类型">
              <el-checkbox-group v-model="config.upload.allowed_extensions">
                <el-checkbox label="jpg" />
                <el-checkbox label="jpeg" />
                <el-checkbox label="png" />
                <el-checkbox label="gif" />
                <el-checkbox label="pdf" />
                <el-checkbox label="doc" />
                <el-checkbox label="docx" />
                <el-checkbox label="xls" />
                <el-checkbox label="xlsx" />
              </el-checkbox-group>
            </el-form-item>

            <!-- 备份配置 -->
            <el-divider content-position="left">备份配置</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="自动备份">
                  <el-switch v-model="config.backup.auto_backup" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="备份时间" v-if="config.backup.auto_backup">
                  <el-time-picker
                    v-model="config.backup.backup_time"
                    format="HH:mm"
                    value-format="HH:mm"
                    placeholder="选择时间"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="保留天数">
              <el-input-number v-model="config.backup.retention_days" :min="1" :max="90" />
            </el-form-item>

            <!-- 邮件服务器配置 -->
            <el-divider content-position="left">邮件服务器配置</el-divider>
            <el-row :gutter="20" style="margin-bottom: 15px;">
              <el-col :span="24">
                <el-alert
                  :title="mailConfigStatus.text"
                  :type="mailConfigStatus.type"
                  :closable="false"
                  show-icon
                />
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="启用邮件服务">
                  <el-switch v-model="config.mail_server.enabled" />
                </el-form-item>
              </el-col>
            </el-row>
            <template v-if="config.mail_server.enabled">
            <el-row :gutter="20" style="margin-bottom: 15px;">
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
              <el-col :span="12" style="display: flex; align-items: flex-end;">
                <el-button type="success" size="small" @click="handleTestEmail" :loading="testEmailLoading" :disabled="!mailConfigComplete || !testEmailTo">
                  发送测试邮件
                </el-button>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="SMTP服务器">
                  <el-select v-model="config.mail_server.host" placeholder="选择邮件服务商" style="width: 100%;">
                    <el-option label="网易免费邮箱 (smtp.163.com)" value="smtp.163.com" />
                    <el-option label="网易邮箱 (smtp.vip.163.com)" value="smtp.vip.163.com" />
                    <el-option label="QQ邮箱 (smtp.qq.com)" value="smtp.qq.com" />
                    <el-option label="企业邮箱" value="" />
                  </el-select>
                  <el-input
                    v-if="!config.mail_server.host || config.mail_server.host === ''"
                    v-model="config.mail_server.host"
                    placeholder="手动输入SMTP服务器地址"
                    style="margin-top: 10px;"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="端口">
                  <el-input-number v-model="config.mail_server.port" :min="1" :max="65535" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="用户名">
                  <el-input v-model="config.mail_server.username" placeholder="yourname@163.com" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="密码/授权码">
                  <el-input v-model="config.mail_server.password" type="password" placeholder="不修改请留空" show-password />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="加密方式">
                  <el-radio-group v-model="config.mail_server.use_ssl" @change="handleEncryptionChange">
                    <el-radio :label="true">SSL (推荐，端口465)</el-radio>
                    <el-radio :label="false">TLS (端口587)</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="发件人地址">
                  <el-input v-model="config.mail_server.from_address" placeholder="yourname@163.com" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="发件人名称">
                  <el-input v-model="config.mail_server.from_name" placeholder="TOPO系统" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-divider content-position="left">发送限制</el-divider>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="每日上限">
                  <el-input-number v-model="config.mail_server.max_daily_limit" :min="1" :max="500" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="每小时上限">
                  <el-input-number v-model="config.mail_server.max_hourly_limit" :min="1" :max="100" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="每分钟上限">
                  <el-input-number v-model="config.mail_server.max_per_minute" :min="1" :max="20" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-alert
              title="配置说明"
              type="info"
              :closable="false"
              style="margin-bottom: 15px;"
            >
              <template #default>
                <div style="font-size: 12px;">
                  <strong>网易邮箱：</strong>推荐使用SSL加密(端口465)，或TLS加密(端口587)。<br>
                  <strong>授权码：</strong>强烈建议使用客户端授权码，授权码需在邮箱网页端设置中生成。<br>
                  <strong>发送限制：</strong>163邮箱有严格发送限制，建议：每日≤80封，每小时≤30封，每分钟≤5封。
                </div>
              </template>
            </el-alert>
            </template>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 数据库维护 -->
      <el-tab-pane label="数据库维护" name="maintenance">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>数据库完整性检查</span>
              <el-button type="warning" @click="handleIntegrityCheck" :loading="integrityLoading">
                <el-icon><Refresh /></el-icon>
                执行检查
              </el-button>
            </div>
          </template>

          <div v-if="integrityResult" class="integrity-result">
            <el-alert
              :title="integrityResult.status === 'ok' ? '数据库状态正常' : '发现数据库问题'"
              :type="integrityResult.status === 'ok' ? 'success' : 'error'"
              :closable="false"
            >
              <template #default>
                <div>共检查 {{ integrityResult.tables?.length || 0 }} 个数据表</div>
              </template>
            </el-alert>

            <el-table :data="integrityResult.tables" style="margin-top: 20px;">
              <el-table-column prop="name" label="表名" />
              <el-table-column prop="record_count" label="记录数" />
              <el-table-column prop="status" label="状态">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'ok' ? 'success' : 'danger'">
                    {{ row.status === 'ok' ? '正常' : '异常' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>

            <div v-if="integrityResult.issues?.length > 0" style="margin-top: 20px;">
              <el-alert
                title="发现以下问题"
                type="error"
                :closable="false"
              >
                <div v-for="(issue, index) in integrityResult.issues" :key="index">
                  {{ issue.table }}: {{ issue.issue }}
                </div>
              </el-alert>
            </div>
          </div>

          <el-empty v-else description="点击上方按钮执行数据库完整性检查" />
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
.system-settings {
  padding: 20px;
}

.header {
  margin-bottom: 24px;
}

.header h1 {
  margin: 0 0 8px 0;
  color: #303133;
}

.header p {
  margin: 0;
  color: #909399;
}

.settings-tabs {
  background: white;
  padding: 20px;
  border-radius: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.integrity-result {
  margin-top: 20px;
}

.time-display-card {
  background: #f5f7fa;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 20px;
}

.time-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.time-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  font-family: monospace;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .system-settings {
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

  .settings-section {
    margin-bottom: 16px;
  }

  .section-title {
    font-size: 16px;
    margin-bottom: 12px;
  }

  .settings-form {
    padding: 12px;
  }

  .el-form-item {
    margin-bottom: 16px;
  }

  .el-form-item__label {
    font-size: 13px;
  }

  .el-input__inner,
  .el-textarea__inner {
    font-size: 14px;
  }

  .switch-group {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .switch-label {
    font-size: 13px;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
  }
}

@media screen and (max-width: 480px) {
  .system-settings {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .section-title {
    font-size: 14px;
  }

  .el-form-item__label {
    font-size: 12px;
  }
}
</style>
