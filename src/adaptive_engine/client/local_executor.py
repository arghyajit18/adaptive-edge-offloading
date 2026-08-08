import time, os
from adaptive_engine.client.task_generator import run_local_kernel
from adaptive_engine.api.schemas import TaskType
from adaptive_engine.config import settings


class LocalExecutor:
    def __init__(self):
        cfg = settings.client.local_executor
        self._base_w = cfg["base_power_w"]
        self._dyn_coeff = cfg["dyn_coeff"]
        self._freq_ghz = cfg["cpu_freq_ghz"]
        self._max_complexity = cfg["max_complexity"]

    def execute(self, req) -> tuple[float, float]:
        payload = os.urandom(req.input_size_bytes)
        start = time.perf_counter()
        _ = run_local_kernel(req.task_type, payload)
        elapsed_s = time.perf_counter() - start
        elapsed_ms = elapsed_s * 1_000
        util = min(req.compute_complexity / self._max_complexity, 1.0)
        power_w = self._base_w + self._dyn_coeff * (self._freq_ghz ** 2) * util
        energy_j = power_w * elapsed_s
        energy_mj = energy_j * 1_000
        return elapsed_ms, energy_mj
