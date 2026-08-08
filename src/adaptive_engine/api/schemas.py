from pydantic import BaseModel, Field
from enum import Enum
from typing import Literal
class TaskType(str, Enum):
    IMAGE = "image"
    MATMUL = "matmul"
    ML_INFERENCE = "ml_inference"
class OffloadRequest(BaseModel):
    task_id: str
    task_type: TaskType
    input_size_bytes: int = Field(gt=0)
    compute_complexity: float = Field(gt=0)
    deadline_ms: int = Field(gt=0)
class Decision(str, Enum):
    LOCAL = "LOCAL"
    OFFLOAD = "OFFLOAD"
class OffloadResponse(BaseModel):
    task_id: str
    decision: Decision
    predicted_latency_ms: float
    predicted_energy_mj: float
