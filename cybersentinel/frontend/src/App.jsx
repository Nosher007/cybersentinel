import { useState, useEffect, useRef } from 'react'
import './index.css'
import { CompanyDashboard } from './components/NovaPay/CompanyDashboard'
import { PromptInput } from './components/AttackConsole/PromptInput'
import { AlertWindow } from './components/CyberSentinel/AlertWindow'
import { AttackStatusBanner } from './components/CyberSentinel/AttackStatusBanner'
import { LogTerminal } from './components/CyberSentinel/LogTerminal'
import { NarrationBox } from './components/CyberSentinel/NarrationBox'
import { ThreatCard } from './components/CyberSentinel/ThreatCard'
import { RemediationPanel } from './components/CyberSentinel/RemediationPanel'
import { useWebSocket } from './hooks/useWebSocket'
import { WelcomeModal } from './components/CyberSentinel/WelcomeModal'
import { SCENARIO_DEPARTMENT_PHASES, PHASE_DELAY_MS } from './utils/threatColors'

const DEFAULT_DEPT_STATUSES = {
  payments: 'HEALTHY',
  auth: 'HEALTHY',
  database: 'HEALTHY',
  api: 'HEALTHY',
  network: 'HEALTHY',
}

function App() {
  const [showWelcome, setShowWelcome] = useState(true)
  const [isAttackRunning, setIsAttackRunning] = useState(false)
  const [attackInfo, setAttackInfo] = useState(null)
  const [departmentStatuses, setDepartmentStatuses] = useState(DEFAULT_DEPT_STATUSES)
  const phaseIntervalRef = useRef(null)

  const { logs, status, threat, remediation, pipelineError, isConnected, metrics, clearState } = useWebSocket()

  useEffect(() => {
    if (status === 'simulation_complete') {
      setIsAttackRunning(false)
    }
  }, [status])

  useEffect(() => {
    if (!attackInfo?.scenario_id) return
    const phases = SCENARIO_DEPARTMENT_PHASES[attackInfo.scenario_id]
    if (!phases) return

    let phaseIndex = 0
    phaseIntervalRef.current = setInterval(() => {
      if (phaseIndex >= phases.length) {
        clearInterval(phaseIntervalRef.current)
        return
      }
      setDepartmentStatuses((prev) => ({ ...prev, ...phases[phaseIndex] }))
      phaseIndex++
    }, PHASE_DELAY_MS)

    return () => clearInterval(phaseIntervalRef.current)
  }, [attackInfo])

  const handleAttackStart = (data) => {
    clearState()
    setDepartmentStatuses(DEFAULT_DEPT_STATUSES)
    clearInterval(phaseIntervalRef.current)
    setAttackInfo(data)
    setIsAttackRunning(true)
  }

  const handleAttackStop = () => {
    clearInterval(phaseIntervalRef.current)
    setIsAttackRunning(false)
    setDepartmentStatuses(DEFAULT_DEPT_STATUSES)
  }

  return (
    <div className="min-h-screen bg-[#0a0e1a] text-slate-200 p-6">
      <div className="max-w-7xl mx-auto">

        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-wide">
              Cyber<span className="text-cyan-400">Sentinel</span>
            </h1>
            <p className="text-slate-500 text-xs mt-0.5">AI-powered threat detection · NovaPay environment</p>
          </div>
          <div className={`flex items-center gap-2 text-sm px-3 py-1.5 rounded-full border ${
            isConnected
              ? 'text-emerald-400 border-emerald-900/60 bg-emerald-950/30'
              : 'text-slate-500 border-slate-800 bg-slate-900/30'
          }`}>
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`} />
            {isConnected ? 'Connected' : 'Disconnected'}
          </div>
        </div>

        {/* Attack status banner */}
        <AttackStatusBanner attackInfo={attackInfo} isAttackRunning={isAttackRunning} />

        {/* Main layout — asymmetric: NovaPay sidebar (1/3) + CyberSentinel panel (2/3) */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="lg:col-span-1">
            <CompanyDashboard
              isAttackRunning={isAttackRunning}
              departmentStatuses={departmentStatuses}
              metrics={metrics}
            />
          </div>

          <div className="lg:col-span-2">
            <AlertWindow threat={threat} isAttackRunning={isAttackRunning}>
              <NarrationBox logs={logs} threat={threat} isAttackRunning={isAttackRunning} />
              <LogTerminal logs={logs} />
              {threat && <ThreatCard threat={threat} />}
              {remediation && <RemediationPanel remediation={remediation} />}
              {pipelineError && (
                <div className="bg-red-900/30 border border-red-700 rounded-lg p-3 text-red-400 text-xs font-mono">
                  Pipeline error: {pipelineError}
                </div>
              )}
            </AlertWindow>
          </div>
        </div>

        {/* Attack console */}
        <div className="mt-5">
          <PromptInput
            onAttackStart={handleAttackStart}
            onAttackStop={handleAttackStop}
            isAttackRunning={isAttackRunning}
          />
        </div>

      </div>

      {showWelcome && <WelcomeModal onClose={() => setShowWelcome(false)} />}
    </div>
  )
}

export default App
