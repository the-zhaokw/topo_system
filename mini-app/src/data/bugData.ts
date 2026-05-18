import { KpiData, TrendData, Bug, FilterOptions } from '../types/bug';

export const mockKpiData: KpiData = {
  total_bugs: 1256,
  total_change: 12.5,
  new_bugs: 89,
  resolved_bugs: 134,
  unresolved_bugs: 156,
  resolution_rate: 87.5,
  avg_fix_time: 2.3
};

export const mockTrendData: TrendData[] = [
  { date: '05-01', new_bugs: 12, resolved_bugs: 8, cumulative_unresolved: 120 },
  { date: '05-02', new_bugs: 15, resolved_bugs: 10, cumulative_unresolved: 125 },
  { date: '05-03', new_bugs: 8, resolved_bugs: 12, cumulative_unresolved: 121 },
  { date: '05-04', new_bugs: 18, resolved_bugs: 9, cumulative_unresolved: 130 },
  { date: '05-05', new_bugs: 14, resolved_bugs: 15, cumulative_unresolved: 129 },
  { date: '05-06', new_bugs: 20, resolved_bugs: 18, cumulative_unresolved: 131 },
  { date: '05-07', new_bugs: 16, resolved_bugs: 14, cumulative_unresolved: 133 },
  { date: '05-08', new_bugs: 22, resolved_bugs: 16, cumulative_unresolved: 139 },
  { date: '05-09', new_bugs: 19, resolved_bugs: 20, cumulative_unresolved: 138 },
  { date: '05-10', new_bugs: 25, resolved_bugs: 22, cumulative_unresolved: 141 },
  { date: '05-11', new_bugs: 17, resolved_bugs: 18, cumulative_unresolved: 140 },
  { date: '05-12', new_bugs: 21, resolved_bugs: 19, cumulative_unresolved: 142 },
  { date: '05-13', new_bugs: 23, resolved_bugs: 21, cumulative_unresolved: 144 },
  { date: '05-14', new_bugs: 19, resolved_bugs: 20, cumulative_unresolved: 143 },
  { date: '05-15', new_bugs: 26, resolved_bugs: 24, cumulative_unresolved: 145 },
  { date: '05-16', new_bugs: 24, resolved_bugs: 22, cumulative_unresolved: 147 },
  { date: '05-17', new_bugs: 28, resolved_bugs: 25, cumulative_unresolved: 150 },
  { date: '05-18', new_bugs: 30, resolved_bugs: 27, cumulative_unresolved: 153 }
];

export const mockBugList: Bug[] = [
  {
    id: 1,
    title: '用户登录页面无法加载验证码',
    project_name: 'TOPO系统前端',
    status: 'new',
    severity: 'high',
    priority: 'high',
    reporter_name: '张三',
    assignee_name: '李四',
    created_at: '2026-05-18 10:30:00'
  },
  {
    id: 2,
    title: '数据导出功能导出文件损坏',
    project_name: 'TOPO系统后端',
    status: 'in_progress',
    severity: 'critical',
    priority: 'urgent',
    reporter_name: '王五',
    assignee_name: '赵六',
    created_at: '2026-05-17 15:20:00'
  },
  {
    id: 3,
    title: '移动端页面布局错位',
    project_name: 'TOPO系统前端',
    status: 'resolved',
    severity: 'medium',
    priority: 'medium',
    reporter_name: '孙七',
    assignee_name: '周八',
    created_at: '2026-05-16 09:15:00'
  },
  {
    id: 4,
    title: '数据库查询性能下降',
    project_name: 'TOPO系统后端',
    status: 'closed',
    severity: 'high',
    priority: 'high',
    reporter_name: '吴九',
    assignee_name: '郑十',
    created_at: '2026-05-15 14:45:00'
  },
  {
    id: 5,
    title: '报表统计结果不准确',
    project_name: 'TOPO系统前端',
    status: 'reopened',
    severity: 'critical',
    priority: 'urgent',
    reporter_name: '钱十一',
    assignee_name: '陈十二',
    created_at: '2026-05-14 11:30:00'
  },
  {
    id: 6,
    title: '文件上传进度条显示异常',
    project_name: 'TOPO系统前端',
    status: 'new',
    severity: 'low',
    priority: 'low',
    reporter_name: '刘十三',
    assignee_name: '杨十四',
    created_at: '2026-05-18 08:00:00'
  },
  {
    id: 7,
    title: 'API接口返回数据格式错误',
    project_name: 'TOPO系统后端',
    status: 'in_progress',
    severity: 'high',
    priority: 'high',
    reporter_name: '黄十五',
    assignee_name: '林十六',
    created_at: '2026-05-17 16:30:00'
  },
  {
    id: 8,
    title: '权限控制逻辑漏洞',
    project_name: 'TOPO系统后端',
    status: 'resolved',
    severity: 'critical',
    priority: 'urgent',
    reporter_name: '赵十七',
    assignee_name: '钱十八',
    created_at: '2026-05-16 13:20:00'
  },
  {
    id: 9,
    title: '移动端适配问题汇总',
    project_name: 'TOPO系统前端',
    status: 'new',
    severity: 'medium',
    priority: 'medium',
    reporter_name: '孙十九',
    assignee_name: '李二十',
    created_at: '2026-05-18 09:00:00'
  },
  {
    id: 10,
    title: '缓存策略需要优化',
    project_name: 'TOPO系统后端',
    status: 'closed',
    severity: 'suggestion',
    priority: 'low',
    reporter_name: '周二十一',
    assignee_name: '吴二十二',
    created_at: '2026-05-15 10:00:00'
  }
];

export const mockFilterOptions: FilterOptions = {
  projects: [
    { id: 1, name: 'TOPO系统前端' },
    { id: 2, name: 'TOPO系统后端' },
    { id: 3, name: '移动端APP' }
  ],
  bugTypes: ['功能缺陷', '界面问题', '性能问题', '安全问题', '其他'],
  severities: ['critical', 'high', 'medium', 'low', 'suggestion'],
  priorities: ['urgent', 'high', 'medium', 'low'],
  statuses: ['new', 'in_progress', 'resolved', 'closed', 'rejected', 'reopened'],
  users: [
    { id: 1, name: '张三' },
    { id: 2, name: '李四' },
    { id: 3, name: '王五' },
    { id: 4, name: '赵六' }
  ]
};
