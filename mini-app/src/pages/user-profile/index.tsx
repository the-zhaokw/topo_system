import React from 'react';
import { View, Text, ScrollView, Image } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';

const UserProfilePage: React.FC = () => {
  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.avatarSection}>
        <Image
          className={styles.avatar}
          src="https://picsum.photos/id/64/200/200"
          mode="aspectFill"
        />
        <Text className={styles.userName}>系统管理员</Text>
        <Text className={styles.userRole}>管理员</Text>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>账号信息</Text>
        <View className={styles.menuItem}>
          <Text className={styles.menuLabel}>用户名</Text>
          <Text className={styles.menuArrow}>admin</Text>
        </View>
        <View className={styles.menuItem}>
          <Text className={styles.menuLabel}>邮箱</Text>
          <Text className={styles.menuArrow}>admin@topo.com</Text>
        </View>
        <View className={styles.menuItem}>
          <Text className={styles.menuLabel}>手机</Text>
          <Text className={styles.menuArrow}>138****8000</Text>
        </View>
      </View>

      <View className={styles.card}>
        <Text className={styles.cardTitle}>其他设置</Text>
        <View
          className={styles.menuItem}
          onClick={() => Taro.navigateTo({ url: '/pages/my-department/index' })}
        >
          <Text className={styles.menuLabel}>我的部门</Text>
          <Text className={styles.menuArrow}>›</Text>
        </View>
        <View className={styles.menuItem}>
          <Text className={styles.menuLabel}>修改密码</Text>
          <Text className={styles.menuArrow}>›</Text>
        </View>
        <View className={styles.menuItem}>
          <Text className={styles.menuLabel}>退出登录</Text>
          <Text className={styles.menuArrow}>›</Text>
        </View>
      </View>
    </ScrollView>
  );
};

export default UserProfilePage;
