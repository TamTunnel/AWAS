# AWAS Technical Specification v1.1

## Table of Contents
- [Overview](#overview)
- [Core Concepts](#core-concepts)
- [AI Action Manifest](#ai-action-manifest)
- [OpenAPI Interoperability](#openapi-interoperability)
- [HTML Data Attributes](#html-data-attributes)
- [Discovery Mechanisms](#discovery-mechanisms)
- [Extended Robots.txt](#extended-robotstxt)
- [HTTP Headers](#http-headers)
- [Security Considerations](#security-considerations)

## Overview

The AI Web Action Standard (AWAS) defines a machine-readable format for describing actionable operations on web pages. It enables AI browsers and agents to interact with websites efficiently while maintaining full backwards compatibility with traditional browsers.

## Protocol Interoperability: MCP, ADK/A2A

AWAS supports direct integration with agent protocols and tool orchestration standards out of the box:

- `/well-known/mcp-manifest.json` for [Model Context Protocol (MCP)] — describes tool capabilities for model-to-API agent flows.
- `/well-known/a2a-manifest.json` for [Agent2Agent (A2A) and Google ADK] — enabling agent discovery, delegation, and specialist invocation.

These files are automatically updatable and work alongside the main AWAS manifest. See the [Interoperability Wiki](https://github.com/TamTunnel/awas/wiki/Interoperability) for full schema, usage guides, and example agent workflows.

**Sample Python: Discover all protocol manifests**
```
import requests
for manifest in [
'/.well-known/ai-actions.json',
'/.well-known/mcp-manifest.json',
'/.well-known/a2a-manifest.json'
]:
resp = requests.get(f'https://yoursite.com{manifest}')
if resp.status_code == 200:
print(manifest, 'found:', resp.json())
```
### Design Principles

1. **Non-Disruptive**: Works alongside existing HTML without modifications
2. **Progressive Enhancement**: Can be adopted incrementally
3. **Backwards Compatible**: Traditional browsers ignore AWAS elements
4. **Security-First**: Built-in permission and rate limiting systems
5. **Framework Agnostic**: Works with any technology stack

### Conformance Levels

- **Level 1 (Minimal)**: AI Action Manifest only
- **Level 2 (Standard)**: Manifest + HTML attributes
- **Level 3 (Complete)**: All components including discovery endpoints

## Core Concepts

### Actions

An **action** is a discrete operation that can be performed on a web page. Actions include:
- Form submissions (e.g., add to cart, search)
- Navigation (e.g., filtering, pagination)
- Data retrieval (e.g., API calls)
- State changes (e.g., toggle, expand)

### Inputs and Outputs

Each action may have:
- **Inputs**: Required or optional parameters
- **Outputs**: Expected response structure
- **Side Effects**: State changes that occur

### Workflows

A **workflow** is a sequence of related actions that accomplish a complex task (e.g., complete purchase = search → filter → add to cart → checkout).

## AI Action Manifest

### Location

The AI Action Manifest MUST be served at:
```
/.well-known/ai-actions.json
```

This follows the RFC 8615 well-known URI specification.

### Manifest Structure

```json
{
  "$schema": "https://awas.dev/schema/v1/manifest.json",
  "specVersion": "1.1",
  "lastUpdated": "2025-12-01T00:00:00Z",
  "name": "string (optional)",
  "description": "string (optional)",
  "actions": [Action],
  "workflows": [Workflow] (optional),
  "conformanceLevel": "L1|L2|L3 (optional)",
  "security": Security (optional),
  "rate_limits": RateLimits (optional),
  "authentication": Authentication (optional)
}

```

### Action Object

```json
{
  "id": "string (required)",
  "name": "string (required)",
  "description": "string (optional)",
  "method": "GET|POST|PUT|DELETE|PATCH (required)",
  "endpoint": "string (required)",
  "intent": "read|write|delete|execute (optional)",
  "sideEffect": "safe|idempotent|destructive (optional)",
  "conformanceLevel": "L1|L2|L3 (optional)",
  "selector": "string (optional)",
  "parameters": [Parameter] (legacy, use inputSchema)",
  "inputSchema": "JSON Schema object (optional)",
  "outputSchema": "JSON Schema object (optional)",
  "openapi": { "$ref": "string (optional)" },
  "previewUrl": "string (optional)",
  "dryRunSupported": "boolean (optional)",
  "idempotencyKeySupported": "boolean (optional)",
  "idempotencyKeyHeader": "string (optional)",
  "preconditions": [string] (optional)",
  "authScopes": [string] (optional)",
  "rateLimitHint": "string (optional)",
  "authentication_required": "boolean (optional)"
}

```

#### Action Types

- `form_submission`: Submit form data
- `navigation`: Navigate to different page/state
- `search`: Search operation
- `filter`: Filter/sort results
- `data_retrieval`: Fetch data
- `state_change`: Modify application state
- `custom`: Custom action type

### Input Object

```json
{
  "name": "string (required)",
  "type": "string|integer|number|boolean|array|object (required)",
  "required": "boolean (default: false)",
  "default": "any (optional)",
  "selector": "string (optional)",
  "description": "string (optional)",
  "validation": {
    "pattern": "string (regex)",
    "min": "number",
    "max": "number",
    "minLength": "number",
    "maxLength": "number",
    "enum": ["array of allowed values"]
  }
}
```

### Output Object

```json
{
  "type": "object|array|string",
  "schema": "object describing response structure",
  "success_codes": [200, 201],
  "error_codes": {
    "400": "Bad request description",
    "404": "Not found description"
  }
}
```

### Workflow Object

```json
{
  "id": "string (required)",
  "name": "string (required)",
  "description": "string (optional)",
  "steps": ["array of action IDs"],
  "conditionals": [
    {
      "step": "number",
      "condition": "string (expression)",
      "on_true": "action_id",
      "on_false": "action_id"
    }
  ]
}
```

### Rate Limits Object

```json
{
  "requests_per_minute": "number",
  "requests_per_hour": "number",
  "burst_limit": "number",
  "concurrent_requests": "number"
}
```

### Authentication Object

```json
{
  "required": "boolean",
  "optional_for": ["array of action IDs"],
  "methods": ["session", "api_key", "oauth", "jwt"],
  "endpoints": {
    "login": "/auth/login",
    "token": "/auth/token"
  }
}
```
### Security Object

```json
{
"csrfRequired": "boolean (optional)",
"csrfTokenHeader": "string (optional)",
"requiredHeaders": ["string"] (optional),
"allowedOrigins": ["string"] (optional),
"sameSite": "strict|lax|none (optional)"
}
```
## OpenAPI Interoperability

AWAS provides optional OpenAPI integration to leverage existing API documentation and tooling while maintaining AWAS as the source of truth for AI agent interactions.

### Purpose

The `openapi` field in action definitions allows sites to:
- Link AWAS actions to existing OpenAPI/Swagger specifications
- Reduce duplication between AWAS manifests and OpenAPI docs
- Enable developers familiar with OpenAPI to adopt AWAS more easily
- Leverage existing OpenAPI tooling for documentation, code generation, and testing

### Design Principles

1. **AWAS is Authoritative**: If there's any conflict between AWAS manifest and OpenAPI spec, AWAS semantics take precedence for agent behavior
2. **Optional Enhancement**: OpenAPI fields are entirely optional; agents that don't support OpenAPI simply ignore them
3. **Vendor Neutral**: Not tied to any specific API platform or vendor
4. **Backward Compatible**: Existing manifests without OpenAPI references continue to work unchanged

### OpenAPI Object Structure

The `openapi` field within an action supports the following properties:

```json
{
  "openapi": {
    "documentUrl": "/openapi.json",
    "operationId": "searchProducts",
    "$ref": "#/paths/~1api~1search/get"
  }
}
```

#### Fields

- **`documentUrl`** (string, optional): URL to the OpenAPI document (JSON or YAML), absolute or site-relative (e.g., `/openapi.json`, `https://api.example.com/v3/openapi.yaml`)
- **`operationId`** (string, optional): The `operationId` from the OpenAPI document that corresponds to this AWAS action
- **`$ref`** (string, optional): JSON Pointer or reference to the specific operation in the OpenAPI document (e.g., `#/paths/~1api~1search/get`)

### Usage Guidelines

**When to use each field:**

- Use `documentUrl` + `operationId` when your OpenAPI spec uses operation IDs (recommended)
- Use `documentUrl` + `$ref` when referencing operations by path and method
- All three fields can be provided for maximum compatibility

**Best practices:**

1. Ensure HTTP method and endpoint in AWAS match the OpenAPI operation
2. Use `inputSchema` and `outputSchema` in AWAS even when linking to OpenAPI for faster agent parsing
3. Keep OpenAPI spec and AWAS manifest synchronized when making changes
4. Document any AWAS-specific semantics (like `sideEffect`, `intent`, `preconditions`) that aren't captured in OpenAPI

### Example

```json
{
  "id": "search_products",
  "name": "Search Products",
  "description": "Search for products by keyword",
  "method": "GET",
  "endpoint": "/api/search",
  "intent": "read",
  "sideEffect": "safe",
  "openapi": {
    "documentUrl": "/openapi.json",
    "operationId": "searchProducts"
  },
  "inputSchema": {
    "type": "object",
    "properties": {
      "q": {
        "type": "string",
        "description": "Search query"
      }
    },
    "required": ["q"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "results": {
        "type": "array",
        "items": {"type": "object"}
      }
    }
  }
}
```

### Agent Behavior

Agents that support OpenAPI interoperability MAY:
- Fetch the OpenAPI document for additional context
- Use OpenAPI schemas for enhanced validation
- Generate code or SDK calls based on OpenAPI specs
- Provide richer documentation to users

Agents MUST:
- Treat OpenAPI references as optional hints, not requirements
- Fall back gracefully if OpenAPI document is unavailable
- Respect AWAS manifest as the primary source of truth
- Never require OpenAPI support for basic functionality


## HTML Data Attributes

### Namespace

All AWAS attributes use the `data-ai-` prefix to avoid conflicts.

### Action Attributes

#### data-ai-action
- **Type**: String
- **Required**: Yes (for actionable elements)
- **Description**: Unique identifier matching an action in the manifest
```html
<button data-ai-action="add_to_cart">Add to Cart</button>
```

#### data-ai-action-type
- **Type**: String
- **Required**: Recommended
- **Values**: form_submission | navigation | search | filter | data_retrieval | state_change
```html
<form data-ai-action="search_products" data-ai-action-type="search">
```

#### data-ai-action-trigger
- **Type**: String
- **Description**: Identifies the specific trigger element
```html
<button data-ai-action-trigger="submit_search">Search</button>
```

### API Attributes

#### data-ai-endpoint
- **Type**: String (URL)
- **Description**: Direct API endpoint for the action
```html
<form data-ai-endpoint="/api/search">
```

#### data-ai-method
- **Type**: String
- **Values**: GET | POST | PUT | DELETE | PATCH
```html
<form data-ai-method="POST">
```

### Parameter Attributes

#### data-ai-param
- **Type**: String
- **Description**: Parameter name for this input
```html
<input name="query" data-ai-param="q">
```

#### data-ai-param-type
- **Type**: String
- **Values**: string | integer | number | boolean | array | object
```html
<input type="number" data-ai-param="quantity" data-ai-param-type="integer">
```

#### data-ai-param-required
- **Type**: String ("true" | "false")
```html
<input data-ai-param="email" data-ai-param-required="true">
```

#### data-ai-param-default
- **Type**: String
```html
<input data-ai-param="quantity" data-ai-param-default="1">
```

### Content Attributes

#### data-ai-content
- **Type**: String
- **Values**: primary | secondary | metadata | navigation | footer
- **Description**: Classifies content importance
```html
<main data-ai-content="primary">
```

#### data-ai-intent
- **Type**: String
- **Description**: Page intent/purpose
- **Examples**: product-detail | search-results | checkout | user-profile
```html
<div data-ai-intent="product-detail">
```

#### data-ai-entity
- **Type**: String
- **Description**: Entity type represented
- **Examples**: product | user | order | review
```html
<article data-ai-entity="product" data-ai-id="PROD-123">
```

#### data-ai-field
- **Type**: String
- **Description**: Specific data field identifier
```html
<span data-ai-field="product-price">$29.99</span>
```

## Discovery Mechanisms

### HTML Link Tags

Manifest discovery through `<link>` tags in `<head>`:

```html
<link rel="ai-actions" href="/.well-known/ai-actions.json" type="application/json">
<link rel="ai-sitemap" href="/.well-known/ai-sitemap.json" type="application/json">
<link rel="ai-capabilities" href="/.well-known/ai-capabilities" type="application/json">
```

### AI Capabilities Endpoint

**Endpoint**: `/.well-known/ai-capabilities`

**Response**:
```json
{
  "version": "1.0",
  "supported_protocols": ["HTTP/1.1", "HTTP/2"],
  "auth_methods": ["session", "api_key", "oauth"],
  "rate_limits": {
    "requests_per_minute": 60,
    "burst_limit": 10
  },
  "features": [
    "structured_actions",
    "workflow_support",
    "real_time_updates",
    "webhooks"
  ],
  "compliance": {
    "gdpr": true,
    "ccpa": true,
    "coppa": false
  }
}
```

### AI Sitemap

**Endpoint**: `/.well-known/ai-sitemap.json`

**Structure**:
```json
{
  "version": "1.0",
  "pages": [
    {
      "url": "/products",
      "intent": "product-listing",
      "actions": ["search_products", "apply_filters"],
      "entities": ["product"],
      "priority": "high",
      "update_frequency": "daily"
    }
  ]
}
```

## Extended Robots.txt

### Standard Directives

Use standard robots.txt directives for AI browser user-agents:

```
User-agent: AtlasBot
User-agent: CometBot
User-agent: AI-Browser/*
Disallow: /checkout/
Allow: /products/
```

### Comment-Based Hints

Additional hints as comments (ignored by traditional crawlers):

```
# agentic-manifest: /.well-known/ai-actions.json
# ai-capabilities: /.well-known/ai-capabilities
# ai-rate-limit: 60/minute
# ai-allowed-actions: search, filter, view
# ai-restricted-actions: purchase, checkout, payment
# ai-respect-privacy: true
# ai-no-data-training: true
```

## HTTP Headers

### Request Headers

AI agents SHOULD include:

```
X-AI-Agent: true
X-AI-Agent-Name: AtlasBot/1.0
X-AI-Agent-Purpose: product_search
User-Agent: Mozilla/5.0 (compatible; AtlasBot/1.0)
```

### Response Headers

Servers MAY include:

```
X-AI-Action-Success: true
X-AI-Action-ID: search_products
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1699564800
```

## Security Considerations

### Rate Limiting

Implementations MUST enforce rate limits specified in the manifest.

### Authentication

Actions requiring authentication MUST be clearly marked in the manifest.

### Conformance Levels

AWAS v1.1 introduces structured conformance levels to enable phased adoption:

- **Level 1 (L1 - Read-Only)**: Safe, read-only actions (search, filter, view). No write operations, no preview required.
- **Level 2 (L2 - Write with Preview)**: Write operations with preview/dry-run support before execution. Includes L1 capabilities.
- **Level 3 (L3 - Full Transactional)**: Complete transactional support with idempotency, rollback, and complex workflows. Includes L1 and L2 capabilities.

See [CONFORMANCE_LEVELS.md](./CONFORMANCE_LEVELS.md) for detailed requirements and examples.


### CSRF Protection

Form submissions MUST implement CSRF protection. Include CSRF tokens in the manifest or action definitions.

### Input Validation

All inputs MUST be validated server-side regardless of manifest specifications.

### Permissions

Implement action-level permissions to control what agents can do.

### Audit Trails

Log AI agent actions for security and compliance purposes.

## Versioning

This specification uses semantic versioning (MAJOR.MINOR.PATCH).

- **MAJOR**: Backwards-incompatible changes
- **MINOR**: Backwards-compatible feature additions
- **PATCH**: Backwards-compatible bug fixes

Current version: **1.1.0**

## References

- RFC 8615: Well-Known URIs
- Schema.org: Structured Data Vocabulary
- OpenAPI Specification 3.1
- WAI-ARIA 1.2
- W3C HTML5 Specification

---

*Last Updated: October 29, 2025*
