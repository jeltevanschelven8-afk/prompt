---
name: api-designer
description: >-
  Design clean REST and HTTP APIs: model resources, choose endpoints and
  methods, pick correct status codes, define a consistent error format, and
  settle pagination, filtering, idempotency and versioning. Produces an
  endpoint table plus example requests and responses, and optionally an OpenAPI
  sketch. Use this skill whenever the user wants to design, plan or review an
  API, asks which status code or URL structure to use, or says help me design
  endpoints for, and for Dutch phrases like "ontwerp een API voor", "welke
  endpoints heb ik nodig" or "hoe structureer ik mijn REST API".
license: "MIT"
metadata:
  author: "prompt"
  category: "code"
  tags: "api, rest, http, endpoints, openapi, design, ontwerp, statuscodes, koppeling"
  version: "1.0.0"
  summary_nl: "Ontwerpt een heldere REST API met endpoints, statuscodes, foutformaat, paginering en voorbeeldpayloads."
---

# API designer

An API is a promise that is expensive to change once clients depend on it. This skill gets the design right on paper first: resources that match the domain, predictable URLs, honest status codes and one error format everywhere. The deliverable is something a frontend developer or partner could start building against.

## Workflow

1. **Understand the consumers and use cases.** Who calls this API (own frontend, mobile app, partners, other services), and what are the five to ten things they need to do? List them as user stories. Design follows use cases, not database tables.
2. **Model the resources.** Identify the nouns (`orders`, `customers`, `invoices`) and their relationships. Decide which are top-level and which are nested. Keep nesting to one level (`/orders/{id}/items`); deeper paths get brittle.
3. **Map operations to methods.**
   - `GET /orders` list, `GET /orders/{id}` read
   - `POST /orders` create, returns `201` with a `Location` header
   - `PATCH /orders/{id}` partial update, `PUT` only for full replacement
   - `DELETE /orders/{id}` returns `204`
   - Actions that are not CRUD become sub-resources or explicit action endpoints: `POST /orders/{id}/cancel`. That is clearer than overloading `PATCH` with a status flag.
4. **Choose status codes deliberately.** `200` OK, `201` Created, `202` Accepted for async work, `204` No Content, `400` malformed input, `401` not authenticated, `403` authenticated but not allowed, `404` not found, `409` conflict (duplicate, version mismatch), `422` valid JSON but fails business rules, `429` rate limited, `500` unexpected server error. Clients branch on these, so consistency matters more than which school you follow.
5. **Define one error format.** Prefer RFC 9457 problem details or a close equivalent, used by every endpoint:
   ```json
   { "type": "https://example.com/errors/out-of-stock", "title": "Item out of stock",
     "status": 409, "detail": "SKU A-100 has 0 units left", "errors": [{"field": "items[0].qty", "message": "exceeds stock"}] }
   ```
6. **Settle the cross-cutting rules.**
   - **Pagination:** cursor-based (`?limit=50&cursor=...`, response has `next_cursor`) for large or changing collections; offset only for small, stable lists.
   - **Filtering and sorting:** `?status=open&sort=-created_at`.
   - **Idempotency:** accept an `Idempotency-Key` header on `POST` endpoints that create money or orders, so retries are safe.
   - **Versioning:** URL prefix `/v1` is simplest to operate; header-based versioning is cleaner but harder to debug. Pick one and note it.
   - **Naming:** plural nouns, kebab-case or snake_case consistently, ISO 8601 timestamps in UTC, ids as strings.
   - **Concurrency:** `ETag` with `If-Match` for updates where lost writes would hurt.
7. **Write it up** with the template below, and offer an OpenAPI 3.1 skeleton if the user wants machine-readable output.
8. **Review against the use cases.** Walk each user story through the endpoints. A story that needs four round trips usually means a missing endpoint or an `?include=` option.

## Output template

```markdown
## Endpoints
| Method | Path | Purpose | Success | Errors |
|---|---|---|---|---|
| GET | /v1/orders | List orders, cursor paginated | 200 | 400 |
| POST | /v1/orders | Create order (Idempotency-Key) | 201 | 400, 409, 422 |
| GET | /v1/orders/{id} | Read one order | 200 | 404 |
| POST | /v1/orders/{id}/cancel | Cancel an open order | 200 | 404, 409 |

## Example: POST /v1/orders
Request:
{ "customer_id": "cus_123", "items": [{ "sku": "A-100", "qty": 2 }] }
Response 201, Location: /v1/orders/ord_789
{ "id": "ord_789", "status": "open", "total": { "amount": "39.90", "currency": "EUR" },
  "created_at": "2026-03-01T10:15:00Z" }

## Conventions
Errors: problem details. Pagination: cursor. Money: string amount plus currency.

## Open decisions
```

## Pitfalls and when to ask

- Money as floats causes rounding bugs; use strings or integer minor units.
- Do not leak database structure (auto-increment ids, join tables) into URLs.
- Returning `200` with an error body breaks every generic client and monitoring tool.
- If an existing API is in production, ask before proposing breaking changes and suggest additive changes or a new version instead.
- Authentication scheme and rate limits depend on infrastructure; ask rather than assume.

## Scope

HTTP and REST style APIs. For GraphQL or gRPC the same thinking applies, but say that conventions differ. Implementing the endpoints is a separate step the user can request afterwards.
