<template>
  <div class="custom-report-container">
    <div class="header">
      <h1>自定义报表生成器</h1>
      <el-button type="primary" @click="saveTemplate" :disabled="!isFormValid">
        保存模板
      </el-button>
    </div>

    <!-- 报表配置区域 -->
    <div class="report-config">
      <el-card class="config-card">
        <template #header>
          <span>报表配置</span>
        </template>
        
        <el-form :model="reportConfig" label-width="120px">
          <el-form-item label="报表名称">
            <el-input v-model="reportConfig.name" placeholder="请输入报表名称" />
          </el-form-item>
          
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="reportConfig.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          
          <el-form-item label="项目筛选">
            <el-select v-model="reportConfig.projectIds" multiple placeholder="选择项目">
              <el-option
                v-for="project in projects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="Bug状态">
            <el-select v-model="reportConfig.statuses" multiple placeholder="选择Bug状态">
              <el-option label="新建" value="new" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已解决" value="resolved" />
              <el-option label="已关闭" value="closed" />
              <el-option label="重新打开" value="reopened" />
            </el-select>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 图表配置区域 -->
    <div class="chart-config">
      <el-card class="config-card">
        <template #header>
          <span>图表配置</span>
          <el-button type="primary" size="small" @click="addChart">添加图表</el-button>
        </template>
        
        <div v-for="(chart, index) in reportConfig.charts" :key="index" class="chart-item">
          <el-form-item label="图表类型">
            <el-select v-model="chart.type" placeholder="选择图表类型">
              <el-option label="趋势图" value="line" />
              <el-option label="柱状图" value="bar" />
              <el-option label="饼图" value="pie" />
              <el-option label="雷达图" value="radar" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="图表标题">
            <el-input v-model="chart.title" placeholder="请输入图表标题" />
          </el-form-item>
          
          <el-form-item label="数据维度">
            <el-select v-model="chart.dimension" placeholder="选择数据维度">
              <el-option label="Bug状态分布" value="status" />
              <el-option label="优先级分布" value="priority" />
              <el-option label="严重程度分布" value="severity" />
              <el-option label="趋势分析" value="trend" />
              <el-option label="根因分析" value="root_cause" />
            </el-select>
          </el-form-item>
          
          <el-button type="danger" size="small" @click="removeChart(index)">删除</el-button>
          <el-divider />
        </div>
      </el-card>
    </div>

    <!-- 预览区域 -->
    <div class="preview-area">
      <el-card class="preview-card">
        <template #header>
          <span>报表预览</span>
          <el-button type="success" @click="generateReport" :disabled="!isFormValid">
            生成报表
          </el-button>
          <el-button type="warning" @click="exportReport" :disabled="!reportData">
            导出报表
          </el-button>
        </template>
        
        <div v-if="reportData" class="report-preview">
          <div v-for="(chartData, index) in reportData.charts" :key="index" class="chart-preview">
            <div ref="chartRef" :style="{ width: '100%', height: '400px' }"></div>
          </div>
        </div>
        
        <div v-else class="empty-preview">
          <p>请配置报表参数并点击"生成报表"查看预览</p>
        </div>
      </el-card>
    </div>

    <!-- 模板管理 -->
    <div class="template-management">
      <el-card class="template-card">
        <template #header>
          <span>报表模板管理</span>
        </template>
        
        <el-table :data="templates" style="width: 100%">
          <el-table-column prop="name" label="模板名称" />
          <el-table-column prop="createdAt" label="创建时间" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button size="small" @click="loadTemplate(scope.row)">加载</el-button>
              <el-button size="small" type="danger" @click="deleteTemplate(scope.row.id)">删除</el-button>
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

export default {
  name: 'CustomReport',
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
.custom-report-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.config-card, .preview-card, .template-card {
  margin-bottom: 20px;
}

.chart-item {
  border: 1px solid #e4e7ed;
  padding: 15px;
  margin-bottom: 15px;
  border-radius: 4px;
}

.chart-preview {
  margin-bottom: 30px;
}

.empty-preview {
  text-align: center;
  padding: 50px;
  color: #909399;
}

.template-management {
  margin-top: 30px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .custom-report {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  .page-header h2 {
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
    font-size: 12px;
    padding: 8px 12px;
  }

  .filter-card {
    margin-bottom: 16px;
  }

  .filter-form {
    flex-direction: column;
    gap: 12px;
  }

  .filter-form .el-form-item {
    margin-right: 0;
    margin-bottom: 8px;
    width: 100%;
  }

  .filter-form .el-input,
  .filter-form .el-select {
    width: 100% !important;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 16px;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-label {
    font-size: 12px;
  }

  .chart-container {
    height: 250px !important;
  }

  .template-management {
    margin-top: 16px;
  }

  .el-table {
    font-size: 11px !important;
  }

  .el-table th,
  .el-table td {
    padding: 6px 4px !important;
  }

  .pagination-container {
    justify-content: center;
    margin-top: 16px;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
  }
}

@media screen and (max-width: 480px) {
  .custom-report {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-value {
    font-size: 18px;
  }

  .el-table {
    font-size: 10px !important;
  }
}
</style>