export interface TestDashboard {
  totalSuites: number;
  totalCases: number;
  passedCases: number;
  failedCases: number;
  blockedCases: number;
  untestedCases: number;
  passRate: number;
  recentExecutions: RecentExecution[];
  suiteSummary: SuiteSummary[];
  weeklyTrend: WeeklyTrend[];
}

export interface RecentExecution {
  id: number;
  suiteName: string;
  executedBy: string;
  executedAt: string;
  passRate: number;
  duration: number;
}

export interface SuiteSummary {
  suiteName: string;
  totalCases: number;
  passedCases: number;
  failedCases: number;
  passRate: number;
}

export interface WeeklyTrend {
  week: string;
  passed: number;
  failed: number;
  total: number;
}

export interface TestSuite {
  id: number;
  suiteName: string;
  projectName: string;
  module: string;
  caseCount: number;
  lastExecution?: string;
  passRate: number;
  status: '正常' | '异常';
  description?: string;
}

export interface TestCase {
  id: number;
  caseNo: string;
  caseName: string;
  priority: 'P0' | 'P1' | 'P2' | 'P3';
  type: '功能测试' | '接口测试' | '性能测试' | '安全测试';
  precondition?: string;
  testSteps: TestStep[];
  expectedResult?: string;
  status: '待测试' | '通过' | '失败' | '阻塞' | '未执行';
  lastExecutionResult?: string;
  lastExecutionTime?: string;
  executor?: string;
}

export interface TestStep {
  stepNo: number;
  description: string;
  testData?: string;
  expectedResult?: string;
}

export interface TestExecution {
  id: number;
  executionNo: string;
  suiteName: string;
  executedBy: string;
  executedAt: string;
  environment: string;
  duration: number;
  totalCases: number;
  passedCases: number;
  failedCases: number;
  blockedCases: number;
  passRate: number;
  status: '执行中' | '已完成' | '已中止';
}

export interface TestReport {
  id: number;
  reportNo: string;
  title: string;
  projectName: string;
  createdBy: string;
  createdAt: string;
  summary: ReportSummary;
  results: ReportResult[];
  attachments?: string[];
}

export interface ReportSummary {
  totalCases: number;
  passedCases: number;
  failedCases: number;
  passRate: number;
  startTime: string;
  endTime: string;
  duration: number;
}

export interface ReportResult {
  suiteName: string;
  caseName: string;
  result: '通过' | '失败' | '阻塞';
  executor: string;
  executionTime: string;
  remarks?: string;
}
