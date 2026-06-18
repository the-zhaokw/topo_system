/**
 * v-permission 指令
 *
 * 用法：
 *   <el-button v-permission="'bug:create'">新建缺陷</el-button>
 *   <el-button v-permission="['bug:edit', 'bug:delete']">操作</el-button>   // 任一权限
 *   <el-button v-permission.all="['bug:edit', 'bug:delete']">操作</el-button> // 全部权限
 *   <el-button v-permission.module="'module:bug'">缺陷模块</el-button>     // 大功能模块
 *
 * 修饰符：
 *   .all   - 需要全部权限才显示
 *   .module- 传入大功能模块编码（如 module:bug）
 *
 * 行为：
 *   - 没有权限时从 DOM 中隐藏该元素（display:none）
 *   - 超级管理员 / 系统管理员始终通过
 *   - 限制权限 (denied) 优先
 *   - 支持 Vue 响应式：currentUser 变化时自动重算
 */
import { useUserStore } from '@/stores/user'

function evaluate(userStore, value, needAll, isModule) {
  if (!value) return true
  const codes = Array.isArray(value) ? value : [value]
  if (isModule) {
    if (needAll) {
      return codes.every(c => userStore.canAccessModule(c))
    }
    return codes.some(c => userStore.canAccessModule(c))
  }
  if (needAll) {
    return codes.every(c => userStore.hasPermission(c))
  }
  return codes.some(c => userStore.hasPermission(c))
}

export default {
  install(app) {
    app.directive('permission', {
      mounted(el, binding) {
        applyPermission(el, binding)
      },
      updated(el, binding) {
        // 仅在绑定值发生变化时重算
        if (binding.value !== binding.oldValue || binding.modifiers.all !== (binding.oldModifiers && binding.oldModifiers.all)) {
          applyPermission(el, binding)
        }
      }
    })
  }
}

function applyPermission(el, binding) {
  const userStore = useUserStore()
  const needAll = !!binding.modifiers.all
  const isModule = !!binding.modifiers.module
  const allowed = evaluate(userStore, binding.value, needAll, isModule)
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
