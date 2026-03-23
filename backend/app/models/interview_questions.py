from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class InterviewQuestionCategory(str, Enum):
    technical = "technical"
    behavioral = "behavioral"
    general = "general"


class InterviewQuestionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: InterviewQuestionCategory
    topic: str = Field(..., min_length=2, max_length=120)
    question: str = Field(..., min_length=3, max_length=1000)


class InterviewQuestionResponse(BaseModel):
    id: str
    company_id: str
    category: InterviewQuestionCategory
    topic: str
    question: str
    created_at: datetime

