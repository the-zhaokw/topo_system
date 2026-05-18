import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockTestSuite } from '../../data/testManagement';

const TestSuiteListPage: React.FC = () => {
  const [suiteList] = useState(mockTestSuite);

  return (
    <ScrollView className={styles.container} scrollY>
      {suiteList.map((suite, index) => (
        <View
          key={index}
          className={styles.suiteItem}
          onClick={() => Taro.navigateTo({ url: `/pages/test-suite-detail/index?id=${suite.id}` })}
        >
          <View className={styles.suiteHeader}>
            <Text className={styles.suiteName}>{suite.suiteName}</Text>
            <Text className={styles.passRate}>{suite.passRate}%</Text>
          </View>
          <Text className={styles.suiteInfo}>项目: {suite.projectName}</Text>
          <Text className={styles.suiteInfo}>模块: {suite.module}</Text>
          <Text className={styles.suiteInfo}>用例数: {suite.caseCount}</Text>
          <View className={styles.progressBar}>
            <View
              className={styles.progressFill}
              style={{ width: `${suite.passRate}%` }}
            />
          </View>
        </View>
      ))}
    </ScrollView>
  );
};

export default TestSuiteListPage;
