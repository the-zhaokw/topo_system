import React, { useState, useEffect } from 'react';
import { View, Text, Button } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockBugList } from '../../data/bugData';

const MinePage: React.FC = () => {
  const [userInfo] = useState({
    name: '张三',
    role: '项目经理',
    email: 'zhangsan@topo.com',
    avatar: ''
  });

  const [stats, setStats] = useState({
    myBugs: 0,
    handling: 0,
    resolved: 0
  });

  useEffect(() => {
    calculateStats();
  }, []);

  const calculateStats = () => {
    const myBugs = mockBugList.filter(bug => bug.reporter_name === '张三').length;
    const handling = mockBugList.filter(bug =>
      bug.assignee_name === '张三' && bug.status === 'in_progress'
    ).length;
    const resolved = mockBugList.filter(bug =>
      bug.assignee_name === '张三' &&
      (bug.status === 'resolved' || bug.status === 'closed')
    ).length;

    setStats({ myBugs, handling, resolved });
  };

  const handleMenuClick = (menu: string) => {
    switch (menu) {
      case 'notifications':
        Taro.showToast({
          title: '通知功能开发中',
          icon: 'info'
        });
        break;
      case 'settings':
        Taro.showToast({
          title: '设置功能开发中',
          icon: 'info'
        });
        break;
      case 'about':
        Taro.showToast({
          title: '关于功能开发中',
          icon: 'info'
        });
        break;
      case 'feedback':
        Taro.showToast({
          title: '反馈功能开发中',
          icon: 'info'
        });
        break;
    }
  };

  const getInitials = (name: string) => {
    return name.charAt(0).toUpperCase();
  };

  return (
    <View className={styles.container}>
      <View className={styles.profileCard}>
        <View className={styles.profileHeader}>
          <View className={styles.avatar}>
            <Text>{getInitials(userInfo.name)}</Text>
          </View>
          <View className={styles.profileInfo}>
            <Text className={styles.userName}>{userInfo.name}</Text>
            <Text className={styles.userRole}>{userInfo.role}</Text>
            <Text className={styles.userEmail}>{userInfo.email}</Text>
          </View>
        </View>

        <View className={styles.statsRow}>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>{stats.myBugs}</Text>
            <Text className={styles.statLabel}>我的Bug</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>{stats.handling}</Text>
            <Text className={styles.statLabel}>处理中</Text>
          </View>
          <View className={styles.statItem}>
            <Text className={styles.statValue}>{stats.resolved}</Text>
            <Text className={styles.statLabel}>已解决</Text>
          </View>
        </View>
      </View>

      <View className={styles.menuSection}>
        <Text className={styles.sectionTitle}>功能</Text>
        <View className={styles.menuList}>
          <View className={styles.menuItem} onClick={() => handleMenuClick('notifications')}>
            <View className={styles.menuIcon} style={{ background: 'rgba(255, 77, 79, 0.1)' }}>
              <Text>🔔</Text>
            </View>
            <View className={styles.menuContent}>
              <Text className={styles.menuTitle}>我的通知</Text>
              <Text className={styles.menuDesc}>查看系统通知和消息</Text>
            </View>
            <Text className={styles.menuArrow}>›</Text>
          </View>

          <View className={styles.menuItem} onClick={() => handleMenuClick('settings')}>
            <View className={styles.menuIcon} style={{ background: 'rgba(24, 144, 255, 0.1)' }}>
              <Text>⚙️</Text>
            </View>
            <View className={styles.menuContent}>
              <Text className={styles.menuTitle}>设置</Text>
              <Text className={styles.menuDesc}>应用设置和偏好</Text>
            </View>
            <Text className={styles.menuArrow}>›</Text>
          </View>

          <View className={styles.menuItem} onClick={() => handleMenuClick('feedback')}>
            <View className={styles.menuIcon} style={{ background: 'rgba(250, 173, 20, 0.1)' }}>
              <Text>💬</Text>
            </View>
            <View className={styles.menuContent}>
              <Text className={styles.menuTitle}>意见反馈</Text>
              <Text className={styles.menuDesc}>提交问题和建议</Text>
            </View>
            <Text className={styles.menuArrow}>›</Text>
          </View>
        </View>
      </View>

      <View className={styles.menuSection}>
        <Text className={styles.sectionTitle}>其他</Text>
        <View className={styles.menuList}>
          <View className={styles.menuItem} onClick={() => handleMenuClick('about')}>
            <View className={styles.menuIcon} style={{ background: 'rgba(82, 196, 26, 0.1)' }}>
              <Text>ℹ️</Text>
            </View>
            <View className={styles.menuContent}>
              <Text className={styles.menuTitle}>关于</Text>
              <Text className={styles.menuDesc}>应用版本和相关信息</Text>
            </View>
            <Text className={styles.menuArrow}>›</Text>
          </View>

          <View className={styles.menuItem}>
            <View className={styles.menuIcon} style={{ background: 'rgba(245, 34, 45, 0.1)' }}>
              <Text>📤</Text>
            </View>
            <View className={styles.menuContent}>
              <Text className={styles.menuTitle}>退出登录</Text>
              <Text className={styles.menuDesc}>退出当前账号</Text>
            </View>
            <Text className={styles.menuArrow}>›</Text>
          </View>
        </View>
      </View>

      <View className={styles.version}>
        <Text>TOPO系统 v1.0.0</Text>
      </View>
    </View>
  );
};

export default MinePage;
