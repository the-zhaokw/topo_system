import React from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';

const ContractListPage: React.FC = () => {
  const contractData = [
    {
      no: 'HT-2026-001',
      name: 'TOPO系统开发合同',
      partyA: 'XX科技',
      partyB: '我们的公司',
      amount: 500000,
      signDate: '2026-01-15',
      status: '执行中'
    },
    {
      no: 'HT-2026-002',
      name: '物料采购合同',
      partyA: '我们的公司',
      partyB: 'YY供应商',
      amount: 200000,
      signDate: '2026-02-20',
      status: '已完成'
    },
    {
      no: 'HT-2026-003',
      name: '技术服务合同',
      partyA: 'ZZ企业',
      partyB: '我们的公司',
      amount: 300000,
      signDate: '2026-03-10',
      status: '待签署'
    }
  ];

  const getStatusClass = (status: string) => {
    switch (status) {
      case '执行中':
        return styles.statusExecuting;
      case '已完成':
        return styles.statusCompleted;
      case '待签署':
        return styles.statusPending;
      default:
        return '';
    }
  };

  return (
    <ScrollView className={styles.container} scrollY>
      {contractData.map((contract, index) => (
        <View
          key={index}
          className={styles.contractItem}
          onClick={() => Taro.navigateTo({ url: '/pages/contract-detail/index' })}
        >
          <Text className={styles.contractName}>{contract.name}</Text>
          <Text className={styles.contractInfo}>合同编号: {contract.no}</Text>
          <Text className={styles.contractInfo}>甲方: {contract.partyA}</Text>
          <Text className={styles.contractInfo}>乙方: {contract.partyB}</Text>
          <Text className={styles.contractInfo}>金额: ¥{contract.amount.toLocaleString()}</Text>
          <Text className={styles.contractInfo}>签订日期: {contract.signDate}</Text>
          <Text className={`${styles.contractInfo} ${getStatusClass(contract.status)}`}>
            状态: {contract.status}
          </Text>
        </View>
      ))}
    </ScrollView>
  );
};

export default ContractListPage;
