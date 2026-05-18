import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockProjectLog } from '../../data/project';

const ProjectLogListPage: React.FC = () => {
  const [logList, setLogList] = useState(mockProjectLog);

  useEffect(() => {
    Taro.setNavigationBarTitle({ title: '项目日志' });
  }, []);

  return (
    <ScrollView className={styles.container} scrollY>
      {logList.map((log, index) => (
        <View key={index} className={styles.logItem}>
          <View className={styles.logHeader}>
            <Text className={styles.logType}>{log.logType}</Text>
            <Text className={styles.logTime}>{log.operateTime}</Text>
          </View>
          <Text className={styles.logTitle}>{log.title}</Text>
          <Text className={styles.logContent}>{log.content}</Text>
          <Text className={styles.logOperator}>操作人: {log.operator}</Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default ProjectLogListPage;
