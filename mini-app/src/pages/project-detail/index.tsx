import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import classnames from 'classnames';
import styles from './index.module.scss';
import { Project } from '../../types/business';
import { mockProjects } from '../../data/businessData';

const ProjectDetailPage: React.FC = () => {
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProjectDetail();
  }, []);

  const loadProjectDetail = async () => {
    const { id } = Taro.getCurrentInstance().router?.params || {};

    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 300));
      const projectData = mockProjects.find(p => p.id === Number(id)) || mockProjects[0];
      setProject(projectData);
      console.log('[ProjectDetail] Loaded project:', projectData);
    } catch (error) {
      console.error('[ProjectDetail] Error loading project:', error);
      Taro.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      setLoading(false);
    }
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

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  };

  const handleAction = (action: string) => {
    switch (action) {
      case 'bugs':
        Taro.navigateTo({
          url: `/pages/bug-list/index?project=${project?.id}`
        });
        break;
      case 'members':
        Taro.showToast({
          title: '成员管理功能开发中',
          icon: 'info'
        });
        break;
      case 'documents':
        Taro.showToast({
          title: '文档管理功能开发中',
          icon: 'info'
        });
        break;
      case 'settings':
        Taro.showToast({
          title: '项目设置功能开发中',
          icon: 'info'
        });
        break;
    }
  };

  if (loading || !project) {
    return (
      <View className={styles.container}>
        <View className={styles.header}>
          <Text style={{ color: '#fff' }}>加载中...</Text>
        </View>
      </View>
    );
  }

  return (
    <View className={styles.container}>
      <View className={styles.header}>
        <Text className={styles.projectName}>{project.name}</Text>
        <View className={styles.statusBadge}>
          <Text>{getStatusLabel(project.status)}</Text>
        </View>
      </View>

      <ScrollView scrollY className={styles.content}>
        <View className={styles.infoCard}>
          <View className={styles.infoRow}>
            <Text className={styles.infoLabel}>项目名称</Text>
            <Text className={styles.infoValue}>{project.name}</Text>
          </View>
          <View className={styles.infoRow}>
            <Text className={styles.infoLabel}>项目经理</Text>
            <Text className={styles.infoValue}>{project.manager_name}</Text>
          </View>
          <View className={styles.infoRow}>
            <Text className={styles.infoLabel}>开始日期</Text>
            <Text className={styles.infoValue}>{formatDate(project.start_date)}</Text>
          </View>
          {project.end_date && (
            <View className={styles.infoRow}>
              <Text className={styles.infoLabel}>结束日期</Text>
              <Text className={styles.infoValue}>{formatDate(project.end_date)}</Text>
            </View>
          )}
          <View className={styles.infoRow}>
            <Text className={styles.infoLabel}>团队成员</Text>
            <Text className={styles.infoValue}>{project.member_count} 人</Text>
          </View>
        </View>

        <View className={styles.descriptionSection}>
          <View className={styles.sectionTitle}>
            <Text>📝</Text>
            <Text>项目描述</Text>
          </View>
          <Text className={styles.description}>{project.description}</Text>
        </View>

        <View className={styles.progressSection}>
          <View className={styles.sectionTitle}>
            <Text>📊</Text>
            <Text>项目进度</Text>
          </View>
          <View className={styles.progressHeader}>
            <Text className={styles.progressLabel}>完成度</Text>
            <Text className={styles.progressValue}>{project.completion_rate}%</Text>
          </View>
          <View className={styles.progressBar}>
            <View
              className={styles.progressFill}
              style={{ width: `${project.completion_rate}%` }}
            />
          </View>
          <View className={styles.statsGrid}>
            <View className={styles.statItem}>
              <Text className={styles.statValue}>{project.member_count}</Text>
              <Text className={styles.statLabel}>团队成员</Text>
            </View>
            <View className={styles.statItem}>
              <Text className={styles.statValue}>{project.bug_count}</Text>
              <Text className={styles.statLabel}>Bug总数</Text>
            </View>
            <View className={styles.statItem}>
              <Text className={styles.statValue}>{project.completion_rate}%</Text>
              <Text className={styles.statLabel}>完成率</Text>
            </View>
          </View>
        </View>

        <View className={styles.quickActions}>
          <View className={styles.sectionTitle}>
            <Text>⚡</Text>
            <Text>快捷操作</Text>
          </View>
          <View className={styles.actionsGrid}>
            <View className={styles.actionItem} onClick={() => handleAction('bugs')}>
              <View className={styles.actionIcon} style={{ background: 'rgba(255, 77, 79, 0.1)' }}>
                <Text>🐛</Text>
              </View>
              <Text className={styles.actionLabel}>Bug列表</Text>
            </View>
            <View className={styles.actionItem} onClick={() => handleAction('members')}>
              <View className={styles.actionIcon} style={{ background: 'rgba(24, 144, 255, 0.1)' }}>
                <Text>👥</Text>
              </View>
              <Text className={styles.actionLabel}>成员</Text>
            </View>
            <View className={styles.actionItem} onClick={() => handleAction('documents')}>
              <View className={styles.actionIcon} style={{ background: 'rgba(250, 173, 20, 0.1)' }}>
                <Text>📄</Text>
              </View>
              <Text className={styles.actionLabel}>文档</Text>
            </View>
            <View className={styles.actionItem} onClick={() => handleAction('settings')}>
              <View className={styles.actionIcon} style={{ background: 'rgba(82, 196, 26, 0.1)' }}>
                <Text>⚙️</Text>
              </View>
              <Text className={styles.actionLabel}>设置</Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </View>
  );
};

export default ProjectDetailPage;
