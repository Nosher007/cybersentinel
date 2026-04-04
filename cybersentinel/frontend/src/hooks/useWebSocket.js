import { useState, useEffect, useRef, useCallback } from 'react'

const WS_URL = 'ws://localhost:8000/ws'

/**
 * useWebSocket — connects to the CyberSentinel backend WebSocket.
 *
 * Returns:
 *   logs        — array of raw log strings
 *   status      — latest status string (e.g. "simulation_complete")
 *   threat      — latest threat_detected payload object
 *   remediation — latest remediation_plan payload object
 *   pipelineError — latest pipeline_error string
 *   isConnected — boolean
 *   clearState  — reset all accumulated state
 */
export function useWebSocket() {
  const [logs, setLogs] = useState([])
  const [status, setStatus] = useState(null)
  const [threat, setThreat] = useState(null)
  const [remediation, setRemediation] = useState(null)
  const [pipelineError, setPipelineError] = useState(null)
  const [isConnected, setIsConnected] = useState(false)

  const wsRef = useRef(null)

  useEffect(() => {
    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      setIsConnected(true)
    }

    ws.onclose = () => {
      setIsConnected(false)
    }

    ws.onerror = () => {
      setIsConnected(false)
    }

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)

        switch (msg.type) {
          case 'log':
            setLogs((prev) => [...prev, msg.log])
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
          default:
            break
        }
      } catch {
        // non-JSON message — ignore
      }
    }

    return () => {
      ws.close()
    }
  }, [])

  const clearState = useCallback(() => {
    setLogs([])
    setStatus(null)
    setThreat(null)
    setRemediation(null)
    setPipelineError(null)
  }, [])

  return {
    logs,
    status,
    threat,
    remediation,
    pipelineError,
    isConnected,
    clearState,
  }
}
