import React from 'react';
import { View, Text, ScrollView, Image } from '@tarojs/components';
import styles from './index.module.scss';

const KnowledgeSharePage: React.FC = () => {
  const shareData = [
    {
      author: '张三',
      avatar: 'https://picsum.photos/id/64/200/200',
      time: '2026-05-18 10:30',
      title: 'TOPO系统架构优化实践',
      content: '分享TOPO系统架构优化的经验和最佳实践，包括微服务拆分、缓存策略、数据库优化等方面的内容。',
      views: 156,
      likes: 45
    },
    {
      author: '李四',
      avatar: 'https://picsum.photos/id/91/200/200',
      time: '2026-05-17 14:20',
      title: 'Vue3 组件设计模式',
      content: '探讨Vue3中组件设计的最佳实践，包括组合式API的使用、组件拆分原则、状态管理等。',
      views: 234,
      likes: 67
    },
    {
      author: '王五',
      avatar: 'https://picsum.photos/id/177/200/200',
      time: '2026-05-16 09:15',
      title: 'React性能优化指南',
      content: '总结React应用性能优化的常用技巧，包括memo、useMemo、useCallback的使用，以及虚拟列表等。',
      views: 189,
      likes: 52
    }
  ];

  return (
    <ScrollView className={styles.container} scrollY>
      {shareData.map((share, index) => (
        <View key={index} className={styles.shareItem}>
          <View className={styles.shareHeader}>
            <Image
              className={styles.avatar}
              src={share.avatar}
              mode="aspectFill"
            />
            <View className={styles.authorInfo}>
              <Text className={styles.authorName}>{share.author}</Text>
              <Text className={styles.shareTime}>{share.time}</Text>
            </View>
          </View>
          <Text className={styles.shareTitle}>{share.title}</Text>
          <Text className={styles.shareContent}>{share.content}</Text>
          <View className={styles.shareMeta}>
            <Text>浏览 {share.views}</Text>
            <Text>点赞 {share.likes}</Text>
          </View>
        </View>
      ))}
    </ScrollView>
  );
};

export default KnowledgeSharePage;
