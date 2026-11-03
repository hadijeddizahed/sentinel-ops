# 🛡️ SentinelOps: Autonomous Cloud Incident Responder

An enterprise-grade autonomous AI incident response agent. SentinelOps ingests production alerts, retrieves runbook mitigation steps via **Hybrid RAG**, maps dependency blast radius via **Knowledge Graphs**, and safely executes diagnostic scripts in an isolated **Python Sandbox** to generate verified post-mortem incident reports.

---

## 🎯 Implementation Checklist

### Milestone 1: Core Foundation & Data Contracts
- [ ] Define `Alert`, `State`, `WorkerOutputs`, and `PostMortem` Pydantic models in `src/schemas/models.py`
- [ ] Build the interactive CLI entrypoint in `src/main.py`
- [ ] Create unit tests in `tests/test_schemas.py` to verify alert validation

### Milestone 2: Knowledge Runbook Retrieval (Hybrid RAG)
- [ ] Add realistic runbooks in `data/runbooks/` (Kafka lag, DB connection pool, K8s OOM, Auth timeout)
- [ ] Implement `src/workers/rag_worker.py` combining **ChromaDB** (Dense) + **BM25Okapi** (Sparse)
- [ ] Implement **Reciprocal Rank Fusion (RRF)** to retrieve top runbook mitigation steps

### Milestone 3: Blast-Radius Knowledge Graph (NetworkX)
- [ ] Define enterprise microservice topology in `data/topology.json`
- [ ] Implement `src/workers/graph_worker.py` to construct a directed graph in NetworkX
- [ ] Implement blast-radius traversal to identify affected upstream/downstream services and owners

### Milestone 4: Sandboxed Code Execution & Executive Synthesis
- [ ] Implement `src/workers/exec_worker.py` with subprocess sandbox, timeouts, and env scrubbing
- [ ] Analyze `data/mock_metrics.csv` to calculate latency percentiles and verify SLA breaches
- [ ] Implement `src/agents/supervisor.py` to orchestrate workers and synthesize the final `PostMortem`
- [ ] *(Optional)* Implement `src/agents/triage_local.py` for fast local Apple M4 (MLX) alert triage

---

## 📂 Project Architecture

```
sentinel-ops/
├── data/
│   ├── runbooks/              # Realistic .md incident runbooks
│   │   ├── kafka_consumer_lag.md
│   │   ├── db_connection_pool.md
│   │   ├── kubernetes_oom.md
│   │   └── auth_gateway_timeout.md
│   ├── topology.json          # Microservice & team ownership definitions
│   └── mock_metrics.csv       # Production latency / error-rate logs
├── src/
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── models.py          # Pydantic schemas (Alert, State, WorkerOutputs, PostMortem)
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── rag_worker.py      # Hybrid RAG (ChromaDB + BM25Okapi + RRF)
│   │   ├── graph_worker.py    # NetworkX dependency & blast-radius analyzer
│   │   └── exec_worker.py     # Subprocess sandbox with timeout/AST guardrails
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── triage_local.py    # (Optional) Local MLX / Ollama fast classifier
│   │   └── supervisor.py      # Main router & multi-agent coordinator
│   ├── __init__.py
│   └── main.py                # CLI entry point / FastAPI webhook receiver
└── tests/
    ├── __init__.py
    ├── test_schemas.py
    ├── test_rag_worker.py
    └── test_sandbox.py
```

---

## 🚀 Getting Started

Run the interactive CLI:
```bash
python -m src.main
```

