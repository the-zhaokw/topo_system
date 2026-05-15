<template>
  <div class="project-statistics">
    <div class="statistics-header animate-fade-in-down">
      <div class="header-title">
        <div class="title-icon">
          <el-icon><PieChart /></el-icon>
        </div>
        <div class="title-content">
          <h2>项目统计看板</h2>
          <p>全面分析项目数据，洞察项目进展</p>
        </div>
      </div>
      <div class="header-actions">
        <el-button @click="refreshData" class="refresh-btn">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- KPI 统计卡片 - 美学设计 -->
    <div class="kpi-cards animate-fade-in-up delay-100">
      <el-row :gutter="20">
        <el-col :span="6" :xs="12" :sm="12" :md="6">
          <div class="kpi-card kpi-card-total" :style="{ '--index': 0 }">
            <div class="kpi-icon-wrapper kpi-icon-total">
              <el-icon><FolderOpened /></el-icon>
            </div>
            <div class="kpi-content">
              <div class="kpi-value">
                <span class="kpi-number">{{ kpiData.totalProjects || 0 }}</span>
              </div>
              <div class="kpi-label">项目总数</div>
            </div>
            <div class="kpi-decoration"></div>
          </div>
        </el-col>
        <el-col :span="6" :xs="12" :sm="12" :md="6">
          <div class="kpi-card kpi-card-active" :style="{ '--index': 1 }">
            <div class="kpi-icon-wrapper kpi-icon-active">
              <el-icon><Folder /></el-icon>
            </div>
            <div class="kpi-content">
              <div class="kpi-value success">
                <span class="kpi-number">{{ kpiData.activeProjects || 0 }}</span>
              </div>
              <div class="kpi-label">进行中项目</div>
            </div>
            <div class="kpi-decoration"></div>
          </div>
        </el-col>
        <el-col :span="6" :xs="12" :sm="12" :md="6">
          <div class="kpi-card kpi-card-tasks" :style="{ '--index': 2 }">
            <div class="kpi-icon-wrapper kpi-icon-tasks">
              <el-icon><List /></el-icon>
            </div>
            <div class="kpi-content">
              <div class="kpi-value info">
                <span class="kpi-number">{{ kpiData.totalTasks || 0 }}</span>
              </div>
              <div class="kpi-label">需求总数</div>
            </div>
            <div class="kpi-decoration"></div>
          </div>
        </el-col>
        <el-col :span="6" :xs="12" :sm="12" :md="6">
          <div class="kpi-card kpi-card-bugs" :style="{ '--index': 3 }">
            <div class="kpi-icon-wrapper kpi-icon-bugs">
              <el-icon><WarningFilled /></el-icon>
            </div>
            <div class="kpi-content">
              <div class="kpi-value danger">
                <span class="kpi-number">{{ kpiData.totalBugs || 0 }}</span>
              </div>
              <div class="kpi-label">缺陷总数</div>
            </div>
            <div class="kpi-decoration"></div>
          </div>
        </el-col>
      </el-row>
    </div>

    <el-row :gutter="20" class="chart-section animate-fade-in-up delay-200">
      <el-col :span="12" :xs="24">
        <el-card class="chart-card glass-card" shadow="hover">
          <template #header>
            <div class="chart-header">
              <div class="chart-title">
                <el-icon><Warning /></el-icon>
                <span>项目Bug分布</span>
              </div>
            </div>
          </template>
          <div ref="bugDistributionChart" class="chart-container" style="height: 400px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12" :xs="24">
        <el-card class="chart-card glass-card" shadow="hover">
          <template #header>
            <div class="chart-header">
              <div class="chart-title">
                <el-icon><List /></el-icon>
                <span>项目需求统计</span>
              </div>
            </div>
          </template>
          <div ref="taskChart" class="chart-container" style="height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="data-table-card glass-card animate-fade-in-up delay-300" shadow="hover">
      <template #header>
        <div class="table-header">
          <div class="table-title">
            <el-icon><Document /></el-icon>
            <span>项目详情列表</span>
          </div>
        </div>
      </template>
      <el-table :data="projectList" v-loading="loading" class="custom-table">
        <el-table-column prop="project_name" label="项目名称" min-width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
