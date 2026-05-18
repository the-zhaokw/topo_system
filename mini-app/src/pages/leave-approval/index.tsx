import React, { useState } from 'react';
import { View, Text, ScrollView, Button } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockLeaveApplication } from '../../data/attendance';

const LeaveApprovalPage: React.FC = () => {
  const [leaveList, setLeaveList] = useState(mockLeaveApplication);

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
      content: '确定通过该请假申请?',
      success: (res) => {
        if (res.confirm) {
          setLeaveList(leaveList.map(item =>
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
      content: '确定拒绝该请假申请?',
      success: (res) => {
        if (res.confirm) {
          setLeaveList(leaveList.map(item =>
            item.id === id ? { ...item, status: '已拒绝' as const } : item
          ));
          Taro.showToast({ title: '已拒绝', icon: 'success' });
        }
      }
    });
  };

  return (
    <ScrollView className={styles.container} scrollY>
      {leaveList.map((leave, index) => (
        <View key={index} className={styles.leaveItem}>
          <View className={styles.leaveHeader}>
            <Text className={styles.applicant}>{leave.applicantName}</Text>
            <Text className={`${styles.statusTag} ${getStatusClass(leave.status)}`}>
              {leave.status}
            </Text>
          </View>
          <Text className={styles.leaveInfo}>请假类型: {leave.leaveType}</Text>
          <Text className={styles.leaveInfo}>
            请假时间: {leave.startDate} 至 {leave.endDate} ({leave.totalDays}天)
          </Text>
          <Text className={styles.leaveInfo}>申请时间: {leave.applyTime}</Text>
          <Text className={styles.leaveReason}>请假原因: {leave.reason}</Text>
          {leave.status === '待审批' && (
            <View style={{ display: 'flex', gap: '16rpx' }}>
              <Button
                className={styles.actionBtn}
                style={{ background: '#22C55E', flex: 1 }}
                onClick={() => handleApprove(leave.id)}
              >
                通过
              </Button>
              <Button
                className={styles.actionBtn}
                style={{ background: '#F43F5E', flex: 1 }}
                onClick={() => handleReject(leave.id)}
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

export default LeaveApprovalPage;
