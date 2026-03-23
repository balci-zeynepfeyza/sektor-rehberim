from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field
from backend.app.models.reactions import CommentReactionCounts
from backend.app.models.reactions import ReactionType


class CommentRatings(BaseModel):
    difficulty: int = Field(..., ge=1, le=5)
    balance: int = Field(..., ge=1, le=5)
    office: int = Field(..., ge=1, le=5)


class CommentArea(str, Enum):
    human_resources = "human_resources"
    software = "software"
    product = "product"
    data = "data"
    design = "design"
    operations = "operations"
    other = "other"


class EmploymentStatus(str, Enum):
    employee = "employee"
    not_employee = "not_employee"
    prefer_not_to_say = "prefer_not_to_say"


class CommentCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # When omitted/empty, the server assigns an anonymous name.
    display_name: str | None = Field(default=None, max_length=40)
    area: CommentArea
    employment_status: EmploymentStatus
    area_note: str | None = Field(default=None, max_length=120)
    message: str = Field(..., min_length=1, max_length=2000)
    ratings: CommentRatings


class CommentResponse(BaseModel):
    id: str
    company_id: str
    display_name: str
    area: CommentArea
    employment_status: EmploymentStatus
    area_note: str | None = None
    message: str
    ratings: CommentRatings
    reaction_counts: CommentReactionCounts = Field(default_factory=CommentReactionCounts)
    user_reaction: ReactionType | None = None
    created_at: datetime

