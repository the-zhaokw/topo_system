import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockContractStatistics } from '../../data/contract';

const ContractStatisticsPage: React.FC = () => {
  const [statistics] = useState(mockContractStatistics);

  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>合同概览</Text>
        <View className={styles.statsGrid}>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>{statistics.totalCount}</Text>
            <Text className={styles.statLabel}>总合同数</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>{(statistics.totalAmount / 10000).toFixed(0)}万</Text>
            <Text className={styles.statLabel}>总金额</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#22C55E' }}>{statistics.executingCount}</Text>
            <Text className={styles.statLabel}>执行中</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#3B82F6' }}>{statistics.completedCount}</Text>
            <Text className={styles.statLabel}>已完成</Text>
          </View>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>合同类型分布</Text>
        {statistics.typeDistribution.map((item, index) => (
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
        <Text className={styles.cardTitle}>合同金额分布</Text>
        {statistics.amountDistribution.map((item, index) => (
          <View key={index} style={{ marginBottom: '24rpx' }}>
            <View style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8rpx' }}>
              <Text style={{ fontSize: '28rpx', color: '#64748B' }}>{item.range}</Text>
              <Text style={{ fontSize: '28rpx', color: '#1E293B' }}>{item.count}个</Text>
            </View>
            <View style={{ height: '8rpx', background: '#E2E8F0', borderRadius: '4rpx', overflow: 'hidden' }}>
              <View style={{ width: `${item.percentage}%`, height: '100%', background: '#6366F1', borderRadius: '4rpx' }} />
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

export default ContractStatisticsPage;
