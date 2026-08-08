from adaptive_engine.metrics.models import DecisionLog, LinkMetric
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select


class MetricsStore:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self._sessionmaker = sessionmaker

    async def add_link_metric(
        self, *, bandwidth_mbps: float, rtt_ms: float, loss: float, sinr_db: float
    ) -> LinkMetric:
        async with self._sessionmaker() as session:
            obj = LinkMetric(
                bandwidth_mbps=bandwidth_mbps, rtt_ms=rtt_ms, loss=loss, sinr_db=sinr_db
            )
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def add_decision(
        self,
        *,
        task_id: str,
        task_type: str,
        input_size_bytes: int,
        compute_complexity: float,
        deadline_ms: int,
        decision: str,
        predicted_latency_ms: float,
        predicted_energy_mj: float,
    ) -> DecisionLog:
        async with self._sessionmaker() as session:
            obj = DecisionLog(
                task_id=task_id,
                task_type=task_type,
                input_size_bytes=input_size_bytes,
                compute_complexity=compute_complexity,
                deadline_ms=deadline_ms,
                decision=decision,
                predicted_latency_ms=predicted_latency_ms,
                predicted_energy_mj=predicted_energy_mj,
            )
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def latest_link_metric(self) -> LinkMetric | None:
        async with self._sessionmaker() as session:
            res = await session.execute(
                select(LinkMetric).order_by(LinkMetric.timestamp.desc()).limit(1)
            )
            return res.scalars().first()

    async def fetch_all_decisions(self) -> list[DecisionLog]:
        async with self._sessionmaker() as session:
            res = await session.execute(select(DecisionLog).order_by(DecisionLog.timestamp))
            return res.scalars().all()
