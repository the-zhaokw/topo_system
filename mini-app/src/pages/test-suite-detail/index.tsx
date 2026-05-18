import React from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';

const TestSuiteDetailPage: React.FC = () => {
  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>基本信息</Text>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>套件名称</Text>
          <Text className={styles.infoValue}>用户管理模块</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>所属项目</Text>
          <Text className={styles.infoValue}>TOPO系统</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>所属模块</Text>
          <Text className={styles.infoValue}>用户模块</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>用例数量</Text>
          <Text className={styles.infoValue}>156</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>通过率</Text>
          <Text className={styles.infoValue} style={{ color: '#22C55E' }}>86.1%</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>最后执行</Text>
          <Text className={styles.infoValue}>2026-05-18 10:30</Text>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>描述</Text>
        <Text style={{ fontSize: '28rpx', color: '#64748B', lineHeight: '1.6' }}>
          包含用户注册、登录、权限管理等功能测试
        </Text>
      </View>
    </ScrollView>
  );
};

export default TestSuiteDetailPage;
