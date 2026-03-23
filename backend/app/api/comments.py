from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.concurrency import run_in_threadpool

from backend.app.models.comments import CommentCreateRequest, CommentResponse
from backend.app.models.companies import CompanyRatingSummary
from backend.app.models.reactions import (
    CommentReactionCreateRequest,
    CommentReactionResponse,
)
from backend.app.models.reports import ReportCreateRequest, ReportResponse
from backend.app.services.anon_names import pick_anon_name
from backend.app.services.moderation import contains_profanity


router = APIRouter()


@router.get("/companies/{company_id}/comments", response_model=list[CommentResponse])
async def list_company_comments(
    raw_request: Request, company_id: str, limit: int = 50, actor_key: str | None = None
) -> list[CommentResponse]:
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")

    store = raw_request.app.state.store
    return await run_in_threadpool(
        store.list_comments, company_id=company_id, limit=limit, actor_key=actor_key
    )


@router.post("/companies/{company_id}/comments", response_model=CommentResponse, status_code=201)
async def create_company_comment(
    company_id: str, request: CommentCreateRequest, raw_request: Request
) -> CommentResponse:
    settings = raw_request.app.state.settings

    if contains_profanity(request.message):
        raise HTTPException(
            status_code=400,
            detail="Yorum içeriği reddedildi (hakaret/küfür içerebilir).",
        )

    display_name = request.display_name.strip() if request.display_name else ""
    if not display_name:
        display_name = pick_anon_name(settings)

    store = raw_request.app.state.store
    return await run_in_threadpool(
        store.create_comment, company_id=company_id, request=request, display_name=display_name
    )


@router.post("/comments/{comment_id}/reports", response_model=ReportResponse, status_code=201)
async def report_comment(comment_id: str, request: ReportCreateRequest, raw_request: Request) -> ReportResponse:
    store = raw_request.app.state.store
    try:
        return await run_in_threadpool(store.create_report, comment_id=comment_id, request=request)
    except ValueError as e:
        if str(e) == "comment_not_found":
            raise HTTPException(status_code=404, detail="Comment not found")
        if str(e) == "actor_key_required":
            raise HTTPException(status_code=400, detail="actor_key is required")
        raise


@router.post(
    "/comments/{comment_id}/reactions",
    response_model=CommentReactionResponse,
    status_code=201,
)
async def react_comment(
    comment_id: str, request: CommentReactionCreateRequest, raw_request: Request
) -> CommentReactionResponse:
    store = raw_request.app.state.store
    try:
        return await run_in_threadpool(
            store.create_comment_reaction, comment_id=comment_id, request=request
        )
    except ValueError as e:
        if str(e) == "comment_not_found":
            raise HTTPException(status_code=404, detail="Comment not found")
        raise


@router.get(
    "/companies/{company_id}/rating-summary",
    response_model=CompanyRatingSummary,
)
async def get_company_rating_summary(
    company_id: str, raw_request: Request
) -> CompanyRatingSummary:
    store = raw_request.app.state.store
    return await run_in_threadpool(store.get_company_rating_summary, company_id=company_id)

