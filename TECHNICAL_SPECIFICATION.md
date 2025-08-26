# DeMatteo Research Clone - Technical Specification

## Project Overview
A modern recreation of the DeMatteo Research platform with identical UI/UX, built with extensible architecture for future AI integration and easy data ingestion.

## Architecture Goals
1. **Pixel-perfect recreation** of existing design and functionality
2. **Modern tech stack** with TypeScript and component-based architecture
3. **Cloud-ready** design for easy GCP migration
4. **API-first** approach for easy data ingestion
5. **AI-ready** data structure for future chatbot integration
6. **Dark/Light mode** support with theme system

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + HeadlessUI
- **State Management**: Zustand + React Query
- **Forms**: React Hook Form + Zod validation
- **Theme**: next-themes for dark/light mode

### Backend
- **API**: Next.js API Routes (initially) → Google Cloud Functions (later)
- **Database**: PostgreSQL (initially) → Google Cloud SQL (later)
- **File Storage**: Local/Vercel Blob (initially) → Google Cloud Storage (later)
- **Search**: PostgreSQL full-text (initially) → Google Cloud Search API (later)

### Deployment
- **Initial**: Vercel + Supabase
- **Migration Target**: Google Cloud Run + Cloud SQL + Cloud Storage

## Database Schema

### Core Tables

```sql
-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  role VARCHAR(50) DEFAULT 'user',
  group_id UUID REFERENCES groups(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Groups
CREATE TABLE groups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Ideas (Investment Ideas)
CREATE TABLE ideas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticker VARCHAR(10) NOT NULL,
  company_name VARCHAR(255) NOT NULL,
  position_type VARCHAR(10) CHECK (position_type IN ('LONG', 'SHORT', 'N/A')),
  sector VARCHAR(100) NOT NULL,
  presented_price DECIMAL(10,2),
  presented_market_cap DECIMAL(15,2),
  presented_date DATE NOT NULL,
  current_price DECIMAL(10,2),
  current_market_cap DECIMAL(15,2),
  performance_percentage DECIMAL(5,2),
  exchange VARCHAR(20) CHECK (exchange IN ('US', 'Foreign')),
  market_cap_category VARCHAR(20) CHECK (market_cap_category IN ('< $5B USD', '> $5B USD')),
  format_type VARCHAR(20) CHECK (format_type IN ('FORMAL', 'INFORMAL')),
  has_comments BOOLEAN DEFAULT FALSE,
  author_name VARCHAR(255),
  author_email VARCHAR(255),
  content TEXT NOT NULL,
  highlights TEXT,
  related_companies TEXT[], -- Array of related tickers
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Research (Conference Calls, Reports)
CREATE TABLE research (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(500) NOT NULL,
  type VARCHAR(50) CHECK (type IN ('REPLAY', 'TEAM', 'TAKEAWAY', 'LIVE')),
  related_tickers VARCHAR(10)[] NOT NULL, -- Array of tickers
  sectors VARCHAR(100)[] NOT NULL, -- Array of sectors
  date DATE NOT NULL,
  audio_url VARCHAR(500), -- For replay audio files
  audio_duration INTEGER, -- Duration in seconds
  content TEXT NOT NULL,
  speaker_name VARCHAR(255),
  speaker_bio TEXT,
  speaker_title VARCHAR(255),
  speaker_company VARCHAR(255),
  why_care_summary TEXT,
  related_research_ids UUID[], -- Array of related research IDs
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Events (Upcoming Events)
CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(500) NOT NULL,
  description TEXT NOT NULL,
  related_tickers VARCHAR(10)[] NOT NULL,
  event_date TIMESTAMP NOT NULL,
  duration_minutes INTEGER DEFAULT 60,
  dial_in_info TEXT,
  rsvp_required BOOLEAN DEFAULT TRUE,
  max_attendees INTEGER,
  current_attendees INTEGER DEFAULT 0,
  contact_name VARCHAR(255),
  contact_email VARCHAR(255),
  contact_phone VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Event RSVPs
CREATE TABLE event_rsvps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID REFERENCES events(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  status VARCHAR(20) CHECK (status IN ('REGISTERED', 'ATTENDED', 'CANCELLED')),
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(event_id, user_id)
);

-- Comments
CREATE TABLE comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content_type VARCHAR(20) CHECK (content_type IN ('IDEA', 'RESEARCH')),
  content_id UUID NOT NULL,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  parent_comment_id UUID REFERENCES comments(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Search optimization
CREATE INDEX idx_ideas_ticker ON ideas(ticker);
CREATE INDEX idx_ideas_sector ON ideas(sector);
CREATE INDEX idx_ideas_position_type ON ideas(position_type);
CREATE INDEX idx_ideas_presented_date ON ideas(presented_date DESC);
CREATE INDEX idx_research_date ON research(date DESC);
CREATE INDEX idx_research_tickers ON research USING GIN (related_tickers);
CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_full_text_search ON ideas USING GIN (to_tsvector('english', ticker || ' ' || company_name || ' ' || content));
```

## API Architecture

### REST Endpoints

```typescript
// Ideas endpoints
GET    /api/ideas                    // List ideas with filtering
GET    /api/ideas/[id]              // Get specific idea
POST   /api/ideas                   // Create new idea
PUT    /api/ideas/[id]              // Update idea
DELETE /api/ideas/[id]              // Delete idea

// Research endpoints  
GET    /api/research                // List research with filtering
GET    /api/research/[id]           // Get specific research
POST   /api/research                // Create new research
PUT    /api/research/[id]           // Update research
DELETE /api/research/[id]           // Delete research

// Events endpoints
GET    /api/events                  // List events
GET    /api/events/[id]             // Get specific event
POST   /api/events                  // Create new event
POST   /api/events/[id]/rsvp        // RSVP to event

// Search endpoints
GET    /api/search?q=query&type=all // Global search
GET    /api/search/tickers          // Ticker autocomplete

// Bulk data ingestion (for future AI/automation)
POST   /api/bulk/ideas              // Bulk create ideas
POST   /api/bulk/research           // Bulk create research
POST   /api/data-sync               // Sync from external sources
```

### Query Parameters for Filtering

```typescript
interface FilterParams {
  // Common filters
  sectors?: string[];           // ['CONSUMER', 'HEALTHCARE']
  tickers?: string[];          // ['AAPL', 'MSFT']
  search?: string;             // Keyword search
  dateRange?: 'lt1yr' | 'gt1yr';
  page?: number;
  limit?: number;
  sortBy?: 'date' | 'performance' | 'alphabetical';
  
  // Ideas specific
  positionType?: 'LONG' | 'SHORT' | 'N/A';
  marketCap?: 'lt5b' | 'gt5b';
  exchange?: 'US' | 'Foreign';
  format?: 'FORMAL' | 'INFORMAL';
  hasComments?: boolean;
  
  // Research specific
  type?: 'REPLAY' | 'TEAM' | 'TAKEAWAY';
}
```

## Component Architecture

### Core Components

```typescript
// Layout Components
- AppLayout (main shell with nav)
- Sidebar (filtering panel)
- NavigationTabs
- ThemeToggle

// Content Components
- IdeasGrid / IdeasCard
- ResearchGrid / ResearchCard  
- EventsGrid / EventsCard
- DetailView (for individual items)

// UI Components
- SearchBar
- FilterSection
- PerformanceBadge
- PositionBadge
- SectorTag
- PriceDisplay
- AudioPlayer
- RSVPButton

// Form Components
- IdeaForm
- ResearchForm
- EventForm
- CommentForm
```

## Styling System

### Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Brand colors matching screenshots
        brand: {
          orange: '#EA580C',    // Ideas, Long positions
          purple: '#6B46C1',    // Research section
          blue: '#0EA5E9',      // Dashboard, events
        },
        performance: {
          positive: '#10B981',   // Green for gains
          negative: '#EF4444',   // Red for losses
        },
        // Dark mode variants
        dark: {
          bg: '#1F2937',
          panel: '#374151',
          text: '#F9FAFB',
        }
      },
      spacing: {
        // Match exact spacing from screenshots
      },
      typography: {
        // Custom typography scales
      }
    }
  }
}
```

## Migration Strategy to Google Cloud

### Phase 1: Initial Development (Vercel + Supabase)
- Quick iteration and prototyping
- Easy deployment and testing
- Feature-complete MVP

### Phase 2: Cloud Migration
```bash
# Database migration
pg_dump supabase_db | psql google_cloud_sql_db

# File migration  
gsutil -m cp -r ./files gs://bucket-name/

# Environment variables update
# Update connection strings and API endpoints
```

### Phase 3: AI Integration Preparation
- Structured data export for AI training
- Vector database setup for semantic search
- API endpoints for chatbot integration

## Future AI Integration Points

### Data Structure for AI
```typescript
interface AIReadyData {
  content: string;           // Full text content
  metadata: {
    type: 'IDEA' | 'RESEARCH' | 'EVENT';
    tickers: string[];
    sector: string;
    date: string;
    performance?: number;
    author?: string;
  };
  embeddings?: number[];     // For semantic search
  relationships: string[];   // Related content IDs
}
```

### Chatbot Integration Points
- `/api/ai/query` - Natural language queries
- `/api/ai/similar` - Find similar content
- `/api/ai/insights` - Generate insights from data
- Real-time data ingestion webhooks

## Development Phases

1. **Setup & Infrastructure** (Week 1)
2. **Core UI Components** (Week 2)
3. **Ideas Section** (Week 3)
4. **Research Section** (Week 4)
5. **Dashboard & Events** (Week 5)
6. **Search & Filtering** (Week 6)
7. **User Management** (Week 7)
8. **Testing & Polish** (Week 8)

This specification provides a solid foundation for building an extensible, modern platform that matches the original design while being ready for future enhancements.