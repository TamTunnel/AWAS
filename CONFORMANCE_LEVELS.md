# AWAS Conformance Levels

## Overview

AWAS v1.1 introduces conformance levels to allow sites to adopt AWAS incrementally and signal to agents which types of operations are supported. This phased approach makes it easier for websites to implement AWAS without requiring full implementation of all features upfront.

## Conformance Levels

### Level 1 (L1): Read-Only

**Purpose:** Safe, non-destructive access to site content and data.

**Characteristics:**
- All actions have `sideEffect: "safe"`
- All actions have `intent: "read"`
- No state changes on the server
- Idempotent and can be cached
- No authentication required (optional)

**Typical Actions:**
- Search and filtering
- Product browsing
- Content navigation
- Data retrieval
- Public API reads

**Requirements:**
- `specVersion: "1.1"`
- `conformanceLevel: "L1"` in manifest
- All actions must be GET requests
- Actions must be safe and idempotent

**Example:**
```json
{
  "conformanceLevel": "L1",
  "actions": [
    {
      "id": "search",
      "intent": "read",
      "sideEffect": "safe",
      "method": "GET"
    }
  ]
}
```

---

### Level 2 (L2): Write with Preview

**Purpose:** Allow state-changing operations with safety nets.

**Characteristics:**
- Includes all L1 capabilities
- Supports write operations with preview/dry-run
- Actions with `sideEffect: "idempotent"` or `"destructive"`
- Supports `intent: "write"` and `"delete"`
- Preview endpoints available (`previewUrl`)
- Dry-run mode supported (`dryRunSupported: true`)
- Idempotency keys supported for safe retries

**Typical Actions:**
- Add to cart (idempotent)
- Update profile (idempotent)
- Submit forms
- Create resources
- Transactional operations

**Requirements:**
- All L1 requirements
- `conformanceLevel: "L2"` in manifest
- `previewUrl` or `dryRunSupported` for write actions
- `idempotencyKeySupported` recommended
- CSRF protection documented in `security` section

**Example:**
```json
{
  "conformanceLevel": "L2",
  "actions": [
    {
      "id": "add_to_cart",
      "intent": "write",
      "sideEffect": "idempotent",
      "method": "POST",
      "previewUrl": "/api/cart/preview",
      "dryRunSupported": true,
      "idempotencyKeySupported": true,
      "conformanceLevel": "L2"
    }
  ],
  "security": {
    "csrfRequired": true,
    "csrfTokenHeader": "X-CSRF-Token"
  }
}
```

---

### Level 3 (L3): Full Transactional

**Purpose:** Complete, production-grade agent support with strong safety guarantees.

**Characteristics:**
- Includes all L2 capabilities
- Full idempotency support across all write operations
- Precondition validation documented
- Authentication and authorization scopes defined
- Rate limiting clearly documented
- Comprehensive error handling
- Full OpenAPI integration (optional)

**Typical Actions:**
- Financial transactions
- Checkout and payment
- Multi-step workflows
- Destructive operations (with safeguards)
- Cross-resource transactions

**Requirements:**
- All L2 requirements
- `conformanceLevel: "L3"` in manifest
- `authScopes` defined for sensitive actions
- `preconditions` documented for complex actions
- `rateLimitHint` for all actions
- `idempotencyKeySupported: true` for all writes
- Complete input/output schemas

**Example:**
```json
{
  "conformanceLevel": "L3",
  "actions": [
    {
      "id": "checkout",
      "intent": "write",
      "sideEffect": "destructive",
      "method": "POST",
      "authScopes": ["payment:write"],
      "preconditions": [
        "Cart must not be empty",
        "Payment method must be valid",
        "Shipping address must be complete"
      ],
      "idempotencyKeySupported": true,
      "idempotencyKeyHeader": "Idempotency-Key",
      "previewUrl": "/api/checkout/preview",
      "dryRunSupported": true,
      "rateLimitHint": {
        "requests": 10,
        "window": "1h"
      },
      "conformanceLevel": "L3"
    }
  ]
}
```

---

## Choosing Your Conformance Level

### Start with L1 if:
- You're new to AWAS
- Your site is primarily informational
- You want to test agent interaction with minimal risk
- You don't have write operations yet

### Move to L2 when:
- You want agents to perform actions on users' behalf
- You have e-commerce or form submission
- You can implement preview/dry-run endpoints
- You're ready for CSRF protection

### Implement L3 when:
- You need production-grade reliability
- You handle sensitive or financial operations
- You want comprehensive agent integration
- You're ready for full observability and rate limiting

---

## Mixed Conformance Levels

You can declare a global conformance level for your manifest while individual actions can require higher levels:

```json
{
  "conformanceLevel": "L1",
  "actions": [
    {
      "id": "search",
      "conformanceLevel": "L1"
    },
    {
      "id": "add_to_cart",
      "conformanceLevel": "L2"
    }
  ]
}
```

Agents will respect the highest conformance level required by the actions they want to execute.

---

## Verification and Testing

### L1 Checklist
- [ ] All actions are GET requests
- [ ] All actions marked as `sideEffect: "safe"`
- [ ] No authentication required for testing
- [ ] Actions are idempotent

### L2 Checklist
- [ ] All L1 requirements met
- [ ] Preview endpoints implemented
- [ ] Dry-run mode available
- [ ] CSRF protection documented
- [ ] Idempotency keys supported

### L3 Checklist
- [ ] All L2 requirements met
- [ ] Auth scopes defined
- [ ] Preconditions documented
- [ ] Rate limits specified
- [ ] Complete error responses
- [ ] Full input/output schemas

---

## For Agent Developers

When consuming an AWAS manifest:

1. Check the manifest's `conformanceLevel`
2. Verify each action's individual `conformanceLevel`
3. Only execute actions at or below your agent's capability level
4. Respect preview/dry-run for L2+ actions
5. Always use idempotency keys for L3 writes

---

## Migration Path

```
L1 (Read-Only)
    ↓
    Add preview endpoints
    Add CSRF protection
    ↓
L2 (Write with Preview)
    ↓
    Add auth scopes
    Add preconditions
    Add rate limit hints
    Add full schemas
    ↓
L3 (Full Transactional)
```

Each level builds on the previous, making incremental adoption straightforward.
