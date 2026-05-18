import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockMaterialCategory } from '../../data/material';

const MaterialCategoryPage: React.FC = () => {
  const [categories] = useState(mockMaterialCategory);

  return (
    <ScrollView className={styles.container} scrollY>
      {categories.map((category, index) => (
        <View key={index} className={styles.categoryItem}>
          <Text className={styles.categoryName}>{category.categoryName}</Text>
          <Text className={styles.categoryInfo}>物料数量: {category.materialCount}种</Text>
          {category.description && (
            <Text className={styles.categoryInfo}>描述: {category.description}</Text>
          )}
        </View>
      ))}
    </ScrollView>
  );
};

export default MaterialCategoryPage;
