<template>
  <div class="project-list">
    <div class="project-list-header">
      <h2>项目管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建项目
        </el-button>
        <el-dropdown @command="handleExportCommand" :disabled="exporting">
          <el-button type="success" :loading="exporting">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="csv">导出为CSV</el-dropdown-item>
              <el-dropdown-item command="excel">导出为Excel</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <!-- 状态灯颜色说明 -->
    <el-card class="status-legend-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>状态灯颜色说明</span>
        </div>
      </template>
      <div class="status-legend">
        <div class="legend-item">
          <div class="status-dot status-green"></div>
          <span>正常</span>
        </div>
        <div class="legend-item">
          <div class="status-dot status-yellow"></div>
          <span>警告</span>
        </div>
        <div class="legend-item">
          <div class="status-dot status-red"></div>
          <span>危险</span>
        </div>
        <div class="legend-item">
          <div class="status-dot status-gray"></div>
          <span>暂停</span>
        </div>
      </div>
    </el-card>
    
    <!-- 项目列表 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>项目列表</span>
          <div class="filter-controls">
            <el-input 
              v-model="filters.keyword" 
              placeholder="搜索项目名称、代码或描述" 
              style="width: 250px; margin-right: 10px;"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select v-model="filters.status" placeholder="状态筛选" clearable style="width: 120px;">
              <el-option label="活跃" value="active" />
              <el-option label="已完成" value="completed" />
              <el-option label="已关闭" value="closed" />
              <el-option label="已归档" value="archived" />
            </el-select>
            <el-select v-model="filters.project_type" placeholder="类型筛选" clearable style="width: 120px;">
              <el-option label="内部项目" value="internal" />
              <el-option label="客户项目" value="client" />
              <el-option label="研发项目" value="rd" />
              <el-option label="维护项目" value="maintenance" />
            </el-select>
          </div>
        </div>
      </template>
      
      <el-table :data="filteredProjects" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="编号" width="80" />
        
        <el-table-column prop="name" label="项目名称" min-width="200">
          <template #default="{ row }">
            <div class="project-name">
              <div class="status-dot" :class="getStatusClass(row.status)"></div>
              <el-button 
                type="primary" 
                link 
                size="small" 
                @click="viewProjectDetail(row)"
              >
                {{ row.name }}
              </el-button>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="manager" label="经理" width="150">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              link 
              size="small" 
              @click="viewManagerDetail(row.manager_id)"
              :disabled="!row.manager_id"
            >
              {{ row.manager }}
            </el-button>
          </template>
        </el-table-column>
        
        <el-table-column prop="project_type" label="项目类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getProjectTypeTag(row.project_type)" size="small">
              {{ getProjectTypeText(row.project_type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="budget" label="预算" width="120">
          <template #default="{ row }">
            {{ row.budget ? `¥${row.budget.toLocaleString()}` : '未设置' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="team_size" label="团队规模" width="100">
          <template #default="{ row }">
            <el-tag :type="getTeamSizeTag(row.team_size)" size="small">
              {{ row.team_size || 0 }}人
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="参与人员" width="200">
          <template #default="{ row }">
            <div class="project-members">
              <el-tooltip 
                v-for="member in row.members" 
                :key="member.user_id"
                :content="`${member.username} - ${member.role} - ${member.department}`"
                placement="top"
              >
                <el-button 
                  type="primary" 
                  link
                  size="small"
                  @click="viewMemberDetail(member.user_id)"
                  style="padding: 0; margin-right: 5px; margin-bottom: 5px;"
                >
                  <el-avatar 
                    :size="32" 
                    :src="getUserAvatar(member.username)"
                  >
                    {{ member.username.charAt(0).toUpperCase() }}
                  </el-avatar>
                </el-button>
              </el-tooltip>
              <el-button 
                v-if="row.members && row.members.length > 3" 
                type="primary" 
                link 
                size="small"
                @click="showAllMembers(row)"
              >
                +{{ row.members.length - 3 }}人
              </el-button>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="start_time" label="开始时间" width="120" />
        
        <el-table-column prop="end_time" label="结束时间" width="120" />
        
        <el-table-column prop="current_stage" label="当前阶段" width="120">
          <template #default="{ row }">
            {{ row.current_stage || (row.status === 'active' ? '进行中' : row.status === 'completed' ? '已完成' : row.status === 'closed' ? '已关闭' : row.status === 'archived' ? '已归档' : '未知') }}
          </template>
        </el-table-column>
        
        <el-table-column prop="progress" label="当前进度" width="100">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :show-text="false" />
            <span class="progress-text">{{ row.progress }}%</span>
          </template>
        </el-table-column>
        
        <el-table-column label="进展" width="80">
          <template #default="{ row }">
            <el-tag :type="getProgressType(row.progress)" size="small">
              {{ getProgressText(row.progress) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="质量" width="80">
          <template #default="{ row }">
            <el-tag :type="getQualityType(row.quality)" size="small">
              {{ row.quality }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="风险" width="80">
          <template #default="{ row }">
            <el-tag :type="getRiskType(row.risk)" size="small">
              {{ row.risk }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="资源" width="80">
          <template #default="{ row }">
            <el-tag :type="getResourceType(row.resources)" size="small">
              {{ row.resources }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="费用" width="80">
          <template #default="{ row }">
            <el-tag :type="getCostType(row.cost)" size="small">
              {{ row.cost }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editProject(row)">编辑</el-button>
            <el-button type="primary" link size="small" @click="viewProjectDetail(row)">查看</el-button>
            <el-button type="danger" link size="small" @click="deleteProject(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 新建/编辑项目对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      :title="editingProject ? '编辑项目' : '新建项目'" 
      width="600px"
    >
      <el-form :model="projectForm" label-width="120px">
        <el-form-item label="项目名称">
          <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目代码">
          <el-input v-model="projectForm.code" placeholder="请输入项目代码" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="projectForm.description" type="textarea" :rows="2" placeholder="请输入项目描述" />
        </el-form-item>
        <el-form-item label="项目类型">
          <el-select v-model="projectForm.project_type" placeholder="选择项目类型">
            <el-option label="内部项目" value="internal" />
            <el-option label="客户项目" value="client" />
            <el-option label="研发项目" value="rd" />
            <el-option label="维护项目" value="maintenance" />
          </el-select>
        </el-form-item>
        <el-form-item label="经理">
          <el-select v-model="projectForm.manager_id" placeholder="选择经理">
            <el-option 
              v-for="manager in managers" 
              :key="manager.id" 
              :label="manager.name" 
              :value="manager.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker 
            v-model="projectForm.start_date" 
            type="date" 
            placeholder="选择开始时间" 
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker 
            v-model="projectForm.end_date" 
            type="date" 
            placeholder="选择结束时间" 
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="当前阶段">
          <el-select v-model="projectForm.current_stage" placeholder="选择当前阶段">
            <el-option label="进行中" value="进行中" />
            <el-option label="已完成" value="已完成" />
            <el-option label="已暂停" value="已暂停" />
            <el-option label="已取消" value="已取消" />
          </el-select>
        </el-form-item>
        <el-form-item label="当前进度">
          <el-slider v-model="projectForm.progress" :show-tooltip="true" />
        </el-form-item>
        <el-form-item label="质量">
          <el-select v-model="projectForm.quality" placeholder="选择质量等级">
            <el-option label="优秀" value="Excellent" />
            <el-option label="良好" value="Good" />
            <el-option label="一般" value="Fair" />
            <el-option label="差" value="Poor" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险">
          <el-select v-model="projectForm.risk" placeholder="选择风险等级">
            <el-option label="低" value="Low" />
            <el-option label="中" value="Medium" />
            <el-option label="高" value="High" />
          </el-select>
        </el-form-item>
        <el-form-item label="资源">
          <el-select v-model="projectForm.resources" placeholder="选择资源状态">
            <el-option label="充足" value="充足" />
            <el-option label="紧张" value="紧张" />
            <el-option label="不足" value="不足" />
          </el-select>
        </el-form-item>
        <el-form-item label="费用">
          <el-select v-model="projectForm.cost" placeholder="选择费用状态">
            <el-option label="正常" value="normal" />
            <el-option label="超支" value="over" />
            <el-option label="节约" value="under" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目状态">
          <el-select v-model="projectForm.status" placeholder="选择项目状态">
            <el-option label="活跃" value="active" />
            <el-option label="已完成" value="completed" />
            <el-option label="已关闭" value="closed" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="projectForm.priority" placeholder="选择优先级">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="技术栈">
          <el-input v-model="projectForm.technology_stack" type="textarea" :rows="2" placeholder="请输入项目使用的技术栈" />
        </el-form-item>
        
        <el-form-item label="预算">
          <el-input-number v-model="projectForm.budget" :min="0" :step="1000" placeholder="请输入预算金额" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="实际成本">
          <el-input-number v-model="projectForm.actual_cost" :min="0" :step="1000" placeholder="请输入实际成本" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="合同金额">
          <el-input-number v-model="projectForm.contract_value" :min="0" :step="1000" placeholder="请输入合同金额" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="预估工时">
          <el-input-number v-model="projectForm.estimated_hours" :min="0" :step="8" placeholder="请输入预估工时" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="实际工时">
          <el-input-number v-model="projectForm.actual_hours" :min="0" :step="8" placeholder="请输入实际工时" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="团队规模">
          <el-input-number v-model="projectForm.team_size" :min="0" :step="1" placeholder="请输入团队人数" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="客户名称">
          <el-input v-model="projectForm.client_name" placeholder="请输入客户名称" />
        </el-form-item>
        
        <el-form-item label="客户联系方式">
          <el-input v-model="projectForm.client_contact" placeholder="请输入客户联系方式" />
        </el-form-item>
        
        <el-form-item label="标签">
          <el-input v-model="projectForm.tags" placeholder="请输入项目标签，多个标签用逗号分隔" />
        </el-form-item>
        
        <el-form-item label="里程碑">
          <el-input v-model="projectForm.milestones" type="textarea" :rows="3" placeholder="请输入项目里程碑，每个里程碑用换行分隔" />
        </el-form-item>
        
        <el-form-item label="参与人员">
          <el-select 
            v-model="selectedMembers" 
            multiple 
            filterable 
            placeholder="选择项目参与人员"
            style="width: 100%"
          >
            <el-option 
              v-for="user in allUsers" 
              :key="user.id" 
              :label="user.username" 
              :value="user.id" 
            />
          </el-select>
          <div style="margin-top: 8px; font-size: 12px; color: #909399;">
            已选择 {{ selectedMembers.length }} 名成员
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveProject">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 项目下有Bug和任务时的统一对话框 -->
    <el-dialog 
      v-model="showProjectItemsDialog" 
      title="项目下的Bug和任务列表" 
      width="900px"
      :close-on-click-modal="false"
    >
      <div v-if="currentProject">
        <p>项目 <strong>{{ currentProject.name }}</strong> 下还有未处理的内容，请先删除后再删除项目。</p>
        
        <el-tabs v-model="activeItemsTab" class="items-tabs">
          <el-tab-pane label="Bug列表" name="bugs" v-if="currentProject.bugs && currentProject.bugs.length > 0">
            <div class="list-actions">
              <el-button 
                type="danger" 
                :disabled="selectedBugIds.length === 0"
                @click="deleteSelectedBugs"
              >
                批量删除选中 ({{ selectedBugIds.length }})
              </el-button>
              <el-button @click="refreshBugList">
                刷新列表
              </el-button>
            </div>
            
            <el-table 
              :data="currentProject.bugs" 
              @selection-change="handleBugSelectionChange"
              style="width: 100%"
            >
              <el-table-column type="selection" width="55" />
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="title" label="Bug标题" min-width="200" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getBugStatusType(row.status)" size="small">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="priority" label="优先级" width="100">
                <template #default="{ row }">
                  <el-tag :type="getBugPriorityType(row.priority)" size="small">
                    {{ row.priority }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="{ row }">
                  <el-button type="danger" link size="small" @click="deleteBug(row.id)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          

        </el-tabs>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showProjectItemsDialog = false">关闭</el-button>
          <el-button 
            type="primary" 
            :disabled="(currentProject?.bugs?.length || 0) > 0"
            @click="retryDeleteProject"
          >
            确认删除项目
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- Bug列表对话框（单独显示时使用） -->
    <el-dialog 
      v-model="showBugListDialog" 
      title="项目下的Bug列表" 
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="currentProject" class="bug-list-container">
        <div class="bug-list-header">
          <p>项目 <strong>{{ currentProject.name }}</strong> 下还有 {{ currentProject.bugs?.length || 0 }} 个Bug未处理。</p>
          <p class="warning-text">请先删除这些Bug后再删除项目。</p>
        </div>
        
        <div class="bug-list-actions" v-if="currentProject.bugs && currentProject.bugs.length > 0">
          <el-button 
            type="danger" 
            :disabled="selectedBugIds.length === 0"
            @click="deleteSelectedBugs"
          >
            批量删除选中 ({{ selectedBugIds.length }})
          </el-button>
          <el-button @click="refreshBugList">
            刷新列表
          </el-button>
        </div>
        
        <el-table 
          :data="currentProject.bugs || []" 
          @selection-change="handleBugSelectionChange"
          style="width: 100%"
          v-loading="bugListLoading"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="title" label="Bug标题" min-width="200" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getBugStatusType(row.status)" size="small">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="优先级" width="100">
            <template #default="{ row }">
              <el-tag :type="getBugPriorityType(row.priority)" size="small">
                {{ row.priority }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="severity" label="严重程度" width="100">
            <template #default="{ row }">
              <el-tag :type="getBugSeverityType(row.severity)" size="small">
                {{ row.severity }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button type="danger" link size="small" @click="deleteBug(row.id)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showBugListDialog = false">关闭</el-button>
          <el-button 
            type="primary" 
            :disabled="currentProject?.bugs?.length > 0"
            @click="retryDeleteProject"
          >
            确认删除项目
          </el-button>
        </div>
      </template>
    </el-dialog>
    

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, toRaw } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Plus, Search, Download } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { apiService } from '@/services/api'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const showCreateDialog = ref(false)
const editingProject = ref(null)
const exporting = ref(false)

// 筛选条件
const filters = reactive({
  keyword: '',
  status: '',
  project_type: ''
})

// 项目数据
const projects = ref([])

// 检查当前用户是否为管理员
const isAdmin = computed(() => {
  const user = userStore.currentUser
  if (!user) return false
  if (user.is_super_admin) return true
  return user.position === '管理员' || user.position?.includes('经理')
})

// 项目表单
const projectForm = reactive({
  name: '',
  code: '',
  description: '',
  manager_id: null,
  start_date: '',
  end_date: '',
  current_stage: '',  // 当前阶段
  status: 'active',  // 项目状态，默认为活跃
  progress: 0,
  quality: 'Fair',  // 质量等级
  risk: 'Medium',   // 风险等级
  resources: '',  // 资源状态
  cost: null,  // 费用状态，默认为 null
  technology_stack: '',  // 技术栈
  budget: 0,  // 预算
  actual_cost: 0,  // 实际成本
  project_type: '',  // 项目类型
  client_name: '',  // 客户名称
  client_contact: '',  // 客户联系方式
  contract_value: 0,  // 合同金额
  estimated_hours: 0,  // 预估工时
  actual_hours: 0,  // 实际工时
  team_size: 0,  // 团队规模
  tags: '',  // 标签
  milestones: '',  // 里程碑
  priority: 'medium'  // 优先级
})

// 经理列表（从项目成员中筛选）
const managers = computed(() => {
  if (!allUsers.value.length) return []
  
  // 从所有用户中筛选可以作为经理的候选人
  // 这里可以根据业务逻辑添加筛选条件，比如角色、权限等
  return allUsers.value.map(user => ({
    id: user.id,
    name: user.username
  }))
})

// 所有用户列表（用于成员选择）
const allUsers = ref([])

// 项目成员选择
const selectedMembers = ref([])

// 获取所有用户列表
const fetchAllUsers = async () => {
  try {
    const response = await apiService.users.getList()
    allUsers.value = response.users || response || []
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败: ' + (error.message || '未知错误'))
  }
}

// 获取项目列表
const fetchProjects = async () => {
  loading.value = true
  try {
    // 传递筛选参数给后端API
    const params = {
      page: 1,
      per_page: 100,
      status: filters.status,
      project_type: filters.project_type,
      search: filters.keyword
    }
    
    // 如果URL中有user_id参数，传递给API获取指定用户的项目
    if (route.query.user_id) {
      params.user_id = route.query.user_id
    }
    
    const response = await apiService.projects.getList(params)
    console.log('项目列表API响应:', response)
    
    // 检查数据结构，确保正确处理
    const projectsData = response.projects || response || []
    
    projects.value = projectsData.map(project => ({
      id: project.id,
      name: project.name,
      code: project.code || '',
      description: project.description || '',
      manager: project.manager_name || project.manager?.username || project.owner?.username || `用户${project.manager_id || project.owner_id}` || '未知',
      manager_id: project.manager_id || project.owner_id,
      start_time: project.start_date ? new Date(project.start_date).toLocaleDateString() : '未设置',
      end_time: project.end_date ? new Date(project.end_date).toLocaleDateString() : '未设置',
      current_stage: project.current_stage || (project.status === 'active' ? '进行中' : '已完成'),
      progress: project.progress || 0,
      quality: project.quality || 'Fair',
      risk: project.risk || 'Medium',
      resources: project.resources || '充足',
      cost: project.cost || null,
      status: project.status,
      technology_stack: project.technology_stack || '',
      budget: project.budget || 0,
      actual_cost: project.actual_cost || 0,
      project_type: project.project_type || '',
      client_name: project.client_name || '',
      client_contact: project.client_contact || '',
      contract_value: project.contract_value || 0,
      estimated_hours: project.estimated_hours || 0,
      actual_hours: project.actual_hours || 0,
      team_size: project.team_size || 0,
      tags: project.tags || '',
      milestones: project.milestones || '',
      members: project.members ? project.members.map(member => ({
        user_id: member.user_id,
        username: member.username || member.user?.username || '未知',
        position: member.position || '成员',
        department: member.department || '未分配',
        joined_at: member.join_date
      })) : []
    }))
    
    console.log('处理后的项目列表:', projects.value)
  } catch (error) {
    console.error('获取项目列表失败:', error)
    ElMessage.error('获取项目列表失败: ' + (error.response?.data?.message || error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 页面加载时获取项目数据和用户列表
onMounted(() => {
  fetchProjects()
  fetchAllUsers()
})


// 筛选后的项目列表
const filteredProjects = computed(() => {
  return projects.value.filter(project => {
    // 权限检查：管理员可以看到所有项目，普通用户只能看到自己参与的项目
    const hasPermission = isAdmin.value || 
      project.members?.some(member => member.user_id === userStore.currentUser?.id)
    
    if (!hasPermission) return false
    
    const matchesKeyword = !filters.keyword || 
      project.name.toLowerCase().includes(filters.keyword.toLowerCase()) ||
      project.code.toLowerCase().includes(filters.keyword.toLowerCase()) ||
      project.description.toLowerCase().includes(filters.keyword.toLowerCase()) ||
      project.manager.toLowerCase().includes(filters.keyword.toLowerCase())
    const matchesStatus = !filters.status || project.status === filters.status
    const matchesProjectType = !filters.project_type || project.project_type === filters.project_type
    return matchesKeyword && matchesStatus && matchesProjectType
  })
})

// 状态灯样式
const getStatusClass = (status) => {
  const classMap = {
    active: 'status-green',
    completed: 'status-yellow',
    closed: 'status-red',
    archived: 'status-gray'
  }
  return classMap[status] || 'status-gray'
}

// 进度标签类型
const getProgressType = (progress) => {
  if (progress >= 90) return 'success'
  if (progress >= 70) return 'warning'
  return 'danger'
}

const getProgressText = (progress) => {
  if (progress >= 90) return '优秀'
  if (progress >= 70) return '良好'
  if (progress >= 50) return '一般'
  return '滞后'
}

// 质量标签类型
const getQualityType = (quality) => {
  if (quality >= 4) return 'success'
  if (quality >= 3) return 'warning'
  return 'danger'
}

// 风险标签类型
const getRiskType = (risk) => {
  if (risk === '低') return 'success'
  if (risk === '中') return 'warning'
  return 'danger'
}

// 资源标签类型
const getResourceType = (resource) => {
  if (resource === '充足') return 'success'
  if (resource === '紧张') return 'warning'
  return 'danger'
}

// 费用标签类型
const getCostType = (cost) => {
  if (cost === '节约') return 'success'
  if (cost === '正常') return 'warning'
  return 'danger'
}

// 项目类型标签类型
const getProjectTypeTag = (projectType) => {
  const typeMap = {
    'internal': 'primary',
    'client': 'success',
    'rd': 'warning',
    'maintenance': 'info'
  }
  return typeMap[projectType] || 'info'
}

// 项目类型显示文本
const getProjectTypeText = (projectType) => {
  const textMap = {
    'internal': '内部项目',
    'client': '客户项目',
    'rd': '研发项目',
    'maintenance': '维护项目'
  }
  return textMap[projectType] || projectType || '未设置'
}

// 团队规模标签类型
const getTeamSizeTag = (teamSize) => {
  if (!teamSize || teamSize === 0) return 'info'
  if (teamSize <= 5) return 'success'
  if (teamSize <= 10) return 'warning'
  return 'danger'
}

// Bug状态类型
const getBugStatusType = (status) => {
  const typeMap = {
    'Open': 'danger',
    'In Progress': 'warning',
    'Resolved': 'success',
    'Closed': 'info',
    'Rejected': 'info'
  }
  return typeMap[status] || 'info'
}

// Bug优先级类型
const getBugPriorityType = (priority) => {
  const typeMap = {
    'Critical': 'danger',
    'High': 'warning',
    'Medium': 'primary',
    'Low': 'info'
  }
  return typeMap[priority] || 'info'
}

// Bug严重程度类型
const getBugSeverityType = (severity) => {
  const typeMap = {
    'Blocker': 'danger',
    'Critical': 'danger',
    'Major': 'warning',
    'Minor': 'info',
    'Trivial': 'info'
  }
  return typeMap[severity] || 'info'
}

// 通用优先级类型
const getPriorityType = (priority) => {
  const typeMap = {
    'Critical': 'danger',
    'High': 'warning',
    'Medium': 'primary',
    'Low': 'info'
  }
  return typeMap[priority] || 'info'
}

// bug列表加载状态
const bugListLoading = ref(false)

// 查看项目详情
const viewProjectDetail = async (project) => {
  // 跳转到项目详情页面，确保id是字符串类型
  console.log('===== 查看项目详情 =====')
  console.log('项目对象:', project)
  console.log('项目ID:', project.id, '类型:', typeof project.id)
  console.log('路由对象:', router)
  console.log('准备跳转的路径:', `/projects/${String(project.id)}`)
  
  try {
    // 使用命名路由方式跳转，更可靠
    const result = await router.push({
      name: 'ProjectDetail',
      params: { id: String(project.id) }
    })
    console.log('路由跳转结果:', result)
    ElMessage.success('正在跳转到项目详情页面...')
  } catch (error) {
    console.error('路由跳转失败:', error)
    // 如果命名路由失败，尝试使用路径方式
    try {
      await router.push(`/projects/${String(project.id)}`)
      ElMessage.success('正在跳转到项目详情页面...')
    } catch (fallbackError) {
      console.error('路径跳转也失败:', fallbackError)
      ElMessage.error('路由跳转失败，请稍后重试')
    }
  }
  
  console.log('===== 查看项目详情结束 =====')
}

// 查看经理详情
const viewManagerDetail = async (managerId) => {
  if (!managerId) {
    ElMessage.warning('无法获取经理信息')
    return
  }
  try {
    await router.push({
      name: 'UserDetail',
      params: { id: String(managerId) }
    })
  } catch (error) {
    console.error('跳转失败:', error)
    ElMessage.error('无法跳转到用户详情页')
  }
}

// 查看成员详情
const viewMemberDetail = async (userId) => {
  if (!userId) {
    ElMessage.warning('无法获取成员信息')
    return
  }
  try {
    await router.push({
      name: 'UserDetail',
      params: { id: String(userId) }
    })
  } catch (error) {
    console.error('跳转失败:', error)
    ElMessage.error('无法跳转到用户详情页')
  }
}

// 获取用户头像
const getUserAvatar = (username) => {
  // 这里可以添加获取用户头像的逻辑
  // 暂时返回空字符串，使用默认头像
  return ''
}

// 显示所有成员
const showAllMembers = (project) => {
  if (!project.members || project.members.length === 0) {
    ElMessage.info('该项目暂无参与人员')
    return
  }
  
  const memberList = project.members.map(member => 
    `${member.username} - ${member.position} - ${member.department}`
  ).join('\n')
  
  ElMessageBox.alert(
    `项目 "${project.name}" 的参与人员：\n\n${memberList}`,
    '项目参与人员',
    {
      confirmButtonText: '确定',
      customClass: 'member-list-dialog'
    }
  )
}

// 编辑项目
const editProject = async (project) => {
  editingProject.value = project

  // 复制项目数据到表单，但需要特殊处理经理字段和日期字段
  Object.assign(projectForm, {
    ...project,
    manager_id: project.manager_id || null, // 保留原有的 manager_id，如果为0也转为null
    start_date: project.start_date || project.start_time || '', // 兼容新旧字段名
    end_date: project.end_date || project.end_time || '', // 兼容新旧字段名
    current_stage: project.current_stage || project.status || '', // 当前阶段
    status: project.status || '' // 项目状态
  })

  // 如果 manager_id 不存在或为0，尝试根据经理名称查找对应的用户ID
  if ((!projectForm.manager_id || projectForm.manager_id === 0) && project.manager && allUsers.value.length > 0) {
    const managerUser = allUsers.value.find(user => user.username === project.manager)
    if (managerUser) {
      projectForm.manager_id = managerUser.id
    }
  }
  
  // 加载项目成员数据
  try {
    const response = await apiService.projects.getById(project.id)
    const projectData = response.project || response
    
    // 设置选中的成员
    if (projectData.members && projectData.members.length > 0) {
      selectedMembers.value = toRaw(projectData.members.map(member => member.user_id))
    } else {
      selectedMembers.value = []
    }
  } catch (error) {
    console.error('获取项目详情失败:', error)
    // 如果获取失败，使用当前项目数据中的成员
    if (project.members && project.members.length > 0) {
      selectedMembers.value = toRaw(project.members.map(member => member.user_id))
    } else {
      selectedMembers.value = []
    }
  }
  
  showCreateDialog.value = true
}



// 删除项目
const deleteProject = async (project, showBugDialog = false) => {
  // 如果需要显示bug对话框
  if (showBugDialog && project.bugs && project.bugs.length > 0) {
    currentProject.value = project
    showBugListDialog.value = true
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除项目"${project.name}"吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 调用后端API删除项目
    await apiService.projects.delete(project.id)
    
    // 从本地列表中移除项目
    const index = projects.value.findIndex(p => p.id === project.id)
    if (index !== -1) {
      projects.value.splice(index, 1)
      ElMessage.success('项目删除成功')
    }
  } catch (error) {
    if (error.response?.data?.code === 'PROJECT_HAS_ITEMS') {
      // 项目下还有Bug，显示统一的对话框
      const bugList = error.response.data.bugs || []
      currentProject.value = {
        ...project,
        bugs: bugList
      }
      showProjectItemsDialog.value = true
      activeItemsTab.value = 'bugs'
    } else if (error.response?.data?.code === 'PROJECT_HAS_BUGS') {
      // 项目下还有Bug，显示bug列表对话框
      const bugList = error.response.data.bugs || []
      currentProject.value = {
        ...project,
        bugs: bugList
      }
      showBugListDialog.value = true
    } else if (error.response?.data?.error) {
      ElMessage.error(`删除失败: ${error.response.data.error}`)
    } else if (error.message && error.message.includes('cancel')) {
      // 用户取消删除，不显示错误
    } else {
      ElMessage.error('删除失败，请稍后重试')
    }
  }
}

// 删除bug
const deleteBug = async (bugId) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个Bug吗？此操作不可恢复。',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await apiService.bugs.delete(bugId)
    
    // 从当前项目的bug列表中移除
    if (currentProject.value && currentProject.value.bugs) {
      const index = currentProject.value.bugs.findIndex(b => b.id === bugId)
      if (index !== -1) {
        currentProject.value.bugs.splice(index, 1)
      }
    }
    
    ElMessage.success('Bug删除成功')
  } catch (error) {
    if (error.message && error.message.includes('cancel')) {
      // 用户取消删除
    } else {
      ElMessage.error('删除Bug失败: ' + (error.response?.data?.error || error.message || '未知错误'))
    }
  }
}

// 批量删除选中bug
const deleteSelectedBugs = async () => {
  if (selectedBugIds.value.length === 0) {
    ElMessage.warning('请选择要删除的Bug')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedBugIds.value.length} 个Bug吗？此操作不可恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 批量删除
    await apiService.bugs.batchDelete(selectedBugIds.value)
    
    // 从当前项目的bug列表中移除
    if (currentProject.value && currentProject.value.bugs) {
      currentProject.value.bugs = currentProject.value.bugs.filter(
        b => !selectedBugIds.value.includes(b.id)
      )
    }
    
    const deletedBugCount = selectedBugIds.value.length
    selectedBugIds.value = []
    ElMessage.success(`成功删除 ${deletedBugCount} 个Bug`)
  } catch (error) {
    if (error.message && error.message.includes('cancel')) {
      // 用户取消删除
    } else {
      ElMessage.error('批量删除Bug失败: ' + (error.response?.data?.error || error.message || '未知错误'))
    }
  }
}

// 重新尝试删除项目
const retryDeleteProject = async () => {
  if (!currentProject.value) return
  
  // 检查是否还有bug
  if (currentProject.value.bugs && currentProject.value.bugs.length > 0) {
    ElMessage.warning('请先删除所有Bug后再删除项目')
    return
  }
  
  showBugListDialog.value = false
  showProjectItemsDialog.value = false
  await deleteProject(currentProject.value)
}

// bug选择相关
const selectedBugIds = ref([])
const currentProject = ref(null)
const showBugListDialog = ref(false)
const showProjectItemsDialog = ref(false)
const activeItemsTab = ref('bugs')

// 处理bug选择
const handleBugSelectionChange = (selection) => {
  selectedBugIds.value = selection.map(bug => bug.id)
}

// 批量删除后重新获取项目bug列表
const refreshBugList = async () => {
  if (!currentProject.value) return
  
  try {
    const response = await apiService.bugs.getList({ project_id: currentProject.value.id })
    const bugsData = response.bugs || response || []
    currentProject.value.bugs = bugsData.map(bug => ({
      id: bug.id,
      title: bug.title,
      status: bug.status,
      priority: bug.priority,
      severity: bug.severity,
      created_at: bug.created_at
    }))
    selectedBugIds.value = []
  } catch (error) {
    console.error('刷新bug列表失败:', error)
  }
}



// 保存项目
const saveProject = async () => {
  if (!projectForm.name.trim()) {
    ElMessage.error('请输入项目名称')
    return
  }
  
  if (!projectForm.code.trim()) {
    ElMessage.error('请输入项目代码')
    return
  }
  
  try {
    if (editingProject.value) {
      // 编辑项目 - 调用更新API - 显式列出所有需要的字段
      // 处理 cost 字段，确保是有效的字符串值或 null
      const validCostValues = ['normal', 'over', 'under']
      const processedCost = projectForm.cost && validCostValues.includes(projectForm.cost) 
        ? projectForm.cost 
        : null
      
      // 处理 manager_id - 确保为有效值或 null
      const processedManagerId = projectForm.manager_id && projectForm.manager_id > 0 
        ? projectForm.manager_id 
        : null
      
      // 处理成员数组 - 确保转换为标准数组并过滤无效值
      let processedMembers = []
      try {
        const rawMembers = toRaw(selectedMembers.value)
        if (Array.isArray(rawMembers)) {
          processedMembers = rawMembers.filter(id => id && id > 0).map(id => Number(id))
        }
      } catch (e) {
        console.warn('处理成员数据时出错:', e)
        processedMembers = []
      }
      
      const updateData = {
        name: projectForm.name?.trim() || '',
        code: projectForm.code?.trim() || '',
        description: projectForm.description?.trim() || '',
        manager_id: processedManagerId,
        start_date: projectForm.start_date,
        end_date: projectForm.end_date,
        current_stage: projectForm.current_stage?.trim() || '',
        status: projectForm.status || null,
        progress: Math.max(0, Math.min(100, Number(projectForm.progress) || 0)),
        quality: projectForm.quality || null,
        risk: projectForm.risk || null,
        resources: projectForm.resources?.trim() || '',
        cost: processedCost,
        technology_stack: projectForm.technology_stack?.trim() || '',
        budget: projectForm.budget ? Number(projectForm.budget) : null,
        actual_cost: projectForm.actual_cost ? Number(projectForm.actual_cost) : null,
        project_type: projectForm.project_type?.trim() || '',
        client_name: projectForm.client_name?.trim() || '',
        client_contact: projectForm.client_contact?.trim() || '',
        contract_value: projectForm.contract_value ? Number(projectForm.contract_value) : null,
        estimated_hours: projectForm.estimated_hours ? Number(projectForm.estimated_hours) : null,
        actual_hours: projectForm.actual_hours ? Number(projectForm.actual_hours) : null,
        team_size: projectForm.team_size ? Number(projectForm.team_size) : null,
        tags: projectForm.tags?.trim() || '',
        milestones: projectForm.milestones?.trim() || '',
        priority: projectForm.priority || 'medium',
        // 确保 members 是标准数组
        members: processedMembers
      }
      
      // 格式化日期字段为ISO字符串 - 修复日期格式化逻辑
      if (updateData.start_date) {
        // 处理日期格式，确保是有效的Date对象
        const startDate = new Date(updateData.start_date)
        if (!isNaN(startDate.getTime())) {
          updateData.start_date = startDate.toISOString()
        } else {
          // 如果日期无效，设置为null
          updateData.start_date = null
        }
      }
      
      if (updateData.end_date) {
        const endDate = new Date(updateData.end_date)
        if (!isNaN(endDate.getTime())) {
          updateData.end_date = endDate.toISOString()
        } else {
          updateData.end_date = null
        }
      }
      
      console.log('发送到后端的更新数据:', updateData)
      console.log('项目ID:', editingProject.value.id)
      console.log('原始表单数据:', projectForm)
      console.log('选中成员:', selectedMembers.value)
      
      await apiService.projects.update(editingProject.value.id, updateData)
      
      // 更新本地数据
      Object.assign(editingProject.value, projectForm)
      
      // 更新projects数组中的对应项目
      const projectIndex = projects.value.findIndex(p => p.id === editingProject.value.id)
      if (projectIndex !== -1) {
        Object.assign(projects.value[projectIndex], projectForm)
        
        // 更新成员数据
        if (projects.value[projectIndex].members) {
          projects.value[projectIndex].members = selectedMembers.value.map(userId => {
            const user = allUsers.value.find(u => u.id === userId)
            return {
              user_id: userId,
              username: user ? user.username : '未知',
              role: 'member',
              position: user ? user.position : '成员',
              department: user ? user.department : '未分配'
            }
          })
        }
      }
      
      ElMessage.success('项目更新成功')
    } else {
      // 新建项目 - 调用创建API - 显式列出所有需要的字段
      // 处理 cost 字段，确保是有效的字符串值或 null
      const validCostValues = ['normal', 'over', 'under']
      const processedCost = projectForm.cost && validCostValues.includes(projectForm.cost)
        ? projectForm.cost
        : null

      // 处理 manager_id - 确保为有效值或 null
      const processedManagerId = projectForm.manager_id && projectForm.manager_id > 0 
        ? projectForm.manager_id 
        : null
      
      // 处理成员数组 - 确保转换为标准数组并过滤无效值
      let processedMembers = []
      try {
        const rawMembers = toRaw(selectedMembers.value)
        if (Array.isArray(rawMembers)) {
          processedMembers = rawMembers.filter(id => id && id > 0).map(id => Number(id))
        }
      } catch (e) {
        console.warn('处理成员数据时出错:', e)
        processedMembers = []
      }

      const createData = {
        name: projectForm.name?.trim() || '',
        code: projectForm.code?.trim() || '',
        description: projectForm.description?.trim() || '',
        manager_id: processedManagerId,
        start_date: projectForm.start_date,
        end_date: projectForm.end_date,
        current_stage: projectForm.current_stage?.trim() || '',
        status: projectForm.status || null,
        progress: Math.max(0, Math.min(100, Number(projectForm.progress) || 0)),
        quality: projectForm.quality || null,
        risk: projectForm.risk || null,
        resources: projectForm.resources?.trim() || '',
        cost: processedCost,
        technology_stack: projectForm.technology_stack?.trim() || '',
        budget: projectForm.budget ? Number(projectForm.budget) : null,
        actual_cost: projectForm.actual_cost ? Number(projectForm.actual_cost) : null,
        project_type: projectForm.project_type?.trim() || '',
        client_name: projectForm.client_name?.trim() || '',
        client_contact: projectForm.client_contact?.trim() || '',
        contract_value: projectForm.contract_value ? Number(projectForm.contract_value) : null,
        estimated_hours: projectForm.estimated_hours ? Number(projectForm.estimated_hours) : null,
        actual_hours: projectForm.actual_hours ? Number(projectForm.actual_hours) : null,
        team_size: projectForm.team_size ? Number(projectForm.team_size) : null,
        tags: projectForm.tags?.trim() || '',
        milestones: projectForm.milestones?.trim() || '',
        priority: projectForm.priority || 'medium',
        // 确保 members 是标准数组
        members: processedMembers
      }

      // 格式化日期字段为ISO字符串
      if (createData.start_date) {
        const startDate = new Date(createData.start_date)
        if (!isNaN(startDate.getTime())) {
          createData.start_date = startDate.toISOString()
        } else {
          createData.start_date = null
        }
      }
      
      if (createData.end_date) {
        const endDate = new Date(createData.end_date)
        if (!isNaN(endDate.getTime())) {
          createData.end_date = endDate.toISOString()
        } else {
          createData.end_date = null
        }
      }
      
      console.log('发送到后端的创建数据:', createData)
      
      const response = await apiService.projects.create(createData)
      
      // 从API响应中获取新创建的项目数据
      const newProject = response.data?.project || response.project || response
      
      // 确保新创建的项目有完整的字段
      if (newProject) {
        // 补充分类等字段
        const fullProject = {
          id: newProject.id,
          name: newProject.name,
          code: newProject.code || createData.code,
          description: createData.description || '',
          manager_id: createData.manager_id,
          manager: allUsers.value.find(u => u.id === createData.manager_id)?.username || '未知',
          start_date: createData.start_date,
          end_date: createData.end_date,
          start_time: createData.start_date ? new Date(createData.start_date).toLocaleDateString() : '未设置',
          end_time: createData.end_date ? new Date(createData.end_date).toLocaleDateString() : '未设置',
          current_stage: createData.current_stage || '进行中',
          progress: createData.progress || 0,
          quality: createData.quality || 'Fair',
          risk: createData.risk || 'Medium',
          resources: createData.resources || '充足',
          cost: createData.cost,
          status: newProject.status || createData.status || 'active',
          technology_stack: createData.technology_stack || '',
          budget: createData.budget || 0,
          actual_cost: createData.actual_cost || 0,
          project_type: createData.project_type || '',
          client_name: createData.client_name || '',
          client_contact: createData.client_contact || '',
          contract_value: createData.contract_value || 0,
          estimated_hours: createData.estimated_hours || 0,
          actual_hours: createData.actual_hours || 0,
          team_size: createData.team_size || 0,
          tags: createData.tags || '',
          milestones: createData.milestones || '',
          members: selectedMembers.value.map(userId => {
            const user = allUsers.value.find(u => u.id === userId)
            return {
              user_id: userId,
              username: user ? user.username : '未知',
              role: 'member',
              position: user ? user.position : '成员',
              department: user ? user.department : '未分配'
            }
          })
        }
        projects.value.push(fullProject)
      }
      
      ElMessage.success('项目创建成功')
    }
    
    showCreateDialog.value = false
    resetForm()
  } catch (error) {
    console.error('保存项目失败:', error)
    
    // 更详细的错误处理
    let errorMessage = '保存项目失败'
    if (error.response?.data) {
      const errorData = error.response.data
      if (errorData.error) {
        errorMessage += '：' + errorData.error
      } else if (errorData.message) {
        errorMessage += '：' + errorData.message
      } else if (typeof errorData === 'string') {
        errorMessage += '：' + errorData
      }
      
      // 如果是验证错误，显示具体字段错误
      if (errorData.code === 'VALIDATION_ERROR' && errorData.details) {
        errorMessage += '\n' + errorData.details
      }
    } else if (error.message) {
      errorMessage += '：' + error.message
    }
    
    ElMessage.error({
      message: errorMessage,
      duration: 5000,
      showClose: true
    })
  }
}

// 重置表单
const resetForm = () => {
  editingProject.value = null
  Object.assign(projectForm, {
    name: '',
    manager_id: null,
    start_date: '',
    end_date: '',
    current_stage: '',  // 当前阶段
    status: '',  // 项目状态
    progress: 0,
    quality: 'Fair',  // 修改：使用英文值
    risk: 'Medium',   // 修改：使用英文值
    resources: '',  // 修改：将 resource 改为 resources
    cost: null  // 修改：使用 null 而不是字符串
  })
  selectedMembers.value = []
}

// 导出项目数据
const handleExportCommand = async (command) => {
  try {
    exporting.value = true
    
    // 根据选择的格式导出数据
    await exportProjects(command)
    
    ElMessage.success(`项目数据已导出为${command.toUpperCase()}格式`)
  } catch (error) {
    console.error('导出项目数据失败:', error)
    ElMessage.error(`导出失败: ${error.response?.data?.message || error.message || '未知错误'}`)
  } finally {
    exporting.value = false
  }
}

const exportProjects = async (format = 'excel') => {
  try {
    // 准备导出参数，可以传递当前筛选条件
    const params = {
      format: format
    }
    
    // 如果有筛选条件，可以传递给后端
    if (filters.status) {
      params.status = filters.status
    }
    if (filters.project_type) {
      params.project_type = filters.project_type
    }
    if (filters.keyword) {
      params.search = filters.keyword
    }
    
    // 调用导出API
    const response = await apiService.projects.export(format, params)
    
    // 创建下载链接
    const blob = new Blob([response.data], { 
      type: format === 'csv' ? 'text/csv;charset=utf-8;' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // 根据格式设置文件名
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')
    const filename = `projects_export_${timestamp}.${format === 'csv' ? 'csv' : 'xlsx'}`
    link.setAttribute('download', filename)
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    return response
  } catch (error) {
    console.error('导出项目数据失败:', error)
    throw error
  }
}

onMounted(() => {
  loading.value = false
})
</script>

<style scoped>
.project-list {
  padding: 0;
}

.project-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.project-list-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.status-legend-card {
  margin-bottom: 24px;
}

.status-legend {
  display: flex;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-green {
  background-color: #67C23A;
}

.status-yellow {
  background-color: #E6A23C;
}

.status-red {
  background-color: #F56C6C;
}

.status-gray {
  background-color: #909399;
}

.project-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  margin-left: 8px;
  font-size: 12px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-controls {
  display: flex;
  gap: 10px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

:deep(.el-table .cell) {
  display: flex;
  align-items: center;
}

:deep(.el-progress) {
  width: 60px;
}

@media (max-width: 768px) {
  .project-list-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .filter-controls {
    flex-direction: column;
    width: 100%;
  }
  
  .status-legend {
    flex-wrap: wrap;
    gap: 16px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
}

.bug-list-container {
  padding: 10px 0;
}

.bug-list-header {
  margin-bottom: 20px;
}

.bug-list-header p {
  margin: 5px 0;
  color: #606266;
}

.bug-list-header .warning-text {
  color: #E6A23C;
  font-weight: bold;
}

.bug-list-actions {
  margin-bottom: 15px;
  display: flex;
  gap: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media screen and (max-width: 768px) {
  .project-list {
    padding: 0;
  }

  .project-list-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
    padding: 12px;
  }

  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    width: 100%;
  }

  .project-list-header h2 {
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
    max-width: calc(50% - 4px);
    font-size: 12px;
    padding: 8px 12px;
  }

  .status-legend-card {
    margin-bottom: 16px;
  }

  .status-legend {
    flex-wrap: wrap;
    gap: 12px;
  }

  .legend-item {
    font-size: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    font-size: 14px;
  }

  .filter-controls {
    flex-direction: column;
    width: 100%;
    gap: 8px;
  }

  .filter-controls .el-input,
  .filter-controls .el-select {
    width: 100% !important;
    margin-right: 0;
  }

  .filter-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: flex-start;
    margin-top: 8px;
  }

  .filter-actions .el-button {
    flex: none;
    font-size: 12px;
    padding: 6px 12px;
  }

  .project-card {
    margin-bottom: 12px;
  }

  .project-card-body {
    padding: 12px;
  }

  .project-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .project-name {
    font-size: 14px;
  }

  .project-description {
    font-size: 12px;
    line-height: 1.5;
  }

  .project-meta {
    flex-wrap: wrap;
    gap: 8px;
    font-size: 11px;
  }

  .project-members {
    flex-wrap: wrap;
    gap: 4px;
  }

  .project-members .el-avatar {
    width: 28px;
    height: 28px;
  }

  .progress-text {
    font-size: 11px;
  }

  .project-tags {
    flex-wrap: wrap;
    gap: 4px;
  }

  .project-tag {
    font-size: 10px;
    padding: 1px 6px;
  }

  .bug-list-container {
    padding: 8px 0;
  }

  .bug-list-header {
    margin-bottom: 12px;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .bug-list-header p {
    font-size: 13px;
  }

  .bug-list-actions {
    margin-bottom: 12px;
    flex-wrap: wrap;
    gap: 8px;
    width: 100%;
  }

  .bug-list-actions .el-button {
    flex: 1;
    min-width: calc(50% - 4px);
    font-size: 12px;
    padding: 8px 12px;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
  }

  .dialog-footer {
    flex-direction: column;
    gap: 8px;
  }

  .dialog-footer .el-button {
    width: 100%;
    margin: 0;
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

  .el-pagination {
    font-size: 11px !important;
    flex-wrap: wrap;
    gap: 4px;
  }

  .el-pagination__sizes,
  .el-pagination__jump {
    display: none !important;
  }

  .el-pagination button,
  .el-pager li {
    min-width: 26px !important;
    height: 26px !important;
    line-height: 26px !important;
    font-size: 11px !important;
  }
}

@media screen and (max-width: 480px) {
  .project-list-header {
    padding: 10px;
  }

  .project-list-header h2 {
    font-size: 16px;
  }

  .header-actions .el-button {
    max-width: 100%;
    flex: none;
    width: 100%;
    font-size: 11px;
    padding: 6px 10px;
  }

  .status-legend {
    gap: 8px;
  }

  .legend-item {
    font-size: 11px;
  }

  .project-name {
    font-size: 13px;
  }

  .project-description {
    font-size: 11px;
  }

  .project-meta {
    font-size: 10px;
    gap: 6px;
  }

  .bug-list-actions .el-button {
    font-size: 11px;
    padding: 6px 10px;
  }

  .el-table {
    font-size: 10px !important;
  }

  .el-form-item {
    margin-bottom: 12px !important;
  }

  .el-input__inner,
  .el-textarea__inner {
    font-size: 14px !important;
  }

  .el-pagination {
    font-size: 10px !important;
  }

  .el-pagination button,
  .el-pager li {
    min-width: 24px !important;
    height: 24px !important;
    line-height: 24px !important;
  }
}
</style>