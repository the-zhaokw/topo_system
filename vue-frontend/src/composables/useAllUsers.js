/**
 * 全量用户加载 composable
 * 用于下拉选择器、对话框等需要一次性拿到所有用户的场景
 * （主列表表格分页场景不要用这个，直接调 api.users.getList 传 page/per_page）
 *
 * 策略：
 *   后端 /api/users 默认 per_page=20，且按 id 倒序，不传分页参数时老员工会被截断
 *   这里先请求 per_page=500，若后端 total 仍大于实际条数，再按 total 补拉一次
 *   这样无论用户数怎么增长都不会被截断
 */
import { ref } from 'vue'
import { apiService } from '@/services/api'

export function useAllUsers() {
  const allUsers = ref([])
  const loading = ref(false)
  const loaded = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      let response = await apiService.users.getList({ per_page: 500 })
      let list = response.users || []

      if ((response.total || 0) > list.length) {
        response = await apiService.users.getList({ per_page: response.total })
        list = response.users || []
      }

      allUsers.value = list
      loaded.value = true
      return list
    } finally {
      loading.value = false
    }
  }

  function reset() {
    allUsers.value = []
    loaded.value = false
  }

  return { allUsers, loading, loaded, fetchAll, reset }
}
