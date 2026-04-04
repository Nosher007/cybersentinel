import { useState, useEffect } from 'react'

const DEPARTMENTS = [
  { id: 'payments', label: 'Payments', icon: '💳' },
  { id: 'auth', label: 'Authentication', icon: '🔐' },
  { id: 'database', label: 'Database', icon: '🗄️' },
  { id: 'api', label: 'API Layer', icon: '⚡' },
  { id: 'network', label: 'Network / Firewall', icon: '🛡️' },
]

// How each scenario affects metrics at peak attack
const ATTACK_PROFILES = {
  ddos_attack:        { txSpike: 8000,  userSpike: 0,    latencySpike: 4200, uptimeDrop: 94.1 },
  account_takeover:   { txSpike: 0,     userSpike: 400,  latencySpike: 380,  uptimeDrop: 99.1 },
  transaction_fraud:  { txSpike: 180,   userSpike: 0,    latencySpike: 210,  uptimeDrop: 98.4 },
  sql_injection:      { txSpike: 0,     userSpike: 0,    latencySpike: 890,  uptimeDrop: 97.2 },
  insider_threat:     { txSpike: 0,     userSpike: 0,    latencySpike: 95,   uptimeDrop: 99.5 },
}

const HEALTHY_METRICS = { txPerSec: 42, activeUsers: 1284, apiLatencyMs: 38, uptimePct: 99.97 }

function randomBetween(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

function lerp(a, b, t) {
  return a + (b - a) * t
}

export function CompanyDashboard({ departmentStatuses = {}, isAttackRunning = false, attackInfo = null }) {
  const [metrics, setMetrics] = useState(HEALTHY_METRICS)
  const [attackProgress, setAttackProgress] = useState(0) // 0 → 1 ramp over time

  // Ramp attack intensity up when running, back to 0 when stopped
  useEffect(() => {
    if (!isAttackRunning) {
      // Gradually recover back to healthy
      const recovery = setInterval(() => {
        setAttackProgress((prev) => {
          if (prev <= 0) { clearInterval(recovery); return 0 }
          return Math.max(0, prev - 0.05)
        })
      }, 300)
      return () => clearInterval(recovery)
    }

    // Ramp up during attack
    const ramp = setInterval(() => {
      setAttackProgress((prev) => Math.min(1, prev + 0.04))
    }, 500)
    return () => clearInterval(ramp)
  }, [isAttackRunning])

  // Tick metrics — blend between healthy and attack profile based on progress
  useEffect(() => {
    const interval = setInterval(() => {
      const profile = attackInfo?.scenario_id
        ? ATTACK_PROFILES[attackInfo.scenario_id]
        : null

      if (!profile || attackProgress === 0) {
        // Healthy idle drift
        setMetrics((prev) => ({
          txPerSec: Math.max(30, prev.txPerSec + randomBetween(-3, 4)),
          activeUsers: Math.max(1000, prev.activeUsers + randomBetween(-8, 10)),
          apiLatencyMs: Math.max(18, prev.apiLatencyMs + randomBetween(-4, 5)),
          uptimePct: 99.97,
        }))
        return
      }

      const jitter = () => randomBetween(-5, 5)

      setMetrics({
        txPerSec: Math.round(
          lerp(HEALTHY_METRICS.txPerSec, profile.txSpike || HEALTHY_METRICS.txPerSec, attackProgress)
          + jitter()
        ),
        activeUsers: Math.round(
          lerp(HEALTHY_METRICS.activeUsers, HEALTHY_METRICS.activeUsers + (profile.userSpike || 0), attackProgress)
          + jitter()
        ),
        apiLatencyMs: Math.round(
          lerp(HEALTHY_METRICS.apiLatencyMs, profile.latencySpike, attackProgress)
          + jitter()
        ),
        uptimePct: parseFloat(
          lerp(99.97, profile.uptimeDrop, attackProgress).toFixed(2)
        ),
      })
    }, 800)

    return () => clearInterval(interval)
  }, [attackProgress, attackInfo])

  const isUnderAttack = isAttackRunning || attackProgress > 0.1

  return (
    <div className={`bg-[#0d1324] rounded-xl p-5 border-2 transition-all duration-500 ${
      isUnderAttack ? 'border-orange-800' : 'border-[#1e2d4a]'
    }`}>
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <div className={`w-2 h-2 rounded-full ${isUnderAttack ? 'bg-orange-400 animate-pulse' : 'bg-emerald-400 animate-pulse'}`} />
        <span className={`font-bold text-lg tracking-wide ${isUnderAttack ? 'text-orange-400' : 'text-emerald-400'}`}>
          NovaPay
        </span>
        <span className="text-slate-500 text-sm ml-auto">
          {isUnderAttack ? 'Under Attack' : 'Live Operations'}
        </span>
      </div>

      {/* Live metrics */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        <MetricTile
          label="Transactions / sec"
          value={metrics.txPerSec.toLocaleString()}
          unit="tx/s"
          color={metrics.txPerSec > 500 ? 'red' : 'cyan'}
        />
        <MetricTile
          label="Active Users"
          value={metrics.activeUsers.toLocaleString()}
          color="violet"
        />
        <MetricTile
          label="API Latency"
          value={metrics.apiLatencyMs.toLocaleString()}
          unit="ms"
          color={metrics.apiLatencyMs > 200 ? 'red' : metrics.apiLatencyMs > 100 ? 'amber' : 'emerald'}
        />
        <MetricTile
          label="Uptime"
          value={metrics.uptimePct}
          unit="%"
          color={metrics.uptimePct < 97 ? 'red' : metrics.uptimePct < 99 ? 'amber' : 'emerald'}
        />
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
    cyan:    'text-cyan-400',
    violet:  'text-violet-400',
    amber:   'text-amber-400',
    emerald: 'text-emerald-400',
    red:     'text-red-400',
  }

  return (
    <div className="bg-[#111827] rounded-lg p-3 border border-[#1e2d4a]">
      <div className="text-slate-500 text-xs mb-1">{label}</div>
      <div className={`text-xl font-mono font-bold transition-colors duration-500 ${colors[color]}`}>
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
