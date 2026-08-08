import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from adaptive_engine.config import settings
from adaptive_engine.metrics.models import Base
from adaptive_engine.metrics.store import MetricsStore
from adaptive_engine.network.link_monitor import LinkMonitor
from adaptive_engine.network.ns3_wrapper import Ns3Wrapper
from adaptive_engine.scheduler.base import Scheduler
from adaptive_engine.scheduler.adaptive import AdaptiveScheduler
from adaptive_engine.api.routes import health, offload
from adaptive_engine.api import deps          # ← new import


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1️⃣ engine & sessionmaker
    engine = create_async_engine(settings.db.url, echo=settings.db.echo, future=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # 2️⃣ create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 3️⃣ store in shared deps **before** any route can be called
    deps._sessionmaker = sessionmaker

    # 4️⃣ ns‑3 wrapper + link monitor
    ns3_wrapper = Ns3Wrapper()
    await ns3_wrapper.start()

    link_monitor = LinkMonitor(
        ns3_wrapper,
        deps.get_sessionmaker,
        store_interval_sec=settings.link_monitor.store_interval_sec,
    )
    asyncio.create_task(link_monitor.run())

    # 5️⃣ scheduler – now safe to expose
    scheduler = AdaptiveScheduler(link_monitor)
    deps._scheduler = scheduler

    # expose for routes that need direct access
    app.state.link_monitor = link_monitor

    yield

    # shutdown
    await link_monitor.stop()
    await ns3_wrapper.stop()
    await engine.dispose()


app = FastAPI(title="Adaptive Edge‑Offloading Engine", lifespan=lifespan)
app.include_router(health.router)
app.include_router(offload.router)
