# Rollback procedure

No deployment or rollback artifact has been exercised. Adapt this generic checklist to the selected deployment platform before release.

1. Stop external action dispatch first; preserve pending and unknown-outcome records.
2. Capture release SHA, configuration revision, migration version, logs and in-flight action identifiers.
3. Roll application instances back to the last known-good immutable artifact using the provider's reviewed procedure.
4. Do not automatically reverse financial actions. Reconcile each external action against the ERP before retry or compensation.
5. Restore database state only under the verified backup/restore runbook; do not drop financial records.
6. Verify health, authentication, approval controls, dispatch state and audit continuity. Record evidence and incident owner.

Provider-specific commands, triggers, RTO and recovery ownership remain release prerequisites.
