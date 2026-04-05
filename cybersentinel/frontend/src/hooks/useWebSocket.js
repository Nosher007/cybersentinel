import { useState, useEffect, useRef, useCallback } from 'react'

// In production, VITE_BACKEND_URL is the Cloud Run URL (set in GitHub Actions)
// In development, falls back to localhost
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:8000'
const WS_URL = BACKEND_URL.replace(/^http/, 'ws') + '/ws'

const HEALTHY_METRICS = {
  txPerSec: 42,
  activeUsers: 1284,
  apiLatencyMs: 38,
  uptimePct: 99.97,
}

export function useWebSocket() {
  const [logs, setLogs] = useState([])
  const [status, setStatus] = useState(null)
  const [threat, setThreat] = useState(null)
  const [remediation, setRemediation] = useState(null)
  const [pipelineError, setPipelineError] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [metrics, setMetrics] = useState(HEALTHY_METRICS)

  const wsRef = useRef(null)

  useEffect(() => {
    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      setIsConnected(true)
      // Clear any stale simulation left over from a previous page session
      fetch(`${BACKEND_URL}/stop`, { method: 'POST' }).catch(() => {})
    }
    ws.onclose = () => setIsConnected(false)
    ws.onerror = () => setIsConnected(false)

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        switch (msg.type) {
          case 'log':
            setLogs((prev) => {
              const next = [...prev, msg.log]
              return next.length > 200 ? next.slice(-200) : next
            })
            break
          case 'status':
            setStatus(msg.message)
            break
          case 'threat_detected':
            setThreat(msg.data)
            break
          case 'remediation_plan':
            setRemediation(msg.data)
            break
          case 'pipeline_error':
            setPipelineError(msg.error)
            break
          case 'metric_update':
            setMetrics(msg.data)
            break
          default:
            break
        }
      } catch {
        // non-JSON message — ignore
      }
    }

    return () => ws.close()
  }, [])

  const clearState = useCallback(() => {
    setLogs([])
    setStatus(null)
    setThreat(null)
    setRemediation(null)
    setPipelineError(null)
    setMetrics(HEALTHY_METRICS)
  }, [])

  return {
    logs,
    status,
    threat,
    remediation,
    pipelineError,
    isConnected,
    metrics,
    clearState,
  }
}
