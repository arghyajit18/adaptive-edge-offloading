from adaptive_engine.scheduler.base import Scheduler
from adaptive_engine.api.schemas import OffloadRequest, Decision
from adaptive_engine.network.link_monitor import LinkMonitor


class GreedyScheduler(Scheduler):
    def __init__(self, link_monitor: LinkMonitor):
        self._lm = link_monitor
        self._local_cpu_mhz = 2000
        self._edge_cpu_mhz = 10000

    async def schedule(self, req: OffloadRequest) -> Decision:
        metric = self._lm.current()
        if not metric:
            return Decision.LOCAL
        bw_mbps = metric["bandwidth_mbps"]
        rtt_ms = metric["rtt_ms"]
        loss = metric["loss"]

        local_ms = (req.compute_complexity * req.input_size_bytes) / (self._local_cpu_mhz * 1e6) * 1e3
        upload_ms = (req.input_size_bytes * 8) / (bw_mbps * 1e6) * 1e3 / (1 - loss)
        edge_compute_ms = (req.compute_complexity * req.input_size_bytes) / (self._edge_cpu_mhz * 1e6) * 1e3
        edge_ms = upload_ms + rtt_ms + edge_compute_ms
        return Decision.OFFLOAD if edge_ms < local_ms else Decision.LOCAL
