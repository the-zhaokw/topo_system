// Bug统计相关类型定义
export interface Bug {
  id: number;
  title: string;
  project_name: string;
  status: BugStatus;
  severity: BugSeverity;
  priority: BugPriority;
  reporter_name: string;
  created_at: string;
}

export type BugStatus = 'new' | 'assigned' | 'in_progress' | 'resolved' | 'verified' | 'closed' | 'rejected' | 'reopened';

export type BugSeverity = 'critical' | 'high' | 'medium' | 'low' | 'suggestion';

export type BugPriority = 'urgent' | 'high' | 'medium' | 'low';

export type TimeRange = 'today' | 'week' | 'month' | 'quarter' | 'custom';

export interface KpiData {
  total_bugs: number;
  total_change: number;
  new_bugs: number;
  resolved_bugs: number;
  unresolved_bugs: number;
  resolution_rate: number;
  avg_fix_time: number;
}

export interface TrendData {
  date: string;
  new_bugs: number;
  resolved_bugs: number;
  cumulative_unresolved: number;
}

export interface DistributionData {
  [key: string]: {
    total: number;
    new: number;
    resolved: number;
    closed: number;
  } | number;
}

export interface TypeDistribution {
  name: string;
  value: number;
}

export interface WorkloadData {
  name: string;
  assigned: number;
  in_progress: number;
  resolved: number;
  closed: number;
}

export interface FilterParams {
  start_date: string;
  end_date: string;
  project_ids?: string;
  bug_types?: string;
  severities?: string;
  statuses?: string;
  priorities?: string;
  reported_by?: string;
  page?: number;
  per_page?: number;
}

export interface BugListResponse {
  bugs: Bug[];
  total: number;
}

export interface FilterOptions {
  projects: Array<{ id: string; name: string }>;
  bugTypes: string[];
  severities: string[];
  priorities: string[];
  statuses: string[];
  users: Array<{ id: string; name: string }>;
}
