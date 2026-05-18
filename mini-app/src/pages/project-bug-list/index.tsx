import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockProjectBug } from '../../data/project';

const ProjectBugListPage: React.FC = () => {
  const [bugList, setBugList] = useState(mockProjectBug);

  useEffect(() => {
    Taro.setNavigationBarTitle({ title: '项目Bug列表' });
  }, []);

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case '严重':
        return styles.severityCritical;
      case '高':
        return styles.severityHigh;
      case '中':
        return styles.severityMedium;
      case '低':
        return styles.severityLow;
      default:
        return '';
    }
  };

  return (
    <ScrollView className={styles.container} scrollY>
      {bugList.map((bug, index) => (
        <View
          key={index}
          className={styles.bugItem}
          onClick={() => Taro.navigateTo({ url: `/pages/bug-detail/index?id=${bug.id}` })}
        >
          <View className={styles.bugHeader}>
            <Text className={styles.bugNo}>{bug.bugNo}</Text>
            <View>
              <Text className={`${styles.severityTag} ${getSeverityClass(bug.severity)}`}>
                {bug.severity}
              </Text>
            </View>
          </View>
          <Text className={styles.bugName}>{bug.bugName}</Text>
          <View className={styles.bugInfo}>
            <Text style={{ marginRight: '32rpx' }}>状态: {bug.status}</Text>
            <Text>创建时间: {bug.createTime}</Text>
          </View>
        </View>
      ))}
    </ScrollView>
  );
};

export default ProjectBugListPage;
