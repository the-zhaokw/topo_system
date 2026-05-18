import React from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';

const TestCaseDetailPage: React.FC = () => {
  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.card}>
        <Text className={styles.cardTitle}>基本信息</Text>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>用例编号</Text>
          <Text className={styles.infoValue}>TC-USER-001</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>用例名称</Text>
          <Text className={styles.infoValue}>用户登录-正确账号密码</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>优先级</Text>
          <Text className={styles.infoValue} style={{ color: '#F43F5E' }}>P0</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>测试类型</Text>
          <Text className={styles.infoValue}>功能测试</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>状态</Text>
          <Text className={styles.infoValue} style={{ color: '#22C55E' }}>通过</Text>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>前置条件</Text>
        <Text style={{ fontSize: '28rpx', color: '#64748B', lineHeight: '1.6' }}>
          用户已注册
        </Text>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>测试步骤</Text>
        <View className={styles.stepItem}>
          <Text className={styles.stepNo}>步骤 1</Text>
          <Text className={styles.stepDesc}>打开登录页面</Text>
          <Text className={styles.stepResult}>预期: 页面正常显示</Text>
        </View>
        <View className={styles.stepItem}>
          <Text className={styles.stepNo}>步骤 2</Text>
          <Text className={styles.stepDesc}>输入正确的用户名和密码</Text>
          <Text className={styles.stepResult}>预期: 输入框正常显示输入内容</Text>
        </View>
        <View className={styles.stepItem}>
          <Text className={styles.stepNo}>步骤 3</Text>
          <Text className={styles.stepDesc}>点击登录按钮</Text>
          <Text className={styles.stepResult}>预期: 登录成功,跳转到首页</Text>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>预期结果</Text>
        <Text style={{ fontSize: '28rpx', color: '#64748B', lineHeight: '1.6' }}>
          登录成功,显示用户信息
        </Text>
      </View>
    </ScrollView>
  );
};

export default TestCaseDetailPage;
