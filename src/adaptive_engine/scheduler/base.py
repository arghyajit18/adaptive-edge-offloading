from abc import ABC, abstractmethod
from adaptive_engine.api.schemas import OffloadRequest, Decision
class Scheduler(ABC):
    @abstractmethod
    async def schedule(self, req: OffloadRequest) -> Decision:
        ...
