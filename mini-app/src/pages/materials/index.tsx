import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { Material } from '../../types/business';
import { mockMaterials } from '../../data/businessData';

const MaterialsPage: React.FC = () => {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadMaterials();
  }, []);

  const loadMaterials = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      setMaterials(mockMaterials);
      console.log('[Materials] Loaded materials:', mockMaterials.length);
    } catch (error) {
      console.error('[Materials] Error loading materials:', error);
      Taro.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const onPullDownRefresh = () => {
    loadMaterials().then(() => {
      Taro.stopPullDownRefresh();
      Taro.showToast({
        title: '刷新成功',
        icon: 'success'
      });
    });
  };

  const formatPrice = (price: number) => {
    return `¥${price.toLocaleString()}`;
  };

  return (
    <View className={styles.container}>
      <ScrollView
        scrollY
        className={styles.materialList}
        enableBackToTop
        onPullDownRefresh={onPullDownRefresh}
      >
        {materials.length === 0 ? (
          <View className={styles.emptyState}>
            <Text className={styles.emptyIcon}>📦</Text>
            <Text className={styles.emptyText}>暂无物料数据</Text>
            <Text className={styles.emptyHint}>添加第一个物料吧</Text>
          </View>
        ) : (
          <>
            {materials.map(material => (
              <View key={material.id} className={styles.materialCard}>
                <View className={styles.materialHeader}>
                  <View className={styles.materialIcon}>
                    <Text>📦</Text>
                  </View>
                  <View className={styles.materialInfo}>
                    <Text className={styles.materialName}>{material.name}</Text>
                    <Text className={styles.materialCode}>{material.code}</Text>
                  </View>
                </View>

                <View className={styles.materialDetails}>
                  <View className={styles.detailItem}>
                    <Text className={styles.detailLabel}>分类</Text>
                    <Text className={styles.detailValue}>{material.category}</Text>
                  </View>
                  <View className={styles.detailItem}>
                    <Text className={styles.detailLabel}>单位</Text>
                    <Text className={styles.detailValue}>{material.unit}</Text>
                  </View>
                  <View className={styles.detailItem}>
                    <Text className={styles.detailLabel}>库存</Text>
                    <Text className={styles.detailValue}>{material.stock}</Text>
                  </View>
                </View>

                <View className={styles.materialFooter}>
                  <View className={styles.warehouse}>
                    <Text>🏭</Text>
                    <Text>{material.warehouse}</Text>
                    {material.location && (
                      <Text className={styles.location}> | {material.location}</Text>
                    )}
                  </View>
                  <Text className={styles.price}>{formatPrice(material.price)}</Text>
                </View>
              </View>
            ))}
          </>
        )}
      </ScrollView>
    </View>
  );
};

export default MaterialsPage;
