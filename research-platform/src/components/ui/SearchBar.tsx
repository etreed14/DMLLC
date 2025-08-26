'use client'

import React, { useState } from 'react'
import { Search } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SearchBarProps {
  onTickerSearch?: (tickers: string) => void
  onKeywordSearch?: (keywords: string) => void
  className?: string
  showGlobalSearch?: boolean
}

export function SearchBar({ 
  onTickerSearch, 
  onKeywordSearch, 
  className,
  showGlobalSearch = false
}: SearchBarProps) {
  const [tickerValue, setTickerValue] = useState('')
  const [keywordValue, setKeywordValue] = useState('')

  const handleTickerChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setTickerValue(value)
    onTickerSearch?.(value)
  }

  const handleKeywordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setKeywordValue(value)
    onKeywordSearch?.(value)
  }

  if (showGlobalSearch) {
    return (
      <div className={cn("max-w-2xl mx-auto", className)}>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search tickers, keywords, companies..."
            className="w-full pl-10 pr-4 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent"
            onChange={(e) => {
              // Handle global search
              onKeywordSearch?.(e.target.value)
            }}
          />
        </div>
      </div>
    )
  }

  return (
    <div className={cn("space-y-3", className)}>
      {/* Ticker Search */}
      <div>
        <input
          type="text"
          placeholder="Ticker(s), comma separated"
          value={tickerValue}
          onChange={handleTickerChange}
          className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent"
        />
      </div>

      {/* Keyword Search */}
      <div className="flex">
        <input
          type="text"
          placeholder="Keyword(s), comma separated"
          value={keywordValue}
          onChange={handleKeywordChange}
          className="flex-1 px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-l text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent"
        />
        <button
          type="button"
          className="px-4 py-2 bg-brand-blue text-white text-sm font-medium rounded-r hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-brand-blue"
        >
          GO
        </button>
      </div>
    </div>
  )
}