import React, { useState } from 'react';
import { View, Text, Input, Button, Picker, Textarea } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';

const OvertimeApplicationPage: React.FC = () => {
  const [formData, setFormData] = useState({
    overtimeDate: '',
    startTime: '',
    endTime: '',
    totalHours: '',
    reason: ''
  });

  const handleSubmit = () => {
    if (!formData.overtimeDate) {
      Taro.showToast({ title: '请选择加班日期', icon: 'none' });
      return;
    }
    if (!formData.startTime || !formData.endTime) {
      Taro.showToast({ title: '请选择加班时间', icon: 'none' });
      return;
    }
    if (!formData.reason) {
      Taro.showToast({ title: '请输入加班原因', icon: 'none' });
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
          <Text className={styles.label}>加班日期</Text>
          <Picker
            mode="date"
            onChange={(e) => setFormData({ ...formData, overtimeDate: e.detail.value })}
          >
            <View className={styles.picker}>
              <Text>{formData.overtimeDate || '请选择'}</Text>
            </View>
          </Picker>
        </View>

        <View className={styles.formItem}>
          <Text className={styles.label}>加班时间</Text>
          <View style={{ display: 'flex', gap: '16rpx' }}>
            <Picker
              mode="time"
              style={{ flex: 1 }}
              onChange={(e) => setFormData({ ...formData, startTime: e.detail.value })}
            >
              <View className={styles.picker}>
                <Text>{formData.startTime || '开始时间'}</Text>
              </View>
            </Picker>
            <Picker
              mode="time"
              style={{ flex: 1 }}
              onChange={(e) => setFormData({ ...formData, endTime: e.detail.value })}
            >
              <View className={styles.picker}>
                <Text>{formData.endTime || '结束时间'}</Text>
              </View>
            </Picker>
          </View>
        </View>

        <View className={styles.formItem}>
          <Text className={styles.label}>加班时长(小时)</Text>
          <Input
            className={styles.input}
            type="number"
            placeholder="请输入加班时长"
            value={formData.totalHours}
            onInput={(e) => setFormData({ ...formData, totalHours: e.detail.value })}
          />
        </View>

        <View className={styles.formItem}>
          <Text className={styles.label}>加班原因</Text>
          <Textarea
            className={styles.textarea}
            placeholder="请输入加班原因..."
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

export default OvertimeApplicationPage;
