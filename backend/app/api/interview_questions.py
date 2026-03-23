from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.concurrency import run_in_threadpool

from backend.app.models.interview_questions import (
    InterviewQuestionCategory,
    InterviewQuestionCreateRequest,
    InterviewQuestionResponse,
)


router = APIRouter()


@router.get("/companies/{company_id}/questions", response_model=list[InterviewQuestionResponse])
async def list_company_questions(
    raw_request: Request,
    company_id: str,
    limit: int = 50,
    category: InterviewQuestionCategory | None = None,
) -> list[InterviewQuestionResponse]:
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")

    store = raw_request.app.state.store
    category_str = category.value if category is not None else None
    return await run_in_threadpool(
        store.list_interview_questions, company_id=company_id, limit=limit, category=category_str
    )


@router.post(
    "/companies/{company_id}/questions",
    response_model=InterviewQuestionResponse,
    status_code=201,
)
async def create_company_question(
    company_id: str,
    request: InterviewQuestionCreateRequest,
    raw_request: Request,
) -> InterviewQuestionResponse:
    store = raw_request.app.state.store
    return await run_in_threadpool(
        store.create_interview_question, company_id=company_id, request=request
    )

