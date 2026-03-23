from __future__ import annotations

from typing import Protocol

from backend.app.models.comments import CommentCreateRequest, CommentResponse
from backend.app.models.reports import ReportCreateRequest, ReportResponse
from backend.app.models.companies import CompanyRatingSummary
from backend.app.models.interview_questions import (
    InterviewQuestionCreateRequest,
    InterviewQuestionResponse,
)
from backend.app.models.reactions import (
    CommentReactionCreateRequest,
    CommentReactionResponse,
)


class CommentStore(Protocol):
    def init(self) -> None: ...

    def create_comment(self, *, company_id: str, request: CommentCreateRequest, display_name: str) -> CommentResponse: ...

    def list_comments(
        self, *, company_id: str, limit: int = 50, actor_key: str | None = None
    ) -> list[CommentResponse]: ...

    def create_report(
        self, *, comment_id: str, request: ReportCreateRequest
    ) -> ReportResponse: ...

    def get_company_rating_summary(self, *, company_id: str) -> CompanyRatingSummary: ...

    def create_interview_question(
        self, *, company_id: str, request: InterviewQuestionCreateRequest
    ) -> InterviewQuestionResponse: ...

    def list_interview_questions(
        self, *, company_id: str, limit: int = 50, category: str | None = None
    ) -> list[InterviewQuestionResponse]: ...

    def create_comment_reaction(
        self, *, comment_id: str, request: CommentReactionCreateRequest
    ) -> CommentReactionResponse: ...

