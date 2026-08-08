from sqlalchemy import Column, DateTime, Float, Integer, String, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class LinkMetric(Base):
    __tablename__ = "link_metrics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    bandwidth_mbps = Column(Float, nullable=False)
    rtt_ms = Column(Float, nullable=False)
    loss = Column(Float, nullable=False)
    sinr_db = Column(Float, nullable=False)


class DecisionLog(Base):
    __tablename__ = "decision_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    task_id = Column(String, nullable=False)
    task_type = Column(String, nullable=False)
    input_size_bytes = Column(Integer, nullable=False)
    compute_complexity = Column(Float, nullable=False)
    deadline_ms = Column(Integer, nullable=False)
    decision = Column(String, nullable=False)
    predicted_latency_ms = Column(Float, nullable=False)
    predicted_energy_mj = Column(Float, nullable=False)
