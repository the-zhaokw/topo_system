import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import classnames from 'classnames';
import styles from './index.module.scss';
import { Bug, BugStatus, BugSeverity } from '../../types/bug';
import { mockBugList } from '../../data/bugData';

const BugListPage: React.FC = () => {
  const [bugList, setBugList] = useState<Bug[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  const [activeFilter, setActiveFilter] = useState<string>('all');

  const statusFilters = [
    { key: 'all', label: '全部' },
    { key: 'new', label: '新建' },
    { key: 'in_progress', label: '处理中' },
    { key: 'resolved', label: '已解决' },
    { key: 'closed', label: '已关闭' }
  ];

  useEffect(() => {
    loadBugs(true);
  }, [activeFilter]);

  const loadBugs = async (reset = false) => {
    if (loading) return;

    const currentPage = reset ? 1 : page;

    if (!reset && !hasMore) return;

    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));

      let filteredData = [...mockBugList];

      if (activeFilter !== 'all') {
        if (activeFilter === 'unresolved') {
          filteredData = filteredData.filter(bug =>
            bug.status === 'new' || bug.status === 'in_progress'
          );
        } else if (activeFilter === 'resolved') {
          filteredData = filteredData.filter(bug =>
            bug.status === 'resolved' || bug.status === 'closed'
          );
        } else {
          filteredData = filteredData.filter(bug => bug.status === activeFilter);
        }
      }

      if (reset) {
        setBugList(filteredData.slice(0, 10));
        setPage(2);
      } else {
        const newData = filteredData.slice((currentPage - 1) * 10, currentPage * 10);
        setBugList(prev => [...prev, ...newData]);
        setPage(currentPage + 1);
      }

      setHasMore(filteredData.length > currentPage * 10);
      console.log(`[BugList] Loaded page ${currentPage}, total ${filteredData.length}`);
    } catch (error) {
      console.error('[BugList] Error loading bugs:', error);
      Taro.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const onPullDownRefresh = () => {
    loadBugs(true).then(() => {
      Taro.stopPullDownRefresh();
      Taro.showToast({
        title: '刷新成功',
        icon: 'success'
      });
    });
  };

  const onReachBottom = () => {
    if (!loading && hasMore) {
      loadBugs(false);
    }
  };

  const handleFilterChange = (filter: string) => {
    setActiveFilter(filter);
  };

  const navigateToDetail = (bugId: number) => {
    Taro.navigateTo({
      url: `/pages/bug-detail/index?id=${bugId}`
    });
  };

  const getStatusLabel = (status: BugStatus): string => {
    const labels: Record<BugStatus, string> = {
      'new': '新建',
      'in_progress': '处理中',
      'resolved': '已解决',
      'closed': '已关闭',
      'rejected': '已拒绝',
      'reopened': '重新打开'
    };
    return labels[status] || status;
  };

  const getSeverityLabel = (severity: BugSeverity): string => {
    const labels: Record<BugSeverity, string> = {
      'critical': 'P0-致命',
      'high': 'P1-严重',
      'medium': 'P2-一般',
      'low': 'P3-轻微',
      'suggestion': 'P4-建议'
    };
    return labels[severity] || severity;
  };

  const formatTime = (timeStr: string) => {
    const date = new Date(timeStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) {
      return '今天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    } else if (days === 1) {
      return '昨天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    } else if (days < 7) {
      return `${days}天前`;
    } else {
      return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
    }
  };

  const getInitials = (name: string) => {
    return name.charAt(0).toUpperCase();
  };

  const getStatusClass = (status: BugStatus) => {
    const classMap: Record<BugStatus, string> = {
      'new': styles.statusNew,
      'in_progress': styles.statusInProgress,
      'resolved': styles.statusResolved,
      'closed': styles.statusClosed,
      'rejected': styles.statusNew,
      'reopened': styles.statusReopened
    };
    return classMap[status] || '';
  };

  const getSeverityClass = (severity: BugSeverity) => {
    const classMap: Record<BugSeverity, string> = {
      'critical': styles.severityCritical,
      'high': styles.severityHigh,
      'medium': styles.severityMedium,
      'low': styles.severityLow,
      'suggestion': styles.severitySuggestion
    };
    return classMap[severity] || '';
  };

  const getStatusCardClass = (status: BugStatus) => {
    const classMap: Record<BugStatus, string> = {
      'new': styles.statusNew,
      'in_progress': styles.statusInProgress,
      'resolved': styles.statusResolved,
      'closed': styles.statusClosed,
      'rejected': styles.statusNew,
      'reopened': styles.statusReopened
    };
    return classMap[status] || '';
  };

  return (
    <View className={styles.container}>
      <View className={styles.filterBar}>
        <ScrollView scrollX className={styles.filterScroll} enableFlex>
          {statusFilters.map(filter => (
            <View
              key={filter.key}
              className={classnames(
                styles.filterChip,
                activeFilter === filter.key && styles.active
              )}
              onClick={() => handleFilterChange(filter.key)}
            >
              {filter.label}
            </View>
          ))}
        </ScrollView>
      </View>

      <ScrollView
        scrollY
        className={styles.bugList}
        enableBackToTop
        onPullDownRefresh={onPullDownRefresh}
        onReachBottom={onReachBottom}
      >
        {bugList.length === 0 ? (
          <View className={styles.emptyState}>
            <Text className={styles.emptyIcon}>🐛</Text>
            <Text className={styles.emptyText}>暂无Bug数据</Text>
            <Text className={styles.emptyHint}>尝试调整筛选条件</Text>
          </View>
        ) : (
          <>
            {bugList.map(bug => (
              <View
                key={bug.id}
                className={classnames(styles.bugCard, getStatusCardClass(bug.status))}
                onClick={() => navigateToDetail(bug.id)}
              >
                <View className={styles.bugHeader}>
                  <Text className={styles.bugId}>#{bug.id}</Text>
                  <Text className={styles.bugTime}>{formatTime(bug.created_at)}</Text>
                </View>

                <Text className={styles.bugTitle}>{bug.title}</Text>

                <View className={styles.bugMeta}>
                  <Text className={classnames(styles.tag, styles.projectTag)}>
                    {bug.project_name}
                  </Text>
                  <Text className={classnames(styles.tag, getSeverityClass(bug.severity))}>
                    {getSeverityLabel(bug.severity)}
                  </Text>
                  <Text className={classnames(styles.tag, getStatusClass(bug.status))}>
                    {getStatusLabel(bug.status)}
                  </Text>
                </View>

                <View className={styles.bugFooter}>
                  <View className={styles.reporter}>
                    <View className={styles.reporterAvatar}>
                      <Text>{getInitials(bug.reporter_name)}</Text>
                    </View>
                    <Text className={styles.reporterName}>{bug.reporter_name}</Text>
                  </View>
                  <Text className={styles.viewBtn}>查看详情</Text>
                </View>
              </View>
            ))}

            {loading && (
              <View className={styles.loadingMore}>
                <Text>加载中...</Text>
              </View>
            )}

            {!hasMore && bugList.length > 0 && (
              <View className={styles.noMore}>
                <Text>没有更多了</Text>
              </View>
            )}
          </>
        )}
      </ScrollView>
    </View>
  );
};

export default BugListPage;
