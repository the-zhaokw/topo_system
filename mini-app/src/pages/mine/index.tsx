import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, Button } from '@tarojs/components';
import Taro from '@tarojs/taro';
import classnames from 'classnames';
import styles from './index.module.scss';
import { mockUser, mockProjects, mockTodos, mockWorkLogs, mockActivity } from '../../data/businessData';
import { mockBugList } from '../../data/bugData';

const MinePage: React.FC = () => {
  const [user] = useState(mockUser[1]);
  const [stats, setStats] = useState({
    myBugs: 0,
    handling: 0,
    resolved: 0,
    hours: 0,
    todos: 0,
    projects: 0
  });

  useEffect(() => {
    calculateStats();
  }, []);

  const calculateStats = () => {
    const myBugs = mockBugList.filter(b => b.reporter_name === user.realName).length;
    const handling = mockBugList.filter(b =>
      b.assignee_name === user.realName && b.status === 'in_progress'
    ).length;
    const resolved = mockBugList.filter(b =>
      b.assignee_name === user.realName &&
      (b.status === 'resolved' || b.status === 'closed')
    ).length;
    const hours = mockWorkLogs
      .filter(w => w.user_name === user.realName)
      .reduce((sum, w) => sum + w.work_hours, 0);
    const todos = mockTodos.filter(t => t.assignee_name === user.realName).length;
    const projects = mockProjects.filter(p => p.manager_name === user.realName).length;

    setStats({ myBugs, handling, resolved, hours, todos, projects });
  };

  const go = (url: string, isTab = false) => {
    if (isTab) {
      Taro.switchTab({ url });
    } else {
      Taro.navigateTo({ url, fail: () => Taro.showToast({ title: '页面暂未实现', icon: 'none' }) });
    }
  };

  const goProfile = () => go('/pages/user-profile/index');
  const goNotifications = () => go('/pages/notifications/index');
  const goMyTodos = () => go('/pages/my-todos/index', true);
  const goProjectList = () => go('/pages/project-list/index', true);
  const goBugList = () => go('/pages/bug-list/index', true);
  const goAttendance = () => go('/pages/attendance/index');
  const goMyDepartment = () => go('/pages/my-department/index');
  const goWorkStatistics = () => go('/pages/work-statistics/index');
  const goWorkLogs = () => go('/pages/work-logs/index');
  const goPersonalPlan = () => go('/pages/personal-plan/index');
  const goActivity = () => go('/pages/activity-list/index');
  const goContracts = () => go('/pages/contracts/index');
  const goMaterials = () => go('/pages/materials/index');
  const goKnowledge = () => go('/pages/knowledge/index');
  const goRisk = () => go('/pages/risk-list/index');
  const goSystemSettings = () => go('/pages/system-settings/index');
  const goMonitoring = () => go('/pages/monitoring-list/index');
  const goUserList = () => go('/pages/user-list/index');

  const handleLogout = () => {
    Taro.showModal({
      title: '退出登录',
      content: '确定要退出当前账号吗？',
      confirmColor: '#EF4444',
      success: (res) => {
        if (res.confirm) {
          Taro.removeStorageSync('token');
          Taro.removeStorageSync('userInfo');
          Taro.showToast({ title: '已退出登录', icon: 'success' });
          // 实际场景：Taro.reLaunch({ url: '/pages/login/index' })
          setTimeout(() => {
            Taro.reLaunch({ url: '/pages/home/index' });
          }, 800);
        }
      }
    });
  };

  const handleEditProfile = () => {
    Taro.showToast({ title: '编辑资料功能开发中', icon: 'none' });
  };

  return (
    <View className={styles.container}>
      <ScrollView scrollY className={styles.scroll} enableBackToTop>
        {/* 顶部用户卡片 */}
        <View className={styles.header}>
          <View className={styles.headerBg} />
          <View className={styles.profileRow} onClick={goProfile}>
            <View className={styles.avatar}>
              <Text>{user.realName.charAt(0)}</Text>
            </View>
            <View className={styles.profileInfo}>
              <View className={styles.nameLine}>
                <Text className={styles.name}>{user.realName}</Text>
                <View className={styles.roleTag}>
                  <Text>{user.position}</Text>
                </View>
              </View>
              <Text className={styles.dept}>{user.department} · @{user.username}</Text>
              <Text className={styles.email}>📧 {user.email}</Text>
            </View>
            <Text className={styles.profileArrow}>›</Text>
          </View>

          {/* 数据概览 4 卡 */}
          <View className={styles.statsGrid}>
            <View className={styles.statItem} onClick={() => go('/pages/bug-list/index?filter=mine', true)}>
              <Text className={styles.statValue}>{stats.myBugs}</Text>
              <Text className={styles.statLabel}>我的 Bug</Text>
            </View>
            <View className={styles.statItem} onClick={() => go('/pages/bug-list/index?filter=handling', true)}>
              <Text className={styles.statValue}>{stats.handling}</Text>
              <Text className={styles.statLabel}>处理中</Text>
            </View>
            <View className={styles.statItem} onClick={() => go('/pages/bug-list/index?filter=resolved', true)}>
              <Text className={styles.statValue}>{stats.resolved}</Text>
              <Text className={styles.statLabel}>已解决</Text>
            </View>
            <View className={styles.statItem} onClick={goWorkStatistics}>
              <Text className={styles.statValue}>{stats.hours}</Text>
              <Text className={styles.statLabel}>累计工时(h)</Text>
            </View>
          </View>
        </View>

        {/* 常用功能 */}
        <View className={styles.section}>
          <View className={styles.sectionHeader}>
            <Text className={styles.sectionTitle}>常用功能</Text>
          </View>
          <View className={styles.quickGrid}>
            <View className={styles.quickItem} onClick={goMyTodos}>
              <View className={classnames(styles.quickIcon, styles.iconTodo)}>
                <Text>✅</Text>
              </View>
              <Text className={styles.quickLabel}>我的待办</Text>
              {stats.todos > 0 && <View className={styles.quickBadge}><Text>{stats.todos}</Text></View>}
            </View>
            <View className={styles.quickItem} onClick={goProjectList}>
              <View className={classnames(styles.quickIcon, styles.iconProject)}>
                <Text>📁</Text>
              </View>
              <Text className={styles.quickLabel}>我的项目</Text>
              {stats.projects > 0 && <View className={styles.quickBadge}><Text>{stats.projects}</Text></View>}
            </View>
            <View className={styles.quickItem} onClick={goBugList}>
              <View className={classnames(styles.quickIcon, styles.iconBug)}>
                <Text>🐛</Text>
              </View>
              <Text className={styles.quickLabel}>我的 Bug</Text>
            </View>
            <View className={styles.quickItem} onClick={goAttendance}>
              <View className={classnames(styles.quickIcon, styles.iconAttendance)}>
                <Text>📅</Text>
              </View>
              <Text className={styles.quickLabel}>考勤打卡</Text>
            </View>
            <View className={styles.quickItem} onClick={goWorkStatistics}>
              <View className={classnames(styles.quickIcon, styles.iconStats)}>
                <Text>📊</Text>
              </View>
              <Text className={styles.quickLabel}>工作统计</Text>
            </View>
            <View className={styles.quickItem} onClick={goWorkLogs}>
              <View className={classnames(styles.quickIcon, styles.iconLog)}>
                <Text>📝</Text>
              </View>
              <Text className={styles.quickLabel}>工作日志</Text>
            </View>
            <View className={styles.quickItem} onClick={goPersonalPlan}>
              <View className={classnames(styles.quickIcon, styles.iconPlan)}>
                <Text>📆</Text>
              </View>
              <Text className={styles.quickLabel}>个人计划</Text>
            </View>
            <View className={styles.quickItem} onClick={goActivity}>
              <View className={classnames(styles.quickIcon, styles.iconActivity)}>
                <Text>📋</Text>
              </View>
              <Text className={styles.quickLabel}>活动记录</Text>
            </View>
          </View>
        </View>

        {/* 业务管理 */}
        <View className={styles.section}>
          <View className={styles.sectionHeader}>
            <Text className={styles.sectionTitle}>业务管理</Text>
          </View>
          <View className={styles.menuList}>
            <View className={styles.menuItem} onClick={goContracts}>
              <View className={classnames(styles.menuIcon, styles.iconContract)}>
                <Text>📄</Text>
              </View>
              <View className={styles.menuInfo}>
                <Text className={styles.menuTitle}>合同管理</Text>
                <Text className={styles.menuDesc}>查看与管理所有合同</Text>
              </View>
              <Text className={styles.menuArrow}>›</Text>
            </View>
            <View className={styles.menuItem} onClick={goMaterials}>
              <View className={classnames(styles.menuIcon, styles.iconMaterial)}>
                <Text>📦</Text>
              </View>
              <View className={styles.menuInfo}>
                <Text className={styles.menuTitle}>物料管理</Text>
                <Text className={styles.menuDesc}>物料、仓库、库存</Text>
              </View>
              <Text className={styles.menuArrow}>›</Text>
            </View>
            <View className={styles.menuItem} onClick={goKnowledge}>
              <View className={classnames(styles.menuIcon, styles.iconKnowledge)}>
                <Text>📚</Text>
              </View>
              <View className={styles.menuInfo}>
                <Text className={styles.menuTitle}>知识库</Text>
                <Text className={styles.menuDesc}>团队知识沉淀与分享</Text>
              </View>
              <Text className={styles.menuArrow}>›</Text>
            </View>
            <View className={styles.menuItem} onClick={goRisk}>
              <View className={classnames(styles.menuIcon, styles.iconRisk)}>
                <Text>⚠️</Text>
              </View>
              <View className={styles.menuInfo}>
                <Text className={styles.menuTitle}>风险问题</Text>
                <Text className={styles.menuDesc}>项目风险登记与跟踪</Text>
              </View>
              <Text className={styles.menuArrow}>›</Text>
            </View>
            <View className={styles.menuItem} onClick={goMyDepartment}>
              <View className={classnames(styles.menuIcon, styles.iconDept)}>
                <Text>🏢</Text>
              </View>
              <View className={styles.menuInfo}>
                <Text className={styles.menuTitle}>我的部门</Text>
                <Text className={styles.menuDesc}>查看部门成员信息</Text>
              </View>
              <Text className={styles.menuArrow}>›</Text>
            </View>
          </View>
        </View>

        {/* 系统与设置 */}
        <View className={styles.section}>
          <View className={styles.sectionHeader}>
            <Text className={styles.sectionTitle}>系统与设置</Text>
          </View>
          <View className={styles.menuList}>
            <View className={styles.menuItem} onClick={goProfile}>
              <View className={classnames(styles.menuIcon, styles.iconProfile)}>
                <Text>👤</Text>
              </View>
              <View className={styles.menuInfo}>
                <Text className={styles.menuTitle}>个人资料</Text>
                <Text className={styles.menuDesc}>查看和编辑个人信息</Text>
              </View>
              <Text className={styles.menuArrow}>›</Text>
            </View>
            <View className={styles.menuItem} onClick={goNotifications}>
              <View className={classnames(styles.menuIcon, styles.iconNotif)}>
                <Text>🔔</Text>
              </View>
              <View className={styles.menuInfo}>
                <Text className={styles.menuTitle}>通知中心</Text>
                <Text className={styles.menuDesc}>查看系统通知和消息</Text>
              </View>
              <Text className={styles.menuArrow}>›</Text>
            </View>
            <View className={styles.menuItem} onClick={goUserList}>
              <View className={classnames(styles.menuIcon, styles.iconUser)}>
                <Text>👥</Text>
              </View>
              <View className={styles.menuInfo}>
                <Text className={styles.menuTitle}>用户列表</Text>
                <Text className={styles.menuDesc}>查看团队成员</Text>
              </View>
              <Text className={styles.menuArrow}>›</Text>
            </View>
            <View className={styles.menuItem} onClick={goMonitoring}>
              <View className={classnames(styles.menuIcon, styles.iconMonitor)}>
                <Text>📡</Text>
              </View>
              <View className={styles.menuInfo}>
                <Text className={styles.menuTitle}>系统监控</Text>
                <Text className={styles.menuDesc}>查看系统运行状态</Text>
              </View>
              <Text className={styles.menuArrow}>›</Text>
            </View>
            <View className={styles.menuItem} onClick={goSystemSettings}>
              <View className={classnames(styles.menuIcon, styles.iconSettings)}>
                <Text>⚙️</Text>
              </View>
              <View className={styles.menuInfo}>
                <Text className={styles.menuTitle}>系统设置</Text>
                <Text className={styles.menuDesc}>应用设置和偏好</Text>
              </View>
              <Text className={styles.menuArrow}>›</Text>
            </View>
          </View>
        </View>

        {/* 关于与退出 */}
        <View className={styles.section}>
          <View className={styles.menuList}>
            <View className={styles.menuItem} onClick={handleEditProfile}>
              <View className={classnames(styles.menuIcon, styles.iconEdit)}>
                <Text>✏️</Text>
              </View>
              <View className={styles.menuInfo}>
                <Text className={styles.menuTitle}>编辑资料</Text>
                <Text className={styles.menuDesc}>修改头像/姓名/手机号</Text>
              </View>
              <Text className={styles.menuArrow}>›</Text>
            </View>
            <View className={styles.menuItem} onClick={() => Taro.showModal({
              title: '关于 TOPO',
              content: 'TOPO 系统 v1.0.0\n企业级项目管理与工作协同平台',
              showCancel: false
            })}>
              <View className={classnames(styles.menuIcon, styles.iconAbout)}>
                <Text>ℹ️</Text>
              </View>
              <View className={styles.menuInfo}>
                <Text className={styles.menuTitle}>关于</Text>
                <Text className={styles.menuDesc}>应用版本和相关信息</Text>
              </View>
              <Text className={styles.menuArrow}>›</Text>
            </View>
            <View className={classnames(styles.menuItem, styles.logoutItem)} onClick={handleLogout}>
              <View className={classnames(styles.menuIcon, styles.iconLogout)}>
                <Text>🚪</Text>
              </View>
              <View className={styles.menuInfo}>
                <Text className={classnames(styles.menuTitle, styles.logoutText)}>退出登录</Text>
                <Text className={styles.menuDesc}>退出当前账号</Text>
              </View>
              <Text className={styles.menuArrow}>›</Text>
            </View>
          </View>
        </View>

        <View className={styles.footer}>
          <Text>TOPO 系统 v1.0.0</Text>
          <Text>企业级项目管理与工作协同平台</Text>
        </View>
      </ScrollView>
    </View>
  );
};

export default MinePage;
