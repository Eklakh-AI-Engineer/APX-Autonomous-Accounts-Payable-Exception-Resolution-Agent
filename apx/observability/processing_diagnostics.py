"""Request-local stage tracking for sanitized invoice-processing diagnostics."""

from contextvars import ContextVar

_processing_stage: ContextVar[str] = ContextVar(
    "apx_processing_stage", default="request_received"
)


def set_processing_stage(stage: str) -> None:
    """Set the current invoice-processing stage for this request context."""
    _processing_stage.set(stage)


def get_processing_stage() -> str:
    """Return the current request's invoice-processing stage."""
    return _processing_stage.get()
