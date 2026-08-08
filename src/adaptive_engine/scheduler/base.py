from abc import ABC, abstractmethod

from adaptive_engine.api.schemas import Decision, OffloadRequest


class Scheduler(ABC):
    @abstractmethod
    async def schedule(self, req: OffloadRequest) -> Decision: ...
