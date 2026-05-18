import React, { useState } from 'react';
import { View, Text, Button, Picker, Textarea } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';

const LeaveApplicationPage: React.FC = () => {
  const [formData, setFormData] = useState({
    leaveType: '年假',
    startDate: '',
    endDate: '',
    reason: ''
  });

  const leaveTypes = ['年假', '病假', '事假', '婚假', '产假', '陪产假', '其他'];

  const handleSubmit = () => {
    if (!formData.startDate || !formData.endDate) {
      Taro.showToast({ title: '请选择日期', icon: 'none' });
      return;
    }
    if (!formData.reason) {
      Taro.showToast({ title: '请输入请假原因', icon: 'none' });
      return;
    }

    Taro.showLoading({ title: '提交中...' });
    setTimeout(() => {
      Taro.hideLoading();
      Taro.showToast({ title: '提交成功', icon: 'success' });
      setTimeout(() => {
        Taro.navigateBack();
      }, 1500);
    }, 1500);
  };

  return (
    <View className={styles.container}>
      <View className={styles.formCard}>
        <View className={styles.formItem}>
          <Text className={styles.label}>请假类型</Text>
          <Picker
            mode="selector"
            range={leaveTypes}
            onChange={(e) => setFormData({ ...formData, leaveType: leaveTypes[e.detail.value] })}
          >
            <View className={styles.picker}>
              <Text>{formData.leaveType}</Text>
            </View>
          </Picker>
        </View>

        <View className={styles.formItem}>
          <Text className={styles.label}>开始日期</Text>
          <Picker
            mode="date"
            onChange={(e) => setFormData({ ...formData, startDate: e.detail.value })}
          >
            <View className={styles.picker}>
              <Text>{formData.startDate || '请选择'}</Text>
            </View>
          </Picker>
        </View>

        <View className={styles.formItem}>
          <Text className={styles.label}>结束日期</Text>
          <Picker
            mode="date"
            onChange={(e) => setFormData({ ...formData, endDate: e.detail.value })}
          >
            <View className={styles.picker}>
              <Text>{formData.endDate || '请选择'}</Text>
            </View>
          </Picker>
        </View>

        <View className={styles.formItem}>
          <Text className={styles.label}>请假原因</Text>
          <Textarea
            className={styles.textarea}
            placeholder="请输入请假原因..."
            value={formData.reason}
            onInput={(e) => setFormData({ ...formData, reason: e.detail.value })}
          />
        </View>

        <Button className={styles.submitBtn} onClick={handleSubmit}>
          提交申请
        </Button>
      </View>
    </View>
  );
};

export default LeaveApplicationPage;
