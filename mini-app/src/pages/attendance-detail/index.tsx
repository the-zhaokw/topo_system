import React from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';

const AttendanceDetailPage: React.FC = () => {
  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>打卡信息</Text>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>打卡日期</Text>
          <Text className={styles.infoValue}>2026-05-18</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>上班打卡</Text>
          <Text className={styles.infoValue}>08:30</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>下班打卡</Text>
          <Text className={styles.infoValue}>17:45</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>工作时长</Text>
          <Text className={styles.infoValue}>8.5小时</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>打卡状态</Text>
          <Text className={styles.infoValue}>正常</Text>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>打卡地点</Text>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>上班地点</Text>
          <Text className={styles.infoValue}>公司总部</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>下班地点</Text>
          <Text className={styles.infoValue}>公司总部</Text>
        </View>
      </View>
    </ScrollView>
  );
};

export default AttendanceDetailPage;
