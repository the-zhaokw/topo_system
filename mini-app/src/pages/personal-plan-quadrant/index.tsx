import React from 'react';
import { View, Text } from '@tarojs/components';
import styles from './index.module.scss';

const PersonalPlanQuadrantPage: React.FC = () => {
  return (
    <View className={styles.container}>
      <View className={styles.placeholder}>
        <Text style={{ fontSize: '64rpx' }}>🎯</Text>
        <Text className={styles.placeholderText}>四象限视图</Text>
        <Text style={{ fontSize: '24rpx', color: '#94A3B8', marginTop: '16rpx' }}>功能正在开发中...</Text>
      </View>
    </View>
  );
};

export default PersonalPlanQuadrantPage;
