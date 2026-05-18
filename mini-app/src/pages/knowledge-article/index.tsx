import React from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';

const KnowledgeArticlePage: React.FC = () => {
  return (
    <ScrollView className={styles.container} scrollY>
      <View className={styles.articleContent}>
        <Text className={styles.articleTitle}>知识库文章标题</Text>
        <Text className={styles.articleInfo}>分类: 技术文档</Text>
        <Text className={styles.articleInfo}>作者: 张三</Text>
        <Text className={styles.articleInfo}>更新时间: 2026-05-18</Text>
        <View style={{ height: '32rpx' }} />
        <Text className={styles.articleBody}>
          这是文章的内容。知识库文章应该包含详细的技术文档、操作指南、最佳实践等内容。
          用户可以在这里查看和学习相关知识。
        </Text>
      </View>
    </ScrollView>
  );
};

export default KnowledgeArticlePage;
