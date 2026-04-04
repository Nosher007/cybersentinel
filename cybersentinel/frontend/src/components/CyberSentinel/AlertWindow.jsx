export function AlertWindow({ threat, isAttackRunning, children }) {
  const isAlert = isAttackRunning || threat !== null

  return (
    <div
      className={`bg-[#0d1324] rounded-xl p-5 border-2 transition-all duration-500 ${
        isAlert
          ? 'border-red-500 shadow-[0_0_24px_rgba(239,68,68,0.25)]'
          : 'border-emerald-800'
      }`}
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <div className={`w-3 h-3 rounded-full ${isAlert ? 'bg-red-500 animate-pulse' : 'bg-emerald-400'}`} />
        <span className={`font-bold text-lg tracking-wide ${isAlert ? 'text-red-400' : 'text-emerald-400'}`}>
          CyberSentinel
        </span>
        <span className={`ml-auto text-xs font-mono font-semibold px-2 py-1 rounded ${
          isAlert
            ? 'bg-red-900/40 text-red-400 border border-red-700'
            : 'bg-emerald-900/40 text-emerald-400 border border-emerald-800'
        }`}>
          {isAlert ? 'THREAT DETECTED' : 'ALL SYSTEMS SECURE'}
        </span>
      </div>

      {/* Body */}
      {isAlert ? (
        <div className="space-y-4">{children}</div>
      ) : (
        <div className="flex flex-col items-center justify-center min-h-[300px] text-center">
          <div className="text-5xl mb-4">🛡️</div>
          <p className="text-emerald-400 font-semibold mb-1">Monitoring Active</p>
          <p className="text-slate-500 text-sm max-w-xs">
            NovaPay infrastructure is healthy. Type an attack prompt below to begin a simulation.
          </p>
        </div>
      )}
    </div>
  )
}
