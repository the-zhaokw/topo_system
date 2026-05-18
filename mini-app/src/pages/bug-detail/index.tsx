import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, Button } from '@tarojs/components';
import Taro from '@tarojs/taro';
import classnames from 'classnames';
import styles from './index.module.scss';
import { Bug, BugStatus, BugSeverity } from '../../types/bug';
import { mockBugList } from '../../data/bugData';

const BugDetailPage: React.FC = () => {
  const [bug, setBug] = useState<Bug | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBugDetail();
  }, []);

  const loadBugDetail = async () => {
    const eventChannel = Taro.getCurrentInstance().page?.getOpenerEventChannel();
    if (eventChannel) {
      eventChannel.on('acceptDataFromOpenerPage', (data) => {
        console.log('[BugDetail] Received data:', data);
      });
    }

    const { id } = Taro.getCurrentInstance().router?.params || {};

    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 300));

      const bugData = mockBugList.find(b => b.id === Number(id)) || mockBugList[0];
      setBug(bugData);
      console.log('[BugDetail] Loaded bug:', bugData);
    } catch (error) {
      console.error('[BugDetail] Error loading bug:', error);
      Taro.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      setLoading(false);
    }
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

  const getPriorityLabel = (priority: string): string => {
    const labels: Record<string, string> = {
      'urgent': '紧急',
      'high': '高',
      'medium': '中',
      'low': '低'
    };
    return labels[priority] || priority;
  };

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
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

  const handleAssign = () => {
    Taro.showToast({
      title: '分配功能开发中',
      icon: 'info'
    });
  };

  const handleUpdateStatus = () => {
    Taro.showToast({
      title: '状态更新功能开发中',
      icon: 'info'
    });
  };

  if (loading || !bug) {
    return (
      <View className={styles.container}>
        <View className={styles.header}>
          <Text style={{ color: '#fff' }}>加载中...</Text>
        </View>
      </View>
    );
  }

  return (
    <View className={styles.container}>
      <View className={styles.header}>
        <View className={styles.bugIdBadge}>
          <Text>#{bug.id}</Text>
        </View>
        <Text className={styles.bugTitle}>{bug.title}</Text>
        <View className={styles.statusBadge}>
          <Text>{getStatusLabel(bug.status)}</Text>
        </View>
      </View>

      <ScrollView scrollY className={styles.content} style={{ paddingBottom: '140rpx' }}>
        <View className={styles.infoCard}>
          <View className={styles.infoRow}>
            <Text className={styles.infoLabel}>所属项目</Text>
            <Text className={styles.infoValue}>{bug.project_name}</Text>
          </View>
          <View className={styles.infoRow}>
            <Text className={styles.infoLabel}>严重程度</Text>
            <View className={styles.tagGroup}>
              <Text className={classnames(styles.tag, getSeverityClass(bug.severity))}>
                {getSeverityLabel(bug.severity)}
              </Text>
            </View>
          </View>
          <View className={styles.infoRow}>
            <Text className={styles.infoLabel}>优先级</Text>
            <Text className={styles.infoValue}>{getPriorityLabel(bug.priority)}</Text>
          </View>
          <View className={styles.infoRow}>
            <Text className={styles.infoLabel}>创建人</Text>
            <Text className={styles.infoValue}>{bug.reporter_name}</Text>
          </View>
          {bug.assignee_name && (
            <View className={styles.infoRow}>
              <Text className={styles.infoLabel}>负责人</Text>
              <Text className={styles.infoValue}>{bug.assignee_name}</Text>
            </View>
          )}
          <View className={styles.infoRow}>
            <Text className={styles.infoLabel}>创建时间</Text>
            <Text className={styles.infoValue}>{formatDateTime(bug.created_at)}</Text>
          </View>
          {bug.updated_at && (
            <View className={styles.infoRow}>
              <Text className={styles.infoLabel}>更新时间</Text>
              <Text className={styles.infoValue}>{formatDateTime(bug.updated_at)}</Text>
            </View>
          )}
        </View>

        <View className={styles.descriptionCard}>
          <View className={styles.sectionTitle}>
            <Text>📝</Text>
            <Text>问题描述</Text>
          </View>
          <Text className={styles.description}>
            {bug.description || '暂无详细描述'}
          </Text>
        </View>

        <View className={styles.timelineCard}>
          <View className={styles.sectionTitle}>
            <Text>📋</Text>
            <Text>操作记录</Text>
          </View>
          <View className={styles.timeline}>
            <View className={styles.timelineItem}>
              <View className={styles.timelineDot} />
              <Text className={styles.timelineTime}>{formatDateTime(bug.created_at)}</Text>
              <Text className={styles.timelineContent}>
                {bug.reporter_name} 创建了这个Bug
              </Text>
            </View>
            {bug.status !== 'new' && (
              <View className={styles.timelineItem}>
                <View className={styles.timelineDot} />
                <Text className={styles.timelineTime}>
                  {new Date(new Date(bug.created_at).getTime() + 86400000).toLocaleString('zh-CN')}
                </Text>
                <Text className={styles.timelineContent}>
                  {bug.assignee_name || '负责人'} 开始处理
                </Text>
              </View>
            )}
            {bug.status === 'resolved' || bug.status === 'closed' ? (
              <View className={styles.timelineItem}>
                <View className={styles.timelineDot} />
                <Text className={styles.timelineTime}>
                  {new Date(new Date(bug.created_at).getTime() + 172800000).toLocaleString('zh-CN')}
                </Text>
                <Text className={styles.timelineContent}>
                  Bug已{getStatusLabel(bug.status)}
                </Text>
              </View>
            ) : null}
          </View>
        </View>
      </ScrollView>

      <View className={styles.actionBar}>
        <Button
          className={classnames(styles.actionBtn, styles.secondaryBtn)}
          onClick={handleAssign}
        >
          分配
        </Button>
        <Button
          className={classnames(styles.actionBtn, styles.primaryBtn)}
          onClick={handleUpdateStatus}
        >
          更新状态
        </Button>
      </View>
    </View>
  );
};

export default BugDetailPage;
