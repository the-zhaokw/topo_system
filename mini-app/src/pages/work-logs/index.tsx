import React from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';

const WorkLogsPage: React.FC = () => {
  const logData = [
    {
      no: 'WL-2026051801',
      project: 'TOPO系统',
      content: '完成用户管理模块的单元测试，修复了3个bug',
      hours: 6,
      date: '2026-05-17',
      submitter: '张三',
      status: '已通过'
    },
    {
      no: 'WL-2026051802',
      project: '合同管理系统',
      content: '修复合同审批流程中的bug',
      hours: 4,
      date: '2026-05-17',
      submitter: '李四',
      status: '待审核'
    },
    {
      no: 'WL-2026051803',
      project: '物料追踪系统',
      content: '优化物料查询性能',
      hours: 5,
      date: '2026-05-16',
      submitter: '王五',
      status: '已驳回'
    }
  ];

  const getStatusClass = (status: string) => {
    switch (status) {
      case '已通过':
        return styles.statusApproved;
      case '待审核':
        return styles.statusPending;
      case '已驳回':
        return styles.statusRejected;
      default:
        return '';
    }
  };

  return (
    <ScrollView className={styles.container} scrollY>
      {logData.map((log, index) => (
        <View key={index} className={styles.logItem}>
          <View className={styles.logHeader}>
            <Text className={styles.logNo}>{log.no}</Text>
            <Text className={`${styles.statusTag} ${getStatusClass(log.status)}`}>
              {log.status}
            </Text>
          </View>
          <Text className={styles.logProject}>{log.project}</Text>
          <Text className={styles.logContent}>{log.content}</Text>
          <Text className={styles.logMeta}>
            工作时长: {log.hours}小时 | 日期: {log.date} | 提交人: {log.submitter}
          </Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default WorkLogsPage;
