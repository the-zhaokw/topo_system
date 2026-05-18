import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockBugStatistics } from '../../data/bugStatistics';

const BugStatisticsPage: React.FC = () => {
  const [statistics, setStatistics] = useState(mockBugStatistics);

  useEffect(() => {
    Taro.setNavigationBarTitle({ title: 'Bug统计' });
  }, []);

  const handleCardClick = (type: string) => {
    switch (type) {
      case 'open':
        Taro.navigateTo({ url: '/pages/bug-list/index?status=open' });
        break;
      case 'inProgress':
        Taro.navigateTo({ url: '/pages/bug-list/index?status=inProgress' });
        break;
      case 'resolved':
        Taro.navigateTo({ url: '/pages/bug-list/index?status=resolved' });
        break;
      case 'closed':
        Taro.navigateTo({ url: '/pages/bug-list/index?status=closed' });
        break;
    }
  };

  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>Bug概览</Text>
        <View className={styles.statsGrid}>
          <View className={styles.statItem} onClick={() => handleCardClick('open')}>
            <Text className={styles.statValue}>{statistics.open}</Text>
            <Text className={styles.statLabel}>待处理</Text>
          </View>
          <View className={styles.statItem} onClick={() => handleCardClick('inProgress')}>
            <Text className={styles.statValue}>{statistics.inProgress}</Text>
            <Text className={styles.statLabel}>处理中</Text>
          </View>
          <View className={styles.statItem} onClick={() => handleCardClick('resolved')}>
            <Text className={styles.statValue}>{statistics.resolved}</Text>
            <Text className={styles.statLabel}>已解决</Text>
          </View>
          <View className={styles.statItem} onClick={() => handleCardClick('closed')}>
            <Text className={styles.statValue}>{statistics.closed}</Text>
            <Text className={styles.statLabel}>已关闭</Text>
          </View>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>优先级分布</Text>
        <View className={styles.statsGrid}>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#F43F5E' }}>
              {statistics.criticalCount}
            </Text>
            <Text className={styles.statLabel}>严重</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#F59E0B' }}>
              {statistics.highCount}
            </Text>
            <Text className={styles.statLabel}>高</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#3B82F6' }}>
              {statistics.mediumCount}
            </Text>
            <Text className={styles.statLabel}>中</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#22C55E' }}>
              {statistics.lowCount}
            </Text>
            <Text className={styles.statLabel}>低</Text>
          </View>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>今日统计</Text>
        <View className={styles.statsGrid}>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#4F46E5' }}>
              {statistics.todayCreated}
            </Text>
            <Text className={styles.statLabel}>新增</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#22C55E' }}>
              {statistics.todayResolved}
            </Text>
            <Text className={styles.statLabel}>解决</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>{statistics.total}</Text>
            <Text className={styles.statLabel}>总计</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>
              {Math.round((statistics.resolved / statistics.total) * 100)}%
            </Text>
            <Text className={styles.statLabel}>解决率</Text>
          </View>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>项目分布</Text>
        {statistics.projectDistribution.map((item, index) => (
          <View key={index} style={{ marginBottom: '16rpx' }}>
            <View style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8rpx' }}>
              <Text style={{ fontSize: '24rpx', color: '#64748B' }}>{item.projectName}</Text>
              <Text style={{ fontSize: '24rpx', color: '#1E293B' }}>{item.count}个</Text>
            </View>
            <View style={{
              height: '8rpx',
              background: '#E2E8F0',
              borderRadius: '4rpx',
              overflow: 'hidden'
            }}>
              <View style={{
                width: `${item.percentage}%`,
                height: '100%',
                background: '#4F46E5',
                borderRadius: '4rpx'
              }} />
            </View>
          </View>
        ))}
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>状态分布</Text>
        {statistics.statusDistribution.map((item, index) => (
          <View key={index} style={{ marginBottom: '16rpx' }}>
            <View style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8rpx' }}>
              <Text style={{ fontSize: '24rpx', color: '#64748B' }}>{item.status}</Text>
              <Text style={{ fontSize: '24rpx', color: '#1E293B' }}>{item.count}个 ({item.percentage}%)</Text>
            </View>
            <View style={{
              height: '8rpx',
              background: '#E2E8F0',
              borderRadius: '4rpx',
              overflow: 'hidden'
            }}>
              <View style={{
                width: `${item.percentage}%`,
                height: '100%',
                background: index % 2 === 0 ? '#6366F1' : '#4F46E5',
                borderRadius: '4rpx'
              }} />
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

export default BugStatisticsPage;
