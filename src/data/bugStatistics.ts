// Bug统计 Mock 数据
import { 
  Bug, 
  KpiData, 
  TrendData, 
  DistributionData, 
  TypeDistribution,
  WorkloadData,
  FilterOptions
} from '../types/bugStatistics';

// KPI 数据
export const mockKpiData: KpiData = {
  total_bugs: 1256,
  total_change: 12.5,
  new_bugs: 45,
  resolved_bugs: 38,
  unresolved_bugs: 67,
  resolution_rate: 76.5,
  avg_fix_time: 2.3
};

// 趋势数据
export const mockTrendData: TrendData[] = [
  { date: '05-01', new_bugs: 12, resolved_bugs: 8, cumulative_unresolved: 1200 },
  { date: '05-02', new_bugs: 15, resolved_bugs: 10, cumulative_unresolved: 1205 },
  { date: '05-03', new_bugs: 8, resolved_bugs: 12, cumulative_unresolved: 1201 },
  { date: '05-04', new_bugs: 18, resolved_bugs: 9, cumulative_unresolved: 1210 },
  { date: '05-05', new_bugs: 10, resolved_bugs: 14, cumulative_unresolved: 1206 },
  { date: '05-06', new_bugs: 14, resolved_bugs: 11, cumulative_unresolved: 1209 },
  { date: '05-07', new_bugs: 16, resolved_bugs: 13, cumulative_unresolved: 1212 },
  { date: '05-08', new_bugs: 13, resolved_bugs: 15, cumulative_unresolved: 1210 },
  { date: '05-09', new_bugs: 11, resolved_bugs: 12, cumulative_unresolved: 1209 },
  { date: '05-10', new_bugs: 17, resolved_bugs: 14, cumulative_unresolved: 1212 },
  { date: '05-11', new_bugs: 9, resolved_bugs: 16, cumulative_unresolved: 1205 },
  { date: '05-12', new_bugs: 14, resolved_bugs: 13, cumulative_unresolved: 1206 },
  { date: '05-13', new_bugs: 16, resolved_bumps: 11, cumulative_unresolved: 1211 },
  { date: '05-14', new_bugs: 12, resolved_bugs: 15, cumulative_unresolved: 1208 },
  { date: '05-15', new_bugs: 18, resolved_bugs: 14, cumulative_unresolved: 1212 },
  { date: '05-16', new_bugs: 15, resolved_bugs: 16, cumulative_unresolved: 1211 },
  { date: '05-17', new_bugs: 13, resolved_bugs: 14, cumulative_unresolved: 1210 },
  { date: '05-18', new_bugs: 17, resolved_bugs: 15, cumulative_unresolved: 1212 }
];

// 分布数据
export const mockDistributionData: DistributionData = {
  '前端项目': { total: 456, new: 120, resolved: 280, closed: 56 },
  '后端服务': { total: 389, new: 98, resolved: 245, closed: 46 },
  '移动端': { total: 234, new: 67, resolved: 134, closed: 33 },
  '数据库': { total: 98, new: 23, resolved: 65, closed: 10 },
  '基础设施': { total: 79, new: 18, resolved: 51, closed: 10 }
};

// 类型分布
export const mockTypeDistribution: TypeDistribution[] = [
  { name: '功能缺陷', value: 567 },
  { name: '界面显示', value: 289 },
  { name: '性能问题', value: 156 },
  { name: '安全漏洞', value: 89 },
  { name: '兼容性问题', value: 98 },
  { name: '其他', value: 57 }
];

// 严重程度分布
export const mockSeverityDistribution: DistributionData = {
  'critical': { total: 45, new: 12, resolved: 28, closed: 5 },
  'high': { total: 189, new: 45, resolved: 112, closed: 32 },
  'medium': { total: 567, new: 134, resolved: 356, closed: 77 },
  'low': { total: 389, new: 89, reverse: 245, closed: 55 },
  'suggestion': { total: 66, new: 15, resolved: 45, closed: 6 }
};

// 工作量数据
export const mockWorkloadData: WorkloadData[] = [
  { name: '张三', assigned: 15, in_progress: 8, resolved: 12, closed: 3 },
  { name: '李四', assigned: 12, in_progress: 6, resolved: 15, closed: 5 },
  { name: '王五', assigned: 18, in_progress: 10, resolved: 14, closed: 4 },
  { name: '赵六', assigned: 10, in_progress: 5, resolved: 11, closed: 3 },
  { name: '钱七', assigned: 14, in_progress: 7, resolved: 13, closed: 4 },
  { name: '孙八', assigned: 16, in_progress: 9, resolved: 10, closed: 3 },
  { name: '周九', assigned: 11, in_progress: 6, resolved: 14, closed: 5 },
  { name: '吴十', assigned: 13, in_progress: 8, resolved: 12, closed: 4 }
];

// Bug 列表数据
export const mockBugList: Bug[] = [
  {
    id: 1,
    title: '用户登录页面加载缓慢',
    project_name: '前端项目',
    status: 'new',
    severity: 'high',
    priority: 'high',
    reporter_name: '张三',
    created_at: '2024-05-18 10:30:00'
  },
  {
    id: 2,
    title: '支付回调接口偶发性超时',
    project_name: '后端服务',
    status: 'in_progress',
    severity: 'critical',
    priority: 'urgent',
    reporter_name: '李四',
    created_at: '2024-05-18 09:15:00'
  },
  {
    id: 3,
    title: 'iOS端图片上传失败',
    project_name: '移动端',
    status: 'resolved',
    severity: 'medium',
    priority: 'medium',
    reporter_name: '王五',
    created_at: '2024-05-17 16:45:00'
  },
  {
    id: 4,
    title: '数据库查询性能优化',
    project_name: '数据库',
    status: 'closed',
    severity: 'low',
    priority: 'low',
    reporter_name: '赵六',
    created_at: '2024-05-16 14:20:00'
  },
  {
    id: 5,
    title: '移动端适配问题汇总',
    project_name: '移动端',
    status: 'in_progress',
    severity: 'medium',
    priority: 'medium',
    reporter_name: '钱七',
    created_at: '2024-05-17 11:30:00'
  },
  {
    id: 6,
    title: 'API接口文档缺失',
    project_name: '后端服务',
    status: 'new',
    severity: 'low',
    priority: 'low',
    reporter_name: '孙八',
    created_at: '2024-05-18 08:00:00'
  },
  {
    id: 7,
    title: '用户权限验证漏洞',
    project_name: '前端项目',
    status: 'in_progress',
    severity: 'critical',
    priority: 'urgent',
    reporter_name: '周九',
    created_at: '2024-05-18 07:30:00'
  },
  {
    id: 8,
    title: '服务器内存泄漏',
    project_name: '基础设施',
    status: 'resolved',
    severity: 'high',
    priority: 'high',
    reporter_name: '吴十',
    created_at: '2024-05-17 15:00:00'
  },
  {
    id: 9,
    title: '表单验证规则不统一',
    project_name: '前端项目',
    status: 'new',
    severity: 'medium',
    priority: 'medium',
    reporter_name: '张三',
    created_at: '2024-05-18 10:00:00'
  },
  {
    id: 10,
    title: '数据库索引缺失导致查询慢',
    project_name: '数据库',
    status: 'in_progress',
    severity: 'high',
    priority: 'high',
    reporter_name: '李四',
    created_at: '2024-05-17 13:45:00'
  }
];

// 筛选选项
export const mockFilterOptions: FilterOptions = {
  projects: [
    { id: '1', name: '前端项目' },
    { id: '2', name: '后端服务' },
    { id: '3', name: '移动端' },
    { id: '4', name: '数据库' },
    { id: '5', name: '基础设施' }
  ],
  bugTypes: ['功能缺陷', '界面显示', '性能问题', '安全漏洞', '兼容性问题'],
  severities: ['critical', 'high', 'medium', 'low', 'suggestion'],
  priorities: ['urgent', 'high', 'medium', 'low'],
  statuses: ['new', 'assigned', 'in_progress', 'resolved', 'verified', 'closed', 'rejected', 'reopened'],
  users: [
    { id: '1', name: '张三' },
    { id: '2', name: '李四' },
    { id: '3', name: '王五' },
    { id: '4', name: '赵六' },
    { id: '5', name: '钱七' },
    { id: '6', name: '孙八' },
    { id: '7', name: '周九' },
    { id: '8', name: '吴十' }
  ]
};
