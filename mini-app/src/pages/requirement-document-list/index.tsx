import React, { useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';
import { mockRequirementDocument } from '../../data/requirement';

const RequirementDocumentListPage: React.FC = () => {
  const [documentList] = useState(mockRequirementDocument);

  const getStatusClass = (status: string) => {
    return status === '已发布' ? styles.statusPublished : styles.statusReviewing;
  };

  return (
    <ScrollView className={styles.container} scrollY>
      {documentList.map((doc, index) => (
        <View
          key={index}
          className={styles.documentItem}
          onClick={() => Taro.navigateTo({ url: `/pages/requirement-document-detail/index?id=${doc.id}` })}
        >
          <Text className={styles.documentName}>{doc.documentName}</Text>
          <Text className={styles.documentInfo}>文档编号: {doc.documentNo}</Text>
          <Text className={styles.documentInfo}>版本: {doc.version}</Text>
          <Text className={styles.documentInfo}>项目: {doc.projectName}</Text>
          <Text className={styles.documentInfo}>模块: {doc.module}</Text>
          <Text className={styles.documentInfo}>需求数量: {doc.requirementCount}</Text>
          <Text className={styles.documentInfo}>作者: {doc.author}</Text>
          <Text className={`${styles.statusTag} ${getStatusClass(doc.status)}`}>
            {doc.status}
          </Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default RequirementDocumentListPage;
