import React, { useState } from 'react'
import { Chat } from '../types'
import { Plus, X, MessageSquare, Clock, Trash2 } from 'lucide-react'
import { ChatSkeleton } from './SkeletonLoader'

interface SidebarProps {
  chats: Chat[]
  currentChat: Chat | null
  onSelectChat: (chat: Chat) => void
  onNewChat: () => void
  onClose: () => void
  onDeleteChat: (chatId: number) => void
  loading?: boolean
}

const Sidebar: React.FC<SidebarProps> = ({
  chats,
  currentChat,
  onSelectChat,
  onNewChat,
  onClose,
  onDeleteChat,
  loading = false
}) => {
  const [deletingChatId, setDeletingChatId] = useState<number | null>(null)

  const handleDelete = async (e: React.MouseEvent, chatId: number) => {
    e.stopPropagation() // Prevent chat selection when clicking delete
    setDeletingChatId(chatId)
    
    try {
      const response = await fetch(`/api/v1/chats/${chatId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        onDeleteChat(chatId)
      } else {
        console.error('Failed to delete chat')
      }
    } catch (error) {
      console.error('Error deleting chat:', error)
    } finally {
      setDeletingChatId(null)
    }
  }
  return (
    <div className="w-80 bg-gray-800 border-r border-gray-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold">Conversations</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <button
          onClick={onNewChat}
          className="w-full btn-primary flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Chat
        </button>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto p-2">
        {loading ? (
          <div className="space-y-2">
            {[...Array(3)].map((_, i) => <ChatSkeleton key={i} />)}
          </div>
        ) : chats.length === 0 ? (
          <div className="text-center text-gray-400 text-sm mt-8">
            <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>No conversations yet</p>
          </div>
        ) : (
          <div className="space-y-2">
            {chats.map((chat) => (
              <div
                key={chat.id}
                className={`w-full rounded-lg transition-colors relative group ${
                  currentChat?.id === chat.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 hover:bg-gray-600 text-gray-100'
                }`}
              >
                <button
                  onClick={() => onSelectChat(chat)}
                  className="w-full text-left p-3 flex items-start gap-3"
                >
                  <MessageSquare className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm truncate">
                      {chat.title}
                    </div>
                    <div className="text-xs opacity-70 mt-1 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(chat.updated_at).toLocaleDateString()}
                    </div>
                  </div>
                </button>
                <button
                  onClick={(e) => handleDelete(e, chat.id)}
                  disabled={deletingChatId === chat.id}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-2 hover:bg-gray-600 rounded-lg transition-colors disabled:opacity-50 opacity-0 group-hover:opacity-100"
                  title="Delete chat"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-700">
        <div className="text-xs text-gray-400">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full" />
            <span>System Online</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
