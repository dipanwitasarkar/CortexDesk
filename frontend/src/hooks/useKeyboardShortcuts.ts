import { useEffect } from 'react'

interface ShortcutConfig {
  key: string
  ctrlKey?: boolean
  shiftKey?: boolean
  altKey?: boolean
  metaKey?: boolean
  handler: () => void
  description: string
}

export const useKeyboardShortcuts = (shortcuts: ShortcutConfig[]) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      for (const shortcut of shortcuts) {
        const keyMatch = e.key.toLowerCase() === shortcut.key.toLowerCase()
        const ctrlMatch = shortcut.ctrlKey ? e.ctrlKey || e.metaKey : !e.ctrlKey && !e.metaKey
        const shiftMatch = shortcut.shiftKey ? e.shiftKey : !e.shiftKey
        const altMatch = shortcut.altKey ? e.altKey : !e.altKey
        const metaMatch = shortcut.metaKey ? e.metaKey : !e.metaKey

        if (keyMatch && ctrlMatch && shiftMatch && altMatch && metaMatch) {
          e.preventDefault()
          shortcut.handler()
          break
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [shortcuts])
}

export const defaultShortcuts = [
  {
    key: 'n',
    ctrlKey: true,
    handler: () => console.log('New Chat'),
    description: 'New Chat'
  },
  {
    key: 'k',
    ctrlKey: true,
    handler: () => console.log('Search'),
    description: 'Search'
  },
  {
    key: 'd',
    ctrlKey: true,
    handler: () => console.log('Documents'),
    description: 'Open Documents'
  },
  {
    key: 'o',
    ctrlKey: true,
    handler: () => console.log('Observability'),
    description: 'Open Observability'
  },
  {
    key: 'm',
    ctrlKey: true,
    handler: () => console.log('MCP Manager'),
    description: 'Open MCP Manager'
  },
  {
    key: '?',
    handler: () => console.log('Show Shortcuts'),
    description: 'Show Keyboard Shortcuts'
  }
]
