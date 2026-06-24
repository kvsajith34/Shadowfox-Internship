"""Metrics response schema."""
from typing import Dict, Any, List
from pydantic import BaseModel


class MetricsResponseData(BaseModel):
    totalFiles: int = 0
    filesGrowth: float = 0.0
    queriesHandled: int = 0
    avgFaithfulness: float = 0.0
    hallucinations: int = 0
    providerStatus: Dict[str, str] = {}
    evaluationTrend: List[float] = []
    ragPerformance: Dict[str, float] = {}
    safetyAudit: Dict[str, int] = {}
