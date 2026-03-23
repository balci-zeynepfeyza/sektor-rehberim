from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class CompanyRatingSummary(BaseModel):
    company_id: str
    rating_count: int = Field(ge=0)

    avg_difficulty: Optional[float] = Field(default=None, ge=1, le=5)
    avg_balance: Optional[float] = Field(default=None, ge=1, le=5)
    avg_office: Optional[float] = Field(default=None, ge=1, le=5)

    # Overall = (avg_difficulty + avg_balance + avg_office) / 3
    avg_overall: Optional[float] = Field(default=None, ge=1, le=5)

