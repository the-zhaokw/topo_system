<template>
  <div class="module-permissions">
    <!-- 权限检查 -->
    <div v-if="!isAdmin" class="permission-denied">
      <el-result
        icon="warning"
        title="权限不足"
        sub-title="您没有权限访问模块权限管理页面"
      >
        <template #extra>
          <el-button type="primary" @click="$router.push('/dashboard')">
            返回首页
          </el-button>
        </template>
      </el-result>
    </div>

    <div v-else>
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="header-title">
            <div class="title-icon-wrapper">
              <el-icon class="title-icon"><Lock /></el-icon>
            </div>
            <div class="title-text">
              <h1>模块权限管理</h1>
              <p class="subtitle">控制每个用户可以看到的系统大功能模块（侧边栏一级菜单）</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 统计卡片 -->
      <el-row :gutter="16" class="stats-row">
        <el-col :xs="12" :sm="8" :md="6">
          <div class="stat-card stat-card-primary">
            <div class="stat-icon-wrapper stat-icon-wrapper-primary">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ total }}</div>
              <div class="stat-label">用户总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <div class="stat-card stat-card-success">
            <div class="stat-icon-wrapper stat-icon-wrapper-success">
              <el-icon><Grid /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ catalog.length }}</div>
              <div class="stat-label">系统模块数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <div class="stat-card stat-card-info">
            <div class="stat-icon-wrapper stat-icon-wrapper-info">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ defaultCount }}</div>
              <div class="stat-label">默认可见模块</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <div class="stat-card stat-card-warning">
            <div class="stat-icon-wrapper stat-icon-wrapper-warning">
              <el-icon><SetUp /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ customCount }}</div>
              <div class="stat-label">已自定义配置</div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 主内容 -->
      <el-card shadow="never" class="main-card">
        <!-- 工具栏 -->
        <div class="toolbar">
          <el-input
            v-model="searchKeyword"
            placeholder="按用户名/邮箱/姓名搜索"
            style="width: 280px;"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button @click="refreshList">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>

        <!-- 用户列表 -->
        <el-table
          v-loading="loading"
          :data="userList"
          stripe
          style="width: 100%"
          :header-cell-style="{ background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)', color: '#0c4a6e', fontWeight: 600 }"
        >
          <el-table-column prop="username" label="用户名" min-width="120">
            <template #default="{ row }">
              <div class="user-cell">
                <el-avatar :size="32" :src="row.avatar || '/avatar-placeholder.png'">
                  {{ row.username?.charAt(0).toUpperCase() }}
                </el-avatar>
                <div class="user-info">
                  <div class="user-name">{{ row.username }}</div>
                  <div class="user-sub" v-if="row.first_name || row.last_name">
                    {{ row.last_name }}{{ row.first_name }}
                  </div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="email" label="邮箱" min-width="200" show-overflow-tooltip />
          <el-table-column label="部门/职位" min-width="160">
            <template #default="{ row }">
              <div class="dept-cell">
                <el-tag v-if="row.department" size="small" type="info">{{ row.department }}</el-tag>
                <span v-if="row.department && row.position" class="separator">·</span>
                <span class="position-text">{{ row.position || '-' }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="身份" width="110">
            <template #default="{ row }">
              <el-tag v-if="row.is_super_admin" type="danger" size="small">系统管理员</el-tag>
              <el-tag v-else-if="row.is_admin" type="warning" size="small">管理员</el-tag>
              <el-tag v-else type="info" size="small">普通用户</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="可见模块" min-width="200">
            <template #default="{ row }">
              <div v-if="row.is_super_admin" class="module-tags">
                <el-tag type="danger" size="small" effect="dark">全部模块</el-tag>
              </div>
              <div v-else class="module-tags">
                <el-tag
                  v-for="code in row.accessible_modules.slice(0, 4)"
                  :key="code"
                  size="small"
                  class="module-tag"
                  effect="plain"
                >
                  {{ getModuleName(code) }}
                </el-tag>
                <el-tag
                  v-if="row.accessible_modules.length > 4"
                  size="small"
                  type="info"
                  class="module-tag"
                >
                  +{{ row.accessible_modules.length - 4 }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="配置状态" width="110">
            <template #default="{ row }">
              <el-tag
                v-if="row.is_super_admin"
                type="danger"
                size="small"
              >系统默认</el-tag>
              <el-tag
                v-else-if="row.is_default"
                type="success"
                size="small"
              >系统默认</el-tag>
              <el-tag v-else type="warning" size="small">已自定义</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="260" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                link
                v-permission="'module_perm:edit'"
                :disabled="row.is_super_admin"
                @click="openEditDialog(row)"
              >
                <el-icon><Setting /></el-icon>
                配置模块
              </el-button>
              <el-button
                v-permission="'template:apply'"
                type="success"
                size="small"
                link
                :disabled="row.is_super_admin"
                @click="openApplyToUserDialog(row)"
              >
                <el-icon><Promotion /></el-icon>
                应用模板
              </el-button>
              <el-button
                v-if="!row.is_super_admin && !row.is_default"
                type="info"
                size="small"
                link
                v-permission="'module_perm:reset'"
                @click="handleReset(row)"
              >
                <el-icon><RefreshLeft /></el-icon>
                重置默认
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.per_page"
            :total="total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 配置模块对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="`配置可见模块 - ${editingUser?.username || ''}`"
      width="880px"
      :close-on-click-modal="false"
      @closed="handleDialogClosed"
    >
      <div v-if="editingUser" class="edit-dialog-content">
        <el-alert
          v-if="editingUser.is_super_admin"
          type="warning"
          :closable="false"
          title="系统管理员默认拥有所有模块，无需配置"
          show-icon
        />
        <template v-else>
          <div class="user-summary">
            <el-avatar :size="48" :src="editingUser.avatar || '/avatar-placeholder.png'">
              {{ editingUser.username?.charAt(0).toUpperCase() }}
            </el-avatar>
            <div class="summary-info">
              <div class="summary-name">
                {{ editingUser.username }}
                <el-tag v-if="editingUser.is_admin" type="warning" size="small">管理员</el-tag>
              </div>
              <div class="summary-meta">
                <span v-if="editingUser.department">{{ editingUser.department }}</span>
                <span v-if="editingUser.position"> · {{ editingUser.position }}</span>
              </div>
            </div>
            <div class="summary-stat">
              <span class="stat-num">{{ selectedModules.length }}</span>
              <span class="stat-divider">/</span>
              <span class="stat-total">{{ catalog.length }}</span>
              <span class="stat-label-text">模块</span>
            </div>
          </div>

          <el-tabs v-model="editTabActive" class="edit-tabs">
            <!-- 可见模块 -->
            <el-tab-pane label="可见模块" name="modules">
              <div class="quick-actions">
                <el-button size="small" @click="selectAll">全选</el-button>
                <el-button size="small" @click="selectDefaults">仅默认</el-button>
                <el-button size="small" @click="selectNone">清空</el-button>
                <el-button size="small" type="primary" plain @click="loadFromDefault">恢复为系统默认</el-button>
              </div>

              <el-divider />

              <el-checkbox-group v-model="selectedModules" class="modules-grid">
                <el-checkbox
                  v-for="module in catalog"
                  :key="module.code"
                  :value="module.code"
                  :label="module.code"
                  border
                  class="module-card"
                >
                  <div class="module-card-content">
                    <div class="module-card-name">
                      {{ module.name }}
                      <el-tag v-if="module.default" type="success" size="small" effect="plain">默认</el-tag>
                    </div>
                    <div class="module-card-desc">{{ module.description }}</div>
                    <div class="module-card-path">{{ module.path }}</div>
                  </div>
                </el-checkbox>
              </el-checkbox-group>
            </el-tab-pane>

            <!-- 细分权限 -->
            <el-tab-pane :label="`细分权限 (${selectedAllowedPermissions.length + selectedDeniedPermissions.length})`" name="permissions">
              <div class="perm-hint">
                <el-alert
                  type="info"
                  :closable="false"
                  show-icon
                  title="细分权限"
                  description="在用户职位权限基础上，通过「额外权限」补充、通过「限制权限」收回具体功能。留空表示沿用职位默认。"
                />
              </div>

              <!-- 细分权限工具栏 -->
              <div class="perm-toolbar">
                <el-input
                  v-model="permKeyword"
                  placeholder="搜索权限名称 / 编码 / 描述"
                  clearable
                  size="small"
                  class="perm-search"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-button-group>
                  <el-button size="small" @click="permExpandAll = !permExpandAll">
                    <el-icon><component :is="permExpandAll ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                    {{ permExpandAll ? '收起全部' : '展开全部' }}
                  </el-button>
                </el-button-group>
              </div>

              <el-tabs v-model="permTabActive" class="perm-tabs">
                <!-- 额外权限 -->
                <el-tab-pane :label="`额外权限 (${selectedAllowedPermissions.length})`" name="allowed">
                  <div class="perm-quick-actions">
                    <el-button size="small" @click="selectPermAll('allowed')">全选</el-button>
                    <el-button size="small" @click="selectPermInverse('allowed')">反选</el-button>
                    <el-button size="small" @click="selectPermNone('allowed')">清空</el-button>
                    <el-button size="small" @click="selectPermFromVisible('allowed')">仅选筛选项</el-button>
                  </div>

                  <el-collapse v-model="permActiveNames" class="perm-collapse">
                    <el-collapse-item
                      v-for="(category, key) in filteredPermissions"
                      :key="key"
                      :name="`allowed-${key}`"
                      class="perm-collapse-item"
                    >
                      <template #title>
                        <div class="perm-collapse-title">
                          <span class="perm-collapse-name">{{ category.name }}</span>
                          <el-tag size="small" effect="plain" class="perm-count-tag">
                            {{ countSelectedInCategory('allowed', category.permissions) }} / {{ category.permissions.length }}
                          </el-tag>
                        </div>
                      </template>

                      <el-checkbox-group v-model="selectedAllowedPermissions" class="perm-checkbox-grid">
                        <el-checkbox
                          v-for="perm in category.permissions"
                          :key="`allowed-${perm.code}`"
                          :value="perm.code"
                          :label="perm.code"
                          border
                          class="perm-card"
                        >
                          <div class="perm-card-content">
                            <div class="perm-card-name">{{ perm.name }}</div>
                            <div class="perm-card-desc">{{ perm.description }}</div>
                            <div class="perm-card-code">{{ perm.code }}</div>
                          </div>
                        </el-checkbox>
                      </el-checkbox-group>
                    </el-collapse-item>
                  </el-collapse>
                </el-tab-pane>

                <!-- 限制权限 -->
                <el-tab-pane :label="`限制权限 (${selectedDeniedPermissions.length})`" name="denied">
                  <div class="perm-quick-actions">
                    <el-button size="small" @click="selectPermAll('denied')">全选</el-button>
                    <el-button size="small" @click="selectPermInverse('denied')">反选</el-button>
                    <el-button size="small" @click="selectPermNone('denied')">清空</el-button>
                    <el-button size="small" @click="selectPermFromVisible('denied')">仅选筛选项</el-button>
                  </div>

                  <el-collapse v-model="permActiveNames" class="perm-collapse">
                    <el-collapse-item
                      v-for="(category, key) in filteredPermissions"
                      :key="key"
                      :name="`denied-${key}`"
                      class="perm-collapse-item"
                    >
                      <template #title>
                        <div class="perm-collapse-title">
                          <span class="perm-collapse-name">{{ category.name }}</span>
                          <el-tag size="small" effect="plain" class="perm-count-tag">
                            {{ countSelectedInCategory('denied', category.permissions) }} / {{ category.permissions.length }}
                          </el-tag>
                        </div>
                      </template>

                      <el-checkbox-group v-model="selectedDeniedPermissions" class="perm-checkbox-grid">
                        <el-checkbox
                          v-for="perm in category.permissions"
                          :key="`denied-${perm.code}`"
                          :value="perm.code"
                          :label="perm.code"
                          border
                          class="perm-card"
                        >
                          <div class="perm-card-content">
                            <div class="perm-card-name">{{ perm.name }}</div>
                            <div class="perm-card-desc">{{ perm.description }}</div>
                            <div class="perm-card-code">{{ perm.code }}</div>
                          </div>
                        </el-checkbox>
                      </el-checkbox-group>
                    </el-collapse-item>
                  </el-collapse>
                </el-tab-pane>
              </el-tabs>
            </el-tab-pane>
          </el-tabs>
        </template>
      </div>

      <template #footer v-if="editingUser && !editingUser.is_super_admin">
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button
          v-if="!isDefaultConfig"
          v-permission="'module_perm:reset'"
          @click="handleReset(editingUser, true)"
        >恢复默认</el-button>
        <el-button
          v-permission="'template:create'"
          @click="openSaveAsTemplateDialog"
        >
          <el-icon><CollectionTag /></el-icon>
          另存为模板
        </el-button>
        <el-button
          type="primary"
          :loading="saving"
          v-permission="'module_perm:edit'"
          @click="handleSave"
        >
          保存配置
        </el-button>
      </template>
    </el-dialog>

    <!-- 应用模板对话框 -->
    <el-dialog
      v-model="applyDialogVisible"
      title="一键应用权限模板"
      width="520px"
      :close-on-click-modal="false"
      @closed="handleApplyDialogClosed"
    >
      <div v-if="applyingToUser" class="apply-tpl-dialog">
        <div class="apply-user-info">
          <el-avatar :size="40" :src="applyingToUser.avatar || '/avatar-placeholder.png'">
            {{ applyingToUser.username?.charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="apply-user-text">
            <div class="apply-user-name">
              {{ applyingToUser.username }}
              <el-tag v-if="applyingToUser.is_admin" type="warning" size="small">管理员</el-tag>
            </div>
            <div class="apply-user-meta">
              {{ applyingToUser.department || '-' }} · {{ applyingToUser.position || '-' }}
            </div>
          </div>
        </div>

        <el-alert
          type="warning"
          :closable="false"
          show-icon
          title="此操作将覆盖该用户当前的「可见模块」「额外权限」「限制权限」配置"
        />

        <el-form-item label="选择模板" style="margin-top: 16px;">
          <el-select
            v-model="selectedTemplateId"
            placeholder="请选择要应用的模板"
            style="width: 100%;"
            filterable
          >
            <el-option
              v-for="tpl in availableTemplates"
              :key="tpl.id"
              :label="`${tpl.name}${tpl.is_builtin ? ' (内置)' : ''}`"
              :value="tpl.id"
              :disabled="!tpl.is_active"
            >
              <div class="tpl-option">
                <div class="tpl-option-name">
                  <el-icon><CollectionTag /></el-icon>
                  <span>{{ tpl.name }}</span>
                  <el-tag v-if="tpl.is_builtin" type="success" size="small">内置</el-tag>
                  <el-tag v-else-if="tpl.category === 'role'" type="warning" size="small">角色</el-tag>
                </div>
                <div class="tpl-option-desc">{{ tpl.description || '（暂无描述）' }}</div>
                <div class="tpl-option-meta">
                  {{ tpl.module_count || 0 }} 个模块 · {{ tpl.permission_count || 0 }} 个细分权限
                </div>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <div v-if="selectedTemplateId && getSelectedTemplate()" class="tpl-preview">
          <h4>模板预览：{{ getSelectedTemplate().name }}</h4>
          <div class="tpl-preview-content">
            <div class="tpl-preview-row">
              <b>可见模块：</b>
              <span>{{ (getSelectedTemplate().modules || []).length }} 个</span>
            </div>
            <div class="tpl-preview-row">
              <b>额外权限：</b>
              <span>{{ (getSelectedTemplate().allowed_permissions || []).length }} 个</span>
            </div>
            <div class="tpl-preview-row">
              <b>限制权限：</b>
              <span>{{ (getSelectedTemplate().denied_permissions || []).length }} 个</span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="applyDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="applyingTemplate"
          :disabled="!selectedTemplateId"
          @click="handleApplyTemplate"
        >
          立即应用
        </el-button>
      </template>
    </el-dialog>

    <!-- 另存为模板 -->
    <el-dialog
      v-model="saveAsTplDialogVisible"
      title="另存为权限模板"
      width="520px"
      :close-on-click-modal="false"
      @closed="saveAsTplForm = { name: '', description: '', category: 'custom' }"
    >
      <el-alert
        type="info"
        :closable="false"
        show-icon
        title="将当前用户配置的「可见模块 + 额外/限制权限」保存为一个可复用的模板"
      />
      <el-form-item label="模板名称" required style="margin-top: 16px;">
        <el-input
          v-model="saveAsTplForm.name"
          placeholder="例如：测试工程师模板"
          maxlength="50"
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="saveAsTplForm.category" style="width: 100%;">
          <el-option label="角色模板" value="role" />
          <el-option label="自定义模板" value="custom" />
        </el-select>
      </el-form-item>
      <el-form-item label="描述">
        <el-input
          v-model="saveAsTplForm.description"
          type="textarea"
          :rows="2"
          placeholder="简单说明此模板的适用场景"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>
      <div class="save-as-summary">
        将保存：<b>{{ selectedModules.length }}</b> 个模块、
        <b>{{ selectedAllowedPermissions.length }}</b> 个额外权限、
        <b>{{ selectedDeniedPermissions.length }}</b> 个限制权限
      </div>

      <template #footer>
        <el-button @click="saveAsTplDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="savingAsTpl"
          @click="handleSaveAsTemplate"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { apiService as api } from '@/services/api'

const userStore = useUserStore()
const searchKeyword = ref('')
const loading = ref(false)
const saving = ref(false)
const userList = ref([])
const total = ref(0)
const customCountTotal = ref(0)
const catalog = ref([])
const defaultModuleCodes = ref([])
const allPermissions = ref({})

const pagination = ref({
  page: 1,
  per_page: 20
})

// 编辑对话框
const editDialogVisible = ref(false)
const editTabActive = ref('modules')
const permTabActive = ref('allowed')
const permKeyword = ref('')
const permActiveNames = ref([])
const permExpandAll = ref(false)
const editingUser = ref(null)
const selectedModules = ref([])
const selectedAllowedPermissions = ref([])
const selectedDeniedPermissions = ref([])
const isDefaultConfig = computed(() => {
  if (!editingUser.value) return true
  if (selectedModules.value.length !== defaultModuleCodes.value.length) return false
  const set1 = new Set(selectedModules.value)
  if (!defaultModuleCodes.value.every(code => set1.has(code))) return false
  if (selectedAllowedPermissions.value.length > 0) return false
  if (selectedDeniedPermissions.value.length > 0) return false
  return true
})

/** 把 allPermissions 转成 { key, name, permissions[] } 的扁平数组，供列表渲染 */
const permissionCategoryList = computed(() => {
  const arr = []
  for (const [key, cat] of Object.entries(allPermissions.value || {})) {
    arr.push({
      key,
      name: cat.name,
      order: cat.order ?? 999,
      permissions: cat.permissions || []
    })
  }
  arr.sort((a, b) => a.order - b.order)
  return arr
})

/** 根据 permKeyword 过滤后的分类列表（仅显示含匹配项的分类） */
const filteredPermissions = computed(() => {
  const kw = (permKeyword.value || '').trim().toLowerCase()
  if (!kw) return permissionCategoryList.value
  return permissionCategoryList.value
    .map(cat => {
      const perms = (cat.permissions || []).filter(p => {
        return (
          (p.name || '').toLowerCase().includes(kw) ||
          (p.code || '').toLowerCase().includes(kw) ||
          (p.description || '').toLowerCase().includes(kw)
        )
      })
      return perms.length ? { ...cat, permissions: perms } : null
    })
    .filter(Boolean)
})

/** 当前过滤结果中所有可见的权限编码 */
const visiblePermCodes = computed(() => {
  const set = new Set()
  for (const cat of filteredPermissions.value) {
    for (const p of cat.permissions) set.add(p.code)
  }
  return set
})

/** 当前分类下已选数量 */
function countSelectedInCategory(type, perms) {
  const list = type === 'allowed' ? selectedAllowedPermissions.value : selectedDeniedPermissions.value
  const set = new Set(list)
  return perms.filter(p => set.has(p.code)).length
}

function selectPermAll(type) {
  const list = type === 'allowed' ? selectedAllowedPermissions : selectedDeniedPermissions
  // 收集所有分类的全部权限编码
  const codes = []
  for (const cat of permissionCategoryList.value) {
    for (const p of cat.permissions) codes.push(p.code)
  }
  list.value = Array.from(new Set(codes))
}

function selectPermNone(type) {
  const list = type === 'allowed' ? selectedAllowedPermissions : selectedDeniedPermissions
  list.value = []
}

function selectPermFromVisible(type) {
  const list = type === 'allowed' ? selectedAllowedPermissions : selectedDeniedPermissions
  const set = new Set(list.value)
  for (const code of visiblePermCodes.value) set.add(code)
  list.value = Array.from(set)
}

function selectPermInverse(type) {
  const list = type === 'allowed' ? selectedAllowedPermissions : selectedDeniedPermissions
  const all = new Set()
  for (const cat of permissionCategoryList.value) {
    for (const p of cat.permissions) all.add(p.code)
  }
  const current = new Set(list.value)
  list.value = Array.from(all).filter(c => !current.has(c))
}

// 监听 permExpandAll：true 展开所有面板；false 收起
watch(permExpandAll, (val) => {
  if (!permissionCategoryList.value.length) return
  const prefix = permTabActive.value === 'allowed' ? 'allowed-' : 'denied-'
  if (val) {
    permActiveNames.value = permissionCategoryList.value.map(c => prefix + c.key)
  } else {
    permActiveNames.value = []
  }
})

const isAdmin = computed(() => {
  // 模块权限管理页面访问权：系统管理员 / 职位管理员 / 经理 / 拥有 module_perm:view 权限
  const u = userStore.currentUser
  if (!u) return false
  if (u.is_super_admin || u.is_admin) return true
  return userStore.hasPermission('module_perm:view')
})

const canEditPerm = computed(() => {
  const u = userStore.currentUser
  if (!u) return false
  if (u.is_super_admin || u.is_admin) return true
  return userStore.hasPermission('module_perm:edit')
})

const canResetPerm = computed(() => {
  const u = userStore.currentUser
  if (!u) return false
  if (u.is_super_admin || u.is_admin) return true
  return userStore.hasPermission('module_perm:reset')
})

const defaultCount = computed(() => defaultModuleCodes.value.length)
const customCount = computed(() => customCountTotal.value)

let searchDebounce = null
const handleSearch = () => {
  if (searchDebounce) clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => {
    pagination.value.page = 1
    fetchUsers()
  }, 300)
}

const handleSizeChange = (size) => {
  pagination.value.per_page = size
  pagination.value.page = 1
  fetchUsers()
}

const handlePageChange = (page) => {
  pagination.value.page = page
  fetchUsers()
}

const fetchCatalog = async () => {
  try {
    const res = await api.users.getModuleCatalog()
    catalog.value = res.modules || []
    defaultModuleCodes.value = catalog.value.filter(m => m.default).map(m => m.code)
  } catch (error) {
    console.error('获取模块列表失败:', error)
    ElMessage.error('获取模块列表失败')
  }
}

const fetchPermissions = async () => {
  try {
    const res = await api.users.getAllPermissions()
    allPermissions.value = res.permissions || {}
  } catch (error) {
    console.error('获取细分权限列表失败:', error)
  }
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await api.users.listUsersModulePermissions({
      keyword: searchKeyword.value,
      page: pagination.value.page,
      per_page: pagination.value.per_page
    })
    userList.value = res.items || []
    total.value = res.total || 0
    customCountTotal.value = typeof res.custom_count === 'number' ? res.custom_count : 0
  } catch (error) {
    console.error('获取用户模块权限列表失败:', error)
    if (error.response?.status === 403) {
      ElMessage.error('权限不足')
    } else {
      ElMessage.error('获取用户模块权限失败')
    }
  } finally {
    loading.value = false
  }
}

const refreshList = () => {
  fetchUsers()
}

const getModuleName = (code) => {
  const m = catalog.value.find(x => x.code === code)
  return m ? m.name : code
}

const openEditDialog = async (user) => {
  editingUser.value = user
  selectedModules.value = [...(user.accessible_modules || [])]
  selectedAllowedPermissions.value = []
  selectedDeniedPermissions.value = []
  editTabActive.value = 'modules'
  permTabActive.value = 'allowed'
  permKeyword.value = ''
  permActiveNames.value = []
  permExpandAll.value = false
  editDialogVisible.value = true

  // 拉取该用户的细分权限
  try {
    const res = await api.users.getUserPermissions(user.id)
    const cp = res.custom_permissions || {}
    selectedAllowedPermissions.value = Array.isArray(cp.allowed) ? [...cp.allowed] : []
    selectedDeniedPermissions.value = Array.isArray(cp.denied) ? [...cp.denied] : []
  } catch (err) {
    console.error('获取用户细分权限失败:', err)
  }
}

const handleDialogClosed = () => {
  editingUser.value = null
  selectedModules.value = []
  selectedAllowedPermissions.value = []
  selectedDeniedPermissions.value = []
  permKeyword.value = ''
  permActiveNames.value = []
  permExpandAll.value = false
}

const selectAll = () => {
  selectedModules.value = catalog.value.map(m => m.code)
}

const selectDefaults = () => {
  selectedModules.value = [...defaultModuleCodes.value]
}

const selectNone = () => {
  selectedModules.value = []
}

const loadFromDefault = async () => {
  try {
    await ElMessageBox.confirm(
      '确认将该用户的可见模块和细分权限全部恢复为系统默认？',
      '提示',
      {
        type: 'warning',
        confirmButtonText: '确认',
        cancelButtonText: '取消'
      }
    )
    try {
      await api.users.resetUserModulePermissions(editingUser.value.id)
      ElMessage.success('已恢复为系统默认')
      selectedModules.value = [...defaultModuleCodes.value]
      selectedAllowedPermissions.value = []
      selectedDeniedPermissions.value = []
      await fetchUsers()
    } catch (err) {
      ElMessage.error(err.response?.data?.error || '恢复失败')
    }
  } catch (e) {
    // 用户取消
  }
}

const handleSave = async () => {
  if (!editingUser.value) return
  saving.value = true
  try {
    await api.users.updateUserModulePermissions(
      editingUser.value.id,
      [...selectedModules.value],
      [...selectedAllowedPermissions.value],
      [...selectedDeniedPermissions.value]
    )
    ElMessage.success('权限配置已保存')
    editDialogVisible.value = false
    await fetchUsers()
  } catch (error) {
    console.error('保存权限配置失败:', error)
    ElMessage.error(error.response?.data?.error || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleReset = async (user, fromDialog = false) => {
  try {
    await ElMessageBox.confirm(
      `确认将用户 "${user.username}" 的可见模块和细分权限全部恢复为系统默认？`,
      '恢复默认',
      {
        type: 'warning',
        confirmButtonText: '确认',
        cancelButtonText: '取消'
      }
    )
    try {
      await api.users.resetUserModulePermissions(user.id)
      ElMessage.success('已恢复为系统默认')
      if (fromDialog) {
        selectedModules.value = [...defaultModuleCodes.value]
        selectedAllowedPermissions.value = []
        selectedDeniedPermissions.value = []
        editDialogVisible.value = false
      }
      await fetchUsers()
    } catch (err) {
      ElMessage.error(err.response?.data?.error || '恢复失败')
    }
  } catch (e) {
    // 用户取消
  }
}

onMounted(async () => {
  await fetchCatalog()
  await fetchPermissions()
  await fetchUsers()
})

// ============================================================
// 一键应用模板（针对单个用户）
// ============================================================
const applyDialogVisible = ref(false)
const applyingToUser = ref(null)
const availableTemplates = ref([])
const selectedTemplateId = ref(null)
const applyingTemplate = ref(false)

const getSelectedTemplate = () => {
  if (!selectedTemplateId.value) return null
  return availableTemplates.value.find(t => t.id === selectedTemplateId.value) || null
}

const openApplyToUserDialog = async (row) => {
  applyingToUser.value = row
  selectedTemplateId.value = null
  applyDialogVisible.value = true
  // 加载模板列表（不包含完整内容，只用于选择）
  try {
    const res = await api.users.listPermissionTemplates({ include_content: true })
    availableTemplates.value = (res.items || []).filter(t => t.is_active)
  } catch (e) {
    console.error('获取模板列表失败:', e)
    ElMessage.error('获取模板列表失败')
  }
}

const handleApplyDialogClosed = () => {
  applyingToUser.value = null
  selectedTemplateId.value = null
  availableTemplates.value = []
}

const handleApplyTemplate = async () => {
  if (!applyingToUser.value || !selectedTemplateId.value) return
  try {
    await ElMessageBox.confirm(
      `确认将模板应用到用户 "${applyingToUser.value.username}"？该操作将覆盖其当前的模块和细分权限配置。`,
      '应用确认',
      { type: 'warning', confirmButtonText: '确认', cancelButtonText: '取消' }
    )
  } catch (e) {
    return
  }
  applyingTemplate.value = true
  try {
    const res = await api.users.applyPermissionTemplate(selectedTemplateId.value, [applyingToUser.value.id])
    const appliedCount = res.applied_count || 0
    if (appliedCount > 0) {
      ElMessage.success(`已成功应用模板 "${res.template_name || ''}" 到用户 ${applyingToUser.value.username}`)
    } else {
      ElMessage.warning('应用未生效（可能因系统管理员被跳过）')
    }
    applyDialogVisible.value = false
    await fetchUsers()
  } catch (e) {
    console.error('应用模板失败:', e)
    ElMessage.error(e.response?.data?.error || '应用失败')
  } finally {
    applyingTemplate.value = false
  }
}

// ============================================================
// 另存为模板
// ============================================================
const saveAsTplDialogVisible = ref(false)
const saveAsTplForm = ref({ name: '', description: '', category: 'custom' })
const savingAsTpl = ref(false)

const openSaveAsTemplateDialog = () => {
  if (!editingUser.value) return
  saveAsTplForm.value = {
    name: `${editingUser.value.username} 权限配置`,
    description: `基于用户 ${editingUser.value.username} 的当前配置生成`,
    category: 'custom'
  }
  saveAsTplDialogVisible.value = true
}

const handleSaveAsTemplate = async () => {
  if (!saveAsTplForm.value.name || !saveAsTplForm.value.name.trim()) {
    ElMessage.warning('请输入模板名称')
    return
  }
  savingAsTpl.value = true
  try {
    await api.users.createPermissionTemplate({
      name: saveAsTplForm.value.name.trim(),
      description: saveAsTplForm.value.description,
      category: saveAsTplForm.value.category,
      modules: [...selectedModules.value],
      allowed_permissions: [...selectedAllowedPermissions.value],
      denied_permissions: [...selectedDeniedPermissions.value]
    })
    ElMessage.success('模板已保存')
    saveAsTplDialogVisible.value = false
  } catch (e) {
    console.error('保存模板失败:', e)
    ElMessage.error(e.response?.data?.error || '保存失败')
  } finally {
    savingAsTpl.value = false
  }
}
</script>

<style scoped>
.module-permissions {
  padding: 0;
}

.permission-denied {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.page-header {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.08) 0%, rgba(14, 165, 233, 0.05) 100%);
  border-radius: 16px;
  padding: 24px 28px;
  margin-bottom: 20px;
  border: 1px solid rgba(56, 189, 248, 0.15);
}

.header-content {
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
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 20px -4px rgba(56, 189, 248, 0.5);
}

.title-icon {
  font-size: 30px;
  color: white;
}

.title-text h1 {
  font-size: 22px;
  font-weight: 700;
  color: #0c4a6e;
  margin: 0 0 4px 0;
}

.subtitle {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 14px;
  padding: 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #f1f5f9;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon-wrapper .el-icon {
  font-size: 24px;
  color: white;
}

.stat-icon-wrapper-primary {
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
}

.stat-icon-wrapper-success {
  background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
}

.stat-icon-wrapper-info {
  background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
}

.stat-icon-wrapper-warning {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #0c4a6e;
  line-height: 1.1;
}

.stat-label {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}

.main-card {
  border-radius: 14px;
  border: 1px solid #e0f2fe;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}

.toolbar > div,
.toolbar > .el-input {
  flex-shrink: 0;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.user-name {
  font-weight: 600;
  color: #0c4a6e;
  font-size: 14px;
}

.user-sub {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}

.dept-cell {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.separator {
  color: #cbd5e1;
  margin: 0 2px;
}

.position-text {
  font-size: 13px;
  color: #64748b;
}

.module-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.module-tag {
  margin: 0 !important;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.edit-dialog-content {
  padding: 0 4px;
}

.user-summary {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.06) 0%, rgba(14, 165, 233, 0.04) 100%);
  border-radius: 12px;
  border: 1px solid rgba(56, 189, 248, 0.15);
  margin-bottom: 16px;
}

.summary-info {
  flex: 1;
  min-width: 0;
}

.summary-name {
  font-size: 16px;
  font-weight: 600;
  color: #0c4a6e;
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-meta {
  font-size: 13px;
  color: #64748b;
  margin-top: 2px;
}

.summary-stat {
  display: flex;
  align-items: baseline;
  gap: 4px;
  color: #0c4a6e;
}

.stat-num {
  font-size: 28px;
  font-weight: 700;
  color: #0ea5e9;
}

.stat-divider {
  font-size: 18px;
  color: #94a3b8;
}

.stat-total {
  font-size: 18px;
  font-weight: 600;
  color: #64748b;
}

.stat-label-text {
  font-size: 12px;
  color: #94a3b8;
  margin-left: 6px;
}

.quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 4px;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
  max-height: 480px;
  overflow-y: auto;
  padding: 4px;
}

.module-card {
  margin: 0 !important;
  padding: 12px 14px;
  border-radius: 10px;
  height: auto;
  width: 100%;
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
}

.module-card:hover {
  border-color: #38bdf8;
  box-shadow: 0 2px 8px rgba(56, 189, 248, 0.15);
}

.module-card.is-checked {
  border-color: #0ea5e9;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.06) 0%, rgba(14, 165, 233, 0.04) 100%);
}

.module-card :deep(.el-checkbox__label) {
  width: 100%;
  white-space: normal;
  padding-left: 8px;
}

.module-card-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.module-card-name {
  font-size: 14px;
  font-weight: 600;
  color: #0c4a6e;
  display: flex;
  align-items: center;
  gap: 6px;
}

.module-card-desc {
  font-size: 12px;
  color: #64748b;
  line-height: 1.4;
}

.perm-card-code {
  font-size: 11px;
  color: #94a3b8;
  font-family: 'Courier New', monospace;
  margin-top: 2px;
}

.perm-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 12px 0;
}

.perm-search {
  flex: 1;
  max-width: 360px;
}

.perm-quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 8px 0 12px 0;
  padding: 8px 12px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
  border: 1px dashed #bae6fd;
}

.perm-collapse {
  border: 1px solid #e0f2fe;
  border-radius: 8px;
  margin-top: 4px;
  background: #fff;
}

.perm-collapse-item {
  border-bottom: 1px solid #f1f5f9;
}

.perm-collapse-item:last-child {
  border-bottom: none;
}

.perm-collapse-item :deep(.el-collapse-item__header) {
  padding-left: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #e2e8f0;
}

.perm-collapse-item :deep(.el-collapse-item__content) {
  padding: 14px 16px;
}

.perm-collapse-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.perm-collapse-name {
  font-size: 14px;
  font-weight: 600;
  color: #0c4a6e;
}

.perm-count-tag {
  font-family: 'Courier New', monospace;
}

.edit-tabs {
  margin-top: 4px;
}

.edit-tabs :deep(.el-tabs__nav-wrap::after) {
  background: #e0f2fe;
}

.perm-hint {
  margin-bottom: 12px;
}

.perm-hint :deep(.el-alert__description) {
  font-size: 12px;
  color: #475569;
}

.perm-tabs {
  margin-top: 8px;
}

.perm-tabs :deep(.el-tabs__header) {
  margin-bottom: 12px;
}

.perm-category {
  margin-bottom: 16px;
}

.perm-category-title {
  font-size: 13px;
  font-weight: 600;
  color: #0c4a6e;
  margin-bottom: 8px;
  padding-left: 6px;
  border-left: 3px solid #0ea5e9;
}

.perm-checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 8px;
  padding: 2px 0 8px 0;
}

.perm-card {
  margin: 0 !important;
  padding: 10px 12px;
  border-radius: 8px;
  height: auto;
  width: 100%;
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
}

.perm-card:hover {
  border-color: #38bdf8;
  box-shadow: 0 2px 8px rgba(56, 189, 248, 0.15);
}

.perm-card.is-checked {
  border-color: #0ea5e9;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.06) 0%, rgba(14, 165, 233, 0.04) 100%);
}

.perm-card :deep(.el-checkbox__label) {
  width: 100%;
  white-space: normal;
  padding-left: 8px;
}

.perm-card-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.perm-card-name {
  font-size: 13px;
  font-weight: 600;
  color: #0c4a6e;
}

.perm-card-desc {
  font-size: 11px;
  color: #64748b;
  line-height: 1.4;
}

.apply-tpl-dialog {
  padding: 0 4px;
}

.apply-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.06) 0%, rgba(14, 165, 233, 0.04) 100%);
  border-radius: 10px;
  border: 1px solid rgba(56, 189, 248, 0.15);
  margin-bottom: 12px;
}

.apply-user-text {
  flex: 1;
  min-width: 0;
}

.apply-user-name {
  font-size: 15px;
  font-weight: 600;
  color: #0c4a6e;
  display: flex;
  align-items: center;
  gap: 6px;
}

.apply-user-meta {
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

.tpl-option {
  padding: 4px 0;
}

.tpl-option-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #0c4a6e;
}

.tpl-option-desc {
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

.tpl-option-meta {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}

.tpl-preview {
  margin-top: 12px;
  padding: 12px 14px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
  border: 1px solid #bae6fd;
}

.tpl-preview h4 {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #0c4a6e;
}

.tpl-preview-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tpl-preview-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #475569;
}

.tpl-preview-row b {
  color: #0c4a6e;
}

.save-as-summary {
  margin-top: 12px;
  padding: 10px 14px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
  font-size: 13px;
  color: #0c4a6e;
}
</style>
