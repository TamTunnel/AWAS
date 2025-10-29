# AWAS Security Guidelines

Security is a core principle of AWAS. This document outlines security considerations and best practices.

## Table of Contents
- [Threat Model](#threat-model)
- [Authentication & Authorization](#authentication--authorization)
- [Rate Limiting](#rate-limiting)
- [Input Validation](#input-validation)
- [CSRF Protection](#csrf-protection)
- [Privacy Considerations](#privacy-considerations)
- [Audit Logging](#audit-logging)
- [Security Headers](#security-headers)

## Threat Model

### Potential Threats

1. **Abuse by Malicious AI Agents**
   - Automated scraping at scale
   - Resource exhaustion attacks
   - Data exfiltration

2. **Action Injection**
   - Manipulating action definitions
   - Bypassing authentication
   - Privilege escalation

3. **Privacy Violations**
   - Unauthorized data access
   - User tracking
   - Data training without consent

4. **Traditional Web Attacks**
   - XSS, CSRF, SQL injection
   - Session hijacking
   - Man-in-the-middle attacks

## Authentication & Authorization

### Action-Level Authentication

Clearly specify authentication requirements in your manifest:

```json
{
  "actions": [
    {
      "id": "add_to_cart",
      "authentication_required": true,
      "authorization": {
        "roles": ["authenticated_user"],
        "scopes": ["cart:write"]
      }
    }
  ]
}
```

### Implementation

**Session-Based Auth**:
```python
from functools import wraps
from flask import session, request, jsonify

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/cart/add', methods=['POST'])
@require_auth
def add_to_cart():
    # User is authenticated
    pass
```

**API Key Auth**:
```python
def validate_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not is_valid_key(api_key):
            return jsonify({"error": "Invalid API key"}), 403
        return f(*args, **kwargs)
    return decorated_function
```

**JWT Auth**:
```python
import jwt

def require_jwt(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = payload
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated_function
```

### OAuth 2.0 Integration

For third-party AI agents:

```python
from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.oauth2.rfc6750 import BearerTokenValidator

require_oauth = ResourceProtector()

@app.route('/api/protected', methods=['POST'])
@require_oauth('scope:action')
def protected_action():
    # OAuth-protected action
    pass
```

## Rate Limiting

### Multi-Tier Rate Limiting

Implement different limits for different user types:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)

def get_rate_limit():
    """Dynamic rate limiting based on agent type"""
    if is_ai_agent(request):
        agent_name = request.headers.get('X-AI-Agent-Name', '')
        if agent_name in TRUSTED_AGENTS:
            return "120 per minute"  # Trusted agents
        return "60 per minute"  # Standard AI agents
    return "300 per minute"  # Human users

@app.route('/api/search')
@limiter.limit(get_rate_limit)
def search():
    pass
```

### Per-Action Rate Limits

```json
{
  "actions": [
    {
      "id": "search_products",
      "rate_limit": {
        "requests": 60,
        "window": "minute"
      }
    },
    {
      "id": "create_order",
      "rate_limit": {
        "requests": 10,
        "window": "hour"
      }
    }
  ]
}
```

### Burst Protection

```python
from redis import Redis
import time

redis_client = Redis()

def check_burst_limit(client_id, burst_limit=10, window=60):
    """Check if client exceeded burst limit"""
    key = f"burst:{client_id}"
    current = redis_client.incr(key)

    if current == 1:
        redis_client.expire(key, window)

    if current > burst_limit:
        return False
    return True
```

## Input Validation

### Server-Side Validation (Required)

NEVER trust client-side validation alone:

```python
from marshmallow import Schema, fields, validate, ValidationError

class AddToCartSchema(Schema):
    product_id = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    quantity = fields.Int(required=True, validate=validate.Range(min=1, max=100))
    variant_id = fields.Str(validate=validate.Length(max=50))

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    schema = AddToCartSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    # Process valid data
    pass
```

### SQL Injection Prevention

Use parameterized queries:

```python
# NEVER do this
cursor.execute(f"SELECT * FROM products WHERE id = '{product_id}'")

# Always do this
cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
```

### XSS Prevention

Sanitize outputs:

```python
from markupsafe import escape

@app.route('/api/search')
def search():
    query = escape(request.args.get('q', ''))
    # Use sanitized query
    pass
```

## CSRF Protection

### Token-Based Protection

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# Exempt AI agent endpoints if using other auth
@app.route('/api/action', methods=['POST'])
@csrf.exempt  # Only if using API key/OAuth
def action():
    if is_ai_agent(request):
        # Validate API key instead
        pass
    else:
        # CSRF token validated automatically
        pass
```

### Double Submit Cookie

```python
import secrets

def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

def validate_csrf_token():
    token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
    if not token or token != session.get('csrf_token'):
        abort(403)
```

## Privacy Considerations

### Data Minimization

Only expose necessary data:

```json
{
  "actions": [
    {
      "id": "search_users",
      "outputs": {
        "fields": ["user_id", "username"],
        "excluded": ["email", "password_hash", "ip_address"]
      }
    }
  ]
}
```

### No-Training Flag

Respect user privacy preferences:

```python
@app.route('/api/action', methods=['POST'])
def action():
    if request.headers.get('X-AI-No-Training') == 'true':
        # Don't log detailed data for AI training
        log_minimal(request)
    else:
        log_full(request)
```

### PII Protection

```python
import re

def mask_pii(data):
    """Mask personally identifiable information"""
    # Mask email
    if 'email' in data:
        data['email'] = re.sub(r'(.{2}).*(@.*)', r'\1***\2', data['email'])

    # Mask phone
    if 'phone' in data:
        data['phone'] = re.sub(r'(\d{3})\d{4}(\d{3})', r'\1****\2', data['phone'])

    return data
```

### GDPR Compliance

```python
@app.route('/api/user/data', methods=['GET'])
@require_auth
def get_user_data():
    """Right to data portability"""
    user_id = session['user_id']
    data = get_all_user_data(user_id)
    return jsonify(data)

@app.route('/api/user/delete', methods=['DELETE'])
@require_auth
def delete_user():
    """Right to be forgotten"""
    user_id = session['user_id']
    delete_all_user_data(user_id)
    return jsonify({"success": True})
```

## Audit Logging

### Comprehensive Logging

```python
import logging
from datetime import datetime

def log_ai_action(action_id, user_id, params, result):
    """Log AI agent actions for audit trail"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'action_id': action_id,
        'user_id': user_id,
        'ai_agent': request.headers.get('X-AI-Agent-Name', 'Unknown'),
        'ip_address': request.remote_addr,
        'params': params,
        'result': result,
        'status_code': result.get('status_code', 200)
    }

    logging.info(f"AI_ACTION: {json.dumps(log_entry)}")

    # Store in database for compliance
    store_audit_log(log_entry)
```

### Security Event Logging

```python
def log_security_event(event_type, details):
    """Log security-relevant events"""
    security_log.warning({
        'event_type': event_type,
        'details': details,
        'timestamp': datetime.utcnow().isoformat(),
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent')
    })

# Usage
@app.route('/api/login', methods=['POST'])
def login():
    if failed_auth:
        log_security_event('failed_login', {
            'username': username,
            'reason': 'invalid_password'
        })
```

## Security Headers

### Required Headers

```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response
```

### CORS Configuration

```python
from flask_cors import CORS

# Restrictive CORS for AI agents
CORS(app, resources={
    r"/.well-known/*": {
        "origins": "*",
        "methods": ["GET"]
    },
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "X-AI-Agent", "Authorization"]
    }
})
```

## Action Permissions

### Permission Matrix

```json
{
  "permissions": {
    "guest": {
      "allowed_actions": ["search_products", "view_product"],
      "denied_actions": ["add_to_cart", "checkout"]
    },
    "authenticated": {
      "allowed_actions": ["*"],
      "denied_actions": ["admin_actions"]
    },
    "ai_agent": {
      "allowed_actions": ["search_products", "view_product", "compare"],
      "denied_actions": ["checkout", "payment", "account_modify"],
      "requires_user_consent": ["add_to_cart", "create_order"]
    }
  }
}
```

### Implementation

```python
def check_permission(action_id, user_role):
    """Check if user has permission for action"""
    permissions = load_permissions()
    role_perms = permissions.get(user_role, {})

    # Check denied first
    if action_id in role_perms.get('denied_actions', []):
        return False

    # Check allowed
    allowed = role_perms.get('allowed_actions', [])
    if '*' in allowed or action_id in allowed:
        return True

    return False

@app.route('/api/action/<action_id>', methods=['POST'])
def execute_action(action_id):
    user_role = get_user_role()

    if not check_permission(action_id, user_role):
        return jsonify({"error": "Forbidden"}), 403

    # Execute action
    pass
```

## Sensitive Actions

### Require Human Verification

```python
SENSITIVE_ACTIONS = ['checkout', 'payment', 'account_delete', 'data_export']

@app.route('/api/action/<action_id>', methods=['POST'])
def execute_action(action_id):
    if action_id in SENSITIVE_ACTIONS:
        if is_ai_agent(request):
            return jsonify({
                "error": "Human verification required",
                "verification_url": f"/verify/{action_id}",
                "message": "This action requires human confirmation"
            }), 403

    # Execute action
    pass
```

## Security Checklist

Before deploying AWAS:

- [ ] Rate limiting implemented and tested
- [ ] Authentication required for sensitive actions
- [ ] Input validation on all endpoints
- [ ] CSRF protection enabled
- [ ] SQL injection prevention verified
- [ ] XSS prevention implemented
- [ ] Security headers configured
- [ ] CORS properly restricted
- [ ] Audit logging in place
- [ ] PII protection mechanisms active
- [ ] GDPR compliance verified
- [ ] Sensitive actions require human verification
- [ ] Regular security testing scheduled
- [ ] Incident response plan documented

## Reporting Security Issues

If you discover a security vulnerability in AWAS:

1. **DO NOT** create a public GitHub issue
2. Email security@awas.dev with details
3. Include steps to reproduce
4. Allow time for patching before disclosure

## Security Updates

Stay informed about security updates:
- Watch the [GitHub repository](https://github.com/TamTunnel/awas)
- Subscribe to security announcements
- Review changelog for security patches

---

*Last Updated: October 29, 2025*
