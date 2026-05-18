export interface Bug {
  id: number;
  title: string;
  project_name: string;
  status: BugStatus;
  severity: BugSeverity;
  priority: BugPriority;
  reporter_name: string;
  assignee_name?: string;
  created_at: string;
  updated_at?: string;
  description?: string;
}

export type BugStatus = 'new' | 'in_progress' | 'resolved' | 'closed' | 'rejected' | 'reopened';
export type BugSeverity = 'critical' | 'high' | 'medium' | 'low' | 'suggestion';
export type BugPriority = 'urgent' | 'high' | 'medium' | 'low';

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

export interface FilterOptions {
  projects: Array<{ id: number; name: string }>;
  bugTypes: string[];
  severities: BugSeverity[];
  priorities: BugPriority[];
  statuses: BugStatus[];
  users: Array<{ id: number; name: string }>;
}

export interface BugFilters {
  timeRange: 'today' | 'week' | 'month' | 'quarter' | 'custom';
  projectIds: number[];
  bugTypes: string[];
  severities: BugSeverity[];
  statuses: BugStatus[];
  priorities: BugPriority[];
  reportedBy: number[];
  customDateRange?: [string, string];
}

export interface User {
  id: number;
  name: string;
  avatar?: string;
  email?: string;
  role?: string;
}
