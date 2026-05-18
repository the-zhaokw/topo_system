export interface BugStatistics {
  total: number;
  open: number;
  inProgress: number;
  resolved: number;
  closed: number;
  criticalCount: number;
  highCount: number;
  mediumCount: number;
  lowCount: number;
  todayCreated: number;
  todayResolved: number;
  weeklyTrend: TrendData[];
  projectDistribution: ProjectDist[];
  statusDistribution: StatusDist[];
  priorityDistribution: PriorityDist[];
}

export interface TrendData {
  date: string;
  created: number;
  resolved: number;
}

export interface ProjectDist {
  projectName: string;
  count: number;
  percentage: number;
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
