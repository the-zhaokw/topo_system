import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import classnames from 'classnames';
import styles from './index.module.scss';
import { Notification } from '../../types/business';
import { mockNotifications } from '../../data/businessData';

const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      setNotifications(mockNotifications);
      console.log('[Notifications] Loaded notifications:', mockNotifications.length);
    } catch (error) {
      console.error('[Notifications] Error loading notifications:', error);
      Taro.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const onPullDownRefresh = () => {
    loadNotifications().then(() => {
      Taro.stopPullDownRefresh();
      Taro.showToast({
        title: '刷新成功',
        icon: 'success'
      });
    });
  };

  const handleMarkAsRead = (notificationId: number) => {
    setNotifications(prev => prev.map(n =>
      n.id === notificationId ? { ...n, is_read: true } : n
    ));
  };

  const getTypeClass = (type: string) => {
    const classMap: Record<string, string> = {
      'info': styles.typeInfo,
      'warning': styles.typeWarning,
      'success': styles.typeSuccess,
      'error': styles.typeError
    };
    return classMap[type] || '';
  };

  const getTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      'info': 'ℹ️',
      'warning': '⚠️',
      'success': '✅',
      'error': '❌'
    };
    return icons[type] || 'ℹ️';
  };

  const formatTime = (timeStr: string) => {
    const date = new Date(timeStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    if (days < 7) return `${days}天前`;
    return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <View className={styles.container}>
      {unreadCount > 0 && (
        <View className={styles.unreadBanner}>
          <Text>您有 {unreadCount} 条未读通知</Text>
        </View>
      )}

      <ScrollView
        scrollY
        className={styles.notificationList}
        enableBackToTop
        onPullDownRefresh={onPullDownRefresh}
      >
        {notifications.length === 0 ? (
          <View className={styles.emptyState}>
            <Text className={styles.emptyIcon}>🔔</Text>
            <Text className={styles.emptyText}>暂无通知</Text>
            <Text className={styles.emptyHint}>所有消息都已处理完毕</Text>
          </View>
        ) : (
          <>
            {notifications.map(notification => (
              <View
                key={notification.id}
                className={classnames(
                  styles.notificationCard,
                  !notification.is_read && styles.unread
                )}
                onClick={() => handleMarkAsRead(notification.id)}
              >
                <View className={classnames(styles.iconWrapper, getTypeClass(notification.type))}>
                  <Text>{getTypeIcon(notification.type)}</Text>
                </View>
                <View className={styles.content}>
                  <View className={styles.header}>
                    <Text className={styles.title}>{notification.title}</Text>
                    {!notification.is_read && <View className={styles.unreadDot} />}
                  </View>
                  <Text className={styles.contentText}>{notification.content}</Text>
                  <Text className={styles.time}>{formatTime(notification.created_at)}</Text>
                </View>
              </View>
            ))}
          </>
        )}
      </ScrollView>
    </View>
  );
};

export default NotificationsPage;
