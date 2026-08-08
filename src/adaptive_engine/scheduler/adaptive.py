from adaptive_engine.api.schemas import Decision, OffloadRequest
from adaptive_engine.config import settings
from adaptive_engine.network.link_monitor import LinkMonitor
from adaptive_engine.prediction.selector import ForecasterSelector
from adaptive_engine.scheduler.base import Scheduler


class AdaptiveScheduler(Scheduler):
    def __init__(self, link_monitor: LinkMonitor):
        self._lm = link_monitor
        self._selector = ForecasterSelector(
            window=settings.prediction.window,
            eval_interval=settings.prediction.eval_interval,
        )
        self._tx_energy_per_mb = 5.0  # mJ per MB transmitted
        self._cpu_energy_per_cycle = 1e-9  # J per CPU cycle
        self._battery_budget_mj = settings.battery.budget_mj
        self._spent_mj = 0.0
        self._local_cpu_hz = 2e9
        self._edge_cpu_hz = 1e10

    async def schedule(self, req: OffloadRequest) -> Decision:
        current = self._lm.current()
        # ---- fallback when we have no live metrics ----
        if not current:
            return Decision.LOCAL

        if current:
            self._selector.update(current)

        pred = self._selector.predict_all()
        bw_mbps = pred.get("bandwidth_mbps", current.get("bandwidth_mbps", 50) if current else 50)
        rtt_ms = pred.get("rtt_ms", current.get("rtt_ms", 5) if current else 5)
        loss = pred.get("loss", current.get("loss", 0.01) if current else 0.01)

        tx_mb = req.input_size_bytes / 1e6
        offload_tx_energy = tx_mb * self._tx_energy_per_mb
        local_cpu_cycles = req.compute_complexity * req.input_size_bytes
        local_cpu_energy = local_cpu_cycles * self._cpu_energy_per_cycle

        if self._spent_mj + min(offload_tx_energy, local_cpu_energy) > self._battery_budget_mj:
            return Decision.LOCAL

        local_ms = (local_cpu_cycles / self._local_cpu_hz) * 1e3
        upload_ms = (req.input_size_bytes * 8) / (bw_mbps * 1e6) * 1e3 / max(1 - loss, 1e-3)
        edge_compute_ms = (local_cpu_cycles / self._edge_cpu_hz) * 1e3
        edge_ms = upload_ms + rtt_ms + edge_compute_ms

        decision = Decision.OFFLOAD if edge_ms < local_ms else Decision.LOCAL
        self._spent_mj += offload_tx_energy if decision == Decision.OFFLOAD else local_cpu_energy
        return decision
