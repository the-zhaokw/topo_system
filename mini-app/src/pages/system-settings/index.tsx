import React from 'react';
import { View, Text } from '@tarojs/components';
import styles from './index.module.scss';

const SystemSettingsPage: React.FC = () => {
  return (
    <View className={styles.container}>
      <View className={styles.placeholder}>
        <Text style={{ fontSize: '64rpx' }}>⚙️</Text>
        <Text className={styles.placeholderText}>系统设置</Text>
        <Text className={styles.placeholderHint}>功能正在开发中...</Text>
      </View>
    </View>
  );
};

export default SystemSettingsPage;
