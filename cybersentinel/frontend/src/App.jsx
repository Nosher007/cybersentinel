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
  const attackStartTimeRef = useRef(null)
  const [threatDetectedAt, setThreatDetectedAt] = useState(null)
  const [departmentStatuses, setDepartmentStatuses] = useState(DEFAULT_DEPT_STATUSES)
  const phaseIntervalRef = useRef(null)
  // Track whether we've ever launched an attack this session
  const [hasAttacked, setHasAttacked] = useState(false)

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

  useEffect(() => {
    if (threat) setThreatDetectedAt(Date.now())
  }, [threat])

  const handleAttackStart = (data) => {
    clearState()
    setDepartmentStatuses(DEFAULT_DEPT_STATUSES)
    clearInterval(phaseIntervalRef.current)
    attackStartTimeRef.current = Date.now()
    setThreatDetectedAt(null)
    setAttackInfo(data)
    setIsAttackRunning(true)
    setHasAttacked(true)
  }

  const handleAttackStop = () => {
    clearInterval(phaseIntervalRef.current)
    setIsAttackRunning(false)
    setThreatDetectedAt(null)
    setDepartmentStatuses(DEFAULT_DEPT_STATUSES)
  }

  // Show panels when attack is running OR when we have results from a finished attack
  const showPanels = hasAttacked

  return (
    <div className="h-screen w-screen bg-[#050505] text-slate-200 flex flex-col overflow-hidden">

      {/* ── Header ──────────────────────────────────────────── */}
      <header className="flex items-center justify-between px-5 py-3 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-cyan-400 subtle-glow" />
          <h1 className="text-lg font-bold text-white tracking-wide">
            Cyber<span className="text-cyan-400">Sentinel</span>
          </h1>
        </div>
        <div className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded-full border ${
          isConnected
            ? 'text-emerald-400 border-emerald-900/60 bg-emerald-950/30'
            : 'text-slate-500 border-slate-800 bg-slate-900/30'
        }`}>
          <div className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </header>

      {/* ── Attack status banner (only when running) ──────── */}
      {isAttackRunning && (
        <div className="px-5 flex-shrink-0">
          <AttackStatusBanner attackInfo={attackInfo} isAttackRunning={isAttackRunning} />
        </div>
      )}

      {/* ── Main content area — flex-1 fills remaining space ─ */}
      <main className="flex-1 flex flex-col min-h-0 px-5 pb-4">

        {!showPanels ? (
          /* ── Idle state: Gemini-style centered greeting ───── */
          <div className="flex-1 flex flex-col items-center justify-center">
            <div className="text-center mb-10 slide-up">
              {/* Radar icon — centered in its own flex container */}
              <div className="flex justify-center mb-8">
                <svg
                  style={{ display: 'block' }}
                  width="128"
                  height="128"
                  viewBox="0 0 128 128"
                >
                  <circle cx="64" cy="64" r="62" fill="none" stroke="rgba(6,182,212,0.15)" strokeWidth="1" />
                  <circle cx="64" cy="64" r="46" fill="none" stroke="rgba(6,182,212,0.12)" strokeWidth="1" />
                  <circle cx="64" cy="64" r="30" fill="none" stroke="rgba(6,182,212,0.10)" strokeWidth="1" />
                  <circle cx="64" cy="64" r="14" fill="none" stroke="rgba(6,182,212,0.08)" strokeWidth="1" />
                  <line
                    className="radar-line"
                    x1="64" y1="64" x2="126" y2="64"
                    stroke="rgba(6,182,212,0.5)"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                  />
                  <circle cx="64" cy="64" r="3" fill="#06b6d4" />
                </svg>
              </div>

              <p className="text-cyan-400 text-sm font-medium mb-1">CyberSentinel AI</p>
              <h2 className="text-2xl sm:text-3xl font-semibold text-white mb-2">
                NovaPay is running normally
              </h2>
              <p className="text-slate-500 text-sm max-w-md mx-auto">
                All systems are healthy. Describe an attack below to begin a security simulation.
              </p>
            </div>

            {/* Input at center when idle */}
            <div className="w-full max-w-2xl">
              <PromptInput
                onAttackStart={handleAttackStart}
                onAttackStop={handleAttackStop}
                isAttackRunning={isAttackRunning}
              />
            </div>
          </div>
        ) : (
          /* ── Attack state: 3 floating panels + bottom input ── */
          <>
            {/* 3-panel grid — fills available space */}
            <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-4 min-h-0">

              {/* Panel 1: NovaPay Live */}
              <div className="glass-panel flex flex-col min-h-0 overflow-hidden lg:col-span-1">
                <CompanyDashboard
                  isAttackRunning={isAttackRunning}
                  departmentStatuses={departmentStatuses}
                  metrics={metrics}
                />
              </div>

              {/* Panel 2: Threat Log */}
              <div className={`flex flex-col min-h-0 overflow-hidden lg:col-span-1 ${
                isAttackRunning ? 'glass-panel-active' : 'glass-panel'
              }`}>
                <AlertWindow threat={threat} isAttackRunning={isAttackRunning}>
                  <NarrationBox logs={logs} threat={threat} isAttackRunning={isAttackRunning} />
                  <LogTerminal logs={logs} />
                  {pipelineError && (
                    <div className="bg-red-900/30 border border-red-700 rounded-lg p-3 text-red-400 text-xs font-mono">
                      Pipeline error: {pipelineError}
                    </div>
                  )}
                </AlertWindow>
              </div>

              {/* Panel 3: AI Response */}
              <div className="glass-panel flex flex-col min-h-0 overflow-hidden lg:col-span-1">
                <div className="p-4 flex flex-col h-full">
                  <div className="flex items-center gap-2 mb-4 flex-shrink-0">
                    <div className={`w-2 h-2 rounded-full ${threat ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`} />
                    <span className="text-sm font-semibold text-slate-300">AI Response</span>
                  </div>
                  <div className="flex-1 overflow-y-auto panel-scroll space-y-4">
                    {threat && (
                      <ThreatCard
                        threat={threat}
                        attackStartTime={attackStartTimeRef.current}
                        threatDetectedAt={threatDetectedAt}
                      />
                    )}
                    {remediation && <RemediationPanel remediation={remediation} />}
                    {!threat && !remediation && (
                      <div className="flex-1 flex flex-col items-center justify-center text-center">
                        <div className="flex justify-center mb-3">
                          <svg
                            style={{ display: 'block' }}
                            xmlns="http://www.w3.org/2000/svg"
                            width="40"
                            height="40"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth={1.5}
                            className="text-slate-700"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 0 1-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 0 1 4.5 0m0 0v5.714a2.25 2.25 0 0 0 .659 1.591L19 14.5M14.25 3.104c.251.023.501.05.75.082M19 14.5l-2.47 2.47a2.25 2.25 0 0 1-1.591.659H9.061a2.25 2.25 0 0 1-1.591-.659L5 14.5m14 0V17a2.25 2.25 0 0 1-2.25 2.25H7.25A2.25 2.25 0 0 1 5 17v-2.5" />
                          </svg>
                        </div>
                        <p className="text-slate-500 text-sm">Waiting for AI analysis...</p>
                        <p className="text-slate-600 text-xs mt-1">Threat detection and remediation will appear here</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Input bar — fixed at bottom of panel view */}
            <div className="flex-shrink-0 mt-4 max-w-3xl mx-auto w-full">
              <PromptInput
                onAttackStart={handleAttackStart}
                onAttackStop={handleAttackStop}
                isAttackRunning={isAttackRunning}
              />
            </div>
          </>
        )}
      </main>

      {showWelcome && <WelcomeModal onClose={() => setShowWelcome(false)} />}
    </div>
  )
}

export default App
