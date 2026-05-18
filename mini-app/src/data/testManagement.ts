import { TestDashboard, TestSuite, TestCase, TestExecution, TestReport } from '../types/testManagement';

export const mockTestDashboard: TestDashboard = {
  totalSuites: 25,
  totalCases: 1256,
  passedCases: 892,
  failedCases: 123,
  blockedCases: 45,
  untestedCases: 196,
  passRate: 71.0,
  recentExecutions: [
    {
      id: 1,
      suiteName: '用户管理模块',
      executedBy: '测试员A',
      executedAt: '2026-05-18 10:30',
      passRate: 85.5,
      duration: 45
    },
    {
      id: 2,
      suiteName: '合同管理模块',
      executedBy: '测试员B',
      executedAt: '2026-05-18 09:15',
      passRate: 92.3,
      duration: 38
    }
  ],
  suiteSummary: [
    { suiteName: '用户管理模块', totalCases: 156, passedCases: 134, failedCases: 15, passRate: 86.1 },
    { suiteName: '合同管理模块', totalCases: 98, passedCases: 89, failedCases: 6, passRate: 90.8 },
    { suiteName: '物料管理模块', totalCases: 234, passedCases: 198, failedCases: 23, passRate: 84.6 }
  ],
  weeklyTrend: [
    { week: '第20周', passed: 245, failed: 32, total: 289 },
    { week: '第21周', passed: 267, failed: 28, total: 312 },
    { week: '第22周', passed: 289, failed: 25, total: 334 },
    { week: '第23周', passed: 312, failed: 22, total: 356 }
  ]
};

export const mockTestSuite: TestSuite[] = [
  {
    id: 1,
    suiteName: '用户管理模块',
    projectName: 'TOPO系统',
    module: '用户模块',
    caseCount: 156,
    lastExecution: '2026-05-18 10:30',
    passRate: 86.1,
    status: '正常',
    description: '包含用户注册、登录、权限管理等功能测试'
  },
  {
    id: 2,
    suiteName: '合同管理模块',
    projectName: '合同管理系统',
    module: '合同模块',
    caseCount: 98,
    lastExecution: '2026-05-18 09:15',
    passRate: 90.8,
    status: '正常',
    description: '包含合同创建、审批、归档等功能测试'
  }
];

export const mockTestCase: TestCase[] = [
  {
    id: 1,
    caseNo: 'TC-USER-001',
    caseName: '用户登录-正确账号密码',
    priority: 'P0',
    type: '功能测试',
    precondition: '用户已注册',
    testSteps: [
      { stepNo: 1, description: '打开登录页面', testData: '', expectedResult: '页面正常显示' },
      { stepNo: 2, description: '输入正确的用户名和密码', testData: '用户名:test, 密码:123456', expectedResult: '输入框正常显示输入内容' },
      { stepNo: 3, description: '点击登录按钮', testData: '', expectedResult: '登录成功,跳转到首页' }
    ],
    expectedResult: '登录成功,显示用户信息',
    status: '通过',
    lastExecutionResult: '通过',
    lastExecutionTime: '2026-05-18 10:30',
    executor: '测试员A'
  }
];

export const mockTestExecution: TestExecution[] = [
  {
    id: 1,
    executionNo: 'TE-2026051801',
    suiteName: '用户管理模块',
    executedBy: '测试员A',
    executedAt: '2026-05-18 10:30',
    environment: '测试环境',
    duration: 45,
    totalCases: 156,
    passedCases: 134,
    failedCases: 15,
    blockedCases: 7,
    passRate: 85.9,
    status: '已完成'
  }
];

export const mockTestReport: TestReport = {
  id: 1,
  reportNo: 'TR-2026051801',
  title: '用户管理模块测试报告',
  projectName: 'TOPO系统',
  createdBy: '测试员A',
  createdAt: '2026-05-18 11:30',
  summary: {
    totalCases: 156,
    passedCases: 134,
    failedCases: 15,
    passRate: 85.9,
    startTime: '2026-05-18 10:30',
    endTime: '2026-05-18 11:15',
    duration: 45
  },
  results: []
};
