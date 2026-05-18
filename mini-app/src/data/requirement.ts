import { RequirementDashboard, RequirementDocument, Requirement } from '../types/requirement';

export const mockRequirementDashboard: RequirementDashboard = {
  totalRequirements: 456,
  draftedRequirements: 45,
  reviewingRequirements: 78,
  approvedRequirements: 123,
  implementedRequirements: 145,
  verifiedRequirements: 32,
  releasedRequirements: 23,
  rejectedRequirements: 10,
  recentUpdates: [
    {
      id: 1,
      requirementNo: 'REQ-2026-001',
      requirementName: '支持多语言切换',
      projectName: 'TOPO系统',
      updatedField: '状态',
      updatedBy: '需求分析师A',
      updatedAt: '2026-05-18 10:30'
    },
    {
      id: 2,
      requirementNo: 'REQ-2026-002',
      requirementName: '优化数据导入性能',
      projectName: 'TOPO系统',
      updatedField: '优先级',
      updatedBy: '项目经理B',
      updatedAt: '2026-05-18 09:15'
    }
  ],
  statusDistribution: [
    { status: '草稿', count: 45, percentage: 9.9 },
    { status: '审核中', count: 78, percentage: 17.1 },
    { status: '已批准', count: 123, percentage: 27.0 },
    { status: '已实现', count: 145, percentage: 31.8 },
    { status: '已验证', count: 32, percentage: 7.0 },
    { status: '已发布', count: 23, percentage: 5.0 },
    { status: '已拒绝', count: 10, percentage: 2.2 }
  ],
  priorityDistribution: [
    { priority: '高', count: 156, percentage: 34.2 },
    { priority: '中', count: 234, percentage: 51.3 },
    { priority: '低', count: 66, percentage: 14.5 }
  ]
};

export const mockRequirementDocument: RequirementDocument[] = [
  {
    id: 1,
    documentNo: 'RD-2026-001',
    documentName: 'TOPO系统需求规格说明书',
    version: 'V2.1',
    projectName: 'TOPO系统',
    module: '整体架构',
    status: '已发布',
    author: '需求分析师A',
    createTime: '2026-01-15',
    updateTime: '2026-05-10',
    requirementCount: 156,
    description: 'TOPO系统整体需求规格说明'
  },
  {
    id: 2,
    documentNo: 'RD-2026-002',
    documentName: '合同管理模块需求文档',
    version: 'V1.3',
    projectName: '合同管理系统',
    module: '合同管理',
    status: '审核中',
    author: '需求分析师B',
    createTime: '2026-03-20',
    updateTime: '2026-05-15',
    requirementCount: 89,
    description: '合同管理模块详细需求'
  }
];

export const mockRequirement: Requirement[] = [
  {
    id: 1,
    requirementNo: 'REQ-2026-001',
    requirementName: '支持多语言切换',
    documentId: 1,
    documentName: 'TOPO系统需求规格说明书',
    module: '系统设置',
    priority: '高',
    status: '已实现',
    type: '功能需求',
    description: '系统应支持中英文语言切换,用户可在个人设置中选择界面语言',
    acceptanceCriteria: '1. 用户可在设置中选择语言\n2. 界面立即更新为所选语言\n3. 语言选择会被保存',
    creator: '需求分析师A',
    assignee: '开发人员C',
    createTime: '2026-01-20',
    updateTime: '2026-05-10',
    linkedBugs: [12, 15],
    linkedTestCases: [34, 35, 36]
  }
];
