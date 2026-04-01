<template>
  <div class="knowledge-enhanced-page">
    <el-page-header title="知识库" content="增强版知识管理" @back="goBack" />
    
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item>
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索知识库..."
            clearable
            style="width: 300px"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-select v-model="searchForm.category_id" placeholder="分类" clearable>
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-select v-model="searchForm.tags" placeholder="标签" multiple collapse-tags>
            <el-option
              v-for="tag in tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.name"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-select v-model="searchForm.sort_by" placeholder="排序">
            <el-option label="最近更新" value="updated_at" />
            <el-option label="创建时间" value="created_at" />
            <el-option label="浏览量" value="views" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 搜索建议 -->
      <div v-if="searchSuggestions.length > 0" class="search-suggestions">
        <div class="suggestion-title">搜索建议</div>
        <div
          v-for="item in searchSuggestions"
          :key="item.id || item.name"
          class="suggestion-item"
          @click="applySuggestion(item)"
        >
          <el-icon v-if="item.type === 'article'"><Document /></el-icon>
          <el-icon v-else><CollectionTag /></el-icon>
          <span>{{ item.title || item.name }}</span>
          <span v-if="item.type === 'tag'" class="tag-count">({{ item.article_count }}篇)</span>
        </div>
      </div>
    </el-card>
    
    <!-- 主内容区 -->
    <el-row :gutter="20" class="main-content">
      <!-- 左侧分类 -->
      <el-col :span="5">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>分类</span>
              <el-button size="small" @click="showCategoryDialog = true">
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </template>
          
          <el-tree
            :data="categoryTree"
            :props="{ label: 'name', children: 'children' }"
            @node-click="handleCategoryClick"
            highlight-current
          />
        </el-card>
        
        <!-- 标签云 -->
        <el-card class="mt-4">
          <template #header>
            <span>热门标签</span>
          </template>
          <div class="tag-cloud">
            <el-tag
              v-for="tag in hotTags"
              :key="tag.id"
              :style="{ fontSize: tag.size + 'px' }"
              class="tag-item"
              @click="searchByTag(tag.name)"
            >
              {{ tag.name }}
            </el-tag>
          </div>
        </el-card>
      </el-col>
      
      <!-- 中间文章列表 -->
      <el-col :span="14">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>文章列表</span>
              <el-button type="primary" @click="createArticle">
                <el-icon><Plus /></el-icon> 新建文章
              </el-button>
            </div>
          </template>
          
          <div v-if="articles.length === 0" class="empty-state">
            <el-empty description="暂无文章" />
          </div>
          
          <div v-else class="article-list">
            <div
              v-for="article in articles"
              :key="article.id"
              class="article-item"
              @click="viewArticle(article)"
            >
              <div class="article-header">
                <h3 class="article-title">{{ article.title }}</h3>
                <el-tag v-if="article.is_pinned" type="danger" size="small">置顶</el-tag>
              </div>
              
              <p class="article-preview">{{ article.content_preview }}</p>
              
              <div class="article-meta">
                <span><el-icon><User /></el-icon> {{ article.author }}</span>
                <span><el-icon><Folder /></el-icon> {{ article.category }}</span>
                <span><el-icon><View /></el-icon> {{ article.view_count }}</span>
                <span><el-icon><Timer /></el-icon> {{ formatDate(article.updated_at) }}</span>
              </div>
              
              <div class="article-tags">
                <el-tag
                  v-for="tag in article.tags"
                  :key="tag"
                  size="small"
                  effect="plain"
                >
                  {{ tag }}
                </el-tag>
              </div>
            </div>
          </div>
          
          <!-- 分页 -->
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.per_page"
            :total="pagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
            class="mt-4"
          />
        </el-card>
      </el-col>
      
      <!-- 右侧统计 -->
      <el-col :span="5">
        <el-card>
          <template #header>
            <span>统计</span>
          </template>
          <div class="statistics">
            <div class="stat-item">
              <div class="stat-value">{{ stats.total_articles }}</div>
              <div class="stat-label">总文章</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.total_views }}</div>
              <div class="stat-label">总浏览</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.total_categories }}</div>
              <div class="stat-label">分类数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.total_tags }}</div>
              <div class="stat-label">标签数</div>
            </div>
          </div>
        </el-card>
        
        <!-- 最近更新 -->
        <el-card class="mt-4">
          <template #header>
            <span>最近更新</span>
          </template>
          <div class="recent-list">
            <div
              v-for="item in recentArticles"
              :key="item.id"
              class="recent-item"
              @click="viewArticle(item)"
            >
              <div class="recent-title">{{ item.title }}</div>
              <div class="recent-time">{{ formatDate(item.updated_at) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 新建/编辑文章对话框 -->
    <el-dialog
      v-model="articleDialog.visible"
      :title="articleDialog.isEdit ? '编辑文章' : '新建文章'"
      width="90%"
      top="5vh"
      :close-on-click-modal="false"
    >
      <el-form :model="articleForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="articleForm.title" placeholder="文章标题" />
        </el-form-item>
        
        <el-form-item label="分类">
          <el-cascader
            v-model="articleForm.category_id"
            :options="categoryTree"
            :props="{ value: 'id', label: 'name', children: 'children' }"
            placeholder="选择分类"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="标签">
          <el-select
            v-model="articleForm.tags"
            multiple
            filterable
            allow-create
            placeholder="输入标签"
          >
            <el-option
              v-for="tag in tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.name"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="内容">
          <BlockEditor v-model="articleForm.content" ref="blockEditor" />
        </el-form-item>
        
        <el-form-item label="选项">
          <el-checkbox v-model="articleForm.is_pinned">置顶</el-checkbox>
          <el-checkbox v-model="articleForm.is_public">公开</el-checkbox>
          <el-checkbox v-model="articleForm.allow_comment">允许评论</el-checkbox>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="articleDialog.visible = false">取消</el-button>
        <el-button @click="previewArticle">预览</el-button>
        <el-button type="primary" @click="saveArticle">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 文章详情对话框 -->
    <el-dialog
      v-model="detailDialog.visible"
      :title="currentArticle.title"
      width="80%"
      top="5vh"
    >
      <div class="article-detail">
        <div class="article-toolbar">
          <el-button-group>
            <el-button v-if="canEditArticle" size="small" @click="editCurrentArticle">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button size="small" @click="showShareDialog = true">
              <el-icon><Share /></el-icon> 分享
            </el-button>
            <el-button size="small" @click="showVersionDialog = true">
              <el-icon><Clock /></el-icon> 历史版本
            </el-button>
            <el-button size="small" @click="exportArticle('pdf')">
              <el-icon><Download /></el-icon> 导出PDF
            </el-button>
            <el-button size="small" @click="exportArticle('markdown')">
              <el-icon><Document /></el-icon> 导出MD
            </el-button>
          </el-button-group>
          
          <el-button
            size="small"
            :type="currentArticle.is_favorite ? 'warning' : 'default'"
            @click="toggleFavorite"
          >
            <el-icon><Star /></el-icon>
            {{ currentArticle.is_favorite ? '已收藏' : '收藏' }}
          </el-button>
        </div>
        
        <div class="article-info">
          <span>作者: {{ currentArticle.author }}</span>
          <span>分类: {{ currentArticle.category }}</span>
          <span>更新: {{ formatDate(currentArticle.updated_at) }}</span>
          <span>版本: v{{ currentArticle.version }}</span>
        </div>
        
        <div class="article-tags">
          <el-tag
            v-for="tag in currentArticle.tags"
            :key="tag"
            size="small"
            @click="searchByTag(tag)"
          >
            {{ tag }}
          </el-tag>
        </div>
        
        <el-divider />
        
        <div class="article-content" v-html="renderedContent"></div>
        
        <!-- 相关文章 -->
        <el-divider content-position="left">相关文章</el-divider>
        <div class="related-articles">
          <div
            v-for="article in relatedArticles"
            :key="article.id"
            class="related-item"
            @click="viewArticle(article)"
          >
            <el-icon><Document /></el-icon>
            <span>{{ article.title }}</span>
            <el-tag size="small" type="info">{{ article.match_reason }}</el-tag>
          </div>
        </div>
        
        <!-- 双向链接 -->
        <el-divider content-position="left">知识链接</el-divider>
        <div class="knowledge-links">
          <div v-if="knowledgeLinks.outgoing.length > 0">
            <div class="link-title">引用</div>
            <div
              v-for="link in knowledgeLinks.outgoing"
              :key="link.id"
              class="link-item"
              @click="viewArticleById(link.to_article_id)"
            >
              <el-icon><Link /></el-icon>
              <span>{{ link.to_article_title }}</span>
              <span v-if="link.context" class="link-context">{{ link.context }}</span>
            </div>
          </div>
          <div v-if="knowledgeLinks.incoming.length > 0" class="mt-2">
            <div class="link-title">被引用</div>
            <div
              v-for="link in knowledgeLinks.incoming"
              :key="link.id"
              class="link-item"
              @click="viewArticleById(link.from_article_id)"
            >
              <el-icon><Link /></el-icon>
              <span>{{ link.from_article_title }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import BlockEditor from '@/components/BlockEditor.vue'
import { marked } from 'marked'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category_id: null,
  tags: [],
  sort_by: 'updated_at'
})

const searchSuggestions = ref([])

// 数据
const categories = ref([])
const categoryTree = ref([])
const tags = ref([])
const hotTags = ref([])
const articles = ref([])
const recentArticles = ref([])
const relatedArticles = ref([])
const knowledgeLinks = ref({ outgoing: [], incoming: [] })

const stats = reactive({
  total_articles: 0,
  total_views: 0,
  total_categories: 0,
  total_tags: 0
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0,
  pages: 0
})

// 对话框
const articleDialog = reactive({
  visible: false,
  isEdit: false
})

const detailDialog = reactive({
  visible: false
})

const showCategoryDialog = ref(false)
const showShareDialog = ref(false)
const showVersionDialog = ref(false)

// 表单
const articleForm = reactive({
  id: null,
  title: '',
  category_id: null,
  tags: [],
  content: '',
  is_pinned: false,
  is_public: true,
  allow_comment: true,
  author_id: null
})

const currentArticle = ref({})
const blockEditor = ref(null)

const userStore = useUserStore()

const isAdmin = computed(() => {
  const user = userStore.currentUser
  if (!user) return false
  if (user.is_super_admin) return true
  return user.position === '管理员' || user.position?.includes('经理')
})

const canEditArticle = computed(() => {
  if (isAdmin.value) return true
  return userStore.currentUser?.id === currentArticle.value.author_id
})

// 渲染 Markdown
const renderedContent = computed(() => {
  if (!currentArticle.value.content) return ''
  return marked(currentArticle.value.content)
})

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleDateString('zh-CN')
}

// 搜索建议
watch(() => searchForm.keyword, async (val) => {
  if (val && val.length >= 2) {
    // 调用搜索建议 API
    // const res = await fetch(`/api/knowledge/enhanced/search/suggestions?q=${val}`)
    // searchSuggestions.value = await res.json()
  } else {
    searchSuggestions.value = []
  }
})

// 搜索
const handleSearch = async () => {
  // 调用高级搜索 API
  const res = await fetch('/api/knowledge/enhanced/search/advanced', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...searchForm,
      page: pagination.page,
      per_page: pagination.per_page
    })
  })
  const data = await res.json()
  articles.value = data.items
  pagination.total = data.total
  pagination.pages = data.pages
}

const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.category_id = null
  searchForm.tags = []
  searchForm.sort_by = 'updated_at'
  handleSearch()
}

// 分类点击
const handleCategoryClick = (data) => {
  searchForm.category_id = data.id
  handleSearch()
}

// 标签搜索
const searchByTag = (tagName) => {
  searchForm.tags = [tagName]
  handleSearch()
}

// 分页
const handleSizeChange = (size) => {
  pagination.per_page = size
  handleSearch()
}

const handlePageChange = (page) => {
  pagination.page = page
  handleSearch()
}

// 文章操作
const createArticle = () => {
  articleDialog.isEdit = false
  articleDialog.visible = true
  articleForm.id = null
  articleForm.title = ''
  articleForm.category_id = null
  articleForm.tags = []
  articleForm.content = ''
  articleForm.is_pinned = false
  articleForm.is_public = true
  articleForm.allow_comment = true
}

const editCurrentArticle = () => {
  detailDialog.visible = false
  articleDialog.isEdit = true
  articleDialog.visible = true
  Object.assign(articleForm, currentArticle.value)
}

const saveArticle = async () => {
  // 获取编辑器内容
  if (blockEditor.value) {
    articleForm.content = blockEditor.value.exportMarkdown()
  }
  
  const url = articleForm.id 
    ? `/api/knowledge/articles/${articleForm.id}`
    : '/api/knowledge/articles'
  
  const res = await fetch(url, {
    method: articleForm.id ? 'PUT' : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(articleForm)
  })
  
  if (res.ok) {
    ElMessage.success('保存成功')
    articleDialog.visible = false
    handleSearch()
  } else {
    ElMessage.error('保存失败')
  }
}

const viewArticle = (article) => {
  currentArticle.value = article
  detailDialog.visible = true
  // 加载相关文章和链接
  loadRelatedArticles(article.id)
  loadKnowledgeLinks(article.id)
}

const viewArticleById = (id) => {
  // 根据 ID 加载文章详情
}

const loadRelatedArticles = async (articleId) => {
  const res = await fetch(`/api/knowledge/enhanced/articles/${articleId}/related`)
  relatedArticles.value = await res.json()
}

const loadKnowledgeLinks = async (articleId) => {
  const res = await fetch(`/api/knowledge/enhanced/articles/${articleId}/links`)
  knowledgeLinks.value = await res.json()
}

// 导出
const exportArticle = async (format) => {
  const res = await fetch(`/api/knowledge/enhanced/articles/${currentArticle.value.id}/export/${format}`)
  if (res.ok) {
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${currentArticle.value.title}.${format === 'markdown' ? 'md' : 'pdf'}`
    a.click()
    window.URL.revokeObjectURL(url)
  }
}

// 收藏
const toggleFavorite = async () => {
  // 调用收藏 API
}

// 返回
const goBack = () => {
  router.back()
}

// 初始化
onMounted(() => {
  handleSearch()
  // 加载分类、标签、统计等
})
</script>

<style scoped>
.knowledge-enhanced-page {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.search-suggestions {
  margin-top: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.suggestion-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  cursor: pointer;
  border-radius: 4px;
}

.suggestion-item:hover {
  background: #ecf5ff;
}

.tag-count {
  color: #909399;
  font-size: 12px;
}

.main-content {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  cursor: pointer;
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.article-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.article-item:hover {
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.article-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.article-title {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.article-preview {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin: 8px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  display: flex;
  gap: 16px;
  color: #909399;
  font-size: 13px;
  margin: 8px 0;
}

.article-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.article-tags {
  display: flex;
  gap: 6px;
  margin-top: 8px;
}

.statistics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-item {
  padding: 8px;
  cursor: pointer;
  border-radius: 4px;
}

.recent-item:hover {
  background: #f5f7fa;
}

.recent-title {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
}

.recent-time {
  font-size: 12px;
  color: #909399;
}

.article-detail {
  padding: 20px;
}

.article-toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.article-info {
  display: flex;
  gap: 16px;
  color: #909399;
  font-size: 13px;
  margin-bottom: 12px;
}

.article-content {
  line-height: 1.8;
  color: #303133;
}

.article-content :deep(h1),
.article-content :deep(h2),
.article-content :deep(h3) {
  margin-top: 24px;
  margin-bottom: 16px;
}

.article-content :deep(p) {
  margin-bottom: 16px;
}

.article-content :deep(pre) {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
}

.article-content :deep(code) {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
}

.article-content :deep(blockquote) {
  border-left: 4px solid #409eff;
  margin: 0;
  padding-left: 16px;
  color: #606266;
}

.related-articles {
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

.knowledge-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.link-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.link-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  cursor: pointer;
  border-radius: 4px;
}

.link-item:hover {
  background: #ecf5ff;
}

.link-context {
  color: #909399;
  font-size: 12px;
}

@media screen and (max-width: 768px) {
  .knowledge-enhanced-page {
    padding: 12px;
  }

  .search-card {
    margin-bottom: 12px;
  }

  .search-card .el-form {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .search-card .el-form-item {
    margin-bottom: 8px;
    width: 100%;
  }

  .search-card .el-input,
  .search-card .el-select {
    width: 100% !important;
  }

  .search-suggestions {
    margin-top: 8px;
    padding: 8px;
  }

  .suggestion-item {
    padding: 8px;
    font-size: 13px;
  }

  .main-content {
    margin-top: 12px;
  }

  .main-content .el-col {
    width: 100% !important;
    max-width: 100% !important;
    flex: 0 0 100% !important;
    margin-bottom: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .tag-cloud {
    gap: 6px;
  }

  .tag-item {
    font-size: 12px !important;
  }

  .article-list {
    gap: 12px;
  }

  .article-item {
    padding: 12px;
  }

  .article-title {
    font-size: 15px;
  }

  .article-preview {
    font-size: 13px;
    -webkit-line-clamp: 3;
  }

  .article-meta {
    flex-wrap: wrap;
    gap: 8px;
    font-size: 12px;
  }

  .article-tags {
    flex-wrap: wrap;
    gap: 4px;
  }

  .statistics {
    gap: 8px;
  }

  .stat-item {
    padding: 8px;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-label {
    font-size: 11px;
  }

  .recent-list {
    gap: 8px;
  }

  .recent-title {
    font-size: 13px;
  }

  .recent-time {
    font-size: 11px;
  }

  .article-detail {
    padding: 12px;
  }

  .article-toolbar {
    flex-direction: column;
    gap: 8px;
  }

  .article-toolbar .el-button-group {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }

  .article-toolbar .el-button-group .el-button {
    flex: 1;
    min-width: calc(50% - 2px);
    font-size: 12px;
    padding: 6px 8px;
  }

  .article-info {
    flex-wrap: wrap;
    gap: 8px;
    font-size: 12px;
  }

  .article-content {
    font-size: 14px;
    line-height: 1.6;
  }

  .article-content :deep(h1) {
    font-size: 20px;
  }

  .article-content :deep(h2) {
    font-size: 18px;
  }

  .article-content :deep(h3) {
    font-size: 16px;
  }

  .article-content :deep(pre) {
    padding: 12px;
    font-size: 12px;
  }

  .article-content :deep(code) {
    font-size: 12px;
  }

  .related-articles {
    gap: 6px;
  }

  .related-item {
    padding: 6px;
    font-size: 13px;
  }

  .knowledge-links {
    gap: 6px;
  }

  .link-item {
    padding: 6px;
    font-size: 13px;
  }
}

@media screen and (max-width: 480px) {
  .knowledge-enhanced-page {
    padding: 8px;
  }

  .article-title {
    font-size: 14px;
  }

  .article-preview {
    font-size: 12px;
  }

  .article-meta {
    font-size: 11px;
  }

  .stat-value {
    font-size: 18px;
  }

  .article-toolbar .el-button-group .el-button {
    min-width: 100%;
    font-size: 11px;
  }
}
</style>
