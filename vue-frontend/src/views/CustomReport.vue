<template>
  <div class="custom-report-container">
    <!-- 页面头部 - 玻璃拟态风格 -->
    <div class="page-header animate-fade-in-down">
      <div class="header-bg-decoration">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="header-content">
        <div class="header-title">
          <div class="title-icon-wrapper">
            <el-icon class="title-icon"><DataLine /></el-icon>
          </div>
          <div class="title-text">
            <h1>自定义报表生成器</h1>
            <p class="subtitle">灵活配置报表维度，一键生成数据洞察</p>
          </div>
        </div>
        <el-button class="btn-gradient btn-save" @click="saveTemplate" :disabled="!isFormValid">
          <el-icon><DocumentChecked /></el-icon>
          保存模板
        </el-button>
      </div>
    </div>

    <!-- 报表配置区域 -->
    <div class="report-config animate-fade-in-up delay-100">
      <el-card class="config-card glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Setting /></el-icon>
              报表配置
            </span>
          </div>
        </template>
        
        <el-form :model="reportConfig" label-width="120px" class="config-form">
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="报表名称">
                <el-input 
                  v-model="reportConfig.name" 
                  placeholder="请输入报表名称" 
                  class="custom-input"
                  clearable
                />
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="时间范围">
                <el-date-picker
                  v-model="reportConfig.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  value-format="YYYY-MM-DD"
                  class="custom-date-picker"
                />
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="项目筛选">
                <el-select 
                  v-model="reportConfig.projectIds" 
                  multiple 
                  placeholder="选择项目"
                  class="custom-select"
                  collapse-tags
                  collapse-tags-tooltip
                >
                  <el-option
                    v-for="project in projects"
                    :key="project.id"
                    :label="project.name"
                    :value="project.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item label="Bug状态">
                <el-select 
                  v-model="reportConfig.statuses" 
                  multiple 
                  placeholder="选择Bug状态"
                  class="custom-select"
                  collapse-tags
                  collapse-tags-tooltip
                >
                  <el-option label="新建" value="new" />
                  <el-option label="进行中" value="in_progress" />
                  <el-option label="已解决" value="resolved" />
                  <el-option label="已关闭" value="closed" />
                  <el-option label="重新打开" value="reopened" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>
    </div>

    <!-- 图表配置区域 -->
    <div class="chart-config animate-fade-in-up delay-200">
      <el-card class="config-card glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><PieChart /></el-icon>
              图表配置
            </span>
            <el-button class="btn-gradient btn-add" size="small" @click="addChart">
              <el-icon><Plus /></el-icon>
              添加图表
            </el-button>
          </div>
        </template>
        
        <div v-for="(chart, index) in reportConfig.charts" :key="index" class="chart-item">
          <el-row :gutter="20" align="middle">
            <el-col :xs="24" :sm="8" :md="6">
              <el-form-item label="图表类型" label-width="80px">
                <el-select v-model="chart.type" placeholder="选择图表类型" class="custom-select">
                  <el-option label="趋势图" value="line">
                    <el-icon><TrendCharts /></el-icon> 趋势图
                  </el-option>
                  <el-option label="柱状图" value="bar">
                    <el-icon><Histogram /></el-icon> 柱状图
                  </el-option>
                  <el-option label="饼图" value="pie">
                    <el-icon><PieChart /></el-icon> 饼图
                  </el-option>
                  <el-option label="雷达图" value="radar">
                    <el-icon><HelpFilled /></el-icon> 雷达图
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="8" :md="6">
              <el-form-item label="图表标题" label-width="80px">
                <el-input v-model="chart.title" placeholder="请输入图表标题" class="custom-input" />
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="8" :md="6">
              <el-form-item label="数据维度" label-width="80px">
                <el-select v-model="chart.dimension" placeholder="选择数据维度" class="custom-select">
                  <el-option label="Bug状态分布" value="status" />
                  <el-option label="优先级分布" value="priority" />
                  <el-option label="严重程度分布" value="severity" />
                  <el-option label="趋势分析" value="trend" />
                  <el-option label="根因分析" value="root_cause" />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="24" :md="6" class="chart-actions">
              <el-button class="btn-delete" size="small" @click="removeChart(index)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </el-col>
          </el-row>
          <el-divider v-if="index < reportConfig.charts.length - 1" class="chart-divider" />
        </div>
      </el-card>
    </div>

    <!-- 预览区域 -->
    <div class="preview-area animate-fade-in-up delay-300">
      <el-card class="preview-card glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><View /></el-icon>
              报表预览
            </span>
            <div class="header-actions">
              <el-button class="btn-gradient btn-generate" @click="generateReport" :disabled="!isFormValid">
                <el-icon><VideoPlay /></el-icon>
                生成报表
              </el-button>
              <el-button class="btn-export" @click="exportReport" :disabled="!reportData">
                <el-icon><Download /></el-icon>
                导出报表
              </el-button>
            </div>
          </div>
        </template>
        
        <div v-if="reportData" class="report-preview">
          <div v-for="(chartData, index) in reportData.charts" :key="index" class="chart-preview">
            <div ref="chartRef" :style="{ width: '100%', height: '400px' }"></div>
          </div>
        </div>
        
        <div v-else class="empty-preview">
          <div class="empty-icon">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <p class="empty-text">请配置报表参数并点击"生成报表"查看预览</p>
          <p class="empty-hint">支持趋势图、柱状图、饼图、雷达图等多种图表类型</p>
        </div>
      </el-card>
    </div>

    <!-- 模板管理 -->
    <div class="template-management animate-fade-in-up delay-400">
      <el-card class="template-card glass-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><FolderOpened /></el-icon>
              报表模板管理
            </span>
          </div>
        </template>
        
        <el-table :data="templates" style="width: 100%" class="custom-table" stripe>
          <el-table-column prop="name" label="模板名称" min-width="200">
            <template #default="{ row }">
              <div class="template-name">
                <el-icon><Document /></el-icon>
                <span>{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="创建时间" width="180" align="center">
            <template #default="{ row }">
              <span class="time-text">{{ row.createdAt }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" align="center" fixed="right">
            <template #default="scope">
              <el-button class="btn-load" size="small" @click="loadTemplate(scope.row)">
                <el-icon><Upload /></el-icon>
                加载
              </el-button>
              <el-button class="btn-delete-template" size="small" @click="deleteTemplate(scope.row.id)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import bugStatisticsService from '@/services/bugStatisticsService'
import { apiService } from '@/services/api.js'
import { useUserStore } from '@/stores/user'
import { 
  DataLine, 
  DocumentChecked, 
  Setting, 
  PieChart, 
  Plus, 
  TrendCharts, 
  Histogram, 
  HelpFilled, 
  Delete, 
  View, 
  VideoPlay, 
  Download, 
  DataAnalysis, 
  FolderOpened, 
  Document, 
  Upload 
} from '@element-plus/icons-vue'

export default {
  name: 'CustomReport',
  components: {
    DataLine,
    DocumentChecked,
    Setting,
    PieChart,
    Plus,
    TrendCharts,
    Histogram,
    HelpFilled,
    Delete,
    View,
    VideoPlay,
    Download,
    DataAnalysis,
    FolderOpened,
    Document,
    Upload
  },
  setup() {
    const userStore = useUserStore()
    const projects = ref([])
    const templates = ref([])
    const chartRef = ref([])
    const chartInstances = ref([])
    
    const reportConfig = reactive({
      name: '',
      dateRange: [],
      projectIds: [],
      statuses: [],
      charts: [
        { type: 'line', title: '', dimension: 'trend' }
      ]
    })
    
    const reportData = ref(null)
    
    const isFormValid = computed(() => {
      return reportConfig.name.trim() && 
             reportConfig.dateRange && 
             reportConfig.dateRange.length === 2 &&
             reportConfig.charts.length > 0
    })
    
    // 检查认证状态
    const checkAuth = () => {
      if (!userStore.isAuthenticated) {
        ElMessage.error('请先登录')
        return false
      }
      return true
    }
    
    // 加载项目列表
    const loadProjects = async () => {
      if (!checkAuth()) return
      
      try {
        const response = await apiService.projects.getList()
        projects.value = response.data || []
      } catch (error) {
        console.error('加载项目列表失败:', error)
        ElMessage.error('加载项目列表失败')
      }
    }
    
    // 添加图表
    const addChart = () => {
      reportConfig.charts.push({
        type: 'line',
        title: '',
        dimension: 'trend'
      })
    }
    
    // 删除图表
    const removeChart = (index) => {
      if (reportConfig.charts.length > 1) {
        reportConfig.charts.splice(index, 1)
      } else {
        ElMessage.warning('至少需要保留一个图表')
      }
    }
    
    // 生成报表
    const generateReport = async () => {
      if (!checkAuth()) return
      
      try {
        const params = {
          name: reportConfig.name,
          start_date: reportConfig.dateRange[0],
          end_date: reportConfig.dateRange[1],
          project_ids: reportConfig.projectIds,
          statuses: reportConfig.statuses,
          charts: reportConfig.charts
        }
        
        const response = await bugStatisticsService.generateCustomReport(params)
        reportData.value = response.data
        
        await nextTick()
        renderCharts()
        
        ElMessage.success('报表生成成功')
      } catch (error) {
        console.error('生成报表失败:', error)
        ElMessage.error('生成报表失败')
      }
    }
    
    // 渲染图表
    const renderCharts = () => {
      if (!reportData.value || !reportData.value.charts) return
      
      // 清理之前的图表实例
      chartInstances.value.forEach(instance => {
        instance.dispose()
      })
      chartInstances.value = []
      
      // 渲染新图表
      reportData.value.charts.forEach((chartData, index) => {
        if (chartRef.value[index]) {
          const chart = echarts.init(chartRef.value[index])
          chart.setOption(chartData.option)
          chartInstances.value.push(chart)
        }
      })
    }
    
    // 导出报表
    const exportReport = async () => {
      if (!checkAuth()) return
      
      try {
        const params = {
          name: reportConfig.name,
          start_date: reportConfig.dateRange[0],
          end_date: reportConfig.dateRange[1],
          project_ids: reportConfig.projectIds,
          statuses: reportConfig.statuses,
          charts: reportConfig.charts
        }
        
        await bugStatisticsService.exportCustomReport(params)
        ElMessage.success('报表导出成功')
      } catch (error) {
        console.error('导出报表失败:', error)
        ElMessage.error('导出报表失败')
      }
    }
    
    // 保存模板
    const saveTemplate = async () => {
      if (!checkAuth()) return
      
      try {
        const template = {
          name: reportConfig.name,
          config: { ...reportConfig }
        }
        
        await bugStatisticsService.saveReportTemplate(template)
        ElMessage.success('模板保存成功')
        loadTemplates()
      } catch (error) {
        console.error('保存模板失败:', error)
        ElMessage.error('保存模板失败')
      }
    }
    
    // 加载模板
    const loadTemplates = async () => {
      if (!checkAuth()) return
      
      try {
        const response = await bugStatisticsService.getReportTemplates()
        templates.value = response.data || []
      } catch (error) {
        console.error('加载模板失败:', error)
      }
    }
    
    // 加载模板配置
    const loadTemplate = (template) => {
      Object.assign(reportConfig, template.config)
      ElMessage.success('模板加载成功')
    }
    
    // 删除模板
    const deleteTemplate = async (templateId) => {
      if (!checkAuth()) return
      
      try {
        await ElMessageBox.confirm('确定删除此模板吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await bugStatisticsService.deleteReportTemplate(templateId)
        ElMessage.success('模板删除成功')
        loadTemplates()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除模板失败:', error)
          ElMessage.error('删除模板失败')
        }
      }
    }
    
    onMounted(() => {
      loadProjects()
      loadTemplates()
    })
    
    return {
      projects,
      templates,
      reportConfig,
      reportData,
      chartRef,
      isFormValid,
      addChart,
      removeChart,
      generateReport,
      exportReport,
      saveTemplate,
      loadTemplate,
      deleteTemplate
    }
  }
}
</script>

<style scoped>
/* 导入设计系统 */
@import '@/styles/design-system.css';

.custom-report-container {
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

.btn-gradient:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-save {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 10px;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-generate {
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-export {
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s;
}

.btn-export:hover {
  transform: translateY(-2px);
  background: rgba(56, 189, 248, 0.1);
  border-color: #0ea5e9;
  color: #0ea5e9;
}

.btn-export:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-delete {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #ef4444;
  border-color: #fecaca;
  transition: all 0.3s;
}

.btn-delete:hover {
  background: #fef2f2;
  border-color: #ef4444;
  color: #dc2626;
  transform: translateY(-2px);
}

.btn-load {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #0ea5e9;
  border-color: #c7d2fe;
  transition: all 0.3s;
}

.btn-load:hover {
  background: #eef2ff;
  border-color: #0ea5e9;
  transform: translateY(-2px);
}

.btn-delete-template {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #ef4444;
  border-color: #fecaca;
  transition: all 0.3s;
}

.btn-delete-template:hover {
  background: #fef2f2;
  border-color: #ef4444;
  transform: translateY(-2px);
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

/* 配置区域 */
.report-config,
.chart-config,
.preview-area,
.template-management {
  margin-bottom: 24px;
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

.config-form {
  padding: 10px 0;
}

/* 自定义输入框样式 */
.custom-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.custom-select :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.custom-date-picker :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* 图表配置区域 */
.chart-item {
  padding: 16px 0;
}

.chart-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.chart-divider {
  margin: 16px 0;
  border-color: rgba(226, 232, 240, 0.6);
}

/* 预览区域 */
.header-actions {
  display: flex;
  gap: 12px;
}

.report-preview {
  padding: 20px 0;
}

.chart-preview {
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.empty-preview {
  text-align: center;
  padding: 80px 20px;
  color: #64748b;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon .el-icon {
  font-size: 40px;
  color: #0ea5e9;
}

.empty-text {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.empty-hint {
  font-size: 13px;
  color: #94a3b8;
}

/* 模板表格 */
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

.template-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #1e293b;
}

.template-name .el-icon {
  color: #0ea5e9;
  font-size: 18px;
}

.time-text {
  color: #64748b;
  font-size: 13px;
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
.delay-400 { animation-delay: 400ms; }

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .custom-report-container {
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

  .btn-save {
    width: 100%;
    justify-content: center;
  }

  .report-config,
  .chart-config,
  .preview-area,
  .template-management {
    margin-bottom: 16px;
  }

  .config-form .el-form-item {
    margin-bottom: 16px;
  }

  .custom-input,
  .custom-select,
  .custom-date-picker {
    width: 100% !important;
  }

  .chart-item {
    padding: 12px 0;
  }

  .chart-actions {
    justify-content: flex-start;
    margin-top: 12px;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 120px;
  }

  .chart-preview {
    padding: 12px;
    margin-bottom: 20px;
  }

  .empty-preview {
    padding: 40px 20px;
  }

  .empty-icon {
    width: 60px;
    height: 60px;
    border-radius: 18px;
  }

  .empty-icon .el-icon {
    font-size: 30px;
  }

  .el-table {
    font-size: 12px !important;
  }

  .el-table th,
  .el-table td {
    padding: 8px 6px !important;
  }
}

@media screen and (max-width: 480px) {
  .page-header {
    padding: 16px;
  }

  .title-text h1 {
    font-size: 20px;
  }

  .card-title {
    font-size: 14px;
  }

  .el-table {
    font-size: 11px !important;
  }
}
</style>
