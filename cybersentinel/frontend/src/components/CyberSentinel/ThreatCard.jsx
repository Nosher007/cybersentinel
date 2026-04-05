import { useState, useEffect, useRef } from 'react'

const SEVERITY_CONFIG = {
  CRITICAL: { bg: 'bg-red-900/40', border: 'border-red-600', text: 'text-red-400', badge: 'bg-red-600' },
  HIGH:     { bg: 'bg-orange-900/30', border: 'border-orange-600', text: 'text-orange-400', badge: 'bg-orange-600' },
  MEDIUM:   { bg: 'bg-amber-900/30', border: 'border-amber-600', text: 'text-amber-400', badge: 'bg-amber-600' },
  LOW:      { bg: 'bg-yellow-900/20', border: 'border-yellow-700', text: 'text-yellow-400', badge: 'bg-yellow-700' },
}

export function ThreatCard({ threat, attackStartTime, threatDetectedAt }) {
  const [visible, setVisible] = useState(false)
  const cardRef = useRef(null)

  useEffect(() => {
    const frame = requestAnimationFrame(() => setVisible(true))
    return () => cancelAnimationFrame(frame)
  }, [])

  useEffect(() => {
    if (cardRef.current) {
      cardRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [])

  if (!threat) return null

  const severity = threat.severity?.toUpperCase() || 'MEDIUM'
  const cfg = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.MEDIUM

  return (
    <div
      ref={cardRef}
      className={`transition-all duration-500 ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      } ${cfg.bg} border ${cfg.border} rounded-lg p-4`}
    >
      {/* Header row */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-slate-300 text-sm font-semibold">Threat Detected</span>
        <span className={`text-xs font-bold px-2 py-1 rounded text-white ${cfg.badge}`}>
          {severity}
        </span>
      </div>

      {/* Attack type + service */}
      <div className="grid grid-cols-2 gap-3 mb-3">
        <div>
          <div className="text-slate-500 text-xs mb-0.5">Attack Type</div>
          <div className={`text-sm font-mono font-semibold ${cfg.text}`}>
            {formatAttackType(threat.attack_type)}
          </div>
        </div>
        <div>
          <div className="text-slate-500 text-xs mb-0.5">Affected Service</div>
          <div className="text-sm font-mono text-slate-300">{threat.affected_service}</div>
        </div>
      </div>

      {/* Score bar */}
      <div className="mb-3">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-slate-500">Risk Score</span>
          <span className={`font-mono font-bold ${cfg.text}`}>{threat.score?.toFixed(1)}/10</span>
        </div>
        <div className="w-full bg-[#111827] rounded-full h-1.5">
          <div
            className={`h-1.5 rounded-full transition-all duration-700 ${cfg.badge}`}
            style={{ width: `${Math.min((threat.score / 10) * 100, 100)}%` }}
          />
        </div>
      </div>

      {/* Justification */}
      {threat.justification && (
        <div>
          <div className="text-slate-500 text-xs mb-1">Justification</div>
          <p className="text-slate-400 text-xs leading-relaxed">{threat.justification}</p>
        </div>
      )}

      {/* Blast radius */}
      {threat.blast_radius?.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1">
          <span className="text-slate-500 text-xs mr-1">Blast radius:</span>
          {threat.blast_radius.map((s) => (
            <span key={s} className="text-xs font-mono bg-[#111827] border border-[#1e2d4a] text-slate-400 px-1.5 py-0.5 rounded">
              {s}
            </span>
          ))}
        </div>
      )}

      {/* Detection timeline */}
      {attackStartTime && threatDetectedAt && (
        <div className="mt-3 pt-3 border-t border-white/5">
          <div className="text-slate-500 text-xs mb-2">Detection Timeline</div>
          <div className="flex items-center gap-1.5 text-xs font-mono">
            <span className="text-slate-500">Attack start</span>
            <div className="flex-1 flex items-center gap-0.5">
              <div className="h-px flex-1 bg-slate-700" />
              <span className={`${cfg.text} shrink-0`}>
                {((threatDetectedAt - attackStartTime) / 1000).toFixed(1)}s
              </span>
              <div className="h-px flex-1 bg-slate-700" />
            </div>
            <span className="text-emerald-400">AI detected</span>
          </div>
        </div>
      )}
    </div>
  )
}

function formatAttackType(raw) {
  if (!raw) return 'Unknown'
  return raw.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}
