import { useState } from 'react'
import './index.css'
import { CompanyDashboard } from './components/NovaPay/CompanyDashboard'
import { PromptInput } from './components/AttackConsole/PromptInput'
import { useWebSocket } from './hooks/useWebSocket'

function App() {
  const [isAttackRunning, setIsAttackRunning] = useState(false)
  const [attackInfo, setAttackInfo] = useState(null)
  const { logs, status, threat, remediation, pipelineError, isConnected, clearState } = useWebSocket()

  const handleAttackStart = (data) => {
    clearState()
    setAttackInfo(data)
    setIsAttackRunning(true)
  }

  const handleAttackStop = () => {
    setIsAttackRunning(false)
  }

  // When simulation_complete arrives, mark attack as done
  if (status === 'simulation_complete' && isAttackRunning) {
    setIsAttackRunning(false)
  }

  return (
    <div className="min-h-screen bg-[#0a0e1a] text-slate-200 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-cyan-400 tracking-wide">CyberSentinel</h1>
            <p className="text-slate-500 text-sm">AI-powered threat detection — NovaPay environment</p>
          </div>
          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 text-sm ${isConnected ? 'text-emerald-400' : 'text-slate-500'}`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`} />
              {isConnected ? 'Connected' : 'Disconnected'}
            </div>
          </div>
        </div>

        {/* Main layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CompanyDashboard isAttackRunning={isAttackRunning} attackInfo={attackInfo} />
          {/* CyberSentinel panel — TICKET-035 */}
          <div className="bg-[#0d1324] border border-[#1e2d4a] rounded-xl p-5 flex items-center justify-center min-h-[400px]">
            <p className="text-slate-600 text-sm">CyberSentinel alert window — coming in TICKET-035</p>
          </div>
        </div>

        {/* Attack prompt */}
        <div className="mt-6">
          <PromptInput
            onAttackStart={handleAttackStart}
            onAttackStop={handleAttackStop}
            isAttackRunning={isAttackRunning}
          />
        </div>
      </div>
    </div>
  )
}

export default App
