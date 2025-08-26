'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, FileText, TrendingUp } from 'lucide-react'
import { cn } from '@/lib/utils'

interface NavTab {
  id: string
  label: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  color: 'blue' | 'purple' | 'orange'
}

const navigationTabs: NavTab[] = [
  {
    id: 'dashboard',
    label: 'DASHBOARD',
    href: '/',
    icon: Home,
    color: 'blue'
  },
  {
    id: 'research',
    label: 'RESEARCH',
    href: '/research',
    icon: FileText,
    color: 'purple'
  },
  {
    id: 'ideas',
    label: 'IDEAS',
    href: '/ideas',
    icon: TrendingUp,
    color: 'orange'
  }
]

export function NavigationTabs() {
  const pathname = usePathname()

  const getTabStyles = (tab: NavTab, isActive: boolean) => {
    const baseStyles = "flex items-center space-x-2 px-6 py-3 text-sm font-medium transition-colors duration-200"
    
    if (isActive) {
      const activeColors = {
        blue: "text-brand-blue border-b-2 border-brand-blue bg-blue-50 dark:bg-blue-950/20",
        purple: "text-brand-purple border-b-2 border-brand-purple bg-purple-50 dark:bg-purple-950/20",
        orange: "text-brand-orange border-b-2 border-brand-orange bg-orange-50 dark:bg-orange-950/20"
      }
      return cn(baseStyles, activeColors[tab.color])
    } else {
      return cn(
        baseStyles,
        "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 border-b-2 border-transparent"
      )
    }
  }

  return (
    <nav className="border-b border-gray-200 dark:border-gray-700 bg-background">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex space-x-8">
          {navigationTabs.map((tab) => {
            const isActive = pathname === tab.href || 
                           (tab.href !== '/' && pathname.startsWith(tab.href))
            
            return (
              <Link
                key={tab.id}
                href={tab.href}
                className={getTabStyles(tab, isActive)}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </Link>
            )
          })}
        </div>
      </div>
    </nav>
  )
}