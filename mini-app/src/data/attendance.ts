import { AttendanceReport, ShiftInfo, LeaveApplication, OvertimeApplication } from '../types/attendance';

export const mockAttendanceReport: AttendanceReport = {
  month: '2026年5月',
  totalDays: 31,
  workDays: 22,
  actualDays: 21,
  normalDays: 18,
  lateDays: 2,
  earlyDays: 1,
  absentDays: 0,
  leaveDays: 1,
  overtimeHours: 12,
  averageWorkHours: 8.5,
  details: []
};

export const mockShiftInfo: ShiftInfo[] = [
  {
    id: 1,
    shiftName: '早班',
    startTime: '08:30',
    endTime: '17:30',
    breakStart: '12:00',
    breakEnd: '13:00',
    workHours: 8
  },
  {
    id: 2,
    shiftName: '中班',
    startTime: '14:00',
    endTime: '22:00',
    breakStart: '18:00',
    breakEnd: '19:00',
    workHours: 8
  }
];

export const mockLeaveApplication: LeaveApplication[] = [
  {
    id: 1,
    applicantName: '张三',
    leaveType: '年假',
    startDate: '2026-05-20',
    endDate: '2026-05-22',
    totalDays: 3,
    reason: '家庭旅行',
    status: '待审批',
    applyTime: '2026-05-15 09:30'
  },
  {
    id: 2,
    applicantName: '李四',
    leaveType: '病假',
    startDate: '2026-05-18',
    endDate: '2026-05-18',
    totalDays: 1,
    reason: '身体不适',
    status: '已通过',
    approver: '王经理',
    applyTime: '2026-05-18 07:45'
  }
];

export const mockOvertimeApplication: OvertimeApplication[] = [
  {
    id: 1,
    applicantName: '张三',
    overtimeDate: '2026-05-17',
    startTime: '18:00',
    endTime: '21:00',
    totalHours: 3,
    reason: '项目紧急上线',
    status: '待审批',
    applyTime: '2026-05-17 17:30'
  }
];
