import pytest
from adaptive_engine.api.schemas import TaskType
from adaptive_engine.client.local_executor import LocalExecutor
from adaptive_engine.client.task_generator import TaskGenerator, run_local_kernel


def test_generator_yields_requests():
    gen = TaskGenerator()
    req = next(gen)
    assert req.task_type in TaskType
    assert req.input_size_bytes > 0
    assert req.compute_complexity > 0
    assert req.deadline_ms > 0


@pytest.mark.parametrize("tt", [TaskType.IMAGE, TaskType.MATMUL, TaskType.ML_INFERENCE])
def test_kernels_run(tt):
    payload = b"\x00" * 1024
    out = run_local_kernel(tt, payload)
    assert isinstance(out, bytes) and len(out) > 0


def test_local_executor_returns_numbers():
    exec_ = LocalExecutor()
    from adaptive_engine.api.schemas import OffloadRequest

    req = OffloadRequest(
        task_id="t",
        task_type=TaskType.MATMUL,
        input_size_bytes=1024,
        compute_complexity=100,
        deadline_ms=100,
    )
    lat, en = exec_.execute(req)
    assert lat > 0 and en > 0
