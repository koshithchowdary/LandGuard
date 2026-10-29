# LandGuard monitoring product — informed by public Landeed materials

Updated: 2026-10-29

## Publicly described competitor capabilities

Landeed publicly describes a Telangana land-monitoring service based on periodic satellite imagery. Its page says imagery updates depend on satellite passes and typically refresh every few weeks. It describes plot boundary overlays, area/perimeter measurements and observations such as disturbance, fencing, encroachment or construction.

Landeed separately describes property-record retrieval APIs and document procurement. Public materials do not prove that its satellite-monitoring service is a daily government-revenue-record polling product, nor disclose the private implementation or source contracts.

References:
- https://web.landeed.com/products/telangana/land-monitoring-services
- https://www.landeed.com/products/retrieval-procurement
- https://www.landeed.com/products/api-mcp

## LandGuard product design

Offer two independent monitoring tracks on a registered property:

1. **Physical plot monitoring**
   - Save plot coordinates/polygon and owner-approved boundary.
   - Obtain imagery only from a licensed satellite imagery provider with permitted monitoring use.
   - Compare suitable imagery dates, with cloud/quality checks and a baseline.
   - Report visible possible changes with image date, resolution/quality and confidence.
   - Do not promise daily imagery; show the actual last-observed date and expected refresh range.
   - Human review for high-impact findings. Satellite imagery is not a legal boundary survey or proof of encroachment.

2. **Government-record monitoring**
   - Use an approved API/feed/provider contract or explicit manual verification.
   - Keep separate state-specific source coverage, retrieval timestamps and freshness.
   - Daily scheduling is a target cadence only where the provider permits it and can actually return fresh records.
   - A source failure means source_unavailable, never no_change.
   - Don't bypass CAPTCHA or authentication or rely on undocumented endpoints.

3. **Optional document retrieval**
   - Let customers request an EC, registered deed, mutation extract or other supported document.
   - Be transparent whether the document is retrieved automatically, manually procured, pending, or unavailable.
   - Display the source, office/document identifiers and retrieved-at timestamp when permitted.

## Current implementation status

The existing monitoring foundation in `monitoring/` supports normalized snapshots, hashes, field-level comparisons and explicit blocked government connector states. This document is product architecture, not a satellite imagery integration.

No satellite provider, government record provider, notification vendor, or paid API has been connected by this change.

## Required partner decisions

### Satellite imagery
- Provider, legal use rights, commercial monitoring and alerting rights
- AOI/polygon support, image resolution, revisit expectations and historical imagery
- Cloud/shadow filtering, image metadata and change-detection API availability
- Price per area, image/task and minimum commitment
- Storage, caching, derived-output, deletion and customer-sharing terms
- Provider API credentials and sandbox/test imagery

### Government records
- Written permission for commercial owner-authorized monitoring
- Official API spec/sandbox/credentials, or a vetted data provider contract
- Supported identifiers, permitted fields, polling quotas, freshness and change-feed support

### Alerts
- Email, SMS and WhatsApp provider contracts and credentials
- Customer consent/opt-out, template approval where required, retries and delivery logs

## Customer-facing promise

Use language such as: “LandGuard checks available sources on the schedule they support and alerts you when a verified change is observed.” Do not promise daily government changes or daily satellite coverage unless actual provider contracts and measured service performance support that promise.
