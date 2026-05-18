import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';
import { mockSerialNumber } from '../../data/material';

const SerialNumberPage: React.FC = () => {
  const [serialList] = useState(mockSerialNumber);

  const getStatusClass = (status: string) => {
    return status === '库存' ? styles.statusInStock : styles.statusInUse;
  };

  return (
    <ScrollView className={styles.container} scrollY>
      {serialList.map((serial, index) => (
        <View key={index} className={styles.serialItem}>
          <Text className={styles.serialNo}>{serial.serialNo}</Text>
          <Text className={styles.serialInfo}>物料: {serial.materialName}</Text>
          <Text className={styles.serialInfo}>仓库: {serial.warehouse}</Text>
          <Text className={styles.serialInfo}>位置: {serial.location}</Text>
          <Text className={styles.serialInfo}>购买日期: {serial.purchaseDate}</Text>
          <Text className={`${styles.statusTag} ${getStatusClass(serial.status)}`}>
            {serial.status}
          </Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default SerialNumberPage;
