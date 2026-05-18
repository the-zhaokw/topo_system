import React, { useState } from 'react';
import { View, Text, Input, Textarea, Button, Picker } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';

const BugFormPage: React.FC = () => {
  const [formData, setFormData] = useState({
    bugName: '',
    projectName: '',
    severity: '中',
    priority: 'P2',
    description: '',
    steps: '',
    expectedResult: ''
  });

  const severityList = ['严重', '高', '中', '低'];
  const priorityList = ['P0', 'P1', 'P2', 'P3'];

  const handleSubmit = () => {
    if (!formData.bugName) {
      Taro.showToast({ title: '请输入Bug名称', icon: 'none' });
      return;
    }
    if (!formData.description) {
      Taro.showToast({ title: '请输入Bug描述', icon: 'none' });
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
          <Text className={styles.label}>Bug名称 *</Text>
          <Input
            className={styles.input}
            placeholder="请输入Bug名称"
            value={formData.bugName}
            onInput={(e) => setFormData({ ...formData, bugName: e.detail.value })}
          />
        </View>

        <View className={styles.formItem}>
          <Text className={styles.label}>所属项目 *</Text>
          <Input
            className={styles.input}
            placeholder="请输入项目名称"
            value={formData.projectName}
            onInput={(e) => setFormData({ ...formData, projectName: e.detail.value })}
          />
        </View>

        <View className={styles.formItem}>
          <Text className={styles.label}>严重程度</Text>
          <Picker
            mode="selector"
            range={severityList}
            onChange={(e) => setFormData({ ...formData, severity: severityList[e.detail.value] })}
          >
            <View className={styles.picker}>
              <Text>{formData.severity}</Text>
            </View>
          </Picker>
        </View>

        <View className={styles.formItem}>
          <Text className={styles.label}>优先级</Text>
          <Picker
            mode="selector"
            range={priorityList}
            onChange={(e) => setFormData({ ...formData, priority: priorityList[e.detail.value] })}
          >
            <View className={styles.picker}>
              <Text>{formData.priority}</Text>
            </View>
          </Picker>
        </View>

        <View className={styles.formItem}>
          <Text className={styles.label}>Bug描述 *</Text>
          <Textarea
            className={styles.textarea}
            placeholder="请详细描述Bug..."
            value={formData.description}
            onInput={(e) => setFormData({ ...formData, description: e.detail.value })}
          />
        </View>

        <View className={styles.formItem}>
          <Text className={styles.label}>复现步骤</Text>
          <Textarea
            className={styles.textarea}
            placeholder="请输入复现步骤..."
            value={formData.steps}
            onInput={(e) => setFormData({ ...formData, steps: e.detail.value })}
          />
        </View>

        <View className={styles.formItem}>
          <Text className={styles.label}>预期结果</Text>
          <Textarea
            className={styles.textarea}
            placeholder="请输入预期结果..."
            value={formData.expectedResult}
            onInput={(e) => setFormData({ ...formData, expectedResult: e.detail.value })}
          />
        </View>

        <Button className={styles.submitBtn} onClick={handleSubmit}>
          提交Bug
        </Button>
      </View>
    </View>
  );
};

export default BugFormPage;
