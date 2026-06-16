import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, Button } from '@tarojs/components';
import Taro from '@tarojs/taro';
import classnames from 'classnames';
import styles from './index.module.scss';
import { mockKpiData, mockTrendData, mockBugList } from '../../data/bugData';
import {
  mockProjects,
  mockTodos,
  mockNotifications,
  mockActivity,
  mockUser,
} from '../../data/businessData';
import { mockWorkStatistics } from '../../data/business';
import { Bug } from '../../types/bug';
import { Project, Notification, Activity } from '../../types/business';

const HomePage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [kpiData] = useState(mockKpiData);
  const [trendData] = useState(mockTrendData);
  const [granularity, setGranularity] = useState<'day' | 'week' | 'month'>('day');
  const [currentUser] = useState(mockUser[1]); // 当前登录用户：张三
  const [recentProjects, setRecentProjects] = useState<Project[]>([]);
  const [recentBugs, setRecentBugs] = useState<Bug[]>([]);
  const [todoSummary, setTodoSummary] = useState({
    total: 0,
    pending: 0,
    inProgress: 0
  });
  const [workStats] = useState(mockWorkStatistics);
  const [recentActivities, setRecentActivities] = useState<Activity[]>([]);
  const [recentNotifications, setRecentNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 300));

      // 1. 我参与的项目：筛选当前用户作为经理的项目
      const myProjects = mockProjects.filter(p => p.manager_name === currentUser.realName);
      setRecentProjects(myProjects.length > 0 ? myProjects : mockProjects.slice(0, 3));

      // 2. 待办汇总
      const myTodos = mockTodos.filter(t => t.assignee_name === currentUser.realName);
      setTodoSummary({
        total: myTodos.length,
        pending: myTodos.filter(t => t.status === 'pending').length,
        inProgress: myTodos.filter(t => t.status === 'in_progress').length
      });

      // 3. 最近 Bug（按创建时间倒序）
      setRecentBugs(mockBugList.slice(0, 5));

      // 4. 活动记录 / 通知
      setRecentActivities(mockActivity.slice(0, 4));
      setRecentNotifications(mockNotifications.slice(0, 3));

      console.log('[Home] Dashboard data loaded');
    } catch (error) {
      console.error('[Home] Error loading data:', error);
      Taro.showToast({ title: '数据加载失败', icon: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const onPullDownRefresh = () => {
    loadData().then(() => {
      Taro.stopPullDownRefresh();
      Taro.showToast({ title: '刷新成功', icon: 'success' });
    });
  };

  const navigateTo = (url: string, isTab = false) => {
    if (isTab) {
      Taro.switchTab({ url });
    } else {
      Taro.navigateTo({ url });
    }
  };

  const goToBugList = (filter?: string) => {
    const url = filter
      ? `/pages/bug-list/index?filter=${filter}`
      : '/pages/bug-list/index';
    navigateTo(url, !filter);
  };

  const goToProjectList = () => navigateTo('/pages/project-list/index', true);
  const goToMyTodos = () => navigateTo('/pages/my-todos/index', true);
  const goToAttendance = () => navigateTo('/pages/attendance/index');
  const goToContracts = () => navigateTo('/pages/contracts/index');
  const goToKnowledge = () => navigateTo('/pages/knowledge/index');
  const goToNotifications = () => navigateTo('/pages/notifications/index');
  const goToPersonalPlan = () => navigateTo('/pages/personal-plan/index');
  const goToWorkStatistics = () => navigateTo('/pages/work-statistics/index');
  const goToProjectDetail = (id: number) => navigateTo(`/pages/project-detail/index?id=${id}`);
  const goToBugDetail = (id: number) => navigateTo(`/pages/bug-detail/index?id=${id}`);
  const goToActivity = () => navigateTo('/pages/activity-list/index');
  const goToMaterials = () => navigateTo('/pages/materials/index');
  const goToWorkLogs = () => navigateTo('/pages/work-logs/index');
  const goToMyDepartment = () => navigateTo('/pages/my-department/index');
  const goToUserProfile = () => navigateTo('/pages/user-profile/index');

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 6) return '夜深了';
    if (hour < 9) return '早上好';
    if (hour < 12) return '上午好';
    if (hour < 14) return '中午好';
    if (hour < 18) return '下午好';
    if (hour < 22) return '晚上好';
    return '夜深了';
  };

  const formatDate = () => {
    const now = new Date();
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    return {
      date: `${now.getMonth() + 1}月${now.getDate()}日`,
      weekday: weekdays[now.getDay()]
    };
  };

  const getProjectStatusLabel = (status: string) => {
    const map: Record<string, string> = {
      planning: '规划中',
      active: '进行中',
      completed: '已完成',
      suspended: '已暂停'
    };
    return map[status] || status;
  };

  const getProjectStatusClass = (status: string) => {
    const map: Record<string, string> = {
      planning: styles.statusPlanning,
      active: styles.statusActive,
      completed: styles.statusCompleted,
      suspended: styles.statusSuspended
    };
    return map[status] || '';
  };

  const getBugStatusLabel = (status: string) => {
    const map: Record<string, string> = {
      new: '新建',
      in_progress: '处理中',
      resolved: '已解决',
      closed: '已关闭',
      rejected: '已拒绝',
      reopened: '重新打开'
    };
    return map[status] || status;
  };

  const getBugSeverityClass = (severity: string) => {
    const map: Record<string, string> = {
      critical: styles.severityCritical,
      high: styles.severityHigh,
      medium: styles.severityMedium,
      low: styles.severityLow,
      suggestion: styles.severitySuggestion
    };
    return map[severity] || '';
  };

  const renderTrendChart = () => {
    const displayData = trendData.slice(-10);
    const maxValue = Math.max(
      ...displayData.map(d => Math.max(d.new_bugs, d.resolved_bugs, d.cumulative_unresolved))
    );

    return (
      <View className={styles.chartBars}>
        {displayData.map((item, index) => (
          <View key={index} className={styles.barGroup}>
            <View className={styles.barWrapper}>
              <View
                className={classnames(styles.bar, styles.barNew)}
                style={{ height: `${(item.new_bugs / maxValue) * 200}rpx` }}
              />
              <View
                className={classnames(styles.bar, styles.barResolved)}
                style={{ height: `${(item.resolved_bugs / maxValue) * 200}rpx` }}
              />
            </View>
            <Text className={styles.barLabel}>{item.date}</Text>
          </View>
        ))}
      </View>
    );
  };

  const dateInfo = formatDate();

  return (
    <View className={styles.container}>
      {/* 顶部 Header：渐变 + 用户问候 + 时间 */}
      <View className={styles.header}>
        <View className={styles.headerTop}>
          <View className={styles.userBlock} onClick={goToUserProfile}>
            <View className={styles.avatar}>
              <Text>{currentUser.realName.charAt(0)}</Text>
            </View>
            <View className={styles.userInfo}>
              <Text className={styles.greeting}>{getGreeting()}</Text>
              <Text className={styles.userName}>{currentUser.realName} · {currentUser.position}</Text>
            </View>
          </View>
          <View className={styles.headerRight}>
            <View className={styles.dateBadge}>
              <Text className={styles.dateText}>{dateInfo.date}</Text>
              <Text className={styles.weekText}>{dateInfo.weekday}</Text>
            </View>
            <View className={styles.notifBtn} onClick={goToNotifications}>
              <Text className={styles.notifIcon}>🔔</Text>
              {recentNotifications.filter(n => !n.is_read).length > 0 && (
                <View className={styles.notifDot} />
              )}
            </View>
          </View>
        </View>

        {/* 顶部 KPI 行 */}
        <View className={styles.headerKpis}>
          <View className={styles.headerKpi} onClick={goToMyTodos}>
            <Text className={styles.headerKpiValue}>{todoSummary.total}</Text>
            <Text className={styles.headerKpiLabel}>待办</Text>
          </View>
          <View className={styles.headerDivider} />
          <View className={styles.headerKpi} onClick={goToProjectList}>
            <Text className={styles.headerKpiValue}>{recentProjects.length}</Text>
            <Text className={styles.headerKpiLabel}>参与项目</Text>
          </View>
          <View className={styles.headerDivider} />
          <View className={styles.headerKpi} onClick={() => goToBugList('unresolved')}>
            <Text className={styles.headerKpiValue}>{kpiData.unresolved_bugs}</Text>
            <Text className={styles.headerKpiLabel}>未解决Bug</Text>
          </View>
          <View className={styles.headerDivider} />
          <View className={styles.headerKpi} onClick={goToWorkStatistics}>
            <Text className={styles.headerKpiValue}>{workStats.totalHours}h</Text>
            <Text className={styles.headerKpiLabel}>本月工时</Text>
          </View>
        </View>
      </View>

      <ScrollView
        scrollY
        className={styles.content}
        enableBackToTop
        onScrollToUpper={onPullDownRefresh}
      >
        {/* 核心 KPI 看板 */}
        <View className={styles.sectionTitle}>
          <View className={styles.dot} />
          <Text>Bug 核心指标</Text>
        </View>
        <View className={styles.kpiGrid}>
          <View
            className={classnames(styles.kpiCard, styles.kpiPrimary)}
            onClick={() => goToBugList()}
          >
            <View className={styles.kpiHeader}>
              <View className={styles.kpiIcon}>
                <Text className={styles.kpiIconText}>🐛</Text>
              </View>
              <View
                className={classnames(
                  styles.kpiTrend,
                  kpiData.total_change > 0 && styles.trendUp,
                  kpiData.total_change < 0 && styles.trendDown,
                  kpiData.total_change === 0 && styles.trendStable
                )}
              >
                <Text>{kpiData.total_change > 0 ? '↑' : kpiData.total_change < 0 ? '↓' : '-'}</Text>
                <Text>{Math.abs(kpiData.total_change)}%</Text>
              </View>
            </View>
            <View className={styles.kpiBody}>
              <Text className={classnames(styles.kpiValue, styles.kpiValueLarge)}>
                {kpiData.total_bugs.toLocaleString()}
              </Text>
              <Text className={styles.kpiLabel}>总 Bug 数</Text>
            </View>
          </View>

          <View
            className={classnames(styles.kpiCard, styles.kpiWarning)}
            onClick={() => goToBugList('new')}
          >
            <View className={styles.kpiHeader}>
              <View className={styles.kpiIcon}>
                <Text className={styles.kpiIconText}>✨</Text>
              </View>
            </View>
            <View className={styles.kpiBody}>
              <Text className={styles.kpiValue}>{kpiData.new_bugs}</Text>
              <Text className={styles.kpiLabel}>新增 Bug</Text>
            </View>
          </View>

          <View
            className={classnames(styles.kpiCard, styles.kpiSuccess)}
            onClick={() => goToBugList('resolved')}
          >
            <View className={styles.kpiHeader}>
              <View className={styles.kpiIcon}>
                <Text className={styles.kpiIconText}>✅</Text>
              </View>
            </View>
            <View className={styles.kpiBody}>
              <Text className={styles.kpiValue}>{kpiData.resolved_bugs}</Text>
              <Text className={styles.kpiLabel}>已解决</Text>
            </View>
          </View>

          <View
            className={classnames(styles.kpiCard, styles.kpiError)}
            onClick={() => goToBugList('unresolved')}
          >
            <View className={styles.kpiHeader}>
              <View className={styles.kpiIcon}>
                <Text className={styles.kpiIconText}>⚠️</Text>
              </View>
            </View>
            <View className={styles.kpiBody}>
              <Text className={styles.kpiValue}>{kpiData.unresolved_bugs}</Text>
              <Text className={styles.kpiLabel}>未解决</Text>
            </View>
          </View>

          <View className={classnames(styles.kpiCard, styles.kpiInfo)}>
            <View className={styles.kpiHeader}>
              <View className={styles.kpiIcon}>
                <Text className={styles.kpiIconText}>📈</Text>
              </View>
            </View>
            <View className={styles.kpiBody}>
              <View className={styles.kpiValue}>
                <Text>{kpiData.resolution_rate}</Text>
                <Text className={styles.kpiUnit}>%</Text>
              </View>
              <Text className={styles.kpiLabel}>解决率</Text>
            </View>
          </View>

          <View className={classnames(styles.kpiCard, styles.kpiPurple)}>
            <View className={styles.kpiHeader}>
              <View className={styles.kpiIcon}>
                <Text className={styles.kpiIconText}>⏱️</Text>
              </View>
            </View>
            <View className={styles.kpiBody}>
              <View className={styles.kpiValue}>
                <Text>{kpiData.avg_fix_time}</Text>
                <Text className={styles.kpiUnit}>天</Text>
              </View>
              <Text className={styles.kpiLabel}>平均解决时长</Text>
            </View>
          </View>
        </View>

        {/* Bug 趋势 */}
        <View className={styles.sectionTitle}>
          <View className={styles.dot} />
          <Text>Bug 趋势分析</Text>
        </View>
        <View className={styles.trendCard}>
          <View className={styles.chartHeader}>
            <Text className={styles.chartTitle}>Bug 趋势</Text>
            <View className={styles.granularity}>
              {(['day', 'week', 'month'] as const).map(item => (
                <Button
                  key={item}
                  className={classnames(
                    styles.granularityBtn,
                    granularity === item && styles.granularityBtnActive
                  )}
                  onClick={() => setGranularity(item)}
                >
                  {item === 'day' ? '日' : item === 'week' ? '周' : '月'}
                </Button>
              ))}
            </View>
          </View>
          {renderTrendChart()}
          <View className={styles.chartLegend}>
            <View className={styles.legendItem}>
              <View className={classnames(styles.legendDot, styles.legendDotNew)} />
              <Text>新增 Bug</Text>
            </View>
            <View className={styles.legendItem}>
              <View className={classnames(styles.legendDot, styles.legendDotResolved)} />
              <Text>已解决</Text>
            </View>
          </View>
        </View>

        {/* 我参与的项目 */}
        <View className={styles.sectionTitle}>
          <View className={styles.dot} />
          <Text>我参与的项目</Text>
          <Text className={styles.sectionMore} onClick={goToProjectList}>
            查看全部 ›
          </Text>
        </View>
        <View className={styles.projectList}>
          {recentProjects.slice(0, 3).map(project => (
            <View
              key={project.id}
              className={styles.projectCard}
              onClick={() => goToProjectDetail(project.id)}
            >
              <View className={styles.projectHeader}>
                <Text className={styles.projectName}>{project.name}</Text>
                <Text className={classnames(styles.projectStatus, getProjectStatusClass(project.status))}>
                  {getProjectStatusLabel(project.status)}
                </Text>
              </View>
              <Text className={styles.projectDesc}>{project.description}</Text>
              <View className={styles.projectProgress}>
                <View className={styles.progressBar}>
                  <View
                    className={styles.progressFill}
                    style={{ width: `${project.completion_rate}%` }}
                  />
                </View>
                <Text className={styles.progressText}>{project.completion_rate}%</Text>
              </View>
              <View className={styles.projectFooter}>
                <Text className={styles.projectMeta}>
                  👤 {project.manager_name} · {project.member_count}人 · 🐛 {project.bug_count}
                </Text>
              </View>
            </View>
          ))}
        </View>

        {/* 最近 Bug */}
        <View className={styles.sectionTitle}>
          <View className={styles.dot} />
          <Text>最近 Bug</Text>
          <Text className={styles.sectionMore} onClick={() => goToBugList()}>
            查看全部 ›
          </Text>
        </View>
        <View className={styles.bugList}>
          {recentBugs.map(bug => (
            <View
              key={bug.id}
              className={styles.bugCard}
              onClick={() => goToBugDetail(bug.id)}
            >
              <View className={styles.bugCardHeader}>
                <Text className={styles.bugId}>#{bug.id}</Text>
                <Text className={classnames(styles.bugSeverity, getBugSeverityClass(bug.severity))}>
                  {bug.severity}
                </Text>
              </View>
              <Text className={styles.bugTitle}>{bug.title}</Text>
              <View className={styles.bugMeta}>
                <Text className={styles.bugStatus}>{getBugStatusLabel(bug.status)}</Text>
                <Text className={styles.bugProject}>📁 {bug.project_name}</Text>
                <Text className={styles.bugReporter}>👤 {bug.reporter_name}</Text>
              </View>
            </View>
          ))}
        </View>

        {/* 快捷入口 */}
        <View className={styles.sectionTitle}>
          <View className={styles.dot} />
          <Text>功能导航</Text>
        </View>
        <View className={styles.quickGrid}>
          <View className={styles.quickItem} onClick={() => goToBugList('new')}>
            <View className={classnames(styles.quickIcon, styles.quickIconBug)}>
              <Text>🐛</Text>
            </View>
            <Text className={styles.quickLabel}>新建 Bug</Text>
          </View>
          <View className={styles.quickItem} onClick={goToProjectList}>
            <View className={classnames(styles.quickIcon, styles.quickIconProject)}>
              <Text>📁</Text>
            </View>
            <Text className={styles.quickLabel}>项目</Text>
          </View>
          <View className={styles.quickItem} onClick={goToMyTodos}>
            <View className={classnames(styles.quickIcon, styles.quickIconTodo)}>
              <Text>✅</Text>
            </View>
            <Text className={styles.quickLabel}>我的待办</Text>
          </View>
          <View className={styles.quickItem} onClick={goToAttendance}>
            <View className={classnames(styles.quickIcon, styles.quickIconAttendance)}>
              <Text>📅</Text>
            </View>
            <Text className={styles.quickLabel}>考勤打卡</Text>
          </View>
          <View className={styles.quickItem} onClick={goToContracts}>
            <View className={classnames(styles.quickIcon, styles.quickIconContract)}>
              <Text>📄</Text>
            </View>
            <Text className={styles.quickLabel}>合同管理</Text>
          </View>
          <View className={styles.quickItem} onClick={goToKnowledge}>
            <View className={classnames(styles.quickIcon, styles.quickIconKnowledge)}>
              <Text>📚</Text>
            </View>
            <Text className={styles.quickLabel}>知识库</Text>
          </View>
          <View className={styles.quickItem} onClick={goToPersonalPlan}>
            <View className={classnames(styles.quickIcon, styles.quickIconPlan)}>
              <Text>📆</Text>
            </View>
            <Text className={styles.quickLabel}>个人计划</Text>
          </View>
          <View className={styles.quickItem} onClick={goToWorkStatistics}>
            <View className={classnames(styles.quickIcon, styles.quickIconStats)}>
              <Text>📊</Text>
            </View>
            <Text className={styles.quickLabel}>工作统计</Text>
          </View>
          <View className={styles.quickItem} onClick={goToActivity}>
            <View className={classnames(styles.quickIcon, styles.quickIconActivity)}>
              <Text>📋</Text>
            </View>
            <Text className={styles.quickLabel}>活动记录</Text>
          </View>
          <View className={styles.quickItem} onClick={goToWorkLogs}>
            <View className={classnames(styles.quickIcon, styles.quickIconLog)}>
              <Text>📝</Text>
            </View>
            <Text className={styles.quickLabel}>工作日志</Text>
          </View>
          <View className={styles.quickItem} onClick={goToMaterials}>
            <View className={classnames(styles.quickIcon, styles.quickIconMaterial)}>
              <Text>📦</Text>
            </View>
            <Text className={styles.quickLabel}>物料管理</Text>
          </View>
          <View className={styles.quickItem} onClick={goToMyDepartment}>
            <View className={classnames(styles.quickIcon, styles.quickIconDept)}>
              <Text>🏢</Text>
            </View>
            <Text className={styles.quickLabel}>我的部门</Text>
          </View>
        </View>

        {/* 动态 / 通知 */}
        <View className={styles.sectionTitle}>
          <View className={styles.dot} />
          <Text>最近动态</Text>
          <Text className={styles.sectionMore} onClick={goToActivity}>
            查看全部 ›
          </Text>
        </View>
        <View className={styles.activityList}>
          {recentActivities.map(activity => (
            <View key={activity.id} className={styles.activityItem}>
              <View className={styles.activityDot} />
              <View className={styles.activityContent}>
                <View className={styles.activityHeader}>
                  <Text className={styles.activityType}>{activity.activityType}</Text>
                  <Text className={styles.activityTime}>{activity.operateTime}</Text>
                </View>
                <Text className={styles.activityTitle}>{activity.title}</Text>
                <Text className={styles.activityOperator}>{activity.operator} · {activity.projectName}</Text>
              </View>
            </View>
          ))}
        </View>

        <View className={styles.footer}>
          <Text>TOPO 系统 v1.0 · 移动工作台</Text>
        </View>
      </ScrollView>

      {loading && (
        <View className={styles.loadingOverlay}>
          <View className={styles.loadingSpinner} />
        </View>
      )}
    </View>
  );
};

export default HomePage;
