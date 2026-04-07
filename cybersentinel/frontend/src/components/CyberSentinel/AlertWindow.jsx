export function AlertWindow({ threat, isAttackRunning, children }) {
  const isAlert = isAttackRunning || threat !== null

  return (
    <div className="p-4 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4 flex-shrink-0">
        <div className={`w-2 h-2 rounded-full ${isAlert ? 'bg-red-500 animate-pulse' : 'bg-emerald-400'}`} />
        <span className={`text-sm font-semibold tracking-wide ${isAlert ? 'text-red-400' : 'text-emerald-400'}`}>
          Threat Log
        </span>
        <span className={`ml-auto text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
          isAlert
            ? 'bg-red-900/40 text-red-400 border border-red-800/50'
            : 'bg-emerald-900/30 text-emerald-500 border border-emerald-800/40'
        }`}>
          {isAlert ? 'ACTIVE' : 'CLEAR'}
        </span>
      </div>

      {/* Body */}
      {isAlert ? (
        <div className="space-y-3 overflow-y-auto flex-1 panel-scroll">{children}</div>
      ) : (
        <div className="flex flex-col items-center justify-center flex-1 text-center">
          <div className="relative w-14 h-14 mb-4">
            <div className="absolute inset-0 rounded-full border border-emerald-800/40" />
            <div className="absolute inset-2 rounded-full border border-emerald-700/30" />
            <div className="absolute inset-4 rounded-full border border-emerald-600/20" />
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
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            </div>
          </div>
          <p className="text-emerald-500 text-xs font-medium mb-0.5">Monitoring</p>
          <p className="text-slate-600 text-xs max-w-[200px]">No threats detected</p>
        </div>
      )}
    </div>
  )
}
