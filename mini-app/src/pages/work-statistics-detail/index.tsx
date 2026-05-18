import React from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';

const WorkStatisticsDetailPage: React.FC = () => {
  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>工作时长统计</Text>
        <View className={styles.statsGrid}>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>168</Text>
            <Text className={styles.statLabel}>本月总时长(h)</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#22C55E' }}>160</Text>
            <Text className={styles.statLabel}>正常工时(h)</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#F59E0B' }}>8</Text>
            <Text className={styles.statLabel}>加班时长(h)</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#3B82F6' }}>8.0</Text>
            <Text className={styles.statLabel}>日均时长(h)</Text>
          </View>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>详细信息</Text>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>统计周期</Text>
          <Text className={styles.infoValue}>2026年5月</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>出勤天数</Text>
          <Text className={styles.infoValue}>20天</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>项目数</Text>
          <Text className={styles.infoValue}>3个</Text>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>项目分布</Text>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>TOPO系统</Text>
          <Text className={styles.infoValue}>80小时 (47.6%)</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>合同管理系统</Text>
          <Text className={styles.infoValue}>45小时 (26.8%)</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>物料追踪系统</Text>
          <Text className={styles.infoValue}>43小时 (25.6%)</Text>
        </View>
      </View>
    </ScrollView>
  );
};

export default WorkStatisticsDetailPage;
