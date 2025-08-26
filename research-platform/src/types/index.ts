// User and Authentication Types
export interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'user'
  groupId?: string
  createdAt: Date
  updatedAt: Date
}

export interface Group {
  id: string
  name: string
  description?: string
  createdAt: Date
}

// Core Content Types
export interface Idea {
  id: string
  ticker: string
  companyName: string
  positionType: 'LONG' | 'SHORT' | 'N/A'
  sector: string
  presentedPrice: number
  presentedMarketCap: number
  presentedDate: Date
  currentPrice: number
  currentMarketCap: number
  performancePercentage: number
  exchange: 'US' | 'Foreign'
  marketCapCategory: '< $5B USD' | '> $5B USD'
  formatType: 'FORMAL' | 'INFORMAL'
  hasComments: boolean
  authorName?: string
  authorEmail?: string
  content: string
  highlights?: string
  relatedCompanies: string[]
  createdAt: Date
  updatedAt: Date
}

export interface Research {
  id: string
  title: string
  type: 'REPLAY' | 'TEAM' | 'TAKEAWAY' | 'LIVE'
  relatedTickers: string[]
  sectors: string[]
  date: Date
  audioUrl?: string
  audioDuration?: number // in seconds
  content: string
  speakerName?: string
  speakerBio?: string
  speakerTitle?: string
  speakerCompany?: string
  whyCareSummary?: string
  relatedResearchIds: string[]
  createdAt: Date
  updatedAt: Date
}

export interface Event {
  id: string
  title: string
  description: string
  relatedTickers: string[]
  eventDate: Date
  durationMinutes: number
  dialInInfo?: string
  rsvpRequired: boolean
  maxAttendees?: number
  currentAttendees: number
  contactName?: string
  contactEmail?: string
  contactPhone?: string
  createdAt: Date
  updatedAt: Date
}

export interface EventRsvp {
  id: string
  eventId: string
  userId: string
  status: 'REGISTERED' | 'ATTENDED' | 'CANCELLED'
  createdAt: Date
}

export interface Comment {
  id: string
  contentType: 'IDEA' | 'RESEARCH'
  contentId: string
  userId: string
  user?: User // populated when fetched
  content: string
  parentCommentId?: string
  replies?: Comment[]
  createdAt: Date
  updatedAt: Date
}

// Filter and Search Types
export interface FilterOptions {
  // Common filters
  sectors?: string[]
  tickers?: string[]
  search?: string
  dateRange?: 'lt1yr' | 'gt1yr'
  page?: number
  limit?: number
  sortBy?: 'date' | 'performance' | 'alphabetical'
  
  // Ideas specific
  positionType?: ('LONG' | 'SHORT' | 'N/A')[]
  marketCap?: ('lt5b' | 'gt5b')[]
  exchange?: ('US' | 'Foreign')[]
  format?: ('FORMAL' | 'INFORMAL')[]
  hasComments?: boolean
  
  // Research specific
  type?: ('REPLAY' | 'TEAM' | 'TAKEAWAY' | 'LIVE')[]
}

export interface SearchResult<T> {
  data: T[]
  total: number
  page: number
  limit: number
  hasNextPage: boolean
  hasPrevPage: boolean
}

// API Response Types
export interface ApiResponse<T> {
  data: T
  success: boolean
  message?: string
}

export interface ApiError {
  success: false
  message: string
  code?: number
}

// UI Component Types
export interface TabItem {
  id: string
  label: string
  href: string
  icon?: React.ComponentType<{ className?: string }>
  count?: number
}

export interface FilterSection {
  id: string
  title: string
  options: FilterOption[]
  type: 'checkbox' | 'radio' | 'range'
}

export interface FilterOption {
  id: string
  label: string
  value: string
  count: number
  checked?: boolean
}

// Theme Types
export type Theme = 'light' | 'dark'

// Chart and Performance Types
export interface PerformanceData {
  percentage: number
  color: 'positive' | 'negative' | 'neutral'
  formatted: string
}

export interface PriceData {
  current: number
  presented: number
  currency: string
  marketCap: number
  marketCapFormatted: string
}

// Bulk Operations (for future API integration)
export interface BulkCreateIdea {
  ticker: string
  companyName: string
  positionType: 'LONG' | 'SHORT' | 'N/A'
  sector: string
  presentedPrice: number
  presentedMarketCap: number
  presentedDate: Date
  content: string
  highlights?: string
  authorName?: string
  authorEmail?: string
}

export interface BulkCreateResearch {
  title: string
  type: 'REPLAY' | 'TEAM' | 'TAKEAWAY'
  relatedTickers: string[]
  sectors: string[]
  date: Date
  content: string
  speakerName?: string
  audioUrl?: string
}

// Sector Constants (matching the screenshots)
export const SECTORS = [
  'CONSUMER',
  'CREDIT', 
  'ENERGY',
  'EVENT DRIVEN/SPECIAL SIT',
  'FINANCE/REAL ESTATE',
  'HARDWARE',
  'HEALTHCARE',
  'INDUSTRIAL/TRANSPORTATION',
  'MACRO',
  'SOFTWARE',
  'SPAC',
  'TMT',
  'UTILITIES'
] as const

export type Sector = typeof SECTORS[number]

// Position type constants
export const POSITION_TYPES = ['LONG', 'SHORT', 'N/A'] as const
export type PositionType = typeof POSITION_TYPES[number]

// Research type constants
export const RESEARCH_TYPES = ['REPLAY', 'TEAM', 'TAKEAWAY', 'LIVE'] as const
export type ResearchType = typeof RESEARCH_TYPES[number]