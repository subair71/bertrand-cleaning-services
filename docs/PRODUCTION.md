# Bertrand production architecture and handover

## Current implementation

The original plain HTML/CSS/JavaScript stack is retained. No framework, backend, real authentication or payment system was introduced. Static HTML entry points provide distinct URLs and initial bilingual SEO metadata. Client navigation uses History API; each URL also opens directly on static hosting.

- `js/app.js`: presentation, routing and interaction controllers.
- `js/i18n.js`: French/English labels and persistent language preference.
- `js/data.js`: existing business content and explicitly labelled sample fixtures.
- `js/logic.js`: request and file validation; HTML escaping.
- `js/repository.js`: data-access adapter, entirely in tab memory.
- `js/config.js`, `js/analytics.js`: external integration boundaries, disabled for demo.
- `scripts/build-pages.py`: reproducible static entry points and sitemap.

Demo requests and object URLs exist in tab memory only, disappear on reload, and are not sent. Real contact actions open WhatsApp or the dialler. No email/SMS notifications are sent. Only language preference is persisted. Admin preview is openly accessible and is not authentication. Users are explicitly told not to enter real personal details or passwords. Gallery demo pairs use one stock photograph with an effect, explicitly labelled as simulated; they must not be represented as cleaning results.

## Content provenance and remaining approvals

Six services retained from the source demo: home/apartment, sofa/carpet, post-construction, windows/glass, deep cleaning, and office/business. Bertrand approval is required for inherited service claims and offers. A provisional typographic wordmark replaces the Al Maher logo. France is confirmed by the client; exact address, service area and hours remain unknown. No map pin or directions are invented. French and English use LTR layouts. Production origin, canonical URLs, hreflang and sitemap must be configured after hosting selection.

All reviews are conspicuously marked as sample. Company must supply approved testimonials, image permissions, real paired photos, exact pin, hours, offer dates/terms and final legal documents before launch. Existing public text referring to trained staff is retained; no new awards, customer totals or years-of-experience claims were created.

## Production API contract (planned, not implemented)

Use the repository interface as an adapter boundary. Production adapter must use a server API; never swap the demo adapter for client-side database admin credentials.

| Endpoint | Permission | Contract |
|---|---|---|
| GET /api/v1/services, /offers, /reviews, /gallery | Public | Published, approved bilingual content only; pagination and cache validators |
| POST /api/v1/quotes | Public with rate limit and spam token | Validated contact/service/address/details, attachment IDs, consent version, idempotency key; 201 only after transaction commit |
| POST /api/v1/bookings | Public with rate limit and spam token | Validated preferred local date/time and timezone Asia/Amman; creates REQUESTED, never confirmed automatically |
| POST /api/v1/uploads/intents | Scoped guest request token | Enforce 5 files × 5 MB; issue short-lived upload capability restricted to exact object and content length |
| POST /api/v1/uploads/:id/complete | Same scoped owner | Validate bytes, decode/re-encode images, malware scan and link clean object to draft request |
| POST /api/v1/auth/login, /logout | Admin identity provider | MFA; secure server session, CSRF protection; no hard-coded/shared passwords |
| GET /api/v1/admin/quotes, /bookings | Admin role | Search/filter/pagination, PII access audit, minimal list fields |
| PATCH /api/v1/admin/requests/:id | Admin role | Allowlisted status transitions, optimistic version check and audit trail |
| POST/PATCH/DELETE /api/v1/admin/{services,gallery,offers,reviews} | Content role | Bilingual validation and approved/published workflow; no cascading deletion of historic requests |
| GET /api/v1/admin/attachments/:id | Authorized record role | Short-lived signed URL; never public bucket URL |

Error envelope: `{ error: { code, fieldErrors, requestId } }`. UI translates stable error codes. Return 422 validation, 401/403 access failure, 409 version conflict, 429 throttling, 5xx retriable server failure. Never display success before committed 201. Preserve retry drafts locally only under an approved privacy policy. Never send phone, names, addresses or uploaded-photo URLs to analytics.

## Relational schema boundaries

Suggested PostgreSQL schema; storage objects in a private object store. UUID primary keys, UTC timestamps, explicit business timezone for visits, migrations and foreign keys. Tenant scope if multi-business use is introduced.

- `services(id, slug UNIQUE, active, version, created_at)`; `service_translations(service_id, locale, title, description, faq_json)` unique(service_id, locale).
- `offers(id, service_id NULL, starts_at, ends_at, status, version)`; `offer_translations(offer_id, locale, title, description, terms)`.
- `gallery_pairs(id, service_id, before_asset_id, after_asset_id, approved_by, approved_at, status)` plus translations and permission evidence.
- `reviews(id, display_name, body_ar, body_en, consent_asset_id, approved_by, approved_at, status)`; no inferred approval.
- `requests(id, type, customer_id NULL, service_id, service_snapshot_json, name, phone, email NULL, address, details, status, preferred_date NULL, preferred_time NULL, timezone, consent_version, idempotency_key UNIQUE, version, created_at)`.
- `assets(id, storage_key UNIQUE, mime, bytes, checksum, scan_state, owner_scope, expires_at NULL)`; `request_assets(request_id, asset_id)`.
- `admin_users(id, identity_subject UNIQUE, role, disabled_at)`; `audit_events(id, actor_id, entity_type, entity_id, action, redacted_diff, created_at)`.
- `settings(key, value_json, version)` for verified address/pin/hours and approved public settings. Secrets stay in the platform secret manager.

Future modules, not version-one functionality or pricing: `customers/profiles` link through nullable customer_id; append-only `loyalty_ledger`; `subscriptions` and recurrence rules; `staff/assignments` linking requests; `payments/payment_events` with verified webhooks and idempotency; `invoices/invoice_lines` with immutable issued snapshots. Keep financial state separate from request status; no card data in the application database. Each future module needs separate scope, migration, permissions and acceptance criteria.

## Security launch gate

1. HTTPS redirect, managed renewal, HSTS after validation; explicit CSP tested with required image/font/map origins, frame-ancestors, nosniff, referrer policy and permissions policy.
2. Identity-provider MFA, secure HttpOnly/SameSite session cookies, session expiry, revocation and per-endpoint role authorization. Admin page secrecy is not access control.
3. Server validates every field, active service IDs, future date/time in Asia/Amman, maximum lengths and email/phone normalization. Client checks are convenience only.
4. Rate limits by account/IP with abuse safeguards, honeypot and provider-backed challenge if needed; notification throttling.
5. Private uploads: magic-byte validation, safe decode/re-encode, malware quarantine, strip EXIF, random keys, strict caps, no SVG/HTML, signed short-lived reads, orphan cleanup and least privilege.
6. Parameterized DB queries; output escaping; CSRF protection; restricted CORS; audit status changes and PII access. No credentials in Git or frontend config.
7. Data retention, deletion/export requests, processor list and breach/escalation contacts approved by the business. No real customer fixtures in source or public demo.
8. Dependency and secret checks; server logs redact PII; request backups and object-store backups encrypted and access controlled.

## Proposed backups (approval and infrastructure required)

Not running in the static demo. Proposed daily 02:00 Asia/Amman database snapshot and coordinated object-store manifest/version capture. Retain 30 daily and 3 monthly snapshots in separate protected backup storage, encrypted with restricted keys. Monitor completion and alert the agreed support contact. Proposed RPO 24 hours; proposed RTO one supported business day, to validate against hosting/size and final support agreement.

Quarterly and before major migrations: restore DB snapshot to isolated environment, restore matching object versions, verify checksums and record counts, sample linked photos, authentication and request status integrity, record recovery time, then delete test PII safely. For an incident: freeze writes, select consistent snapshot/manifest, restore in isolation, verify attachment references and access controls, obtain authorized business sign-off, cut over, rotate affected credentials and document data loss. Deletion requests and retention must cover backup expiry; do not silently reintroduce deleted records when restoring.

## Deployment and SEO

Work is on `dev`; do not change `main` or production Pages source automatically. Serve locally with `npm run serve`. For an isolated hosted preview deploy the dev commit to a separate staging target; no production credentials or records.

Every page is noindex/nofollow; robots disallows indexing because sample content and draft legal terms are not production-ready. `sitemap.xml` and canonical/alternate URLs are templates based on the existing GitHub Pages address. Before launch set the verified production origin in `scripts/build-pages.py`, rebuild, remove noindex only from approved public pages, keep admin out of sitemap, allow public crawling and declare the sitemap in robots.txt. Add approved FAQ/Service schema where supported, not invented aggregate ratings. Existing structured data omits unverified coordinates/hours.

Google Analytics ID is empty and `production:false`. Client must supply G-ID and approve consent. Wire a reviewed consent UI to `enableAnalytics()` and page-view reporting; do not collect request contents or query strings. Map embed and directions URL only activated after exact pin approval. Photographs are now self-hosted optimized WebP; fonts are local WOFF2 with OFL licence files. Retain licence notices and source attribution. External WhatsApp and map links still require internet.

## Handover

See client-facing `docs/proposal.html` for proposed commercial terms, inclusions, exclusions and ownership. Total price, currency/taxes, hosting inclusion/renewal, support/maintenance fees and final delivery dates are TBC. Proposed milestones and estimates are not agreed commitments.
