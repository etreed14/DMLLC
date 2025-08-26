import { SearchBar } from '@/components/ui/SearchBar'
import { Calendar, Clock } from 'lucide-react'

export default function Dashboard() {
  return (
    <div className="bg-gray-50 dark:bg-gray-900 min-h-screen">
      {/* Search Section */}
      <div className="bg-background border-b border-gray-200 dark:border-gray-700 py-6">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <SearchBar showGlobalSearch={true} />
        </div>
      </div>

      {/* Three Column Layout */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column - Upcoming Events */}
          <div className="space-y-6">
            <h2 className="text-lg font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wide">
              Upcoming Events
            </h2>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-brand-blue text-lg font-medium mb-2">
                C-Stores & Summer Driving Demand
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                3382 JP, ATD CN, CASY, MUSA
              </p>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <div className="flex items-center space-x-1">
                  <Calendar className="w-4 h-4" />
                  <span>28 AUG, 2025</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Clock className="w-4 h-4" />
                  <span>10:00-11:00AM ET</span>
                </div>
              </div>
            </div>
          </div>

          {/* Middle Column - Recent Research */}
          <div className="space-y-6">
            <h2 className="text-lg font-semibold text-brand-purple uppercase tracking-wide">
              Recent Research
            </h2>
            
            <div className="space-y-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                <p className="text-sm text-gray-500 mb-2">08/26/2025</p>
                <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                  🎤 REPLAY: FERG Preparing for Rate Cuts
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  AOS, CARR, FBIN, FERG, HD, LOW, MAS, TT
                </p>
                <p className="text-xs text-gray-500">Consumer, Industrial/Transportation</p>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                <p className="text-sm text-gray-500 mb-2">08/22/2025</p>
                <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                  🎤 REPLAY: Cosmetics Supply Chain Dealing with Disruption
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  COTY, EL, ELF, MC FP, TGT, ULTA
                </p>
                <p className="text-xs text-gray-500">Consumer, Macro</p>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                <p className="text-sm text-gray-500 mb-2">08/22/2025</p>
                <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                  📋 TEAM: AI, Rovo and Outlook - Takeaways
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  NOW, TEAM
                </p>
                <p className="text-xs text-gray-500">TMT, Software</p>
              </div>
            </div>
          </div>

          {/* Right Column - Recent Ideas */}
          <div className="space-y-6">
            <h2 className="text-lg font-semibold text-brand-orange uppercase tracking-wide">
              Recent Ideas
            </h2>
            
            <div className="space-y-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="text-sm text-gray-500">08/18/2025</p>
                    <h3 className="font-semibold text-brand-orange text-lg">AC CN</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Air Canada Inc.</p>
                  </div>
                  <div className="text-right">
                    <span className="text-performance-positive text-sm font-medium">+0.05%</span>
                    <span className="ml-2 bg-brand-orange text-white text-xs px-2 py-1 rounded font-medium">L</span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 text-xs text-gray-500">
                  <div>
                    <span className="font-medium">PRESENTED:</span><br/>
                    Price: CA$19.66, CAP: $4.65B
                  </div>
                  <div>
                    <span className="font-medium">CURRENT:</span><br/>
                    Price: CA$19.67, CAP: $4.66B
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">Industrial/Transportation</p>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="text-sm text-gray-500">08/18/2025</p>
                    <h3 className="font-semibold text-brand-orange text-lg">ESAB</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">ESAB Corp</p>
                  </div>
                  <div className="text-right">
                    <span className="text-performance-positive text-sm font-medium">+3.30%</span>
                    <span className="ml-2 bg-brand-orange text-white text-xs px-2 py-1 rounded font-medium">L</span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 text-xs text-gray-500">
                  <div>
                    <span className="font-medium">PRESENTED:</span><br/>
                    Price: $111.68, CAP: $6.78B
                  </div>
                  <div>
                    <span className="font-medium">CURRENT:</span><br/>
                    Price: $115.36, CAP: $7.00B
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">Industrial/Transportation</p>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="text-sm text-gray-500">08/18/2025</p>
                    <h3 className="font-semibold text-brand-orange text-lg">FM CN</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">First Quantum Minerals Ltd.</p>
                  </div>
                  <div className="text-right">
                    <span className="text-performance-negative text-sm font-medium">-0.25%</span>
                    <span className="ml-2 bg-brand-orange text-white text-xs px-2 py-1 rounded font-medium">L</span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 text-xs text-gray-500">
                  <div>
                    <span className="font-medium">PRESENTED:</span><br/>
                    Price: CA$23.64, CAP: $15.65B
                  </div>
                  <div>
                    <span className="font-medium">CURRENT:</span><br/>
                    Price: CA$23.58, CAP: $15.61B
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">Industrial/Transportation</p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
