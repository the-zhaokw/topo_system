import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import classnames from 'classnames';
import styles from './index.module.scss';
import { Contract } from '../../types/business';
import { mockContracts } from '../../data/businessData';

const ContractsPage: React.FC = () => {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadContracts();
  }, []);

  const loadContracts = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      setContracts(mockContracts);
      console.log('[Contracts] Loaded contracts:', mockContracts.length);
    } catch (error) {
      console.error('[Contracts] Error loading contracts:', error);
      Taro.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const onPullDownRefresh = () => {
    loadContracts().then(() => {
      Taro.stopPullDownRefresh();
      Taro.showToast({
        title: '刷新成功',
        icon: 'success'
      });
    });
  };

  const getStatusClass = (status: string) => {
    const classMap: Record<string, string> = {
      'draft': styles.statusDraft,
      'pending': styles.statusPending,
      'signed': styles.statusSigned,
      'completed': styles.statusCompleted,
      'cancelled': styles.statusCancelled
    };
    return classMap[status] || '';
  };

  const getStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      'draft': '草稿',
      'pending': '待签署',
      'signed': '已签署',
      'completed': '已完成',
      'cancelled': '已取消'
    };
    return labels[status] || status;
  };

  const formatAmount = (amount: number) => {
    return `¥${amount.toLocaleString()}`;
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  };

  return (
    <View className={styles.container}>
      <ScrollView
        scrollY
        className={styles.contractList}
        enableBackToTop
        onPullDownRefresh={onPullDownRefresh}
      >
        {contracts.length === 0 ? (
          <View className={styles.emptyState}>
            <Text className={styles.emptyIcon}>📄</Text>
            <Text className={styles.emptyText}>暂无合同数据</Text>
            <Text className={styles.emptyHint}>创建第一个合同吧</Text>
          </View>
        ) : (
          <>
            {contracts.map(contract => (
              <View key={contract.id} className={styles.contractCard}>
                <View className={styles.contractHeader}>
                  <Text className={styles.contractNo}>{contract.contract_no}</Text>
                  <Text className={classnames(styles.statusBadge, getStatusClass(contract.status))}>
                    {getStatusLabel(contract.status)}
                  </Text>
                </View>
                <Text className={styles.contractName}>{contract.name}</Text>
                <View className={styles.contractInfo}>
                  <View className={styles.infoItem}>
                    <Text className={styles.infoLabel}>客户</Text>
                    <Text className={styles.infoValue}>{contract.customer_name}</Text>
                  </View>
                  <View className={styles.infoItem}>
                    <Text className={styles.infoLabel}>签署日期</Text>
                    <Text className={styles.infoValue}>{formatDate(contract.sign_date)}</Text>
                  </View>
                </View>
                <View className={styles.contractAmount}>
                  <Text className={styles.amountLabel}>合同金额</Text>
                  <Text className={styles.amountValue}>{formatAmount(contract.amount)}</Text>
                </View>
              </View>
            ))}
          </>
        )}
      </ScrollView>
    </View>
  );
};

export default ContractsPage;
