import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';
import { mockLocation } from '../../data/material';

const LocationPage: React.FC = () => {
  const [locationList] = useState(mockLocation);

  return (
    <ScrollView className={styles.container} scrollY>
      {locationList.map((location, index) => (
        <View key={index} className={styles.locationItem}>
          <Text className={styles.locationCode}>{location.locationCode}</Text>
          <Text className={styles.locationInfo}>仓库: {location.warehouseName}</Text>
          <Text className={styles.locationInfo}>分区: {location.zone}</Text>
          <Text className={styles.locationInfo}>货架: {location.shelf}</Text>
          <Text className={styles.locationInfo}>容量: {location.capacity}</Text>
          <Text className={styles.locationInfo}>当前库存: {location.currentStock}</Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default LocationPage;
