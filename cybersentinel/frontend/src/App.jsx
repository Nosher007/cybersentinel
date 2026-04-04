import { useState, useEffect, useRef } from 'react'
import './index.css'
import { CompanyDashboard } from './components/NovaPay/CompanyDashboard'
import { PromptInput } from './components/AttackConsole/PromptInput'
import { AlertWindow } from './components/CyberSentinel/AlertWindow'
import { LogTerminal } from './components/CyberSentinel/LogTerminal'
import { ThreatCard } from './components/CyberSentinel/ThreatCard'
import { RemediationPanel } from './components/CyberSentinel/RemediationPanel'
import { useWebSocket } from './hooks/useWebSocket'
import { SCENARIO_DEPARTMENT_PHASES, PHASE_DELAY_MS } from './utils/threatColors'

const DEFAULT_DEPT_STATUSES = {
  payments: 'HEALTHY',
  auth: 'HEALTHY',
  database: 'HEALTHY',
  api: 'HEALTHY',
  network: 'HEALTHY',
}

function App() {
  const [isAttackRunning, setIsAttackRunning] = useState(false)
  const [attackInfo, setAttackInfo] = useState(null)
  const [departmentStatuses, setDepartmentStatuses] = useState(DEFAULT_DEPT_STATUSES)
  const phaseIntervalRef = useRef(null)

  const { logs, status, threat, remediation, pipelineError, isConnected, clearState } = useWebSocket()

  // When simulation_complete arrives, mark attack as done
  useEffect(() => {
    if (status === 'simulation_complete') {
      setIsAttackRunning(false)
    }
  }, [status])

  // Department escalation animation when attack starts
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
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-cyan-400 tracking-wide">CyberSentinel</h1>
            <p className="text-slate-500 text-sm">AI-powered threat detection — NovaPay environment</p>
          </div>
          <div className={`flex items-center gap-2 text-sm ${isConnected ? 'text-emerald-400' : 'text-slate-500'}`}>
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`} />
            {isConnected ? 'Connected' : 'Disconnected'}
          </div>
        </div>

        {/* Main layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CompanyDashboard
            isAttackRunning={isAttackRunning}
            attackInfo={attackInfo}
            departmentStatuses={departmentStatuses}
          />
          <AlertWindow threat={threat} isAttackRunning={isAttackRunning}>
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
