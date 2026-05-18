export interface Contract {
  id: number;
  contractNo: string;
  contractName: string;
  partyA: string;
  partyB: string;
  amount: number;
  signDate: string;
  startDate: string;
  endDate: string;
  status: '执行中' | '已完成' | '已终止' | '待签署';
  type: string;
  manager: string;
}

export interface ContractStatistics {
  totalCount: number;
  totalAmount: number;
  executingCount: number;
  completedCount: number;
  terminatedCount: number;
  pendingCount: number;
  monthlyTrend: MonthlyTrend[];
  typeDistribution: TypeDist[];
  amountDistribution: AmountDist[];
}

export interface MonthlyTrend {
  month: string;
  count: number;
  amount: number;
}

export interface TypeDist {
  type: string;
  count: number;
  percentage: number;
}

export interface AmountDist {
  range: string;
  count: number;
  percentage: number;
}
