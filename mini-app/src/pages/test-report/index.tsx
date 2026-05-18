import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';
import { mockTestReport } from '../../data/testManagement';

const TestReportPage: React.FC = () => {
  const [report] = useState(mockTestReport);

  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>报告信息</Text>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>报告编号</Text>
          <Text className={styles.infoValue}>{report.reportNo}</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>报告标题</Text>
          <Text className={styles.infoValue}>{report.title}</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>项目名称</Text>
          <Text className={styles.infoValue}>{report.projectName}</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>创建人</Text>
          <Text className={styles.infoValue}>{report.createdBy}</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>创建时间</Text>
          <Text className={styles.infoValue}>{report.createdAt}</Text>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>执行摘要</Text>
        <View className={styles.statsGrid}>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>{report.summary.totalCases}</Text>
            <Text className={styles.statLabel}>总用例</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#22C55E' }}>
              {report.summary.passedCases}
            </Text>
            <Text className={styles.statLabel}>通过</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#F43F5E' }}>
              {report.summary.failedCases}
            </Text>
            <Text className={styles.statLabel}>失败</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue} style={{ color: '#3B82F6' }}>
              {report.summary.passRate}%
            </Text>
            <Text className={styles.statLabel}>通过率</Text>
          </View>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>开始时间</Text>
          <Text className={styles.infoValue}>{report.summary.startTime}</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>结束时间</Text>
          <Text className={styles.infoValue}>{report.summary.endTime}</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>执行时长</Text>
          <Text className={styles.infoValue}>{report.summary.duration}分钟</Text>
        </View>
      </View>
    </ScrollView>
  );
};

export default TestReportPage;
