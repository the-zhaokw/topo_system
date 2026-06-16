<template>
  <div class="permission-templates">
    <!-- 权限检查 -->
    <div v-if="!canView" class="permission-denied">
      <el-result
        icon="warning"
        title="权限不足"
        sub-title="您没有权限访问权限模板管理页面"
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
              <el-icon class="title-icon"><CollectionTag /></el-icon>
            </div>
            <div class="title-text">
              <h1>权限模板管理</h1>
              <p class="subtitle">预设「可见模块 + 细分权限」组合，一键应用到用户身上</p>
            </div>
          </div>
          <div class="header-actions">
            <el-button
              type="primary"
              v-permission="'template:create'"
              @click="openCreateDialog"
            >
              <el-icon><Plus /></el-icon>
              新建模板
            </el-button>
          </div>
        </div>
      </div>

      <!-- 统计卡片 -->
      <el-row :gutter="16" class="stats-row">
        <el-col :xs="12" :sm="6">
          <div class="stat-card stat-card-primary">
            <div class="stat-icon-wrapper stat-icon-wrapper-primary">
              <el-icon><Files /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ templates.length }}</div>
              <div class="stat-label">模板总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card stat-card-success">
            <div class="stat-icon-wrapper stat-icon-wrapper-success">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ builtinCount }}</div>
              <div class="stat-label">内置模板</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card stat-card-info">
            <div class="stat-icon-wrapper stat-icon-wrapper-info">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ customCount }}</div>
              <div class="stat-label">自定义模板</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card stat-card-warning">
            <div class="stat-icon-wrapper stat-icon-wrapper-warning">
              <el-icon><Histogram /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ activeCount }}</div>
              <div class="stat-label">启用中</div>
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
            placeholder="按名称/描述搜索"
            style="width: 280px;"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="filterCategory"
            placeholder="按分类筛选"
            clearable
            style="width: 160px;"
            @change="handleSearch"
          >
            <el-option label="内置模板" value="builtin" />
            <el-option label="角色模板" value="role" />
            <el-option label="自定义模板" value="custom" />
          </el-select>
          <el-button @click="fetchTemplates">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>

        <!-- 模板列表 -->
        <el-table
          v-loading="loading"
          :data="filteredTemplates"
          stripe
          style="width: 100%"
          :header-cell-style="{ background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)', color: '#0c4a6e', fontWeight: 600 }"
        >
          <el-table-column label="模板" min-width="280">
            <template #default="{ row }">
              <div class="template-cell">
                <el-icon class="template-icon" :class="`icon-${row.category}`">
                  <component :is="row.icon || 'Document'" />
                </el-icon>
                <div class="template-info">
                  <div class="template-name">
                    {{ row.name }}
                    <el-tag v-if="row.is_builtin" type="success" size="small" effect="dark">内置</el-tag>
                    <el-tag v-else-if="!row.is_active" type="info" size="small">已停用</el-tag>
                  </div>
                  <div class="template-desc">{{ row.description || '（暂无描述）' }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="分类" width="110">
            <template #default="{ row }">
              <el-tag v-if="row.category === 'builtin'" type="success" size="small">内置</el-tag>
              <el-tag v-else-if="row.category === 'role'" type="warning" size="small">角色</el-tag>
              <el-tag v-else size="small">自定义</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="内容" min-width="220">
            <template #default="{ row }">
              <div class="content-cell">
                <div class="content-item">
                  <el-icon><Grid /></el-icon>
                  <span>{{ row.module_count ?? 0 }} 个模块</span>
                </div>
                <div class="content-item">
                  <el-icon><Key /></el-icon>
                  <span>{{ row.permission_count ?? 0 }} 个细分权限</span>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag v-if="row.is_active" type="success" size="small">启用</el-tag>
              <el-tag v-else type="info" size="small">停用</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="更新时间" width="170">
            <template #default="{ row }">
              <span class="time-text">{{ formatTime(row.updated_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="280" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                link
                v-permission="'template:apply'"
                :disabled="!row.is_active"
                @click="openApplyDialog(row)"
              >
                <el-icon><Promotion /></el-icon>
                一键应用
              </el-button>
              <el-button
                type="info"
                size="small"
                link
                @click="openViewDialog(row)"
              >
                <el-icon><View /></el-icon>
                查看
              </el-button>
              <el-button
                size="small"
                link
                v-permission="'template:edit'"
                :disabled="row.is_builtin"
                @click="openEditDialog(row)"
              >
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                link
                v-permission="'template:delete'"
                :disabled="row.is_builtin"
                @click="handleDelete(row)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty
          v-if="!loading && filteredTemplates.length === 0"
          description="暂无权限模板"
        >
          <el-button
            v-permission="'template:create'"
            type="primary"
            @click="openCreateDialog"
          >
            <el-icon><Plus /></el-icon>
            新建模板
          </el-button>
        </el-empty>
      </el-card>
    </div>

    <!-- 创建/编辑 模板 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="editingTemplate ? `编辑模板 - ${editingTemplate.name}` : '新建权限模板'"
      width="960px"
      :close-on-click-modal="false"
      @closed="handleEditDialogClosed"
    >
      <div v-if="form" class="edit-dialog-content">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="模板名称" required>
              <el-input
                v-model="form.name"
                placeholder="例如：测试工程师模板"
                maxlength="50"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="分类">
              <el-select v-model="form.category" style="width: 100%;">
                <el-option label="角色模板" value="role" />
                <el-option label="自定义模板" value="custom" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="排序">
              <el-input-number v-model="form.sort_order" :min="0" :step="10" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="2"
            placeholder="简单说明此模板的适用场景"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-tabs v-model="formTabActive" class="form-tabs">
          <!-- 可见模块 -->
          <el-tab-pane label="可见模块" name="modules">
            <div class="quick-actions">
              <el-button size="small" @click="formSelectAllModules">全选</el-button>
              <el-button size="small" @click="formSelectDefaultModules">仅默认</el-button>
              <el-button size="small" @click="formClearModules">清空</el-button>
            </div>
            <el-divider />
            <el-checkbox-group v-model="formModules" class="modules-grid">
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
                </div>
              </el-checkbox>
            </el-checkbox-group>
          </el-tab-pane>

          <!-- 额外权限 -->
          <el-tab-pane :label="`额外权限 (${formAllowedPermissions.length})`" name="allowed">
            <div class="perm-hint">
              <el-alert
                type="success"
                :closable="false"
                show-icon
                title="额外权限"
                description="在用户职位权限基础上，额外补充的细分权限。"
              />
            </div>
            <div class="perm-toolbar">
              <el-input
                v-model="formPermKeyword"
                placeholder="搜索权限名称 / 编码"
                clearable
                size="small"
                class="perm-search"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-button-group>
                <el-button size="small" @click="formSelectAllAllowed">全选</el-button>
                <el-button size="small" @click="formClearAllowed">清空</el-button>
              </el-button-group>
            </div>
            <el-collapse v-model="formAllowedActive" class="perm-collapse">
              <el-collapse-item
                v-for="(category, key) in formFilteredPermissions"
                :key="key"
                :name="`allowed-${key}`"
                class="perm-collapse-item"
              >
                <template #title>
                  <div class="perm-collapse-title">
                    <span class="perm-collapse-name">{{ category.name }}</span>
                    <el-tag size="small" effect="plain" class="perm-count-tag">
                      {{ formCountSelected('allowed', category.permissions) }} / {{ category.permissions.length }}
                    </el-tag>
                  </div>
                </template>
                <el-checkbox-group v-model="formAllowedPermissions" class="perm-checkbox-grid">
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
          <el-tab-pane :label="`限制权限 (${formDeniedPermissions.length})`" name="denied">
            <div class="perm-hint">
              <el-alert
                type="warning"
                :closable="false"
                show-icon
                title="限制权限"
                description="强制收回的细分权限（即使职位有，也会被禁用）。"
              />
            </div>
            <div class="perm-toolbar">
              <el-input
                v-model="formPermKeyword"
                placeholder="搜索权限名称 / 编码"
                clearable
                size="small"
                class="perm-search"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-button-group>
                <el-button size="small" @click="formSelectAllDenied">全选</el-button>
                <el-button size="small" @click="formClearDenied">清空</el-button>
              </el-button-group>
            </div>
            <el-collapse v-model="formDeniedActive" class="perm-collapse">
              <el-collapse-item
                v-for="(category, key) in formFilteredPermissions"
                :key="key"
                :name="`denied-${key}`"
                class="perm-collapse-item"
              >
                <template #title>
                  <div class="perm-collapse-title">
                    <span class="perm-collapse-name">{{ category.name }}</span>
                    <el-tag size="small" effect="plain" class="perm-count-tag">
                      {{ formCountSelected('denied', category.permissions) }} / {{ category.permissions.length }}
                    </el-tag>
                  </div>
                </template>
                <el-checkbox-group v-model="formDeniedPermissions" class="perm-checkbox-grid">
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
      </div>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="saving"
          @click="handleSaveTemplate"
        >
          保存模板
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看模板 -->
    <el-dialog
      v-model="viewDialogVisible"
      :title="`模板详情 - ${viewingTemplate?.name || ''}`"
      width="780px"
      @closed="viewingTemplate = null"
    >
      <div v-if="viewingTemplate" class="view-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="模板名称">{{ viewingTemplate.name }}</el-descriptions-item>
          <el-descriptions-item label="分类">
            <el-tag v-if="viewingTemplate.category === 'builtin'" type="success" size="small">内置</el-tag>
            <el-tag v-else-if="viewingTemplate.category === 'role'" type="warning" size="small">角色</el-tag>
            <el-tag v-else size="small">自定义</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag v-if="viewingTemplate.is_active" type="success" size="small">启用</el-tag>
            <el-tag v-else type="info" size="small">停用</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(viewingTemplate.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ viewingTemplate.description || '（暂无描述）' }}</el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <h4>可见模块（{{ (viewingTemplate.modules || []).length }}）</h4>
        <div class="tag-list">
          <el-tag
            v-for="code in viewingTemplate.modules || []"
            :key="code"
            class="mr-2 mb-2"
            effect="plain"
          >
            {{ getModuleName(code) }}
          </el-tag>
          <el-tag v-if="!(viewingTemplate.modules || []).length" type="info" effect="plain">无</el-tag>
        </div>

        <h4>额外权限（{{ (viewingTemplate.allowed_permissions || []).length }}）</h4>
        <div class="tag-list">
          <el-tag
            v-for="code in viewingTemplate.allowed_permissions || []"
            :key="code"
            class="mr-2 mb-2"
            type="success"
            effect="plain"
          >
            {{ code }}
          </el-tag>
          <el-tag v-if="!(viewingTemplate.allowed_permissions || []).length" type="info" effect="plain">无</el-tag>
        </div>

        <h4>限制权限（{{ (viewingTemplate.denied_permissions || []).length }}）</h4>
        <div class="tag-list">
          <el-tag
            v-for="code in viewingTemplate.denied_permissions || []"
            :key="code"
            class="mr-2 mb-2"
            type="warning"
            effect="plain"
          >
            {{ code }}
          </el-tag>
          <el-tag v-if="!(viewingTemplate.denied_permissions || []).length" type="info" effect="plain">无</el-tag>
        </div>
      </div>
    </el-dialog>

    <!-- 应用模板 -->
    <el-dialog
      v-model="applyDialogVisible"
      :title="`一键应用模板 - ${applyingTemplate?.name || ''}`"
      width="780px"
      :close-on-click-modal="false"
      @closed="handleApplyDialogClosed"
    >
      <div v-if="applyingTemplate" class="apply-dialog-content">
        <el-alert
          type="warning"
          :closable="false"
          show-icon
          title="注意：此操作将覆盖目标用户的「可见模块」「额外权限」「限制权限」配置"
        />
        <div class="apply-tpl-info">
          <el-icon class="info-icon"><CollectionTag /></el-icon>
          <div class="info-text">
            <div class="info-name">{{ applyingTemplate.name }}</div>
            <div class="info-desc">
              {{ applyingTemplate.description || '（暂无描述）' }}
              · {{ applyingTemplate.module_count || 0 }} 个模块
              · {{ applyingTemplate.permission_count || 0 }} 个细分权限
            </div>
          </div>
        </div>

        <div class="apply-toolbar">
          <el-input
            v-model="applyUserKeyword"
            placeholder="按用户名/邮箱/姓名搜索"
            clearable
            class="apply-search"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button-group>
            <el-button size="small" @click="applySelectAll">全选</el-button>
            <el-button size="small" @click="applyInvert">反选</el-button>
            <el-button size="small" @click="applyClear">清空</el-button>
          </el-button-group>
        </div>

        <el-table
          ref="applyTableRef"
          v-loading="applyUserLoading"
          :data="filteredApplyUsers"
          max-height="380"
          @selection-change="onApplySelectionChange"
        >
          <el-table-column type="selection" width="50" />
          <el-table-column label="用户" min-width="200">
            <template #default="{ row }">
              <div class="user-cell">
                <el-avatar :size="32" :src="row.avatar || '/avatar-placeholder.png'">
                  {{ row.username?.charAt(0).toUpperCase() }}
                </el-avatar>
                <div class="user-info">
                  <div class="user-name">{{ row.username }}</div>
                  <div class="user-sub">{{ row.email || '-' }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="部门" min-width="120">
            <template #default="{ row }">
              <span>{{ row.department || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="职位" min-width="120">
            <template #default="{ row }">
              <span>{{ row.position || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="身份" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.is_super_admin" type="danger" size="small">系统管理员</el-tag>
              <el-tag v-else-if="row.is_admin" type="warning" size="small">管理员</el-tag>
              <el-tag v-else type="info" size="small">普通</el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div class="apply-summary">
          已选择 <b>{{ applySelectedIds.length }}</b> 个用户
          <span v-if="applySelectedIds.length" class="ml-2 text-muted">
            （系统管理员会被自动跳过）
          </span>
        </div>
      </div>

      <template #footer>
        <el-button @click="applyDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="applying"
          :disabled="applySelectedIds.length === 0"
          @click="handleApply"
        >
          一键应用（{{ applySelectedIds.length }}）
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { apiService as api } from '@/services/api'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const saving = ref(false)
const templates = ref([])
const searchKeyword = ref('')
const filterCategory = ref('')

const catalog = ref([])
const allPermissions = ref({})
const defaultModuleCodes = ref([])

let searchDebounce = null
const handleSearch = () => {
  if (searchDebounce) clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => {
    // 仅本地过滤
  }, 200)
}

const canView = computed(() => {
  const u = userStore.currentUser
  if (!u) return false
  if (u.is_super_admin || u.is_admin) return true
  if (u.role === 'admin' || u.role === 'manager') return true
  return userStore.hasPermission('template:view')
})

const filteredTemplates = computed(() => {
  const kw = (searchKeyword.value || '').trim().toLowerCase()
  return templates.value.filter(t => {
    if (filterCategory.value && t.category !== filterCategory.value) return false
    if (kw) {
      const blob = `${t.name || ''} ${t.description || ''}`.toLowerCase()
      if (!blob.includes(kw)) return false
    }
    return true
  })
})

const builtinCount = computed(() => templates.value.filter(t => t.category === 'builtin').length)
const customCount = computed(() => templates.value.filter(t => t.category === 'custom').length)
const activeCount = computed(() => templates.value.filter(t => t.is_active).length)

const fetchTemplates = async () => {
  loading.value = true
  try {
    const res = await api.users.listPermissionTemplates({ include_content: true })
    templates.value = res.items || []
  } catch (error) {
    console.error('获取模板列表失败:', error)
    if (error.response?.status === 403) {
      ElMessage.error('权限不足，无法查看权限模板')
    } else {
      ElMessage.error('获取模板列表失败')
    }
  } finally {
    loading.value = false
  }
}

const fetchCatalog = async () => {
  try {
    const res = await api.users.getModuleCatalog()
    catalog.value = res.modules || []
    defaultModuleCodes.value = catalog.value.filter(m => m.default).map(m => m.code)
  } catch (e) {
    console.error('获取模块目录失败:', e)
  }
}

const fetchPermissions = async () => {
  try {
    const res = await api.users.getAllPermissions()
    allPermissions.value = res.permissions || {}
  } catch (e) {
    console.error('获取细分权限失败:', e)
  }
}

const getModuleName = (code) => {
  const m = catalog.value.find(x => x.code === code)
  return m ? m.name : code
}

const formatTime = (t) => {
  if (!t) return '-'
  try {
    return new Date(t).toLocaleString('zh-CN', { hour12: false })
  } catch (e) {
    return t
  }
}

// ============================================================
// 创建/编辑 模板
// ============================================================
const editDialogVisible = ref(false)
const editingTemplate = ref(null)
const form = ref(null)
const formTabActive = ref('modules')
const formModules = ref([])
const formAllowedPermissions = ref([])
const formDeniedPermissions = ref([])
const formPermKeyword = ref('')
const formAllowedActive = ref([])
const formDeniedActive = ref([])

const formPermissionCategoryList = computed(() => {
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

const formFilteredPermissions = computed(() => {
  const kw = (formPermKeyword.value || '').trim().toLowerCase()
  if (!kw) return formPermissionCategoryList.value
  return formPermissionCategoryList.value
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

const formCountSelected = (type, perms) => {
  const list = type === 'allowed' ? formAllowedPermissions.value : formDeniedPermissions.value
  const set = new Set(list)
  return perms.filter(p => set.has(p.code)).length
}

const formSelectAllModules = () => {
  formModules.value = catalog.value.map(m => m.code)
}
const formSelectDefaultModules = () => {
  formModules.value = [...defaultModuleCodes.value]
}
const formClearModules = () => {
  formModules.value = []
}

const formSelectAllAllowed = () => {
  const codes = []
  for (const cat of formPermissionCategoryList.value) {
    for (const p of cat.permissions) codes.push(p.code)
  }
  formAllowedPermissions.value = Array.from(new Set(codes))
}
const formClearAllowed = () => { formAllowedPermissions.value = [] }
const formSelectAllDenied = () => {
  const codes = []
  for (const cat of formPermissionCategoryList.value) {
    for (const p of cat.permissions) codes.push(p.code)
  }
  formDeniedPermissions.value = Array.from(new Set(codes))
}
const formClearDenied = () => { formDeniedPermissions.value = [] }

const openCreateDialog = () => {
  editingTemplate.value = null
  form.value = {
    name: '',
    description: '',
    category: 'custom',
    icon: 'Document',
    is_active: true,
    sort_order: 100
  }
  formModules.value = [...defaultModuleCodes.value]
  formAllowedPermissions.value = []
  formDeniedPermissions.value = []
  formTabActive.value = 'modules'
  formPermKeyword.value = ''
  formAllowedActive.value = []
  formDeniedActive.value = []
  editDialogVisible.value = true
}

const openEditDialog = async (row) => {
  editingTemplate.value = row
  // 重新拉取详情
  try {
    const fresh = await api.users.getPermissionTemplate(row.id)
    form.value = {
      name: fresh.name,
      description: fresh.description || '',
      category: fresh.category,
      icon: fresh.icon || 'Document',
      is_active: !!fresh.is_active,
      sort_order: fresh.sort_order || 0
    }
    formModules.value = Array.isArray(fresh.modules) ? [...fresh.modules] : []
    formAllowedPermissions.value = Array.isArray(fresh.allowed_permissions) ? [...fresh.allowed_permissions] : []
    formDeniedPermissions.value = Array.isArray(fresh.denied_permissions) ? [...fresh.denied_permissions] : []
    formTabActive.value = 'modules'
    formPermKeyword.value = ''
    formAllowedActive.value = []
    formDeniedActive.value = []
    editDialogVisible.value = true
  } catch (e) {
    ElMessage.error('获取模板详情失败')
  }
}

const handleEditDialogClosed = () => {
  editingTemplate.value = null
  form.value = null
  formModules.value = []
  formAllowedPermissions.value = []
  formDeniedPermissions.value = []
  formPermKeyword.value = ''
}

const handleSaveTemplate = async () => {
  if (!form.value) return
  if (!form.value.name || !form.value.name.trim()) {
    ElMessage.warning('请输入模板名称')
    return
  }
  saving.value = true
  try {
    const payload = {
      name: form.value.name.trim(),
      description: form.value.description,
      category: form.value.category,
      icon: form.value.icon,
      is_active: form.value.is_active,
      sort_order: form.value.sort_order,
      modules: [...formModules.value],
      allowed_permissions: [...formAllowedPermissions.value],
      denied_permissions: [...formDeniedPermissions.value]
    }
    if (editingTemplate.value) {
      await api.users.updatePermissionTemplate(editingTemplate.value.id, payload)
      ElMessage.success('模板已更新')
    } else {
      await api.users.createPermissionTemplate(payload)
      ElMessage.success('模板已创建')
    }
    editDialogVisible.value = false
    await fetchTemplates()
  } catch (error) {
    console.error('保存模板失败:', error)
    ElMessage.error(error.response?.data?.error || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认删除模板 "${row.name}"？该操作不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '确认', cancelButtonText: '取消' }
    )
    try {
      await api.users.deletePermissionTemplate(row.id)
      ElMessage.success('已删除')
      await fetchTemplates()
    } catch (e) {
      ElMessage.error(e.response?.data?.error || '删除失败')
    }
  } catch (e) {
    // 取消
  }
}

// ============================================================
// 查看模板
// ============================================================
const viewDialogVisible = ref(false)
const viewingTemplate = ref(null)
const openViewDialog = async (row) => {
  try {
    const fresh = await api.users.getPermissionTemplate(row.id)
    viewingTemplate.value = fresh
    viewDialogVisible.value = true
  } catch (e) {
    ElMessage.error('获取模板详情失败')
  }
}

// ============================================================
// 一键应用
// ============================================================
const applyDialogVisible = ref(false)
const applyingTemplate = ref(null)
const applyUsers = ref([])
const applyUserLoading = ref(false)
const applyUserKeyword = ref('')
const applySelectedIds = ref([])
const applyTableRef = ref(null)
const applying = ref(false)

const filteredApplyUsers = computed(() => {
  const kw = (applyUserKeyword.value || '').trim().toLowerCase()
  return applyUsers.value.filter(u => {
    if (u.is_super_admin) return false
    if (kw) {
      const blob = `${u.username || ''} ${u.email || ''} ${u.first_name || ''} ${u.last_name || ''}`.toLowerCase()
      if (!blob.includes(kw)) return false
    }
    return true
  })
})

const openApplyDialog = async (row) => {
  applyingTemplate.value = row
  applyUserKeyword.value = ''
  applySelectedIds.value = []
  applyDialogVisible.value = true
  await fetchApplyUsers()
}

const fetchApplyUsers = async () => {
  applyUserLoading.value = true
  try {
    const res = await api.users.listUsersModulePermissions({ per_page: 500 })
    applyUsers.value = res.items || []
  } catch (e) {
    console.error('获取用户列表失败:', e)
    ElMessage.error('获取用户列表失败')
  } finally {
    applyUserLoading.value = false
  }
}

const handleApplyDialogClosed = () => {
  applyingTemplate.value = null
  applySelectedIds.value = []
  applyUserKeyword.value = ''
}

const onApplySelectionChange = (rows) => {
  applySelectedIds.value = rows.map(r => r.id)
}

const applySelectAll = async () => {
  await nextTick()
  if (applyTableRef.value) {
    applyTableRef.value.toggleAllSelection(true)
  }
}

const applyClear = async () => {
  await nextTick()
  if (applyTableRef.value) {
    applyTableRef.value.clearSelection()
  }
}

const applyInvert = async () => {
  await nextTick()
  if (!applyTableRef.value) return
  const data = filteredApplyUsers.value
  const current = new Set(applySelectedIds.value)
  applyTableRef.value.clearSelection()
  data.forEach(row => {
    if (!current.has(row.id)) {
      applyTableRef.value.toggleRowSelection(row, true)
    }
  })
}

const handleApply = async () => {
  if (!applyingTemplate.value || applySelectedIds.value.length === 0) return
  applying.value = true
  try {
    const res = await api.users.applyPermissionTemplate(applyingTemplate.value.id, applySelectedIds.value)
    const msg = `已成功应用模板到 ${res.applied_count || 0} 个用户`
    if (res.skipped_count > 0) {
      ElMessage.warning(`${msg}，${res.skipped_count} 个用户被跳过`)
    } else {
      ElMessage.success(msg)
    }
    applyDialogVisible.value = false
  } catch (e) {
    console.error('应用模板失败:', e)
    ElMessage.error(e.response?.data?.error || '应用失败')
  } finally {
    applying.value = false
  }
}

onMounted(async () => {
  if (!canView.value) return
  await Promise.all([fetchCatalog(), fetchPermissions(), fetchTemplates()])
})
</script>

<style scoped>
.permission-templates {
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
  gap: 16px;
  flex-wrap: wrap;
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
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.template-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.template-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: white;
  background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
  flex-shrink: 0;
}

.template-icon.icon-builtin {
  background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
}

.template-icon.icon-role {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
}

.template-icon.icon-custom {
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
}

.template-info {
  min-width: 0;
  flex: 1;
}

.template-name {
  font-weight: 600;
  color: #0c4a6e;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.template-desc {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.content-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.content-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #475569;
}

.content-item .el-icon {
  font-size: 14px;
  color: #38bdf8;
}

.time-text {
  font-size: 13px;
  color: #64748b;
}

.edit-dialog-content {
  padding: 0 4px;
}

.form-tabs {
  margin-top: 8px;
}

.form-tabs :deep(.el-tabs__header) {
  margin-bottom: 12px;
}

.quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
  max-height: 420px;
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

.perm-hint {
  margin-bottom: 12px;
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

.perm-card-code {
  font-size: 11px;
  color: #94a3b8;
  font-family: 'Courier New', monospace;
  margin-top: 2px;
}

.view-content h4 {
  font-size: 13px;
  font-weight: 600;
  color: #0c4a6e;
  margin: 16px 0 8px 0;
  padding-left: 8px;
  border-left: 3px solid #0ea5e9;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.apply-dialog-content {
  padding: 0 4px;
}

.apply-tpl-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.06) 0%, rgba(14, 165, 233, 0.04) 100%);
  border-radius: 10px;
  border: 1px solid rgba(56, 189, 248, 0.15);
  margin: 12px 0;
}

.info-icon {
  font-size: 28px;
  color: #0ea5e9;
}

.info-text {
  flex: 1;
}

.info-name {
  font-size: 15px;
  font-weight: 600;
  color: #0c4a6e;
}

.info-desc {
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

.apply-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 12px 0;
}

.apply-search {
  flex: 1;
  max-width: 360px;
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

.apply-summary {
  margin-top: 12px;
  padding: 10px 14px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
  font-size: 13px;
  color: #0c4a6e;
}

.text-muted {
  color: #94a3b8;
  font-weight: normal;
}

.ml-2 {
  margin-left: 8px;
}

.mr-2 {
  margin-right: 8px;
}

.mb-2 {
  margin-bottom: 8px;
}
</style>
