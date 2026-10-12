# Approval and execution boundary

## Current verified-by-inspection scope

The code separates recommendation/guardrail checks from action execution, but the current human approval path is not suitable for external financial execution.

`POST /cases/{case_id}/approve` accepts an `approver_id` in the request body. API keys are mapped to roles rather than authenticated person identifiers. The service records that caller-supplied string, does not verify it against `required_approvers`, and does not enforce requester/approver separation. `Phase4Pipeline` can also turn pending approvals into `APPROVED` based on the `DEV` retrieval profile. These are authorization defects, not documentation-only limitations.

## Required controls before enabling an external action adapter

- Resolve the human subject from a trusted identity provider; never trust the body to name the approver.
- Bind an approval to invoice/case, exact action type and canonical parameters, policy version, and evidence digest.
- Enforce eligible approver, requester separation, expiry and revocation at the execution boundary.
- Recompute or verify the authorization binding immediately before dispatch.
- Fail closed for absent, stale, mismatched, or uncertain approval state.
- Remove profile/environment-driven auto-approval from the production-capable code path. Test-only behavior must be explicit and unable to share production credentials or adapters.
- Persist decision and execution transitions transactionally and record immutable audit evidence.

Until these changes are implemented and tested with authenticated identities, keep external financial actions disabled. Mock adapter behavior is not an ERP sandbox verification.

The current implementation accepts a configured approver API key in the form `key:approver:subject` via `APX_API_API_KEYS`; approval endpoints use that configured subject and ignore the request body's `approver_id`. The initiating case-processing identity is not yet persisted, so requester separation is not fully established.
