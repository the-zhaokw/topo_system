export default defineAppConfig({
  pages: [
    'pages/home/index',
    'pages/bug-list/index',
    'pages/bug-detail/index',
    'pages/project-list/index',
    'pages/project-detail/index',
    'pages/my-todos/index',
    'pages/attendance/index',
    'pages/contracts/index',
    'pages/materials/index',
    'pages/knowledge/index',
    'pages/notifications/index',
    'pages/personal-plan/index',
    'pages/mine/index'
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#4F46E5',
    navigationBarTitleText: 'TOPO系统',
    navigationBarTextStyle: 'white',
    backgroundColor: '#F8FAFC'
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
        text: 'Bug列表'
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
