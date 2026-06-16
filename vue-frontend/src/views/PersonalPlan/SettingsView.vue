<template>
  <div class="settings-view">
    <div class="settings-content">
      <el-tabs v-model="activeTab" class="settings-tabs">
        <el-tab-pane label="模板管理" name="templates">
          <div class="tab-content">
            <div class="section-header">
              <h3>计划模板</h3>
              <el-button type="primary" @click="showTemplateDialog = true">
                <el-icon><Plus /></el-icon>
                新建模板
              </el-button>
            </div>

            <el-table :data="templates || []" style="width: 100%">
              <el-table-column prop="name" label="模板名称" />
              <el-table-column prop="type" label="类型">
                <template #default="{ row }">
                  <el-tag>{{ typeMap[row.type] || row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="taskCount" label="任务数" width="100" />
              <el-table-column prop="description" label="描述" />
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button text size="small" @click="editTemplate(row)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button text size="small" type="primary" @click="applyTemplate(row)">
                    应用
                  </el-button>
                  <el-button text size="small" type="danger" @click="deleteTemplate(row)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane label="提醒规则" name="notifications">
          <div class="tab-content">
            <div class="section-header">
              <h3>提醒设置</h3>
            </div>

            <el-form label-width="120px" class="settings-form">
              <el-form-item label="默认提醒时间">
                <el-select v-model="notificationSettings.defaultReminderTime">
                  <el-option label="截止前15分钟" :value="15" />
                  <el-option label="截止前30分钟" :value="30" />
                  <el-option label="截止前1小时" :value="60" />
                  <el-option label="截止前2小时" :value="120" />
                  <el-option label="截止前1天" :value="1440" />
                </el-select>
              </el-form-item>

              <el-form-item label="浏览器通知">
                <el-switch v-model="notificationSettings.browserEnabled" />
              </el-form-item>

              <el-form-item label="邮件通知">
                <el-switch v-model="notificationSettings.emailEnabled" />
              </el-form-item>

              <el-form-item label="通知时机">
                <el-checkbox-group v-model="notificationSettings.notifyOn">
                  <el-checkbox label="task_created">任务创建时</el-checkbox>
                  <el-checkbox label="task_updated">任务更新时</el-checkbox>
                  <el-checkbox label="task_completed">任务完成时</el-checkbox>
                  <el-checkbox label="task_overdue">任务超时时</el-checkbox>
                </el-checkbox-group>
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="saveNotificationSettings">保存设置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <el-tab-pane label="日历同步" name="calendar">
          <div class="tab-content">
            <div class="section-header">
              <h3>日历同步</h3>
            </div>

            <div class="sync-options">
              <div class="sync-card">
                <div class="sync-icon ical">
                  <el-icon><Calendar /></el-icon>
                </div>
                <div class="sync-info">
                  <h4>iCal 订阅</h4>
                  <p>生成 iCal 格式的订阅链接，可导入到任何支持日历订阅的应用</p>
                  <el-input v-model="icalLink" readonly class="sync-link">
                    <template #append>
                      <el-button @click="copyICalLink">复制</el-button>
                    </template>
                  </el-input>
                </div>
              </div>

              <div class="sync-card">
                <div class="sync-icon google">
                  <svg viewBox="0 0 24 24" width="32" height="32">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                </div>
                <div class="sync-info">
                  <h4>Google Calendar</h4>
                  <p>连接到 Google 日历，自动同步任务</p>
                  <el-button type="primary" @click="connectGoogleCalendar">
                    连接 Google 日历
                  </el-button>
                </div>
              </div>

              <div class="sync-card">
                <div class="sync-icon outlook">
                  <svg viewBox="0 0 24 24" width="32" height="32">
                    <path fill="#0078D4" d="M24 7.387v10.478c0 .23-.08.424-.239.572-.159.149-.353.223-.572.223H20.5L12 21.5l-8.5-7.84V7.387c0-.219.074-.413.223-.572.149-.159.343-.239.572-.239H12l7.5-4.889L24 7.387z"/>
                  </svg>
                </div>
                <div class="sync-info">
                  <h4>Outlook Calendar</h4>
                  <p>连接到 Microsoft Outlook 日历</p>
                  <el-button type="primary" @click="connectOutlookCalendar">
                    连接 Outlook
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="团队管理" name="team">
          <div class="tab-content">
            <div class="section-header">
              <h3>团队成员</h3>
              <el-button type="primary" @click="showInviteDialog = true">
                <el-icon><Plus /></el-icon>
                邀请成员
              </el-button>
            </div>

            <el-table :data="teamMembers" style="width: 100%">
              <el-table-column prop="name" label="姓名" />
              <el-table-column prop="email" label="邮箱" />
              <el-table-column prop="role" label="角色">
                <template #default="{ row }">
                  <el-tag :type="roleTypeMap[row.role]">{{ row.role }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                    {{ row.status === 'active' ? '已激活' : '待激活' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-dropdown trigger="click">
                    <el-button text size="small">
                      <el-icon><MoreFilled /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item @click="changeMemberRole(row)">修改角色</el-dropdown-item>
                        <el-dropdown-item divided @click="removeMember(row)" type="danger">移除</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog v-model="showTemplateDialog" :title="editingTemplate ? '编辑模板' : '新建模板'" width="600px">
      <el-form :model="templateForm" label-width="100px">
        <el-form-item label="模板名称">
          <el-input v-model="templateForm.name" placeholder="请输入模板名称" />
        </el-form-item>

        <el-form-item label="模板类型">
          <el-select v-model="templateForm.type" placeholder="选择类型">
            <el-option label="日计划" value="daily" />
            <el-option label="周计划" value="weekly" />
            <el-option label="项目计划" value="project" />
          </el-select>
        </el-form-item>

        <el-form-item label="描述">
          <el-input v-model="templateForm.description" type="textarea" :rows="3" />
        </el-form-item>

        <el-form-item label="任务模板">
          <div class="task-template-list">
            <div v-for="(task, index) in templateForm.tasks" :key="index" class="task-template-item">
              <el-input v-model="task.title" placeholder="任务名称" />
              <el-select v-model="task.priority" placeholder="优先级" style="width: 100px;">
                <el-option label="紧急" value="urgent" />
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
              </el-select>
              <el-input-number v-model="task.estimated_minutes" :min="5" :step="5" :max="480" placeholder="分钟" />
              <el-button text type="danger" @click="removeTemplateTask(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button text @click="addTemplateTask">
              <el-icon><Plus /></el-icon>
              添加任务
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showTemplateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTemplate">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showInviteDialog" title="邀请成员" width="400px">
      <el-form :model="inviteForm" label-width="80px">
        <el-form-item label="邮箱">
          <el-input v-model="inviteForm.email" placeholder="请输入邮箱地址" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="inviteForm.role" placeholder="选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="成员" value="member" />
            <el-option label="观察者" value="viewer" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showInviteDialog = false">取消</el-button>
        <el-button type="primary" @click="sendInvite">发送邀请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Edit, Delete, Calendar, MoreFilled } from '@element-plus/icons-vue'

const activeTab = ref('templates')

const showTemplateDialog = ref(false)
const editingTemplate = ref(null)
const templateForm = reactive({
  name: '',
  type: 'daily',
  description: '',
  tasks: []
})

const showInviteDialog = ref(false)
const inviteForm = reactive({
  email: '',
  role: 'member'
})

const templates = ref([
  { id: 1, name: '每日工作模板', type: 'daily', taskCount: 5, description: '包含晨会、任务处理、日志等' },
  { id: 2, name: '周计划模板', type: 'weekly', taskCount: 10, description: '本周主要工作安排' },
  { id: 3, name: '项目启动模板', type: 'project', taskCount: 8, description: '新项目启动 checklist' }
])

const notificationSettings = reactive({
  defaultReminderTime: 60,
  browserEnabled: true,
  emailEnabled: false,
  notifyOn: ['task_overdue', 'task_completed']
})

const icalLink = ref('webcal://topo-system.com/ical/user123')

const teamMembers = ref([
  { id: 1, name: '张三', email: 'zhangsan@example.com', role: 'admin', status: 'active' },
  { id: 2, name: '李四', email: 'lisi@example.com', role: 'member', status: 'active' },
  { id: 3, name: '王五', email: 'wangwu@example.com', role: 'viewer', status: 'pending' }
])

const typeMap = {
  daily: '日计划',
  weekly: '周计划',
  project: '项目'
}

const roleTypeMap = {
  admin: 'danger',
  member: 'primary',
  viewer: 'info'
}

const addTemplateTask = () => {
  templateForm.tasks.push({
    title: '',
    priority: 'medium',
    estimated_minutes: 30
  })
}

const removeTemplateTask = (index) => {
  templateForm.tasks.splice(index, 1)
}

const editTemplate = (template) => {
  editingTemplate.value = template
  templateForm.name = template.name
  templateForm.type = template.type
  templateForm.description = template.description
  templateForm.tasks = []
  showTemplateDialog.value = true
}

const saveTemplate = async () => {
  if (!templateForm.name) {
    ElMessage.warning('请输入模板名称')
    return
  }

  try {
    if (editingTemplate.value) {
      Object.assign(editingTemplate.value, templateForm)
      ElMessage.success('模板已更新')
    } else {
      templates.value.push({
        id: Date.now(),
        ...templateForm,
        taskCount: templateForm.tasks.length
      })
      ElMessage.success('模板已创建')
    }
    showTemplateDialog.value = false
    editingTemplate.value = null
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const deleteTemplate = async (template) => {
  templates.value = templates.value.filter(t => t.id !== template.id)
  ElMessage.success('模板已删除')
}

const applyTemplate = async (template) => {
  ElMessage.success(`已应用模板：${template.name}`)
}

const saveNotificationSettings = async () => {
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success('提醒设置已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const copyICalLink = () => {
  navigator.clipboard.writeText(icalLink.value)
  ElMessage.success('链接已复制')
}

const connectGoogleCalendar = () => {
  ElMessage.info('Google Calendar 集成功能开发中')
}

const connectOutlookCalendar = () => {
  ElMessage.info('Outlook Calendar 集成功能开发中')
}

const sendInvite = async () => {
  if (!inviteForm.email) {
    ElMessage.warning('请输入邮箱地址')
    return
  }

  try {
    teamMembers.value.push({
      id: Date.now(),
      name: inviteForm.email.split('@')[0],
      email: inviteForm.email,
      role: inviteForm.role,
      status: 'pending'
    })
    ElMessage.success('邀请已发送')
    showInviteDialog.value = false
    inviteForm.email = ''
    inviteForm.role = 'member'
  } catch (error) {
    ElMessage.error('邀请失败')
  }
}

const changeMemberRole = (member) => {
  ElMessage.info(`修改 ${member.name} 角色功能开发中`)
}

const removeMember = async (member) => {
  teamMembers.value = teamMembers.value.filter(m => m.id !== member.id)
  ElMessage.success(`已移除 ${member.name}`)
}

onMounted(() => {
})
</script>

<style scoped>
.settings-view {
  max-width: 1200px;
  margin: 0 auto;
}

.settings-content {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.settings-tabs {
  height: 100%;
}

.settings-tabs :deep(.el-tabs__header) {
  margin-bottom: 24px;
}

.tab-content {
  padding: 8px 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.settings-form {
  max-width: 600px;
}

.sync-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sync-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  border: 1px solid #e6e6e6;
  border-radius: 12px;
  transition: all 0.2s;
}

.sync-card:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
}

.sync-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sync-icon.ical {
  background: #ecf5ff;
  color: #409EFF;
  font-size: 24px;
}

.sync-icon.google {
  background: #fff;
}

.sync-icon.outlook {
  background: #fff;
}

.sync-info {
  flex: 1;
}

.sync-info h4 {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.sync-info p {
  margin: 0 0 12px 0;
  font-size: 13px;
  color: #909399;
}

.sync-link {
  max-width: 400px;
}

.task-template-list {
  width: 100%;
}

.task-template-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  align-items: center;
}

.task-template-item .el-input {
  flex: 1;
}

@media screen and (max-width: 768px) {
  .settings-view {
    padding: 0;
  }

  .settings-header {
    padding: 12px;
  }

  .settings-header h2 {
    font-size: 18px;
  }

  .settings-content {
    padding: 12px;
  }

  .settings-section {
    padding: 12px;
    margin-bottom: 12px;
    border-radius: 8px;
  }

  .settings-section h3 {
    font-size: 15px;
  }

  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .setting-label {
    width: 100% !important;
  }

  .setting-control {
    width: 100%;
  }

  .tag-input-row {
    flex-direction: column;
    align-items: stretch;
  }

  .tag-input-row .el-input {
    width: 100% !important;
    margin-bottom: 8px;
  }

  .task-template-item {
    flex-wrap: wrap;
  }

  .sync-link {
    max-width: 100%;
  }
}
</style>
