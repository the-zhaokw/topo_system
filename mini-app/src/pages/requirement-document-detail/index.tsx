import React from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';

const RequirementDocumentDetailPage: React.FC = () => {
  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>文档信息</Text>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>文档编号</Text>
          <Text className={styles.infoValue}>RD-2026-001</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>文档名称</Text>
          <Text className={styles.infoValue}>TOPO系统需求规格说明书</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>版本</Text>
          <Text className={styles.infoValue}>V2.1</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>所属项目</Text>
          <Text className={styles.infoValue}>TOPO系统</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>所属模块</Text>
          <Text className={styles.infoValue}>整体架构</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>需求数量</Text>
          <Text className={styles.infoValue}>156</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>作者</Text>
          <Text className={styles.infoValue}>需求分析师A</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>状态</Text>
          <Text className={styles.infoValue} style={{ color: '#22C55E' }}>已发布</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>创建时间</Text>
          <Text className={styles.infoValue}>2026-01-15</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>更新时间</Text>
          <Text className={styles.infoValue}>2026-05-10</Text>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>描述</Text>
        <Text style={{ fontSize: '28rpx', color: '#64748B', lineHeight: '1.6' }}>
          TOPO系统整体需求规格说明
        </Text>
      </View>
    </ScrollView>
  );
};

export default RequirementDocumentDetailPage;
