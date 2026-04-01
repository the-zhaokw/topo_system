<template>
  <div class="knowledge-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1>知识库</h1>
          <p>结构化管理和浏览知识文章</p>
        </div>
        <el-button type="primary" @click="openArticleDialog()">
          新建文章
        </el-button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <el-card class="search-card" shadow="never">
      <el-row :gutter="20" align="middle">
        <el-col :span="8">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索文章标题、内容、拼音..."
            clearable
            @keyup.enter="handleSearch"
            @input="handleSearchInput"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <!-- 搜索建议 -->
          <div v-if="searchSuggestions.length > 0" class="search-suggestions">
            <div
              v-for="item in searchSuggestions"
              :key="item.id"
              class="suggestion-item"
              @click="applySuggestion(item)"
            >
              <el-icon v-if="item.type === 'article'"><Document /></el-icon>
              <el-icon v-else><CollectionTag /></el-icon>
              <span>{{ item.title || item.name }}</span>
            </div>
          </div>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.category_id" placeholder="全部分类" clearable @change="handleSearch">
            <el-option
              v-for="cat in flattenCategories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
              :style="{ paddingLeft: cat.level * 20 + 'px' }"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.tags" placeholder="标签筛选" multiple collapse-tags clearable @change="handleSearch">
            <el-option
              v-for="tag in availableTags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.name"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.sort_by" placeholder="排序方式" @change="handleSearch">
            <el-option label="最新更新" value="updated_at" />
            <el-option label="创建时间" value="created_at" />
            <el-option label="浏览最多" value="view_count" />
            <el-option label="点赞最多" value="like_count" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 主内容区 -->
    <div class="knowledge-layout">
      <!-- 左侧边栏 -->
      <div class="knowledge-sidebar">
        <!-- 分类树 -->
        <el-card shadow="never" class="sidebar-card">
          <template #header>
            <div class="sidebar-header">
              <span>分类导航</span>
              <el-button type="primary" link :icon="Plus" @click="openCategoryDialog()">
                新建
              </el-button>
            </div>
          </template>
          <el-input
            v-model="categorySearchKeyword"
            placeholder="搜索分类..."
            clearable
            size="small"
            class="mb-2"
          />
          <el-scrollbar height="calc(100vh - 420px)">
            <el-tree
              ref="categoryTreeRef"
              :data="filteredCategoryTree"
              :props="{ label: 'name', children: 'children' }"
              node-key="id"
              :expand-on-click-node="false"
              :filter-node-method="filterCategory"
              @node-click="handleCategorySelect"
              highlight-current
              draggable
              :allow-drop="allowDrop"
              :allow-drag="allowDrag"
              @node-drop="handleCategoryDrop"
            >
              <template #default="{ node, data }">
                <span class="category-node" @contextmenu.prevent="showCategoryContextMenu($event, data)">
                  <el-icon v-if="data.children?.length"><Folder /></el-icon>
                  <el-icon v-else><Document /></el-icon>
                  <span class="category-name">{{ node.label }}</span>
                  <span class="category-count">({{ data.article_count || 0 }})</span>
                </span>
              </template>
            </el-tree>
          </el-scrollbar>
        </el-card>

        <!-- 热门标签 -->
        <el-card shadow="never" class="sidebar-card">
          <template #header>
            <span>热门标签</span>
          </template>
          <div class="tag-cloud">
            <el-tag
              v-for="tag in popularTags"
              :key="tag.id"
              :type="selectedTags.includes(tag.name) ? 'primary' : 'info'"
              class="tag-item"
              @click="toggleTag(tag.name)"
              size="small"
            >
              {{ tag.name }}
            </el-tag>
          </div>
        </el-card>

        <!-- 快捷链接 -->
        <el-card shadow="never" class="sidebar-card">
          <template #header>
            <span>快捷访问</span>
          </template>
          <el-menu :default-active="activeMenu" @select="handleMenuSelect">
            <el-menu-item index="all">
              <el-icon><Document /></el-icon>
              <span>全部文章</span>
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

      <!-- 右侧主内容 -->
      <div class="knowledge-main">
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
              <el-divider direction="vertical" />
              <el-checkbox v-model="listQuery.onlyMine" @change="handleSearch">
                仅看我的
              </el-checkbox>
              <el-checkbox v-model="listQuery.includeSubcategories" @change="handleSearch">
                包含子分类
              </el-checkbox>
            </div>
            <div class="toolbar-right">
              <el-button v-if="selectedArticles.length > 0" size="small" @click="handleBatchMove">
                批量移动
              </el-button>
              <el-button v-if="selectedArticles.length > 0" size="small" type="danger" @click="handleBatchDelete">
                批量删除
              </el-button>
              <el-divider direction="vertical" v-if="selectedArticles.length > 0" />
              <el-pagination
                v-model:current-page="listQuery.page"
                v-model:page-size="listQuery.per_page"
                :total="total"
                :page-sizes="[10, 20, 50, 100]"
                layout="total, sizes, prev, pager, next"
                @size-change="loadArticles"
                @current-change="loadArticles"
                small
              />
            </div>
          </div>

          <!-- 文章列表 - 列表模式 -->
          <div v-if="viewMode === 'list'" v-loading="loading" class="article-list">
            <el-empty v-if="!loading && articleList.length === 0" description="暂无文章">
              <el-button type="primary" @click="openArticleDialog()">创建第一篇文章</el-button>
            </el-empty>
            
            <el-table
              v-else
              ref="articleTableRef"
              :data="articleList"
              style="width: 100%"
              @selection-change="handleSelectionChange"
              :row-class-name="getRowClassName"
            >
              <el-table-column type="selection" width="50" />
              <el-table-column prop="title" label="标题" min-width="280">
                <template #default="{ row }">
                  <div class="article-title-wrapper">
                    <el-link type="primary" class="article-title" @click="handleArticleClick(row)">
                      {{ row.title }}
                    </el-link>
                    <div class="article-tags">
                      <el-tag v-if="row.is_pinned" type="danger" size="small" effect="dark">置顶</el-tag>
                      <el-tag v-if="row.status === 'draft'" type="info" size="small">草稿</el-tag>
                      <el-tag v-if="row.is_public === false" type="warning" size="small">私密</el-tag>
                      <el-tag v-for="tag in (Array.isArray(row.tags) ? row.tags : []).slice(0, 3)" :key="tag" size="small" effect="plain">
                        {{ tag }}
                      </el-tag>
                    </div>
                  </div>
                  <div class="article-summary">{{ row.summary }}</div>
                </template>
              </el-table-column>
              <el-table-column prop="category_name" label="分类" width="120" />
              <el-table-column prop="author_name" label="作者" width="100" />
              <el-table-column label="统计" width="150" align="center">
                <template #default="{ row }">
                  <div class="article-stats">
                    <span title="浏览"><el-icon><View /></el-icon> {{ row.view_count || 0 }}</span>
                    <span title="点赞"><el-icon><Star /></el-icon> {{ row.like_count || 0 }}</span>
                    <span title="版本">v{{ row.version || 1 }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="updated_at" label="更新时间" width="160">
                <template #default="{ row }">
                  <div>{{ formatDate(row.updated_at) }}</div>
                  <div class="text-gray">{{ formatRelativeTime(row.updated_at) }}</div>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="220" fixed="right">
                <template #default="{ row }">
                  <el-button-group>
                    <el-button type="primary" link @click="handleArticleClick(row)">查看</el-button>
                    <el-button v-if="canEditArticle(row)" type="primary" link @click="openArticleDialog(row)">编辑</el-button>
                  </el-button-group>
                  <el-dropdown trigger="click" @command="(cmd) => handleArticleCommand(cmd, row)">
                    <el-button type="primary" link>
                      更多<el-icon><ArrowDown /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="version">版本历史</el-dropdown-item>
                        <el-dropdown-item command="share">分享管理</el-dropdown-item>
                        <el-dropdown-item command="favorite">{{ row.is_favorited ? '取消收藏' : '收藏' }}</el-dropdown-item>
                        <el-dropdown-item command="pin">{{ row.is_pinned ? '取消置顶' : '置顶' }}</el-dropdown-item>
                        <el-dropdown-item divided command="export">导出 Markdown</el-dropdown-item>
                        <el-dropdown-item command="delete" class="text-danger">删除</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 文章列表 - 卡片模式 -->
          <div v-else v-loading="loading" class="article-cards">
            <el-empty v-if="!loading && articleList.length === 0" description="暂无文章">
              <el-button type="primary" @click="openArticleDialog()">创建第一篇文章</el-button>
            </el-empty>
            
            <el-row :gutter="20" v-else>
              <el-col :xs="24" :sm="12" :md="8" :lg="8" v-for="article in articleList" :key="article.id">
                <el-card class="article-card" :class="{ 'is-pinned': article.is_pinned }" shadow="hover">
                  <div class="card-header">
                    <div class="card-title-wrapper">
                      <el-link type="primary" class="card-title" @click="handleArticleClick(article)">
                        {{ article.title }}
                      </el-link>
                      <div class="card-badges">
                        <el-tag v-if="article.is_pinned" type="danger" size="small" effect="dark">置顶</el-tag>
                        <el-tag v-if="article.status === 'draft'" type="info" size="small">草稿</el-tag>
                      </div>
                    </div>
                  </div>
                  <div class="card-summary">{{ article.summary || (article.content && article.content.substring(0, 100) + '...') || '' }}</div>
                  <div class="card-tags" v-if="Array.isArray(article.tags) && article.tags.length">
                    <el-tag v-for="tag in article.tags.slice(0, 3)" :key="tag" size="small" effect="plain">
                      {{ tag }}
                    </el-tag>
                  </div>
                  <div class="card-meta">
                    <span><el-icon><User /></el-icon> {{ article.author_name }}</span>
                    <span><el-icon><Folder /></el-icon> {{ article.category_name }}</span>
                  </div>
                  <div class="card-stats">
                    <span title="浏览"><el-icon><View /></el-icon> {{ article.view_count || 0 }}</span>
                    <span title="点赞"><el-icon><Star /></el-icon> {{ article.like_count || 0 }}</span>
                    <span title="评论"><el-icon><ChatDotRound /></el-icon> {{ article.comment_count || 0 }}</span>
                    <span>v{{ article.version || 1 }}</span>
                  </div>
                  <div class="card-actions">
                    <el-button type="primary" link @click="handleArticleClick(article)">查看</el-button>
                    <el-button v-if="canEditArticle(article)" type="primary" link @click="openArticleDialog(article)">编辑</el-button>
                    <el-button type="primary" link @click="showVersionHistory(article)">版本</el-button>
                    <el-button type="primary" link @click="showShareManager(article)">分享</el-button>
                    <el-dropdown trigger="click" @command="(cmd) => handleArticleCommand(cmd, article)">
                      <el-button type="primary" link>更多</el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item command="favorite">{{ article.is_favorited ? '取消收藏' : '收藏' }}</el-dropdown-item>
                          <el-dropdown-item command="pin">{{ article.is_pinned ? '取消置顶' : '置顶' }}</el-dropdown-item>
                          <el-dropdown-item divided command="export">导出 Markdown</el-dropdown-item>
                          <el-dropdown-item command="delete" class="text-danger">删除</el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 文章详情抽屉 -->
    <el-drawer
      v-model="articleDetailVisible"
      :title="currentArticle?.title"
      size="70%"
      destroy-on-close
    >
      <div v-if="currentArticle" class="article-detail">
        <div class="detail-header">
          <div class="detail-meta">
            <span><el-icon><User /></el-icon> {{ currentArticle.author_name }}</span>
            <span><el-icon><Folder /></el-icon> {{ currentArticle.category_name }}</span>
            <span><el-icon><Clock /></el-icon> {{ formatDate(currentArticle.created_at) }}</span>
            <span>版本: v{{ currentArticle.version || 1 }}</span>
          </div>
          <div class="detail-actions">
            <el-button-group>
              <el-button @click="openArticleDialog(currentArticle)">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-button @click="showVersionHistory(currentArticle)">
                <el-icon><Clock /></el-icon> 版本
              </el-button>
              <el-button @click="showShareManager(currentArticle)">
                <el-icon><Share /></el-icon> 分享
              </el-button>
            </el-button-group>
          </div>
        </div>
        <el-divider />
        <div class="detail-content" v-html="renderMarkdown(currentArticle.content)"></div>
        
        <!-- 附件 -->
        <div v-if="currentArticle.attachments?.length" class="detail-attachments">
          <h4>附件</h4>
          <div v-for="att in currentArticle.attachments" :key="att.id" class="attachment-item">
            <el-icon><Document /></el-icon>
            <span>{{ att.filename }}</span>
            <el-button type="primary" link @click="downloadAttachment(att)">下载</el-button>
          </div>
        </div>
        
        <!-- 相关文章 -->
        <div v-if="relatedArticles.length > 0" class="detail-related">
          <el-divider />
          <h4>相关文章</h4>
          <div class="related-list">
            <div v-for="article in relatedArticles" :key="article.id" class="related-item" @click="loadArticleDetail(article.id)">
              <el-icon><Document /></el-icon>
              <span>{{ article.title }}</span>
            </div>
          </div>
        </div>
        
        <!-- 评论区 -->
        <div class="detail-comments">
          <el-divider />
          <h4>评论 ({{ comments.length }})</h4>
          <div class="comment-input">
            <el-input
              v-model="newComment"
              type="textarea"
              :rows="3"
              placeholder="发表评论..."
            />
            <el-button type="primary" @click="submitComment" class="mt-2">
              发表评论
            </el-button>
          </div>
          <div class="comment-list">
            <div v-for="comment in comments" :key="comment.id" class="comment-item">
              <div class="comment-header">
                <span class="comment-author">{{ comment.author_name }}</span>
                <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
              </div>
              <div class="comment-content">{{ comment.content }}</div>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- 文章编辑对话框 -->
    <el-dialog
      v-model="articleDialogVisible"
      :title="isEditing ? '编辑文章' : '新建文章'"
      width="85%"
      top="3vh"
      destroy-on-close
    >
      <ArticleForm
        ref="articleFormRef"
        :article="currentArticle"
        :categories="categoryTree"
        @save="handleArticleSave"
        @cancel="articleDialogVisible = false"
        @refresh-categories="loadCategoryTree"
      />
    </el-dialog>

    <!-- 分类编辑对话框 -->
    <el-dialog v-model="categoryDialogVisible" :title="isEditingCategory ? '编辑分类' : '新建分类'" width="500px">
      <el-form :model="categoryForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="categoryForm.name" placeholder="分类名称" />
        </el-form-item>
        <el-form-item label="父分类">
          <el-tree-select
            v-model="categoryForm.parent_id"
            :data="categoryTree"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="无（顶级分类）"
            clearable
            check-strictly
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="categoryForm.description" type="textarea" :rows="3" placeholder="分类描述（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCategory">保存</el-button>
      </template>
    </el-dialog>

    <!-- 版本历史对话框 -->
    <VersionHistory
      v-model:visible="versionHistoryVisible"
      :article-id="currentArticle?.id"
      @restore="handleVersionRestore"
    />

    <!-- 分享管理对话框 -->
    <ShareManager
      v-model:visible="shareManagerVisible"
      :article-id="currentArticle?.id"
      :article-title="currentArticle?.title"
    />

    <!-- 批量移动对话框 -->
    <el-dialog v-model="batchMoveVisible" title="批量移动到" width="400px">
      <el-tree-select
        v-model="targetCategoryId"
        :data="categoryTree"
        :props="{ label: 'name', value: 'id', children: 'children' }"
        placeholder="选择目标分类"
        check-strictly
      />
      <template #footer>
        <el-button @click="batchMoveVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmBatchMove">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { 
  Search, Plus, Document, CollectionTag, View, Star, 
  Folder, User, Clock, Top, List, Grid, ArrowDown,
  Edit, Share, ChatDotRound, Upload
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import VersionHistory from '@/components/VersionHistory.vue'
import ShareManager from '@/components/ShareManager.vue'
import BlockEditor from '@/components/BlockEditor.vue'
import ArticleForm from '@/components/knowledge/ArticleForm.vue'

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

// API 基础 URL - 生产环境使用完整 URL
const API_BASE_URL = import.meta.env.DEV ? '' : 'http://172.18.36.249:5000'

// 通用 API 请求函数
const apiRequest = async (url, options = {}) => {
  const token = localStorage.getItem('token')
  const headers = {
    ...options.headers,
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  }
  const response = await fetch(`${API_BASE_URL}${url}`, { ...options, headers })
  if (response.status === 401) {
    ElMessage.error('请先登录')
    router.push('/login')
    throw new Error('Unauthorized')
  }
  if (response.status === 403) {
    ElMessage.error('没有权限')
    throw new Error('Forbidden')
  }
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  return response.json()
}

// ============ 状态定义 ============
const loading = ref(false)
const isMounted = ref(false)
const articleList = ref([])
const total = ref(0)
const selectedArticles = ref([])
const categoryTree = ref([])
const availableTags = ref([])
const currentArticle = ref(null)
const relatedArticles = ref([])
const comments = ref([])
const newComment = ref('')

const categoryTreeRef = ref(null)
const articleTableRef = ref(null)
const articleFormRef = ref(null)

// 视图模式
const viewMode = ref('list')
const activeMenu = ref('all')
const categorySearchKeyword = ref('')
const selectedTags = ref([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category_id: null,
  tags: [],
  sort_by: 'updated_at'
})

// 列表查询
const listQuery = reactive({
  page: 1,
  per_page: 20,
  onlyMine: false,
  includeSubcategories: true
})

// 搜索建议
const searchSuggestions = ref([])

// 对话框状态
const articleDetailVisible = ref(false)
const articleDialogVisible = ref(false)
const categoryDialogVisible = ref(false)
const versionHistoryVisible = ref(false)
const shareManagerVisible = ref(false)
const batchMoveVisible = ref(false)

// 表单数据
const articleForm = reactive({
  id: null,
  title: '',
  summary: '',
  content: '',
  category_id: null,
  tags: [],
  is_public: true,
  allow_comment: true,
  is_pinned: false,
  attachments: []
})

const articleAttachments = ref([])

const categoryForm = reactive({
  id: null,
  name: '',
  parent_id: null,
  description: ''
})

const targetCategoryId = ref(null)
const isEditing = ref(false)
const isEditingCategory = ref(false)

// ============ 计算属性 ============
const flattenCategories = computed(() => {
  const result = []
  const flatten = (items) => {
    if (!Array.isArray(items)) return
    items.forEach(item => {
      result.push({ ...item, level: item.level || 0 })
      if (item.children && Array.isArray(item.children)) {
        item.children.forEach(child => {
          result.push({ ...child, level: (item.level || 0) + 1 })
        })
      }
    })
  }
  flatten(categoryTree.value)
  return result
})

const filteredCategoryTree = computed(() => {
  if (!categorySearchKeyword.value) return categoryTree.value
  const keyword = categorySearchKeyword.value.toLowerCase()
  const filter = (items) => {
    return items.filter(item => {
      const match = item.name.toLowerCase().includes(keyword)
      if (item.children) {
        item.children = filter(item.children)
        return match || item.children.length > 0
      }
      return match
    })
  }
  return filter([...categoryTree.value])
})

const popularTags = computed(() => {
  return Array.isArray(availableTags.value) ? availableTags.value.slice(0, 15) : []
})

// ============ 方法 ============
const loadArticles = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: listQuery.page,
      per_page: listQuery.per_page,
      category_id: searchForm.category_id || '',
      keyword: searchForm.keyword,
      tags: searchForm.tags.join(','),
      sort_by: searchForm.sort_by,
      only_mine: listQuery.onlyMine,
      include_subcategories: listQuery.includeSubcategories
    })
    const response = await apiRequest(`/api/knowledge/articles?${params}`)
    if (isMounted.value) {
      articleList.value = response?.data?.articles || []
      total.value = response?.data?.total || 0
    }
  } catch (error) {
    console.error('加载文章失败:', error)
    ElMessage.error('加载文章失败')
  } finally {
    if (isMounted.value) {
      loading.value = false
    }
  }
}

const loadCategoryTree = async () => {
  try {
    const response = await apiRequest(`/api/knowledge/categories/tree`)
    if (isMounted.value) {
      categoryTree.value = response?.data || []
    }
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

const loadTags = async () => {
  try {
    const response = await apiRequest(`/api/knowledge/tags`)
    if (isMounted.value) {
      availableTags.value = Array.isArray(response?.data) ? response.data : []
    }
  } catch (error) {
    console.error('加载标签失败:', error)
  }
}

const handleSearch = () => {
  listQuery.page = 1
  loadArticles()
}

const handleSearchInput = async () => {
  if (!searchForm.keyword || searchForm.keyword.length < 2) {
    searchSuggestions.value = []
    return
  }
  if (!isMounted.value) return
  try {
    const response = await apiRequest(`/api/knowledge/enhanced/search/suggestions?keyword=${searchForm.keyword}`)
    if (isMounted.value) {
      searchSuggestions.value = response?.data?.suggestions || response?.data || []
    }
  } catch (error) {
    if (isMounted.value) {
      console.error('获取搜索建议失败:', error)
    }
  }
}

const applySuggestion = (item) => {
  if (item.type === 'article') {
    loadArticleDetail(item.id)
  } else {
    searchForm.tags = [item.name]
    handleSearch()
  }
  searchSuggestions.value = []
}

const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.category_id = null
  searchForm.tags = []
  searchForm.sort_by = 'updated_at'
  listQuery.onlyMine = false
  selectedTags.value = []
  handleSearch()
}

const handleCategorySelect = (data) => {
  searchForm.category_id = data.id
  handleSearch()
}

const toggleTag = (tagName) => {
  const index = selectedTags.value.indexOf(tagName)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  } else {
    selectedTags.value.push(tagName)
  }
  searchForm.tags = [...selectedTags.value]
  handleSearch()
}

const handleMenuSelect = (index) => {
  activeMenu.value = index
  switch (index) {
    case 'all':
      listQuery.onlyMine = false
      searchForm.category_id = null
      break
    case 'my':
      listQuery.onlyMine = true
      break
    case 'favorites':
      // TODO: 加载收藏文章
      break
    case 'recent':
      // TODO: 加载最近浏览
      break
    case 'pinned':
      // TODO: 加载置顶文章
      break
  }
  handleSearch()
}

const handleSelectionChange = (selection) => {
  selectedArticles.value = selection
}

const getRowClassName = ({ row }) => {
  if (row.is_pinned) return 'pinned-row'
  return ''
}

const handleArticleClick = (row) => {
  loadArticleDetail(row.id)
}

const loadArticleDetail = async (id) => {
  try {
    const response = await apiRequest(`/api/knowledge/articles/${id}`)
    currentArticle.value = response?.data || response || null
    articleDetailVisible.value = true
    loadRelatedArticles(id)
    loadComments(id)
  } catch (error) {
    console.error('加载文章详情失败:', error)
    ElMessage.error('加载文章详情失败')
  }
}

const loadRelatedArticles = async (id) => {
  try {
    const response = await apiRequest(`/api/knowledge/articles/${id}/related`)
    relatedArticles.value = response?.data?.items || response?.data || []
  } catch (error) {
    console.error('加载相关文章失败:', error)
  }
}

const loadComments = async (id) => {
  try {
    const response = await apiRequest(`/api/knowledge/articles/${id}/comments`)
    comments.value = response?.data?.comments || response?.data || []
  } catch (error) {
    console.error('加载评论失败:', error)
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  if (!currentArticle.value || !currentArticle.value.id) {
    ElMessage.error('文章信息不完整')
    return
  }
  try {
    await apiRequest(`/api/knowledge/articles/${currentArticle.value.id}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: newComment.value })
    })
    ElMessage.success('评论成功')
    newComment.value = ''
    loadComments(currentArticle.value.id)
  } catch (error) {
    console.error('发表评论失败:', error)
    ElMessage.error('发表评论失败')
  }
}

const handleArticleCommand = (cmd, row) => {
  switch (cmd) {
    case 'version':
      showVersionHistory(row)
      break
    case 'share':
      showShareManager(row)
      break
    case 'favorite':
      toggleFavorite(row)
      break
    case 'pin':
      togglePin(row)
      break
    case 'export':
      exportArticle(row, 'markdown')
      break
    case 'delete':
      handleDeleteArticle(row)
      break
  }
}

const showVersionHistory = (article) => {
  currentArticle.value = article
  versionHistoryVisible.value = true
}

const showShareManager = (article) => {
  currentArticle.value = article
  shareManagerVisible.value = true
}

const toggleFavorite = async (article) => {
  try {
    const method = article.is_favorited ? 'DELETE' : 'POST'
    await apiRequest(`/api/knowledge/articles/${article.id}/favorite`, { method })
    article.is_favorited = !article.is_favorited
    ElMessage.success(article.is_favorited ? '收藏成功' : '取消收藏')
  } catch (error) {
    console.error('收藏操作失败:', error)
  }
}

const togglePin = async (article) => {
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
    console.error('置顶操作失败:', error)
  }
}

const handleVersionRestore = () => {
  loadArticles()
  ElMessage.success('版本恢复成功')
}

const exportArticle = async (article, format) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/knowledge/articles/${article.id}/export/${format}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${article.title}.${format}`
    a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

const handleDeleteArticle = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这篇文章吗？', '提示', { type: 'warning' })
    await apiRequest(`/api/knowledge/articles/${row.id}`, { method: 'DELETE' })
    ElMessage.success('删除成功')
    loadArticles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchDelete = async () => {
  if (selectedArticles.value.length === 0) return
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedArticles.value.length} 篇文章吗？`, '提示', { type: 'warning' })
    for (const article of selectedArticles.value) {
      await apiRequest(`/api/knowledge/articles/${article.id}`, { method: 'DELETE' })
    }
    ElMessage.success('批量删除成功')
    selectedArticles.value = []
    loadArticles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
    }
  }
}

const handleBatchMove = () => {
  if (selectedArticles.value.length === 0) return
  targetCategoryId.value = null
  batchMoveVisible.value = true
}

const confirmBatchMove = async () => {
  if (!targetCategoryId.value) {
    ElMessage.warning('请选择目标分类')
    return
  }
  try {
    for (const article of selectedArticles.value) {
      await apiRequest(`/api/knowledge/articles/${article.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category_id: targetCategoryId.value })
      })
    }
    ElMessage.success('批量移动成功')
    batchMoveVisible.value = false
    selectedArticles.value = []
    loadArticles()
  } catch (error) {
    console.error('批量移动失败:', error)
    ElMessage.error('批量移动失败')
  }
}

// 分类管理
const openCategoryDialog = (category = null) => {
  if (category) {
    categoryForm.id = category.id
    categoryForm.name = category.name
    categoryForm.parent_id = category.parent_id
    categoryForm.description = category.description
    isEditingCategory.value = true
  } else {
    categoryForm.id = null
    categoryForm.name = ''
    categoryForm.parent_id = null
    categoryForm.description = ''
    isEditingCategory.value = false
  }
  categoryDialogVisible.value = true
}

const saveCategory = async () => {
  try {
    const method = categoryForm.id ? 'PUT' : 'POST'
    const url = categoryForm.id ? `/api/knowledge/categories/${categoryForm.id}` : '/api/knowledge/categories'
    await apiRequest(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(categoryForm)
    })
    ElMessage.success(isEditingCategory.value ? '更新成功' : '创建成功')
    categoryDialogVisible.value = false
    loadCategoryTree()
  } catch (error) {
    console.error('保存分类失败:', error)
    ElMessage.error('保存分类失败')
  }
}

const allowDrop = (draggingNode, dropNode, type) => {
  if (type === 'inner') {
    return true
  }
  return true
}

const allowDrag = (draggingNode) => {
  return true
}

const handleCategoryDrop = async (draggingNode, dropNode, dropType) => {
  try {
    await apiRequest(`/api/knowledge/categories/${draggingNode.data.id}/move`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        parent_id: dropType === 'inner' ? dropNode.data.id : dropNode.data.parent_id,
        sort_order: 0
      })
    })
    ElMessage.success('移动成功')
    loadCategoryTree()
  } catch (error) {
    console.error('移动分类失败:', error)
  }
}

// 文章编辑
const openArticleDialog = async (article = null) => {
  if (article) {
    // 编辑模式 - 获取完整文章详情
    try {
      const response = await apiRequest(`/api/knowledge/articles/${article.id}`)
      const fullArticle = response?.data || response
      currentArticle.value = fullArticle
      articleForm.id = fullArticle.id
      articleForm.title = fullArticle.title
      articleForm.summary = fullArticle.summary || ''
      articleForm.content = fullArticle.content
      articleForm.category_id = fullArticle.category_id
      articleForm.tags = Array.isArray(fullArticle.tags) ? fullArticle.tags : []
      articleForm.is_public = fullArticle.is_public !== false
      articleForm.allow_comment = fullArticle.allow_comment !== false
      articleForm.is_pinned = fullArticle.is_pinned || false
      articleAttachments.value = Array.isArray(fullArticle.attachments) ? [...fullArticle.attachments] : []
      isEditing.value = true
    } catch (error) {
      console.error('获取文章详情失败:', error)
      ElMessage.error('获取文章详情失败')
      return
    }
  } else {
    // 新建模式
    currentArticle.value = null
    articleForm.id = null
    articleForm.title = ''
    articleForm.summary = ''
    articleForm.content = ''
    articleForm.category_id = null
    articleForm.tags = []
    articleForm.is_public = true
    articleForm.allow_comment = true
    articleForm.is_pinned = false
    articleAttachments.value = []
    isEditing.value = false
  }
  await nextTick()
  articleDialogVisible.value = true
}

const saveArticle = async () => {
  try {
    const method = articleForm.id ? 'PUT' : 'POST'
    const url = articleForm.id ? `/api/knowledge/articles/${articleForm.id}` : '/api/knowledge/articles'
    const body = {
      title: articleForm.title,
      content: articleForm.content,
      summary: articleForm.summary,
      category_id: articleForm.category_id,
      tags: articleForm.tags,
      is_public: articleForm.is_public,
      allow_comment: articleForm.allow_comment,
      is_pinned: articleForm.is_pinned,
      status: 'published'
    }
    await apiRequest(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    ElMessage.success(isEditing.value ? '更新成功' : '发布成功')
    articleDialogVisible.value = false
    loadArticles()
  } catch (error) {
    console.error('保存文章失败:', error)
    ElMessage.error('保存文章失败')
  }
}

const saveDraft = async () => {
  try {
    const method = articleForm.id ? 'PUT' : 'POST'
    const url = articleForm.id ? `/api/knowledge/articles/${articleForm.id}` : '/api/knowledge/articles'
    const body = {
      title: articleForm.title,
      content: articleForm.content,
      summary: articleForm.summary,
      category_id: articleForm.category_id,
      tags: articleForm.tags,
      is_public: articleForm.is_public,
      allow_comment: articleForm.allow_comment,
      is_pinned: articleForm.is_pinned,
      status: 'draft'
    }
    await apiRequest(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    ElMessage.success('草稿保存成功')
    articleDialogVisible.value = false
    loadArticles()
  } catch (error) {
    console.error('保存草稿失败:', error)
    ElMessage.error('保存草稿失败')
  }
}

const handleUploadSuccess = (response) => {
  articleAttachments.value.push(response)
}

const downloadAttachment = (att) => {
  window.open(`${API_BASE_URL}/api/knowledge/attachments/${att.id}/download`)
}

// 处理 ArticleForm 保存事件
const handleArticleSave = async (formData) => {
  try {
    const method = isEditing.value ? 'PUT' : 'POST'
    const url = isEditing.value
      ? `/api/knowledge/articles/${articleForm.id}`
      : '/api/knowledge/articles'

    const body = {
      title: formData.title,
      content: formData.content,
      summary: formData.summary,
      category_id: formData.category_id,
      tags: formData.tags,
      is_public: formData.is_public,
      allow_comment: formData.allow_comment,
      is_pinned: formData.is_pinned,
      status: formData.status,
      author_id: formData.author_id
    }

    await apiRequest(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    
    ElMessage.success(formData.status === 'draft' ? '草稿保存成功' : (isEditing.value ? '更新成功' : '发布成功'))
    articleDialogVisible.value = false
    loadArticles()
  } catch (error) {
    console.error('保存文章失败:', error)
    ElMessage.error('保存文章失败')
  }
}

// 工具函数
const renderMarkdown = (content) => {
  if (!content) return ''
  return marked(content, { sanitize: true })
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

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

// ============ 生命周期 ============
onMounted(() => {
  isMounted.value = true
  loadCategoryTree()
  loadTags()
  loadArticles()
})

onUnmounted(() => {
  isMounted.value = false
  categoryTreeRef.value = null
  articleTableRef.value = null
})
</script>

<style scoped>
.knowledge-container {
  padding: 20px;
  min-height: calc(100vh - 60px);
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  font-size: 24px;
  margin: 0 0 8px 0;
}

.header-content p {
  color: #909399;
  margin: 0;
}

.search-card {
  margin-bottom: 20px;
  position: relative;
}

.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  margin-top: 5px;
  z-index: 100;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.suggestion-item {
  padding: 10px 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.suggestion-item:hover {
  background: #f5f7fa;
}

.knowledge-layout {
  display: flex;
  gap: 20px;
}

.knowledge-sidebar {
  width: 280px;
  flex-shrink: 0;
}

.sidebar-card {
  margin-bottom: 16px;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-node {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
}

.category-name {
  flex: 1;
}

.category-count {
  color: #909399;
  font-size: 12px;
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  cursor: pointer;
}

.knowledge-main {
  flex: 1;
  min-width: 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 10px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.article-list {
  min-height: 400px;
}

.article-title-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.article-title {
  font-weight: 500;
}

.article-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.article-summary {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.article-stats {
  display: flex;
  justify-content: center;
  gap: 12px;
  color: #909399;
  font-size: 13px;
}

.article-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.text-gray {
  color: #909399;
  font-size: 12px;
}

/* 卡片视图 */
.article-cards {
  min-height: 400px;
}

.article-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.article-card.is-pinned {
  border: 1px solid #f56c6c;
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
  font-weight: 500;
  font-size: 16px;
  flex: 1;
}

.card-badges {
  display: flex;
  gap: 4px;
}

.card-summary {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 12px;
  min-height: 44px;
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
  color: #909399;
  font-size: 13px;
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
  color: #909399;
  font-size: 13px;
  margin-bottom: 12px;
}

.card-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* 文章详情 */
.article-detail {
  padding: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.detail-meta {
  display: flex;
  gap: 20px;
  color: #909399;
  font-size: 14px;
}

.detail-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.detail-content {
  line-height: 1.8;
  font-size: 15px;
}

.detail-content :deep(h1),
.detail-content :deep(h2),
.detail-content :deep(h3) {
  margin-top: 24px;
  margin-bottom: 16px;
}

.detail-content :deep(p) {
  margin-bottom: 16px;
}

.detail-content :deep(code) {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
}

.detail-content :deep(pre) {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
}

.detail-attachments {
  margin-top: 20px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 8px;
}

.detail-related {
  margin-top: 20px;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.related-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  cursor: pointer;
  border-radius: 4px;
}

.related-item:hover {
  background: #f5f7fa;
}

/* 评论 */
.detail-comments {
  margin-top: 20px;
}

.comment-input {
  margin-bottom: 20px;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.comment-author {
  font-weight: 500;
}

.comment-time {
  color: #909399;
  font-size: 12px;
}

.comment-content {
  color: #606266;
}

/* 表格样式 */
:deep(.pinned-row) {
  background: #fff5f5;
}

/* 响应式 */
@media screen and (max-width: 1200px) {
  .knowledge-layout {
    flex-direction: column;
  }
  
  .knowledge-sidebar {
    width: 100%;
  }
  
  .toolbar {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media screen and (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .detail-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .detail-meta {
    flex-wrap: wrap;
  }
}

/* 工具类 */
.mb-2 {
  margin-bottom: 8px;
}

.mt-2 {
  margin-top: 8px;
}

.mt-4 {
  margin-top: 16px;
}

.text-danger {
  color: #f56c6c;
}
</style>
