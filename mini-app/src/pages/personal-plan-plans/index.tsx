import React from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';

const PersonalPlanPlansPage: React.FC = () => {
  const plans = [
    { title: 'TOPO系统v2.0开发', time: '2026-05-01 至 2026-05-31', progress: 75, status: '进行中' },
    { title: '合同管理模块优化', time: '2026-05-10 至 2026-05-20', progress: 100, status: '已完成' },
    { title: '物料追踪功能开发', time: '2026-05-15 至 2026-06-15', progress: 30, status: '进行中' },
    { title: '系统性能优化', time: '2026-06-01 至 2026-06-30', progress: 0, status: '待开始' }
  ];

  const getStatusClass = (status: string) => {
    switch (status) {
      case '已完成':
        return styles.statusCompleted;
      case '进行中':
        return styles.statusInProgress;
      case '待开始':
        return styles.statusPending;
      default:
        return '';
    }
  };

  return (
    <ScrollView className={styles.container} scrollY>
      {plans.map((plan, index) => (
        <View key={index} className={styles.planItem}>
          <View className={styles.planHeader}>
            <Text className={styles.planTitle}>{plan.title}</Text>
            <Text className={`${styles.statusTag} ${getStatusClass(plan.status)}`}>
              {plan.status}
            </Text>
          </View>
          <Text className={styles.planTime}>{plan.time}</Text>
          <View className={styles.progressBar}>
            <View
              className={styles.progressFill}
              style={{ width: `${plan.progress}%` }}
            />
          </View>
          <Text style={{ fontSize: '24rpx', color: '#64748B' }}>
            进度: {plan.progress}%
          </Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default PersonalPlanPlansPage;
