import { useState, useEffect } from 'react'
import { getNarrationFromLog, getNarrationFromThreat } from '../../utils/narratorEngine'

export function NarrationBox({ logs, threat, isAttackRunning }) {
  const [currentText, setCurrentText] = useState(null)
  const [visible, setVisible] = useState(false)

  // After threat arrives, use the threat narration
  useEffect(() => {
    if (threat) {
      const text = getNarrationFromThreat(threat)
      if (text) {
        setVisible(false)
        setTimeout(() => {
          setCurrentText(text)
          setVisible(true)
        }, 150)
      }
    }
  }, [threat])

  // During simulation, update narration from the latest meaningful log
  useEffect(() => {
    if (threat) return  // threat narration takes over
    if (!logs || logs.length === 0) return
    const latest = logs[logs.length - 1]
    const text = getNarrationFromLog(latest)
    if (text && text !== currentText) {
      setVisible(false)
      setTimeout(() => {
        setCurrentText(text)
        setVisible(true)
      }, 150)
    }
  }, [logs])

  // Reset when attack stops
  useEffect(() => {
    if (!isAttackRunning && !threat) {
      setCurrentText(null)
      setVisible(false)
    }
  }, [isAttackRunning, threat])

  const isThreatNarration = !!threat

  if (!isAttackRunning && !threat) {
    return (
      <div className="bg-[#0d1a2e] border border-[#1e2d4a] rounded-lg p-4 flex items-center gap-3">
        <div className="text-2xl">🔍</div>
        <p className="text-slate-500 text-sm">
          All systems nominal. Type an attack prompt below to start a simulation.
        </p>
      </div>
    )
  }

  return (
    <div className={`rounded-lg p-4 border-l-4 transition-all duration-300 ${
      isThreatNarration
        ? 'bg-red-950/30 border-l-red-500 border border-red-900/40'
        : 'bg-[#0d1a2e] border-l-amber-500 border border-[#1e2d4a]'
    }`}>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xs font-semibold uppercase tracking-widest text-slate-500">
          {isThreatNarration ? 'AI Analysis' : "What's happening"}
        </span>
        {!isThreatNarration && (
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
        )}
      </div>
      <p className={`text-sm leading-relaxed transition-all duration-300 ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-1'
      } ${isThreatNarration ? 'text-slate-300' : 'text-slate-400'}`}>
        {currentText || 'Monitoring...'}
      </p>
    </div>
  )
}
