import random
import time
from dataclasses import dataclass

import numpy as np
from adaptive_engine.api.schemas import OffloadRequest, TaskType
from adaptive_engine.config import settings


@dataclass
class TaskSpec:
    task_type: TaskType
    input_size_bytes: int
    compute_complexity: float
    deadline_ms: int


class TaskGenerator:
    def __init__(self):
        cfg = settings.client
        self._mix = cfg.mix
        self._size_range = cfg.size_range_bytes
        self._complexity_range = cfg.complexity_range
        self._deadline_range = cfg.deadline_range_ms
        self._rng = random.Random(cfg.seed)

    def __iter__(self):
        return self

    def __next__(self) -> OffloadRequest:
        t = self._rng.choices(list(self._mix.keys()), weights=list(self._mix.values()))[0]
        task_type = TaskType(t)
        sz = self._rng.randint(*self._size_range)
        comp = self._rng.uniform(*self._complexity_range)
        dl = self._rng.randint(*self._deadline_range)
        return OffloadRequest(
            task_id=f"{task_type.value}-{int(time.time()*1e6)}",
            task_type=task_type,
            input_size_bytes=sz,
            compute_complexity=comp,
            deadline_ms=dl,
        )


def _image_filter(data: bytes) -> bytes:
    # 64×64 = 4096 bytes → we need exactly that many bytes
    needed = 64 * 64
    if len(data) < needed:
        data = data.ljust(needed, b"\x00")
    img = np.frombuffer(data[:needed], dtype=np.uint8).reshape(64, 64).astype(np.float32)
    kernel = np.ones((3, 3), np.float32) / 9.0
    out = np.zeros_like(img)
    for i in range(1, 63):
        for j in range(1, 63):
            out[i, j] = np.sum(img[i - 1 : i + 2, j - 1 : j + 2] * kernel)
    return out.astype(np.uint8).tobytes()


def _matmul(data: bytes) -> bytes:
    # we expect a square matrix; choose the biggest n where n*n*8*2 <= len(data)
    max_bytes = len(data)
    n = int(np.sqrt(max_bytes // 16))  # 2 matrices, each n*n*8 bytes
    if n < 1:
        n = 1
    a_bytes = n * n * 8
    b_bytes = n * n * 8
    a = np.frombuffer(data[:a_bytes], dtype=np.float64).reshape(n, n)
    b = np.frombuffer(data[a_bytes : a_bytes + b_bytes], dtype=np.float64).reshape(n, n)
    c = a @ b
    return c.astype(np.float64).tobytes()


def _ml_inference(data: bytes) -> bytes:
    # we need 128‑dim input → 128 * 4 = 512 bytes
    needed = 128 * 4
    if len(data) < needed:
        data = data.ljust(needed, b"\x00")
    x = np.frombuffer(data[:needed], dtype=np.float32)  # shape (128,)
    w1 = np.sin(np.arange(128 * 64).reshape(128, 64)).astype(np.float32)
    w2 = np.cos(np.arange(64 * 10).reshape(64, 10)).astype(np.float32)
    h = np.maximum(0, x @ w1)  # (64,)
    y = h @ w2  # (10,)
    return y.astype(np.float32).tobytes()


_KERNELS = {
    TaskType.IMAGE: _image_filter,
    TaskType.MATMUL: _matmul,
    TaskType.ML_INFERENCE: _ml_inference,
}


def run_local_kernel(task_type: TaskType, payload: bytes) -> bytes:
    return _KERNELS[task_type](payload)
