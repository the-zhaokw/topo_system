import { ref, onMounted, onUnmounted, computed } from 'vue'

const MOBILE_BREAKPOINT = 768

export function useResponsive() {
  const isMobile = ref(false)
  const isMenuOpen = ref(false)

  const checkMobile = () => {
    isMobile.value = window.innerWidth < MOBILE_BREAKPOINT
  }

  const openMenu = () => {
    isMenuOpen.value = true
  }

  const closeMenu = () => {
    isMenuOpen.value = false
  }

  const toggleMenu = () => {
    isMenuOpen.value = !isMenuOpen.value
  }

  onMounted(() => {
    checkMobile()
    window.addEventListener('resize', checkMobile)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', checkMobile)
  })

  return {
    isMobile: computed(() => isMobile.value),
    isMobileRef: isMobile,
    isMenuOpen: computed(() => isMenuOpen.value),
    isMenuOpenRef: isMenuOpen,
    openMenu,
    closeMenu,
    toggleMenu
  }
}
