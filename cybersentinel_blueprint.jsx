import { useState } from "react";

const techColors = {
  react: "#61DAFB",
  fastapi: "#009688",
  langchain: "#1C3C3C",
  langraph: "#FF6B35",
  openai: "#10A37F",
  chroma: "#FF4B4B",
  websocket: "#9B59B6",
  python: "#3776AB",
};

const Layer = ({ title, color, children, subtitle }) => (
  <div className="rounded-xl border-2 p-4 mb-2" style={{ borderColor: color, background: color + "11" }}>
    <div className="text-xs font-bold uppercase tracking-widest mb-1" style={{ color }}>
      {title}
    </div>
    {subtitle && <div className="text-xs text-gray-400 mb-3">{subtitle}</div>}
    {children}
  </div>
);

const Box = ({ title, tech, icon, color, desc, onClick, selected }) => (
  <div
    onClick={() => onClick && onClick()}
    className="rounded-lg p-3 cursor-pointer transition-all duration-200 border"
    style={{
      background: selected ? color + "33" : "#1a1a2e",
      borderColor: selected ? color : "#333",
      transform: selected ? "scale(1.03)" : "scale(1)",
    }}
  >
    <div className="text-lg mb-1">{icon}</div>
    <div className="text-white text-xs font-bold">{title}</div>
    <div className="text-xs mt-1 font-mono px-1 rounded" style={{ color, background: color + "22" }}>
      {tech}
    </div>
    {desc && <div className="text-gray-400 text-xs mt-1">{desc}</div>}
  </div>
);

const Arrow = ({ label }) => (
  <div className="flex flex-col items-center my-1">
    <div className="text-xs text-gray-500 mb-1">{label}</div>
    <div className="text-gray-500 text-lg">↓</div>
  </div>
);

const FlowArrow = ({ from, to }) => (
  <div className="flex items-center justify-center gap-1 my-2">
    <span className="text-xs text-gray-500">{from}</span>
    <span className="text-orange-400 text-sm">→</span>
    <span className="text-xs text-gray-500">{to}</span>
  </div>
);

const InfoPanel = ({ node }) => {
  if (!node) return (
    <div className="text-gray-500 text-sm text-center mt-8">
      👆 Click any component to see details
    </div>
  );

  const details = {
    "React Dashboard": {
      color: techColors.react,
      desc: "The user-facing control center. Built with React + TailwindCSS.",
      responsibilities: [
        "Attack Control Panel — buttons to trigger each scenario",
        "Live Log Terminal — real-time streaming log feed",
        "Threat Alert Panel — severity badges, threat timeline",
        "Remediation Panel — AI-generated fix steps",
        "NovaPay company dashboard skin",
      ],
      libs: ["React 18", "TailwindCSS", "Recharts (threat graphs)", "WebSocket client"],
    },
    "FastAPI Backend": {
      color: techColors.fastapi,
      desc: "The central nervous system — connects all layers together.",
      responsibilities: [
        "WebSocket endpoint for real-time log streaming",
        "REST endpoints: /trigger-attack, /analyze, /threats",
        "Bridges simulation engine to LangGraph agents",
        "Handles streaming AI responses back to frontend",
      ],
      libs: ["FastAPI", "Uvicorn", "Python-WebSockets", "Pydantic v2"],
    },
    "Simulation Engine": {
      color: "#F59E0B",
      desc: "Generates realistic attack logs for NovaPay's fake infrastructure.",
      responsibilities: [
        "5 pre-scripted attack scenarios with timed phases",
        "Log generators: Auth, Nginx, Firewall, DB, API",
        "Realistic IPs, timestamps, user agents, transaction IDs",
        "Emits logs via WebSocket at configurable speed",
      ],
      libs: ["Python", "Faker (realistic data)", "asyncio (timed emission)", "Custom log templates"],
    },
    "Log Parser Agent": {
      color: techColors.langraph,
      desc: "First agent in the LangGraph pipeline.",
      responsibilities: [
        "Auto-detects log type (auth/nginx/firewall/db/api)",
        "Normalizes raw log strings into structured JSON",
        "Extracts: IP, timestamp, user, action, status code",
        "Passes structured data to Threat Detector",
      ],
      libs: ["LangChain", "LangGraph node", "Pydantic output parser"],
    },
    "Threat Detector Agent": {
      color: techColors.langraph,
      desc: "The core intelligence — spots attack patterns using LLM reasoning.",
      responsibilities: [
        "Pattern matching: brute force, SQLi, DDoS, exfiltration",
        "Cross-correlates multiple log lines for context",
        "LLM reasons about intent not just signatures",
        "Passes threat objects to Severity Classifier",
      ],
      libs: ["LangGraph", "GPT-4o / Claude", "RAG over CVE database"],
    },
    "Severity Classifier Agent": {
      color: techColors.langraph,
      desc: "Scores and prioritizes every detected threat.",
      responsibilities: [
        "Outputs: CRITICAL / HIGH / MEDIUM / LOW",
        "Structured Pydantic output — no hallucination risk",
        "Considers: attack type, affected system, blast radius",
        "Triggers immediate alert for CRITICAL threats",
      ],
      libs: ["LangGraph", "Pydantic structured output", "GPT-4o"],
    },
    "Remediation Agent": {
      color: techColors.langraph,
      desc: "Generates actionable fix steps for each threat.",
      responsibilities: [
        "Step-by-step remediation instructions",
        "References relevant CVEs if applicable",
        "Tailored to NovaPay's stack (Node.js, Nginx, PostgreSQL)",
        "Short-term fix + long-term hardening recommendations",
      ],
      libs: ["LangGraph", "RAG over security playbooks", "GPT-4o"],
    },
    "ChromaDB + RAG": {
      color: techColors.chroma,
      desc: "Knowledge base that makes the AI responses accurate and specific.",
      responsibilities: [
        "CVE database embeddings (50k+ known vulnerabilities)",
        "Security playbooks (OWASP, NIST frameworks)",
        "Attack pattern signatures",
        "NovaPay-specific context (stack, services, compliance)",
      ],
      libs: ["ChromaDB", "OpenAI Embeddings", "LangChain VectorStore"],
    },
    "LangGraph Orchestrator": {
      color: "#FF6B35",
      desc: "The brain that routes between all agents in the right order.",
      responsibilities: [
        "State machine managing agent handoffs",
        "Parallel execution: Parser runs while Detector waits",
        "Error recovery: retries failed agent steps",
        "Streams intermediate results back to FastAPI",
      ],
      libs: ["LangGraph", "StateGraph", "Conditional edges"],
    },
  };

  const d = details[node];
  if (!d) return null;

  return (
    <div>
      <div className="text-white font-bold text-sm mb-2" style={{ color: d.color }}>{node}</div>
      <p className="text-gray-300 text-xs mb-3">{d.desc}</p>
      <div className="text-xs font-bold text-gray-400 uppercase mb-2">Responsibilities</div>
      <ul className="space-y-1 mb-3">
        {d.responsibilities.map((r, i) => (
          <li key={i} className="text-xs text-gray-300 flex gap-2">
            <span style={{ color: d.color }}>▸</span> {r}
          </li>
        ))}
      </ul>
      <div className="text-xs font-bold text-gray-400 uppercase mb-2">Libraries / Tools</div>
      <div className="flex flex-wrap gap-1">
        {d.libs.map((l, i) => (
          <span key={i} className="text-xs px-2 py-0.5 rounded-full" style={{ background: d.color + "22", color: d.color }}>
            {l}
          </span>
        ))}
      </div>
    </div>
  );
};

export default function Blueprint() {
  const [selected, setSelected] = useState(null);

  const toggle = (name) => setSelected(selected === name ? null : name);

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6 font-sans">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="text-3xl font-black tracking-tight mb-1">
          🛡️ <span className="text-orange-400">CyberSentinel</span>
        </div>
        <div className="text-gray-400 text-sm">AI-Powered Log Security Analyzer + NovaPay Simulation</div>
        <div className="text-gray-600 text-xs mt-1">Click any component to explore its role</div>
      </div>

      <div className="flex gap-6 max-w-6xl mx-auto">
        {/* LEFT: Architecture Diagram */}
        <div className="flex-1 min-w-0">

          {/* Layer 1: Frontend */}
          <Layer title="Layer 1 — Frontend" color={techColors.react} subtitle="What the user sees & controls">
            <div className="grid grid-cols-2 gap-2">
              <Box title="React Dashboard" tech="React + Tailwind" icon="🖥️" color={techColors.react}
                desc="Attack panel, log feed, threat alerts" onClick={() => toggle("React Dashboard")} selected={selected === "React Dashboard"} />
              <Box title="WebSocket Client" tech="WS + Streaming" icon="⚡" color={techColors.websocket}
                desc="Real-time log stream receiver" onClick={() => toggle("React Dashboard")} selected={selected === "React Dashboard"} />
            </div>
          </Layer>

          <Arrow label="HTTP / WebSocket" />

          {/* Layer 2: Backend */}
          <Layer title="Layer 2 — Backend" color={techColors.fastapi} subtitle="Central orchestration server">
            <Box title="FastAPI Backend" tech="FastAPI + Uvicorn" icon="⚙️" color={techColors.fastapi}
              desc="REST + WebSocket, bridges all layers" onClick={() => toggle("FastAPI Backend")} selected={selected === "FastAPI Backend"} />
          </Layer>

          <div className="flex gap-2 items-start">
            <div className="flex-1">
              <Arrow label="triggers" />
              {/* Layer 3a: Simulation */}
              <Layer title="Layer 3A — Simulation Engine" color="#F59E0B" subtitle="NovaPay fake company logs">
                <Box title="Simulation Engine" tech="Python + Faker" icon="🏦" color="#F59E0B"
                  desc="5 attack scenarios, realistic log emission" onClick={() => toggle("Simulation Engine")} selected={selected === "Simulation Engine"} />
                <div className="grid grid-cols-3 gap-1 mt-2">
                  {["Auth Logs", "Nginx Logs", "Firewall Logs", "DB Logs", "API Logs", "App Logs"].map(l => (
                    <div key={l} className="text-center text-xs py-1 rounded" style={{ background: "#F59E0B22", color: "#F59E0B" }}>{l}</div>
                  ))}
                </div>
              </Layer>
            </div>

            <div className="flex-1">
              <Arrow label="log stream" />
              {/* Layer 3b: LangGraph */}
              <Layer title="Layer 3B — LangGraph Agents" color={techColors.langraph} subtitle="Multi-agent AI pipeline">
                <Box title="LangGraph Orchestrator" tech="LangGraph StateGraph" icon="🧠" color="#FF6B35"
                  desc="Routes between agents, manages state" onClick={() => toggle("LangGraph Orchestrator")} selected={selected === "LangGraph Orchestrator"} />
                <div className="mt-2 space-y-2">
                  {[
                    { title: "Log Parser Agent", icon: "📋", desc: "Normalizes raw logs to structured JSON" },
                    { title: "Threat Detector Agent", icon: "🔍", desc: "Detects attack patterns via LLM" },
                    { title: "Severity Classifier Agent", icon: "🚨", desc: "Scores CRITICAL/HIGH/MEDIUM/LOW" },
                    { title: "Remediation Agent", icon: "🔧", desc: "Generates step-by-step fix plans" },
                  ].map(a => (
                    <Box key={a.title} title={a.title} tech="LangChain + GPT-4o" icon={a.icon} color={techColors.langraph}
                      desc={a.desc} onClick={() => toggle(a.title)} selected={selected === a.title} />
                  ))}
                </div>
              </Layer>
            </div>
          </div>

          <Arrow label="vector search + embeddings" />

          {/* Layer 4: Infrastructure */}
          <Layer title="Layer 4 — AI Infrastructure" color={techColors.chroma} subtitle="Knowledge base & LLM">
            <div className="grid grid-cols-3 gap-2">
              <Box title="ChromaDB + RAG" tech="ChromaDB + Embeddings" icon="🗄️" color={techColors.chroma}
                desc="CVE database, security playbooks" onClick={() => toggle("ChromaDB + RAG")} selected={selected === "ChromaDB + RAG"} />
              <Box title="LLM" tech="GPT-4o / Claude" icon="🤖" color={techColors.openai}
                desc="Core reasoning engine" onClick={() => toggle("LangGraph Orchestrator")} selected={selected === "LangGraph Orchestrator"} />
              <Box title="Embeddings" tech="OpenAI Ada-002" icon="🔢" color="#6366F1"
                desc="Log + CVE vectorization" onClick={() => toggle("ChromaDB + RAG")} selected={selected === "ChromaDB + RAG"} />
            </div>
          </Layer>

          {/* Data Flow Summary */}
          <div className="mt-6 rounded-xl border border-gray-800 p-4 bg-gray-900">
            <div className="text-xs font-bold text-gray-400 uppercase mb-3">⚡ Data Flow — End to End</div>
            <div className="flex flex-wrap gap-1 items-center text-xs">
              {[
                { label: "User triggers attack", color: techColors.react },
                { label: "→" },
                { label: "Sim Engine generates logs", color: "#F59E0B" },
                { label: "→" },
                { label: "FastAPI streams via WS", color: techColors.fastapi },
                { label: "→" },
                { label: "Parser normalizes", color: techColors.langraph },
                { label: "→" },
                { label: "Detector flags threats", color: techColors.langraph },
                { label: "→" },
                { label: "RAG adds CVE context", color: techColors.chroma },
                { label: "→" },
                { label: "Classifier scores severity", color: techColors.langraph },
                { label: "→" },
                { label: "Remediation generates fix", color: techColors.langraph },
                { label: "→" },
                { label: "React dashboard lights up", color: techColors.react },
              ].map((item, i) =>
                item.label === "→"
                  ? <span key={i} className="text-gray-600">→</span>
                  : <span key={i} className="px-2 py-0.5 rounded-full text-xs" style={{ background: item.color + "22", color: item.color }}>{item.label}</span>
              )}
            </div>
          </div>
        </div>

        {/* RIGHT: Info Panel */}
        <div className="w-72 flex-shrink-0">
          <div className="sticky top-6 rounded-xl border border-gray-800 bg-gray-900 p-4 min-h-64">
            <div className="text-xs font-bold text-gray-400 uppercase mb-3">📌 Component Details</div>
            <InfoPanel node={selected} />
          </div>

          {/* Tech Stack Summary */}
          <div className="mt-4 rounded-xl border border-gray-800 bg-gray-900 p-4">
            <div className="text-xs font-bold text-gray-400 uppercase mb-3">🛠️ Full Tech Stack</div>
            <div className="space-y-2">
              {[
                { label: "Frontend", tech: "React + TailwindCSS", color: techColors.react },
                { label: "Backend", tech: "FastAPI + Uvicorn", color: techColors.fastapi },
                { label: "Orchestration", tech: "LangGraph + LangChain", color: techColors.langraph },
                { label: "LLM", tech: "GPT-4o or Claude 3.5", color: techColors.openai },
                { label: "Vector DB", tech: "ChromaDB", color: techColors.chroma },
                { label: "Realtime", tech: "WebSockets", color: techColors.websocket },
                { label: "Simulation", tech: "Python + Faker", color: "#F59E0B" },
                { label: "Data Models", tech: "Pydantic v2", color: techColors.python },
              ].map(item => (
                <div key={item.label} className="flex justify-between items-center">
                  <span className="text-gray-400 text-xs">{item.label}</span>
                  <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: item.color + "22", color: item.color }}>{item.tech}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Attack Scenarios */}
          <div className="mt-4 rounded-xl border border-gray-800 bg-gray-900 p-4">
            <div className="text-xs font-bold text-gray-400 uppercase mb-3">🎬 Attack Scenarios</div>
            <div className="space-y-1">
              {[
                { icon: "🔨", name: "Account Takeover", severity: "CRITICAL" },
                { icon: "💳", name: "Transaction Fraud", severity: "CRITICAL" },
                { icon: "💉", name: "SQL Injection", severity: "HIGH" },
                { icon: "👤", name: "Insider Threat", severity: "HIGH" },
                { icon: "🌊", name: "DDoS Attack", severity: "HIGH" },
              ].map(s => (
                <div key={s.name} className="flex items-center justify-between text-xs">
                  <span className="text-gray-300">{s.icon} {s.name}</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs ${s.severity === "CRITICAL" ? "bg-red-900 text-red-300" : "bg-orange-900 text-orange-300"}`}>
                    {s.severity}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
