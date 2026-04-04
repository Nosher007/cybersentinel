import { useState } from 'react'

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
      const res = await fetch('/attack', {
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
    } catch (err) {
      setError('Could not reach the backend. Is it running?')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleStop = async () => {
    try {
      await fetch('/stop', { method: 'POST' })
    } catch {
      // best-effort
    }
    onAttackStop?.()
  }

  const disabled = isSubmitting || isAttackRunning

  return (
    <div className="bg-[#0d1324] border border-[#1e2d4a] rounded-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-slate-400 text-sm font-semibold tracking-wide uppercase">Attack Console</span>
        {isAttackRunning && (
          <span className="ml-auto flex items-center gap-1.5 text-red-400 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            ATTACK IN PROGRESS
          </span>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe an attack in plain English..."
          disabled={disabled}
          className="flex-1 bg-[#111827] border border-[#1e2d4a] rounded-lg px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        />
        {isAttackRunning ? (
          <button
            type="button"
            onClick={handleStop}
            className="px-5 py-3 rounded-lg bg-red-600 hover:bg-red-700 text-white text-sm font-semibold transition-colors"
          >
            Stop
          </button>
        ) : (
          <button
            type="submit"
            disabled={disabled || !prompt.trim()}
            className="px-5 py-3 rounded-lg bg-cyan-600 hover:bg-cyan-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-semibold transition-colors"
          >
            {isSubmitting ? 'Launching...' : 'Launch'}
          </button>
        )}
      </form>

      {error && (
        <p className="mt-2 text-red-400 text-xs">{error}</p>
      )}

      {/* Example prompts */}
      {!isAttackRunning && (
        <div className="mt-3 flex flex-wrap gap-2">
          {EXAMPLE_PROMPTS.map((ex) => (
            <button
              key={ex}
              onClick={() => setPrompt(ex)}
              disabled={disabled}
              className="text-xs text-slate-500 hover:text-cyan-400 disabled:opacity-40 disabled:cursor-not-allowed transition-colors border border-[#1e2d4a] rounded px-2 py-1 hover:border-cyan-800"
            >
              {ex}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
