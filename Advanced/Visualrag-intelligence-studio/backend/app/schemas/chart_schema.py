"""Chart analysis request/response schemas."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ChartResponseData(BaseModel):
    chart_type: str = ""
    title: str = ""
    main_trend: str = ""
    highest_value: str = ""
    lowest_value: str = ""
    key_insights: List[str] = []
    possible_limitations: List[str] = []
    data_table: List[Dict[str, Any]] = []
    confidence_score: float = 0.0
    answer: str = ""
    evaluation: Dict[str, Any] = {}
