import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockProjectStatistics } from '../../data/project';

const ProjectStatisticsPage: React.FC = () => {
  const [statistics, setStatistics] = useState(mockProjectStatistics);

  useEffect(() => {
    Taro.setNavigationBarTitle({ title: '项目统计' });
  }, []);

  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>项目概览</Text>
        <View className={styles.statsGrid}>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>{statistics.totalProjects}</Text>
            <Text className={styles.statLabel}>总项目数</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#22C55E' }}>
              {statistics.ongoingProjects}
            </Text>
            <Text className={styles.statLabel}>进行中</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#3B82F6' }}>
              {statistics.completedProjects}
            </Text>
            <Text className={styles.statLabel}>已完成</Text>
          </View>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>项目进度</Text>
        <View style={{ marginBottom: '24rpx' }}>
          <View style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8rpx' }}>
            <Text style={{ fontSize: '28rpx', color: '#64748B' }}>平均进度</Text>
            <Text style={{ fontSize: '28rpx', color: '#1E293B', fontWeight: '600' }}>
              {statistics.averageProgress}%
            </Text>
          </View>
          <View className={styles.progressBar}>
            <View
              className={styles.progressFill}
              style={{ width: `${statistics.averageProgress}%` }}
            />
          </View>
        </View>

        <View style={{ marginBottom: '24rpx' }}>
          <View style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8rpx' }}>
            <Text style={{ fontSize: '28rpx', color: '#64748B' }}>总预算</Text>
            <Text style={{ fontSize: '28rpx', color: '#1E293B', fontWeight: '600' }}>
              ¥{(statistics.totalBudget / 10000).toFixed(0)}万
            </Text>
          </View>
        </View>

        <View>
          <View style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8rpx' }}>
            <Text style={{ fontSize: '28rpx', color: '#64748B' }}>已消耗</Text>
            <Text style={{ fontSize: '28rpx', color: '#F59E0B', fontWeight: '600' }}>
              ¥{(statistics.totalSpent / 10000).toFixed(0)}万
            </Text>
          </View>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>项目类型分布</Text>
        {statistics.projectTypeDistribution.map((item, index) => (
          <View key={index} style={{ marginBottom: '24rpx' }}>
            <View style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8rpx' }}>
              <Text style={{ fontSize: '28rpx', color: '#64748B' }}>{item.type}</Text>
              <Text style={{ fontSize: '28rpx', color: '#1E293B' }}>{item.count}个</Text>
            </View>
            <View style={{ height: '8rpx', background: '#E2E8F0', borderRadius: '4rpx', overflow: 'hidden' }}>
              <View style={{ width: `${item.percentage}%`, height: '100%', background: '#4F46E5', borderRadius: '4rpx' }} />
            </View>
          </View>
        ))}
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>项目状态分布</Text>
        {statistics.projectStatusDistribution.map((item, index) => (
          <View key={index} style={{ marginBottom: '24rpx' }}>
            <View style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8rpx' }}>
              <Text style={{ fontSize: '28rpx', color: '#64748B' }}>{item.status}</Text>
              <Text style={{ fontSize: '28rpx', color: '#1E293B' }}>{item.count}个</Text>
            </View>
            <View style={{ height: '8rpx', background: '#E2E8F0', borderRadius: '4rpx', overflow: 'hidden' }}>
              <View style={{ width: `${item.percentage}%`, height: '100%', background: '#6366F1', borderRadius: '4rpx' }} />
            </View>
          </View>
        ))}
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>资源利用率</Text>
        {statistics.resourceUtilization.map((item, index) => (
          <View key={index} style={{ marginBottom: '24rpx' }}>
            <View style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8rpx' }}>
              <Text style={{ fontSize: '28rpx', color: '#64748B' }}>{item.resourceName}</Text>
              <Text style={{ fontSize: '28rpx', color: '#1E293B', fontWeight: '600' }}>
                {item.utilizationRate}%
              </Text>
            </View>
            <View style={{ height: '8rpx', background: '#E2E8F0', borderRadius: '4rpx', overflow: 'hidden' }}>
              <View style={{ width: `${item.utilizationRate}%`, height: '100%', background: '#22C55E', borderRadius: '4rpx' }} />
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

export default ProjectStatisticsPage;
