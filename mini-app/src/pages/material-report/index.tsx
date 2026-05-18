import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockMaterialReport } from '../../data/material';

const MaterialReportPage: React.FC = () => {
  const [report] = useState(mockMaterialReport);

  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>物料概览</Text>
        <View className={styles.statsGrid}>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>{report.totalMaterials}</Text>
            <Text className={styles.statLabel}>物料种类</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>{(report.totalValue / 10000).toFixed(0)}万</Text>
            <Text className={styles.statLabel}>总价值</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#F59E0B' }}>{report.lowStockCount}</Text>
            <Text className={styles.statLabel}>库存不足</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#F43F5E' }}>{report.outOfStockCount}</Text>
            <Text className={styles.statLabel}>缺货</Text>
          </View>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>分类分布</Text>
        {report.categoryDistribution.map((item, index) => (
          <View key={index} style={{ marginBottom: '24rpx' }}>
            <View style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8rpx' }}>
              <Text style={{ fontSize: '28rpx', color: '#64748B' }}>{item.categoryName}</Text>
              <Text style={{ fontSize: '28rpx', color: '#1E293B' }}>{item.count}种</Text>
            </View>
            <View style={{ height: '8rpx', background: '#E2E8F0', borderRadius: '4rpx', overflow: 'hidden' }}>
              <View style={{ width: `${(item.value / report.totalValue) * 100}%`, height: '100%', background: '#4F46E5', borderRadius: '4rpx' }} />
            </View>
          </View>
        ))}
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>仓库分布</Text>
        {report.warehouseDistribution.map((item, index) => (
          <View key={index} style={{ marginBottom: '24rpx' }}>
            <View style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8rpx' }}>
              <Text style={{ fontSize: '28rpx', color: '#64748B' }}>{item.warehouseName}</Text>
              <Text style={{ fontSize: '28rpx', color: '#1E293B' }}>{item.count}种</Text>
            </View>
            <View style={{ height: '8rpx', background: '#E2E8F0', borderRadius: '4rpx', overflow: 'hidden' }}>
              <View style={{ width: `${(item.value / report.totalValue) * 100}%`, height: '100%', background: '#6366F1', borderRadius: '4rpx' }} />
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

export default MaterialReportPage;
