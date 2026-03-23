from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class ReactionType(str, Enum):
    like = "like"
    dislike = "dislike"
    report = "report"


class CommentReactionCounts(BaseModel):
    like: int = 0
    dislike: int = 0
    report: int = 0


class CommentReactionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor_key: str
    reaction_type: ReactionType


class CommentReactionResponse(BaseModel):
    comment_id: str
    counts: CommentReactionCounts
    user_reaction: ReactionType | None = None

