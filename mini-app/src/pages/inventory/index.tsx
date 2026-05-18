import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';
import { mockInventoryItem } from '../../data/material';

const InventoryPage: React.FC = () => {
  const [inventoryList] = useState(mockInventoryItem);

  const getStatusClass = (status: string) => {
    switch (status) {
      case '正常':
        return styles.statusNormal;
      case '库存不足':
        return styles.statusWarning;
      case '库存过剩':
        return styles.statusError;
      default:
        return '';
    }
  };

  return (
    <ScrollView className={styles.container} scrollY>
      {inventoryList.map((item, index) => (
        <View key={index} className={styles.inventoryItem}>
          <Text className={styles.materialName}>{item.materialName}</Text>
          <Text className={styles.materialInfo}>物料编号: {item.materialNo}</Text>
          <Text className={styles.materialInfo}>仓库: {item.warehouse}</Text>
          <Text className={styles.materialInfo}>位置: {item.location}</Text>
          <Text className={styles.materialInfo}>数量: {item.quantity} {item.unit}</Text>
          <Text className={styles.materialInfo}>
            安全库存: {item.minStock} - {item.maxStock}
          </Text>
          <Text className={`${styles.materialInfo} ${getStatusClass(item.status)}`}>
            状态: {item.status}
          </Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default InventoryPage;
