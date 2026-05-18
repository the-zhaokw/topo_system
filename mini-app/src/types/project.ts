export interface ProjectForm {
  id?: number;
  projectName: string;
  projectCode: string;
  projectType: string;
  description?: string;
  startDate: string;
  endDate: string;
  status: '筹备中' | '进行中' | '已完成' | '已终止' | '已暂停';
  priority: '高' | '中' | '低';
  manager: string;
  teamMembers: string[];
  budget?: number;
  milestones?: Milestone[];
  objectives?: string;
  risks?: string;
}

export interface Milestone {
  id: number;
  milestoneName: string;
  planDate: string;
  actualDate?: string;
  status: '待完成' | '已完成' | '延期';
  deliverable?: string;
}

export interface ProjectStatistics {
  totalProjects: number;
  ongoingProjects: number;
  completedProjects: number;
  overdueProjects: number;
  totalBudget: number;
  totalSpent: number;
  averageProgress: number;
  projectTypeDistribution: TypeDist[];
  projectStatusDistribution: StatusDist[];
  monthlyTrend: MonthlyTrend[];
  resourceUtilization: ResourceUtil[];
}

export interface TypeDist {
  type: string;
  count: number;
  percentage: number;
}

export interface StatusDist {
  status: string;
  count: number;
  percentage: number;
}

export interface MonthlyTrend {
  month: string;
  created: number;
  completed: number;
}

export interface ResourceUtil {
  resourceName: string;
  assigned: number;
  available: number;
  utilizationRate: number;
}

export interface ProjectBug {
  id: number;
  bugNo: string;
  bugName: string;
  severity: '严重' | '高' | '中' | '低';
  status: '新建' | '待分配' | '开发中' | '待验证' | '已关闭';
  assignee?: string;
  reporter: string;
  createTime: string;
  projectName: string;
}

export interface ProjectLog {
  id: number;
  logNo: string;
  logType: '进度更新' | '风险识别' | '问题记录' | '变更记录' | '里程碑完成';
  title: string;
  content: string;
  projectName: string;
  operator: string;
  operateTime: string;
  attachments?: string[];
}
