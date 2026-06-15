<template>
  <div class="my-department">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><OfficeBuilding /></el-icon>
          </div>
          <div class="title-text">
            <h1>{{ pageTitle }}</h1>
            <p v-if="departmentInfo.has_department && departmentInfo.department && !canViewAll" class="subtitle">
              {{ departmentInfo.department.name }}
              <el-tag v-if="departmentInfo.is_manager" type="success" size="small" class="manager-tag">
                部门经理
              </el-tag>
            </p>
            <p v-else-if="canViewAll" class="subtitle">
              <el-tag type="danger" size="small" class="admin-tag">系统管理员</el-tag>
            </p>
            <p v-else class="subtitle">管理您的部门和团队成员</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-container animate-fade-in-up">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="!departmentInfo.has_department && !canViewAll" class="empty-state animate-fade-in-up">
      <el-empty description="您尚未加入任何部门">
        <template #image>
          <div class="empty-icon-wrapper">
            <el-icon :size="80" color="#909399">
              <OfficeBuilding />
            </el-icon>
          </div>
        </template>
      </el-empty>
    </div>

    <div v-else class="department-content">
      <!-- 非经理视图 - 部门信息卡片 -->
      <el-card v-if="!departmentInfo.is_manager && !canViewAll" class="info-card glass-card animate-fade-in-up delay-100" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><InfoFilled /></el-icon>
              部门信息
            </span>
          </div>
        </template>
        <div class="department-info">
          <el-descriptions :column="2" border class="custom-descriptions">
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
          class="info-alert"
        >
          <template #title>
            <el-icon><InfoFilled /></el-icon>
            <span style="margin-left: 5px;">提示</span>
          </template>
          {{ departmentInfo.message || '您不是部门经理，无法查看部门员工列表' }}
        </el-alert>
      </el-card>

      <div v-else>
        <!-- 统计卡片区域 -->
        <div class="stats-row animate-fade-in-up delay-100">
          <el-row :gutter="16">
            <el-col :xs="12" :sm="6" :md="6" :lg="6">
              <div class="stat-card stat-card-members">
                <div class="stat-icon-wrapper stat-icon-wrapper-members">
                  <el-icon><User /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ statistics.total || 0 }}</div>
                  <div class="stat-label">{{ canViewAll ? '系统总人数' : '部门人数' }}</div>
                </div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6" :md="6" :lg="6">
              <div class="stat-card stat-card-projects">
                <div class="stat-icon-wrapper stat-icon-wrapper-projects">
                  <el-icon><Folder /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ projectCount }}</div>
                  <div class="stat-label">项目数</div>
                </div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6" :md="6" :lg="6">
              <div class="stat-card stat-card-activities">
                <div class="stat-icon-wrapper stat-icon-wrapper-activities">
                  <el-icon><Calendar /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ monthlyActivities }}</div>
                  <div class="stat-label">本月活动</div>
                </div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6" :md="6" :lg="6">
              <div class="stat-card stat-card-todos">
                <div class="stat-icon-wrapper stat-icon-wrapper-todos">
                  <el-icon><List /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ todoCount }}</div>
                  <div class="stat-label">待办事项</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 部门列表（管理员视图） -->
        <el-card v-if="canViewAll && departments.length > 0" class="departments-card glass-card animate-fade-in-up delay-200" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Grid /></el-icon>
                部门列表
              </span>
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
              <div class="dept-icon">
                <el-icon><OfficeBuilding /></el-icon>
              </div>
              <div class="dept-name">{{ dept.name }}</div>
              <div class="dept-count">{{ dept.member_count }} 人</div>
            </div>
            <div 
              class="department-item"
              :class="{ 'active': selectedDepartment === '' }"
              @click="selectDepartment('')"
            >
              <div class="dept-icon">
                <el-icon><UserFilled /></el-icon>
              </div>
              <div class="dept-name">全部</div>
              <div class="dept-count">{{ statistics.total }} 人</div>
            </div>
          </div>
        </el-card>

        <!-- 成员列表 -->
        <el-card class="members-card glass-card animate-fade-in-up delay-300" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><UserFilled /></el-icon>
                {{ canViewAll ? '人员列表' : '部门成员列表' }}
              </span>
              <div class="header-actions">
                <el-input
                  v-model="searchText"
                  placeholder="搜索成员"
                  class="search-input"
                  clearable
                  @clear="handleSearch"
                  @keyup.enter="handleSearch"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-button type="primary" @click="handleSearch" class="btn-gradient">
                  <el-icon><Search /></el-icon>
                  搜索
                </el-button>
              </div>
            </div>
          </template>

          <!-- 职位筛选 -->
          <div v-if="positions.length > 0" class="position-filter">
            <el-tag
              :type="selectedPosition === '' ? 'primary' : 'info'"
              class="filter-tag"
              @click="selectPosition('')"
            >
              全部 ({{ members.length }})
            </el-tag>
            <el-tag
              v-for="pos in positions"
              :key="pos"
              :type="selectedPosition === pos ? 'primary' : 'info'"
              class="filter-tag"
              @click="selectPosition(pos)"
            >
              {{ pos }} ({{ groupedMembers[pos]?.length || 0 }})
            </el-tag>
          </div>

          <!-- 成员分组列表 -->
          <div v-for="(membersInPosition, position) in groupedMembers" :key="position" class="position-group">
            <div class="position-header">
              <div class="position-title-wrapper">
                <div class="position-icon">
                  <el-icon><Avatar /></el-icon>
                </div>
                <span class="position-title">{{ position }}</span>
              </div>
              <span class="position-count">{{ membersInPosition.length }} 人</span>
            </div>
            <div class="members-grid">
              <div 
                v-for="member in membersInPosition" 
                :key="member.id" 
                class="member-card"
                @click="viewUserDetail(member.id)"
              >
                <div class="member-avatar-wrapper">
                  <div class="member-avatar">
                    {{ getAvatarText(member) }}
                  </div>
                  <div class="member-status" :class="{ 'active': member.is_active }"></div>
                </div>
                <div class="member-info">
                  <div class="member-name">{{ member.username }}</div>
                  <div v-if="member.first_name || member.last_name" class="member-real-name">
                    {{ member.last_name }}{{ member.first_name }}
                  </div>
                  <div class="member-email">{{ member.email }}</div>
                  <div class="member-tags">
                    <el-tag v-if="member.position" size="small" class="position-tag">
                      {{ member.position }}
                    </el-tag>
                    <el-tag :type="member.is_active ? 'success' : 'danger'" size="small" class="status-tag">
                      {{ member.is_active ? '活跃' : '禁用' }}
                    </el-tag>
                    <el-tag v-if="canViewAll && member.department" size="small" type="info" class="dept-tag">
                      {{ member.department }}
                    </el-tag>
                  </div>
                </div>
                <div class="member-action">
                  <el-button type="primary" link size="small" class="view-btn">
                    <el-icon><ArrowRight /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
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
  UserFilled,
  Search,
  InfoFilled,
  Folder,
  Calendar,
  List,
  Grid,
  User as Avatar,
  ArrowRight
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

// 模拟统计数据
const projectCount = ref(12)
const monthlyActivities = ref(28)
const todoCount = ref(5)

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

// 获取头像文字
const getAvatarText = (member) => {
  if (member.last_name && member.first_name) {
    return member.last_name.charAt(0)
  }
  return member.username ? member.username.charAt(0).toUpperCase() : '?'
}

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
/* 导入设计系统 */
@import '@/styles/design-system.css';

.my-department {
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
  display: flex;
  align-items: center;
  gap: 8px;
}

.manager-tag {
  background: rgba(255, 255, 255, 0.2) !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
  color: white !important;
}

.admin-tag {
  background: rgba(239, 68, 68, 0.8) !important;
  border-color: rgba(239, 68, 68, 0.5) !important;
  color: white !important;
}

/* 加载状态 */
.loading-container {
  padding: 40px;
}

/* 空状态 */
.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.empty-icon-wrapper {
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
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

/* 统计卡片区域 */
.stats-row {
  margin-bottom: 24px;
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

/* 4种不同的渐变配色 */
.stat-card-members::before { background: linear-gradient(90deg, #7dd3fc, #38bdf8); }
.stat-card-projects::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-activities::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-todos::before { background: linear-gradient(90deg, #ec4899, #f472b6); }

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

.stat-icon-wrapper-members {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #7dd3fc;
  box-shadow: 0 4px 15px -3px rgba(56, 189, 248, 0.4);
}

.stat-icon-wrapper-projects {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-icon-wrapper-activities {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-icon-wrapper-todos {
  background: linear-gradient(135deg, #fce7f3 0%, #f9a8d4 100%);
  color: #db2777;
  box-shadow: 0 4px 15px -3px rgba(236, 72, 153, 0.4);
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

.stat-card-members .stat-value {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-projects .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-activities .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-todos .stat-value {
  background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
}

/* 卡片头部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

/* 部门信息卡片 */
.info-card {
  margin-bottom: 24px;
}

.info-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.department-info {
  margin-bottom: 20px;
}

.custom-descriptions :deep(.el-descriptions__label) {
  background: rgba(241, 245, 249, 0.8);
  font-weight: 500;
}

.info-alert {
  margin-top: 20px;
  border-radius: 10px;
}

/* 部门列表卡片 */
.departments-card {
  margin-bottom: 24px;
}

.departments-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.departments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
}

.department-item {
  padding: 20px 16px;
  background: rgba(255, 255, 255, 0.6);
  border: 2px solid rgba(226, 232, 240, 0.6);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.department-item:hover {
  border-color: #7dd3fc;
  background: rgba(56, 189, 248, 0.05);
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -8px rgba(56, 189, 248, 0.2);
}

.department-item.active {
  border-color: #7dd3fc;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  box-shadow: 0 12px 24px -8px rgba(56, 189, 248, 0.4);
}

.dept-icon {
  width: 44px;
  height: 44px;
  background: rgba(56, 189, 248, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: #7dd3fc;
  transition: all 0.3s;
}

.department-item.active .dept-icon {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.dept-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
  transition: all 0.3s;
}

.department-item.active .dept-name {
  color: white;
}

.dept-count {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
  transition: all 0.3s;
}

.department-item.active .dept-count {
  color: rgba(255, 255, 255, 0.9);
}

/* 成员列表卡片 */
.members-card {
  margin-bottom: 24px;
}

.members-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-input {
  width: 200px;
}

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

/* 职位筛选 */
.position-filter {
  margin-bottom: 24px;
  padding: 16px;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-tag {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
  padding: 6px 14px;
}

.filter-tag:hover {
  transform: translateY(-2px);
}

/* 职位分组 */
.position-group {
  margin-bottom: 28px;
}

.position-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  margin-bottom: 16px;
  border-bottom: 2px solid #e2e8f0;
}

.position-title-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.position-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
}

.position-title {
  font-weight: 700;
  font-size: 16px;
  color: #1e293b;
}

.position-count {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 12px;
  border-radius: 20px;
}

/* 成员网格 */
.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

/* 成员卡片 - 玻璃拟态 */
.member-card {
  position: relative;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(226, 232, 240, 0.6);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.member-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #7dd3fc, #38bdf8);
  transform: scaleX(0);
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.member-card:hover {
  background: rgba(255, 255, 255, 0.95);
  transform: translateY(-4px);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.1), 0 10px 20px -5px rgba(0, 0, 0, 0.05);
}

.member-card:hover::before {
  transform: scaleX(1);
}

/* 成员头像 - 渐变边框 */
.member-avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.member-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  font-weight: 700;
  position: relative;
  z-index: 1;
}

.member-avatar-wrapper::before {
  content: '';
  position: absolute;
  top: -3px;
  left: -3px;
  right: -3px;
  bottom: -3px;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 50%, #f093fb 100%);
  border-radius: 50%;
  z-index: 0;
  opacity: 0;
  transition: all 0.4s;
}

.member-card:hover .member-avatar-wrapper::before {
  opacity: 1;
  animation: rotate 3s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.member-status {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #ef4444;
  border: 2px solid white;
  z-index: 2;
}

.member-status.active {
  background: #22c55e;
}

.member-info {
  flex: 1;
  min-width: 0;
}

.member-name {
  font-weight: 700;
  color: #1e293b;
  font-size: 15px;
  margin-bottom: 2px;
}

.member-real-name {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.member-email {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.member-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.position-tag {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  border-color: transparent;
  color: #7dd3fc;
}

.status-tag {
  border-radius: 6px;
}

.dept-tag {
  border-radius: 6px;
}

.member-action {
  flex-shrink: 0;
  opacity: 0;
  transition: all 0.3s;
}

.member-card:hover .member-action {
  opacity: 1;
}

.view-btn {
  color: #7dd3fc;
}

/* 空成员状态 */
.empty-members {
  padding: 60px 0;
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

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .my-department {
    padding: 0;
  }

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
    flex-wrap: wrap;
  }

  .stats-row {
    margin-bottom: 20px;
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

  .departments-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 12px;
  }

  .department-item {
    padding: 16px 12px;
  }

  .dept-icon {
    width: 36px;
    height: 36px;
    font-size: 18px;
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
    width: 100%;
    gap: 8px;
  }

  .search-input {
    width: 100% !important;
  }

  .members-grid {
    grid-template-columns: 1fr;
  }

  .member-card {
    padding: 16px;
  }

  .member-avatar {
    width: 48px;
    height: 48px;
    font-size: 18px;
  }

  .member-action {
    opacity: 1;
  }

  .position-filter {
    padding: 12px;
  }

  .filter-tag {
    padding: 4px 10px;
    font-size: 12px;
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

  .position-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .position-count {
    align-self: flex-start;
  }
}
</style>
