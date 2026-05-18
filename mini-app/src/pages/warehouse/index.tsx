import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';
import { mockWarehouse } from '../../data/material';

const WarehousePage: React.FC = () => {
  const [warehouseList] = useState(mockWarehouse);

  return (
    <ScrollView className={styles.container} scrollY>
      {warehouseList.map((warehouse, index) => (
        <View key={index} className={styles.warehouseItem}>
          <Text className={styles.warehouseName}>{warehouse.warehouseName}</Text>
          <Text className={styles.warehouseInfo}>地址: {warehouse.address}</Text>
          <Text className={styles.warehouseInfo}>负责人: {warehouse.manager}</Text>
          <Text className={styles.warehouseInfo}>容量: {warehouse.capacity}</Text>
          <Text className={styles.warehouseInfo}>当前库存: {warehouse.currentStock}</Text>
          <View className={styles.utilizationBar}>
            <View
              className={styles.utilizationFill}
              style={{ width: `${warehouse.utilizationRate}%` }}
            />
          </View>
          <Text style={{ fontSize: '24rpx', color: '#22C55E', fontWeight: '600' }}>
            利用率: {warehouse.utilizationRate}%
          </Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default WarehousePage;
