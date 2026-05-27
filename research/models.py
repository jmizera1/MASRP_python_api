from pydantic import BaseModel
from typing import List


class MetricValue(BaseModel):
    metric_id: int
    value: float


class ResultRow(BaseModel):
    platform_name: str
    workload: str
    number_of_agents: int
    number_of_repetitions: int
    number_of_containers: int
    message_size: int
    group_size: int
    ram: float
    vcpu: str
    metrics: List[MetricValue]


class ExperimentPayload(BaseModel):
    name: str
    description: str
    selected_metric_ids: List[int]
    rows: List[ResultRow]
    user_id: int = 0
