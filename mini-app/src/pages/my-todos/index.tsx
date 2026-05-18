import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import classnames from 'classnames';
import styles from './index.module.scss';
import { Todo } from '../../types/business';
import { mockTodos } from '../../data/businessData';

const MyTodosPage: React.FC = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeFilter, setActiveFilter] = useState<string>('all');

  const statusFilters = [
    { key: 'all', label: '全部' },
    { key: 'pending', label: '待处理' },
    { key: 'in_progress', label: '进行中' },
    { key: 'completed', label: '已完成' }
  ];

  useEffect(() => {
    loadTodos(true);
  }, [activeFilter]);

  const loadTodos = async (reset = false) => {
    if (loading) return;

    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));

      let filteredData = [...mockTodos];

      if (activeFilter !== 'all') {
        filteredData = filteredData.filter(todo => todo.status === activeFilter);
      }

      setTodos(filteredData);
      console.log(`[MyTodos] Loaded ${filteredData.length} todos`);
    } catch (error) {
      console.error('[MyTodos] Error loading todos:', error);
      Taro.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const onPullDownRefresh = () => {
    loadTodos(true).then(() => {
      Taro.stopPullDownRefresh();
      Taro.showToast({
        title: '刷新成功',
        icon: 'success'
      });
    });
  };

  const handleFilterChange = (filter: string) => {
    setActiveFilter(filter);
  };

  const handleComplete = (todoId: number) => {
    setTodos(prev => prev.map(todo =>
      todo.id === todoId ? { ...todo, status: 'completed' as const } : todo
    ));
    Taro.showToast({
      title: '任务已完成',
      icon: 'success'
    });
  };

  const getPriorityLabel = (priority: string): string => {
    const labels: Record<string, string> = {
      'urgent': '紧急',
      'high': '高',
      'medium': '中',
      'low': '低'
    };
    return labels[priority] || priority;
  };

  const getStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      'pending': '待处理',
      'in_progress': '进行中',
      'completed': '已完成'
    };
    return labels[status] || status;
  };

  const getPriorityClass = (priority: string) => {
    const classMap: Record<string, string> = {
      'urgent': styles.priorityUrgent,
      'high': styles.priorityHigh,
      'medium': styles.priorityMedium,
      'low': styles.priorityLow
    };
    return classMap[priority] || '';
  };

  const getStatusClass = (status: string) => {
    const classMap: Record<string, string> = {
      'pending': styles.statusPending,
      'in_progress': styles.statusInProgress,
      'completed': styles.statusCompleted
    };
    return classMap[status] || '';
  };

  const getTodoCardClass = (priority: string) => {
    const classMap: Record<string, string> = {
      'urgent': styles.priorityUrgent,
      'high': styles.priorityHigh,
      'medium': styles.priorityMedium,
      'low': styles.priorityLow
    };
    return classMap[priority] || '';
  };

  const isOverdue = (dueDate?: string) => {
    if (!dueDate) return false;
    return new Date(dueDate) < new Date();
  };

  const formatDueDate = (dueDate?: string) => {
    if (!dueDate) return '';
    const date = new Date(dueDate);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days < 0) {
      return `剩余${Math.abs(days)}天`;
    } else if (days === 0) {
      return '今天到期';
    } else {
      return `已逾期${days}天`;
    }
  };

  return (
    <View className={styles.container}>
      <View className={styles.filterBar}>
        <ScrollView scrollX className={styles.filterScroll} enableFlex>
          {statusFilters.map(filter => (
            <View
              key={filter.key}
              className={classnames(
                styles.filterChip,
                activeFilter === filter.key && styles.active
              )}
              onClick={() => handleFilterChange(filter.key)}
            >
              {filter.label}
            </View>
          ))}
        </ScrollView>
      </View>

      <ScrollView
        scrollY
        className={styles.todoList}
        enableBackToTop
        onPullDownRefresh={onPullDownRefresh}
      >
        {todos.length === 0 ? (
          <View className={styles.emptyState}>
            <Text className={styles.emptyIcon}>✅</Text>
            <Text className={styles.emptyText}>暂无待办任务</Text>
            <Text className={styles.emptyHint}>太棒了，所有任务都已完成！</Text>
          </View>
        ) : (
          <>
            {todos.map(todo => (
              <View
                key={todo.id}
                className={classnames(styles.todoCard, getTodoCardClass(todo.priority))}
              >
                <View className={styles.todoHeader}>
                  <Text className={styles.todoTitle}>{todo.title}</Text>
                  <Text className={classnames(styles.priorityBadge, getPriorityClass(todo.priority))}>
                    {getPriorityLabel(todo.priority)}
                  </Text>
                </View>

                {todo.description && (
                  <Text className={styles.todoDesc}>{todo.description}</Text>
                )}

                <View className={styles.todoMeta}>
                  <Text className={classnames(styles.tag, getStatusClass(todo.status))}>
                    {getStatusLabel(todo.status)}
                  </Text>
                  {todo.project_name && (
                    <Text className={classnames(styles.tag, styles.projectTag)}>
                      {todo.project_name}
                    </Text>
                  )}
                </View>

                <View className={styles.todoFooter}>
                  {todo.due_date && (
                    <View className={classnames(
                      styles.dueDate,
                      isOverdue(todo.due_date) && styles.overdue
                    )}>
                      <Text>📅</Text>
                      <Text>{formatDueDate(todo.due_date)}</Text>
                    </View>
                  )}
                  {todo.status !== 'completed' && (
                    <View
                      className={styles.completeBtn}
                      onClick={() => handleComplete(todo.id)}
                    >
                      完成
                    </View>
                  )}
                </View>
              </View>
            ))}
          </>
        )}
      </ScrollView>
    </View>
  );
};

export default MyTodosPage;
