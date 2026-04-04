import { useState, useEffect } from 'react'

const DEPARTMENTS = [
  { id: 'payments', label: 'Payments', icon: '💳' },
  { id: 'auth', label: 'Authentication', icon: '🔐' },
  { id: 'database', label: 'Database', icon: '🗄️' },
  { id: 'api', label: 'API Layer', icon: '⚡' },
  { id: 'network', label: 'Network / Firewall', icon: '🛡️' },
]

function randomBetween(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

export function CompanyDashboard({ departmentStatuses = {} }) {
  const [metrics, setMetrics] = useState({
    txPerSec: 42,
    activeUsers: 1284,
    apiLatencyMs: 38,
    uptimePct: 99.97,
  })

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics((prev) => ({
        txPerSec: Math.max(30, prev.txPerSec + randomBetween(-3, 4)),
        activeUsers: Math.max(1000, prev.activeUsers + randomBetween(-8, 10)),
        apiLatencyMs: Math.max(18, prev.apiLatencyMs + randomBetween(-4, 5)),
        uptimePct: 99.97,
      }))
    }, 1200)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="bg-[#0d1324] border border-[#1e2d4a] rounded-xl p-5">
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        <span className="text-emerald-400 font-bold text-lg tracking-wide">NovaPay</span>
        <span className="text-slate-500 text-sm ml-auto">Live Operations</span>
      </div>

      {/* Live metrics */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        <MetricTile label="Transactions / sec" value={metrics.txPerSec} unit="tx/s" color="cyan" />
        <MetricTile label="Active Users" value={metrics.activeUsers.toLocaleString()} color="violet" />
        <MetricTile label="API Latency" value={metrics.apiLatencyMs} unit="ms" color="amber" />
        <MetricTile label="Uptime" value={metrics.uptimePct} unit="%" color="emerald" />
      </div>

      {/* Department health */}
      <div className="space-y-2">
        {DEPARTMENTS.map((dept) => {
          const status = departmentStatuses[dept.id] || 'HEALTHY'
          return <DepartmentRow key={dept.id} dept={dept} status={status} />
        })}
      </div>
    </div>
  )
}

function MetricTile({ label, value, unit = '', color }) {
  const colors = {
    cyan: 'text-cyan-400',
    violet: 'text-violet-400',
    amber: 'text-amber-400',
    emerald: 'text-emerald-400',
  }

  return (
    <div className="bg-[#111827] rounded-lg p-3 border border-[#1e2d4a]">
      <div className="text-slate-500 text-xs mb-1">{label}</div>
      <div className={`text-xl font-mono font-bold ${colors[color]}`}>
        {value}<span className="text-sm font-normal ml-1 text-slate-400">{unit}</span>
      </div>
    </div>
  )
}

function DepartmentRow({ dept, status }) {
  const statusConfig = {
    HEALTHY:  { dot: 'bg-emerald-400', text: 'text-emerald-400', label: 'HEALTHY' },
    WARNING:  { dot: 'bg-amber-400 animate-pulse', text: 'text-amber-400', label: 'WARNING' },
    CRITICAL: { dot: 'bg-orange-500 animate-pulse', text: 'text-orange-500', label: 'CRITICAL' },
    BREACHED: { dot: 'bg-red-500 animate-pulse', text: 'text-red-500', label: 'BREACHED' },
  }

  const cfg = statusConfig[status] || statusConfig.HEALTHY

  return (
    <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-[#111827] border border-[#1e2d4a]">
      <div className="flex items-center gap-2">
        <span className="text-base">{dept.icon}</span>
        <span className="text-slate-300 text-sm">{dept.label}</span>
      </div>
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${cfg.dot}`} />
        <span className={`text-xs font-mono font-semibold ${cfg.text}`}>{cfg.label}</span>
      </div>
    </div>
  )
}
