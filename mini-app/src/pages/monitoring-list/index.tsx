import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';
import { mockMonitoringItem } from '../../data/business';

const MonitoringListPage: React.FC = () => {
  const [monitorList] = useState(mockMonitoringItem);

  const getStatusClass = (status: string) => {
    switch (status) {
      case '正常':
        return styles.statusNormal;
      case '警告':
        return styles.statusWarning;
      case '异常':
        return styles.statusError;
      default:
        return '';
    }
  };

  return (
    <ScrollView className={styles.container} scrollY>
      {monitorList.map((monitor, index) => (
        <View key={index} className={styles.monitorItem}>
          <View className={styles.monitorHeader}>
            <Text className={styles.monitorName}>{monitor.monitorName}</Text>
            <Text className={`${styles.statusTag} ${getStatusClass(monitor.status)}`}>
              {monitor.status}
            </Text>
          </View>
          <Text className={styles.monitorInfo}>类型: {monitor.monitorType}</Text>
          <Text className={styles.monitorInfo}>最后检查: {monitor.lastCheckTime}</Text>
          <Text className={styles.monitorInfo}>阈值: {monitor.threshold}</Text>
          <Text className={styles.monitorValue}>{monitor.value}</Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default MonitoringListPage;
