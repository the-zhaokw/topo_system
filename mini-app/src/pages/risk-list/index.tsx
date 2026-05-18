import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';
import { mockRisk } from '../../data/business';

const RiskListPage: React.FC = () => {
  const [riskList] = useState(mockRisk);

  const getLevelClass = (level: string) => {
    switch (level) {
      case '严重':
        return styles.levelSerious;
      case '高':
        return styles.levelHigh;
      case '中':
        return styles.levelMedium;
      case '低':
        return styles.levelLow;
      default:
        return '';
    }
  };

  return (
    <ScrollView className={styles.container} scrollY>
      {riskList.map((risk, index) => (
        <View key={index} className={styles.riskItem}>
          <View className={styles.riskHeader}>
            <Text className={styles.riskNo}>{risk.riskNo}</Text>
            <Text className={`${styles.levelTag} ${getLevelClass(risk.level)}`}>
              {risk.level}
            </Text>
          </View>
          <Text className={styles.riskName}>{risk.riskName}</Text>
          <Text className={styles.riskInfo}>项目: {risk.projectName}</Text>
          <Text className={styles.riskInfo}>类别: {risk.category}</Text>
          <Text className={styles.riskInfo}>概率: {risk.probability} | 影响: {risk.impact}</Text>
          <Text className={styles.riskInfo}>状态: {risk.status}</Text>
          <Text className={styles.riskInfo}>负责人: {risk.owner}</Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default RiskListPage;
