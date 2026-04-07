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
    <div className="bg-emerald-900/10 border border-emerald-800/30 rounded-lg p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-emerald-400 text-xs font-semibold">Remediation Plan</span>
        {remediation.plan_id && (
          <span className="text-slate-700 text-[10px] font-mono">{remediation.plan_id}</span>
        )}
      </div>

      {remediation.summary && (
        <p className="text-slate-400 text-xs mb-3 leading-relaxed">{remediation.summary}</p>
      )}

      {/* Immediate steps */}
      {immediateSteps.length > 0 && (
        <div className="mb-3">
          <div className="text-[10px] text-slate-600 uppercase tracking-widest mb-2">Immediate</div>
          <div className="space-y-1.5">
            {immediateSteps.map((step, i) => {
              shownSoFar++
              const show = visibleCount >= shownSoFar
              return <StepRow key={`imm-${i}`} step={step} show={show} color="emerald" />
            })}
          </div>
        </div>
      )}

      {/* Hardening steps */}
      {hardeningSteps.length > 0 && (
        <div className="mb-3">
          <div className="text-[10px] text-slate-600 uppercase tracking-widest mb-2">Hardening</div>
          <div className="space-y-1.5">
            {hardeningSteps.map((step, i) => {
              shownSoFar++
              const show = visibleCount >= shownSoFar
              return <StepRow key={`hard-${i}`} step={step} show={show} color="cyan" />
            })}
          </div>
        </div>
      )}

      {/* CVE references */}
      {cveRefs.length > 0 && visibleCount >= allSteps.length && (
        <div className="mt-3 pt-3 border-t border-emerald-900/40">
          <div className="text-[10px] text-slate-600 uppercase tracking-widest mb-2">CVE Refs</div>
          <div className="flex flex-wrap gap-1.5">
            {cveRefs.map((cve) => (
              <span
                key={cve}
                className="text-[10px] font-mono bg-white/[0.03] border border-white/[0.06] text-slate-400 px-2 py-0.5 rounded"
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
  const [popped, setPopped] = useState(false)
  const [checked, setChecked] = useState(false)

  useEffect(() => {
    if (!show) return
    const t1 = setTimeout(() => setPopped(true), 50)
    const t2 = setTimeout(() => setChecked(true), 450)
    return () => { clearTimeout(t1); clearTimeout(t2) }
  }, [show])

  const bgColors = { emerald: 'bg-emerald-500', cyan: 'bg-cyan-500' }

  return (
    <div className={`transition-all duration-500 ${
      show ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-2'
    } flex gap-2.5 items-start`}>
      <div className={`w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${bgColors[color]} ${popped ? 'step-pop' : ''}`}>
        <span className="text-white text-[9px] font-bold">
          {checked ? '✓' : step.order}
        </span>
      </div>
      <div>
        <div className="text-slate-300 text-xs font-medium">{step.action}</div>
        {step.detail && (
          <div className="text-slate-600 text-[11px] mt-0.5 leading-relaxed">{step.detail}</div>
        )}
      </div>
    </div>
  )
}
