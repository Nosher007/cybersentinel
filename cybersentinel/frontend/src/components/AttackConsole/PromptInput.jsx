import { useState } from 'react'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? ''

const EXAMPLE_PROMPTS = [
  'Brute force the login',
  'Flood the API with traffic',
  'SQL injection on the database',
  'Steal customer credit cards',
  'Insider threat — off-hours admin',
]

export function PromptInput({ onAttackStart, onAttackStop, isAttackRunning }) {
  const [prompt, setPrompt] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!prompt.trim() || isSubmitting || isAttackRunning) return

    setIsSubmitting(true)
    setError(null)

    try {
      const res = await fetch(`${BACKEND_URL}/attack`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt.trim() }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        setError(data.detail || `Error ${res.status}`)
        return
      }

      const data = await res.json()
      onAttackStart?.(data)
      setPrompt('')
    } catch {
      setError('Backend not reachable — start the server on port 8000 first')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleStop = async () => {
    try {
      await fetch(`${BACKEND_URL}/stop`, { method: 'POST' })
    } catch {
      // best-effort
    }
    onAttackStop?.()
  }

  const disabled = isSubmitting || isAttackRunning

  return (
    <div>
      {/* Gemini-style pill input */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-center gap-3 bg-[#1a1a1a] border border-white/[0.08] rounded-2xl px-6 py-3.5 focus-within:border-cyan-500/40 transition-colors">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe your attack..."
            disabled={disabled}
            className="flex-1 bg-transparent text-sm text-slate-200 placeholder-slate-600 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed pl-1"
          />
          {isAttackRunning ? (
            <button
              type="button"
              onClick={handleStop}
              className="shrink-0 w-9 h-9 rounded-xl bg-red-600 hover:bg-red-500 active:scale-90 flex items-center justify-center transition-all"
              title="Stop Attack"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="currentColor">
                <rect x="6" y="6" width="12" height="12" rx="1" />
              </svg>
            </button>
          ) : (
            <button
              type="submit"
              disabled={disabled || !prompt.trim()}
              className="shrink-0 w-9 h-9 rounded-xl bg-cyan-600 hover:bg-cyan-500 active:scale-90 disabled:opacity-30 disabled:cursor-not-allowed flex items-center justify-center transition-all"
              title="Launch Attack"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
              </svg>
            </button>
          )}
        </div>
      </form>

      {error && (
        <p className="mt-2 text-red-400 text-xs text-center">{error}</p>
      )}

      {/* Quick-select chips */}
      {!isAttackRunning && (
        <div className="flex flex-wrap justify-center gap-2 mt-3">
          {EXAMPLE_PROMPTS.map((ex) => (
            <button
              key={ex}
              onClick={() => setPrompt(ex)}
              disabled={disabled}
              className="text-xs text-slate-500 hover:text-cyan-400 disabled:opacity-40 disabled:cursor-not-allowed transition-colors border border-white/[0.06] hover:border-cyan-800/60 bg-white/[0.02] rounded-full px-3 py-1.5"
            >
              {ex}
            </button>
          ))}
        </div>
      )}

      {isAttackRunning && (
        <div className="flex items-center justify-center gap-2 mt-2 text-red-400 text-xs font-mono">
          <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
          SIMULATION RUNNING
        </div>
      )}
    </div>
  )
}
