from __future__ import annotations

import json
import logging
import traceback
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from apx.api.middleware import get_current_role, get_current_user_id, get_request_id
from apx.api.schemas import (
    ErrorResponse,
    InvoiceLineResponse,
    InvoiceRequest,
    InvoiceResponse,
    InvoiceSubmitResponse,
    ProcessResponse,
    ValidationErrorResponse,
)
from apx.application.services import get_invoice_service
from apx.observability.processing_diagnostics import (
    get_processing_stage,
    set_processing_stage,
)
from apx.persistence import CaseRepository
from apx.persistence.database import get_session_factory

router = APIRouter()
logger = logging.getLogger("apx.api.routes.invoices")


@router.post(
    "",
    response_model=InvoiceSubmitResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
    },
)
async def submit_invoice(
    request: Request,
    invoice_request: InvoiceRequest,
    idempotency_key: Optional[str] = Query(None, alias="idempotency_key"),
):
    """Submit an invoice for processing."""
    # Check idempotency
    factory = get_session_factory()
    with factory() as session:
        from sqlalchemy import select

        from apx.persistence.models import CaseORM
        existing = session.execute(
            select(CaseORM).where(CaseORM.idempotency_key == idempotency_key)
        ).scalar_one_or_none()
        if existing:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "invoice_id": existing.invoice_id,
                    "case_id": str(existing.case_id),
                    "status": "already_exists",
                    "message": f"Invoice already processed with idempotency key {idempotency_key}",
                },
            )

    service = get_invoice_service()

    try:
        # Convert request to domain invoice
        invoice = service._request_to_invoice(invoice_request)
        result = service.submit_invoice(invoice, idempotency_key)
        return InvoiceSubmitResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse,
    responses={
        404: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
    },
)
async def get_invoice(
    invoice_id: str,
    request: Request,
):
    """Get invoice by ID with case status."""
    service = get_invoice_service()
    result = service.get_invoice(invoice_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found",
        )
    return InvoiceResponse(**result)


@router.post(
    "/{invoice_id}/process",
    response_model=ProcessResponse,
    responses={
        404: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def process_invoice(
    invoice_id: str,
    request: Request,
    idempotency_key: Optional[str] = Query(None, alias="idempotency_key"),
):
    """Process an invoice through the full APX pipeline."""
    requester_id = get_current_user_id(request)
    if not requester_id:
        raise HTTPException(status_code=403, detail="Authenticated requester identity is required")
    service = get_invoice_service()

    try:
        set_processing_stage("invoice_service_call")
        result = service.process_invoice(invoice_id, idempotency_key, requested_by=requester_id)
        set_processing_stage("response_serialization")
        return ProcessResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as exc:
        # Log only exception class and traceback frame coordinates. Do not put
        # exception messages, SQL, source lines, or local variables in logs or
        # public responses.
        frames = [
            {"file": frame.filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1],
             "line": frame.lineno,
             "function": frame.name}
            for frame in traceback.extract_tb(exc.__traceback__)
        ]
        request_id = getattr(request.state, "request_id", get_request_id())
        correlation_id = getattr(request.state, "correlation_id", request_id)
        logger.error(
            json.dumps(
                {
                    "event": "invoice.processing_failed",
                    "exception_type": type(exc).__name__,
                    "stage": get_processing_stage(),
                    "request_id": request_id,
                    "correlation_id": correlation_id,
                    "traceback": frames,
                },
                separators=(",", ":"),
            )
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_error",
                "message": "Invoice processing failed. Contact support with the request ID.",
                "request_id": request_id,
            },
        )
