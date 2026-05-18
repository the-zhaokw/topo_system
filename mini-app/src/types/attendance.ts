export interface AttendanceDetail {
  id: number;
  userId: number;
  userName: string;
  date: string;
  checkInTime: string;
  checkOutTime: string;
  workHours: number;
  status: '正常' | '迟到' | '早退' | '缺勤' | '请假';
  location: string;
  remarks?: string;
}

export interface AttendanceReport {
  month: string;
  totalDays: number;
  workDays: number;
  actualDays: number;
  normalDays: number;
  lateDays: number;
  earlyDays: number;
  absentDays: number;
  leaveDays: number;
  overtimeHours: number;
  averageWorkHours: number;
  details: AttendanceDetail[];
}

export interface ShiftInfo {
  id: number;
  shiftName: string;
  startTime: string;
  endTime: string;
  breakStart: string;
  breakEnd: string;
  workHours: number;
}

export interface LeaveApplication {
  id: number;
  applicantName: string;
  leaveType: '年假' | '病假' | '事假' | '婚假' | '产假' | '陪产假' | '其他';
  startDate: string;
  endDate: string;
  totalDays: number;
  reason: string;
  status: '待审批' | '已通过' | '已拒绝';
  approver?: string;
  applyTime: string;
}

export interface OvertimeApplication {
  id: number;
  applicantName: string;
  overtimeDate: string;
  startTime: string;
  endTime: string;
  totalHours: number;
  reason: string;
  status: '待审批' | '已通过' | '已拒绝';
  approver?: string;
  applyTime: string;
}
