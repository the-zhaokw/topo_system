export interface RequirementDashboard {
  totalRequirements: number;
  draftedRequirements: number;
  reviewingRequirements: number;
  approvedRequirements: number;
  implementedRequirements: number;
  verifiedRequirements: number;
  releasedRequirements: number;
  rejectedRequirements: number;
  recentUpdates: RequirementUpdate[];
  statusDistribution: StatusDist[];
  priorityDistribution: PriorityDist[];
}

export interface RequirementUpdate {
  id: number;
  requirementNo: string;
  requirementName: string;
  projectName: string;
  updatedField: string;
  updatedBy: string;
  updatedAt: string;
}

export interface StatusDist {
  status: string;
  count: number;
  percentage: number;
}

export interface PriorityDist {
  priority: string;
  count: number;
  percentage: number;
}

export interface RequirementDocument {
  id: number;
  documentNo: string;
  documentName: string;
  version: string;
  projectName: string;
  module: string;
  status: '草稿' | '审核中' | '已发布' | '已归档';
  author: string;
  createTime: string;
  updateTime: string;
  requirementCount: number;
  description?: string;
}

export interface Requirement {
  id: number;
  requirementNo: string;
  requirementName: string;
  documentId: number;
  documentName: string;
  module: string;
  priority: '高' | '中' | '低';
  status: '草稿' | '待评审' | '已评审' | '已分配' | '开发中' | '已完成' | '已验证' | '已关闭';
  type: '功能需求' | '性能需求' | '安全需求' | '接口需求' | '其他';
  description: string;
  acceptanceCriteria?: string;
  creator: string;
  assignee?: string;
  createTime: string;
  updateTime: string;
  linkedBugs?: number[];
  linkedTestCases?: number[];
}

export interface RequirementTraceMatrix {
  requirementNo: string;
  requirementName: string;
  priority: string;
  status: string;
  testCases: TraceTestCase[];
  bugs: TraceBug[];
  completionRate: number;
}

export interface TraceTestCase {
  caseNo: string;
  caseName: string;
  result?: '通过' | '失败' | '阻塞' | '未执行';
}

export interface TraceBug {
  bugNo: string;
  bugName: string;
  severity: string;
  status: string;
}
