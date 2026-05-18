import { ContractStatistics } from '../types/contract';

export const mockContractStatistics: ContractStatistics = {
  totalCount: 45,
  totalAmount: 12500000,
  executingCount: 28,
  completedCount: 12,
  terminatedCount: 2,
  pendingCount: 3,
  monthlyTrend: [
    { month: '2026-01', count: 5, amount: 1500000 },
    { month: '2026-02', count: 3, amount: 800000 },
    { month: '2026-03', count: 7, amount: 2200000 },
    { month: '2026-04', count: 6, amount: 1800000 },
    { month: '2026-05', count: 4, amount: 1200000 }
  ],
  typeDistribution: [
    { type: '软件开发合同', count: 18, percentage: 40.0 },
    { type: '技术服务合同', count: 12, percentage: 26.7 },
    { type: '设备采购合同', count: 8, percentage: 17.8 },
    { type: '运维服务合同', count: 7, percentage: 15.6 }
  ],
  amountDistribution: [
    { range: '10万以下', count: 15, percentage: 33.3 },
    { range: '10-50万', count: 18, percentage: 40.0 },
    { range: '50-100万', count: 8, percentage: 17.8 },
    { range: '100万以上', count: 4, percentage: 8.9 }
  ]
};
