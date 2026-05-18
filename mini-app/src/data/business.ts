import { User, Department, Activity, WorkLog, WorkStatistics, Risk, MonitoringItem } from '../types/business';

export const mockUser: User[] = [
  {
    id: 1,
    username: 'admin',
    realName: '系统管理员',
    email: 'admin@topo.com',
    phone: '13800138000',
    department: '技术部',
    position: '系统管理员',
    role: '管理员',
    status: '在职',
    avatar: 'https://picsum.photos/id/64/200/200',
    joinDate: '2020-01-01'
  },
  {
    id: 2,
    username: 'zhangsan',
    realName: '张三',
    email: 'zhangsan@topo.com',
    phone: '13800138001',
    department: '研发部',
    position: '项目经理',
    role: '项目经理',
    status: '在职',
    avatar: 'https://picsum.photos/id/91/200/200',
    joinDate: '2021-03-15'
  }
];

export const mockDepartment: Department[] = [
  {
    id: 1,
    departmentName: '技术部',
    manager: '系统管理员',
    memberCount: 45,
    description: '负责公司技术研发',
    children: [
      { id: 11, departmentName: '研发部', manager: '研发总监', memberCount: 20, parentId: 1 },
      { id: 12, departmentName: '测试部', manager: '测试总监', memberCount: 10, parentId: 1 },
      { id: 13, departmentName: '运维部', manager: '运维总监', memberCount: 8, parentId: 1 }
    ]
  },
  {
    id: 2,
    departmentName: '市场部',
    manager: '市场总监',
    memberCount: 15,
    description: '负责市场拓展'
  }
];

export const mockActivity: Activity[] = [
  {
    id: 1,
    activityType: '项目更新',
    title: 'TOPO系统完成v2.0版本开发',
    content: 'TOPO系统已完成v2.0版本的开发工作,包含20个新功能点和15个优化项',
    projectName: 'TOPO系统',
    operator: '张三',
    operateTime: '2026-05-18 10:30'
  },
  {
    id: 2,
    activityType: 'Bug变更',
    title: '修复了Bug #156',
    content: '修复了物料列表页面加载慢的问题',
    projectName: 'TOPO系统',
    operator: '李四',
    operateTime: '2026-05-18 09:15'
  }
];

export const mockWorkLog: WorkLog[] = [
  {
    id: 1,
    logNo: 'WL-2026051801',
    projectName: 'TOPO系统',
    workContent: '完成用户管理模块的单元测试',
    workHours: 6,
    workDate: '2026-05-17',
    submitter: '张三',
    submitTime: '2026-05-17 18:30',
    status: '已通过',
    approver: '项目经理A',
    approveTime: '2026-05-18 09:00'
  },
  {
    id: 2,
    logNo: 'WL-2026051802',
    projectName: '合同管理系统',
    workContent: '修复合同审批流程中的bug',
    workHours: 4,
    workDate: '2026-05-17',
    submitter: '李四',
    submitTime: '2026-05-17 17:45',
    status: '待审核'
  }
];

export const mockWorkStatistics: WorkStatistics = {
  totalHours: 168,
  normalHours: 160,
  overtimeHours: 8,
  projectDistribution: [
    { projectName: 'TOPO系统', hours: 80, percentage: 47.6 },
    { projectName: '合同管理系统', hours: 45, percentage: 26.8 },
    { projectName: '物料追踪系统', hours: 43, percentage: 25.6 }
  ],
  weeklyTrend: [
    { week: '第20周', hours: 42 },
    { week: '第21周', hours: 40 },
    { week: '第22周', hours: 44 },
    { week: '第23周', hours: 42 }
  ],
  monthlySummary: [
    { month: '2026-01', normalHours: 160, overtimeHours: 12, totalHours: 172 },
    { month: '2026-02', normalHours: 152, overtimeHours: 8, totalHours: 160 },
    { month: '2026-03', normalHours: 168, overtimeHours: 16, totalHours: 184 }
  ]
};

export const mockRisk: Risk[] = [
  {
    id: 1,
    riskNo: 'RSK-2026-001',
    riskName: '关键人员离职风险',
    projectName: 'TOPO系统',
    category: '资源风险',
    probability: '高',
    impact: '高',
    level: '严重',
    status: '监控中',
    owner: '项目经理A',
    createTime: '2026-04-15',
    description: '核心开发人员可能在项目关键时期离职',
    mitigationPlan: '1. 做好知识备份\n2. 培养备选人员\n3. 及时沟通了解人员动态'
  },
  {
    id: 2,
    riskNo: 'RSK-2026-002',
    riskName: '第三方接口不稳定',
    projectName: '合同管理系统',
    category: '技术风险',
    probability: '中',
    impact: '中',
    level: '中',
    status: '应对计划',
    owner: '技术负责人B',
    createTime: '2026-05-01',
    description: '依赖的第三方支付接口不稳定',
    mitigationPlan: '1. 准备备选方案\n2. 实施接口监控\n3. 及时切换'
  }
];

export const mockMonitoringItem: MonitoringItem[] = [
  {
    id: 1,
    monitorName: '系统CPU使用率',
    monitorType: '系统监控',
    status: '正常',
    lastCheckTime: '2026-05-18 11:00',
    value: '45%',
    threshold: '<80%',
    description: '服务器CPU使用率监控'
  },
  {
    id: 2,
    monitorName: '数据库连接池',
    monitorType: '性能监控',
    status: '警告',
    lastCheckTime: '2026-05-18 11:00',
    value: '85%',
    threshold: '<90%',
    description: '数据库连接池使用率'
  },
  {
    id: 3,
    monitorName: '接口响应时间',
    monitorType: '性能监控',
    status: '正常',
    lastCheckTime: '2026-05-18 11:00',
    value: '120ms',
    threshold: '<500ms',
    description: '核心接口平均响应时间'
  }
];
