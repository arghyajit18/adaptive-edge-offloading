Architecture Details
flowchart TD
    subgraph NS3[ns‑3 5G‑NR Simulator]
        UE[UE + RandomWaypoint Mobility] -->|Radio Link| GNB[gNB]
        GNB -->|Per‑tick JSON (BW,RTT,Loss,SINR)| WRAP[Ns3Wrapper (stdout)]
    end

    WRAP -->|async generator| LM[LinkMonitor]
    LM -->|latest snapshot| SCHED[AdaptiveScheduler]
    LM -->|persist| DB[(SQLite: link_metrics)]

    CLIENT[TaskGenerator] -->|HTTP POST /offload| API[FastAPI]
    API -->|DecisionRequest| SCHED
    SCHED -->|DecisionResponse| API
    API -->|DecisionLog| DB
    API -->|Response| CLIENT

    DB --> DASH[Plotly‑Dash Dashboard]
    DASH -->|poll (2 s)| DB
Component Responsibilities
Component	Language	Key Classes
ns‑3 scenario	C++	NrHelper, mobility, Simulator::Schedule
Ns3Wrapper	Python	Ns3Wrapper.start(), metrics() async generator
LinkMonitor	Python	LinkMonitor.run(), current()
Schedulers	Python	Scheduler ABC + AlwaysLocal, AlwaysEdge, Greedy, Adaptive
Predictors	Python	MovingAverageForecaster, ExpSmoothingForecaster, ForecasterSelector
FastAPI API	Python	main.lifespan, routes/offload, schemas
Client	Python	TaskGenerator, LocalExecutor
Dashboard	Python (Dash)	app.layout, callbacks (update_network_graphs, update_decision_graphs)
Persistence	Python (SQLAlchemy)	LinkMetric, DecisionLog, MetricsStore
Data Flow (per task)
1. Client creates OffloadRequest → POST /offload.
2. API hands request to Scheduler (Adaptive).
3. Scheduler asks LinkMonitor for latest metric snapshot (or predicts next).
4. Cost model → LOCAL / OFFLOAD + predicted latency & energy.
5. API stores DecisionLog (includes predictions) → returns response.
6. Dashboard polls SQLite every N seconds → live charts.
Configuration (YAML)
All tunables live in config/default.yaml (see file for full list).  
Environment variables override any key (e.g. NS3_BIN, DB_URL).
