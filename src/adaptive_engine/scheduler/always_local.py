from adaptive_engine.api.schemas import Decision, OffloadRequest
from adaptive_engine.scheduler.base import Scheduler


class AlwaysLocalScheduler(Scheduler):
    async def schedule(self, req: OffloadRequest) -> Decision:
        return Decision.LOCAL
