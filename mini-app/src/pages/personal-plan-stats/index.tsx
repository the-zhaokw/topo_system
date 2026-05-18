import React from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';

const PersonalPlanStatsPage: React.FC = () => {
  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>计划完成统计</Text>
        <View className={styles.statsGrid}>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>12</Text>
            <Text className={styles.statLabel}>本月计划</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#22C55E' }}>9</Text>
            <Text className={styles.statLabel}>已完成</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#3B82F6' }}>2</Text>
            <Text className={styles.statLabel}>进行中</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#F59E0B' }}>75%</Text>
            <Text className={styles.statLabel}>完成率</Text>
          </View>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>本周趋势</Text>
        <View style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '8rpx', textAlign: 'center' }}>
          {['一', '二', '三', '四', '五', '六', '日'].map((day, index) => (
            <View key={index}>
              <Text style={{ fontSize: '24rpx', color: '#64748B' }}>{day}</Text>
              <View style={{
                width: '60rpx',
                height: '60rpx',
                background: index < 5 ? '#4F46E5' : '#E2E8F0',
                borderRadius: '8rpx',
                marginTop: '8rpx',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Text style={{ fontSize: '24rpx', color: index < 5 ? '#fff' : '#64748B' }}>
                  {index + 1}
                </Text>
              </View>
            </View>
          ))}
        </View>
      </View>
    </ScrollView>
  );
};

export default PersonalPlanStatsPage;
