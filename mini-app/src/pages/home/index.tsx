import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, Button } from '@tarojs/components';
import Taro from '@tarojs/taro';
import classnames from 'classnames';
import styles from './index.module.scss';
import { KpiData, TrendData } from '../../types/bug';
import { mockKpiData, mockTrendData } from '../../data/bugData';

const HomePage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [kpiData, setKpiData] = useState<KpiData>(mockKpiData);
  const [trendData, setTrendData] = useState<TrendData[]>(mockTrendData);
  const [granularity, setGranularity] = useState<'day' | 'week' | 'month'>('day');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      setKpiData(mockKpiData);
      setTrendData(mockTrendData);
      console.log('[Home] Data loaded successfully');
    } catch (error) {
      console.error('[Home] Error loading data:', error);
      Taro.showToast({
        title: '数据加载失败',
        icon: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const onPullDownRefresh = () => {
    loadData().then(() => {
      Taro.stopPullDownRefresh();
      Taro.showToast({
        title: '刷新成功',
        icon: 'success'
      });
    });
  };

  const getChangeClass = (change: number) => {
    if (change > 0) return 'trendUp';
    if (change < 0) return 'trendDown';
    return 'trendStable';
  };

  const getChangeIcon = (change: number) => {
    if (change > 0) return '↑';
    if (change < 0) return '↓';
    return '-';
  };

  const navigateToBugList = (filter?: string) => {
    if (filter) {
      Taro.navigateTo({
        url: `/pages/bug-list/index?filter=${filter}`
      });
    } else {
      Taro.switchTab({
        url: '/pages/bug-list/index'
      });
    }
  };

  const navigateToProjectList = () => {
    Taro.navigateTo({
      url: '/pages/project-list/index'
    });
  };

  const navigateToMyTodos = () => {
    Taro.navigateTo({
      url: '/pages/my-todos/index'
    });
  };

  const navigateToAttendance = () => {
    Taro.navigateTo({
      url: '/pages/attendance/index'
    });
  };

  const navigateToContracts = () => {
    Taro.navigateTo({
      url: '/pages/contracts/index'
    });
  };

  const navigateToKnowledge = () => {
    Taro.navigateTo({
      url: '/pages/knowledge/index'
    });
  };

  const renderTrendChart = () => {
    const displayData = trendData.slice(-10);
    const maxValue = Math.max(...displayData.map(d => Math.max(d.new_bugs, d.resolved_bugs, d.cumulative_unresolved)));

    return (
      <View className={styles.chartContainer}>
        <View className={styles.chartBars}>
          {displayData.map((item, index) => (
            <View key={index} className={styles.barGroup}>
              <View className={styles.barWrapper}>
                <View
                  className={classnames(styles.bar, styles.barNew)}
                  style={{
                    height: `${(item.new_bugs / maxValue) * 200}rpx`
                  }}
                />
                <View
                  className={classnames(styles.bar, styles.barResolved)}
                  style={{
                    height: `${(item.resolved_bugs / maxValue) * 200}rpx`
                  }}
                />
              </View>
              <Text className={styles.barLabel}>{item.date}</Text>
            </View>
          ))}
        </View>
        <View className={styles.chartLegend}>
          <View className={styles.legendItem}>
            <View className={classnames(styles.legendDot, styles.legendDotNew)} />
            <Text>新增Bug</Text>
          </View>
          <View className={styles.legendItem}>
            <View className={classnames(styles.legendDot, styles.legendDotResolved)} />
            <Text>已解决</Text>
          </View>
        </View>
      </View>
    );
  };

  return (
    <View className={styles.container}>
      <View className={styles.header}>
        <View className={styles.titleWrapper}>
          <View className={styles.icon}>📊</View>
          <View className={styles.titleText}>
            <Text className={styles.mainTitle}>Bug统计看板</Text>
            <Text className={styles.subTitle}>全面分析Bug数据，洞察项目质量</Text>
          </View>
        </View>
        <Button
          className={styles.refreshBtn}
          onClick={loadData}
          loading={loading}
        >
          刷新
        </Button>
      </View>

      <ScrollView
        scrollY
        className={styles.content}
        enableBackToTop
      >
        <View className={styles.sectionTitle}>
          <View className={styles.dot} />
          <Text>核心指标</Text>
        </View>

        <View className={styles.kpiGrid}>
          <View
            className={classnames(styles.kpiCard, styles.kpiPrimary)}
            onClick={() => navigateToBugList()}
          >
            <View className={styles.kpiHeader}>
              <View className={styles.kpiIcon}>
                <Text className={styles.iconText}>🐛</Text>
                <View className={styles.kpiGlow} />
              </View>
              <View className={classnames(styles.kpiTrend, getChangeClass(kpiData.total_change))}>
                <Text>{getChangeIcon(kpiData.total_change)}</Text>
                <Text>{Math.abs(kpiData.total_change)}%</Text>
              </View>
            </View>
            <View className={styles.kpiBody}>
              <View className={classnames(styles.kpiValue, styles.kpiValueLarge)}>
                <Text>{kpiData.total_bugs.toLocaleString()}</Text>
              </View>
              <Text className={styles.kpiLabel}>总Bug数</Text>
            </View>
          </View>

          <View
            className={classnames(styles.kpiCard, styles.kpiWarning)}
            onClick={() => navigateToBugList('new')}
          >
            <View className={styles.kpiHeader}>
              <View className={styles.kpiIcon}>
                <Text className={styles.iconText}>✨</Text>
                <View className={styles.kpiGlow} />
              </View>
            </View>
            <View className={styles.kpiBody}>
              <View className={styles.kpiValue}>
                <Text>{kpiData.new_bugs}</Text>
              </View>
              <Text className={styles.kpiLabel}>新增Bug</Text>
            </View>
          </View>

          <View
            className={classnames(styles.kpiCard, styles.kpiSuccess)}
            onClick={() => navigateToBugList('resolved')}
          >
            <View className={styles.kpiHeader}>
              <View className={styles.kpiIcon}>
                <Text className={styles.iconText}>✅</Text>
                <View className={styles.kpiGlow} />
              </View>
            </View>
            <View className={styles.kpiBody}>
              <View className={styles.kpiValue}>
                <Text>{kpiData.resolved_bugs}</Text>
              </View>
              <Text className={styles.kpiLabel}>已解决</Text>
            </View>
          </View>

          <View
            className={classnames(styles.kpiCard, styles.kpiError)}
            onClick={() => navigateToBugList('unresolved')}
          >
            <View className={styles.kpiHeader}>
              <View className={styles.kpiIcon}>
                <Text className={styles.iconText}>⚠️</Text>
                <View className={styles.kpiGlow} />
              </View>
            </View>
            <View className={styles.kpiBody}>
              <View className={styles.kpiValue}>
                <Text>{kpiData.unresolved_bugs}</Text>
              </View>
              <Text className={styles.kpiLabel}>未解决</Text>
            </View>
          </View>

          <View className={classnames(styles.kpiCard, styles.kpiInfo)}>
            <View className={styles.kpiHeader}>
              <View className={styles.kpiIcon}>
                <Text className={styles.iconText}>📈</Text>
                <View className={styles.kpiGlow} />
              </View>
            </View>
            <View className={styles.kpiBody}>
              <View className={styles.kpiValue}>
                <Text>{kpiData.resolution_rate}</Text>
                <Text className={styles.kpiUnit}>%</Text>
              </View>
              <Text className={styles.kpiLabel}>解决率</Text>
            </View>
          </View>

          <View className={classnames(styles.kpiCard, styles.kpiPurple)}>
            <View className={styles.kpiHeader}>
              <View className={styles.kpiIcon}>
                <Text className={styles.iconText}>⏱️</Text>
                <View className={styles.kpiGlow} />
              </View>
            </View>
            <View className={styles.kpiBody}>
              <View className={styles.kpiValue}>
                <Text>{kpiData.avg_fix_time}</Text>
                <Text className={styles.kpiUnit}>天</Text>
              </View>
              <Text className={styles.kpiLabel}>平均解决时长</Text>
            </View>
          </View>
        </View>

        <View className={styles.sectionTitle}>
          <View className={styles.dot} />
          <Text>趋势分析</Text>
        </View>

        <View className={styles.trendChart}>
          <View className={styles.chartHeader}>
            <Text className={styles.chartTitle}>Bug趋势</Text>
            <View className={styles.granularity}>
              {(['day', 'week', 'month'] as const).map(item => (
                <Button
                  key={item}
                  className={classnames(
                    styles.granularityBtn,
                    granularity === item && styles.active
                  )}
                  onClick={() => setGranularity(item)}
                >
                  {item === 'day' ? '日' : item === 'week' ? '周' : '月'}
                </Button>
              ))}
            </View>
          </View>
          {renderTrendChart()}
        </View>

        <View className={styles.sectionTitle}>
          <View className={styles.dot} />
          <Text>快捷入口</Text>
        </View>

        <View className={styles.quickActions}>
          <View className={styles.actionsGrid}>
            <View className={styles.actionItem} onClick={() => navigateToBugList('new')}>
              <View className={styles.actionIcon} style={{ background: 'linear-gradient(135deg, #FEF3C7, #FDE68A)' }}>
                <Text>🐛</Text>
              </View>
              <Text className={styles.actionLabel}>新建Bug</Text>
            </View>
            <View className={styles.actionItem} onClick={() => navigateToProjectList()}>
              <View className={styles.actionIcon} style={{ background: 'linear-gradient(135deg, #DBEAFE, #BFDBFE)' }}>
                <Text>📁</Text>
              </View>
              <Text className={styles.actionLabel}>项目列表</Text>
            </View>
            <View className={styles.actionItem} onClick={() => navigateToMyTodos()}>
              <View className={styles.actionIcon} style={{ background: 'linear-gradient(135deg, #FEE2E2, #FECACA)' }}>
                <Text>✅</Text>
              </View>
              <Text className={styles.actionLabel}>我的待办</Text>
            </View>
            <View className={styles.actionItem} onClick={() => navigateToAttendance()}>
              <View className={styles.actionIcon} style={{ background: 'linear-gradient(135deg, #D1FAE5, #A7F3D0)' }}>
                <Text>📅</Text>
              </View>
              <Text className={styles.actionLabel}>考勤打卡</Text>
            </View>
            <View className={styles.actionItem} onClick={() => navigateToContracts()}>
              <View className={styles.actionIcon} style={{ background: 'linear-gradient(135deg, #E0E7FF, #C7D2FE)' }}>
                <Text>📄</Text>
              </View>
              <Text className={styles.actionLabel}>合同管理</Text>
            </View>
            <View className={styles.actionItem} onClick={() => navigateToKnowledge()}>
              <View className={styles.actionIcon} style={{ background: 'linear-gradient(135deg, #FCE7F3, #FBCFE8)' }}>
                <Text>📚</Text>
              </View>
              <Text className={styles.actionLabel}>知识库</Text>
            </View>
          </View>
        </View>
      </ScrollView>

      {loading && (
        <View className={styles.loadingOverlay}>
          <View className={styles.loadingSpinner} />
        </View>
      )}
    </View>
  );
};

export default HomePage;
