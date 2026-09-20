/**
 * 全局表格拖拽滚动插件
 * 功能：在任意 el-table 表格行上按住鼠标左键左右拖动，即可横向滚动查看更多列，
 *       无需把页面/滚动条拉到底部再拖动底部横向滚动条。
 * 实现：document 级事件委托，对页面上所有 Element Plus 表格自动生效；
 *       不影响按钮、链接、输入框、复选框等可交互元素；拖动后抑制误触发的行点击。
 */
export default {
  install() {
    if (typeof document === 'undefined') return

    // 拖动状态
    let drag = null
    // 拖动结束后短暂抑制 click（防止行点击/按钮误触）
    let suppressClick = false

    // 这些元素上不启动拖拽（保证正常点击交互）
    const INTERACTIVE_SELECTOR = [
      'button', 'a', 'input', 'textarea', 'select', 'label',
      '.el-button', '.el-checkbox', '.el-radio', '.el-switch',
      '.el-input', '.el-select', '.el-link', '.el-tag',
      '.el-tooltip__trigger', '[role="button"]'
    ].join(',')

    // 定位 Element Plus 表格体的横向滚动容器
    const findScrollWrap = (el) => {
      if (!el || !el.closest) return null
      return (
        el.closest('.el-table .el-table__body-wrapper .el-scrollbar__wrap') ||
        el.closest('.el-table .el-table__body-wrapper') ||
        null
      )
    }

    document.addEventListener('mousedown', (e) => {
      // 仅响应鼠标左键
      if (e.button !== 0) return
      // 交互元素上不拖拽
      if (e.target.closest && e.target.closest(INTERACTIVE_SELECTOR)) return
      const wrap = findScrollWrap(e.target)
      if (!wrap) return
      // 仅当表格确实存在横向溢出（列超出可视宽度）时才启用
      if (wrap.scrollWidth <= wrap.clientWidth + 2) return

      drag = {
        wrap,
        startX: e.pageX,
        startLeft: wrap.scrollLeft,
        moved: false
      }
      wrap.classList.add('is-table-dragging')
      // 阻止文本选中
      e.preventDefault()
    })

    document.addEventListener('mousemove', (e) => {
      if (!drag) return
      const dx = e.pageX - drag.startX
      if (Math.abs(dx) > 4) drag.moved = true
      // 向右拖（dx>0）内容右移 →  scrollLeft 减小
      drag.wrap.scrollLeft = drag.startLeft - dx
    })

    const endDrag = () => {
      if (!drag) return
      drag.wrap.classList.remove('is-table-dragging')
      if (drag.moved) {
        // click 事件在 mouseup 之后同步派发，setTimeout(0) 在其后复位
        suppressClick = true
        setTimeout(() => { suppressClick = false }, 0)
      }
      drag = null
    }

    document.addEventListener('mouseup', endDrag)
    document.addEventListener('mouseleave', endDrag)

    // 捕获阶段拦截拖拽后的误点击
    document.addEventListener('click', (e) => {
      if (suppressClick) {
        e.stopPropagation()
        e.preventDefault()
      }
    }, true)
  }
}
