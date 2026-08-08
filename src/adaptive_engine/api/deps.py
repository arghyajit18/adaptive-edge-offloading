"""Shared dependency helpers – breaks the circular import between main & routes."""

from adaptive_engine.scheduler.always_local import AlwaysLocalScheduler  # fallback
from adaptive_engine.scheduler.base import Scheduler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# placeholders – filled in main.py during lifespan start‑up
_sessionmaker: async_sessionmaker[AsyncSession] | None = None
_scheduler: Scheduler | None = None


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    if _sessionmaker is None:
        raise RuntimeError("Sessionmaker not initialised")
    return _sessionmaker


def get_scheduler() -> Scheduler:
    """Return the real scheduler if it exists, otherwise a harmless LOCAL‑only one."""
    if _scheduler is None:
        # This path is only hit in tests that don't start the full lifespan.
        return AlwaysLocalScheduler()
    return _scheduler
