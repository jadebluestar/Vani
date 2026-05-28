import React from 'react'
import { User, Bot } from 'lucide-react'

export default function MessageBubble({ role, content, timestamp }) {
  const isUser = role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex gap-3 max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser 
            ? 'bg-primary-100 dark:bg-primary-900' 
            : 'bg-gray-200 dark:bg-gray-700'
        }`}>
          {isUser ? (
            <User size={16} className="text-primary-600 dark:text-primary-400" />
          ) : (
            <Bot size={16} className="text-gray-600 dark:text-gray-400" />
          )}
        </div>
        <div>
          <div className={`rounded-2xl px-4 py-2 ${
            isUser 
              ? 'bg-primary-500 text-white' 
              : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
          }`}>
            <p className="text-sm whitespace-pre-wrap">{content}</p>
          </div>
          {timestamp && (
            <p className={`text-xs text-gray-500 dark:text-gray-400 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
              {new Date(timestamp).toLocaleTimeString()}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}