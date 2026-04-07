import { useEffect, useRef } from 'react'

const LOG_COLORS = [
  { pattern: /\b(FAILED|ERROR|CRITICAL|ALERT|BLOCKED|ATTACK|INJECT|DROP)\b/i, className: 'text-red-400' },
  { pattern: /\b(WARNING|WARN|SUSPICIOUS|UNUSUAL|ANOMALY)\b/i, className: 'text-amber-400' },
  { pattern: /\b(SUCCESS|OK|200|ACCEPTED|AUTHENTICATED|ALLOWED)\b/i, className: 'text-emerald-400' },
  { pattern: /\b(INFO|GET|POST|PUT|DELETE|REQUEST)\b/i, className: 'text-cyan-400' },
]

function colorClass(line) {
  for (const { pattern, className } of LOG_COLORS) {
    if (pattern.test(line)) return className
  }
  return 'text-slate-500'
}

export function LogTerminal({ logs }) {
  const containerRef = useRef(null)

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [logs])

  if (!logs || logs.length === 0) return null

  return (
    <div>
      <div className="text-[10px] text-slate-600 font-mono uppercase tracking-widest mb-1.5">Live Logs</div>
      <div
        ref={containerRef}
        className="bg-black/40 border border-white/[0.04] rounded-lg p-2.5 h-32 sm:h-40 overflow-y-auto panel-scroll font-mono text-[11px] leading-relaxed space-y-px"
      >
        {logs.map((line, i) => (
          <div key={i} className={`whitespace-pre-wrap break-all ${colorClass(line)}`}>
            {line}
          </div>
        ))}
      </div>
    </div>
  )
}
