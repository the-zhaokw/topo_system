import React from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';

const PersonalPlanDashboardPage: React.FC = () => {
  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>今日概览</Text>
        <View className={styles.statsGrid}>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>5</Text>
            <Text className={styles.statLabel}>待办任务</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#22C55E' }}>3</Text>
            <Text className={styles.statLabel}>已完成</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#3B82F6' }}>2</Text>
            <Text className={styles.statLabel}>进行中</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#F59E0B' }}>8h</Text>
            <Text className={styles.statLabel}>计划时长</Text>
          </View>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>本周进度</Text>
        <View style={{ display: 'flex', justifyContent: 'space-around', marginTop: '24rpx' }}>
          {['一', '二', '三', '四', '五', '六', '日'].map((day, index) => (
            <View key={index} style={{ textAlign: 'center' }}>
              <Text style={{ fontSize: '24rpx', color: '#64748B' }}>{day}</Text>
              <View style={{
                width: '60rpx',
                height: '60rpx',
                background: index < 4 ? '#4F46E5' : '#E2E8F0',
                borderRadius: '50%',
                marginTop: '8rpx',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Text style={{ fontSize: '24rpx', color: index < 4 ? '#fff' : '#64748B' }}>
                  {index + 1}
                </Text>
              </View>
            </View>
          ))}
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>快速操作</Text>
        <View style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '24rpx', marginTop: '24rpx' }}>
          <View style={{ padding: '24rpx', background: '#F8FAFC', borderRadius: '12rpx', textAlign: 'center' }}>
            <Text style={{ fontSize: '48rpx' }}>📝</Text>
            <Text style={{ fontSize: '28rpx', color: '#1E293B', display: 'block', marginTop: '8rpx' }}>新建任务</Text>
          </View>
          <View style={{ padding: '24rpx', background: '#F8FAFC', borderRadius: '12rpx', textAlign: 'center' }}>
            <Text style={{ fontSize: '48rpx' }}>📅</Text>
            <Text style={{ fontSize: '28rpx', color: '#1E293B', display: 'block', marginTop: '8rpx' }}>查看日历</Text>
          </View>
          <View style={{ padding: '24rpx', background: '#F8FAFC', borderRadius: '12rpx', textAlign: 'center' }}>
            <Text style={{ fontSize: '48rpx' }}>📊</Text>
            <Text style={{ fontSize: '28rpx', color: '#1E293B', display: 'block', marginTop: '8rpx' }}>统计数据</Text>
          </View>
          <View style={{ padding: '24rpx', background: '#F8FAFC', borderRadius: '12rpx', textAlign: 'center' }}>
            <Text style={{ fontSize: '48rpx' }}>🎯</Text>
            <Text style={{ fontSize: '28rpx', color: '#1E293B', display: 'block', marginTop: '8rpx' }}>专注模式</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

export default PersonalPlanDashboardPage;
