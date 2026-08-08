from adaptive_engine.scheduler.base import Scheduler
from adaptive_engine.api.schemas import OffloadRequest, Decision
class AlwaysLocalScheduler(Scheduler):
    async def schedule(self, req: OffloadRequest) -> Decision:
        return Decision.LOCAL
