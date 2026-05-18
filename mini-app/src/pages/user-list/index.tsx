import React, { useState } from 'react';
import { View, Text, ScrollView, Image } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockUser } from '../../data/business';

const UserListPage: React.FC = () => {
  const [userList] = useState(mockUser);

  const getStatusClass = (status: string) => {
    return status === '在职' ? styles.statusWorking : styles.statusLeave;
  };

  return (
    <ScrollView className={styles.container} scrollY>
      {userList.map((user, index) => (
        <View
          key={index}
          className={styles.userItem}
          onClick={() => Taro.navigateTo({ url: `/pages/user-detail/index?id=${user.id}` })}
        >
          <Image
            className={styles.avatar}
            src={user.avatar || 'https://picsum.photos/id/64/200/200'}
            mode="aspectFill"
          />
          <View className={styles.userInfo}>
            <Text className={styles.userName}>{user.realName}</Text>
            <Text className={styles.userMeta}>部门: {user.department}</Text>
            <Text className={styles.userMeta}>职位: {user.position}</Text>
            <Text className={`${styles.statusTag} ${getStatusClass(user.status)}`}>
              {user.status}
            </Text>
          </View>
        </View>
      ))}
    </ScrollView>
  );
};

export default UserListPage;
