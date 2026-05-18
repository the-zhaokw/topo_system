import React, { useEffect } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from '../../pages/attendance-detail/index.module.scss';
import { mockAttendanceReport } from '../../data/attendance';

const AttendanceReportPage: React.FC = () => {
  const report = mockAttendanceReport;

  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>考勤概览</Text>
        <View style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '24rpx', marginTop: '24rpx' }}>
          <View>
            <Text style={{ fontSize: '48rpx', fontWeight: 'bold', color: '#4F46E5' }}>{report.actualDays}</Text>
            <Text style={{ fontSize: '24rpx', color: '#64748B', display: 'block', marginTop: '8rpx' }}>实际出勤</Text>
          </View>
          <View>
            <Text style={{ fontSize: '48rpx', fontWeight: 'bold', color: '#22C55E' }}>{report.normalDays}</Text>
            <Text style={{ fontSize: '24rpx', color: '#64748B', display: 'block', marginTop: '8rpx' }}>正常天数</Text>
          </View>
          <View>
            <Text style={{ fontSize: '48rpx', fontWeight: 'bold', color: '#F59E0B' }}>{report.lateDays}</Text>
            <Text style={{ fontSize: '24rpx', color: '#64748B', display: 'block', marginTop: '8rpx' }}>迟到次数</Text>
          </View>
          <View>
            <Text style={{ fontSize: '48rpx', fontWeight: 'bold', color: '#3B82F6' }}>{report.overtimeHours}h</Text>
            <Text style={{ fontSize: '24rpx', color: '#64748B', display: 'block', marginTop: '8rpx' }}>加班时长</Text>
          </View>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>考勤明细</Text>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>应出勤天数</Text>
          <Text className={styles.infoValue}>{report.workDays}天</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>早退次数</Text>
          <Text className={styles.infoValue}>{report.earlyDays}次</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>缺勤天数</Text>
          <Text className={styles.infoValue}>{report.absentDays}天</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>请假天数</Text>
          <Text className={styles.infoValue}>{report.leaveDays}天</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>平均工作时长</Text>
          <Text className={styles.infoValue}>{report.averageWorkHours}小时</Text>
        </View>
      </View>
    </ScrollView>
  );
};

export default AttendanceReportPage;
