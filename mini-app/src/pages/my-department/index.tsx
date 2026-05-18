import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';
import { mockDepartment } from '../../data/business';

const MyDepartmentPage: React.FC = () => {
  const [departments] = useState(mockDepartment);

  return (
    <ScrollView className={styles.container} scrollY>
      {departments.map((dept, index) => (
        <View key={index} className={styles.departmentItem}>
          <Text className={styles.departmentName}>{dept.departmentName}</Text>
          <Text className={styles.departmentInfo}>负责人: {dept.manager}</Text>
          <Text className={styles.departmentInfo}>成员数量: {dept.memberCount}</Text>
          {dept.description && (
            <Text className={styles.departmentInfo}>描述: {dept.description}</Text>
          )}
          {dept.children && dept.children.length > 0 && (
            <View className={styles.subDepartment}>
              {dept.children.map((child, childIndex) => (
                <View key={childIndex} style={{ marginBottom: '24rpx' }}>
                  <Text className={styles.departmentName}>{child.departmentName}</Text>
                  <Text className={styles.departmentInfo}>负责人: {child.manager}</Text>
                  <Text className={styles.departmentInfo}>成员数量: {child.memberCount}</Text>
                </View>
              ))}
            </View>
          )}
        </View>
      ))}
    </ScrollView>
  );
};

export default MyDepartmentPage;
