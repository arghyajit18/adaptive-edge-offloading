import asyncio
from adaptive_engine.network.ns3_wrapper import Ns3Wrapper
from adaptive_engine.metrics.store import MetricsStore
from sqlalchemy.ext.asyncio import async_sessionmaker
class LinkMonitor:
    def init(self, wrapper: Ns3Wrapper, sessionmaker: async_sessionmaker,
                 store_interval_sec: float = 1.0):
        self._wrapper = wrapper
        self._store = MetricsStore(sessionmaker)
        self.interval = store_interval_sec
        self.task: asyncio.Task | None = None
        self._latest = None
async def run(self) -> None:
    self._task = asyncio.create_task(self._loop())

async def _loop(self) -> None:
    async for metric in self._wrapper.metrics():
        self._latest = metric
        await self._store.add_link_metric(**metric)
        await asyncio.sleep(self._interval)

def current(self) -> dict | None:
    return self._latest

async def stop(self) -> None:
    if self._task:
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
