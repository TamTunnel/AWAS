# AWAS Technical Specification v1.0

## Table of Contents
- [Overview](#overview)
- [Core Concepts](#core-concepts)
- [AI Action Manifest](#ai-action-manifest)
- [HTML Data Attributes](#html-data-attributes)
- [Discovery Mechanisms](#discovery-mechanisms)
- [Extended Robots.txt](#extended-robotstxt)
- [HTTP Headers](#http-headers)
- [Security Considerations](#security-considerations)

## Overview

The AI Web Action Standard (AWAS) defines a machine-readable format for describing actionable operations on web pages. It enables AI browsers and agents to interact with websites efficiently while maintaining full backwards compatibility with traditional browsers.

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
  "version": "1.0",
  "name": "string",
  "description": "string",
  "actions": [Action],
  "workflows": [Workflow],
  "rate_limits": RateLimits,
  "authentication": Authentication
}
```

### Action Object

```json
{
  "id": "string (required)",
  "type": "string (required)",
  "name": "string (required)",
  "description": "string (optional)",
  "method": "GET|POST|PUT|DELETE|PATCH (required)",
  "endpoint": "string (required)",
  "selector": "string (optional)",
  "inputs": [Input],
  "outputs": Output,
  "authentication_required": "boolean (optional)",
  "rate_limit": "number (optional)"
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

Current version: **1.0.0**

## References

- RFC 8615: Well-Known URIs
- Schema.org: Structured Data Vocabulary
- OpenAPI Specification 3.1
- WAI-ARIA 1.2
- W3C HTML5 Specification

---

*Last Updated: October 29, 2025*
