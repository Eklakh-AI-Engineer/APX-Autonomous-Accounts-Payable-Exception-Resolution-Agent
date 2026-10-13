"""Canonical fingerprints for approval and execution integrity checks."""
from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def evidence_snapshot_digest(evidence_set: Any) -> str:
    if evidence_set is None:
        return canonical_digest([])
    snapshot = [
        item.model_dump(mode="json")
        for item in sorted(
            evidence_set.validated_evidence,
            key=lambda item: (item.evidence.evidence_id, item.rank),
        )
    ]
    return canonical_digest(snapshot)


def action_fingerprint(action_plan: Any, evidence_digest: str, policy_fingerprint: str) -> str:
    return canonical_digest(
        {
            "action_id": str(action_plan.action_id),
            "invoice_id": str(action_plan.target),
            "action_type": getattr(action_plan.action_type, "value", action_plan.action_type),
            "parameters": action_plan.parameters,
            "idempotency_key": action_plan.idempotency_key,
            "evidence_digest": evidence_digest,
            "policy_fingerprint": policy_fingerprint,
        }
    )


def policy_fingerprint(guardrail: Any) -> str:
    config = getattr(guardrail, "config", None)
    if config is None:
        raise ValueError("Guardrail policy is unavailable")
    return canonical_digest(config.model_dump(mode="json"))
