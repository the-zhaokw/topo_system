import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';
import { mockWorkStatistics } from '../../data/business';

const WorkStatisticsPage: React.FC = () => {
  const [statistics] = useState(mockWorkStatistics);

  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>工作时长统计</Text>
        <View className={styles.statsGrid}>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>{statistics.totalHours}</Text>
            <Text className={styles.statLabel}>总时长(小时)</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#22C55E' }}>
              {statistics.normalHours}
            </Text>
            <Text className={styles.statLabel}>正常工时</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#F59E0B' }}>
              {statistics.overtimeHours}
            </Text>
            <Text className={styles.statLabel}>加班时长</Text>
          </View>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>项目分布</Text>
        {statistics.projectDistribution.map((item, index) => (
          <View key={index} style={{ marginBottom: '24rpx' }}>
            <View style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8rpx' }}>
              <Text style={{ fontSize: '28rpx', color: '#64748B' }}>{item.projectName}</Text>
              <Text style={{ fontSize: '28rpx', color: '#1E293B' }}>{item.hours}小时</Text>
            </View>
            <View style={{ height: '8rpx', background: '#E2E8F0', borderRadius: '4rpx', overflow: 'hidden' }}>
              <View style={{ width: `${item.percentage}%`, height: '100%', background: '#4F46E5', borderRadius: '4rpx' }} />
            </View>
          </View>
        ))}
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>月度汇总</Text>
        {statistics.monthlySummary.map((item, index) => (
          <View key={index} style={{ marginBottom: '24rpx', padding: '16rpx', background: '#F8FAFC', borderRadius: '8rpx' }}>
            <Text style={{ fontSize: '28rpx', fontWeight: '600', color: '#1E293B' }}>
              {item.month}
            </Text>
            <Text style={{ fontSize: '24rpx', color: '#64748B', display: 'block', marginTop: '8rpx' }}>
              正常工时: {item.normalHours}h | 加班: {item.overtimeHours}h | 合计: {item.totalHours}h
            </Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

export default WorkStatisticsPage;
