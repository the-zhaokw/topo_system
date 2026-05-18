import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockTestExecution } from '../../data/testManagement';

const TestExecutionPage: React.FC = () => {
  const [executionList] = useState(mockTestExecution);

  return (
    <ScrollView className={styles.container} scrollY>
      {executionList.map((execution, index) => (
        <View
          key={index}
          className={styles.executionItem}
          onClick={() => Taro.navigateTo({ url: `/pages/test-report/index?id=${execution.id}` })}
        >
          <Text className={styles.executionNo}>{execution.executionNo}</Text>
          <Text className={styles.executionInfo}>测试套件: {execution.suiteName}</Text>
          <Text className={styles.executionInfo}>执行人: {execution.executedBy}</Text>
          <Text className={styles.executionInfo}>执行时间: {execution.executedAt}</Text>
          <Text className={styles.executionInfo}>环境: {execution.environment}</Text>
          <Text className={styles.executionInfo}>总用例: {execution.totalCases}</Text>
          <Text className={styles.executionInfo}>通过: {execution.passedCases} | 失败: {execution.failedCases}</Text>
          <Text className={styles.passRate}>通过率: {execution.passRate}%</Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default TestExecutionPage;
