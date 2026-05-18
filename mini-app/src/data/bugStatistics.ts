import { BugStatistics } from '../types/bugStatistics';

export const mockBugStatistics: BugStatistics = {
  total: 156,
  open: 45,
  inProgress: 23,
  resolved: 67,
  closed: 21,
  criticalCount: 8,
  highCount: 34,
  mediumCount: 78,
  lowCount: 36,
  todayCreated: 5,
  todayResolved: 3,
  weeklyTrend: [
    { date: '2026-05-12', created: 12, resolved: 8 },
    { date: '2026-05-13', created: 15, resolved: 10 },
    { date: '2026-05-14', created: 8, resolved: 12 },
    { date: '2026-05-15', created: 18, resolved: 14 },
    { date: '2026-05-16', created: 10, resolved: 16 },
    { date: '2026-05-17', created: 6, resolved: 9 },
    { date: '2026-05-18', created: 5, resolved: 3 }
  ],
  projectDistribution: [
    { projectName: 'TOPO系统', count: 56, percentage: 35.9 },
    { projectName: '合同管理系统', count: 34, percentage: 21.8 },
    { projectName: '物料追踪系统', count: 28, percentage: 17.9 },
    { projectName: '考勤管理系统', count: 21, percentage: 13.5 },
    { projectName: '知识库系统', count: 17, percentage: 10.9 }
  ],
  statusDistribution: [
    { status: '新建', count: 28, percentage: 17.9 },
    { status: '待分配', count: 17, percentage: 10.9 },
    { status: '开发中', count: 23, percentage: 14.7 },
    { status: '待验证', count: 45, percentage: 28.8 },
    { status: '已关闭', count: 43, percentage: 27.6 }
  ],
  priorityDistribution: [
    { priority: '严重', count: 8, percentage: 5.1 },
    { priority: '高', count: 34, percentage: 21.8 },
    { priority: '中', count: 78, percentage: 50.0 },
    { priority: '低', count: 36, percentage: 23.1 }
  ]
};
