import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { KnowledgeArticle } from '../../types/business';
import { mockKnowledgeArticles } from '../../data/businessData';

const KnowledgePage: React.FC = () => {
  const [articles, setArticles] = useState<KnowledgeArticle[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadArticles();
  }, []);

  const loadArticles = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      setArticles(mockKnowledgeArticles);
      console.log('[Knowledge] Loaded articles:', mockKnowledgeArticles.length);
    } catch (error) {
      console.error('[Knowledge] Error loading articles:', error);
      Taro.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const onPullDownRefresh = () => {
    loadArticles().then(() => {
      Taro.stopPullDownRefresh();
      Taro.showToast({
        title: '刷新成功',
        icon: 'success'
      });
    });
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return '今天';
    if (days === 1) return '昨天';
    if (days < 7) return `${days}天前`;
    return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
  };

  return (
    <View className={styles.container}>
      <ScrollView
        scrollY
        className={styles.articleList}
        enableBackToTop
        onPullDownRefresh={onPullDownRefresh}
      >
        {articles.length === 0 ? (
          <View className={styles.emptyState}>
            <Text className={styles.emptyIcon}>📚</Text>
            <Text className={styles.emptyText}>暂无知识文章</Text>
            <Text className={styles.emptyHint}>开始创作第一篇文章吧</Text>
          </View>
        ) : (
          <>
            {articles.map(article => (
              <View key={article.id} className={styles.articleCard}>
                <View className={styles.articleHeader}>
                  <Text className={styles.category}>{article.category}</Text>
                  <Text className={styles.date}>{formatDate(article.created_at)}</Text>
                </View>
                <Text className={styles.title}>{article.title}</Text>
                {article.summary && (
                  <Text className={styles.summary}>{article.summary}</Text>
                )}
                <View className={styles.articleFooter}>
                  <View className={styles.author}>
                    <Text>👤</Text>
                    <Text className={styles.authorName}>{article.author}</Text>
                  </View>
                  <View className={styles.views}>
                    <Text>👁️</Text>
                    <Text className={styles.viewCount}>{article.view_count}</Text>
                  </View>
                </View>
              </View>
            ))}
          </>
        )}
      </ScrollView>
    </View>
  );
};

export default KnowledgePage;
