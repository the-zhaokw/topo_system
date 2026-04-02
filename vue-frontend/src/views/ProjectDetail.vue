<template>
  <div class="project-detail">
    <el-page-header @back="$router.back()" content="项目详情"></el-page-header>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="project-info-card" shadow="hover">
          <div class="project-header">
            <h2 class="project-title">{{ project.name }}</h2>
            <el-tag :type="getStatusType(project.status)" size="large">{{ getStatusText(project.status) }}</el-tag>
          </div>

          <el-descriptions :column="2" border>
            <el-descriptions-item label="项目ID">{{ project.id }}</el-descriptions-item>
            <el-descriptions-item label="项目代码">{{ project.code || '未知' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(project.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ formatDate(project.updated_at) }}</el-descriptions-item>
            <el-descriptions-item label="项目状态" :span="2">{{ getStatusText(project.status) }}</el-descriptions-item>
            <el-descriptions-item label="项目类型" :span="2">{{ getProjectTypeText(project.project_type) }}</el-descriptions-item>
            <el-descriptions-item label="项目经理">{{ project.manager_name || '未知' }}</el-descriptions-item>
            <el-descriptions-item label="当前阶段">{{ project.current_stage || '未知' }}</el-descriptions-item>
            <el-descriptions-item label="进度" :span="2">
              <el-progress :percentage="project.progress || 0" :show-text="true" :stroke-width="16" />
            </el-descriptions-item>
            <el-descriptions-item label="开始时间">{{ formatDate(project.start_date) || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="结束时间">{{ formatDate(project.end_date) || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="优先级">
              <el-tag :type="getPriorityType(project.priority)" size="small">{{ getPriorityText(project.priority) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="质量">
              <el-tag :type="getQualityType(project.quality)" size="small">{{ getQualityText(project.quality) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="风险">
              <el-tag :type="getRiskType(project.risk)" size="small">{{ getRiskText(project.risk) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="资源状态">
              <el-tag :type="getResourceType(project.resources)" size="small">{{ project.resources || '未设置' }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="缺陷数量" :span="2">{{ project.bug_count || 0 }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="project-tech-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>技术信息</span>
            </div>
          </template>

          <el-descriptions :column="2" border>
            <el-descriptions-item label="技术栈" :span="2">
              <div v-if="project.technology_stack">{{ project.technology_stack }}</div>
              <span v-else class="text-muted">未设置</span>
            </el-descriptions-item>
            <el-descriptions-item label="标签" :span="2">
              <div v-if="project.tags" class="tags-container">
                <el-tag v-for="(tag, index) in parseTags(project.tags)" :key="index" size="small" style="margin-right: 5px;">{{ tag }}</el-tag>
              </div>
              <span v-else class="text-muted">未设置</span>
            </el-descriptions-item>
            <el-descriptions-item label="里程碑" :span="2">
              <div v-if="project.milestones" class="milestones-container">
                <div v-for="(milestone, index) in parseMilestones(project.milestones)" :key="index" class="milestone-item">
                  <el-icon><Flag /></el-icon>
                  <span>{{ milestone }}</span>
                </div>
              </div>
              <span v-else class="text-muted">未设置</span>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="project-client-card" shadow="hover" v-if="project.client_name || project.project_type === 'client'">
          <template #header>
            <div class="card-header">
              <span>客户信息</span>
            </div>
          </template>

          <el-descriptions :column="2" border>
            <el-descriptions-item label="客户名称">{{ project.client_name || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="客户联系方式">{{ project.client_contact || '未设置' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="project-finance-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>财务与资源信息</span>
            </div>
          </template>

          <el-descriptions :column="3" border>
            <el-descriptions-item label="预算">{{ project.budget ? `¥${parseFloat(project.budget).toLocaleString()}` : '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="实际成本">{{ project.actual_cost ? `¥${parseFloat(project.actual_cost).toLocaleString()}` : '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="合同金额">{{ project.contract_value ? `¥${parseFloat(project.contract_value).toLocaleString()}` : '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="预估工时">{{ project.estimated_hours || 0 }}小时</el-descriptions-item>
            <el-descriptions-item label="实际工时">{{ project.actual_hours || 0 }}小时</el-descriptions-item>
            <el-descriptions-item label="团队规模">{{ project.team_size || 0 }}人</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="project-intro-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>项目介绍</span>
            </div>
          </template>
          <div class="project-intro-content">
            {{ project.description || '暂无项目介绍' }}
          </div>
        </el-card>

        <el-card class="project-versions-card" :class="{ 'versions-empty': versions.length === 0 }" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>项目版本</span>
              <span class="member-count">(共 {{ versions.length }} 个版本)</span>
              <el-button type="primary" size="small" :icon="Plus" @click="addVersion" style="margin-left: auto;">
                添加版本
              </el-button>
            </div>
          </template>

          <div v-if="versions.length > 0" class="versions-table-container">
            <el-table :data="versions" style="width: 100%" stripe>
              <el-table-column prop="name" label="版本名称" width="150">
                <template #default="{ row }">
                  <el-tag type="primary">{{ row.name || '未命名' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="版本描述" min-width="200"></el-table-column>
              <el-table-column prop="release_date" label="发布日期" width="180">
                <template #default="{ row }">
                  {{ row.release_date || '未设置' }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row, $index }">
                  <el-button type="primary" size="small" :icon="Edit" circle @click="editVersion(row, $index)" />
                  <el-button type="danger" size="small" :icon="Delete" circle @click="deleteVersion($index)" />
                </template>
              </el-table-column>
            </el-table>
          </div>
          <el-empty v-else description="暂无版本信息，请在项目编辑中添加版本" :image-size="80" />
        </el-card>

        <el-card class="project-modules-card" :class="{ 'modules-empty': modules.length === 0 }" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>项目模块</span>
              <span class="member-count">(共 {{ modules.length }} 个模块)</span>
              <el-button type="primary" size="small" :icon="Plus" @click="addModule" style="margin-left: auto;">
                添加模块
              </el-button>
            </div>
          </template>

          <div v-if="modules.length > 0" class="modules-tags">
            <el-tag
              v-for="(module, index) in modules"
              :key="index"
              type="success"
              closable
              @close="deleteModule(index)"
              @click="editModule(module, index)"
              class="module-tag"
            >
              {{ module.name }}
            </el-tag>
          </div>
          <el-empty v-else description="暂无模块信息，点击添加模块" :image-size="80" />
        </el-card>

        <el-card class="project-members-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>参与人员</span>
              <span class="member-count">(共 {{ members.length }} 人)</span>
            </div>
          </template>

          <el-table :data="members" style="width: 100%" stripe>
            <el-table-column prop="user_id" label="用户ID" width="100"></el-table-column>
            <el-table-column prop="username" label="用户名" width="150">
              <template #default="{ row }">
                <router-link :to="'/users/' + row.user_id" class="user-link">
                  {{ row.username }}
                </router-link>
              </template>
            </el-table-column>
            <el-table-column prop="position" label="职位" width="120">
              <template #default="{ row }">
                <el-tag>{{ row.position || '未设置' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="department" label="部门" width="150"></el-table-column>
            <el-table-column prop="joined_at" label="加入时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.joined_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card class="bug-stats-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>缺陷报告统计</span>
            </div>
          </template>

          <el-row :gutter="20" class="stats-row">
            <el-col :span="6">
              <el-card class="stat-card" shadow="hover">
                <div class="stat-content">
                  <div class="stat-number">{{ bugStats.total || 0 }}</div>
                  <div class="stat-label">总缺陷数</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card" shadow="hover">
                <div class="stat-content">
                  <div class="stat-number">{{ bugStats.open || 0 }}</div>
                  <div class="stat-label">未解决</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card" shadow="hover">
                <div class="stat-content">
                  <div class="stat-number">{{ bugStats.in_progress || 0 }}</div>
                  <div class="stat-label">处理中</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card" shadow="hover">
                <div class="stat-content">
                  <div class="stat-number">{{ bugStats.closed || 0 }}</div>
                  <div class="stat-label">已关闭</div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <div class="severity-section">
            <h3>严重程度分布</h3>
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="severity-item">
                  <div class="severity-label">
                    <el-tag type="danger">严重</el-tag>
                  </div>
                  <div class="severity-value">{{ bugStats.severity?.critical || 0 }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="severity-item">
                  <div class="severity-label">
                    <el-tag type="warning">高</el-tag>
                  </div>
                  <div class="severity-value">{{ bugStats.severity?.high || 0 }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="severity-item">
                  <div class="severity-label">
                    <el-tag type="info">中</el-tag>
                  </div>
                  <div class="severity-value">{{ bugStats.severity?.medium || 0 }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="severity-item">
                  <div class="severity-label">
                    <el-tag type="success">低</el-tag>
                  </div>
                  <div class="severity-value">{{ bugStats.severity?.low || 0 }}</div>
                </div>
              </el-col>
            </el-row>
          </div>

          <div class="priority-section">
            <h3>优先级分布</h3>
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="priority-item">
                  <div class="priority-label">
                    <el-tag type="danger">高</el-tag>
                  </div>
                  <div class="priority-value">{{ bugStats.priority?.high || 0 }}</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="priority-item">
                  <div class="priority-label">
                    <el-tag type="warning">中</el-tag>
                  </div>
                  <div class="priority-value">{{ bugStats.priority?.medium || 0 }}</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="priority-item">
                  <div class="priority-label">
                    <el-tag type="success">低</el-tag>
                  </div>
                  <div class="priority-value">{{ bugStats.priority?.low || 0 }}</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="project-subfunctions-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>项目子功能</span>
            </div>
          </template>

          <div class="subfunctions-list">
            <div class="subfunction-item" @click="navigateToSubfunction('bugs')">
              <el-icon class="subfunction-icon"><Warning /></el-icon>
              <div class="subfunction-info">
                <div class="subfunction-title">缺陷管理</div>
                <div class="subfunction-count">{{ bugStats.total || 0 }} 个缺陷</div>
              </div>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </div>
            <div class="subfunction-item" @click="navigateToSubfunction('requirements')">
              <el-icon class="subfunction-icon"><Document /></el-icon>
              <div class="subfunction-info">
                <div class="subfunction-title">需求管理</div>
                <div class="subfunction-count">需求集管理</div>
              </div>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </div>
            <div class="subfunction-item" @click="navigateToSubfunction('tests')">
              <el-icon class="subfunction-icon"><CircleCheck /></el-icon>
              <div class="subfunction-info">
                <div class="subfunction-title">测试管理</div>
                <div class="subfunction-count">测试集与用例管理</div>
              </div>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </div>
            <div class="subfunction-item" @click="navigateToSubfunction('risks')">
              <el-icon class="subfunction-icon"><Warning /></el-icon>
              <div class="subfunction-info">
                <div class="subfunction-title">风险管理</div>
                <div class="subfunction-count">风险与问题管理</div>
              </div>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </div>
            <div class="subfunction-item" @click="navigateToSubfunction('logs')">
              <el-icon class="subfunction-icon"><Document /></el-icon>
              <div class="subfunction-info">
                <div class="subfunction-title">日志管理</div>
                <div class="subfunction-count">项目日志记录</div>
              </div>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
  
  <!-- 添加/编辑版本对话框 -->
  <el-dialog v-model="showVersionDialog" :title="versionDialogTitle" width="500px">
    <el-form :model="versionForm" label-width="100px">
      <el-form-item label="版本名称" required>
        <el-input v-model="versionForm.name" placeholder="如：v2.3" />
      </el-form-item>
      <el-form-item label="版本说明">
        <el-input v-model="versionForm.description" type="textarea" :rows="3" placeholder="请输入版本说明" />
      </el-form-item>
      <el-form-item label="发布日期">
        <el-date-picker
          v-model="versionForm.release_date"
          type="date"
          placeholder="选择发布日期"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showVersionDialog = false">取消</el-button>
      <el-button type="primary" @click="saveVersion" :loading="versionLoading">保存</el-button>
    </template>
  </el-dialog>
  
  <!-- 添加/编辑模块对话框 -->
  <el-dialog v-model="showModuleDialog" :title="moduleDialogTitle" width="400px">
    <el-form :model="moduleForm" label-width="80px">
      <el-form-item label="模块名称" required>
        <el-input v-model="moduleForm.name" placeholder="如：OSPF、ISIS、BGP" />
      </el-form-item>
      <el-form-item label="模块描述">
        <el-input v-model="moduleForm.description" type="textarea" :rows="2" placeholder="请输入模块描述" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showModuleDialog = false">取消</el-button>
      <el-button type="primary" @click="saveModule" :loading="moduleLoading">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, CircleCheck, Warning, Plus, Edit, Delete, Flag, ArrowRight } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'
import { formatDate } from '@/utils/dateUtils'

console.log('===== ProjectDetail组件加载 =====')

const route = useRoute()
const router = useRouter()
const projectId = route.params.id

// 项目数据
const project = ref({})
const members = ref([])
const versions = ref([])
const modules = ref([])
const bugStats = ref({})
const loading = ref(false)

// 版本管理对话框
const showVersionDialog = ref(false)
const versionDialogTitle = ref('添加版本')
const editingVersionIndex = ref(-1)
const versionForm = ref({
  name: '',
  description: '',
  release_date: ''
})
const versionLoading = ref(false)

// 模块管理对话框
const showModuleDialog = ref(false)
const moduleDialogTitle = ref('添加模块')
const editingModuleIndex = ref(-1)
const moduleForm = ref({
  name: '',
  description: ''
})
const moduleLoading = ref(false)

// 添加新版本
const addVersion = () => {
  versionDialogTitle.value = '添加版本'
  editingVersionIndex.value = -1
  versionForm.value = {
    name: '',
    description: '',
    release_date: ''
  }
  showVersionDialog.value = true
}

// 编辑版本
const editVersion = (row, index) => {
  versionDialogTitle.value = '编辑版本'
  editingVersionIndex.value = index
  versionForm.value = {
    name: row.name,
    description: row.description,
    release_date: row.release_date
  }
  showVersionDialog.value = true
}

// 删除版本
const deleteVersion = async (index) => {
  try {
    await ElMessageBox.confirm('确定要删除该版本吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    versionLoading.value = true
    const currentVersions = [...versions.value]
    currentVersions.splice(index, 1)
    
    await apiService.projects.update(projectId, {
      versions: JSON.stringify(currentVersions)
    })
    
    versions.value = currentVersions
    ElMessage.success('版本删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除版本失败:', error)
      ElMessage.error('删除版本失败')
    }
  } finally {
    versionLoading.value = false
  }
}

// 保存版本
const saveVersion = async () => {
  if (!versionForm.value.name) {
    ElMessage.warning('请输入版本名称')
    return
  }
  
  versionLoading.value = true
  try {
    const currentVersions = [...versions.value]
    const versionData = {
      name: versionForm.value.name,
      description: versionForm.value.description,
      release_date: versionForm.value.release_date
    }
    
    if (editingVersionIndex.value !== -1) {
      currentVersions[editingVersionIndex.value] = versionData
    } else {
      currentVersions.push(versionData)
    }
    
    await apiService.projects.update(projectId, {
      versions: JSON.stringify(currentVersions)
    })
    
    versions.value = currentVersions
    showVersionDialog.value = false
    ElMessage.success(editingVersionIndex.value !== -1 ? '版本更新成功' : '版本添加成功')
  } catch (error) {
    console.error('保存版本失败:', error)
    ElMessage.error('保存版本失败')
  } finally {
    versionLoading.value = false
  }
}

// 添加新模块
const addModule = () => {
  moduleDialogTitle.value = '添加模块'
  editingModuleIndex.value = -1
  moduleForm.value = {
    name: '',
    description: ''
  }
  showModuleDialog.value = true
}

// 编辑模块
const editModule = (row, index) => {
  moduleDialogTitle.value = '编辑模块'
  editingModuleIndex.value = index
  moduleForm.value = {
    name: row.name,
    description: row.description
  }
  showModuleDialog.value = true
}

// 删除模块
const deleteModule = async (index) => {
  try {
    await ElMessageBox.confirm('确定要删除该模块吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    moduleLoading.value = true
    const currentModules = [...modules.value]
    currentModules.splice(index, 1)
    
    await apiService.projects.update(projectId, {
      modules: JSON.stringify(currentModules)
    })
    
    modules.value = currentModules
    ElMessage.success('模块删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除模块失败:', error)
      ElMessage.error('删除模块失败')
    }
  } finally {
    moduleLoading.value = false
  }
}

// 保存模块
const saveModule = async () => {
  if (!moduleForm.value.name) {
    ElMessage.warning('请输入模块名称')
    return
  }
  
  moduleLoading.value = true
  try {
    const currentModules = [...modules.value]
    const moduleData = {
      name: moduleForm.value.name,
      description: moduleForm.value.description
    }
    
    if (editingModuleIndex.value !== -1) {
      currentModules[editingModuleIndex.value] = moduleData
    } else {
      currentModules.push(moduleData)
    }
    
    await apiService.projects.update(projectId, {
      modules: JSON.stringify(currentModules)
    })
    
    modules.value = currentModules
    showModuleDialog.value = false
    ElMessage.success(editingModuleIndex.value !== -1 ? '模块更新成功' : '模块添加成功')
  } catch (error) {
    console.error('保存模块失败:', error)
    ElMessage.error('保存模块失败')
  } finally {
    moduleLoading.value = false
  }
}

// 子功能导航
const navigateToSubfunction = (subfunction) => {
  switch (subfunction) {
    case 'bugs':
      router.push(`/projects/${projectId}/bugs`)
      break
    case 'requirements':
      router.push(`/projects/${projectId}/requirements`)
      break
    case 'tests':
      router.push(`/projects/${projectId}/tests/suites`)
      break
    case 'risks':
      ElMessage.info('风险管理功能开发中...')
      break
    case 'logs':
      router.push(`/projects/${projectId}/logs`)
      break
    default:
      ElMessage.info('该功能正在开发中...')
  }
}

// 新建Bug
const createNewBug = () => {
  router.push(`/projects/${projectId}/bugs/new`)
}

// 加载项目详情
const loadProjectDetail = async () => {
  loading.value = true
  try {
    // 获取项目基本信息
    console.log('开始加载项目详情，项目ID:', projectId)
    const projectResponse = await apiService.projects.getById(projectId)
    console.log('项目详情API响应:', projectResponse)
    
    // 处理响应数据，确保正确提取项目信息
    const projectData = projectResponse.project || projectResponse || {}
    project.value = projectData
    
    // 解析项目版本
    if (projectData.versions) {
      try {
        versions.value = typeof projectData.versions === 'string' 
          ? JSON.parse(projectData.versions) 
          : projectData.versions
      } catch (e) {
        console.error('解析项目版本失败:', e)
        versions.value = []
      }
    } else {
      versions.value = []
    }
    
    // 解析项目模块
    if (projectData.modules) {
      try {
        modules.value = typeof projectData.modules === 'string' 
          ? JSON.parse(projectData.modules) 
          : projectData.modules
      } catch (e) {
        console.error('解析项目模块失败:', e)
        modules.value = []
      }
    } else {
      modules.value = []
    }
    
    // 直接从项目数据中获取成员信息，不需要单独调用API
    members.value = projectData.members || []
    
    // 初始化缺陷统计数据
    bugStats.value = {
      total: projectData.bug_count || 0,
      open: 0,
      in_progress: 0,
      closed: 0,
      severity: {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0
      },
      priority: {
        high: 0,
        medium: 0,
        low: 0
      }
    }
    
    console.log('项目详情加载完成')
  } catch (error) {
    console.error('加载项目详情失败:', error)
    ElMessage.error('加载项目详情失败')
  } finally {
    loading.value = false
  }
}

// 项目状态类型映射
const getStatusType = (status) => {
  const typeMap = {
    'planning': 'info',
    'in_progress': 'warning',
    'completed': 'success',
    'on_hold': 'danger',
    'cancelled': 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'planning': '规划中',
    'in_progress': '进行中',
    'completed': '已完成',
    'on_hold': '暂停',
    'cancelled': '已取消'
  }
  return textMap[status] || status
}

// 项目类型文本转换
const getProjectTypeText = (projectType) => {
  const textMap = {
    'internal': '内部项目',
    'client': '客户项目',
    'rd': '研发项目',
    'maintenance': '维护项目'
  }
  return textMap[projectType] || projectType || '未设置'
}

// 优先级类型映射
const getPriorityType = (priority) => {
  const typeMap = {
    'Critical': 'danger',
    'High': 'warning',
    'Medium': 'primary',
    'Low': 'info'
  }
  return typeMap[priority] || 'info'
}

const getPriorityText = (priority) => {
  const textMap = {
    'Critical': '紧急',
    'High': '高',
    'Medium': '中',
    'Low': '低'
  }
  return textMap[priority] || priority || '未设置'
}

// 质量类型映射
const getQualityType = (quality) => {
  const typeMap = {
    'Excellent': 'success',
    'Good': 'success',
    'Fair': 'warning',
    'Poor': 'danger'
  }
  return typeMap[quality] || 'info'
}

const getQualityText = (quality) => {
  const textMap = {
    'Excellent': '优秀',
    'Good': '良好',
    'Fair': '一般',
    'Poor': '差'
  }
  return textMap[quality] || quality || '未设置'
}

// 风险类型映射
const getRiskType = (risk) => {
  const typeMap = {
    'High': 'danger',
    'Medium': 'warning',
    'Low': 'success'
  }
  return typeMap[risk] || 'info'
}

const getRiskText = (risk) => {
  const textMap = {
    'High': '高',
    'Medium': '中',
    'Low': '低'
  }
  return textMap[risk] || risk || '未设置'
}

// 资源类型映射
const getResourceType = (resource) => {
  const typeMap = {
    '充足': 'success',
    '紧张': 'warning',
    '不足': 'danger'
  }
  return typeMap[resource] || 'info'
}

// 解析标签
const parseTags = (tags) => {
  if (!tags) return []
  if (typeof tags === 'string') {
    return tags.split(',').map(t => t.trim()).filter(t => t)
  }
  return []
}

// 解析里程碑
const parseMilestones = (milestones) => {
  if (!milestones) return []
  if (typeof milestones === 'string') {
    return milestones.split('\n').map(m => m.trim()).filter(m => m)
  }
  return []
}

// 角色类型映射
const getRoleType = (role) => {
  const typeMap = {
    'manager': 'danger',
    'project_manager': 'warning',
    'software_engineer': 'success',
    'test_engineer': 'info'
  }
  return typeMap[role] || 'info'
}

const getRoleText = (role) => {
  const textMap = {
    'manager': '系统管理员',
    'project_manager': '项目经理',
    'software_engineer': '软件工程师',
    'test_engineer': '测试工程师'
  }
  return textMap[role] || role
}

onMounted(() => {
  loadProjectDetail()
})
</script>

<style scoped>
.project-detail {
  padding: 20px;
}

.project-info-card {
  margin-bottom: 20px;
}

.project-tech-card {
  margin-bottom: 20px;
}

.project-client-card {
  margin-bottom: 20px;
}

.text-muted {
  color: #909399;
  font-style: italic;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.milestones-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.milestone-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.milestone-item .el-icon {
  color: #409EFF;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.project-title {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.project-intro-card {
  margin-bottom: 20px;
}

.project-versions-card {
  margin-bottom: 20px;
}

.versions-empty {
  min-height: auto;
}

.versions-empty .el-card__body {
  padding: 8px 20px;
  min-height: auto;
}

.versions-empty .el-empty {
  padding: 10px 0;
}

.versions-empty .el-empty__description {
  margin-top: 0;
  padding: 0;
}

.versions-empty .el-empty__description p {
  font-size: 13px;
  margin: 0;
}

.versions-table-container {
  padding: 10px 0;
}

.project-modules-card {
  margin-bottom: 20px;
}

.modules-empty {
  min-height: auto;
}

.modules-empty .el-card__body {
  padding: 8px 20px;
  min-height: auto;
}

.modules-empty .el-empty {
  padding: 10px 0;
}

.modules-empty .el-empty__description {
  margin-top: 0;
  padding: 0;
}

.modules-empty .el-empty__description p {
  font-size: 13px;
  margin: 0;
}

.modules-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px 0;
}

.module-tag {
  cursor: pointer;
  font-size: 14px;
}

.module-tag:hover {
  opacity: 0.8;
}

.project-intro-content {
  padding: 10px 0;
  line-height: 1.6;
  color: #606266;
}

.project-subfunctions-card {
  margin-bottom: 20px;
  position: sticky;
  top: 20px;
}

.subfunctions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.subfunction-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.subfunction-item:hover {
  background-color: #ecf5ff;
  transform: translateX(4px);
}

.subfunction-icon {
  font-size: 28px;
  color: #409EFF;
  margin-right: 15px;
}

.subfunction-info {
  flex: 1;
}

.subfunction-title {
  font-size: 15px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.subfunction-count {
  font-size: 13px;
  color: #909399;
}

.arrow-icon {
  font-size: 16px;
  color: #c0c4cc;
  transition: all 0.3s;
}

.subfunction-item:hover .arrow-icon {
  color: #409EFF;
  transform: translateX(4px);
}

.project-members-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #303133;
}

.member-count {
  font-size: 14px;
  color: #909399;
  margin-left: 10px;
  font-weight: normal;
}

.user-link {
  color: #409EFF;
  text-decoration: none;
  font-weight: 500;
}

.user-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.bug-stats-card {
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.severity-section,
.priority-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.severity-section h3,
.priority-section h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
}

.severity-item,
.priority-item {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.severity-label,
.priority-label {
  margin-right: 10px;
}

.severity-value,
.priority-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

@media screen and (max-width: 768px) {
  .project-detail {
    padding: 12px;
  }

  .project-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 12px;
  }

  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    width: 100%;
  }

  .project-title {
    font-size: 18px;
    word-break: break-all;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 80px;
    max-width: calc(50% - 4px);
    font-size: 12px;
    padding: 8px 12px;
  }

  .project-info-card,
  .project-tech-card,
  .project-client-card,
  .project-intro-card,
  .project-versions-card,
  .project-modules-card,
  .project-members-card,
  .bug-stats-card,
  .project-subfunctions-card {
    margin-bottom: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    font-size: 14px;
  }

  .card-header .el-dropdown {
    width: 100%;
  }

  .card-header .el-dropdown__trigger {
    width: 100%;
    justify-content: space-between;
  }

  .tags-container {
    flex-wrap: wrap;
    gap: 4px;
  }

  .tag-item {
    font-size: 11px;
    padding: 2px 6px;
  }

  .milestone-item {
    padding: 6px;
    font-size: 12px;
  }

  .milestone-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .milestone-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .milestone-actions .el-button {
    font-size: 11px;
    padding: 4px 8px;
  }

  .version-item {
    padding: 10px;
  }

  .version-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .version-title {
    font-size: 14px;
  }

  .version-info {
    font-size: 11px;
    flex-wrap: wrap;
    gap: 4px;
  }

  .version-progress {
    width: 100%;
    margin-top: 8px;
  }

  .module-item {
    padding: 12px;
  }

  .module-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .module-icon {
    margin-right: 0;
    margin-bottom: 4px;
  }

  .module-title {
    font-size: 14px;
  }

  .module-description {
    font-size: 12px;
  }

  .module-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 6px;
  }

  .module-actions .el-button {
    flex: 1;
    min-width: 70px;
    font-size: 11px;
    padding: 6px 8px;
  }

  .member-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding: 12px;
  }

  .member-info {
    width: 100%;
  }

  .member-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: flex-start;
  }

  .member-actions .el-button {
    flex: none;
    font-size: 11px;
    padding: 4px 8px;
  }

  .stat-card {
    height: auto;
    min-height: 80px;
    padding: 12px;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-label {
    font-size: 12px;
  }

  .stats-row .el-col {
    width: 50%;
    max-width: 50%;
    flex: 0 0 50%;
    margin-bottom: 12px;
  }

  .subfunction-item {
    padding: 12px;
  }

  .subfunction-icon {
    font-size: 22px;
    margin-right: 10px;
  }

  .subfunction-title {
    font-size: 14px;
  }

  .subfunction-count {
    font-size: 12px;
  }

  .el-descriptions {
    font-size: 12px;
  }

  .el-descriptions-item {
    display: block !important;
  }

  .el-descriptions-item__label {
    width: 100% !important;
    padding: 4px !important;
  }

  .el-descriptions-item__content {
    width: 100% !important;
    padding: 4px !important;
  }

  .info-grid {
    flex-direction: column;
  }

  .info-item {
    width: 100%;
    padding: 8px 0;
  }

  .tech-tags {
    flex-wrap: wrap;
    gap: 4px;
  }

  .tech-tag {
    font-size: 11px;
    padding: 2px 6px;
  }

  .client-logo {
    width: 60px;
    height: 60px;
  }

  .client-info {
    flex-direction: column;
    gap: 4px;
  }

  .client-name {
    font-size: 14px;
  }

  .client-detail {
    font-size: 12px;
  }

  .intro-content {
    font-size: 13px;
    line-height: 1.6;
  }

  .bug-stat-item {
    padding: 10px;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .bug-stat-header {
    width: 100%;
    flex-wrap: wrap;
    gap: 4px;
  }

  .bug-stat-value {
    font-size: 18px;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
    max-height: 90vh !important;
  }

  .el-dialog__header {
    padding: 12px !important;
  }

  .el-dialog__body {
    padding: 12px !important;
    max-height: 60vh !important;
    overflow-y: auto !important;
  }

  .el-dialog__footer {
    padding: 12px !important;
  }

  .form-section {
    padding: 12px;
  }

  .form-section-title {
    font-size: 14px;
    margin-bottom: 12px;
  }

  .form-actions {
    flex-wrap: wrap;
    gap: 8px;
  }

  .form-actions .el-button {
    flex: 1;
    min-width: 80px;
  }
}

@media screen and (max-width: 480px) {
  .project-detail {
    padding: 8px;
  }

  .project-header {
    margin-bottom: 12px;
    padding-bottom: 10px;
  }

  .project-title {
    font-size: 16px;
  }

  .header-actions .el-button {
    max-width: 100%;
    flex: none;
    width: 100%;
    font-size: 11px;
    padding: 6px 10px;
  }

  .stat-card {
    min-height: 70px;
    padding: 10px;
  }

  .stat-value {
    font-size: 18px;
  }

  .stat-label {
    font-size: 11px;
  }

  .stats-row .el-col {
    width: 50%;
    max-width: 50%;
    flex: 0 0 50%;
  }

  .module-item,
  .subfunction-item,
  .member-item {
    padding: 10px;
  }

  .module-actions .el-button,
  .member-actions .el-button {
    font-size: 10px;
    padding: 4px 6px;
  }

  .el-form-item {
    margin-bottom: 12px !important;
  }

  .el-input__inner,
  .el-textarea__inner {
    font-size: 14px !important;
  }
}
</style>