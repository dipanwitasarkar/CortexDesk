import { useEffect, useCallback } from 'react'

export const useAccessibility = () => {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // Escape key to close modals
    if (event.key === 'Escape') {
      const activeModal = document.querySelector('[role="dialog"]')
      if (activeModal) {
        const closeButton = activeModal.querySelector('button[aria-label*="close"]') as HTMLElement
        closeButton?.click()
      }
    }

    // Tab navigation for modals
    if (event.key === 'Tab') {
      const activeModal = document.querySelector('[role="dialog"]')
      if (activeModal) {
        const focusableElements = activeModal.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
        const firstElement = focusableElements[0] as HTMLElement
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

        if (event.shiftKey && document.activeElement === firstElement) {
          event.preventDefault()
          lastElement?.focus()
        } else if (!event.shiftKey && document.activeElement === lastElement) {
          event.preventDefault()
          firstElement?.focus()
        }
      }
    }
  }, [])

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [handleKeyDown])

  const announceToScreenReader = useCallback((message: string) => {
    const announcement = document.createElement('div')
    announcement.setAttribute('role', 'status')
    announcement.setAttribute('aria-live', 'polite')
    announcement.setAttribute('aria-atomic', 'true')
    announcement.className = 'sr-only'
    announcement.textContent = message
    
    document.body.appendChild(announcement)
    
    setTimeout(() => {
      document.body.removeChild(announcement)
    }, 1000)
  }, [])

  const setFocus = useCallback((element: HTMLElement | null) => {
    element?.focus()
  }, [])

  const trapFocus = useCallback((element: HTMLElement) => {
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const firstElement = focusableElements[0] as HTMLElement
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

    firstElement?.focus()

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        if (e.shiftKey && document.activeElement === firstElement) {
          e.preventDefault()
          lastElement?.focus()
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          e.preventDefault()
          firstElement?.focus()
        }
      }
    }

    element.addEventListener('keydown', handleKeyDown)
    return () => element.removeEventListener('keydown', handleKeyDown)
  }, [])

  return {
    announceToScreenReader,
    setFocus,
    trapFocus
  }
}
