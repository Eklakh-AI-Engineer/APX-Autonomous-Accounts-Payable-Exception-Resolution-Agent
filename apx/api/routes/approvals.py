from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
import logging

from apx.api.schemas import ApprovalResponse, ApproveRequest, RejectRequest, ErrorResponse
from apx.application.services import get_approval_service
from apx.api.middleware import get_current_user_groups, get_current_user_id

router = APIRouter()

logger = logging.getLogger("apx.api.routes.approvals")


@router.get(
    "/{case_id}/approval",
    response_model=ApprovalResponse,
    responses={
        404: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
    },
)
async def get_approval(
    case_id: str,
    request: Request,
):
    """Get approval for a case."""
    service = get_approval_service()
    result = service.get_approval(case_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Approval for case {case_id} not found",
        )
    return ApprovalResponse(**result)


@router.post(
    "/{case_id}/approve",
    response_model=ApprovalResponse,
    responses={
        404: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    },
)
async def approve_case(
    case_id: str,
    request: Request,
    approve_request: ApproveRequest,
):
    """Approve a case."""
    approver_id = get_current_user_id(request)
    if not approver_id:
        raise HTTPException(status_code=403, detail="Authenticated approver identity is required")
    service = get_approval_service()
    logger.info("Approving case: %s", case_id)
    try:
        result = service.approve_case(
            case_id, approver_id, approve_request.notes, get_current_user_groups(request)
        )
        return ApprovalResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/{case_id}/reject",
    response_model=ApprovalResponse,
    responses={
        404: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    },
)
async def reject_case(
    case_id: str,
    request: Request,
    reject_request: RejectRequest,
):
    """Reject a case."""
    approver_id = get_current_user_id(request)
    if not approver_id:
        raise HTTPException(status_code=403, detail="Authenticated approver identity is required")
    service = get_approval_service()
    try:
        result = service.reject_case(
            case_id, approver_id, reject_request.notes, get_current_user_groups(request)
        )
        return ApprovalResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
