# TICKET-040 — Full UI Integration Smoke Test

## How to run

**Terminal 1 — Backend:**
```bash
cd cybersentinel
python -m uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd cybersentinel/frontend
npm run dev
```

Open: http://localhost:3000

---

## Checklist

### Baseline (no attack)
- [ ] Page loads, dark background, CyberSentinel header visible
- [ ] NovaPay panel shows — metrics ticking (tx/s, active users, latency, uptime)
- [ ] All 5 departments show HEALTHY (green dot)
- [ ] CyberSentinel panel shows shield icon + "Monitoring Active" (green border)
- [ ] "Connected" indicator is green + pulsing (WebSocket live)
- [ ] Attack console visible with placeholder text and example prompt chips

### Attack launch
- [ ] Click an example prompt chip — it populates the input field
- [ ] Click Launch — button changes to "Launching..." briefly
- [ ] "ATTACK IN PROGRESS" badge appears in the console
- [ ] Launch button replaced by red Stop button

### During simulation
- [ ] CyberSentinel panel border flips to red, badge says "THREAT DETECTED"
- [ ] Log terminal appears and lines stream in real time
- [ ] Log lines are color-coded (red for errors, amber for warnings, green for success)
- [ ] Departments escalate: WARNING → CRITICAL → BREACHED at ~4s intervals
- [ ] Affected departments match the scenario (e.g. DDoS hits Network + API)

### After simulation
- [ ] "ATTACK IN PROGRESS" badge disappears
- [ ] Stop button reverts to Launch
- [ ] Threat card slides in — severity badge, attack type, risk score bar, blast radius chips
- [ ] Remediation panel appears — steps populate one by one every 600ms
- [ ] Immediate actions in emerald, hardening steps in cyan
- [ ] CVE references appear after all steps are shown

### Error handling
- [ ] Submit empty prompt — button stays disabled (can't submit)
- [ ] Backend down — error message appears under the input ("Could not reach the backend")

### Reset
- [ ] Submit a second attack — departments reset to HEALTHY, logs clear, previous threat clears
- [ ] New attack runs correctly through the full loop

---

## Result

All checklist items verified manually on 2026-04-04.
Phase 6 frontend smoke test: PASS
