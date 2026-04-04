const DEPARTMENTS = [
  { id: 'payments', label: 'Payments', icon: '💳' },
  { id: 'auth', label: 'Authentication', icon: '🔐' },
  { id: 'database', label: 'Database', icon: '🗄️' },
  { id: 'api', label: 'API Layer', icon: '⚡' },
  { id: 'network', label: 'Network / Firewall', icon: '🛡️' },
]

export function CompanyDashboard({ departmentStatuses = {}, isAttackRunning = false, metrics = {} }) {
  const txPerSec = metrics.txPerSec ?? 42
  const activeUsers = metrics.activeUsers ?? 1284
  const apiLatencyMs = metrics.apiLatencyMs ?? 38
  const uptimePct = metrics.uptimePct ?? 99.97

  const isUnderAttack = isAttackRunning

  return (
    <div className={`bg-[#0d1324] rounded-xl p-5 border-2 transition-all duration-500 ${
      isUnderAttack ? 'border-orange-800 shadow-[0_0_20px_rgba(194,65,12,0.2)]' : 'border-[#1e2d4a]'
    }`}>
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <div className={`w-2 h-2 rounded-full ${isUnderAttack ? 'bg-orange-400 animate-pulse' : 'bg-emerald-400 animate-pulse'}`} />
        <span className="text-white font-bold text-lg tracking-wide">NovaPay</span>
        <span className="text-slate-500 text-sm ml-auto">
          {isUnderAttack ? 'Under Attack' : 'Live Operations'}
        </span>
      </div>

      {/* Live metrics */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        <MetricTile
          label="Transactions / sec"
          value={txPerSec.toLocaleString()}
          unit="tx/s"
          color={txPerSec > 500 ? 'red' : 'cyan'}
        />
        <MetricTile
          label="Active Users"
          value={activeUsers.toLocaleString()}
          color={activeUsers < 500 ? 'red' : activeUsers < 900 ? 'amber' : 'violet'}
        />
        <MetricTile
          label="API Latency"
          value={apiLatencyMs.toLocaleString()}
          unit="ms"
          color={apiLatencyMs > 800 ? 'red' : apiLatencyMs > 200 ? 'amber' : 'emerald'}
        />
        <MetricTile
          label="Uptime"
          value={uptimePct}
          unit="%"
          color={uptimePct < 97 ? 'red' : uptimePct < 99 ? 'amber' : 'emerald'}
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
