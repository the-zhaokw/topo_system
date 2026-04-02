<template>
  <div class="my-department">
    <div class="page-header">
      <h2>{{ pageTitle }}</h2>
      <p v-if="departmentInfo.has_department && departmentInfo.department && !canViewAll">
        {{ departmentInfo.department.name }}
        <el-tag v-if="departmentInfo.is_manager" type="success" size="small" style="margin-left: 10px;">
          部门经理
        </el-tag>
      </p>
      <p v-else-if="canViewAll">
        <el-tag type="danger" size="small">系统管理员</el-tag>
      </p>
    </div>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="!departmentInfo.has_department && !canViewAll" class="empty-state">
      <el-empty description="您尚未加入任何部门">
        <template #image>
          <el-icon :size="80" color="#909399">
            <OfficeBuilding />
          </el-icon>
        </template>
      </el-empty>
    </div>

    <div v-else class="department-content">
      <el-card v-if="!departmentInfo.is_manager && !canViewAll" class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>部门信息</span>
          </div>
        </template>
        <div class="department-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="部门名称">
              {{ departmentInfo.department?.name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="部门描述">
              {{ departmentInfo.department?.description || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="我的职位">
              {{ departmentInfo.current_user?.position || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
        <el-alert
          type="info"
          :closable="false"
          style="margin-top: 20px;"
        >
          <template #title>
            <el-icon><InfoFilled /></el-icon>
            <span style="margin-left: 5px;">提示</span>
          </template>
          {{ departmentInfo.message || '您不是部门经理，无法查看部门员工列表' }}
        </el-alert>
      </el-card>

      <div v-else>
        <el-row :gutter="20" class="stats-row">
          <el-col :span="8">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-icon" style="background: #E3F2FD;">
                  <el-icon :size="30" color="#2196F3">
                    <User />
                  </el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.total || 0 }}</div>
                  <div class="stat-label">{{ canViewAll ? '系统总人数' : '部门总人数' }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-icon" style="background: #E8F5E9;">
                  <el-icon :size="30" color="#4CAF50">
                    <CircleCheck />
                  </el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.active || 0 }}</div>
                  <div class="stat-label">活跃成员</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-icon" style="background: #FFEBEE;">
                  <el-icon :size="30" color="#F44336">
                    <CircleClose />
                  </el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ statistics.inactive || 0 }}</div>
                  <div class="stat-label">非活跃成员</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-card v-if="canViewAll && departments.length > 0" class="departments-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>部门列表</span>
            </div>
          </template>
          <div class="departments-grid">
            <div 
              v-for="dept in departments" 
              :key="dept.id" 
              class="department-item"
              :class="{ 'active': selectedDepartment === dept.name }"
              @click="selectDepartment(dept.name)"
            >
              <div class="dept-name">{{ dept.name }}</div>
              <div class="dept-count">{{ dept.member_count }} 人</div>
            </div>
            <div 
              class="department-item"
              :class="{ 'active': selectedDepartment === '' }"
              @click="selectDepartment('')"
            >
              <div class="dept-name">全部</div>
              <div class="dept-count">{{ statistics.total }} 人</div>
            </div>
          </div>
        </el-card>

        <el-card class="members-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>{{ canViewAll ? '人员列表' : '部门成员列表' }}</span>
              <div class="header-actions">
                <el-input
                  v-model="searchText"
                  placeholder="搜索成员"
                  style="width: 200px; margin-right: 10px;"
                  clearable
                  @clear="handleSearch"
                  @keyup.enter="handleSearch"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-button type="primary" @click="handleSearch">
                  <el-icon><Search /></el-icon>
                  搜索
                </el-button>
              </div>
            </div>
          </template>

          <div v-if="positions.length > 0" class="position-filter">
            <el-tag
              :type="selectedPosition === '' ? 'primary' : 'info'"
              style="margin-right: 8px; cursor: pointer;"
              @click="selectPosition('')"
            >
              全部 ({{ members.length }})
            </el-tag>
            <el-tag
              v-for="pos in positions"
              :key="pos"
              :type="selectedPosition === pos ? 'primary' : 'info'"
              style="margin-right: 8px; cursor: pointer;"
              @click="selectPosition(pos)"
            >
              {{ pos }} ({{ groupedMembers[pos]?.length || 0 }})
            </el-tag>
          </div>

          <div v-for="(membersInPosition, position) in groupedMembers" :key="position" class="position-group">
            <div class="position-header">
              <span class="position-title">{{ position }}</span>
              <span class="position-count">{{ membersInPosition.length }} 人</span>
            </div>
            <el-table
              :data="membersInPosition"
              style="width: 100%"
              :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
              size="small"
            >
              <el-table-column prop="id" label="ID" width="60" />
              <el-table-column label="姓名" min-width="120">
                <template #default="{ row }">
                  <div class="user-info">
                    <span class="username">{{ row.username }}</span>
                    <span v-if="row.first_name || row.last_name" class="real-name">
                      ({{ row.last_name }}{{ row.first_name }})
                    </span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="email" label="邮箱" min-width="150" />
              <el-table-column v-if="canViewAll" prop="department" label="部门" width="100" />
              <el-table-column label="职位" width="100">
                <template #default="{ row }">
                  <el-tag size="small">
                    {{ row.position || '-' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="状态" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                    {{ row.is_active ? '活跃' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80" fixed="right">
                <template #default="{ row }">
                  <el-button
                    type="primary"
                    link
                    size="small"
                    @click="viewUserDetail(row.id)"
                  >
                    详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div v-if="Object.keys(groupedMembers).length === 0 && !tableLoading" class="empty-members">
            <el-empty description="暂无成员数据" />
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  OfficeBuilding, 
  User, 
  CircleCheck, 
  CircleClose, 
  Search,
  InfoFilled 
} from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

const router = useRouter()

const loading = ref(true)
const tableLoading = ref(false)
const departmentInfo = ref({})
const members = ref([])
const filteredMembers = ref([])
const statistics = ref({})
const departments = ref([])
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const totalMembers = ref(0)
const selectedDepartment = ref('')
const selectedPosition = ref('')
const canViewAll = ref(false)

const pageTitle = computed(() => {
  return canViewAll.value ? '人员管理' : '我的部门'
})

const positions = computed(() => {
  const positionSet = new Set()
  members.value.forEach(member => {
    if (member.position) {
      positionSet.add(member.position)
    }
  })
  return Array.from(positionSet).sort()
})

const groupedMembers = computed(() => {
  const groups = {}
  const displayMembers = selectedPosition.value
    ? members.value.filter(m => m.position === selectedPosition.value)
    : members.value

  displayMembers.forEach(member => {
    const pos = member.position || '未分配职位'
    if (!groups[pos]) {
      groups[pos] = []
    }
    groups[pos].push(member)
  })
  return groups
})

/**
 * 获取部门信息
 * 权限说明：
 * - is_system_admin: 系统管理员，可以查看所有部门和人员
 * - is_manager: 部门经理，可以查看自己部门的成员
 * - can_view_all: 是否可以查看所有部门（仅系统管理员为true）
 */
const fetchMyDepartment = async () => {
  try {
    loading.value = true
    const response = await apiService.users.getMyDepartment({
      page: currentPage.value,
      per_page: pageSize.value,
      search: searchText.value,
      department: selectedDepartment.value
    })

    departmentInfo.value = response
    canViewAll.value = response.can_view_all || false

    // 系统管理员才有所有部门列表
    if (response.departments) {
      departments.value = response.departments
    }

    // 部门经理或系统管理员可以查看成员列表
    if ((response.is_manager || response.can_view_all) && response.members) {
      members.value = response.members
      totalMembers.value = response.total_members || 0
      statistics.value = response.statistics || {}
    }
  } catch (error) {
    console.error('获取部门信息失败:', error)
    ElMessage.error(error.response?.data?.error || '获取部门信息失败')
  } finally {
    loading.value = false
  }
}

const selectDepartment = (deptName) => {
  selectedDepartment.value = deptName
  selectedPosition.value = ''
  currentPage.value = 1
  fetchMyDepartment()
}

const selectPosition = (position) => {
  selectedPosition.value = position
}

const handleSearch = () => {
  currentPage.value = 1
  fetchMyDepartment()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchMyDepartment()
}

const handlePageChange = (val) => {
  currentPage.value = val
  fetchMyDepartment()
}

const viewUserDetail = (userId) => {
  router.push(`/users/${userId}`)
}

onMounted(() => {
  fetchMyDepartment()
})
</script>

<style scoped>
.my-department {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
}

.page-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  display: flex;
  align-items: center;
}

.loading-container {
  padding: 40px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.department-content {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #303133;
}

.department-info {
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 100%;
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.departments-card {
  margin-bottom: 20px;
}

.departments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
}

.department-item {
  padding: 16px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
}

.department-item:hover {
  border-color: #409EFF;
  background: #ecf5ff;
}

.department-item.active {
  border-color: #409EFF;
  background: #409EFF;
}

.department-item.active .dept-name,
.department-item.active .dept-count {
  color: white;
}

.dept-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  font-size: 14px;
}

.dept-count {
  font-size: 12px;
  color: #909399;
}

.members-card {
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 500;
  color: #303133;
}

.real-name {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.position-filter {
  margin-bottom: 20px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.position-group {
  margin-bottom: 20px;
}

.position-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  margin-bottom: 10px;
  border-bottom: 2px solid #409EFF;
}

.position-title {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.position-count {
  font-size: 14px;
  color: #909399;
}

.empty-members {
  padding: 40px 0;
}

@media screen and (max-width: 768px) {
  .my-department {
    padding: 10px;
  }

  .page-header h2 {
    font-size: 20px;
  }

  .stats-row {
    margin-bottom: 10px;
  }

  .stat-content {
    padding: 5px;
  }

  .stat-icon {
    width: 50px;
    height: 50px;
  }

  .stat-number {
    font-size: 24px;
  }

  .stat-label {
    font-size: 12px;
  }

  .departments-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 8px;
  }

  .department-item {
    padding: 12px 8px;
  }

  .dept-name {
    font-size: 12px;
  }

  .dept-count {
    font-size: 11px;
  }

  .header-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions .el-input {
    width: 100% !important;
    margin-right: 0 !important;
    margin-bottom: 10px;
  }

  .pagination-container {
    overflow-x: auto;
  }
}
</style>
