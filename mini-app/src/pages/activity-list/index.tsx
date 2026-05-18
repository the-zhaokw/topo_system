import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import styles from './index.module.scss';
import { mockActivity } from '../../data/business';

const ActivityListPage: React.FC = () => {
  const [activityList] = useState(mockActivity);

  return (
    <ScrollView className={styles.container} scrollY>
      {activityList.map((activity, index) => (
        <View key={index} className={styles.activityItem}>
          <Text className={styles.activityType}>{activity.activityType}</Text>
          <Text className={styles.activityTitle}>{activity.title}</Text>
          <Text className={styles.activityContent}>{activity.content}</Text>
          <Text className={styles.activityMeta}>
            {activity.projectName ? `${activity.projectName} | ` : ''}{activity.operator} | {activity.operateTime}
          </Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default ActivityListPage;
