import React from 'react';
import { View, Text, ScrollView, Image } from '@tarojs/components';
import styles from './index.module.scss';

const UserDetailPage: React.FC = () => {
  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.avatarSection}>
        <Image
          className={styles.avatar}
          src="https://picsum.photos/id/64/200/200"
          mode="aspectFill"
        />
        <Text className={styles.userName}>张三</Text>
        <Text className={styles.userRole}>项目经理</Text>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>基本信息</Text>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>用户名</Text>
          <Text className={styles.infoValue}>zhangsan</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>邮箱</Text>
          <Text className={styles.infoValue}>zhangsan@topo.com</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>手机</Text>
          <Text className={styles.infoValue}>138****8001</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>部门</Text>
          <Text className={styles.infoValue}>研发部</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>职位</Text>
          <Text className={styles.infoValue}>项目经理</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>入职日期</Text>
          <Text className={styles.infoValue}>2021-03-15</Text>
        </View>
        <View className={styles.infoItem}>
          <Text className={styles.infoLabel}>状态</Text>
          <Text className={styles.infoValue} style={{ color: '#22C55E' }}>在职</Text>
        </View>
      </View>
    </ScrollView>
  );
};

export default UserDetailPage;
