<template>
  <div class="knowledge-base">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <svg class="knowledge-svg-icon" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
              <!-- 书本底座 -->
              <path class="book-base" d="M8 48 L8 16 Q8 12 12 12 L52 12 Q56 12 56 16 L56 48 Q56 52 52 52 L12 52 Q8 52 8 48Z" />
              <!-- 书本页面 -->
              <path class="book-page-left" d="M12 16 L12 44 Q12 46 14 46 L30 46 L30 16 L14 16 Q12 16 12 16Z" />
              <path class="book-page-right" d="M52 16 L52 44 Q52 46 50 46 L34 46 L34 16 L50 16 Q52 16 52 16Z" />
              <!-- 书脊 -->
              <rect class="book-spine" x="30" y="14" width="4" height="34" rx="1" />
              <!-- 书签 -->
              <path class="bookmark" d="M44 8 L44 22 L48 18 L52 22 L52 8Z" />
              <!-- 知识光芒 -->
              <g class="knowledge-rays">
                <line x1="32" y1="4" x2="32" y2="8" />
                <line x1="20" y1="6" x2="22" y2="10" />
                <line x1="44" y1="6" x2="42" y2="10" />
                <line x1="12" y1="12" x2="16" y2="14" />
                <line x1="52" y1="12" x2="48" y2="14" />
              </g>
              <!-- 知识节点 -->
              <circle class="knowledge-node" cx="20" cy="26" r="3" />
              <circle class="knowledge-node" cx="32" cy="22" r="3" />
              <circle class="knowledge-node" cx="44" cy="26" r="3" />
              <circle class="knowledge-node" cx="26" cy="36" r="3" />
              <circle class="knowledge-node" cx="38" cy="36" r="3" />
              <!-- 连接线 -->
              <g class="knowledge-lines">
                <line x1="20" y1="26" x2="32" y2="22" />
                <line x1="32" y1="22" x2="44" y2="26" />
                <line x1="20" y1="26" x2="26" y2="36" />
                <line x1="44" y1="26" x2="38" y2="36" />
                <line x1="26" y1="36" x2="38" y2="36" />
                <line x1="32" y1="22" x2="32" y2="30" />
              </g>
            </svg>
          </div>
          <div class="title-text">
            <h1>知识库</h1>
            <p class="subtitle">结构化管理和浏览知识文章</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button class="btn-secondary" :icon="Refresh" @click="refreshData">刷新</el-button>
          <el-button class="btn-gradient" type="primary" :icon="Plus" @click="createArticle">新建文章</el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up delay-100">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="12" :md="6" v-for="stat in statistics.slice(0, 4)" :key="stat.key">
          <div class="stat-card" :class="stat.class" @click="handleStatClick(stat)">
            <div class="stat-icon-wrapper">
              <el-icon class="stat-icon" :size="24">
                <component :is="stat.icon" />
              </el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索栏 -->
    <div class="filter-section animate-fade-in-up delay-200">
      <el-card class="filter-card glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Search /></el-icon>
              搜索筛选
            </span>
          </div>
        </template>
        <el-row :gutter="16" align="middle">
          <el-col :xs="24" :sm="8" :md="6">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索标题、内容、拼音..."
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :xs="12" :sm="6" :md="4">
            <el-select v-model="searchForm.category" placeholder="全部分类" clearable @change="handleSearch">
              <el-option
                v-for="cat in categories"
                :key="cat.id"
                :label="cat.name"
                :value="cat.id"
              />
            </el-select>
          </el-col>
          <el-col :xs="12" :sm="6" :md="4">
            <el-select v-model="searchForm.tag" placeholder="标签筛选" clearable @change="handleSearch">
              <el-option
                v-for="tag in tags"
                :key="tag"
                :label="tag"
                :value="tag"
              />
            </el-select>
          </el-col>
          <el-col :xs="12" :sm="6" :md="4">
            <el-select v-model="searchForm.status" placeholder="全部状态" clearable @change="handleSearch">
              <el-option label="已发布" value="published" />
              <el-option label="草稿" value="draft" />
            </el-select>
          </el-col>
          <el-col :xs="12" :sm="6" :md="4">
            <el-select v-model="searchForm.sort" placeholder="最新更新" @change="handleSearch">
              <el-option label="最新更新" value="updated" />
              <el-option label="创建时间" value="created" />
              <el-option label="浏览最多" value="views" />
            </el-select>
          </el-col>
          <el-col :xs="24" :sm="4" :md="2">
            <el-button class="btn-gradient" type="primary" @click="handleSearch">搜索</el-button>
            <el-button class="btn-secondary" link @click="resetSearch">重置</el-button>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 主内容区 -->
    <div class="main-content animate-fade-in-up delay-300">
      <!-- 左侧边栏 -->
      <div class="sidebar">
        <el-card shadow="never" class="sidebar-card">
          <template #header>
            <span class="sidebar-title">快捷导航</span>
          </template>
          <el-menu
            :default-active="activeMenu"
            @select="handleMenuSelect"
            class="nav-menu"
          >
            <el-menu-item index="all">
              <el-icon><Document /></el-icon>
              <span>全部文章</span>
            </el-menu-item>
            <el-menu-item index="published">
              <el-icon><CircleCheck /></el-icon>
              <span>已发布</span>
            </el-menu-item>
            <el-menu-item index="draft">
              <el-icon><EditPen /></el-icon>
              <span>草稿箱</span>
            </el-menu-item>
            <el-menu-item index="my">
              <el-icon><User /></el-icon>
              <span>我的文章</span>
            </el-menu-item>
            <el-menu-item index="favorites">
              <el-icon><Star /></el-icon>
              <span>我的收藏</span>
            </el-menu-item>
            <el-menu-item index="recent">
              <el-icon><Clock /></el-icon>
              <span>最近浏览</span>
            </el-menu-item>
            <el-menu-item index="pinned">
              <el-icon><Top /></el-icon>
              <span>置顶文章</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </div>

      <!-- 右侧内容 -->
      <div class="content">
        <el-card shadow="never">
          <!-- 工具栏 -->
          <div class="toolbar">
            <div class="toolbar-left">
              <el-radio-group v-model="viewMode" size="small">
                <el-radio-button label="list">
                  <el-icon><List /></el-icon> 列表
                </el-radio-button>
                <el-radio-button label="card">
                  <el-icon><Grid /></el-icon> 卡片
                </el-radio-button>
              </el-radio-group>
              <el-checkbox v-model="includeSubcategories" @change="handleSearch">
                包含子分类
              </el-checkbox>
            </div>
            <div class="toolbar-right">
              <span class="total-info">共 {{ total }} 条</span>
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :total="total"
                :page-sizes="[10, 20, 50]"
                layout="prev, pager, next"
                @change="handlePageChange"
                small
              />
            </div>
          </div>

          <!-- 文章列表 -->
          <div v-if="viewMode === 'list'" class="article-list">
            <el-table
              :data="articles"
              style="width: 100%"
              v-loading="loading"
            >
              <el-table-column type="selection" width="50" />
              <el-table-column label="文章" min-width="300">
                <template #default="{ row }">
                  <div class="article-info">
                    <div class="article-title-row">
                      <el-link type="primary" class="article-title" @click="viewArticle(row)">
                        {{ row.title }}
                      </el-link>
                      <el-tag v-if="row.is_pinned" type="danger" size="small" effect="dark" class="ml-2">置顶</el-tag>
                      <el-tag v-if="row.status === 'draft'" type="info" size="small" class="ml-2">草稿</el-tag>
                    </div>
                    <div class="article-tags" v-if="row.tags && row.tags.length">
                      <el-tag
                        v-for="tag in row.tags.slice(0, 3)"
                        :key="tag"
                        size="small"
                        effect="plain"
                        class="tag-item"
                      >
                        {{ tag }}
                      </el-tag>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="category_name" label="分类" width="120" />
              <el-table-column label="统计" width="150" align="center">
                <template #default="{ row }">
                  <div class="article-stats">
                    <span class="stat-item" title="浏览">
                      <el-icon><View /></el-icon>
                      {{ formatNumber(row.view_count) }}
                    </span>
                    <span class="stat-item" title="点赞">
                      <el-icon><Star /></el-icon>
                      {{ formatNumber(row.like_count) }}
                    </span>
                    <span class="stat-item" title="评论">
                      <el-icon><ChatDotRound /></el-icon>
                      {{ formatNumber(row.comment_count) }}
                    </span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="作者" width="120">
                <template #default="{ row }">
                  <router-link :to="`/users/${row.author_id}`" class="author-link">
                    <el-avatar :size="24" :src="getUserAvatar(row.author_avatar)" />
                    <span class="author-name">{{ row.author_name }}</span>
                  </router-link>
                </template>
              </el-table-column>
              <el-table-column label="时间" width="150">
                <template #default="{ row }">
                  <div class="time-info">
                    <div>{{ formatDate(row.updated_at) }}</div>
                    <div class="time-relative">{{ formatRelativeTime(row.updated_at) }}</div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button-group>
                    <el-button type="primary" link size="small" @click="viewArticle(row)">查看</el-button>
                    <el-button v-if="canEditArticle(row)" type="primary" link size="small" @click="editArticle(row)">编辑</el-button>
                  </el-button-group>
                  <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, row)">
                    <el-button type="primary" link size="small">
                      更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="share">分享</el-dropdown-item>
                        <el-dropdown-item command="favorite">{{ row.is_favorited ? '取消收藏' : '收藏' }}</el-dropdown-item>
                        <el-dropdown-item command="pin">{{ row.is_pinned ? '取消置顶' : '置顶' }}</el-dropdown-item>
                        <el-dropdown-item divided command="delete" class="text-danger">删除</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 卡片视图 -->
          <div v-else class="article-cards">
            <el-row :gutter="16">
              <el-col :xs="24" :sm="12" :md="8" v-for="article in articles" :key="article.id">
                <el-card class="article-card" :class="{ 'is-pinned': article.is_pinned }" shadow="hover">
                  <div class="card-header">
                    <div class="card-title-wrapper">
                      <el-link type="primary" class="card-title" @click="viewArticle(article)">
                        {{ article.title }}
                      </el-link>
                      <div class="card-badges">
                        <el-tag v-if="article.is_pinned" type="danger" size="small" effect="dark">置顶</el-tag>
                        <el-tag v-if="article.status === 'draft'" type="info" size="small">草稿</el-tag>
                      </div>
                    </div>
                  </div>
                  <div class="card-summary">{{ article.summary || article.content?.substring(0, 100) + '...' }}</div>
                  <div class="card-tags" v-if="article.tags && article.tags.length">
                    <el-tag
                      v-for="tag in article.tags.slice(0, 3)"
                      :key="tag"
                      size="small"
                      effect="plain"
                    >
                      {{ tag }}
                    </el-tag>
                  </div>
                  <div class="card-meta">
                    <span><el-icon><Folder /></el-icon> {{ article.category_name }}</span>
                    <router-link :to="`/users/${article.author_id}`" class="card-author-link">
                      <el-avatar :size="16" :src="getUserAvatar(article.author_avatar)" />
                      {{ article.author_name }}
                    </router-link>
                  </div>
                  <div class="card-stats">
                    <span><el-icon><View /></el-icon> {{ formatNumber(article.view_count) }}</span>
                    <span><el-icon><Star /></el-icon> {{ formatNumber(article.like_count) }}</span>
                    <span><el-icon><ChatDotRound /></el-icon> {{ formatNumber(article.comment_count) }}</span>
                  </div>
                  <div class="card-actions">
                    <el-button type="primary" link size="small" @click="viewArticle(article)">查看</el-button>
                    <el-button v-if="canEditArticle(article)" type="primary" link size="small" @click="editArticle(article)">编辑</el-button>
                    <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, article)">
                      <el-button type="primary" link size="small">更多</el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item command="share">分享</el-dropdown-item>
                          <el-dropdown-item command="favorite">{{ article.is_favorited ? '取消收藏' : '收藏' }}</el-dropdown-item>
                          <el-dropdown-item command="pin">{{ article.is_pinned ? '取消置顶' : '置顶' }}</el-dropdown-item>
                          <el-dropdown-item divided command="delete" class="text-danger">删除</el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>

          <!-- 空状态 -->
          <el-empty v-if="!loading && articles.length === 0" description="暂无文章">
            <el-button type="primary" @click="createArticle">创建第一篇文章</el-button>
          </el-empty>
        </el-card>
      </div>
    </div>



    <!-- 文章编辑对话框 -->
    <el-dialog
      v-model="editVisible"
      :title="isEditing ? '编辑文章' : '新建文章'"
      width="80%"
      top="5vh"
      destroy-on-close
    >
      <ArticleForm
        v-if="editVisible"
        :article="currentArticle"
        :categories="categories"
        @save="handleSave"
        @cancel="editVisible = false"
        @refresh-categories="loadCategories"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import {
  Plus, Refresh, Search, Document, CircleCheck, EditPen,
  User, Star, Clock, Top, List, Grid, View, ChatDotRound,
  ArrowDown, Folder
} from '@element-plus/icons-vue'
import ArticleForm from '@/components/knowledge/ArticleForm.vue'

// API 基础 URL
const API_BASE_URL = import.meta.env.DEV ? 'http://localhost:5000' : 'http://172.18.36.249:5000'

const router = useRouter()
const userStore = useUserStore()

const isAdmin = computed(() => {
  const user = userStore.currentUser
  if (!user) return false
  if (user.is_super_admin) return true
  return user.position === '管理员' || user.position?.includes('经理')
})

const canEditArticle = (article) => {
  if (isAdmin.value) return true
  return userStore.currentUser?.id === article.author_id
}

// 状态
const loading = ref(false)
const articles = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const viewMode = ref('list')
const activeMenu = ref('all')
const includeSubcategories = ref(true)
const editVisible = ref(false)
const isEditing = ref(false)
const currentArticle = ref(null)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category: '',
  tag: '',
  status: '',
  sort: 'updated'
})

// 分类和标签
const categories = ref([])
const tags = ref([])

// 统计数据 - 使用4种渐变配色
const statistics = ref([
  { key: 'total', label: '文章总数', value: 0, class: 'stat-card-total', icon: 'Document' },
  { key: 'published', label: '本月新增', value: 0, class: 'stat-card-create', icon: 'CircleCheck' },
  { key: 'views', label: '阅读量', value: 0, class: 'stat-card-update', icon: 'View' },
  { key: 'favorites', label: '收藏量', value: 0, class: 'stat-card-today', icon: 'Star' }
])

// API 请求
const apiRequest = async (url, options = {}) => {
  const token = localStorage.getItem('token')
  const headers = {
    ...options.headers,
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  }
  const response = await fetch(`${API_BASE_URL}${url}`, { ...options, headers })
  if (response.status === 401) {
    ElMessage.error('请先登录')
    throw new Error('Unauthorized')
  }
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  return response.json()
}

// 加载文章列表
const loadArticles = async () => {
  loading.value = true
  try {
    // 根据 activeMenu 选择不同的 API
    let apiUrl = '/api/knowledge/articles'
    const params = new URLSearchParams({
      page: currentPage.value,
      per_page: pageSize.value,
      keyword: searchForm.keyword,
      category_id: searchForm.category,
      status: searchForm.status,
      sort_by: searchForm.sort
    })
    
    // 根据 activeMenu 添加筛选条件
    if (activeMenu.value === 'favorites') {
      // 我的收藏 - 使用 favorites 参数
      params.append('favorites', 'true')
    } else if (activeMenu.value === 'my') {
      // 我的文章 - 使用专门的 API
      apiUrl = '/api/knowledge/articles/my'
    } else if (activeMenu.value === 'published') {
      // 已发布 - 通过 status 参数筛选
      params.set('status', 'published')
    } else if (activeMenu.value === 'draft') {
      // 草稿 - 通过 status 参数筛选
      params.set('status', 'draft')
    } else if (activeMenu.value === 'pinned') {
      // 置顶文章 - 后端需要支持 is_pinned 参数
      // 暂时通过前端过滤或特殊处理
      params.append('is_pinned', 'true')
    }
    // all - 全部文章，不需要额外参数
    
    const response = await apiRequest(`${apiUrl}?${params}`)
    articles.value = response.data?.articles || []
    total.value = response.data?.total || 0
  } catch (error) {
    console.error('加载文章失败:', error)
    ElMessage.error('加载文章失败')
  } finally {
    loading.value = false
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await apiRequest('/api/knowledge/stats')
    const data = response.data || {}
    statistics.value = [
      { key: 'total', label: '文章总数', value: data.total || 0, class: 'stat-card-total', icon: 'Document' },
      { key: 'published', label: '本月新增', value: data.monthly_new || data.published || 0, class: 'stat-card-create', icon: 'CircleCheck' },
      { key: 'views', label: '阅读量', value: formatNumber(data.views || 0), class: 'stat-card-update', icon: 'View' },
      { key: 'favorites', label: '收藏量', value: data.favorites || 0, class: 'stat-card-today', icon: 'Star' }
    ]
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

// 加载分类
const loadCategories = async () => {
  try {
    const response = await apiRequest('/api/knowledge/categories')
    categories.value = response.data || []
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

// 加载标签
const loadTags = async () => {
  try {
    const response = await apiRequest('/api/knowledge/tags')
    tags.value = (response.data || []).map(t => t.name)
  } catch (error) {
    console.error('加载标签失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadArticles()
}

// 重置搜索
const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.category = ''
  searchForm.tag = ''
  searchForm.status = ''
  searchForm.sort = 'updated'
  handleSearch()
}

// 菜单选择
const handleMenuSelect = (index) => {
  activeMenu.value = index
  searchForm.status = '' // 重置状态筛选
  
  // 根据不同菜单设置不同的筛选逻辑
  switch (index) {
    case 'all':
      // 全部文章 - 清除所有筛选
      searchForm.status = ''
      break
    case 'published':
      // 已发布
      searchForm.status = 'published'
      break
    case 'draft':
      // 草稿
      searchForm.status = 'draft'
      break
    case 'my':
      // 我的文章 - 使用专门的 API，不需要额外参数
      break
    case 'favorites':
      // 我的收藏 - 使用 favorites 参数
      break
    case 'recent':
      // TODO: 加载最近浏览
      break
    case 'pinned':
      // TODO: 加载置顶
      break
  }
  handleSearch()
}

// 统计卡片点击
const handleStatClick = (stat) => {
  // 阅读量和收藏量是汇总数据，不适合筛选，跳过
  if (stat.key === 'views' || stat.key === 'favorites') {
    ElMessage.info('该数据是汇总统计，无法筛选')
    return
  }
  handleMenuSelect(stat.key)
}

// 分页
const handlePageChange = () => {
  loadArticles()
}

// 刷新
const refreshData = () => {
  loadArticles()
  loadStats()
}

// 创建文章
const createArticle = () => {
  currentArticle.value = null
  isEditing.value = false
  editVisible.value = true
}

// 查看文章
const viewArticle = (article) => {
  // 跳转到文章详情页
  router.push(`/knowledge/articles/${article.id}`)
}

// 编辑文章
const editArticle = async (article) => {
  // 先获取完整的文章详情（包含内容）
  try {
    const response = await apiRequest(`/api/knowledge/articles/${article.id}`)
    if (response.success) {
      currentArticle.value = response.data
    } else {
      currentArticle.value = article
    }
  } catch (error) {
    console.error('获取文章详情失败:', error)
    currentArticle.value = article
  }
  isEditing.value = true
  editVisible.value = true
}

// 保存文章
const handleSave = async (articleData) => {
  try {
    const method = isEditing.value ? 'PUT' : 'POST'
    const url = isEditing.value
      ? `/api/knowledge/articles/${currentArticle.value.id}`
      : '/api/knowledge/articles'
    await apiRequest(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(articleData)
    })
    ElMessage.success(isEditing.value ? '更新成功' : '创建成功')
    editVisible.value = false
    loadArticles()
    loadStats()
  } catch (error) {
    console.error('保存文章失败:', error)
    ElMessage.error('保存文章失败')
  }
}

// 更多操作
const handleCommand = async (cmd, article) => {
  switch (cmd) {
    case 'share':
      // TODO: 分享功能
      break
    case 'favorite':
      try {
        await apiRequest(`/api/knowledge/articles/${article.id}/favorite`, {
          method: article.is_favorited ? 'DELETE' : 'POST'
        })
        article.is_favorited = !article.is_favorited
        ElMessage.success(article.is_favorited ? '收藏成功' : '取消收藏')
        loadStats()
      } catch (error) {
        ElMessage.error('操作失败')
      }
      break
    case 'pin':
      try {
        await apiRequest(`/api/knowledge/articles/${article.id}/pin`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ is_pinned: !article.is_pinned })
        })
        article.is_pinned = !article.is_pinned
        ElMessage.success(article.is_pinned ? '置顶成功' : '取消置顶')
        loadArticles()
      } catch (error) {
        ElMessage.error('操作失败')
      }
      break
    case 'delete':
      try {
        await ElMessageBox.confirm('确定要删除这篇文章吗？', '提示', { type: 'warning' })
        await apiRequest(`/api/knowledge/articles/${article.id}`, { method: 'DELETE' })
        ElMessage.success('删除成功')
        loadArticles()
        loadStats()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败')
        }
      }
      break
  }
}

// 格式化数字
const formatNumber = (num) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num || 0
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

// 格式化相对时间
const formatRelativeTime = (date) => {
  if (!date) return ''
  const now = new Date()
  const past = new Date(date)
  const diff = (now - past) / 1000

  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  if (diff < 604800) return `${Math.floor(diff / 86400)}天前`
  return formatDate(date)
}

// 获取用户头像URL
const getUserAvatar = (avatar) => {
  if (!avatar) {
    // 使用绝对路径确保头像能正确显示
    return `${window.location.origin}/avatar-placeholder.png`
  }
  if (avatar.startsWith('http://') || avatar.startsWith('https://')) {
    return avatar
  }
  return `${API_BASE_URL}${avatar}`
}

// 初始化
onMounted(() => {
  loadArticles()
  loadStats()
  loadCategories()
  loadTags()
})
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.knowledge-base {
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

/* SVG 图标样式 */
.knowledge-svg-icon {
  width: 44px;
  height: 44px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.knowledge-svg-icon .book-base {
  fill: rgba(255, 255, 255, 0.95);
}

.knowledge-svg-icon .book-page-left,
.knowledge-svg-icon .book-page-right {
  fill: rgba(255, 255, 255, 0.9);
}

.knowledge-svg-icon .book-spine {
  fill: rgba(255, 255, 255, 0.7);
}

.knowledge-svg-icon .bookmark {
  fill: #f56c6c;
}

.knowledge-svg-icon .knowledge-rays line {
  stroke: #ffd700;
  stroke-width: 2;
  stroke-linecap: round;
}

.knowledge-svg-icon .knowledge-node {
  fill: #409EFF;
  stroke: white;
  stroke-width: 1.5;
}

.knowledge-svg-icon .knowledge-lines line {
  stroke: #409EFF;
  stroke-width: 1.5;
  opacity: 0.8;
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
  cursor: pointer;
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

.stat-card-total::before { background: linear-gradient(90deg, #7dd3fc, #38bdf8); }
.stat-card-create::before { background: linear-gradient(90deg, #11998e, #38ef7d); }
.stat-card-update::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.stat-card-today::before { background: linear-gradient(90deg, #ec4899, #f472b6); }

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

.stat-card-total .stat-icon-wrapper {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #7dd3fc;
  box-shadow: 0 4px 15px -3px rgba(56, 189, 248, 0.4);
}

.stat-card-create .stat-icon-wrapper {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #059669;
  box-shadow: 0 4px 15px -3px rgba(16, 185, 129, 0.4);
}

.stat-card-update .stat-icon-wrapper {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 4px 15px -3px rgba(245, 158, 11, 0.4);
}

.stat-card-today .stat-icon-wrapper {
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

.stat-card-total .stat-value {
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-create .stat-value {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-update .stat-value {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card-today .stat-value {
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

/* 筛选区域 */
.filter-section {
  margin-bottom: 24px;
}

.filter-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

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

.btn-secondary {
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(56, 189, 248, 0.1);
  border-color: #0ea5e9;
  color: #0ea5e9;
}

/* 主内容区 */
.main-content {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.sidebar {
  width: 220px;
  flex-shrink: 0;
}

.sidebar-card {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.sidebar-title {
  font-weight: 600;
  color: #1e293b;
}

.nav-menu {
  border-right: none;
}

.nav-menu :deep(.el-menu-item) {
  border-radius: 10px;
  margin: 4px 0;
  transition: all 0.3s;
}

.nav-menu :deep(.el-menu-item:hover) {
  background: rgba(56, 189, 248, 0.08);
}

.nav-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.15) 0%, rgba(14, 165, 233, 0.15) 100%);
  color: #7dd3fc;
  font-weight: 600;
}

.content {
  flex: 1;
  min-width: 0;
}

.content > .el-card {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.total-info {
  color: #64748b;
  font-size: 13px;
  background: rgba(241, 245, 249, 0.8);
  padding: 4px 12px;
  border-radius: 20px;
}

/* 文章列表 */
.article-list {
  min-height: 400px;
}

.article-list :deep(.el-table) {
  --el-table-header-bg-color: rgba(241, 245, 249, 0.8);
  --el-table-row-hover-bg-color: rgba(56, 189, 248, 0.05);
}

.article-list :deep(.el-table__header th) {
  font-weight: 600;
  color: #1e293b;
  background: rgba(241, 245, 249, 0.8);
}

.article-list :deep(.el-table__row) {
  transition: all 0.3s;
}

.article-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.article-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.article-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.article-title:hover {
  color: #7dd3fc;
}

.article-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.tag-item {
  margin-right: 0;
}

.article-stats {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #64748b;
  font-size: 13px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-name {
  font-size: 13px;
  color: #475569;
}

.author-link {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: inherit;
  transition: opacity 0.3s;
}

.author-link:hover {
  opacity: 0.7;
}

.author-link .author-name {
  color: #7dd3fc;
}

.card-author-link {
  display: flex;
  align-items: center;
  gap: 4px;
  text-decoration: none;
  color: #64748b;
  transition: color 0.3s;
}

.card-author-link:hover {
  color: #7dd3fc;
}

.time-info {
  font-size: 13px;
}

.time-relative {
  color: #94a3b8;
  font-size: 12px;
}

/* 卡片视图 */
.article-cards {
  min-height: 400px;
}

.article-card {
  margin-bottom: 16px;
  border-radius: 16px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(226, 232, 240, 0.6);
  overflow: hidden;
}

.article-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.12), 0 10px 20px -5px rgba(0, 0, 0, 0.08);
  border-color: rgba(56, 189, 248, 0.3);
}

.article-card.is-pinned {
  border: 1px solid #f56c6c;
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.05) 0%, rgba(255, 255, 255, 0.95) 100%);
}

.article-card.is-pinned:hover {
  border-color: #f56c6c;
  box-shadow: 0 20px 40px -10px rgba(245, 108, 108, 0.2);
}

.card-header {
  margin-bottom: 12px;
}

.card-title-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.card-title {
  font-weight: 600;
  font-size: 15px;
  flex: 1;
  line-height: 1.4;
  color: #1e293b;
}

.card-title:hover {
  color: #7dd3fc;
}

.card-badges {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.card-summary {
  color: #475569;
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 12px;
  min-height: 40px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-tags {
  margin-bottom: 12px;
}

.card-meta {
  display: flex;
  gap: 16px;
  color: #64748b;
  font-size: 12px;
  margin-bottom: 12px;
}

.card-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-stats {
  display: flex;
  gap: 16px;
  color: #64748b;
  font-size: 12px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.card-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-actions {
  display: flex;
  gap: 8px;
}

/* 工具类 */
.ml-2 {
  margin-left: 8px;
}

.text-danger {
  color: #f56c6c;
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

/* 响应式 */
@media screen and (max-width: 1200px) {
  .main-content {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
  }

  .nav-menu {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .nav-menu :deep(.el-menu-item) {
    margin: 0;
  }
}

@media screen and (max-width: 768px) {
  .knowledge-base {
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

  .knowledge-svg-icon {
    width: 32px;
    height: 32px;
  }

  .title-text h1 {
    font-size: 22px;
  }

  .subtitle {
    font-size: 13px;
  }

  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
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

  .toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .filter-card :deep(.el-row) {
    flex-direction: column;
  }

  .filter-card :deep(.el-col) {
    width: 100% !important;
    margin-bottom: 12px;
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

  .article-card {
    margin-bottom: 12px;
  }
}
</style>
