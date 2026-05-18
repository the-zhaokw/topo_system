import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import {
  mockKpiData,
  mockTrendData,
  mockBugList,
  mockFilterOptions
} from '@/data/bugStatistics';
import { KpiData, Bug, TimeRange } from '@/types/bugStatistics';

const BugStatisticsPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState<TimeRange>('month');
  const [kpiData, setKpiData] = useState<KpiData>(mockKpiData);
  const [bugList, setBugList] = useState<Bug[]>(mockBugList);
  const [showFilter, setShowFilter] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPage] = useState(3);
  const [trendTab, setTrendTab] = useState<'day' | 'week' | 'month'>('day');

  useEffect(() => {
    loadData();
  }, [timeRange]);

  const loadData = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      setKpiData(mockKpiData);
      setBugList(mockBugList);
    } catch (error) {
      console.error('[BugStatistics] 加载数据失败:', error);
      Taro.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadData();
    Taro.showToast({ title: '刷新成功', icon: 'success' });
  };

  const handleFilterChange = () => {
    setShowFilter(false);
    loadData();
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      'new': '新建',
      'assigned': '已分配',
      'in_progress': '处理中',
      'resolved': '已解决',
      'verified': '已验证',
      'closed': '已关闭',
      'rejected': '已拒绝',
      'reopened': '重新打开'
    };
    return labels[status] || status;
  };

  const getSeverityLabel = (severity: string) => {
    const labels: Record<string, string> = {
      'critical': '致命P0',
      'high': '严重P1',
      'medium': '一般P2',
      'low': '轻微P3',
      'suggestion': '建议P4'
    };
    return labels[severity] || severity;
  };

  const getPriorityLabel = (priority: string) => {
    const labels: Record<string, string> = {
      'urgent': '紧急',
      'high': '高',
      'medium': '中',
      'low': '低'
    };
    return labels[priority] || priority;
  };

  const getTimeRangeLabel = () => {
    const labels: Record<TimeRange, string> = {
      'today': '今日',
      'week': '本周',
      'month': '本月',
      'quarter': '本季度',
      'custom': '自定义'
    };
    return labels[timeRange];
  };

  const renderTrendChart = () => {
    const data = mockTrendData.slice(-7);
    const maxValue = Math.max(...data.map(d => Math.max(d.new_bugs, d.resolved_bugs, d.cumulative_unresolved / 100)));

    return (
      <View className={styles.simpleChart}>
        <View style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'flex-end', height: '320rpx', padding: '0 16rpx' }}>
          {data.map((item, index) => (
            <View key={index} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
              <View style={{ display: 'flex', gap: '4rpx', alignItems: 'flex-end', height: '240rpx' }}>
                <View style={{
                  width: '24rpx',
                  height: `${(item.new_bugs / maxValue) * 200}rpx`,
                  background: '#8b5cf6',
                  borderRadius: '4rpx 4rpx 0 0'
                }} />
                <View style={{
                  width: '24rpx',
                  height: `${(item.resolved_bugs / maxValue) * 200}rpx`,
                  background: '#22c55e',
                  borderRadius: '4rpx 4rpx 0 0'
                }} />
              </View>
              <Text style={{ fontSize: '20rpx', color: '#86909c', marginTop: '8rpx' }}>
                {item.date.slice(-2)}
              </Text>
            </View>
          ))}
        </View>
        <View className={styles.chartLegend}>
          <View className={styles.legendItem}>
            <View className={styles.legendDot} style={{ background: '#8b5cf6' }} />
            <Text>新增Bug</Text>
          </View>
          <View className={styles.legendItem}>
            <View className={styles.legendDot} style={{ background: '#22c55e' }} />
            <Text>解决Bug</Text>
          </View>
        </View>
      </View>
    );
  };

  return (
    <View className={styles.container}>
      {/* 头部 */}
      <View className={styles.header}>
        <View className={styles.headerContent}>
          <View className={styles.titleSection}>
            <View className={styles.iconWrapper}>
              <Text className={styles.icon}>📊</Text>
            </View>
            <View className={styles.titleText}>
              <Text className={styles.title}>Bug统计看板</Text>
              <Text className={styles.subtitle}>全面分析Bug数据，洞察项目质量</Text>
            </View>
          </View>
          <View className={styles.refreshBtn} onClick={handleRefresh}>
            <Text>🔄</Text>
          </View>
        </View>
      </View>

      <ScrollView
        scrollY
        className={styles.scrollView}
        onScrollToLower={() => {
          if (currentPage < totalPage) {
            setCurrentPage(prev => prev + 1);
          }
        }}
      >
        {/* 筛选区域 */}
        <View className={styles.filterSection}>
          <View className={styles.filterRow}>
            <Text className={styles.filterLabel}>时间:</Text>
            <View className={styles.filterSelect}>
              <Text
                className={styles.chartTabActive}
                onClick={() => setShowFilter(true)}
              >
                {getTimeRangeLabel()} ▼
              </Text>
            </View>
            <View className={styles.filterItem}>
              <Text
                className={styles.chartTab}
                onClick={() => setShowFilter(true)}
              >
                多条件筛选
              </Text>
            </View>
          </View>
        </View>

        {/* KPI统计卡片 */}
        <View className={styles.kpiSection}>
          <ScrollView scrollX className={styles.kpiScroll}>
            <View className={styles.kpiCard}>
              <View className={styles.kpiCardTop}>
                <View className={`${styles.kpiIcon} ${styles.kpiIconTotal}`}>
                  <Text>⚠️</Text>
                </View>
              </View>
              <View>
                <View style={{ display: 'flex', alignItems: 'baseline', gap: '8rpx' }}>
                  <Text className={styles.kpiValue}>{kpiData.total_bugs}</Text>
                  <Text className={`${styles.kpiChange} ${styles.kpiChangeUp}`}>
                    ↑ {kpiData.total_change}%
                  </Text>
                </View>
                <Text className={styles.kpiLabel}>总Bug数</Text>
              </View>
            </View>

            <View className={styles.kpiCard}>
              <View className={styles.kpiCardTop}>
                <View className={`${styles.kpiIcon} ${styles.kpiIconNew}`}>
                  <Text>➕</Text>
                </View>
              </View>
              <View>
                <View style={{ display: 'flex', alignItems: 'baseline', gap: '8rpx' }}>
                  <Text className={styles.kpiValue}>{kpiData.new_bugs}</Text>
                  <Text className={styles.kpiSub}>周期内</Text>
                </View>
                <Text className={styles.kpiLabel}>新增Bug</Text>
              </View>
            </View>

            <View className={styles.kpiCard}>
              <View className={styles.kpiCardTop}>
                <View className={`${styles.kpiIcon} ${styles.kpiIconResolved}`}>
                  <Text>✅</Text>
                </View>
              </View>
              <View>
                <Text className={`${styles.kpiValue} ${styles.kpiValueSuccess}`}>
                  {kpiData.resolved_bugs}
                </Text>
                <Text className={styles.kpiLabel}>已解决</Text>
              </View>
            </View>

            <View className={styles.kpiCard}>
              <View className={styles.kpiCardTop}>
                <View className={`${styles.kpiIcon} ${styles.kpiIconUnresolved}`}>
                  <Text>⚠️</Text>
                </View>
              </View>
              <View>
                <Text className={`${styles.kpiValue} ${styles.kpiValueDanger}`}>
                  {kpiData.unresolved_bugs}
                </Text>
                <Text className={styles.kpiLabel}>未解决</Text>
              </View>
            </View>

            <View className={styles.kpiCard}>
              <View className={styles.kpiCardTop}>
                <View className={`${styles.kpiIcon} ${styles.kpiIconRate}`}>
                  <Text>📈</Text>
                </View>
              </View>
              <View>
                <View style={{ display: 'flex', alignItems: 'baseline', gap: '4rpx' }}>
                  <Text className={styles.kpiValue}>{kpiData.resolution_rate}</Text>
                  <Text className={styles.kpiUnit}>%</Text>
                </View>
                <Text className={styles.kpiLabel}>解决率</Text>
              </View>
            </View>

            <View className={styles.kpiCard}>
              <View className={styles.kpiCardTop}>
                <View className={`${styles.kpiIcon} ${styles.kpiIconTime}`}>
                  <Text>⏱️</Text>
                </View>
              </View>
              <View>
                <View style={{ display: 'flex', alignItems: 'baseline', gap: '4rpx' }}>
                  <Text className={styles.kpiValue}>{kpiData.avg_fix_time}</Text>
                  <Text className={styles.kpiUnit}>天</Text>
                </View>
                <Text className={styles.kpiLabel}>平均解决时长</Text>
              </View>
            </View>
          </ScrollView>
        </View>

        {/* 趋势图表 */}
        <View className={styles.chartSection}>
          <View className={styles.chartCard}>
            <View className={styles.chartHeader}>
              <Text className={styles.chartTitle}>Bug趋势分析</Text>
              <View className={styles.chartControls}>
                {(['day', 'week', 'month'] as const).map(tab => (
                  <Text
                    key={tab}
                    className={`${styles.chartTab} ${trendTab === tab ? styles.chartTabActive : ''}`}
                    onClick={() => setTrendTab(tab)}
                  >
                    {tab === 'day' ? '日' : tab === 'week' ? '周' : '月'}
                  </Text>
                ))}
              </View>
            </View>
            {renderTrendChart()}
          </View>
        </View>

        {/* Bug列表 */}
        <View className={styles.bugListSection}>
          <View className={styles.bugListHeader}>
            <View className={styles.bugListTitle}>
              <Text>Bug明细列表</Text>
              <Text className={styles.bugCount}>{bugList.length}</Text>
            </View>
          </View>

          {bugList.map(bug => (
            <View key={bug.id} className={styles.bugCard}>
              <View className={styles.bugCardHeader}>
                <Text className={styles.bugId}>#{bug.id}</Text>
                <View className={styles.bugTags}>
                  <Text className={`${styles.tag} ${styles[`tag${bug.status.charAt(0).toUpperCase() + bug.status.slice(1)}`] || styles.tagNew}`}>
                    {getStatusLabel(bug.status)}
                  </Text>
                  <Text className={`${styles.tag} ${styles[`tag${bug.severity.charAt(0).toUpperCase() + bug.severity.slice(1)}`] || styles.tagMedium}`}>
                    {getSeverityLabel(bug.severity)}
                  </Text>
                </View>
              </View>
              <Text className={styles.bugTitle}>{bug.title}</Text>
              <View className={styles.bugMeta}>
                <Text className={styles.bugProject}>
                  📁 {bug.project_name}
                </Text>
                <Text className={styles.bugProject}>
                  👤 {bug.reporter_name}
                </Text>
              </View>
            </View>
          ))}

          {currentPage < totalPage && (
            <View className={styles.loadMore}>
              <Text className={styles.loadMoreText}>上滑加载更多...</Text>
            </View>
          )}
        </View>
      </ScrollView>

      {/* 筛选抽屉 */}
      <View
        className={`${styles.filterDrawer} ${showFilter ? '' : styles.filterDrawerHidden}`}
        onClick={() => setShowFilter(false)}
      >
        <View
          className={styles.filterDrawerContent}
          onClick={e => e.stopPropagation()}
        >
          <View className={styles.filterDrawerHeader}>
            <Text className={styles.filterDrawerTitle}>筛选条件</Text>
            <View className={styles.filterDrawerClose} onClick={() => setShowFilter(false)}>
              <Text>✕</Text>
            </View>
          </View>

          <View className={styles.filterDrawerBody}>
            <View className={styles.filterGroup}>
              <Text className={styles.filterGroupTitle}>时间范围</Text>
              <View className={styles.filterOptions}>
                {(['today', 'week', 'month', 'quarter'] as TimeRange[]).map(range => (
                  <Text
                    key={range}
                    className={`${styles.filterOption} ${timeRange === range ? styles.filterOptionActive : ''}`}
                    onClick={() => setTimeRange(range)}
                  >
                    {getTimeRangeLabel()}
                  </Text>
                ))}
              </View>
            </View>

            <View className={styles.filterGroup}>
              <Text className={styles.filterGroupTitle}>严重程度</Text>
              <View className={styles.filterOptions}>
                {['critical', 'high', 'medium', 'low', 'suggestion'].map(sev => (
                  <Text key={sev} className={styles.filterOption}>
                    {getSeverityLabel(sev)}
                  </Text>
                ))}
              </View>
            </View>

            <View className={styles.filterGroup}>
              <Text className={styles.filterGroupTitle}>Bug状态</Text>
              <View className={styles.filterOptions}>
                {['new', 'in_progress', 'resolved', 'closed'].map(status => (
                  <Text key={status} className={styles.filterOption}>
                    {getStatusLabel(status)}
                  </Text>
                ))}
              </View>
            </View>

            <View className={styles.filterGroup}>
              <Text className={styles.filterGroupTitle}>所属项目</Text>
              <View className={styles.filterOptions}>
                {mockFilterOptions.projects.map(project => (
                  <Text key={project.id} className={styles.filterOption}>
                    {project.name}
                  </Text>
                ))}
              </View>
            </View>
          </View>

          <View className={styles.filterDrawerFooter}>
            <View className={styles.filterResetBtn} onClick={() => setTimeRange('month')}>
              <Text>重置</Text>
            </View>
            <View className={styles.filterConfirmBtn} onClick={handleFilterChange}>
              <Text>确定筛选</Text>
            </View>
          </View>
        </View>
      </View>
    </View>
  );
};

export default BugStatisticsPage;
