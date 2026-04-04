import { useState, useEffect } from 'react'

const STEP_REVEAL_INTERVAL_MS = 600

export function RemediationPanel({ remediation }) {
  const [visibleCount, setVisibleCount] = useState(0)

  const allSteps = remediation
    ? [...(remediation.immediate_steps || []), ...(remediation.hardening_steps || [])]
    : []

  useEffect(() => {
    if (!remediation || allSteps.length === 0) return

    setVisibleCount(0)

    const interval = setInterval(() => {
      setVisibleCount((prev) => {
        if (prev >= allSteps.length) {
          clearInterval(interval)
          return prev
        }
        return prev + 1
      })
    }, STEP_REVEAL_INTERVAL_MS)

    return () => clearInterval(interval)
  }, [remediation])

  if (!remediation) return null

  const immediateSteps = remediation.immediate_steps || []
  const hardeningSteps = remediation.hardening_steps || []
  const cveRefs = remediation.cve_references || []

  let shownSoFar = 0

  return (
    <div className="bg-[#0d1a12] border border-emerald-900 rounded-lg p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-emerald-400 text-sm font-semibold">Remediation Plan</span>
        {remediation.plan_id && (
          <span className="text-slate-600 text-xs font-mono">{remediation.plan_id}</span>
        )}
      </div>

      {remediation.summary && (
        <p className="text-slate-400 text-xs mb-4 leading-relaxed">{remediation.summary}</p>
      )}

      {/* Immediate steps */}
      {immediateSteps.length > 0 && (
        <div className="mb-4">
          <div className="text-xs text-slate-500 uppercase tracking-widest mb-2">Immediate Actions</div>
          <div className="space-y-2">
            {immediateSteps.map((step, i) => {
              shownSoFar++
              const show = visibleCount >= shownSoFar
              return (
                <StepRow
                  key={`imm-${i}`}
                  step={step}
                  show={show}
                  color="emerald"
                />
              )
            })}
          </div>
        </div>
      )}

      {/* Hardening steps */}
      {hardeningSteps.length > 0 && (
        <div className="mb-4">
          <div className="text-xs text-slate-500 uppercase tracking-widest mb-2">Hardening Steps</div>
          <div className="space-y-2">
            {hardeningSteps.map((step, i) => {
              shownSoFar++
              const show = visibleCount >= shownSoFar
              return (
                <StepRow
                  key={`hard-${i}`}
                  step={step}
                  show={show}
                  color="cyan"
                />
              )
            })}
          </div>
        </div>
      )}

      {/* CVE references */}
      {cveRefs.length > 0 && visibleCount >= allSteps.length && (
        <div className="mt-3 pt-3 border-t border-emerald-900/50">
          <div className="text-xs text-slate-500 uppercase tracking-widest mb-2">CVE References</div>
          <div className="flex flex-wrap gap-2">
            {cveRefs.map((cve) => (
              <span
                key={cve}
                className="text-xs font-mono bg-[#111827] border border-[#1e2d4a] text-slate-400 px-2 py-0.5 rounded"
              >
                {cve}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function StepRow({ step, show, color }) {
  const colors = {
    emerald: 'bg-emerald-500',
    cyan: 'bg-cyan-500',
  }

  return (
    <div
      className={`transition-all duration-500 ${
        show ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-2'
      } flex gap-3 items-start`}
    >
      <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${colors[color]}`}>
        <span className="text-white text-xs font-bold">{step.order}</span>
      </div>
      <div>
        <div className="text-slate-300 text-xs font-semibold">{step.action}</div>
        {step.detail && (
          <div className="text-slate-500 text-xs mt-0.5 leading-relaxed">{step.detail}</div>
        )}
      </div>
    </div>
  )
}
