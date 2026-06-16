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

// ============== 项目 ==============
export interface Project {
  id: number;
  name: string;
  description: string;
  status: 'planning' | 'active' | 'completed' | 'suspended';
  start_date: string;
  end_date?: string;
  manager_name: string;
  member_count: number;
  bug_count: number;
  completion_rate: number;
}

// ============== 待办事项 ==============
export type TodoPriority = 'urgent' | 'high' | 'medium' | 'low';
export type TodoStatus = 'pending' | 'in_progress' | 'completed';
export type TodoCategory = 'approval' | 'bug' | 'review' | 'contract';

export interface Todo {
  id: number;
  title: string;
  description?: string;
  priority: TodoPriority;
  status: TodoStatus;
  category?: TodoCategory;
  due_date?: string;
  created_at: string;
  assignee_name?: string;
  project_name?: string;
}

// ============== 考勤 ==============
export type AttendanceStatus = 'normal' | 'late' | 'absent' | 'leave';

export interface Attendance {
  id: number;
  user_name: string;
  date: string;
  check_in_time?: string;
  check_out_time?: string;
  status: AttendanceStatus;
  work_hours: number;
}

// ============== 物料 ==============
export interface Material {
  id: number;
  name: string;
  code: string;
  category: string;
  unit: string;
  stock: number;
  price: number;
  warehouse: string;
  location: string;
}

// ============== 知识库 ==============
export interface KnowledgeArticle {
  id: number;
  title: string;
  category: string;
  author: string;
  created_at: string;
  view_count: number;
  summary?: string;
  content?: string;
}

// ============== 通知 ==============
export type NotificationType = 'info' | 'warning' | 'success' | 'error';

export interface Notification {
  id: number;
  title: string;
  content: string;
  type: NotificationType;
  is_read: boolean;
  created_at: string;
  link?: string;
  target_type?: string;
  target_id?: number;
}

// ============== 个人计划 ==============
export type PlanType = 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
export type PlanStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';

export interface PersonalPlan {
  id: number;
  title: string;
  plan_type: PlanType;
  start_time: string;
  end_time: string;
  status: PlanStatus;
  progress: number;
  description?: string;
}

// ============== 合同（与 businessData 中的 mockContracts 字段保持一致） ==============
export type ContractStatus = 'draft' | 'pending' | 'signed' | 'completed' | 'terminated';

export interface Contract {
  id: number;
  contract_no: string;
  name: string;
  customer_name: string;
  amount: number;
  sign_date: string;
  status: ContractStatus;
  project_name?: string;
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
