<template>
  <div class="project-detail-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-left">
          <el-page-header @back="$router.back()" class="custom-page-header">
            <template #content>
              <span class="header-title-text">项目详情</span>
            </template>
          </el-page-header>
          <div class="header-title">
            <div class="title-icon-wrapper">
              <el-icon class="title-icon"><Folder /></el-icon>
            </div>
            <div class="title-text">
              <h1>{{ project.name }}</h1>
              <p class="subtitle">{{ getProjectTypeText(project.project_type) }} · {{ getStatusText(project.status) }}</p>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <el-tag :type="getStatusType(project.status)" size="large" effect="light" class="status-tag">
            {{ getStatusText(project.status) }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-total">
            <div class="stat-icon-wrapper stat-icon-wrapper-total">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ bugStats.total || 0 }}</div>
              <div class="stat-label">Bug总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-open">
            <div class="stat-icon-wrapper stat-icon-wrapper-open">
              <el-icon><CircleClose /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ bugStats.open || 0 }}</div>
              <div class="stat-label">未解决</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-progress">
            <div class="stat-icon-wrapper stat-icon-wrapper-progress">
              <el-icon><Loading /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ bugStats.in_progress || 0 }}</div>
              <div class="stat-label">进行中</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card stat-card-closed">
            <div class="stat-icon-wrapper stat-icon-wrapper-closed">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ bugStats.closed || 0 }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6" :lg="6" class="member-stat-col">
          <div class="stat-card stat-card-members">
            <div class="stat-icon-wrapper stat-icon-wrapper-members">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ members.length || 0 }}</div>
              <div class="stat-label">成员数</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- Tab 标签页 -->
    <div class="tabs-section animate-fade-in-up delay-200">
      <div class="custom-tabs">
        <div 
          v-for="tab in tabs" 
          :key="tab.key"
          :class="['tab-item', { active: activeTab === tab.key }]"
          @click="activeTab = tab.key"
        >
          <el-icon class="tab-icon"><component :is="tab.icon" /></el-icon>
          <span class="tab-label">{{ tab.label }}</span>
        </div>
      </div>
    </div>

    <el-row :gutter="20" class="content-row animate-fade-in-up delay-300">
      <el-col :span="16">
        <!-- 项目概览 Tab -->
        <template v-if="activeTab === 'overview'">
          <el-card class="project-info-card glass-card" shadow="hover">
            <div class="project-header">
              <h2 class="project-title">{{ project.name }}</h2>
              <el-tag :type="getStatusType(project.status)" size="large">{{ getStatusText(project.status) }}</el-tag>
            </div>

            <el-descriptions :column="2" border class="custom-descriptions">
              <el-descriptions-item label="项目ID">{{ project.id }}</el-descriptions-item>
              <el-descriptions-item label="项目代码">{{ project.code || '未知' }}</el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ formatDate(project.created_at) }}</el-descriptions-item>
              <el-descriptions-item label="更新时间">{{ formatDate(project.updated_at) }}</el-descriptions-item>
              <el-descriptions-item label="项目状态" :span="2">{{ getStatusText(project.status) }}</el-descriptions-item>
              <el-descriptions-item label="项目类型" :span="2">{{ getProjectTypeText(project.project_type) }}</el-descriptions-item>
              <el-descriptions-item label="项目经理">{{ project.manager_name || '未知' }}</el-descriptions-item>
              <el-descriptions-item label="当前阶段">{{ project.current_stage || '未知' }}</el-descriptions-item>
              <el-descriptions-item label="进度" :span="2">
                <el-progress :percentage="project.progress || 0" :show-text="true" :stroke-width="16" class="custom-progress" />
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

          <el-card class="project-tech-card glass-card" shadow="hover">
            <div class="tech-stack-info">
              <span class="tech-label">技术栈：</span>
              <span class="tech-value">{{ project.technology_stack || '未设置' }}</span>
            </div>
          </el-card>

          <el-card class="project-client-card glass-card" shadow="hover" v-if="project.client_name || project.project_type === 'client'">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><OfficeBuilding /></el-icon>
                  客户信息
                </span>
              </div>
            </template>

            <el-descriptions :column="2" border class="custom-descriptions">
              <el-descriptions-item label="客户名称">{{ project.client_name || '未设置' }}</el-descriptions-item>
              <el-descriptions-item label="客户联系方式">{{ project.client_contact || '未设置' }}</el-descriptions-item>
            </el-descriptions>
          </el-card>

          <el-card class="project-finance-card glass-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Money /></el-icon>
                  财务与资源信息
                </span>
              </div>
            </template>

            <el-descriptions :column="3" border class="custom-descriptions">
              <el-descriptions-item label="预算">{{ project.budget ? `¥${parseFloat(project.budget).toLocaleString()}` : '未设置' }}</el-descriptions-item>
              <el-descriptions-item label="实际成本">{{ project.actual_cost ? `¥${parseFloat(project.actual_cost).toLocaleString()}` : '未设置' }}</el-descriptions-item>
              <el-descriptions-item label="合同金额">{{ project.contract_value ? `¥${parseFloat(project.contract_value).toLocaleString()}` : '未设置' }}</el-descriptions-item>
              <el-descriptions-item label="预估工时">{{ project.estimated_hours || 0 }}小时</el-descriptions-item>
              <el-descriptions-item label="实际工时">{{ project.actual_hours || 0 }}小时</el-descriptions-item>
              <el-descriptions-item label="团队规模">{{ project.team_size || 0 }}人</el-descriptions-item>
            </el-descriptions>
          </el-card>

          <el-card class="project-intro-card glass-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Document /></el-icon>
                  项目介绍
                </span>
              </div>
            </template>
            <div class="project-intro-content">
              {{ project.description || '暂无项目介绍' }}
            </div>
          </el-card>
        </template>

        <!-- 版本管理 Tab -->
        <template v-if="activeTab === 'versions'">
          <el-card class="project-versions-card glass-card" :class="{ 'versions-empty': versions.length === 0 }" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Collection /></el-icon>
                  项目版本
                </span>
                <span class="member-count">(共 {{ versions.length }} 个版本)</span>
                <el-button type="primary" size="small" :icon="Plus" @click="addVersion" class="btn-gradient">
                  添加版本
                </el-button>
              </div>
            </template>

            <div v-if="versions.length > 0" class="versions-table-container">
              <el-table :data="versions" style="width: 100%" stripe class="custom-table">
                <el-table-column prop="name" label="版本名称" width="150">
                  <template #default="{ row }">
                    <el-tag type="primary" effect="light" class="version-tag">{{ row.name || '未命名' }}</el-tag>
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
        </template>

        <!-- 模块管理 Tab -->
        <template v-if="activeTab === 'modules'">
          <el-card class="project-modules-card glass-card" :class="{ 'modules-empty': modules.length === 0 }" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Grid /></el-icon>
                  项目模块
                </span>
                <span class="member-count">(共 {{ modules.length }} 个模块)</span>
                <el-button type="primary" size="small" :icon="Plus" @click="addModule" class="btn-gradient">
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
                effect="light"
              >
                {{ module.name }}
              </el-tag>
            </div>
            <el-empty v-else description="暂无模块信息，点击添加模块" :image-size="80" />
          </el-card>
        </template>

        <!-- 成员管理 Tab -->
        <template v-if="activeTab === 'members'">
          <el-card class="project-members-card glass-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><UserFilled /></el-icon>
                  参与人员
                </span>
                <span class="member-count">(共 {{ members.length }} 人)</span>
              </div>
            </template>

            <el-table :data="members" style="width: 100%" stripe class="custom-table">
              <el-table-column prop="user_id" label="用户ID" width="100" align="center">
                <template #default="{ row }">
                  <span class="id-badge">#{{ row.user_id }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="username" label="用户名" width="150">
                <template #default="{ row }">
                  <router-link :to="'/users/' + row.user_id" class="user-link">
                    {{ row.username }}
                  </router-link>
                </template>
              </el-table-column>
              <el-table-column prop="position" label="职位" width="120">
                <template #default="{ row }">
                  <el-tag effect="light" size="small">{{ row.position || '未设置' }}</el-tag>
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
        </template>

        <!-- 缺陷统计 Tab -->
        <template v-if="activeTab === 'bugs'">
          <el-card class="bug-stats-card glass-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><WarningFilled /></el-icon>
                  缺陷报告统计
                </span>
              </div>
            </template>

            <el-row :gutter="20" class="stats-row-inner">
              <el-col :span="6">
                <div class="mini-stat-card mini-stat-total">
                  <div class="mini-stat-value">{{ bugStats.total || 0 }}</div>
                  <div class="mini-stat-label">总缺陷数</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="mini-stat-card mini-stat-open">
                  <div class="mini-stat-value">{{ bugStats.open || 0 }}</div>
                  <div class="mini-stat-label">未解决</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="mini-stat-card mini-stat-progress">
                  <div class="mini-stat-value">{{ bugStats.in_progress || 0 }}</div>
                  <div class="mini-stat-label">处理中</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="mini-stat-card mini-stat-closed">
                  <div class="mini-stat-value">{{ bugStats.closed || 0 }}</div>
                  <div class="mini-stat-label">已关闭</div>
                </div>
              </el-col>
            </el-row>

            <div class="severity-section">
              <h3 class="section-title">
                <el-icon><Warning /></el-icon>
                严重程度分布
              </h3>
              <el-row :gutter="20">
                <el-col :span="6">
                  <div class="severity-item severity-critical">
                    <div class="severity-label">
                      <el-tag type="danger" effect="dark">严重</el-tag>
                    </div>
                    <div class="severity-value">{{ bugStats.severity?.critical || 0 }}</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="severity-item severity-high">
                    <div class="severity-label">
                      <el-tag type="warning" effect="dark">高</el-tag>
                    </div>
                    <div class="severity-value">{{ bugStats.severity?.high || 0 }}</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="severity-item severity-medium">
                    <div class="severity-label">
                      <el-tag type="info" effect="dark">中</el-tag>
                    </div>
                    <div class="severity-value">{{ bugStats.severity?.medium || 0 }}</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="severity-item severity-low">
                    <div class="severity-label">
                      <el-tag type="success" effect="dark">低</el-tag>
                    </div>
                    <div class="severity-value">{{ bugStats.severity?.low || 0 }}</div>
                  </div>
                </el-col>
              </el-row>
            </div>

            <div class="priority-section">
              <h3 class="section-title">
                <el-icon><Flag /></el-icon>
                优先级分布
              </h3>
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="priority-item priority-high">
                    <div class="priority-label">
                      <el-tag type="danger" effect="dark">高</el-tag>
                    </div>
                    <div class="priority-value">{{ bugStats.priority?.high || 0 }}</div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="priority-item priority-medium">
                    <div class="priority-label">
                      <el-tag type="warning" effect="dark">中</el-tag>
                    </div>
                    <div class="priority-value">{{ bugStats.priority?.medium || 0 }}</div>
                </div>
                </el-col>
                <el-col :span="8">
                  <div class="priority-item priority-low">
                    <div class="priority-label">
                      <el-tag type="success" effect="dark">低</el-tag>
                    </div>
                    <div class="priority-value">{{ bugStats.priority?.low || 0 }}</div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-card>
        </template>
      </el-col>

      <el-col :span="8">
        <el-card class="project-subfunctions-card glass-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Menu /></el-icon>
                项目子功能
              </span>
            </div>
          </template>

          <div class="subfunctions-list">
            <div class="subfunction-item" @click="navigateToSubfunction('bugs')">
              <div class="subfunction-icon-wrapper">
                <el-icon class="subfunction-icon"><Warning /></el-icon>
              </div>
              <div class="subfunction-info">
                <div class="subfunction-title">缺陷管理</div>
                <div class="subfunction-count">{{ bugStats.total || 0 }} 个缺陷</div>
              </div>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </div>
            <div class="subfunction-item" @click="navigateToSubfunction('requirements')">
              <div class="subfunction-icon-wrapper icon-requirements">
                <el-icon class="subfunction-icon"><Document /></el-icon>
              </div>
              <div class="subfunction-info">
                <div class="subfunction-title">需求管理</div>
                <div class="subfunction-count">需求集管理</div>
              </div>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </div>
            <div class="subfunction-item" @click="navigateToSubfunction('tests')">
              <div class="subfunction-icon-wrapper icon-tests">
                <el-icon class="subfunction-icon"><CircleCheck /></el-icon>
              </div>
              <div class="subfunction-info">
                <div class="subfunction-title">测试管理</div>
                <div class="subfunction-count">测试集与用例管理</div>
              </div>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </div>
            <div class="subfunction-item" @click="navigateToSubfunction('risks')">
              <div class="subfunction-icon-wrapper icon-risks">
                <el-icon class="subfunction-icon"><WarningFilled /></el-icon>
              </div>
              <div class="subfunction-info">
                <div class="subfunction-title">风险管理</div>
                <div class="subfunction-count">风险与问题管理</div>
              </div>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </div>
            <div class="subfunction-item" @click="navigateToSubfunction('logs')">
              <div class="subfunction-icon-wrapper icon-logs">
                <el-icon class="subfunction-icon"><Timer /></el-icon>
              </div>
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
  <el-dialog v-model="showVersionDialog" :title="versionDialogTitle" width="500px" class="custom-dialog">
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
      <el-button type="primary" @click="saveVersion" :loading="versionLoading" class="btn-gradient">保存</el-button>
    </template>
  </el-dialog>
  
  <!-- 添加/编辑模块对话框 -->
  <el-dialog v-model="showModuleDialog" :title="moduleDialogTitle" width="400px" class="custom-dialog">
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
      <el-button type="primary" @click="saveModule" :loading="moduleLoading" class="btn-gradient">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Document, CircleCheck, Warning, Plus, Edit, Delete, Flag, ArrowRight, 
  Folder, User, CircleClose, Loading, UserFilled, WarningFilled, 
  Collection, Grid, Menu, OfficeBuilding, Money, Timer 
} from '@element-plus/icons-vue'
import { apiService } from '@/services/api'
import bugStatisticsService from '@/services/bugStatisticsService'
import { formatDate } from '@/utils/dateUtils'

console.log('===== ProjectDetail组件加载 =====')

const route = useRoute()
const router = useRouter()
const projectId = route.params.id

// Tab 配置
const tabs = [
  { key: 'overview', label: '项目概览', icon: 'Document' },
  { key: 'versions', label: '版本管理', icon: 'Collection' },
  { key: 'modules', label: '模块管理', icon: 'Grid' },
  { key: 'members', label: '成员管理', icon: 'UserFilled' },
  { key: 'bugs', label: '缺陷统计', icon: 'WarningFilled' },
]
const activeTab = ref('overview')

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
      router.push(`/projects/${projectId}/risks`)
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

// 获取项目缺陷统计数据
const fetchProjectBugStats = async () => {
  try {
    const result = await bugStatisticsService.getProjectStats(projectId.value || projectId)
    if (result.success && result.data) {
      const data = result.data
      bugStats.value = {
        total: data.status_summary?.total || 0,
        open: data.status_summary?.open || 0,
        in_progress: data.status_summary?.in_progress || 0,
        closed: data.status_summary?.closed || 0,
        severity: {
          critical: data.severity_distribution?.critical || 0,
          high: data.severity_distribution?.high || 0,
          medium: data.severity_distribution?.medium || 0,
          low: data.severity_distribution?.low || 0
        },
        priority: {
          high: data.priority_distribution?.high || 0,
          medium: data.priority_distribution?.medium || 0,
          low: data.priority_distribution?.low || 0
        }
      }
    }
  } catch (error) {
    console.error('获取项目缺陷统计数据失败:', error)
    bugStats.value = {
      total: 0,
      open: 0,
      in_progress: 0,
      closed: 0,
      severity: { critical: 0, high: 0, medium: 0, low: 0 },
      priority: { high: 0, medium: 0, low: 0 }
    }
  }
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

    // 获取项目缺陷统计数据
    await fetchProjectBugStats()

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
    'active': 'success',
    'inprogress': 'warning',
    'completed': 'success',
    'on_hold': 'danger',
    'paused': 'warning',
    'cancelled': 'danger',
    'archived': 'info'
  }
  return typeMap[status?.toLowerCase()] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'planning': '规划中',
    'in_progress': '进行中',
    'active': '进行中',
    'inprogress': '进行中',
    'completed': '已完成',
    'on_hold': '暂停',
    'paused': '暂停',
    'cancelled': '已取消',
    'archived': '已归档'
  }
  const key = status?.toLowerCase()
  return textMap[key] || status || '未设置'
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
    'critical': 'danger',
    'urgent': 'danger',
    'high': 'warning',
    'medium': 'primary',
    'normal': 'primary',
    'low': 'info'
  }
  return typeMap[priority?.toLowerCase()] || 'info'
}

const getPriorityText = (priority) => {
  const textMap = {
    'critical': '紧急',
    'urgent': '紧急',
    'high': '高',
    'medium': '中',
    'normal': '中',
    'low': '低'
  }
  const key = priority?.toLowerCase()
  return textMap[key] || priority || '未设置'
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
/* 导入设计系统 */
@import '@/styles/design-system.css';

.project-detail-container {
  padding: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
  min-height: 100%;
}

/* 页面头部 - 玻璃拟态风格 */
.page-header {
  position: relative;
  margin-bottom: 24px;
  padding: 28px 32px;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px -10px rgba(56, 189, 248, 0.4);
}

.page-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at top right, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse at bottom left, rgba(14, 165, 233, 0.3) 0%, transparent 50%);
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

.header-left {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.custom-page-header {
  color: white;
}

.custom-page-header :deep(.el-page-header__left) {
  color: rgba(255, 255, 255, 0.9);
}

.custom-page-header :deep(.el-page-header__content) {
  color: white;
}

.header-title-text {
  font-size: 14px;
  font-weight: 500;
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

.header-actions {
  display: flex;
  gap: 12px;
}

.status-tag {
  font-size: 14px;
  padding: 8px 16px;
  border-radius: 8px;
}

/* 统计卡片区域 */
.stats-row {
  margin-bottom: 24px;
}

.member-stat-col {
  margin-top: 16px;
}

.stat-card {
  position: relative;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.stat-card::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  transform: scaleX(0);
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.15), 0 10px 20px -5px rgba(0, 0, 0, 0.1);
}

.stat-card:hover::before {
  transform: scaleX(1);
}

/* 5种不同的渐变配色 */
.stat-card-total::before { background: linear-gradient(90deg, #7dd3fc, #38bdf8); }
.stat-card-open::before { background: linear-gradient(90deg, #ef4444, #f87171); }
.stat-card-progress::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-closed::before { background: linear-gradient(90deg, #10b981, #34d399); }
.stat-card-members::before { background: linear-gradient(90deg, #3b82f6, #60a5fa); }

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: all 0.4s;
}

.stat-card:hover .stat-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.stat-icon-wrapper-total {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #7dd3fc;
  box-shadow: 0 4px 15px -3px rgba(56, 189, 248, 0.4);
}

.stat-icon-wrapper-open {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
  box-shadow: 0 4px 15px -3px rgba(239, 68, 68, 0.4);
}

.stat-icon-wrapper-progress {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-closed {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-members {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #2563eb;
  box-shadow: 0 4px 15px -3px rgba(59, 130, 246, 0.4);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 26px;
  font-weight: 800;
  line-height: 1.2;
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-card-total .stat-value {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-open .stat-value {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-progress .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-closed .stat-value {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-members .stat-value {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
}

/* Tab 标签页 */
.tabs-section {
  margin-bottom: 24px;
}

.custom-tabs {
  display: flex;
  gap: 8px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  padding: 6px;
  border-radius: 14px;
  border: 1px solid rgba(226, 232, 240, 0.6);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: #64748b;
  font-weight: 500;
  font-size: 14px;
}

.tab-item:hover {
  background: rgba(56, 189, 248, 0.08);
  color: #0ea5e9;
}

.tab-item.active {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  color: white;
  box-shadow: 0 4px 12px -2px rgba(56, 189, 248, 0.4);
}

.tab-icon {
  font-size: 16px;
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
  margin-bottom: 20px;
}

.glass-card:hover {
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.12), 0 10px 20px -5px rgba(0, 0, 0, 0.08);
}

.glass-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
}

.card-title .el-icon {
  color: #0ea5e9;
  font-size: 18px;
}

.member-count {
  font-size: 14px;
  color: #909399;
  margin-left: 10px;
  font-weight: normal;
}

/* 项目信息卡片 */
.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.project-title {
  margin: 0;
  color: #1e293b;
  font-size: 22px;
  font-weight: 700;
}

/* 自定义描述列表 */
.custom-descriptions :deep(.el-descriptions__label) {
  background: rgba(241, 245, 249, 0.8);
  font-weight: 600;
  color: #475569;
}

.custom-descriptions :deep(.el-descriptions__content) {
  color: #1e293b;
}

/* 自定义进度条 */
.custom-progress :deep(.el-progress-bar__outer) {
  background-color: rgba(226, 232, 240, 0.6);
  border-radius: 8px;
}

.custom-progress :deep(.el-progress-bar__inner) {
  background: linear-gradient(90deg, #7dd3fc 0%, #38bdf8 100%);
  border-radius: 8px;
}

/* 技术栈卡片 */
.tech-stack-info {
  font-size: 14px;
  line-height: 1.6;
  padding: 10px 0;
}

.tech-label {
  font-weight: 600;
  color: #475569;
}

.tech-value {
  color: #1e293b;
  background: rgba(56, 189, 248, 0.08);
  padding: 4px 12px;
  border-radius: 6px;
}

/* 项目介绍 */
.project-intro-content {
  padding: 10px 0;
  line-height: 1.8;
  color: #475569;
  font-size: 14px;
}

/* 版本管理 */
.versions-empty {
  min-height: auto;
}

.versions-empty :deep(.el-card__body) {
  padding: 8px 20px;
  min-height: auto;
}

.versions-empty :deep(.el-empty) {
  padding: 10px 0;
}

.versions-table-container {
  padding: 10px 0;
}

.version-tag {
  font-weight: 500;
  border-radius: 6px;
}

/* 模块管理 */
.modules-empty {
  min-height: auto;
}

.modules-empty :deep(.el-card__body) {
  padding: 8px 20px;
  min-height: auto;
}

.modules-empty :deep(.el-empty) {
  padding: 10px 0;
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
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s;
}

.module-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 成员管理 */
.id-badge {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #64748b;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
}

.user-link {
  color: #0ea5e9;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s;
}

.user-link:hover {
  color: #0284c7;
  text-decoration: underline;
}

/* 自定义表格 */
.custom-table {
  --el-table-header-bg-color: rgba(241, 245, 249, 0.8);
  --el-table-row-hover-bg-color: rgba(56, 189, 248, 0.05);
}

.custom-table :deep(.el-table__header th) {
  font-weight: 600;
  color: #1e293b;
  background: rgba(241, 245, 249, 0.8);
}

.custom-table :deep(.el-table__row) {
  transition: all 0.3s;
}

/* 缺陷统计 */
.stats-row-inner {
  margin-bottom: 24px;
}

.mini-stat-card {
  text-align: center;
  padding: 20px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(226, 232, 240, 0.6);
  transition: all 0.3s;
}

.mini-stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.mini-stat-total {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(14, 165, 233, 0.1) 100%);
  border-color: rgba(56, 189, 248, 0.3);
}

.mini-stat-open {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(248, 113, 113, 0.1) 100%);
  border-color: rgba(239, 68, 68, 0.3);
}

.mini-stat-progress {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 191, 36, 0.1) 100%);
  border-color: rgba(245, 158, 11, 0.3);
}

.mini-stat-closed {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(52, 211, 153, 0.1) 100%);
  border-color: rgba(16, 185, 129, 0.3);
}

.mini-stat-value {
  font-size: 28px;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 4px;
}

.mini-stat-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.severity-section,
.priority-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(226, 232, 240, 0.6);
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #1e293b;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title .el-icon {
  color: #0ea5e9;
}

.severity-item,
.priority-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 16px;
  border-radius: 10px;
  transition: all 0.3s;
}

.severity-item:hover,
.priority-item:hover {
  transform: translateY(-2px);
}

.severity-critical {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(248, 113, 113, 0.1) 100%);
}

.severity-high {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 191, 36, 0.1) 100%);
}

.severity-medium {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(129, 140, 248, 0.1) 100%);
}

.severity-low {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(52, 211, 153, 0.1) 100%);
}

.priority-high {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(248, 113, 113, 0.1) 100%);
}

.priority-medium {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 191, 36, 0.1) 100%);
}

.priority-low {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(52, 211, 153, 0.1) 100%);
}

.severity-value,
.priority-value {
  font-size: 24px;
  font-weight: 800;
  color: #1e293b;
}

/* 子功能卡片 */
.project-subfunctions-card {
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
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.subfunction-item:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.subfunction-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 14px;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  color: white;
  font-size: 20px;
}

.icon-requirements {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.icon-tests {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
}

.icon-risks {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
}

.icon-logs {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
}

.subfunction-icon {
  font-size: 20px;
}

.subfunction-info {
  flex: 1;
}

.subfunction-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.subfunction-count {
  font-size: 13px;
  color: #64748b;
}

.arrow-icon {
  font-size: 16px;
  color: #94a3b8;
  transition: all 0.3s;
}

.subfunction-item:hover .arrow-icon {
  color: #0ea5e9;
  transform: translateX(4px);
}

/* 按钮样式 */
.btn-gradient {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border: none;
  color: white;
  transition: all 0.3s;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.5);
}

/* 对话框样式 */
:deep(.custom-dialog .el-dialog__header) {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  padding: 20px;
  margin-right: 0;
}

:deep(.custom-dialog .el-dialog__title) {
  color: white;
  font-weight: 600;
}

:deep(.custom-dialog .el-dialog__headerbtn .el-dialog__close) {
  color: rgba(255, 255, 255, 0.8);
}

:deep(.custom-dialog .el-dialog__headerbtn:hover .el-dialog__close) {
  color: white;
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

/* 内容行 */
.content-row {
  margin-bottom: 20px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .project-detail-container {
    padding: 0;
  }

  .page-header {
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 16px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
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

  .stats-row {
    margin-bottom: 20px;
  }

  .member-stat-col {
    margin-top: 0;
  }

  .stat-card {
    padding: 16px;
    gap: 12px;
    margin-bottom: 12px;
  }

  .stat-icon-wrapper {
    width: 44px;
    height: 44px;
    border-radius: 12px;
  }

  .stat-value {
    font-size: 22px;
  }

  .stat-label {
    font-size: 12px;
  }

  .custom-tabs {
    flex-wrap: wrap;
    padding: 4px;
  }

  .tab-item {
    padding: 8px 14px;
    font-size: 13px;
  }

  .tab-icon {
    font-size: 14px;
  }

  .glass-card {
    margin-bottom: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .project-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .project-title {
    font-size: 18px;
  }

  .custom-descriptions :deep(.el-descriptions-item) {
    display: block !important;
  }

  .custom-descriptions :deep(.el-descriptions-item__label) {
    width: 100% !important;
    padding: 8px !important;
  }

  .custom-descriptions :deep(.el-descriptions-item__content) {
    width: 100% !important;
    padding: 8px !important;
  }

  .modules-tags {
    gap: 8px;
  }

  .module-tag {
    font-size: 13px;
    padding: 6px 12px;
  }

  .stats-row-inner .el-col {
    width: 50%;
    max-width: 50%;
    flex: 0 0 50%;
    margin-bottom: 12px;
  }

  .mini-stat-card {
    padding: 14px;
  }

  .mini-stat-value {
    font-size: 22px;
  }

  .severity-item,
  .priority-item {
    padding: 12px;
    height: auto;
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }

  .severity-value,
  .priority-value {
    font-size: 20px;
  }

  .project-subfunctions-card {
    position: static;
    margin-top: 20px;
  }

  .subfunction-item {
    padding: 12px;
  }

  .subfunction-icon-wrapper {
    width: 40px;
    height: 40px;
    margin-right: 10px;
  }

  .subfunction-icon {
    font-size: 18px;
  }

  .subfunction-title {
    font-size: 14px;
  }

  .subfunction-count {
    font-size: 12px;
  }

  .custom-table {
    font-size: 12px !important;
  }

  .custom-table :deep(.el-table th),
  .custom-table :deep(.el-table td) {
    padding: 8px 6px !important;
  }

  :deep(.custom-dialog) {
    width: 95% !important;
    margin: 10px auto !important;
  }
}

@media screen and (max-width: 480px) {
  .page-header {
    padding: 16px;
  }

  .title-text h1 {
    font-size: 20px;
  }

  .stat-card {
    padding: 14px;
  }

  .stat-value {
    font-size: 20px;
  }

  .tab-item {
    padding: 6px 10px;
    font-size: 12px;
  }

  .tab-label {
    display: none;
  }

  .custom-table {
    font-size: 11px !important;
  }
}
</style>
