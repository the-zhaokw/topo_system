import React from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';

const ContractDetailPage: React.FC = () => {
  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>基本信息</Text>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>合同编号</Text>
          <Text className={styles.infoValue}>HT-2026-001</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>合同名称</Text>
          <Text className={styles.infoValue}>TOPO系统开发合同</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>甲方</Text>
          <Text className={styles.infoValue}>XX科技有限公司</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>乙方</Text>
          <Text className={styles.infoValue}>我们的公司</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>合同金额</Text>
          <Text className={styles.infoValue}>¥500,000</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>签订日期</Text>
          <Text className={styles.infoValue}>2026-01-15</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>合同状态</Text>
          <Text className={styles.infoValue}>执行中</Text>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>时间信息</Text>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>开始日期</Text>
          <Text className={styles.infoValue}>2026-01-20</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>结束日期</Text>
          <Text className={styles.infoValue}>2026-12-31</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>负责人</Text>
          <Text className={styles.infoValue}>张三</Text>
        </View>
      </View>
    </ScrollView>
  );
};

export default ContractDetailPage;
