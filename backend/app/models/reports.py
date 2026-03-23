from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReportCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(..., min_length=3, max_length=500)


class ReportResponse(BaseModel):
    id: str
    comment_id: str
    company_id: str
    reason: str
    status: str
    created_at: datetime

