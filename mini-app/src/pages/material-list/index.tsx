import React from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';

const MaterialListPage: React.FC = () => {
  const materialData = [
    { name: 'FPGA芯片', no: 'MAT-001', category: '电子元器件', stock: 150, unit: '个', status: '正常' },
    { name: '高速连接器', no: 'MAT-002', category: '连接器', stock: 30, unit: '个', status: '库存不足' },
    { name: 'PCB板', no: 'MAT-003', category: '电路板', stock: 89, unit: '块', status: '正常' },
    { name: '电阻', no: 'MAT-004', category: '电子元器件', stock: 0, unit: '个', status: '缺货' }
  ];

  const getStatusClass = (status: string) => {
    switch (status) {
      case '正常':
        return styles.statusNormal;
      case '库存不足':
        return styles.statusLow;
      case '缺货':
        return styles.statusOut;
      default:
        return '';
    }
  };

  return (
    <ScrollView className={styles.container} scrollY>
      {materialData.map((item, index) => (
        <View key={index} className={styles.materialItem}>
          <Text className={styles.materialName}>{item.name}</Text>
          <Text className={styles.materialInfo}>物料编号: {item.no}</Text>
          <Text className={styles.materialInfo}>类别: {item.category}</Text>
          <Text className={styles.materialInfo}>库存: {item.stock} {item.unit}</Text>
          <Text className={`${styles.materialInfo} ${getStatusClass(item.status)}`}>
            状态: {item.status}
          </Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default MaterialListPage;
