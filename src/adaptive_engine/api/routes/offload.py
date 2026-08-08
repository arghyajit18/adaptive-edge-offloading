from fastapi import APIRouter, Depends
from adaptive_engine.api.schemas import OffloadRequest, OffloadResponse, Decision
from adaptive_engine.scheduler.base import Scheduler
from adaptive_engine.api.deps import get_scheduler, get_sessionmaker   # ← from deps
from adaptive_engine.metrics.store import MetricsStore
from adaptive_engine.client.local_executor import LocalExecutor

router = APIRouter(prefix="/offload", tags=["offload"])
_executor = LocalExecutor()


@router.post("", response_model=OffloadResponse)
async def decide_offload(
    req: OffloadRequest,
    scheduler: Scheduler = Depends(get_scheduler),
    sessionmaker = Depends(get_sessionmaker),
) -> OffloadResponse:
    decision = await scheduler.schedule(req)

    if decision == Decision.LOCAL:
        pred_lat_ms, pred_energy_mj = _executor.execute(req)
    else:
        from adaptive_engine.network.link_monitor import LinkMonitor
        from adaptive_engine.api.main import app
        lm: LinkMonitor = app.state.link_monitor
        metric = lm.current() or {"bandwidth_mbps": 50, "rtt_ms": 5, "loss": 0.01}
        bw, rtt, loss = metric["bandwidth_mbps"], metric["rtt_ms"], metric["loss"]
        upload_ms = (req.input_size_bytes * 8) / (bw * 1e6) * 1e3 / max(1 - loss, 1e-3)
        edge_compute_ms = (req.compute_complexity * req.input_size_bytes) / 1e10 * 1e3
        pred_lat_ms = upload_ms + rtt + edge_compute_ms
        pred_energy_mj = (req.input_size_bytes / 1e6) * 5.0

    store = MetricsStore(sessionmaker)
    await store.add_decision(
        task_id=req.task_id,
        task_type=req.task_type.value,
        input_size_bytes=req.input_size_bytes,
        compute_complexity=req.compute_complexity,
        deadline_ms=req.deadline_ms,
        decision=decision.value,
        predicted_latency_ms=pred_lat_ms,
        predicted_energy_mj=pred_energy_mj,
    )

    return OffloadResponse(
        task_id=req.task_id,
        decision=decision,
        predicted_latency_ms=pred_lat_ms,
        predicted_energy_mj=pred_energy_mj,
    )
