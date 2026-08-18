import api from './api.js'

/**
 * 项目研发管理 - Kanban 看板服务
 */
const rdKanbanService = {
  /** 获取某项目所有 Kanban 卡片及列定义 */
  list: (projectId) => api.get(`/rd-kanban/${projectId}`),

  /** 新建卡片 */
  create: (payload) => api.post('/rd-kanban', payload),

  /** 更新卡片 */
  update: (id, payload) => api.put(`/rd-kanban/${id}`, payload),

  /** 删除卡片 */
  remove: (id) => api.delete(`/rd-kanban/${id}`),

  /** 批量更新排序/换列 */
  sort: (moves) => api.put('/rd-kanban/sort', { moves }),

  /** 获取卡片详情（item + comments + attachments） */
  detail: (itemId) => api.get(`/rd-kanban/${itemId}/detail`),

  // 评论
  listComments: (itemId) => api.get(`/rd-kanban/${itemId}/comments`),
  addComment: (itemId, payload) => api.post(`/rd-kanban/${itemId}/comments`, payload),
  updateComment: (commentId, payload) => api.put(`/rd-kanban/comments/${commentId}`, payload),
  deleteComment: (commentId) => api.delete(`/rd-kanban/comments/${commentId}`),
  reactComment: (commentId, emoji) => api.post(`/rd-kanban/comments/${commentId}/react`, { emoji }),

  // 附件
  listAttachments: (itemId) => api.get(`/rd-kanban/${itemId}/attachments`),
  uploadAttachment: (itemId, formData) =>
    api.post(`/rd-kanban/${itemId}/attachments`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  deleteAttachment: (attId) => api.delete(`/rd-kanban/attachments/${attId}`),
  attachmentDownloadUrl: (attId) => `/api/rd-kanban/attachments/${attId}/download`,
}

export default rdKanbanService

