import { Project, Todo, Attendance, Contract, Material, KnowledgeArticle, Notification, WorkLog, PersonalPlan } from '../types/business';

export const mockProjects: Project[] = [
  {
    id: 1,
    name: 'TOPO系统前端重构',
    description: '对TOPO系统前端进行架构重构，提升用户体验和性能',
    status: 'active',
    start_date: '2026-03-01',
    end_date: '2026-06-30',
    manager_name: '张三',
    member_count: 8,
    bug_count: 45,
    completion_rate: 65
  },
  {
    id: 2,
    name: '移动端APP开发',
    description: '开发TOPO系统微信小程序和APP端',
    status: 'active',
    start_date: '2026-04-01',
    manager_name: '李四',
    member_count: 5,
    bug_count: 23,
    completion_rate: 40
  },
  {
    id: 3,
    name: '数据库优化项目',
    description: '优化数据库性能，提升查询效率',
    status: 'completed',
    start_date: '2026-01-01',
    end_date: '2026-03-31',
    manager_name: '王五',
    member_count: 3,
    bug_count: 12,
    completion_rate: 100
  },
  {
    id: 4,
    name: '智能报表系统',
    description: '开发新一代智能报表生成系统',
    status: 'planning',
    start_date: '2026-06-01',
    manager_name: '赵六',
    member_count: 6,
    bug_count: 0,
    completion_rate: 0
  }
];

export const mockTodos: Todo[] = [
  {
    id: 1,
    title: '完成Bug统计页面开发',
    description: '实现Bug统计看板的所有图表和统计功能',
    priority: 'high',
    status: 'in_progress',
    due_date: '2026-05-20',
    created_at: '2026-05-15 10:00:00',
    assignee_name: '张三',
    project_name: 'TOPO系统前端重构'
  },
  {
    id: 2,
    title: '修复登录页面兼容性问题',
    description: '解决部分浏览器无法登录的问题',
    priority: 'urgent',
    status: 'pending',
    due_date: '2026-05-19',
    created_at: '2026-05-18 09:00:00',
    assignee_name: '张三'
  },
  {
    id: 3,
    title: '优化数据库查询性能',
    description: '优化复杂查询语句，提升响应速度',
    priority: 'medium',
    status: 'pending',
    due_date: '2026-05-25',
    created_at: '2026-05-10 14:30:00',
    assignee_name: '李四',
    project_name: '数据库优化项目'
  },
  {
    id: 4,
    title: '编写技术文档',
    description: '整理并编写项目技术文档',
    priority: 'low',
    status: 'completed',
    created_at: '2026-05-01 11:00:00',
    assignee_name: '王五'
  },
  {
    id: 5,
    title: '代码审查',
    description: '对新提交的代码进行审查',
    priority: 'high',
    status: 'in_progress',
    due_date: '2026-05-21',
    created_at: '2026-05-17 16:00:00',
    assignee_name: '赵六'
  }
];

export const mockAttendance: Attendance[] = [
  {
    id: 1,
    user_name: '张三',
    date: '2026-05-18',
    check_in_time: '09:00:00',
    check_out_time: '18:00:00',
    status: 'normal',
    work_hours: 9
  },
  {
    id: 2,
    user_name: '张三',
    date: '2026-05-17',
    check_in_time: '08:55:00',
    check_out_time: '18:05:00',
    status: 'normal',
    work_hours: 9.17
  },
  {
    id: 3,
    user_name: '张三',
    date: '2026-05-16',
    check_in_time: '09:30:00',
    check_out_time: '18:00:00',
    status: 'late',
    work_hours: 8.5
  },
  {
    id: 4,
    user_name: '张三',
    date: '2026-05-15',
    status: 'leave',
    work_hours: 0
  },
  {
    id: 5,
    user_name: '张三',
    date: '2026-05-14',
    check_in_time: '08:50:00',
    check_out_time: '17:50:00',
    status: 'normal',
    work_hours: 9
  }
];

export const mockContracts: Contract[] = [
  {
    id: 1,
    contract_no: 'CT-2026-001',
    name: 'TOPO系统定制开发合同',
    customer_name: '某某科技有限公司',
    amount: 500000,
    sign_date: '2026-01-15',
    status: 'signed',
    project_name: 'TOPO系统前端重构'
  },
  {
    id: 2,
    contract_no: 'CT-2026-002',
    name: '移动端APP开发合同',
    customer_name: '某某集团',
    amount: 300000,
    sign_date: '2026-03-20',
    status: 'pending',
    project_name: '移动端APP开发'
  },
  {
    id: 3,
    contract_no: 'CT-2025-015',
    name: '系统维护服务合同',
    customer_name: '某某企业',
    amount: 120000,
    sign_date: '2025-12-01',
    status: 'completed'
  }
];

export const mockMaterials: Material[] = [
  {
    id: 1,
    name: '服务器主机',
    code: 'SRV-001',
    category: '硬件设备',
    unit: '台',
    stock: 10,
    price: 15000,
    warehouse: 'A仓库',
    location: 'A-01-01'
  },
  {
    id: 2,
    name: '显示器',
    code: 'MON-001',
    category: '硬件设备',
    unit: '台',
    stock: 25,
    price: 2000,
    warehouse: 'A仓库',
    location: 'A-02-01'
  },
  {
    id: 3,
    name: '机械键盘',
    code: 'KBD-001',
    category: '办公用品',
    unit: '个',
    stock: 50,
    price: 300,
    warehouse: 'B仓库',
    location: 'B-01-05'
  },
  {
    id: 4,
    name: '无线鼠标',
    code: 'MSE-001',
    category: '办公用品',
    unit: '个',
    stock: 80,
    price: 150,
    warehouse: 'B仓库',
    location: 'B-01-06'
  },
  {
    id: 5,
    name: '笔记本电脑',
    code: 'LAP-001',
    category: '硬件设备',
    unit: '台',
    stock: 15,
    price: 8000,
    warehouse: 'A仓库',
    location: 'A-03-01'
  }
];

export const mockKnowledgeArticles: KnowledgeArticle[] = [
  {
    id: 1,
    title: 'Vue3 组合式API最佳实践',
    category: '前端开发',
    author: '张三',
    created_at: '2026-05-15 10:00:00',
    view_count: 1256,
    summary: '深入讲解Vue3组合式API的使用技巧和最佳实践'
  },
  {
    id: 2,
    title: 'Taro多端开发指南',
    category: '移动开发',
    author: '李四',
    created_at: '2026-05-12 14:30:00',
    view_count: 890,
    summary: '使用Taro框架开发微信小程序的完整指南'
  },
  {
    id: 3,
    title: '数据库性能优化实战',
    category: '后端开发',
    author: '王五',
    created_at: '2026-05-10 09:15:00',
    view_count: 2103,
    summary: 'SQL查询优化和数据库设计的实战经验总结'
  },
  {
    id: 4,
    title: 'Git协作开发规范',
    category: '工具使用',
    author: '赵六',
    created_at: '2026-05-08 16:45:00',
    view_count: 567,
    summary: '团队协作中的Git使用规范和工作流程'
  },
  {
    id: 5,
    title: 'TypeScript入门教程',
    category: '前端开发',
    author: '孙七',
    created_at: '2026-05-05 11:20:00',
    view_count: 3421,
    summary: 'TypeScript基础语法和类型系统详解'
  }
];

export const mockNotifications: Notification[] = [
  {
    id: 1,
    title: '新Bug指派通知',
    content: '您有一个新的Bug被指派给您，请及时处理',
    type: 'warning',
    is_read: false,
    created_at: '2026-05-18 10:30:00'
  },
  {
    id: 2,
    title: '项目进度更新',
    content: 'TOPO系统前端重构项目已完成65%，请关注',
    type: 'info',
    is_read: true,
    created_at: '2026-05-17 15:00:00'
  },
  {
    id: 3,
    title: '会议提醒',
    content: '明天下午2点有项目评审会议，请准时参加',
    type: 'warning',
    is_read: false,
    created_at: '2026-05-18 08:00:00'
  },
  {
    id: 4,
    title: '代码审查通过',
    content: '您的代码已通过审查，可以合并到主分支',
    type: 'success',
    is_read: true,
    created_at: '2026-05-16 14:20:00'
  },
  {
    id: 5,
    title: '系统公告',
    content: '系统将于本周六进行例行维护，请提前做好准备',
    type: 'info',
    is_read: false,
    created_at: '2026-05-18 09:00:00'
  }
];

export const mockWorkLogs: WorkLog[] = [
  {
    id: 1,
    user_name: '张三',
    work_date: '2026-05-18',
    work_content: '完成Bug统计页面的图表开发',
    work_hours: 6,
    project_name: 'TOPO系统前端重构'
  },
  {
    id: 2,
    user_name: '张三',
    work_date: '2026-05-17',
    work_content: '修复登录页面兼容性问题',
    work_hours: 4,
    project_name: 'TOPO系统前端重构'
  },
  {
    id: 3,
    user_name: '张三',
    work_date: '2026-05-17',
    work_content: '参与项目评审会议',
    work_hours: 2
  },
  {
    id: 4,
    user_name: '张三',
    work_date: '2026-05-16',
    work_content: '代码审查和优化',
    work_hours: 5,
    project_name: '数据库优化项目'
  },
  {
    id: 5,
    user_name: '张三',
    work_date: '2026-05-15',
    work_content: '编写技术文档',
    work_hours: 3
  }
];

export const mockPersonalPlans: PersonalPlan[] = [
  {
    id: 1,
    title: '本周工作计划',
    plan_type: 'weekly',
    start_time: '2026-05-13 00:00:00',
    end_time: '2026-05-19 23:59:59',
    status: 'in_progress',
    progress: 65
  },
  {
    id: 2,
    title: '月度学习计划',
    plan_type: 'monthly',
    start_time: '2026-05-01 00:00:00',
    end_time: '2026-05-31 23:59:59',
    status: 'in_progress',
    progress: 40
  },
  {
    id: 3,
    title: '每日早起计划',
    plan_type: 'daily',
    start_time: '2026-05-01 00:00:00',
    end_time: '2026-05-31 23:59:59',
    status: 'in_progress',
    progress: 80
  }
];
