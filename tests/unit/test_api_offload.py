import pytest
from httpx import AsyncClient, ASGITransport
from adaptive_engine.api.main import app
from adaptive_engine.scheduler.always_local import AlwaysLocalScheduler
from adaptive_engine.api.deps import get_scheduler, get_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from adaptive_engine.metrics.models import Base


@pytest.fixture(autouse=True)
def _override_deps():
    """Force the /offload endpoint to use a LOCAL‑only scheduler *and* a real DB."""
    # ----- DB ---------------------------------------------------------
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)

    async def _create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # run the async table creation once
    import asyncio
    asyncio.run(_create_tables())

    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    # ----- overrides --------------------------------------------------
    app.dependency_overrides[get_scheduler] = lambda: AlwaysLocalScheduler()
    app.dependency_overrides[get_sessionmaker] = lambda: sessionmaker

    yield

    # cleanup
    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())


@pytest.mark.asyncio
async def test_offload_endpoint_returns_local():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "task_id": "t-1",
            "task_type": "matmul",
            "input_size_bytes": 1024,
            "compute_complexity": 2.5,
            "deadline_ms": 100,
        }
        resp = await ac.post("/offload", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] == "LOCAL"
    assert data["task_id"] == "t-1"
