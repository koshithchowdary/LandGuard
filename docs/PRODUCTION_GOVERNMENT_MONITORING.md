# LandGuard AI — Government Land-Record Monitoring Production Plan

## Product promise

LandGuard monitors owner-authorized land-record sources, detects verified changes when source access permits, and notifies owners with the source, timestamp, observed difference, confidence, and next step. It does not guarantee prevention of fraud, prove title, or replace a lawyer or revenue official.

## Important integration reality

As of 29 October 2026, the public official portal pages reviewed expose citizen-facing land-information and application-status workflows. The reviewed public pages do not document a general-purpose, public developer API, change feed, webhook, or subscription service for third-party monitoring.

- Telangana: Bhu Bharati is the current Revenue Department land-record portal; do not build a new integration against legacy Dharani URLs without confirmation from the department.
- Andhra Pradesh: MeeBhoomi is the citizen-facing land-record portal. NIC Andhra Pradesh describes Webland as the workflow-backed land-record management system integrated with MeeBhoomi and other departmental services.

**Do not represent either integration as live until the department/vendor has supplied written authorization, API documentation, a sandbox, credentials, permitted fields, rate limits, and a support contact.** Do not bypass CAPTCHA, authentication, access controls, or scrape at scale. Use manual user-initiated checks or owner-provided official documents as a clearly labelled interim workflow.

## Target architecture

1. Web/API application: customer accounts, MFA, property registry, consent, subscription and notification preferences.
2. PostgreSQL: tenants, users, properties, parcel identifiers, source connections, check runs, normalized snapshots, change events, alert delivery attempts, audit logs.
3. Provider adapters: one adapter per state/source with an explicit capability declaration (official API, scheduled polling, manual upload, or unavailable). Never assume provider capabilities are identical.
4. Scheduler/worker queue: scheduled checks, retries with backoff, idempotency keys, rate limiting, dead-letter queue and health checks.
5. Change detection: compare normalized records and hashes; classify field-level changes; deduplicate events; retain original source payloads only as permitted by provider terms and privacy policy.
6. Notification service: email first; SMS/WhatsApp only after consent and provider setup. Delivery status and retries must be tracked.
7. Evidence and audit: append-only audit events, UTC timestamps, source URL/reference, retrieval time, snapshot hash, actor, and reviewer decision. Hashes establish integrity of stored bytes only; they do not prove ownership or the truth of a government record.
8. Admin console: connector health, stale data warnings, failed jobs, alert review, customer support and audit export.

## Data model (minimum)

- users: id, email/phone, auth subject, status, created_at
- properties: id, owner_user_id, state, district, mandal/taluk, village, survey/subdivision, parcel/ULPIN if applicable, owner-supplied reference, created_at
- source_connections: id, property_id, provider, access_mode, consent_id, status, last_success_at, next_check_at, error_code
- record_snapshots: id, connection_id, retrieved_at, source_reference, normalized_json, content_hash, provider_version
- change_events: id, property_id, snapshot_before_id, snapshot_after_id, change_type, severity, confidence, review_status, created_at
- alert_deliveries: id, change_event_id, channel, recipient_ref, status, attempts, delivered_at
- consents: id, user_id, property_id, purpose, terms_version, granted_at, revoked_at
- audit_events: id, actor_id, action, resource_type, resource_id, occurred_at, metadata

Store only necessary personal data. Do not collect Aadhaar numbers or passbook credentials unless there is a lawful, documented necessity and a secure approved flow. Never store OTPs or passwords from government portals.

## Change detection rules

- Compare normalized fields (record status, recorded extent, survey/subdivision, transaction/application status, record timestamp) only when that field is available and its use is authorized.
- Alert only on an observed source change, not on speculation that a fraud has occurred.
- Label events as source_changed, possible_mismatch, source_unavailable, or review_required.
- Include the previous and current values where legally permitted, source link/reference, last checked time, and a neutral next step.
- A failed check is never a “no change” result. Notify internally and show the user that the source could not be checked.
- Require human review for high-impact alerts before describing them as potentially material.

## Provider onboarding checklist

For each of Bhu Bharati and MeeBhoomi/Webland, obtain:
- Written authorization and allowed use for commercial monitoring
- API/OpenAPI documentation and sandbox/test account
- Authentication method and scopes
- Search keys and stable parcel identifiers
- Whether a record-change feed, webhook, or audit/history endpoint exists
- Update frequency, expected freshness, maintenance windows and rate limits
- Data retention, display, caching and redistribution rules
- SLA, incident contact and change-management process
- Security review and test data that contains no real personal data

If no official change feed exists, negotiate an approved polling interface. Until approved, the connector must remain manual_only or not_connected.

## Security and production gates

- OIDC-based authentication; MFA for admins; RBAC for field agents
- Encryption in transit and at rest; managed secrets; no secrets committed to Git
- Tenant isolation and object-level authorization tests
- Consent capture, revocation, retention and deletion workflows
- Rate limiting, CSRF protections, secure uploads, malware scanning
- Structured logs with PII redaction; monitoring and incident response
- Backups and tested restore; database migrations; staging and production separation
- Unit, integration, permission, connector contract, retry, deduplication and notification tests
- Legal review of terms, privacy notice, disclaimers and government-data licensing

## Release sequence

### Phase 0 — Credentials and legal access
Confirm provider access and receive sandbox credentials. No production government connector can be called live without these.

### Phase 1 — Production platform foundation
Replace demo authentication and local SQLite assumptions with managed identity and PostgreSQL; add consent, audit, background jobs, secrets management and email notifications.

### Phase 2 — Connector contract and sandbox
Implement provider adapter interfaces and mocked contract tests. Implement each real adapter only from the provider's approved specification.

### Phase 3 — Shadow mode
Run authorized checks without customer-facing alerts. Compare results with manually verified official records and measure false positives, missed changes and freshness.

### Phase 4 — Limited production
Launch with explicit source coverage and freshness labels, support escalation, alert review and incident monitoring.

## Public references reviewed

- Telangana Bhu Bharati land status: https://www.bhubharati.telangana.gov.in/knowLandStatus
- Telangana Bhu Bharati official portal: https://bhubharati.telangana.gov.in/homePage
- Andhra Pradesh NIC description of Webland and MeeBhoomi integration: https://ap.nic.in/en/publication/presentation-of-state-centre/
- Tirupati District government land-records page: https://tirupati.ap.gov.in/service/land-records/

These public pages establish the existence and role of the portals, not permission to integrate with private/internal APIs or evidence of a public third-party change feed.
