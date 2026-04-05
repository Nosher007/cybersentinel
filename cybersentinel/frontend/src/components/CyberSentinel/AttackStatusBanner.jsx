import { useState, useEffect, useRef } from 'react'

function formatElapsed(seconds) {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0')
  const s = (seconds % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

export function AttackStatusBanner({ attackInfo, isAttackRunning }) {
  const [elapsed, setElapsed] = useState(0)
  const startRef = useRef(null)

  useEffect(() => {
    if (isAttackRunning) {
      startRef.current = Date.now()
      setElapsed(0)
      const t = setInterval(() => {
        setElapsed(Math.floor((Date.now() - startRef.current) / 1000))
      }, 1000)
      return () => clearInterval(t)
    }
  }, [isAttackRunning])

  if (!isAttackRunning || !attackInfo) return null

  const scenario = (attackInfo.scenario_id ?? '').replace(/_/g, ' ')
  const attackType = (attackInfo.attack_type ?? '').replace(/_/g, ' ')
  const target = attackInfo.target_service ?? ''
  const intensity = (attackInfo.intensity ?? '').toUpperCase()

  const intensityColor = {
    HIGH: 'text-red-400',
    MEDIUM: 'text-amber-400',
    LOW: 'text-yellow-400',
  }[intensity] ?? 'text-slate-400'

  return (
    <div className="mb-4 sm:mb-5 rounded-lg bg-red-950/40 border border-red-800/60 px-3 sm:px-5 py-3 flex items-center gap-3 sm:gap-6 flex-wrap">
      <div className="flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
        <span className="text-red-400 text-xs font-bold tracking-widest uppercase">Attack In Progress</span>
      </div>
      <div className="flex items-center gap-1 text-xs text-slate-400">
        <span className="text-slate-600">Scenario:</span>
        <span className="text-slate-300 font-semibold capitalize">{scenario}</span>
      </div>
      {attackType && (
        <div className="flex items-center gap-1 text-xs text-slate-400">
          <span className="text-slate-600">Type:</span>
          <span className="text-slate-300 capitalize">{attackType}</span>
        </div>
      )}
      {target && (
        <div className="flex items-center gap-1 text-xs text-slate-400">
          <span className="text-slate-600">Target:</span>
          <span className="text-slate-300 font-mono">{target}</span>
        </div>
      )}
      {intensity && (
        <div className="flex items-center gap-1 text-xs">
          <span className="text-slate-600">Intensity:</span>
          <span className={`font-bold ${intensityColor}`}>{intensity}</span>
        </div>
      )}
      <div className="ml-auto font-mono text-sm text-slate-400 tabular-nums">
        {formatElapsed(elapsed)}
      </div>
    </div>
  )
}
