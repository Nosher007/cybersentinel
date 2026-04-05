export function AlertWindow({ threat, isAttackRunning, children }) {
  const isAlert = isAttackRunning || threat !== null

  return (
    <div
      className={`bg-[#0d1324] rounded-xl p-5 border-2 transition-all duration-500 flex flex-col max-h-[720px] ${
        isAlert
          ? 'border-red-500 shadow-[0_0_28px_rgba(239,68,68,0.2)]'
          : 'border-emerald-800'
      }`}
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-5 flex-shrink-0">
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
        <div className="space-y-4 overflow-y-auto flex-1">{children}</div>
      ) : (
        <div className="flex flex-col items-center justify-center flex-1 min-h-[280px] text-center">
          {/* Radar animation */}
          <div className="relative w-20 h-20 mb-5">
            <div className="absolute inset-0 rounded-full border-2 border-emerald-800/50" />
            <div className="absolute inset-2 rounded-full border border-emerald-700/40" />
            <div className="absolute inset-4 rounded-full border border-emerald-600/30" />
            {/* Sweep line */}
            <div className="absolute inset-0 rounded-full overflow-hidden radar-sweep origin-center">
              <div
                className="absolute top-1/2 left-1/2 w-1/2 h-px origin-left"
                style={{
                  background: 'linear-gradient(to right, transparent, #10b981)',
                  transform: 'translateY(-50%)',
                }}
              />
            </div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-2 h-2 rounded-full bg-emerald-400" />
            </div>
          </div>

          <p className="text-emerald-400 font-semibold mb-1">Monitoring Active</p>
          <p className="text-slate-500 text-sm max-w-xs">
            NovaPay infrastructure is healthy. Type an attack prompt below to begin a simulation.
          </p>
        </div>
      )}
    </div>
  )
}
