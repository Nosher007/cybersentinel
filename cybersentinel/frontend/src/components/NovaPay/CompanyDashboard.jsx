import { useState, useEffect } from 'react'

const HEALTHY_BASE = { txPerSec: 42, activeUsers: 1284, apiLatencyMs: 38, uptimePct: 99.97 }

function rand(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

const DEPARTMENTS = [
  { id: 'payments', label: 'Payments', icon: 'PAY' },
  { id: 'auth', label: 'Authentication', icon: 'AUTH' },
  { id: 'database', label: 'Database', icon: 'DB' },
  { id: 'api', label: 'API Layer', icon: 'API' },
  { id: 'network', label: 'Network / Firewall', icon: 'NET' },
]

export function CompanyDashboard({ departmentStatuses = {}, isAttackRunning = false, metrics = {} }) {
  const [idleMetrics, setIdleMetrics] = useState(HEALTHY_BASE)

  useEffect(() => {
    if (isAttackRunning) return
    const t = setInterval(() => {
      setIdleMetrics((prev) => ({
        txPerSec:     Math.max(28, prev.txPerSec     + rand(-3, 4)),
        activeUsers:  Math.max(1100, prev.activeUsers + rand(-8, 10)),
        apiLatencyMs: Math.max(22, prev.apiLatencyMs  + rand(-3, 4)),
        uptimePct:    99.97,
      }))
    }, 1200)
    return () => clearInterval(t)
  }, [isAttackRunning])

  const display = isAttackRunning ? metrics : idleMetrics
  const txPerSec    = display.txPerSec    ?? HEALTHY_BASE.txPerSec
  const activeUsers = display.activeUsers ?? HEALTHY_BASE.activeUsers
  const apiLatencyMs = display.apiLatencyMs ?? HEALTHY_BASE.apiLatencyMs
  const uptimePct   = display.uptimePct   ?? HEALTHY_BASE.uptimePct

  return (
    <div className="p-5 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-3 mb-5 flex-shrink-0">
        <div className={`w-2.5 h-2.5 rounded-full ${isAttackRunning ? 'bg-orange-400 animate-pulse' : 'bg-emerald-400 animate-pulse'}`} />
        <span className="text-white font-bold text-base tracking-wide">NovaPay Live</span>
        <span className="text-slate-500 text-sm ml-auto">
          {isAttackRunning ? 'Under Attack' : 'Healthy'}
        </span>
      </div>

      {/* Live metrics — 2x2 grid */}
      <div className="grid grid-cols-2 gap-3 mb-5 flex-shrink-0">
        <MetricTile label="TX/sec" value={txPerSec} color={txPerSec > 500 ? 'red' : 'cyan'} />
        <MetricTile label="Users" value={activeUsers} color={activeUsers < 500 ? 'red' : 'violet'} />
        <MetricTile label="Latency" value={`${apiLatencyMs}ms`} color={apiLatencyMs > 800 ? 'red' : 'emerald'} />
        <MetricTile label="Uptime" value={`${uptimePct}%`} color={uptimePct < 97 ? 'red' : 'emerald'} />
      </div>

      {/* Department health */}
      <div className="flex-1 overflow-y-auto panel-scroll space-y-2">
        {DEPARTMENTS.map((dept) => {
          const status = departmentStatuses[dept.id] || 'HEALTHY'
          return <DepartmentRow key={dept.id} dept={dept} status={status} />
        })}
      </div>
    </div>
  )
}

function MetricTile({ label, value, color }) {
  const colors = {
    cyan:    'text-cyan-400',
    violet:  'text-violet-400',
    amber:   'text-amber-400',
    emerald: 'text-emerald-400',
    red:     'text-red-400',
  }

  return (
    <div className="bg-white/[0.02] border border-white/[0.05] rounded-lg p-3">
      <div className="text-slate-500 text-xs uppercase tracking-wider mb-1">{label}</div>
      <div className={`text-xl font-mono font-bold transition-colors duration-500 ${colors[color]}`}>
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
    </div>
  )
}

function DepartmentRow({ dept, status }) {
  const statusConfig = {
    HEALTHY:  { dot: 'bg-emerald-400', text: 'text-emerald-400', label: 'OK' },
    WARNING:  { dot: 'bg-amber-400 animate-pulse', text: 'text-amber-400', label: 'WARN' },
    CRITICAL: { dot: 'bg-orange-500 animate-pulse', text: 'text-orange-500', label: 'CRIT' },
    BREACHED: { dot: 'bg-red-500 animate-pulse', text: 'text-red-500', label: 'BREACH' },
  }

  const cfg = statusConfig[status] || statusConfig.HEALTHY

  return (
    <div className="flex items-center justify-between px-3 py-2.5 rounded-lg bg-white/[0.02] border border-white/[0.04]">
      <div className="flex items-center gap-3">
        <span className="text-xs font-mono font-bold text-slate-500 w-8">{dept.icon}</span>
        <span className="text-slate-300 text-sm">{dept.label}</span>
      </div>
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${cfg.dot}`} />
        <span className={`text-xs font-mono font-bold ${cfg.text}`}>{cfg.label}</span>
      </div>
    </div>
  )
}
