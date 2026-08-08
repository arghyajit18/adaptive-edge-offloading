from unittest.mock import MagicMock

import pytest
from adaptive_engine.api.schemas import Decision, OffloadRequest
from adaptive_engine.network.link_monitor import LinkMonitor
from adaptive_engine.scheduler.adaptive import AdaptiveScheduler
from adaptive_engine.scheduler.always_edge import AlwaysEdgeScheduler
from adaptive_engine.scheduler.always_local import AlwaysLocalScheduler
from adaptive_engine.scheduler.greedy import GreedyScheduler


@pytest.fixture
def sample_req():
    return OffloadRequest(
        task_id="t-1",
        task_type="matmul",
        input_size_bytes=2_000_000,
        compute_complexity=500,
        deadline_ms=200,
    )


@pytest.mark.asyncio
async def test_always_local(sample_req):
    s = AlwaysLocalScheduler()
    assert await s.schedule(sample_req) == Decision.LOCAL


@pytest.mark.asyncio
async def test_always_edge(sample_req):
    s = AlwaysEdgeScheduler()
    assert await s.schedule(sample_req) == Decision.OFFLOAD


@pytest.mark.asyncio
async def test_greedy_uses_link_monitor(sample_req):
    lm = MagicMock(spec=LinkMonitor)
    lm.current = MagicMock(return_value={"bandwidth_mbps": 100, "rtt_ms": 2, "loss": 0.0})
    s = GreedyScheduler(lm)
    assert await s.schedule(sample_req) == Decision.OFFLOAD


@pytest.mark.asyncio
async def test_adaptive_falls_back_to_local_when_no_metrics(sample_req):
    lm = MagicMock(spec=LinkMonitor)
    lm.current = MagicMock(return_value=None)
    s = AdaptiveScheduler(lm)
    assert await s.schedule(sample_req) == Decision.LOCAL
