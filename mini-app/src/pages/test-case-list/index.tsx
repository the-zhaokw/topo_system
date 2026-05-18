import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockTestCase } from '../../data/testManagement';

const TestCaseListPage: React.FC = () => {
  const [caseList] = useState(mockTestCase);

  const getPriorityClass = (priority: string) => {
    switch (priority) {
      case 'P0':
        return styles.priorityP0;
      case 'P1':
        return styles.priorityP1;
      case 'P2':
        return styles.priorityP2;
      default:
        return '';
    }
  };

  return (
    <ScrollView className={styles.container} scrollY>
      {caseList.map((testCase, index) => (
        <View
          key={index}
          className={styles.caseItem}
          onClick={() => Taro.navigateTo({ url: `/pages/test-case-detail/index?id=${testCase.id}` })}
        >
          <View className={styles.caseHeader}>
            <Text className={styles.caseNo}>{testCase.caseNo}</Text>
            <Text className={`${styles.priorityTag} ${getPriorityClass(testCase.priority)}`}>
              {testCase.priority}
            </Text>
          </View>
          <Text className={styles.caseName}>{testCase.caseName}</Text>
          <Text className={styles.caseInfo}>类型: {testCase.type}</Text>
          <Text className={styles.caseInfo}>状态: {testCase.status}</Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default TestCaseListPage;
