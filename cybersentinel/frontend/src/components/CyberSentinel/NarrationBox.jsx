import { useState, useEffect } from 'react'
import { getNarrationFromLog, getNarrationFromThreat } from '../../utils/narratorEngine'

export function NarrationBox({ logs, threat, isAttackRunning }) {
  const [currentText, setCurrentText] = useState(null)
  const [visible, setVisible] = useState(false)

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

  useEffect(() => {
    if (threat) return
    if (!logs || logs.length === 0) return
    const latest = logs[logs.length - 1]
    const text = getNarrationFromLog(latest)
    if (text !== null && text !== undefined && text !== currentText) {
      setVisible(false)
      setTimeout(() => {
        setCurrentText(text)
        setVisible(true)
      }, 150)
    }
  }, [logs])

  useEffect(() => {
    if (isAttackRunning && !threat) {
      setVisible(true)
    }
  }, [isAttackRunning])

  useEffect(() => {
    if (!isAttackRunning && !threat) {
      setCurrentText(null)
      setVisible(false)
    }
  }, [isAttackRunning, threat])

  const isThreatNarration = !!threat

  if (!isAttackRunning && !threat) {
    return (
      <div className="bg-white/[0.02] border border-white/[0.04] rounded-lg p-3 flex items-center gap-3">
        <p className="text-slate-600 text-xs">
          All systems nominal. Waiting for simulation.
        </p>
      </div>
    )
  }

  return (
    <div className={`rounded-lg p-3 border-l-2 transition-all duration-300 ${
      isThreatNarration
        ? 'bg-red-950/20 border-l-red-500 border border-red-900/30'
        : 'bg-white/[0.02] border-l-amber-500 border border-white/[0.04]'
    }`}>
      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-600">
          {isThreatNarration ? 'AI Analysis' : "What's happening"}
        </span>
        {!isThreatNarration && (
          <span className="w-1 h-1 rounded-full bg-amber-400 animate-pulse" />
        )}
      </div>
      <p className={`text-xs leading-relaxed transition-all duration-300 ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-1'
      } ${isThreatNarration ? 'text-slate-300' : 'text-slate-500'}`}>
        {currentText || 'Monitoring...'}
      </p>
    </div>
  )
}
