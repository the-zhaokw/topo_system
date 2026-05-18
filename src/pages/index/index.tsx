import React from 'react';
import { View, Text, Image } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';

const Index: React.FC = () => {
  const handleClick = () => {
    Taro.navigateTo({ url: '/pages/bug-statistics/index' });
  };

  return (
    <View className={styles.container}>
      <View className={styles.card}>
        <Text className={styles.logo}>🎉</Text>
        <Text className={styles.welcome}>欢迎使用 Bug 统计小程序</Text>
        <Text className={styles.desc}>全面分析Bug数据，洞察项目质量</Text>
        <View className={styles.button} onClick={handleClick}>
          <Text className={styles.buttonText}>进入统计看板</Text>
        </View>
      </View>
    </View>
  );
};

export default Index;
