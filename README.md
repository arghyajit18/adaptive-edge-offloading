# Adaptive Edge‑Offloading Engine for 5G 🚀

> Real‑time decision engine that decides **LOCAL** vs **OFFLOAD** for compute tasks over a simulated 5G‑NR link (ns‑3).  
> Built for a portfolio that targets Samsung, Qualcomm, Ericsson, Nokia, and other telecom / edge‑software teams.

---

## 🎯 Features
| Area | Highlights |
|------|------------|
| **5G‑NR Link Emulator** | ns‑3.42 + 5G‑NR module, mobility, Rayleigh fading, per‑100 ms JSON metrics |
| **Decision Engine** | Baselines (Always‑Local, Always‑Edge, Greedy) + **Adaptive** predictor (MA / EWMA) + battery budget |
| **API** | FastAPI + async SQLAlchemy (SQLite) – `/offload` returns decision, predicted latency & energy |
| **Client Workloads** | Synthetic image filter, matrix multiply, tiny‑ML inference; local executor measures true CPU time & energy |
| **Dashboard** | Plotly‑Dash live charts (BW, RTT, loss, SINR, decision ratio, latency, energy, deadline‑miss) |
| **Offline Benchmark** | `scripts/run_comparison.py` → CSV for paper‑style plots |
| **CI/CD** | GitHub Actions (ruff, black, isort, codespell, mypy, pytest, multi‑arch Docker) |
| **Developer Experience** | `make lint`, `make test`, `pre-commit`, poetry, type hints, structured logging |

---

## 🏗 Architecture

```mermaid
flowchart LR
    subgraph Sim[ns‑3 5G‑NR Simulator]
        UE[UE + Mobility] -->|JSON metrics| Wrapper[Python Ns3Wrapper]
    end
    Wrapper -->|async stream| LinkMon[LinkMonitor]
    LinkMon -->|latest snapshot| Sched[Adaptive Scheduler]
    Client[Task Generator] -->|HTTP /offload| API[FastAPI]
    API --> Sched
    API --> DB[(SQLite)]
    Sched -->|decision| API
    API -->|response| Client
    DB --> Dash[Plotly‑Dash]
⚡ Quick‑Start (Docker)
# 1️⃣ Clone & enter
git clone https://github.com/<your‑org>/adaptive-edge-offloading.git
cd adaptive-edge-offloading

# 2️⃣ Build & launch all services
docker compose -f docker/docker-compose.yml up --build -d

# 3️⃣ Open the dashboard
#    http://localhost:8050
#    API docs: http://localhost:8000/docs
The ns3 container streams link metrics, the api container runs the decision engine, and the dashboard container visualises everything.
🧪 Local Development (no Docker)
# 1️⃣ Create venv & install
python -m venv .venv && source .venv/bin/activate
pip install -U pip poetry
poetry install --with dev

# 2️⃣ Run ns‑3 (needs the compiled binary – use the Docker image or build locally)
#    For a quick mock:
poetry run python -m adaptive_engine.network.ns3_wrapper   # prints JSON lines

# 3️⃣ Start API + background monitor
poetry run uvicorn adaptive_engine.api.main:app --reload

# 4️⃣ Start dashboard (separate terminal)
poetry run python -m adaptive_engine.dashboard.app
Run the test‑suite:
make test          # or: poetry run pytest -q
Lint / type‑check:
make lint
📦 Publish Docker Images (GitHub Actions + Docker Hub)
1. Add two repository secrets in GitHub → Settings → Secrets → Actions  
- DOCKERHUB_USERNAME  
- DOCKERHUB_TOKEN (personal access token)
2. Tag a release (git tag v0.1.0 && git push --tags).  
3. The docker-build job in CI will push three images:  
your‑dockerhub/adaptive-edge-offloading/api:<sha>  
your‑dockerhub/adaptive-edge-offloading/ns3:<sha>  
your‑dockerhub/adaptive-edge-offloading/dashboard:<sha>
You can also push manually:
make docker-build
make docker-push   # requires `docker login` first
📂 Repo Layout (key folders)
adaptive-edge-offloading/
├─ config/                 # YAML config (network, battery, client, dashboard)
├─ docker/                 # Multi‑stage Dockerfiles + compose
├─ docs/                   # Architecture markdown (Mermaid)
├─ scripts/                # ns3 scenario, comparison harness
├─ src/adaptive_engine/    # Core Python package
│   ├─ api/                # FastAPI routes, schemas, lifespan
│   ├─ client/             # TaskGenerator, LocalExecutor
│   ├─ dashboard/          # Plotly‑Dash app
│   ├─ metrics/            # SQLAlchemy models + store
│   ├─ network/            # Ns3Wrapper, LinkMonitor
│   ├─ prediction/         # MA, EWMA, Selector
│   └─ scheduler/          # Baselines + AdaptiveScheduler
├─ tests/                  # Unit & integration tests
├─ .github/workflows/ci.yml
├─ Makefile
├─ pyproject.toml
├─ README.md
└─ CHANGELOG.md
📈 Results (example)
Running the offline harness (scripts/run_comparison.py, 200 tasks) yields a CSV that can be plotted:
Scheduler	Avg Latency (ms)
AlwaysLocal	18.4
AlwaysEdge	9.1
Greedy	8.7
Adaptive	8.5
(Numbers are illustrative – they depend on the ns‑3 trace.)
📜 License
MIT – see LICENSE.
🙏 Acknowledgements
- ns‑3 & 5G‑NR module maintainers  
- FastAPI, Plotly‑Dash, SQLAlchemy, Pydantic communities
Built with ❤️ for a telecom‑grade portfolio piece.  
