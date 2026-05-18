import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockRequirementDashboard } from '../../data/requirement';

const RequirementDashboardPage: React.FC = () => {
  const [dashboard] = useState(mockRequirementDashboard);

  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>需求概览</Text>
        <View className={styles.statsGrid}>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>{dashboard.totalRequirements}</Text>
            <Text className={styles.statLabel}>总需求</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#22C55E' }}>
              {dashboard.implementedRequirements}
            </Text>
            <Text className={styles.statLabel}>已实现</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#3B82F6' }}>
              {dashboard.releasedRequirements}
            </Text>
            <Text className={styles.statLabel}>已发布</Text>
          </View>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>需求状态分布</Text>
        {dashboard.statusDistribution.map((item, index) => (
          <View key={index} style={{ marginBottom: '24rpx' }}>
            <View style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8rpx' }}>
              <Text style={{ fontSize: '28rpx', color: '#64748B' }}>{item.status}</Text>
              <Text style={{ fontSize: '28rpx', color: '#1E293B' }}>{item.count}</Text>
            </View>
            <View style={{ height: '8rpx', background: '#E2E8F0', borderRadius: '4rpx', overflow: 'hidden' }}>
              <View style={{ width: `${item.percentage}%`, height: '100%', background: '#4F46E5', borderRadius: '4rpx' }} />
            </View>
          </View>
        ))}
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>最新更新</Text>
        {dashboard.recentUpdates.map((item, index) => (
          <View key={index} style={{ marginBottom: '24rpx', padding: '16rpx', background: '#F8FAFC', borderRadius: '8rpx' }}>
            <Text style={{ fontSize: '28rpx', fontWeight: '600', color: '#1E293B' }}>
              {item.requirementName}
            </Text>
            <Text style={{ fontSize: '24rpx', color: '#64748B', display: 'block', marginTop: '8rpx' }}>
              {item.projectName} | {item.updatedBy}
            </Text>
            <Text style={{ fontSize: '24rpx', color: '#94A3B8' }}>
              {item.updatedAt}
            </Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

export default RequirementDashboardPage;
