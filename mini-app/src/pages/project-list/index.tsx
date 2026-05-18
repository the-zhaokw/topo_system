import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import classnames from 'classnames';
import styles from './index.module.scss';
import { Project } from '../../types/business';
import { mockProjects } from '../../data/businessData';

const ProjectListPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      setProjects(mockProjects);
      console.log('[ProjectList] Loaded projects:', mockProjects.length);
    } catch (error) {
      console.error('[ProjectList] Error loading projects:', error);
      Taro.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const onPullDownRefresh = () => {
    loadProjects().then(() => {
      Taro.stopPullDownRefresh();
      Taro.showToast({
        title: '刷新成功',
        icon: 'success'
      });
    });
  };

  const navigateToDetail = (projectId: number) => {
    Taro.navigateTo({
      url: `/pages/project-detail/index?id=${projectId}`
    });
  };

  const getStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      'planning': '规划中',
      'active': '进行中',
      'completed': '已完成',
      'suspended': '已暂停'
    };
    return labels[status] || status;
  };

  const getStatusClass = (status: string) => {
    const classMap: Record<string, string> = {
      'planning': styles.statusPlanning,
      'active': styles.statusActive,
      'completed': styles.statusCompleted,
      'suspended': styles.statusSuspended
    };
    return classMap[status] || '';
  };

  const getInitials = (name: string) => {
    return name.charAt(0).toUpperCase();
  };

  const formatDateRange = (startDate: string, endDate?: string) => {
    const start = new Date(startDate).toLocaleDateString('zh-CN', {
      month: '2-digit',
      day: '2-digit'
    });

    if (!endDate) {
      return `${start} - 进行中`;
    }

    const end = new Date(endDate).toLocaleDateString('zh-CN', {
      month: '2-digit',
      day: '2-digit'
    });
    return `${start} - ${end}`;
  };

  return (
    <View className={styles.container}>
      <ScrollView
        scrollY
        className={styles.projectList}
        enableBackToTop
        onPullDownRefresh={onPullDownRefresh}
      >
        {projects.length === 0 ? (
          <View className={styles.emptyState}>
            <Text className={styles.emptyIcon}>📁</Text>
            <Text className={styles.emptyText}>暂无项目数据</Text>
            <Text className={styles.emptyHint}>创建第一个项目吧</Text>
          </View>
        ) : (
          <>
            {projects.map(project => (
              <View
                key={project.id}
                className={styles.projectCard}
                onClick={() => navigateToDetail(project.id)}
              >
                <View className={styles.projectHeader}>
                  <Text className={styles.projectName}>{project.name}</Text>
                  <Text className={classnames(styles.statusBadge, getStatusClass(project.status))}>
                    {getStatusLabel(project.status)}
                  </Text>
                </View>

                <Text className={styles.projectDesc}>{project.description}</Text>

                <View className={styles.progressSection}>
                  <View className={styles.progressHeader}>
                    <Text className={styles.progressLabel}>项目进度</Text>
                    <Text className={styles.progressValue}>{project.completion_rate}%</Text>
                  </View>
                  <View className={styles.progressBar}>
                    <View
                      className={styles.progressFill}
                      style={{ width: `${project.completion_rate}%` }}
                    />
                  </View>
                </View>

                <View className={styles.statsRow}>
                  <View className={styles.statItem}>
                    <Text className={styles.statValue}>{project.member_count}</Text>
                    <Text className={styles.statLabel}>成员</Text>
                  </View>
                  <View className={styles.statItem}>
                    <Text className={styles.statValue}>{project.bug_count}</Text>
                    <Text className={styles.statLabel}>Bug</Text>
                  </View>
                  <View className={styles.statItem}>
                    <Text className={styles.statValue}>{project.completion_rate}%</Text>
                    <Text className={styles.statLabel}>完成度</Text>
                  </View>
                </View>

                <View className={styles.projectFooter}>
                  <View className={styles.manager}>
                    <View className={styles.managerAvatar}>
                      <Text>{getInitials(project.manager_name)}</Text>
                    </View>
                    <Text className={styles.managerName}>{project.manager_name}</Text>
                  </View>
                  <Text className={styles.dateRange}>
                    {formatDateRange(project.start_date, project.end_date)}
                  </Text>
                </View>
              </View>
            ))}

            {loading && (
              <View className={styles.loadingMore}>
                <Text>加载中...</Text>
              </View>
            )}
          </>
        )}
      </ScrollView>
    </View>
  );
};

export default ProjectListPage;
