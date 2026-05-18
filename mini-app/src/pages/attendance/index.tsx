import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import classnames from 'classnames';
import styles from './index.module.scss';
import { Attendance } from '../../types/business';
import { mockAttendance } from '../../data/businessData';

const AttendancePage: React.FC = () => {
  const [attendanceList, setAttendanceList] = useState<Attendance[]>([]);
  const [loading, setLoading] = useState(false);
  const [todayStats, setTodayStats] = useState({
    checkIn: '--:--',
    checkOut: '--:--',
    workHours: 0,
    status: '未打卡'
  });

  useEffect(() => {
    loadAttendance();
  }, []);

  const loadAttendance = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      setAttendanceList(mockAttendance);

      const today = mockAttendance.find(a => a.date === '2026-05-18');
      if (today) {
        setTodayStats({
          checkIn: today.check_in_time?.substring(0, 5) || '--:--',
          checkOut: today.check_out_time?.substring(0, 5) || '--:--',
          workHours: today.work_hours,
          status: today.status === 'normal' ? '正常' : today.status === 'late' ? '迟到' : '未打卡'
        });
      }

      console.log('[Attendance] Loaded attendance records');
    } catch (error) {
      console.error('[Attendance] Error loading attendance:', error);
      Taro.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const onPullDownRefresh = () => {
    loadAttendance().then(() => {
      Taro.stopPullDownRefresh();
      Taro.showToast({
        title: '刷新成功',
        icon: 'success'
      });
    });
  };

  const handleCheckIn = () => {
    const now = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    setTodayStats(prev => ({
      ...prev,
      checkIn: now,
      status: parseInt(now.split(':')[0]) > 9 ? '迟到' : '正常'
    }));
    Taro.showToast({
      title: '签到成功',
      icon: 'success'
    });
  };

  const handleCheckOut = () => {
    const now = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    setTodayStats(prev => ({
      ...prev,
      checkOut: now,
      workHours: 8
    }));
    Taro.showToast({
      title: '签退成功',
      icon: 'success'
    });
  };

  const getStatusClass = (status: string) => {
    const classMap: Record<string, string> = {
      'normal': styles.statusNormal,
      'late': styles.statusLate,
      'absent': styles.statusAbsent,
      'leave': styles.statusLeave
    };
    return classMap[status] || '';
  };

  const getStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      'normal': '正常',
      'late': '迟到',
      'absent': '缺勤',
      'leave': '请假'
    };
    return labels[status] || status;
  };

  return (
    <View className={styles.container}>
      <View className={styles.todayCard}>
        <View className={styles.todayHeader}>
          <Text className={styles.todayDate}>今日打卡</Text>
          <Text className={classnames(styles.statusBadge, getStatusClass(todayStats.status))}>
            {todayStats.status}
          </Text>
        </View>
        <View className={styles.clockTimes}>
          <View className={styles.clockItem}>
            <Text className={styles.clockLabel}>签到时间</Text>
            <Text className={styles.clockTime}>{todayStats.checkIn}</Text>
          </View>
          <View className={styles.clockDivider} />
          <View className={styles.clockItem}>
            <Text className={styles.clockLabel}>签退时间</Text>
            <Text className={styles.clockTime}>{todayStats.checkOut}</Text>
          </View>
        </View>
        <View className={styles.workHours}>
          <Text>工作时长：{todayStats.workHours} 小时</Text>
        </View>
        <View className={styles.clockActions}>
          <View className={styles.clockBtn} onClick={handleCheckIn}>
            <Text className={styles.clockBtnText}>签到</Text>
          </View>
          <View className={classnames(styles.clockBtn, styles.clockBtnSecondary)} onClick={handleCheckOut}>
            <Text className={classnames(styles.clockBtnText, styles.clockBtnTextSecondary)}>签退</Text>
          </View>
        </View>
      </View>

      <ScrollView
        scrollY
        className={styles.historyList}
        enableBackToTop
        onPullDownRefresh={onPullDownRefresh}
      >
        <View className={styles.sectionTitle}>打卡记录</View>
        {attendanceList.map(record => (
          <View key={record.id} className={styles.recordCard}>
            <View className={styles.recordHeader}>
              <Text className={styles.recordDate}>{record.date}</Text>
              <Text className={classnames(styles.statusTag, getStatusClass(record.status))}>
                {getStatusLabel(record.status)}
              </Text>
            </View>
            <View className={styles.recordTimes}>
              <View className={styles.recordTime}>
                <Text className={styles.timeLabel}>签到</Text>
                <Text className={styles.timeValue}>
                  {record.check_in_time?.substring(0, 5) || '--:--'}
                </Text>
              </View>
              <View className={styles.recordTime}>
                <Text className={styles.timeLabel}>签退</Text>
                <Text className={styles.timeValue}>
                  {record.check_out_time?.substring(0, 5) || '--:--'}
                </Text>
              </View>
              <View className={styles.recordTime}>
                <Text className={styles.timeLabel}>工时</Text>
                <Text className={styles.timeValue}>{record.work_hours}h</Text>
              </View>
            </View>
          </View>
        ))}
      </ScrollView>
    </View>
  );
};

export default AttendancePage;
