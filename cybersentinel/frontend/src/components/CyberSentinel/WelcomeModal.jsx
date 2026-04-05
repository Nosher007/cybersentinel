import { useEffect, useState } from 'react'

export function WelcomeModal({ onClose }) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    setTimeout(() => setVisible(true), 50)
  }, [])

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className={`bg-[#0d1324] border border-[#1e2d4a] rounded-xl p-6 max-w-md w-full mx-4
          shadow-[0_0_40px_rgba(6,182,212,0.1)] transition-all duration-300
          ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center gap-2 mb-4">
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <span className="text-white font-bold text-lg tracking-wide">CyberSentinel</span>
          <span className="ml-auto text-xs text-slate-500 font-mono">AI Threat Lab</span>
        </div>

        {/* Description */}
        <p className="text-slate-400 text-sm leading-relaxed mb-4">
          An interactive cybersecurity simulation powered by AI. Watch{' '}
          <span className="text-cyan-400">NovaPay</span> — a fictional fintech company —
          operate in real time, then launch an attack and see how the AI detects and responds.
        </p>

        {/* Steps */}
        <div className="space-y-2 mb-5">
          {[
            ['01', 'Watch NovaPay operate live — transactions, users, servers'],
            ['02', 'Type any attack prompt in plain English'],
            ['03', 'AI detects the threat and generates a remediation plan'],
          ].map(([num, text]) => (
            <div key={num} className="flex items-start gap-3">
              <span className="text-xs font-mono text-cyan-600 mt-0.5 shrink-0">{num}</span>
              <span className="text-slate-400 text-sm">{text}</span>
            </div>
          ))}
        </div>

        {/* Dismiss button */}
        <button
          onClick={onClose}
          className="w-full py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 active:scale-95
            text-white text-sm font-bold transition-all"
        >
          Launch Simulation
        </button>
      </div>
    </div>
  )
}
