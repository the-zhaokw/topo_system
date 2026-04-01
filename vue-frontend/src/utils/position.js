/**
 * 职位权限工具函数
 * 用于检查用户的职位和权限
 */

/**
 * 检查用户是否为管理员
 * @param {Object} user - 用户对象
 * @returns {boolean} - 是否为管理员
 */
export const isAdmin = (user) => {
  if (!user) return false
  if (user.is_super_admin) return true
  if (user.is_admin) return true
  return user.position === '管理员' ||
         user.position === '超级管理员' ||
         user.position === '经理' ||
         user.position === '项目经理' ||
         user.position === '部门经理' ||
         user.position === '人事专员'
}

/**
 * 检查用户是否为部门经理
 * @param {Object} user - 用户对象
 * @returns {boolean} - 是否为部门经理
 */
export const isDepartmentManager = (user) => {
  if (!user) return false
  return user.position === '部门经理' ||
         user.position === '部门负责人' ||
         user.position?.includes('经理') ||
         user.position?.includes('主管')
}

/**
 * 检查用户是否为项目经理
 * @param {Object} user - 用户对象
 * @returns {boolean} - 是否为项目经理
 */
export const isProjectManager = (user) => {
  if (!user) return false
  return user.position === '项目经理'
}

/**
 * 检查用户是否为测试工程师
 * @param {Object} user - 用户对象
 * @returns {boolean} - 是否为测试工程师
 */
export const isTester = (user) => {
  if (!user) return false
  return user.position === '测试工程师'
}

/**
 * 检查用户是否为软件工程师
 * @param {Object} user - 用户对象
 * @returns {boolean} - 是否为软件工程师
 */
export const isDeveloper = (user) => {
  if (!user) return false
  return user.position === '软件工程师'
}

/**
 * 检查用户是否为开发者或管理者
 * @param {Object} user - 用户对象
 * @returns {boolean} - 是否为开发者或管理者
 */
export const isDeveloperOrManager = (user) => {
  if (!user) return false
  return user.position === '软件工程师' ||
         user.position === '测试工程师' ||
         user.position?.includes('经理') ||
         user.position === '项目经理' ||
         user.position === '部门经理'
}

/**
 * 检查用户是否具有管理权限（管理员、项目经理或超级管理员）
 * @param {Object} user - 用户对象
 * @returns {boolean} - 是否具有管理权限
 */
export const hasManagementPermission = (user) => {
  if (!user) return false
  if (user.is_super_admin) return true
  return user.position === '管理员' ||
         user.position === '超级管理员' ||
         user.position === '经理' ||
         user.position === '项目经理' ||
         user.position === '部门经理' ||
         user.position === '人事专员' ||
         user.position?.includes('经理')
}

/**
 * 获取用户的职位名称
 * @param {Object} user - 用户对象
 * @returns {string} - 职位名称
 */
export const getPositionName = (user) => {
  if (!user) return ''
  return user.position || ''
}

/**
 * 检查用户是否为超级管理员
 * @param {Object} user - 用户对象
 * @returns {boolean} - 是否为超级管理员
 */
export const isSuperAdmin = (user) => {
  if (!user) return false
  return !!user.is_super_admin
}

/**
 * 职位分类
 */
export const PositionCategory = {
  MANAGEMENT: ['超级管理员', '经理', '项目经理', '部门经理', '部门负责人', '人事专员', '管理员'],
  ENGINEERING: ['软件工程师', '测试工程师', '开发工程师', '前端工程师', '后端工程师', '全栈工程师'],
  GENERAL: ['普通用户', '实习生', '外包人员', '兼职人员']
}

/**
 * 检查用户是否属于管理职位
 * @param {Object} user - 用户对象
 * @returns {boolean}
 */
export const isManagementPosition = (user) => {
  if (!user) return false
  return PositionCategory.MANAGEMENT.includes(user.position)
}

/**
 * 检查用户是否属于工程技术职位
 * @param {Object} user - 用户对象
 * @returns {boolean}
 */
export const isEngineeringPosition = (user) => {
  if (!user) return false
  return PositionCategory.ENGINEERING.includes(user.position)
}
