import { useState } from 'react'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? ''

const EXAMPLE_PROMPTS = [
  'Try to brute force the login system',
  'Flood the payment API with traffic',
  'Steal customer credit card data from the database',
  'Perform a SQL injection on the API',
  'Simulate an insider threat — off-hours admin access',
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
      setError('Could not reach the backend. Is it running on port 8000?')
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
    <div className="rounded-xl p-[1px] bg-gradient-to-r from-cyan-900/60 via-slate-800 to-violet-900/60">
      <div className="bg-[#0d1324] rounded-xl p-5">
        {/* Header */}
        <div className="flex items-center gap-2 mb-4">
          <span className="text-xs font-bold tracking-widest uppercase text-cyan-600">
            ⌨ Attack Console
          </span>
          {isAttackRunning && (
            <span className="ml-auto flex items-center gap-1.5 text-red-400 text-xs font-mono font-semibold">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
              SIMULATION RUNNING
            </span>
          )}
        </div>

        {/* Input row */}
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe an attack in plain English..."
            disabled={disabled}
            className="flex-1 bg-[#111827] border border-[#1e2d4a] rounded-lg px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          />
          {isAttackRunning ? (
            <button
              type="button"
              onClick={handleStop}
              className="px-6 py-3 rounded-lg bg-red-600 hover:bg-red-700 active:scale-95 text-white text-sm font-bold transition-all"
            >
              Stop Attack
            </button>
          ) : (
            <button
              type="submit"
              disabled={disabled || !prompt.trim()}
              className="px-6 py-3 rounded-lg bg-cyan-600 hover:bg-cyan-500 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-bold transition-all"
            >
              {isSubmitting ? 'Launching...' : 'Launch Attack'}
            </button>
          )}
        </form>

        {error && (
          <p className="mt-2 text-red-400 text-xs">{error}</p>
        )}

        {/* Example prompts */}
        {!isAttackRunning && (
          <div className="mt-4">
            <p className="text-slate-600 text-xs mb-2">Try an example:</p>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_PROMPTS.map((ex) => (
                <button
                  key={ex}
                  onClick={() => setPrompt(ex)}
                  disabled={disabled}
                  className="text-xs text-slate-500 hover:text-cyan-400 disabled:opacity-40 disabled:cursor-not-allowed transition-colors border border-[#1e2d4a] hover:border-cyan-800/60 rounded-full px-3 py-1"
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
