import React, { useState } from 'react';
import { View, Text, Input, Textarea, Button, Picker } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';

const ProjectFormPage: React.FC = () => {
  const [formData, setFormData] = useState({
    projectName: '',
    projectCode: '',
    projectType: '',
    description: '',
    startDate: '',
    endDate: '',
    manager: '',
    budget: ''
  });

  const typeList = ['软件开发', '系统集成', '运维服务', '咨询服务'];
  const priorityList = ['高', '中', '低'];

  const handleSubmit = () => {
    if (!formData.projectName) {
      Taro.showToast({ title: '请输入项目名称', icon: 'none' });
      return;
    }
    if (!formData.projectCode) {
      Taro.showToast({ title: '请输入项目编号', icon: 'none' });
      return;
    }

    Taro.showLoading({ title: '提交中...' });
    setTimeout(() => {
      Taro.hideLoading();
      Taro.showToast({ title: '创建成功', icon: 'success' });
      setTimeout(() => {
        Taro.navigateBack();
      }, 1500);
    }, 1500);
  };

  return (
    <View className={styles.container}>
      <View className={styles.formCard}>
        <View className={styles.formItem}>
          <Text className={styles.label}>项目名称 *</Text>
          <Input
            className={styles.input}
            placeholder="请输入项目名称"
            value={formData.projectName}
            onInput={(e) => setFormData({ ...formData, projectName: e.detail.value })}
          />
        </View>

        <View className={styles.formItem}>
          <Text className={styles.label}>项目编号 *</Text>
          <Input
            className={styles.input}
            placeholder="请输入项目编号"
            value={formData.projectCode}
            onInput={(e) => setFormData({ ...formData, projectCode: e.detail.value })}
          />
        </View>

        <View className={styles.formItem}>
          <Text className={styles.label}>项目类型</Text>
          <Picker
            mode="selector"
            range={typeList}
            onChange={(e) => setFormData({ ...formData, projectType: typeList[e.detail.value] })}
          >
            <View className={styles.picker}>
              <Text>{formData.projectType || '请选择'}</Text>
            </View>
          </Picker>
        </View>

        <View className={styles.formItem}>
          <Text className={styles.label}>项目经理</Text>
          <Input
            className={styles.input}
            placeholder="请输入项目经理"
            value={formData.manager}
            onInput={(e) => setFormData({ ...formData, manager: e.detail.value })}
          />
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
          <Text className={styles.label}>项目预算</Text>
          <Input
            className={styles.input}
            type="number"
            placeholder="请输入项目预算"
            value={formData.budget}
            onInput={(e) => setFormData({ ...formData, budget: e.detail.value })}
          />
        </View>

        <View className={styles.formItem}>
          <Text className={styles.label}>项目描述</Text>
          <Textarea
            className={styles.textarea}
            placeholder="请输入项目描述..."
            value={formData.description}
            onInput={(e) => setFormData({ ...formData, description: e.detail.value })}
          />
        </View>

        <Button className={styles.submitBtn} onClick={handleSubmit}>
          创建项目
        </Button>
      </View>
    </View>
  );
};

export default ProjectFormPage;
