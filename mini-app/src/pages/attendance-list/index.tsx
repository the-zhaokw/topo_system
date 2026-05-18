import React from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';

const AttendanceListPage: React.FC = () => {
  const attendanceData = [
    { date: '2026-05-18', checkIn: '08:30', checkOut: '17:45', workHours: 8.5, status: '正常' },
    { date: '2026-05-17', checkIn: '08:35', checkOut: '17:50', workHours: 8.5, status: '正常' },
    { date: '2026-05-16', checkIn: '08:45', checkOut: '17:30', workHours: 8.0, status: '迟到' },
    { date: '2026-05-15', checkIn: '08:30', checkOut: '17:40', workHours: 8.5, status: '正常' },
    { date: '2026-05-14', checkIn: '08:30', checkOut: '17:45', workHours: 8.5, status: '正常' }
  ];

  const getStatusClass = (status: string) => {
    switch (status) {
      case '正常':
        return styles.statusNormal;
      case '迟到':
        return styles.statusLate;
      case '缺勤':
        return styles.statusAbsent;
      default:
        return '';
    }
  };

  return (
    <ScrollView className={styles.container} scrollY>
      {attendanceData.map((item, index) => (
        <View
          key={index}
          className={styles.attendanceItem}
          onClick={() => Taro.navigateTo({ url: '/pages/attendance-detail/index' })}
        >
          <Text className={styles.attendanceDate}>{item.date}</Text>
          <Text className={styles.attendanceInfo}>上班打卡: {item.checkIn}</Text>
          <Text className={styles.attendanceInfo}>下班打卡: {item.checkOut}</Text>
          <Text className={styles.attendanceInfo}>工作时长: {item.workHours}小时</Text>
          <Text className={`${styles.attendanceInfo} ${getStatusClass(item.status)}`}>
            状态: {item.status}
          </Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default AttendanceListPage;
