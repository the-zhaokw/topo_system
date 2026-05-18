import React, { useState } from 'react';
import { View, Text, ScrollView, Button } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockOvertimeApplication } from '../../data/attendance';

const OvertimeApprovalPage: React.FC = () => {
  const [overtimeList, setOvertimeList] = useState(mockOvertimeApplication);

  const getStatusClass = (status: string) => {
    switch (status) {
      case '待审批':
        return styles.statusPending;
      case '已通过':
        return styles.statusApproved;
      case '已拒绝':
        return styles.statusRejected;
      default:
        return '';
    }
  };

  const handleApprove = (id: number) => {
    Taro.showModal({
      title: '确认',
      content: '确定通过该加班申请?',
      success: (res) => {
        if (res.confirm) {
          setOvertimeList(overtimeList.map(item =>
            item.id === id ? { ...item, status: '已通过' as const } : item
          ));
          Taro.showToast({ title: '已通过', icon: 'success' });
        }
      }
    });
  };

  const handleReject = (id: number) => {
    Taro.showModal({
      title: '确认',
      content: '确定拒绝该加班申请?',
      success: (res) => {
        if (res.confirm) {
          setOvertimeList(overtimeList.map(item =>
            item.id === id ? { ...item, status: '已拒绝' as const } : item
          ));
          Taro.showToast({ title: '已拒绝', icon: 'success' });
        }
      }
    });
  };

  return (
    <ScrollView className={styles.container} scrollY>
      {overtimeList.map((overtime, index) => (
        <View key={index} className={styles.overtimeItem}>
          <View className={styles.overtimeHeader}>
            <Text className={styles.applicant}>{overtime.applicantName}</Text>
            <Text className={`${styles.statusTag} ${getStatusClass(overtime.status)}`}>
              {overtime.status}
            </Text>
          </View>
          <Text className={styles.overtimeInfo}>加班日期: {overtime.overtimeDate}</Text>
          <Text className={styles.overtimeInfo}>
            加班时间: {overtime.startTime} - {overtime.endTime} ({overtime.totalHours}小时)
          </Text>
          <Text className={styles.overtimeInfo}>申请时间: {overtime.applyTime}</Text>
          <Text className={styles.overtimeReason}>加班原因: {overtime.reason}</Text>
          {overtime.status === '待审批' && (
            <View style={{ display: 'flex', gap: '16rpx' }}>
              <Button
                className={styles.actionBtn}
                style={{ background: '#22C55E', flex: 1 }}
                onClick={() => handleApprove(overtime.id)}
              >
                通过
              </Button>
              <Button
                className={styles.actionBtn}
                style={{ background: '#F43F5E', flex: 1 }}
                onClick={() => handleReject(overtime.id)}
              >
                拒绝
              </Button>
            </View>
          )}
        </View>
      ))}
    </ScrollView>
  );
};

export default OvertimeApprovalPage;
