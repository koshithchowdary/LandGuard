# LandGuard production implementation status

Updated: 2026-10-29

## Implemented in this branch
- Provider registry for Telangana Bhu Bharati and AP MeeBhoomi/Webland with explicit blocked status; no undocumented endpoints are called.
- Allow-listed normalized snapshots, deterministic SHA-256 fingerprints, field-level comparisons and safe check-result states.
- Retrieval failures produce `source_unavailable`, never a false “no change”.
- SQLite persistence for monitoring preferences, owner-provided record snapshots, check outcomes and audit history; a Streamlit page exposes preferences, connector status and history. This is still single-demo-account/local storage, not production multi-tenant infrastructure.
- Notification channel readiness checks for email, SMS and WhatsApp environment variables. This is configuration detection only; it does not send messages.
- `.env.example` lists expected secret names without real credentials.
- Unit tests for hashing, allow-listing, changes, failure handling, government connector status, and monitoring-store persistence (tests added; execution not yet verified).

## Not implemented / not production-ready
- Government APIs: blocked pending written access, specs, sandbox and credentials.
- Actual email/SMS/WhatsApp provider SDKs and verified delivery: not implemented.
- Production authentication/MFA, PostgreSQL migrations, queue/scheduler, tenant authorization, payment integration, secure upload scanning, backups, deployment and monitoring: not implemented.
- Existing Streamlit MVP still uses seeded demo users and local SQLite. Do not expose it as a production multi-tenant service.

## Required government access pack (for BOTH states)
Request from the respective Revenue Department / authorized system operator:
1. Written authorization for commercial owner-authorized monitoring.
2. Official API specification/OpenAPI, sandbox URL and test account.
3. Auth scheme, scopes, client credentials, key rotation and IP allow-list requirements.
4. Permitted identifiers/fields, stable parcel IDs and data retention/display rules.
5. Change feed/webhook/history availability, update cadence, quotas/rate limits and retry rules.
6. Support/SLA contact, incident escalation and change-management policy.
7. Approved synthetic test records and acceptance criteria.

Public citizen portals are not API contracts. Do not automate CAPTCHA, replay private endpoints, or collect portal passwords/OTPs.

## Required secrets / services
- App signing/session secret in managed secret storage.
- Official government connector credentials per state, only after approval.
- Email provider API key and verified sender/domain.
- SMS provider credentials and approved sender ID/template configuration as applicable.
- WhatsApp Business provider credentials, sender/phone-number ID, approved templates and opt-in records as applicable.
- Managed PostgreSQL connection string; Redis/queue URL if background workers are introduced.
- Object storage bucket/region and restricted credentials for property documents.
- Error monitoring DSN and deployment-specific environment settings.

Never put actual secrets in GitHub issues, source code, logs, or user-visible alerts. Rotate any credential that is accidentally committed.

## Infrastructure recommendation
- Web frontend/API service + worker service; managed PostgreSQL; managed Redis/queue; encrypted object storage; secret manager; TLS/domain; email/SMS/WhatsApp vendors; error monitoring; daily encrypted backups and tested restore.
- Separate development, staging and production environments.
- Alert on job failures, stale source data, delivery failures and elevated error rates.
- Apply tenant isolation, least privilege, audit logging, consent/revocation, retention/deletion and incident response before public launch.

## Acceptance gates before calling a connector “live”
- Provider confirms authorization and field semantics in writing.
- Sandbox contract tests pass; authentication, rate limits and retries are verified.
- Snapshot and change tests pass against provider-approved fixtures.
- Shadow mode is reconciled with manual official records.
- Notification delivery and opt-out tests pass.
- Customer UI exposes source, last successful check and freshness; failures remain visible.
- Security/privacy review and restore drill complete.
