/**
 * v-permission 指令
 *
 * 用法：
 *   <el-button v-permission="'bug:create'">新建缺陷</el-button>
 *   <el-button v-permission="['bug:edit', 'bug:delete']">操作</el-button>   // 任一权限
 *   <el-button v-permission.all="['bug:edit', 'bug:delete']">操作</el-button> // 全部权限
 *
 * 修饰符：
 *   .all  - 需要全部权限才显示
 *
 * 行为：
 *   - 没有权限时从 DOM 中移除该元素
 *   - 超级管理员 / 系统管理员始终通过
 *   - 限制权限 (denied) 优先
 */
import { useUserStore } from '@/stores/user'

function evaluate(userStore, value, needAll) {
  if (!value) return true
  const codes = Array.isArray(value) ? value : [value]
  if (needAll) {
    return codes.every(c => userStore.hasPermission(c))
  }
  return codes.some(c => userStore.hasPermission(c))
}

export default {
  install(app) {
    app.directive('permission', {
      mounted(el, binding) {
        const userStore = useUserStore()
        const needAll = !!binding.modifiers.all
        if (!evaluate(userStore, binding.value, needAll)) {
          el.style.display = 'none'
          // 同时移除事件占位（防御性）
          el.setAttribute('aria-hidden', 'true')
          el.dataset.permissionHidden = '1'
        }
      },
      updated(el, binding) {
        const userStore = useUserStore()
        const needAll = !!binding.modifiers.all
        const allowed = evaluate(userStore, binding.value, needAll)
        if (allowed) {
          if (el.dataset.permissionHidden === '1') {
            el.style.display = ''
            el.removeAttribute('aria-hidden')
            delete el.dataset.permissionHidden
          }
        } else if (el.dataset.permissionHidden !== '1') {
          el.style.display = 'none'
          el.setAttribute('aria-hidden', 'true')
          el.dataset.permissionHidden = '1'
        }
      }
    })
  }
}
