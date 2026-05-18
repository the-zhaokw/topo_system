import React from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockShiftInfo } from '../../data/attendance';

const ShiftManagementPage: React.FC = () => {
  return (
    <ScrollView className={styles.container} scrollY>
      {mockShiftInfo.map((shift, index) => (
        <View key={index} className={styles.shiftItem}>
          <Text className={styles.shiftName}>{shift.shiftName}</Text>
          <View className={styles.shiftTime}>
            <Text>上班时间: {shift.startTime}</Text>
            <Text>下班时间: {shift.endTime}</Text>
          </View>
          <View className={styles.shiftTime}>
            <Text>休息开始: {shift.breakStart}</Text>
            <Text>休息结束: {shift.breakEnd}</Text>
          </View>
          <Text className={styles.workHours}>工作时长: {shift.workHours}小时</Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default ShiftManagementPage;
