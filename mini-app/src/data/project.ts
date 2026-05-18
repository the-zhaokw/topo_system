import { ProjectStatistics, ProjectBug, ProjectLog } from '../types/project';

export const mockProjectStatistics: ProjectStatistics = {
  totalProjects: 12,
  ongoingProjects: 8,
  completedProjects: 3,
  overdueProjects: 1,
  totalBudget: 5000000,
  totalSpent: 3200000,
  averageProgress: 68.5,
  projectTypeDistribution: [
    { type: '软件开发', count: 6, percentage: 50.0 },
    { type: '系统集成', count: 3, percentage: 25.0 },
    { type: '运维服务', count: 2, percentage: 16.7 },
    { type: '咨询服务', count: 1, percentage: 8.3 }
  ],
  projectStatusDistribution: [
    { status: '进行中', count: 8, percentage: 66.7 },
    { status: '已完成', count: 3, percentage: 25.0 },
    { status: '已暂停', count: 1, percentage: 8.3 }
  ],
  monthlyTrend: [
    { month: '2026-01', created: 3, completed: 1 },
    { month: '2026-02', created: 2, completed: 2 },
    { month: '2026-03', created: 4, completed: 1 },
    { month: '2026-04', created: 3, completed: 2 },
    { month: '2026-05', created: 2, completed: 1 }
  ],
  resourceUtilization: [
    { resourceName: '开发人员', assigned: 15, available: 20, utilizationRate: 75.0 },
    { resourceName: '测试人员', assigned: 8, available: 10, utilizationRate: 80.0 },
    { resourceName: '项目经理', assigned: 5, available: 6, utilizationRate: 83.3 }
  ]
};

export const mockProjectBug: ProjectBug[] = [
  {
    id: 1,
    bugNo: 'BUG-2026-156',
    bugName: '用户列表加载慢',
    severity: '高',
    status: '开发中',
    assignee: '张三',
    reporter: '李四',
    createTime: '2026-05-15 10:30',
    projectName: 'TOPO系统'
  },
  {
    id: 2,
    bugNo: 'BUG-2026-157',
    bugName: '登录页面样式错位',
    severity: '中',
    status: '待分配',
    reporter: '王五',
    createTime: '2026-05-16 14:20',
    projectName: 'TOPO系统'
  }
];

export const mockProjectLog: ProjectLog[] = [
  {
    id: 1,
    logNo: 'PL-2026-045',
    logType: '进度更新',
    title: '完成用户管理模块开发',
    content: '用户管理模块已完成开发,包括用户CRUD、角色管理、权限分配等功能',
    projectName: 'TOPO系统',
    operator: '张三',
    operateTime: '2026-05-18 10:30',
    attachments: ['进度报告.pdf']
  },
  {
    id: 2,
    logNo: 'PL-2026-044',
    logType: '风险识别',
    title: '发现关键技术风险',
    content: '第三方支付接口不稳定,需要准备备选方案',
    projectName: '合同管理系统',
    operator: '李四',
    operateTime: '2026-05-17 16:45'
  }
];
