<template>
  <div class="user-list">
    <!-- 权限检查 -->
    <div v-if="!isAdmin" class="permission-denied">
      <el-result
        icon="warning"
        title="权限不足"
        sub-title="您没有权限访问用户管理页面"
      >
        <template #extra>
          <el-button type="primary" @click="$router.push('/dashboard')" class="btn-gradient">
            返回首页
          </el-button>
        </template>
      </el-result>
    </div>
    
    <div v-else>
      <!-- 页面头部 - 玻璃拟态风格 -->
      <div class="page-header animate-fade-in-down">
        <div class="header-bg-decoration">
          <div class="gradient-orb orb-1"></div>
          <div class="gradient-orb orb-2"></div>
        </div>
        <div class="header-content">
          <div class="header-title">
            <div class="title-icon-wrapper">
              <el-icon class="title-icon"><UserFilled /></el-icon>
            </div>
            <div class="title-text">
              <h1>用户管理</h1>
              <p class="subtitle">管理系统用户、部门和职位</p>
            </div>
          </div>
          <div class="header-actions">
            <el-button class="btn-gradient" @click="showCreateDialog = true">
              <el-icon><Plus /></el-icon>
              新建用户
            </el-button>
            <el-button class="btn-success-gradient" @click="exportUsers('csv')">
              <el-icon><Download /></el-icon>
              导出CSV
            </el-button>
            <el-button class="btn-success-gradient" @click="exportUsers('xlsx')">
              <el-icon><Download /></el-icon>
              导出Excel
            </el-button>
            <el-button class="btn-warning-gradient" @click="importUsers">
              <el-icon><Upload /></el-icon>
              导入用户
            </el-button>
            <el-button class="btn-info-gradient" @click="showFilter = !showFilter">
              <el-icon><Filter /></el-icon>
              {{ showFilter ? '隐藏筛选' : '显示筛选' }}
            </el-button>
          </div>
        </div>
      </div>

      <!-- 统计卡片 -->
      <el-row :gutter="16" class="stats-row animate-fade-in-up">
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <div class="stat-card stat-card-primary">
            <div class="stat-icon-wrapper stat-icon-wrapper-primary">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ users.length }}</div>
              <div class="stat-label">用户总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <div class="stat-card stat-card-success">
            <div class="stat-icon-wrapper stat-icon-wrapper-success">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ activeUsersCount }}</div>
              <div class="stat-label">活跃用户</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <div class="stat-card stat-card-info">
            <div class="stat-icon-wrapper stat-icon-wrapper-info">
              <el-icon><OfficeBuilding /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ departments.length }}</div>
              <div class="stat-label">部门数量</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <div class="stat-card stat-card-secondary">
            <div class="stat-icon-wrapper stat-icon-wrapper-secondary">
              <el-icon><Postcard /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ positions.length }}</div>
              <div class="stat-label">职位数量</div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 部门列表 - 玻璃拟态卡片 -->
      <el-card shadow="never" class="department-card glass-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><OfficeBuilding /></el-icon>
              部门列表
            </span>
            <div class="card-actions">
              <el-button type="primary" size="small" @click="showCreateDepartmentDialog" class="btn-sm-gradient">
                <el-icon><Plus /></el-icon>
                新建部门
              </el-button>
              <el-button type="danger" size="small" @click="showDeleteDepartmentDialog">
                <el-icon><Delete /></el-icon>
                删除部门
              </el-button>
            </div>
          </div>
        </template>
        <div v-if="departments.length > 0" class="department-list">
          <el-tag 
            v-for="dept in departments" 
            :key="dept" 
            class="department-tag"
            effect="light"
            @click="viewDepartmentMembers(dept)"
          >
            {{ dept }}
            <el-icon class="edit-icon" @click.stop="showEditDepartmentDialogFromTag(dept)"><Edit /></el-icon>
          </el-tag>
        </div>
        <el-empty v-else description="暂无部门" :image-size="60" />
      </el-card>

      <!-- 删除部门对话框 -->
      <el-dialog 
        v-model="showDeleteDepartmentDialogVisible" 
        title="删除部门"
        width="400px"
        class="custom-dialog"
      >
        <el-form 
          ref="deleteDepartmentFormRef"
          :model="deleteDepartmentForm" 
          label-width="80px"
        >
          <el-form-item label="选择部门">
            <el-select 
              v-model="deleteDepartmentForm.departmentName" 
              placeholder="请选择要删除的部门"
              style="width: 100%"
            >
              <el-option 
                v-for="dept in departments" 
                :key="dept" 
                :label="dept" 
                :value="dept" 
              />
            </el-select>
          </el-form-item>
        </el-form>
      
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="showDeleteDepartmentDialogVisible = false">取消</el-button>
            <el-button type="danger" @click="confirmDeleteDepartment">
              删除
            </el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 职位列表 - 玻璃拟态卡片 -->
      <el-card shadow="never" class="department-card glass-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Postcard /></el-icon>
              职位列表
            </span>
            <div class="card-actions">
              <el-button type="primary" size="small" @click="showCreatePositionDialog" class="btn-sm-gradient">
                <el-icon><Plus /></el-icon>
                新建职位
              </el-button>
              <el-button type="danger" size="small" @click="showDeletePositionDialog">
                <el-icon><Delete /></el-icon>
                删除职位
              </el-button>
            </div>
          </div>
        </template>
        <div v-if="positions.length > 0" class="department-list">
          <el-tag 
            v-for="pos in positions" 
            :key="pos" 
            type="success"
            class="position-tag"
            effect="light"
            @click="viewPositionMembers(pos)"
          >
            {{ pos }}
            <el-icon class="edit-icon" @click.stop="showEditPositionDialogFromTag(pos)"><Edit /></el-icon>
          </el-tag>
        </div>
        <el-empty v-else description="暂无职位" :image-size="60" />
      </el-card>

      <!-- 删除职位对话框 -->
      <el-dialog 
        v-model="showDeletePositionDialogVisible" 
        title="删除职位"
        width="400px"
        class="custom-dialog"
      >
        <el-form 
          ref="deletePositionFormRef"
          :model="deletePositionForm" 
          label-width="80px"
        >
          <el-form-item label="选择职位">
            <el-select 
              v-model="deletePositionForm.positionName" 
              placeholder="请选择要删除的职位"
              style="width: 100%"
            >
              <el-option 
                v-for="pos in positions" 
                :key="pos" 
                :label="pos" 
                :value="pos" 
              />
            </el-select>
          </el-form-item>
        </el-form>
      
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="showDeletePositionDialogVisible = false">取消</el-button>
            <el-button type="danger" @click="confirmDeletePosition">
              删除
            </el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 创建/编辑职位对话框 -->
      <el-dialog 
        v-model="showPositionFormDialog" 
        :title="editingPosition ? '编辑职位' : '新建职位'"
        width="400px"
        class="custom-dialog"
      >
        <el-form 
          ref="positionFormRef"
          :model="positionForm" 
          label-width="80px"
        >
          <el-form-item label="职位名称" prop="name">
            <el-input v-model="positionForm.name" placeholder="请输入职位名称" />
          </el-form-item>
        </el-form>
      
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="showPositionFormDialog = false">取消</el-button>
            <el-button type="primary" @click="submitPositionForm" class="btn-gradient">
              {{ editingPosition ? '更新' : '创建' }}
            </el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 筛选表单 - 玻璃拟态卡片 -->
      <el-card v-if="showFilter" shadow="never" class="filter-card glass-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Filter /></el-icon>
              筛选条件
            </span>
          </div>
        </template>
        <el-form :model="filters" label-width="80px">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="用户名">
                <el-input v-model="filters.username" placeholder="用户名" clearable @clear="handleFilter" @keyup.enter="handleFilter" />
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="邮箱">
                <el-input v-model="filters.email" placeholder="邮箱" clearable @clear="handleFilter" @keyup.enter="handleFilter" />
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="职位">
                <el-select v-model="filters.position" placeholder="选择职位" clearable @change="handleFilter" style="width: 100%">
                  <el-option v-for="pos in positions" :key="pos" :label="pos" :value="pos" />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="状态">
                <el-select v-model="filters.is_active" placeholder="状态" clearable @clear="handleFilter">
                  <el-option label="激活" :value="true" />
                  <el-option label="禁用" :value="false" />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="部门">
                <el-input v-model="filters.department" placeholder="部门" clearable @clear="handleFilter" @keyup.enter="handleFilter" />
              </el-form-item>
            </el-col>

            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label-width="0" class="filter-actions">
                <el-button @click="resetFilter">重置</el-button>
                <el-button type="primary" @click="handleFilter" class="btn-gradient">
                  筛选
                </el-button>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>

      <!-- 用户表格 - 玻璃拟态卡片 -->
      <el-card shadow="never" class="table-card glass-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><List /></el-icon>
              用户列表
              <span class="total-count">共 {{ users.length }} 个用户</span>
            </span>
            <div class="card-actions">
              <el-button type="primary" link @click="refreshUsers" class="refresh-btn">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table :data="users" v-loading="loading" style="width: 100%" class="custom-table">
          <el-table-column prop="id" label="ID" width="80" />
          
          <el-table-column prop="username" label="用户名" width="120">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                link 
                size="small" 
                @click="viewUserDetail(row)"
                class="user-link"
              >
                {{ row.username }}
              </el-button>
            </template>
          </el-table-column>
          
          <el-table-column prop="email" label="邮箱" min-width="200" />
          
          <el-table-column prop="first_name" label="姓名" width="120">
            <template #default="{ row }">
              <span class="user-name">{{ row.last_name || '' }} {{ row.first_name || '' }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="department" label="部门" width="120">
            <template #default="{ row }">
              <span class="dept-text">{{ row.department || '-' }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="position" label="职位" width="120">
            <template #default="{ row }">
              <span class="position-text">{{ row.position || '-' }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="is_active" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'" size="small" effect="light" class="status-tag">
                {{ row.is_active ? '激活' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="employee_id" label="工号" width="100">
            <template #default="{ row }">
              <span class="employee-id">{{ row.employee_id || '-' }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="last_login" label="最后登录" width="180">
            <template #default="{ row }">
              <span class="date-text">{{ row.last_login ? formatDate(row.last_login) : '从未登录' }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              <span class="date-text">{{ formatDate(row.created_at) }}</span>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="300" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button
                  type="primary"
                  link
                  size="small"
                  @click="editUser(row)"
                  class="action-btn"
                >
                  <el-icon><Edit /></el-icon>编辑
                </el-button>
                <el-button
                  type="warning"
                  link
                  size="small"
                  @click="openPermissionDialog(row)"
                  class="action-btn"
                >
                  <el-icon><Key /></el-icon>权限
                </el-button>
                <el-button
                  type="danger"
                  link
                  size="small"
                  @click="deleteUser(row)"
                  class="action-btn"
                >
                  <el-icon><Delete /></el-icon>删除
                </el-button>
                <el-button
                  :type="row.is_active ? 'info' : 'success'"
                  link
                  size="small"
                  @click="toggleUserStatus(row)"
                  class="action-btn"
                >
                  <el-icon><Switch /></el-icon>
                  {{ row.is_active ? '禁用' : '激活' }}
                </el-button>
                <el-button
                  type="info"
                  link
                  size="small"
                  @click="resetUserPassword(row)"
                  class="action-btn"
                >
                  <el-icon><Lock /></el-icon>重置密码
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
      
      <!-- 创建/编辑用户对话框 -->
      <el-dialog 
        v-model="showCreateDialog" 
        :title="editingUser ? '编辑用户' : '新建用户'"
        width="500px"
        class="custom-dialog"
      >
        <el-form 
          ref="userFormRef" 
          :model="userForm" 
          :rules="userRules" 
          label-width="80px"
        >
          <el-form-item label="用户名" prop="username">
            <el-input v-model="userForm.username" placeholder="请输入用户名" />
          </el-form-item>
          
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="userForm.email" placeholder="请输入邮箱" />
          </el-form-item>
          
          <el-form-item label="密码" prop="password" v-if="!editingUser">
            <el-input 
              v-model="userForm.password" 
              type="password" 
              placeholder="请输入密码"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirmPassword" v-if="!editingUser">
            <el-input 
              v-model="userForm.confirmPassword" 
              type="password" 
              placeholder="请确认密码"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="姓" prop="last_name">
            <el-input v-model="userForm.last_name" placeholder="请输入姓" />
          </el-form-item>
          
          <el-form-item label="名" prop="first_name">
            <el-input v-model="userForm.first_name" placeholder="请输入名" />
          </el-form-item>
          
          <el-form-item label="部门" prop="department">
            <el-select v-model="userForm.department" placeholder="请选择或输入部门" clearable filterable allow-create style="width: 100%">
              <el-option v-for="dept in departments" :key="dept" :label="dept" :value="dept" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="职位" prop="position">
            <el-select v-model="userForm.position" placeholder="请选择或输入职位" clearable filterable allow-create style="width: 100%">
              <el-option v-for="pos in positions" :key="pos" :label="pos" :value="pos" />
            </el-select>
          </el-form-item>

          <el-form-item label="工号" prop="employee_id">
            <el-input v-model="userForm.employee_id" placeholder="请输入工号" />
          </el-form-item>

          <el-form-item label="公司电话" prop="company_phone">
            <el-input v-model="userForm.company_phone" placeholder="请输入公司电话" />
          </el-form-item>

          <el-form-item label="手机号码" prop="mobile_phone">
            <el-input v-model="userForm.mobile_phone" placeholder="请输入手机号码" />
          </el-form-item>

          <el-form-item label="生日" prop="birthday">
            <el-date-picker
              v-model="userForm.birthday"
              type="date"
              placeholder="请选择生日"
              style="width: 100%"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>

          <el-form-item label="性别" prop="gender">
            <el-select v-model="userForm.gender" placeholder="请选择性别">
              <el-option label="男" value="男" />
              <el-option label="女" value="女" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-form-item>

          <el-form-item label="工作语言" prop="work_language">
            <el-input v-model="userForm.work_language" placeholder="请输入工作语言" />
          </el-form-item>

          <el-form-item label="状态" prop="is_active">
            <el-switch
              v-model="userForm.is_active"
              active-text="激活"
              inactive-text="禁用"
            />
          </el-form-item>
        </el-form>
      
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="showCreateDialog = false">取消</el-button>
            <el-button type="primary" @click="submitUserForm" class="btn-gradient">
              {{ editingUser ? '更新' : '创建' }}
            </el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 部门人员对话框 -->
      <el-dialog 
        v-model="showDepartmentDialog" 
        :title="selectedDepartment + ' - 部门成员'"
        width="900px"
        class="custom-dialog"
      >
        <div class="department-actions-bar">
          <el-button type="primary" size="small" @click="showBatchAddDialog" class="btn-sm-gradient">
            <el-icon><Plus /></el-icon>
            批量添加成员
          </el-button>
          <el-button type="danger" size="small" :disabled="!selectedMembers.length" @click="showBatchRemoveDialog">
            <el-icon><Delete /></el-icon>
            批量移除成员
          </el-button>
        </div>
        
        <el-table 
          v-model:selection="selectedMembers"
          :data="departmentMembers" 
          style="width: 100%; margin-top: 16px;" 
          class="custom-table"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="50" />
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="username" label="用户名" width="120">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                link 
                size="small" 
                @click="viewUserDetail(row)"
                class="user-link"
              >
                {{ row.username }}
              </el-button>
            </template>
          </el-table-column>
          <el-table-column prop="email" label="邮箱" min-width="180" />
          <el-table-column prop="first_name" label="姓名" width="120">
            <template #default="{ row }">
              <span class="user-name">{{ row.last_name || '' }} {{ row.first_name || '' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="position" label="职位" width="120">
            <template #default="{ row }">
              <span class="position-text">{{ row.position || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'" size="small" effect="light">
                {{ row.is_active ? '激活' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      
        <template #footer>
          <div class="dialog-footer">
            <el-button type="warning" size="small" @click="showEditDepartmentDialog">
              编辑部门
            </el-button>
            <el-button @click="showDepartmentDialog = false">关闭</el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 职位人员对话框 -->
      <el-dialog 
        v-model="showPositionDialog" 
        :title="selectedPosition + ' - 职位成员'"
        width="900px"
        class="custom-dialog"
      >
        <el-table 
          :data="positionMembers" 
          style="width: 100%; margin-top: 16px;" 
          class="custom-table"
        >
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="username" label="用户名" width="120">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                link 
                size="small" 
                @click="viewUserDetail(row)"
                class="user-link"
              >
                {{ row.username }}
              </el-button>
            </template>
          </el-table-column>
          <el-table-column prop="email" label="邮箱" min-width="180" />
          <el-table-column prop="first_name" label="姓名" width="120">
            <template #default="{ row }">
              <span class="user-name">{{ row.last_name || '' }} {{ row.first_name || '' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="department" label="部门" width="120">
            <template #default="{ row }">
              <span class="dept-text">{{ row.department || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'" size="small" effect="light">
                {{ row.is_active ? '激活' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="showPositionDialog = false">关闭</el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 创建/编辑部门对话框 -->
      <el-dialog 
        v-model="showDepartmentFormDialog" 
        :title="editingDepartment ? '编辑部门' : '新建部门'"
        width="400px"
        class="custom-dialog"
      >
        <el-form 
          ref="departmentFormRef"
          :model="departmentForm" 
          :rules="departmentRules" 
          label-width="80px"
        >
          <el-form-item label="部门名称" prop="name">
            <el-input v-model="departmentForm.name" placeholder="请输入部门名称" />
          </el-form-item>
        </el-form>
      
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="showDepartmentFormDialog = false">取消</el-button>
            <el-button type="primary" @click="submitDepartmentForm" class="btn-gradient">
              {{ editingDepartment ? '更新' : '创建' }}
            </el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 批量添加成员对话框 -->
      <el-dialog 
        v-model="showBatchAddDialogVisible" 
        :title="'批量添加成员到 ' + selectedDepartment"
        width="700px"
        class="custom-dialog"
      >
        <div class="batch-add-content">
          <div class="filter-section">
            <el-input 
              v-model="userSearchKeyword" 
              placeholder="搜索用户名或邮箱" 
              clearable 
              @input="filterAvailableUsers"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
          <el-table 
            v-model:selection="usersToAdd"
            :data="availableUsers" 
            style="width: 100%" 
            class="custom-table"
            max-height="400"
          >
            <el-table-column type="selection" width="50" />
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="email" label="邮箱" min-width="180" />
            <el-table-column prop="department" label="当前部门" width="120">
              <template #default="{ row }">
                <span class="dept-text">{{ row.department || '未分配' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="position" label="职位" width="100">
              <template #default="{ row }">
                <span class="position-text">{{ row.position || '-' }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="showBatchAddDialogVisible = false">取消</el-button>
            <el-button type="primary" :disabled="usersToAdd.length === 0" @click="submitBatchAdd" class="btn-gradient">
              添加 ({{ usersToAdd.length }})
            </el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 批量移除成员确认对话框 -->
      <el-dialog 
        v-model="showBatchRemoveDialogVisible" 
        :title="'确认移除成员'"
        width="400px"
        class="custom-dialog"
      >
        <div class="batch-remove-content">
          <p>确定要从 <strong>{{ selectedDepartment }}</strong> 部门移除以下 <strong>{{ selectedMembers.length }}</strong> 个成员吗？</p>
          <div class="remove-list">
            <el-tag v-for="member in selectedMembers" :key="member.id" class="remove-tag" type="danger">
              {{ member.username }}
            </el-tag>
          </div>
        </div>
      
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="showBatchRemoveDialogVisible = false">取消</el-button>
            <el-button type="danger" @click="submitBatchRemove">
              确认移除
            </el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 权限管理对话框 -->
      <el-dialog
        v-model="showPermissionDialog"
        title="用户权限管理"
        width="800px"
        class="custom-dialog"
      >
        <div v-if="permissionLoading" class="permission-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          加载中...
        </div>
        <div v-else-if="permissionUser" class="permission-content">
          <el-alert
            v-if="permissionUser.is_super_admin"
            title="系统管理员"
            type="warning"
            description="此用户为系统管理员，拥有系统全部权限，无法修改"
            :closable="false"
            show-icon
            class="admin-alert"
          />
          <div class="permission-user-info">
            <el-avatar :size="50" class="user-avatar">
              {{ permissionUser.username?.charAt(0).toUpperCase() }}
            </el-avatar>
            <div class="user-info-text">
              <h4>{{ permissionUser.username }}</h4>
              <el-tag v-if="permissionUser.position" size="small" type="info">
                {{ permissionUser.position }}
              </el-tag>
            </div>
          </div>

          <el-divider />

          <div class="permission-section">
            <h4>职位权限</h4>
            <p class="permission-desc">基于用户职位的默认权限</p>
            <div v-if="currentRolePermissions.length > 0" class="permission-tags">
              <el-tag
                v-for="perm in currentRolePermissions"
                :key="perm.code"
                size="small"
                type="info"
                class="permission-tag"
                effect="light"
              >
                {{ perm.name }}
              </el-tag>
            </div>
            <el-tag v-else size="small" type="success" effect="light">拥有全部权限</el-tag>
          </div>

          <el-divider />

          <div class="permission-section">
            <h4>自定义权限</h4>
            <p class="permission-desc">在职位权限基础上额外添加或移除的权限</p>
            <el-tabs v-model="permissionTabActive" class="permission-tabs">
              <el-tab-pane label="额外权限" name="allowed">
                <div class="permission-category" v-for="(category, key) in allPermissions" :key="key">
                  <h5>{{ category.name }}</h5>
                  <el-checkbox-group v-model="selectedAllowedPermissions">
                    <el-checkbox
                      v-for="perm in category.permissions"
                      :key="perm.code"
                      :label="perm.code"
                      :disabled="permissionUser.is_super_admin"
                    >
                      {{ perm.name }}
                      <span class="perm-desc">{{ perm.description }}</span>
                    </el-checkbox>
                  </el-checkbox-group>
                </div>
              </el-tab-pane>
              <el-tab-pane label="限制权限" name="denied">
                <div class="permission-category" v-for="(category, key) in allPermissions" :key="key">
                  <h5>{{ category.name }}</h5>
                  <el-checkbox-group v-model="selectedDeniedPermissions">
                    <el-checkbox
                      v-for="perm in category.permissions"
                      :key="perm.code"
                      :label="perm.code"
                      :disabled="permissionUser.is_super_admin"
                    >
                      {{ perm.name }}
                      <span class="perm-desc">{{ perm.description }}</span>
                    </el-checkbox>
                  </el-checkbox-group>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>

        <template #footer>
          <div class="dialog-footer">
            <el-button @click="showPermissionDialog = false">取消</el-button>
            <el-button
              type="primary"
              @click="saveUserPermissions"
              :disabled="permissionUser?.is_super_admin"
              class="btn-gradient"
            >
              保存
            </el-button>
          </div>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Download, 
  Upload, 
  Plus, 
  Filter, 
  Refresh, 
  Delete, 
  Loading, 
  Edit, 
  UserFilled, 
  User, 
  CircleCheck, 
  OfficeBuilding, 
  Postcard, 
  List,
  Key,
  Switch,
  Lock,
  Search
} from '@element-plus/icons-vue'
import { apiService as api } from '@/services/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const router = useRouter()
const loading = ref(false)
const users = ref([])
const showCreateDialog = ref(false)
const editingUser = ref(null)
const userFormRef = ref(null)
const showFilter = ref(false)
const departments = ref([])
const showDepartmentDialog = ref(false)
const showPositionDialog = ref(false)
const positionMembers = ref([])
const selectedPosition = ref('')
const departmentMembers = ref([])
const selectedDepartment = ref('')
const selectedMembers = ref([])
const showDepartmentFormDialog = ref(false)
const editingDepartment = ref(null)
const departmentFormRef = ref(null)
const departmentForm = reactive({
  name: ''
})
const departmentRules = {
  name: [
    { required: true, message: '请输入部门名称', trigger: 'blur' }
  ]
}
const showBatchAddDialogVisible = ref(false)
const showBatchRemoveDialogVisible = ref(false)
const allUsers = ref([])
const availableUsers = ref([])
const usersToAdd = ref([])
const userSearchKeyword = ref('')
const showDeleteDepartmentDialogVisible = ref(false)
const deleteDepartmentFormRef = ref(null)
const deleteDepartmentForm = reactive({
  departmentName: ''
})

const positions = ref([])
const showDeletePositionDialogVisible = ref(false)
const showPositionFormDialog = ref(false)
const editingPosition = ref(null)
const positionFormRef = ref(null)
const positionForm = reactive({
  name: ''
})
const deletePositionFormRef = ref(null)
const deletePositionForm = reactive({
  positionName: ''
})

const showPermissionDialog = ref(false)
const permissionUser = ref(null)
const permissionLoading = ref(false)
const permissionTabActive = ref('allowed')
const allPermissions = ref({})
const selectedAllowedPermissions = ref([])
const selectedDeniedPermissions = ref([])
const currentRolePermissions = ref([])

// 筛选条件
const filters = reactive({
  username: '',
  email: '',
  is_active: null,
  department: '',
  position: ''
})

// 检查当前用户是否为管理员
const isAdmin = computed(() => {
  const user = userStore.currentUser
  if (!user) return false
  if (user.is_super_admin) return true
  if (user.is_admin) return true
  return user.position === '系统管理员' ||
         user.position === '管理员' ||
         user.position === '经理' ||
         user.position === '项目经理' ||
         user.position === '部门经理' ||
         user.position === '人事专员' ||
         user.position?.includes('经理')
})

// 统计计算属性
const activeUsersCount = computed(() => {
  return users.value.filter(u => u.is_active).length
})

const userForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  first_name: '',
  last_name: '',
  department: '',
  position: '',
  employee_id: '',
  company_phone: '',
  phone: '',
  mobile_phone: '',
  birthday: '',
  gender: '',
  work_language: '',
  is_active: true
})

const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== userForm.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 获取用户列表
const fetchUsers = async () => {
  if (!isAdmin.value) {
    return
  }
  
  loading.value = true
  try {
    const response = await api.users.getList()
    users.value = response.users || []
  } catch (error) {
    console.error('获取用户列表失败:', error)
    if (error.response?.status === 403) {
      ElMessage.error('权限不足，无法查看用户列表')
    } else {
      ElMessage.error('获取用户列表失败')
    }
  } finally {
    loading.value = false
  }
}

// 获取部门列表
const fetchDepartments = async () => {
  try {
    const response = await api.users.getDepartments()
    departments.value = response.departments || []
  } catch (error) {
    console.error('获取部门列表失败:', error)
  }
}

// 获取职位列表
const fetchPositions = async () => {
  try {
    const response = await api.users.getPositions()
    positions.value = response.positions || []
  } catch (error) {
    console.error('获取职位列表失败:', error)
  }
}

// 显示删除职位对话框
const showDeletePositionDialog = () => {
  deletePositionForm.positionName = ''
  showDeletePositionDialogVisible.value = true
}

// 确认删除职位
const confirmDeletePosition = async () => {
  if (!deletePositionForm.positionName) {
    ElMessage.warning('请选择要删除的职位')
    return
  }
  
  try {
    await api.users.deletePosition(deletePositionForm.positionName)
    ElMessage.success('职位删除成功')
    showDeletePositionDialogVisible.value = false
    fetchPositions()
  } catch (error) {
    console.error('删除职位失败:', error)
    ElMessage.error(error.response?.data?.error || '删除职位失败')
  }
}

// 显示创建职位对话框
const showCreatePositionDialog = () => {
  editingPosition.value = null
  positionForm.name = ''
  showPositionFormDialog.value = true
}

// 提交职位表单
const submitPositionForm = async () => {
  if (!positionFormRef.value) return
  
  await positionFormRef.value.validate()
  
  try {
    if (editingPosition.value) {
      await api.users.updatePosition(editingPosition.value, positionForm.name)
      ElMessage.success('职位更新成功')
    } else {
      await api.users.createPosition(positionForm.name)
      ElMessage.success('职位创建成功')
    }
    showPositionFormDialog.value = false
    fetchPositions()
  } catch (error) {
    console.error('提交职位失败:', error)
    ElMessage.error(error.response?.data?.error || '提交职位失败')
  }
}

// 查看部门人员
const viewDepartmentMembers = async (departmentName) => {
  selectedDepartment.value = departmentName
  selectedMembers.value = []
  showDepartmentDialog.value = true
  try {
    const response = await api.users.getDepartmentMembers(departmentName)
    departmentMembers.value = response.members || []
  } catch (error) {
    console.error('获取部门人员失败:', error)
    ElMessage.error('获取部门人员失败')
  }
}

// 查看职位人员
const viewPositionMembers = async (positionName) => {
  selectedPosition.value = positionName
  showPositionDialog.value = true
  try {
    const response = await api.users.getPositionMembers(positionName)
    positionMembers.value = response.members || []
  } catch (error) {
    console.error('获取职位人员失败:', error)
    ElMessage.error('获取职位人员失败')
  }
}

// 显示删除部门对话框
const showDeleteDepartmentDialog = () => {
  deleteDepartmentForm.departmentName = ''
  showDeleteDepartmentDialogVisible.value = true
}

// 确认删除部门
const confirmDeleteDepartment = async () => {
  if (!deleteDepartmentForm.departmentName) {
    ElMessage.warning('请选择要删除的部门')
    return
  }
  
  try {
    await api.users.deleteDepartment(deleteDepartmentForm.departmentName)
    ElMessage.success('部门删除成功')
    showDeleteDepartmentDialogVisible.value = false
    fetchDepartments()
  } catch (error) {
    console.error('删除部门失败:', error)
    ElMessage.error(error.response?.data?.error || '删除部门失败')
  }
}

// 显示创建部门对话框
const showCreateDepartmentDialog = () => {
  editingDepartment.value = null
  departmentForm.name = ''
  showDepartmentFormDialog.value = true
}

// 显示编辑部门对话框
const showEditDepartmentDialog = () => {
  editingDepartment.value = selectedDepartment.value
  departmentForm.name = selectedDepartment.value
  showDepartmentFormDialog.value = true
}

// 从标签点击编辑部门
const showEditDepartmentDialogFromTag = (dept) => {
  editingDepartment.value = dept
  departmentForm.name = dept
  showDepartmentFormDialog.value = true
}

// 从标签点击编辑职位
const showEditPositionDialogFromTag = (pos) => {
  editingPosition.value = pos
  positionForm.name = pos
  showPositionFormDialog.value = true
}

// 提交部门表单
const submitDepartmentForm = async () => {
  if (!departmentFormRef.value) return
  
  try {
    await departmentFormRef.value.validate()
    
    if (editingDepartment.value) {
      await api.users.updateDepartment(editingDepartment.value, departmentForm.name)
      ElMessage.success('部门更新成功')
    } else {
      await api.users.createDepartment(departmentForm.name)
      ElMessage.success('部门创建成功')
    }
    
    showDepartmentFormDialog.value = false
    fetchDepartments()
    if (selectedDepartment.value && editingDepartment.value) {
      selectedDepartment.value = departmentForm.name
      viewDepartmentMembers(departmentForm.name)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('提交部门失败:', error)
      ElMessage.error(error.response?.data?.error || '提交部门失败')
    }
  }
}

// 处理选择变化
const handleSelectionChange = (selection) => {
  selectedMembers.value = selection
}

// 显示批量添加对话框
const showBatchAddDialog = async () => {
  usersToAdd.value = []
  userSearchKeyword.value = ''
  showBatchAddDialogVisible.value = true
  
  try {
    const response = await api.users.getList({ per_page: 1000 })
    const allUserList = response.users || []
    allUsers.value = allUserList
    filterAvailableUsers()
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  }
}

// 筛选可用用户
const filterAvailableUsers = () => {
  const keyword = userSearchKeyword.value.toLowerCase()
  const currentDeptMembers = departmentMembers.value.map(m => m.id)
  
  availableUsers.value = allUsers.value.filter(user => {
    if (currentDeptMembers.includes(user.id)) return false
    if (!keyword) return true
    return user.username.toLowerCase().includes(keyword) || 
           user.email.toLowerCase().includes(keyword)
  })
}

// 提交批量添加
const submitBatchAdd = async () => {
  if (usersToAdd.value.length === 0) return
  
  try {
    const userIds = usersToAdd.value.map(u => u.id)
    await api.users.batchAddDepartmentMembers(selectedDepartment.value, userIds)
    ElMessage.success(`成功添加 ${userIds.length} 个成员`)
    showBatchAddDialogVisible.value = false
    viewDepartmentMembers(selectedDepartment.value)
    fetchUsers()
  } catch (error) {
    console.error('批量添加成员失败:', error)
    ElMessage.error(error.response?.data?.error || '批量添加成员失败')
  }
}

// 显示批量移除对话框
const showBatchRemoveDialog = () => {
  showBatchRemoveDialogVisible.value = true
}

// 提交批量移除
const submitBatchRemove = async () => {
  if (selectedMembers.value.length === 0) return
  
  try {
    const userIds = selectedMembers.value.map(m => m.id)
    await api.users.batchRemoveDepartmentMembers(selectedDepartment.value, userIds)
    ElMessage.success(`成功移除 ${userIds.length} 个成员`)
    showBatchRemoveDialogVisible.value = false
    selectedMembers.value = []
    viewDepartmentMembers(selectedDepartment.value)
    fetchUsers()
  } catch (error) {
    console.error('批量移除成员失败:', error)
    ElMessage.error(error.response?.data?.error || '批量移除成员失败')
  }
}

// 筛选用户
const handleFilter = () => {
  if (!users.value.length) return
  
  const filteredUsers = users.value.filter(user => {
    return (
      (!filters.username || user.username?.toLowerCase().includes(filters.username.toLowerCase())) &&
      (!filters.email || user.email?.toLowerCase().includes(filters.email.toLowerCase())) &&
      (filters.is_active === null || user.is_active === filters.is_active) &&
      (!filters.department || user.department?.toLowerCase().includes(filters.department.toLowerCase())) &&
      (!filters.position || user.position?.toLowerCase().includes(filters.position.toLowerCase()))
    )
  })
  
  users.value = filteredUsers
  ElMessage.success(`筛选到 ${filteredUsers.length} 个用户`)
}

// 重置筛选
const resetFilter = () => {
  Object.keys(filters).forEach(key => {
    filters[key] = key === 'is_active' ? null : ''
  })
  fetchUsers()
  ElMessage.success('筛选条件已重置')
}

// 刷新用户列表
const refreshUsers = () => {
  fetchUsers()
  ElMessage.success('用户列表已刷新')
}

// 创建用户
const createUser = async (data) => {
  if (!isAdmin.value) {
    ElMessage.error('权限不足，无法创建用户')
    return
  }
  
  try {
    await api.users.create(data)
    ElMessage.success('用户创建成功')
    showCreateDialog.value = false
    resetUserForm()
    fetchUsers()
  } catch (error) {
    console.error('创建用户失败:', error)
    if (error.response?.status === 403) {
      ElMessage.error('权限不足，无法创建用户')
    } else {
      ElMessage.error('创建用户失败')
    }
  }
}

// 更新用户
const updateUser = async (id, data) => {
  if (!isAdmin.value) {
    ElMessage.error('权限不足，无法更新用户')
    return
  }
  
  try {
    await api.users.update(id, data)
    ElMessage.success('用户更新成功')
    showCreateDialog.value = false
    resetUserForm()
    fetchUsers()
  } catch (error) {
    console.error('更新用户失败:', error)
    if (error.response?.status === 403) {
      ElMessage.error('权限不足，无法更新用户')
    } else {
      ElMessage.error('更新用户失败')
    }
  }
}

// 删除用户
const deleteUser = async (user) => {
  if (!isAdmin.value) {
    ElMessage.error('权限不足，无法删除用户')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.users.delete(user.id)
    ElMessage.success('用户删除成功')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      if (error.response?.status === 403) {
        ElMessage.error('权限不足，无法删除用户')
      } else {
        ElMessage.error('删除用户失败')
      }
    }
  }
}

// 切换用户状态
const toggleUserStatus = async (user) => {
  if (!isAdmin.value) {
    ElMessage.error('权限不足，无法修改用户状态')
    return
  }
  
  try {
    const newStatus = !user.is_active
    const action = newStatus ? '激活' : '禁用'
    
    await ElMessageBox.confirm(
      `确定要${action}用户 "${user.username}" 吗？`,
      `确认${action}`,
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.users.update(user.id, {
      is_active: newStatus
    })
    
    ElMessage.success(`用户${action}成功`)
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('切换用户状态失败:', error)
      if (error.response?.status === 403) {
        ElMessage.error('权限不足，无法修改用户状态')
      } else {
        ElMessage.error('切换用户状态失败')
      }
    }
  }
}

// 查看用户详情
const viewUserDetail = (user) => {
  router.push(`/users/${user.id}`)
}

// 重置用户密码
const resetUserPassword = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要重置用户 "${user.username}" 的密码吗？重置后密码将设置为默认密码。`,
      '确认重置密码',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.users.resetPassword(user.id, { password: '123456' })
    ElMessage.success('密码重置成功，新密码为：123456')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重置密码失败:', error)
      ElMessage.error('重置密码失败')
    }
  }
}

// 编辑用户
const editUser = (user) => {
  editingUser.value = user
  userForm.username = user.username || ''
  userForm.email = user.email || ''
  userForm.first_name = user.first_name || ''
  userForm.last_name = user.last_name || ''
  userForm.department = user.department || ''
  userForm.position = user.position || ''
  userForm.employee_id = user.employee_id || ''
  userForm.company_phone = user.company_phone || ''
  userForm.phone = user.phone || ''
  userForm.mobile_phone = user.mobile_phone || ''
  userForm.birthday = user.birthday || ''
  userForm.gender = user.gender || ''
  userForm.work_language = user.work_language || ''
  userForm.is_active = user.is_active !== false
  showCreateDialog.value = true
}

// 提交用户表单
const submitUserForm = async () => {
  if (!userFormRef.value) return
  
  try {
    await userFormRef.value.validate()
    
    const formData = { ...userForm }
    delete formData.confirmPassword
    if (editingUser.value) {
      delete formData.password
    }

    if (editingUser.value) {
      await updateUser(editingUser.value.id, formData)
    } else {
      await createUser(formData)
    }
  } catch (error) {
    // 表单验证失败
  }
}

// 重置用户表单
const resetUserForm = () => {
  userForm.username = ''
  userForm.email = ''
  userForm.password = ''
  userForm.confirmPassword = ''
  userForm.first_name = ''
  userForm.last_name = ''
  userForm.department = ''
  userForm.position = ''
  userForm.employee_id = ''
  userForm.company_phone = ''
  userForm.phone = ''
  userForm.mobile_phone = ''
  userForm.birthday = ''
  userForm.gender = ''
  userForm.work_language = ''
  userForm.is_active = true
  editingUser.value = null
  if (userFormRef.value) {
    userFormRef.value.resetFields()
  }
}

// 打开权限管理对话框
const openPermissionDialog = async (user) => {
  permissionUser.value = user
  showPermissionDialog.value = true
  permissionLoading.value = true
  permissionTabActive.value = 'allowed'
  selectedAllowedPermissions.value = []
  selectedDeniedPermissions.value = []
  currentRolePermissions.value = []

  try {
    const [permsResponse, userPermsResponse] = await Promise.all([
      api.users.getAllPermissions(),
      api.users.getUserPermissions(user.id)
    ])

    allPermissions.value = permsResponse.permissions || {}

    if (userPermsResponse.position) {
      const posPerms = userPermsResponse.position_permissions || []
      const permMap = {}
      Object.values(allPermissions.value).forEach(cat => {
        cat.permissions.forEach(p => {
          permMap[p.code] = p
        })
      })
      currentRolePermissions.value = posPerms.map(code => permMap[code] || { code, name: code })
    }

    if (userPermsResponse.is_super_admin || (userPermsResponse.position && userPermsResponse.position.is_admin)) {
      permissionUser.value = { ...user, is_super_admin: true }
    } else {
      permissionUser.value = { ...user, is_super_admin: false }
    }

    const customPerms = userPermsResponse.custom_permissions || {}
    selectedAllowedPermissions.value = customPerms.allowed || []
    selectedDeniedPermissions.value = customPerms.denied || []
  } catch (error) {
    console.error('获取权限信息失败:', error)
    ElMessage.error('获取权限信息失败')
  } finally {
    permissionLoading.value = false
  }
}

// 保存用户权限
const saveUserPermissions = async () => {
  if (!permissionUser.value || permissionUser.value.is_super_admin) {
    ElMessage.warning('无法修改系统管理员的权限')
    return
  }

  if (permissionUser.value.position && permissionUser.value.position.is_admin) {
    ElMessage.warning('无法修改管理员的权限')
    return
  }

  try {
    await api.users.updateUserPermissions(permissionUser.value.id, {
      allowed: selectedAllowedPermissions.value,
      denied: selectedDeniedPermissions.value
    })
    ElMessage.success('权限更新成功')
    showPermissionDialog.value = false
  } catch (error) {
    console.error('保存权限失败:', error)
    ElMessage.error(error.response?.data?.error || '保存权限失败')
  }
}

// 格式化日期
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 导出用户数据
const exportUsers = async (format) => {
  try {
    const response = await api.users.exportUsers(format)
    
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    const timestamp = new Date().toISOString().slice(0, 10)
    const extension = format === 'csv' ? 'csv' : 'xlsx'
    link.download = `用户数据_${timestamp}.${extension}`
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(`用户数据导出成功`)
  } catch (error) {
    console.error('导出用户数据失败:', error)
    ElMessage.error('导出用户数据失败')
  }
}

// 导入用户数据
const importUsers = async () => {
  try {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.csv,.xlsx'
    
    input.onchange = async (event) => {
      const file = event.target.files[0]
      if (!file) return
      
      const fileExtension = file.name.split('.').pop().toLowerCase()
      if (!['csv', 'xlsx'].includes(fileExtension)) {
        ElMessage.error('请选择CSV或Excel文件')
        return
      }
      
      await ElMessageBox.confirm(
        `确定要导入文件 "${file.name}" 吗？这将批量创建或更新用户数据。`,
        '确认导入',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      const formData = new FormData()
      formData.append('file', file)
      
      try {
        const response = await api.users.importUsers(formData)
        ElMessage.success(`用户数据导入成功，共处理 ${response.processed || response.data?.processed} 条记录`)
        fetchUsers()
      } catch (error) {
        console.error('导入用户数据失败:', error)
        ElMessage.error('导入用户数据失败')
      }
    }
    
    input.click()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('导入操作取消:', error)
    }
  }
}

// 监听对话框关闭
watch(showCreateDialog, (newVal) => {
  if (!newVal) {
    resetUserForm()
  }
})

onMounted(() => {
  fetchUsers()
  fetchDepartments()
  fetchPositions()
})
</script>

<style scoped>
.user-list {
  padding: 0;
}

/* 页面头部样式 */
.page-header {
  position: relative;
  margin-bottom: 24px;
  padding: 24px;
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--secondary-600) 100%);
  border-radius: var(--radius-lg);
  overflow: hidden;
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
  opacity: 0.4;
}

.orb-1 {
  width: 200px;
  height: 200px;
  background: var(--accent-400);
  top: -50px;
  right: 10%;
  animation: float 6s ease-in-out infinite;
}

.orb-2 {
  width: 150px;
  height: 150px;
  background: var(--success-400);
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
  gap: 16px;
}

.title-icon-wrapper {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.title-icon {
  font-size: 28px;
  color: white;
}

.title-text h1 {
  margin: 0;
  color: white;
  font-size: 28px;
  font-weight: 700;
}

.subtitle {
  margin: 4px 0 0 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-success-gradient {
  background: linear-gradient(135deg, var(--success-500) 0%, var(--success-600) 100%);
  border: none;
  color: white;
}

.btn-success-gradient:hover {
  background: linear-gradient(135deg, var(--success-600) 0%, var(--success-700) 100%);
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-success);
}

.btn-warning-gradient {
  background: linear-gradient(135deg, var(--warning-500) 0%, var(--warning-600) 100%);
  border: none;
  color: white;
}

.btn-warning-gradient:hover {
  background: linear-gradient(135deg, var(--warning-600) 0%, var(--warning-700) 100%);
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-warning);
}

.btn-info-gradient {
  background: linear-gradient(135deg, var(--info-500) 0%, var(--info-600) 100%);
  border: none;
  color: white;
}

.btn-info-gradient:hover {
  background: linear-gradient(135deg, var(--info-600) 0%, var(--info-700) 100%);
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-info);
}

.btn-sm-gradient {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  border: none;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  background: var(--bg-elevated);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--gradient-primary);
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-card-primary {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  color: white;
}

.stat-card-success {
  background: linear-gradient(135deg, var(--success-500) 0%, var(--success-600) 100%);
  color: white;
}

.stat-card-info {
  background: linear-gradient(135deg, var(--secondary-500) 0%, var(--secondary-600) 100%);
  color: white;
}

.stat-card-secondary {
  background: linear-gradient(135deg, var(--neutral-500) 0%, var(--neutral-600) 100%);
  color: white;
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: all var(--transition-normal);
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.stat-card:hover .stat-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
  color: white;
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  margin-top: 4px;
}

/* 玻璃拟态卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  margin-bottom: 24px;
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
  gap: 8px;
  font-weight: 600;
  color: var(--text-primary);
}

.total-count {
  margin-left: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: normal;
}

.card-actions {
  display: flex;
  gap: 8px;
}

/* 部门列表 */
.department-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.department-tag,
.position-tag {
  cursor: pointer;
  padding: 8px 16px;
  font-size: 14px;
  transition: all var(--transition-normal);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: var(--radius-md);
}

.department-tag:hover,
.position-tag:hover {
  transform: scale(1.05);
  box-shadow: var(--shadow-md);
}

.department-tag .edit-icon,
.position-tag .edit-icon {
  font-size: 12px;
  opacity: 0.6;
  transition: all var(--transition-fast);
}

.department-tag .edit-icon:hover,
.position-tag .edit-icon:hover {
  opacity: 1;
  color: var(--primary-500);
  transform: scale(1.2);
}

/* 筛选卡片 */
.filter-card {
  margin-bottom: 24px;
}

.filter-actions {
  display: flex;
  gap: 8px;
}

/* 表格卡片 */
.table-card {
  margin-bottom: 24px;
}

.custom-table {
  --el-table-header-bg-color: var(--neutral-50);
  --el-table-row-hover-bg-color: var(--primary-50);
}

:deep(.el-table th) {
  font-weight: 600;
  color: var(--text-primary);
  background: var(--neutral-50);
}

.user-link {
  font-weight: 500;
}

.user-name,
.dept-text,
.position-text,
.employee-id {
  color: var(--text-secondary);
}

.status-tag {
  border-radius: var(--radius-sm);
}

.date-text {
  color: var(--text-secondary);
  font-size: 13px;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 4px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.department-actions-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

/* 批量添加 */
.batch-add-content {
  min-height: 400px;
}

.filter-section {
  margin-bottom: 16px;
}

/* 批量移除 */
.batch-remove-content {
  padding: 16px 0;
}

.batch-remove-content p {
  margin-bottom: 16px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.remove-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.remove-tag {
  margin: 4px;
}

/* 权限管理 */
.permission-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  color: var(--text-secondary);
}

.permission-content {
  max-height: 60vh;
  overflow-y: auto;
}

.admin-alert {
  margin-bottom: 16px;
}

.permission-user-info {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 0;
}

.user-avatar {
  background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
  color: white;
  font-weight: 600;
}

.user-info-text h4 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.permission-section {
  margin-bottom: 20px;
}

.permission-section h4 {
  margin: 0 0 4px 0;
  color: var(--text-primary);
}

.permission-desc {
  margin: 0 0 12px 0;
  color: var(--text-tertiary);
  font-size: 13px;
}

.permission-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.permission-tag {
  margin-bottom: 4px;
  border-radius: var(--radius-sm);
}

.permission-category {
  margin-bottom: 16px;
}

.permission-category h5 {
  margin: 0 0 8px 0;
  color: var(--text-secondary);
  font-weight: 500;
}

.permission-category .el-checkbox {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
  white-space: normal;
}

.permission-category .el-checkbox .perm-desc {
  display: block;
  font-size: 12px;
  color: var(--text-tertiary);
  margin-left: 20px;
}

.permission-tabs {
  margin-top: 16px;
}

/* 权限拒绝页面 */
.permission-denied {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

/* 动画 */
.animate-fade-in-down {
  animation: fadeInDown 0.6s ease-out;
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-15px);
  }
}

/* 响应式适配 */
@media (max-width: 768px) {
  .page-header {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .title-text h1 {
    font-size: 20px;
  }
  
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .stats-row .el-col {
    margin-bottom: 12px;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-value {
    font-size: 22px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .card-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .filter-actions {
    width: 100%;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }
  
  .permission-user-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}

@media screen and (max-width: 480px) {
  .title-icon-wrapper {
    width: 44px;
    height: 44px;
  }
  
  .title-icon {
    font-size: 22px;
  }
  
  .title-text h1 {
    font-size: 18px;
  }
  
  .subtitle {
    font-size: 12px;
  }
  
  .stat-icon-wrapper {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .stat-label {
    font-size: 12px;
  }
  
  .department-tag,
  .position-tag {
    font-size: 12px;
    padding: 6px 12px;
  }
}
</style>
