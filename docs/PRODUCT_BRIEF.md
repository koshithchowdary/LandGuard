# LANDGUARD — Product Brief

**Tagline:** Your property. Watched locally.

**Product:** A property-protection and monitoring service for owners who cannot regularly visit their land or home, starting with out-of-city owners and NRIs with properties in Nellore and Hyderabad.

## The customer problem

Owners often depend on occasional family visits, brokers, guards, or manual portal searches to know what is happening to a property. Information is fragmented across documents, field observations, and government record portals. The owner needs a clear, time-stamped view of what was checked, what changed, what could not be checked, and what action is recommended.

## Product promise

LandGuard brings property documents, recurring physical inspections, evidence, record snapshots, change history, and service requests into one Property Passport. It reports observations with evidence and clearly distinguishes verified data from estimates, owner-supplied documents, and unavailable sources.

LandGuard does **not** promise prevention of encroachment, certify title, replace a lawyer or surveyor, or claim government monitoring unless an authorized source check actually occurred.

## Initial customer

- People living in another city who own plots or houses in Nellore or Hyderabad.
- NRIs who need trusted local visibility and evidence.
- Families managing inherited or long-held property.

## MVP journeys

1. **Property Passport:** property profile, identifiers, documents checklist, and monitoring preferences.
2. **Record snapshot comparison:** owner enters fields from an existing record; LandGuard stores a normalized baseline and compares later supplied snapshots.
3. **Field inspection:** a local agent captures observations, time, location, notes, and evidence; suspicious findings require human review.
4. **Change and alert history:** show what was observed, the source, timestamp, evidence, severity, and next action.
5. **Service coordination:** request a site visit, boundary check, cleaning, or other local service.
6. **Operations view:** admins review pending inspections, evidence, alerts, source failures, and service requests.

## AI agent responsibilities

- Extract candidate property identifiers and record fields from customer-authorized documents, with a human confirmation step.
- Normalize fields and compare new authorized snapshots with prior snapshots.
- Summarize differences in plain language, cite the source and date, and recommend a human verification step.
- Analyze inspection images only as potential observations, never as conclusive proof of ownership, encroachment, or legal status.
- Explain source failures and uncertainty.

## Source-of-truth rules

- Customer-supplied document = owner-provided evidence, not independently verified.
- Official provider response = source-backed observation with retrieval timestamp and reference.
- Satellite imagery = physical-change signal only; revisit cadence and resolution vary and cannot establish legal ownership.
- Failed retrieval, CAPTCHA, unavailable portal, expired credentials, or parsing errors = **check failed / status unknown**, never “no change.”
- A difference is a potential change requiring review, not automatically fraud or an illegal transfer.

## Data-source strategy

1. Seek commercial API/MCP access and terms from Landeed; explicitly confirm AP and Telangana coverage, recurring retrieval rights, change feeds/webhooks, retention rules, and customer-facing redistribution rights.
2. Seek official AP and Telangana access in parallel.
3. Do not bypass authentication/CAPTCHA, scrape at scale, or represent public portal access as a production integration.
4. Keep source adapters replaceable and disabled until credentials, terms, and tests are in place.

## Product status — 29 October 2026

**Implemented in the current feature branch:** monitoring provider status registry, allow-listed normalized snapshot hashing and diffs, SQLite preference/snapshot/check history, source-unavailable semantics, notification configuration checks, and a Streamlit monitoring page. This branch includes a manual record-snapshot workflow for comparing owner-supplied details.

**Not yet production-ready:** live government record retrieval, automatic scheduling, satellite imagery provider, OCR/document extraction, outbound email/SMS/WhatsApp delivery, production authentication and tenant isolation, PostgreSQL, secure object storage, deployment/monitoring, and completed automated test execution.

## Definition of a safe pilot

- One named property owner has explicitly authorized the records and inspection.
- Every result records source, time, reference, and whether it is owner-supplied or independently retrieved.
- Source outages and parsing uncertainty are visible and never converted into “all clear.”
- Changes are reviewed by a person before high-impact customer alerts.
- Customer data is tenant-isolated, access-controlled, backed up, and subject to a documented retention/deletion policy.
- Test suite passes; secrets are stored outside source control; alert delivery is tested end to end.
- The customer is told exactly what is and is not monitored.

## Success metrics for the first pilot

- Percentage of scheduled inspections completed with usable evidence.
- Time from observation to customer notification.
- Percentage of alerts accepted after human review.
- False-positive rate for physical-change flags.
- Percentage of record checks completed successfully versus source unavailable.
- Customer retention and willingness to pay after a 60–90 day pilot.

## Suggested rollout

**Stage 1 — Evidence-first pilot:** Property Passport, owner-provided snapshots, manual site visits, and transparent history.

**Stage 2 — Authorized data connectors:** Landeed or government integrations after access and recurring-check terms are confirmed.

**Stage 3 — Reliable operations:** scheduled jobs, durable queues, delivery providers, multi-tenant backend, secure storage, monitoring, and support workflows.

**Stage 4 — Scaled property intelligence:** imagery comparison, human-reviewed AI findings, service partners, and additional districts/states.
