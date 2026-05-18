import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import classnames from 'classnames';
import styles from './index.module.scss';
import { PersonalPlan } from '../../types/business';
import { mockPersonalPlans } from '../../data/businessData';

const PersonalPlanPage: React.FC = () => {
  const [plans, setPlans] = useState<PersonalPlan[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      setPlans(mockPersonalPlans);
      console.log('[PersonalPlan] Loaded plans:', mockPersonalPlans.length);
    } catch (error) {
      console.error('[PersonalPlan] Error loading plans:', error);
      Taro.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const onPullDownRefresh = () => {
    loadPlans().then(() => {
      Taro.stopPullDownRefresh();
      Taro.showToast({
        title: '刷新成功',
        icon: 'success'
      });
    });
  };

  const getTypeLabel = (type: string): string => {
    const labels: Record<string, string> = {
      'daily': '每日计划',
      'weekly': '周计划',
      'monthly': '月计划'
    };
    return labels[type] || type;
  };

  const getTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      'daily': '📅',
      'weekly': '📆',
      'monthly': '🗓️'
    };
    return icons[type] || '📋';
  };

  const getStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      'pending': '待开始',
      'in_progress': '进行中',
      'completed': '已完成'
    };
    return labels[status] || status;
  };

  const getStatusClass = (status: string) => {
    const classMap: Record<string, string> = {
      'pending': styles.statusPending,
      'in_progress': styles.statusInProgress,
      'completed': styles.statusCompleted
    };
    return classMap[status] || '';
  };

  const formatTimeRange = (start: string, end: string) => {
    const startDate = new Date(start);
    const endDate = new Date(end);
    const startStr = startDate.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
    const endStr = endDate.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
    return `${startStr} - ${endStr}`;
  };

  return (
    <View className={styles.container}>
      <ScrollView
        scrollY
        className={styles.planList}
        enableBackToTop
        onPullDownRefresh={onPullDownRefresh}
      >
        {plans.length === 0 ? (
          <View className={styles.emptyState}>
            <Text className={styles.emptyIcon}>📋</Text>
            <Text className={styles.emptyText}>暂无个人计划</Text>
            <Text className={styles.emptyHint}>开始制定您的第一个计划吧</Text>
          </View>
        ) : (
          <>
            {plans.map(plan => (
              <View key={plan.id} className={styles.planCard}>
                <View className={styles.planHeader}>
                  <View className={styles.planIcon}>
                    <Text>{getTypeIcon(plan.plan_type)}</Text>
                  </View>
                  <View className={styles.planInfo}>
                    <Text className={styles.planTitle}>{plan.title}</Text>
                    <Text className={styles.planTime}>
                      {formatTimeRange(plan.start_time, plan.end_time)}
                    </Text>
                  </View>
                  <Text className={classnames(styles.statusBadge, getStatusClass(plan.status))}>
                    {getStatusLabel(plan.status)}
                  </Text>
                </View>

                <View className={styles.progressSection}>
                  <View className={styles.progressHeader}>
                    <Text className={styles.progressLabel}>完成进度</Text>
                    <Text className={styles.progressValue}>{plan.progress}%</Text>
                  </View>
                  <View className={styles.progressBar}>
                    <View
                      className={styles.progressFill}
                      style={{ width: `${plan.progress}%` }}
                    />
                  </View>
                </View>

                <View className={styles.planFooter}>
                  <View className={styles.typeTag}>
                    <Text>{getTypeLabel(plan.plan_type)}</Text>
                  </View>
                </View>
              </View>
            ))}
          </>
        )}
      </ScrollView>
    </View>
  );
};

export default PersonalPlanPage;
