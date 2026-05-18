import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockTestDashboard } from '../../data/testManagement';

const TestDashboardPage: React.FC = () => {
  const [dashboard] = useState(mockTestDashboard);

  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>测试概览</Text>
        <View className={styles.statsGrid}>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>{dashboard.totalCases}</Text>
            <Text className={styles.statLabel}>总用例数</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#22C55E' }}>
              {dashboard.passRate.toFixed(1)}%
            </Text>
            <Text className={styles.statLabel}>通过率</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#22C55E' }}>
              {dashboard.passedCases}
            </Text>
            <Text className={styles.statLabel}>通过</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#F43F5E' }}>
              {dashboard.failedCases}
            </Text>
            <Text className={styles.statLabel}>失败</Text>
          </View>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>测试套件统计</Text>
        <Text style={{ fontSize: '48rpx', fontWeight: 'bold', color: '#4F46E5', marginBottom: '16rpx' }}>
          {dashboard.totalSuites}
        </Text>
        <Text style={{ fontSize: '24rpx', color: '#64748B' }}>测试套件总数</Text>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>最新执行</Text>
        {dashboard.recentExecutions.map((execution, index) => (
          <View key={index} style={{ marginBottom: '24rpx', padding: '16rpx', background: '#F8FAFC', borderRadius: '8rpx' }}>
            <Text style={{ fontSize: '28rpx', fontWeight: '600', color: '#1E293B' }}>
              {execution.suiteName}
            </Text>
            <Text style={{ fontSize: '24rpx', color: '#64748B', display: 'block', marginTop: '8rpx' }}>
              执行人: {execution.executedBy}
            </Text>
            <Text style={{ fontSize: '24rpx', color: '#64748B' }}>
              执行时间: {execution.executedAt}
            </Text>
            <Text style={{ fontSize: '24rpx', color: '#22C55E', fontWeight: '600' }}>
              通过率: {execution.passRate}%
            </Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

export default TestDashboardPage;
