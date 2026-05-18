import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';
import { mockWorkLog } from '../../data/business';

const WorkLogListPage: React.FC = () => {
  const [logList] = useState(mockWorkLog);

  const getStatusClass = (status: string) => {
    return status === '已通过' ? styles.statusApproved : styles.statusPending;
  };

  return (
    <ScrollView className={styles.container} scrollY>
      {logList.map((log, index) => (
        <View key={index} className={styles.logItem}>
          <View className={styles.logHeader}>
            <Text className={styles.logNo}>{log.logNo}</Text>
            <Text className={`${styles.statusTag} ${getStatusClass(log.status)}`}>
              {log.status}
            </Text>
          </View>
          <Text className={styles.logProject}>{log.projectName}</Text>
          <Text className={styles.logContent}>{log.workContent}</Text>
          <Text className={styles.logMeta}>
            工作时长: {log.workHours}小时 | 日期: {log.workDate} | 提交人: {log.submitter}
          </Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default WorkLogListPage;
