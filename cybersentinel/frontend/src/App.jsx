import './index.css'
import { CompanyDashboard } from './components/NovaPay/CompanyDashboard'

function App() {
  return (
    <div className="min-h-screen bg-[#0a0e1a] text-slate-200 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-cyan-400 tracking-wide">CyberSentinel</h1>
            <p className="text-slate-500 text-sm">AI-powered threat detection — NovaPay environment</p>
          </div>
          <div className="flex items-center gap-2 text-emerald-400 text-sm">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            System Nominal
          </div>
        </div>

        {/* Main layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CompanyDashboard />
          {/* CyberSentinel panel — TICKET-035 */}
          <div className="bg-[#0d1324] border border-[#1e2d4a] rounded-xl p-5 flex items-center justify-center">
            <p className="text-slate-600 text-sm">CyberSentinel alert window — coming in TICKET-035</p>
          </div>
        </div>

        {/* Attack prompt — TICKET-034 */}
        <div className="mt-6 bg-[#0d1324] border border-[#1e2d4a] rounded-xl p-4 flex items-center justify-center">
          <p className="text-slate-600 text-sm">Attack prompt input — coming in TICKET-034</p>
        </div>
      </div>
    </div>
  )
}

export default App
