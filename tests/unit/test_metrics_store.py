import pytest
import pytest_asyncio  # <‑‑ use pytest‑asyncio fixture
from adaptive_engine.metrics.models import Base
from adaptive_engine.metrics.store import MetricsStore
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest_asyncio.fixture(scope="function")  # <‑‑ async fixture
async def store():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sm = async_sessionmaker(engine, expire_on_commit=False)
    yield MetricsStore(sm)
    await engine.dispose()


@pytest.mark.asyncio
async def test_link_metric_roundtrip(store):
    m = await store.add_link_metric(bandwidth_mbps=120.5, rtt_ms=3.2, loss=0.001, sinr_db=22.0)
    assert m.id == 1
    latest = await store.latest_link_metric()
    assert latest.bandwidth_mbps == 120.5
