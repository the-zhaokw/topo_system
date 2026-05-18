export interface User {
  id: number;
  username: string;
  realName: string;
  email: string;
  phone?: string;
  department: string;
  position: string;
  role: '管理员' | '项目经理' | '开发人员' | '测试人员' | '普通用户';
  status: '在职' | '离职' | '休假';
  avatar?: string;
  joinDate: string;
}

export interface Department {
  id: number;
  departmentName: string;
  parentId?: number;
  manager: string;
  memberCount: number;
  description?: string;
  children?: Department[];
}

export interface Activity {
  id: number;
  activityType: '项目更新' | 'Bug变更' | '需求变更' | '文档更新' | '系统通知';
  title: string;
  content: string;
  projectName?: string;
  operator: string;
  operateTime: string;
  relatedId?: number;
}

export interface WorkLog {
  id: number;
  logNo: string;
  projectName: string;
  workContent: string;
  workHours: number;
  workDate: string;
  submitter: string;
  submitTime: string;
  status: '待审核' | '已通过' | '已驳回';
  approver?: string;
  approveTime?: string;
}

export interface WorkStatistics {
  totalHours: number;
  normalHours: number;
  overtimeHours: number;
  projectDistribution: ProjectHours[];
  weeklyTrend: WeeklyHours[];
  monthlySummary: MonthlySummary[];
}

export interface ProjectHours {
  projectName: string;
  hours: number;
  percentage: number;
}

export interface WeeklyHours {
  week: string;
  hours: number;
}

export interface MonthlySummary {
  month: string;
  normalHours: number;
  overtimeHours: number;
  totalHours: number;
}

export interface Risk {
  id: number;
  riskNo: string;
  riskName: string;
  projectName: string;
  category: '技术风险' | '进度风险' | '资源风险' | '质量风险' | '外部风险';
  probability: '高' | '中' | '低';
  impact: '高' | '中' | '低';
  level: '严重' | '高' | '中' | '低';
  status: '识别' | '评估中' | '应对计划' | '监控中' | '已解决' | '已接受';
  owner: string;
  createTime: string;
  description?: string;
  mitigationPlan?: string;
}

export interface MonitoringItem {
  id: number;
  monitorName: string;
  monitorType: '系统监控' | '性能监控' | '业务监控' | '安全监控';
  status: '正常' | '警告' | '异常';
  lastCheckTime: string;
  value?: string;
  threshold?: string;
  description?: string;
}
