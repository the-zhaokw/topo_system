export default defineAppConfig({
  pages: [
    // Tab 页面
    'pages/home/index',
    'pages/bug-list/index',
    'pages/my-todos/index',
    'pages/mine/index',
    // 其他业务页面（通过 navigateTo 进入）
    'pages/bug-detail/index',
    'pages/bug-form/index',
    'pages/bug-statistics/index',
    'pages/project-list/index',
    'pages/project-detail/index',
    'pages/project-form/index',
    'pages/project-log-list/index',
    'pages/project-statistics/index',
    'pages/attendance/index',
    'pages/attendance-detail/index',
    'pages/attendance-list/index',
    'pages/attendance-report/index',
    'pages/leave-application/index',
    'pages/leave-approval/index',
    'pages/overtime-application/index',
    'pages/overtime-approval/index',
    'pages/shift-management/index',
    'pages/contracts/index',
    'pages/contract-list/index',
    'pages/contract-detail/index',
    'pages/contract-statistics/index',
    'pages/materials/index',
    'pages/material-list/index',
    'pages/material-category/index',
    'pages/material-report/index',
    'pages/material-relationship/index',
    'pages/warehouse/index',
    'pages/inventory/index',
    'pages/serial-number/index',
    'pages/location/index',
    'pages/knowledge/index',
    'pages/knowledge-article/index',
    'pages/knowledge-enhanced/index',
    'pages/knowledge-share/index',
    'pages/notifications/index',
    'pages/personal-plan/index',
    'pages/personal-plan-dashboard/index',
    'pages/personal-plan-plans/index',
    'pages/personal-plan-inbox/index',
    'pages/personal-plan-quadrant/index',
    'pages/personal-plan-gantt/index',
    'pages/personal-plan-calendar/index',
    'pages/personal-plan-focus/index',
    'pages/personal-plan-habits/index',
    'pages/personal-plan-review/index',
    'pages/personal-plan-stats/index',
    'pages/work-logs/index',
    'pages/work-log-list/index',
    'pages/work-statistics/index',
    'pages/work-statistics-detail/index',
    'pages/activity-list/index',
    'pages/my-department/index',
    'pages/user-profile/index',
    'pages/user-detail/index',
    'pages/user-list/index',
    'pages/risk-list/index',
    'pages/custom-report/index',
    'pages/system-settings/index',
    'pages/monitoring-list/index',
    'pages/dashboard/index'
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#4F46E5',
    navigationBarTitleText: 'TOPO系统',
    navigationBarTextStyle: 'white',
    backgroundColor: '#F8FAFC',
    enablePullDownRefresh: false
  },
  tabBar: {
    color: '#64748B',
    selectedColor: '#4F46E5',
    backgroundColor: '#FFFFFF',
    borderStyle: 'black',
    list: [
      {
        pagePath: 'pages/home/index',
        text: '首页'
      },
      {
        pagePath: 'pages/bug-list/index',
        text: 'Bug'
      },
      {
        pagePath: 'pages/my-todos/index',
        text: '待办'
      },
      {
        pagePath: 'pages/mine/index',
        text: '我的'
      }
    ]
  }
})
