import { useEffect, useState } from 'react'

export function WelcomeModal({ onClose }) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    setTimeout(() => setVisible(true), 50)
  }, [])

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-md"
      onClick={onClose}
    >
      <div
        className={`glass-panel p-6 max-w-md w-full mx-4 shadow-[0_0_60px_rgba(6,182,212,0.06)] transition-all duration-300
          ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center gap-2 mb-5">
          <div className="w-2 h-2 rounded-full bg-cyan-400 subtle-glow" />
          <span className="text-white font-bold text-lg tracking-wide">
            Cyber<span className="text-cyan-400">Sentinel</span>
          </span>
        </div>

        {/* Description */}
        <p className="text-slate-400 text-sm leading-relaxed mb-5">
          An interactive cybersecurity simulation powered by AI. Watch{' '}
          <span className="text-cyan-400">NovaPay</span> — a fictional fintech company —
          operate in real time, then launch an attack and see how the AI detects and responds.
        </p>

        {/* Steps */}
        <div className="space-y-3 mb-6">
          {[
            ['01', 'Watch NovaPay operate live — transactions, users, servers'],
            ['02', 'Type any attack prompt in plain English'],
            ['03', 'AI detects the threat and generates a remediation plan'],
          ].map(([num, text]) => (
            <div key={num} className="flex items-start gap-3">
              <span className="text-[11px] font-mono text-cyan-600 mt-0.5 shrink-0">{num}</span>
              <span className="text-slate-400 text-sm">{text}</span>
            </div>
          ))}
        </div>

        {/* Dismiss */}
        <button
          onClick={onClose}
          className="w-full py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 active:scale-[0.98] text-white text-sm font-bold transition-all"
        >
          Enter Simulation
        </button>
      </div>
    </div>
  )
}
