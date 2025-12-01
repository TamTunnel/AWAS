
# 3. IMPLEMENTATION.md
files['docs/IMPLEMENTATION.md'] = '''# AWAS Implementation Guide

This guide provides step-by-step instructions for implementing AWAS on your website.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Phase 1: Basic Setup](#phase-1-basic-setup)
- [Phase 2: HTML Enhancement](#phase-2-html-enhancement)
- [Phase 3: Server Implementation](#phase-3-server-implementation)
- [Phase 4: Testing](#phase-4-testing)
- [Framework-Specific Guides](#framework-specific-guides)

## Prerequisites

- Web server with support for `.well-known` directory
- Ability to add HTML attributes (for Phase 2)
- Backend API endpoints (for full implementation)
- Basic understanding of JSON and REST APIs

## Phase 1: Basic Setup (30 minutes)

### Step 1: Create AI Action Manifest

Create a file at `/.well-known/ai-actions.json`:

```json
{
  "$schema": "https://awas.dev/schema/v1/manifest.json",
  "version": "1.0",
  "name": "My Website Actions",
  "description": "Available actions for AI agents",
  "actions": [
    {
      "id": "search_products",
      "type": "search",
      "name": "Search Products",
      "description": "Search for products by keyword",
      "method": "GET",
      "endpoint": "/api/search",
      "inputs": [
        {
          "name": "q",
          "type": "string",
          "required": true,
          "description": "Search query"
        }
      ]
    }
  ],
  "rate_limits": {
    "requests_per_minute": 60,
    "burst_limit": 10
  },
  "authentication": {
    "required": false
  }
}
```

### Step 2: Configure Web Server

Ensure `.well-known` directory is accessible:

**Apache (.htaccess)**:
```apache
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^.well-known/(.*)$ /.well-known/$1 [L]
</IfModule>

<FilesMatch "ai-actions.json">
    Header set Content-Type "application/json"
    Header set Access-Control-Allow-Origin "*"
</FilesMatch>
```

**Nginx**:
```nginx
location /.well-known/ {
    alias /var/www/html/.well-known/;
    add_header Content-Type application/json;
    add_header Access-Control-Allow-Origin *;
}
```

### Step 3: Add Discovery Links

Add to your HTML `<head>`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Website</title>
    
    <!-- AWAS Discovery -->
    <link rel="ai-actions" href="/.well-known/ai-actions.json" type="application/json">
    
    <!-- Optional: Additional discovery endpoints -->
    <link rel="ai-sitemap" href="/.well-known/ai-sitemap.json" type="application/json">
</head>
<body>
    <!-- Your content -->
</body>
</html>
```

### Step 4: Verify Setup

Test your manifest is accessible:
```bash
curl https://yourwebsite.com/.well-known/ai-actions.json
```

**✅ Checkpoint**: You now have Level 1 compliance!

## Phase 2: HTML Enhancement (2-4 hours)

### Step 1: Identify Interactive Elements

List all user actions on your pages:
- Form submissions
- Search functionality
- Filters and sorting
- Add to cart
- Navigation actions

### Step 2: Add Data Attributes

Enhance your HTML with AWAS attributes:

**Search Form Example**:
```html
<form 
    role="search"
    data-ai-action="search_products"
    data-ai-action-type="search"
    data-ai-endpoint="/api/search"
    data-ai-method="GET"
    aria-label="Product search">
    
    <input 
        type="search" 
        name="q" 
        placeholder="Search products..."
        data-ai-param="q"
        data-ai-param-type="string"
        data-ai-param-required="true"
        aria-label="Search query">
    
    <select 
        name="category"
        data-ai-param="category"
        data-ai-param-type="string"
        data-ai-param-required="false"
        aria-label="Product category">
        <option value="">All Categories</option>
        <option value="electronics">Electronics</option>
        <option value="clothing">Clothing</option>
    </select>
    
    <button 
        type="submit"
        data-ai-action-trigger="search_products"
        aria-label="Submit search">
        Search
    </button>
</form>
```

**Add to Cart Example**:
```html
<form 
    id="add-to-cart-form"
    data-ai-action="add_to_cart"
    data-ai-action-type="form_submission"
    data-ai-endpoint="/api/cart/add"
    data-ai-method="POST">
    
    <input 
        type="hidden" 
        name="product_id" 
        value="PROD-123"
        data-ai-param="product_id"
        data-ai-param-type="string"
        data-ai-param-required="true">
    
    <label>
        Quantity:
        <input 
            type="number" 
            name="quantity" 
            value="1" 
            min="1"
            data-ai-param="quantity"
            data-ai-param-type="integer"
            data-ai-param-default="1"
            data-ai-param-required="false">
    </label>
    
    <button 
        type="submit"
        data-ai-action-trigger="add_to_cart">
        Add to Cart
    </button>
</form>
```

**Product Detail Page**:
```html
<main data-ai-content="primary" data-ai-intent="product-detail">
    <article 
        itemscope 
        itemtype="https://schema.org/Product"
        data-ai-entity="product"
        data-ai-id="PROD-123">
        
        <h1 
            itemprop="name" 
            data-ai-field="product-name">
            Premium Wireless Headphones
        </h1>
        
        <div 
            data-ai-field="product-price" 
            itemprop="offers" 
            itemscope 
            itemtype="https://schema.org/Offer">
            <span itemprop="price" content="299.99">$299.99</span>
            <meta itemprop="priceCurrency" content="USD">
        </div>
        
        <div 
            data-ai-field="product-description"
            itemprop="description">
            High-quality noise-canceling headphones...
        </div>
    </article>
</main>
```

### Step 3: Update Your Manifest

Add corresponding actions to your manifest for each enhanced element.

**✅ Checkpoint**: You now have Level 2 compliance!

## Phase 3: Server Implementation (4-8 hours)

### Step 1: Install Middleware

Choose your platform:

**Node.js/Express**:
```bash
npm install awas-middleware
```

**Python/Flask**:
```bash
pip install awas-flask
```

**PHP**:
```bash
composer require awas/middleware
```

### Step 2: Configure Middleware

**Node.js/Express Example**:
```javascript
const express = require('express');
const { AWASMiddleware } = require('awas-middleware');

const app = express();
const awas = new AWASMiddleware({
    manifestPath: '.well-known/ai-actions.json',
    enableRateLimiting: true,
    enableLogging: true
});

// Apply middleware
app.use(awas.middleware());

// Your routes...
app.post('/api/cart/add', 
    awas.validateAction('add_to_cart'),
    (req, res) => {
        // Your logic
        res.json({ success: true });
    }
);
```

**Python/Flask Example**:
```python
from flask import Flask
from awas import AWASMiddleware

app = Flask(__name__)
awas = AWASMiddleware(
    app, 
    manifest_path='.well-known/ai-actions.json',
    enable_rate_limiting=True
)

@app.route('/api/cart/add', methods=['POST'])
@awas.validate_action('add_to_cart')
def add_to_cart():
    # Your logic
    return {'success': True}
```

### Step 3: Implement AI Agent Detection

Add agent detection to your middleware:

```python
def is_ai_agent(request):
    """Detect if request is from an AI agent"""
    return request.headers.get('X-AI-Agent') == 'true'

@app.before_request
def handle_ai_requests():
    if is_ai_agent(request):
        # Apply AI-specific handling
        g.ai_agent = True
        g.ai_agent_name = request.headers.get('X-AI-Agent-Name', 'Unknown')
```

### Step 4: Implement Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["60 per minute"]
)

@app.route('/api/search')
@limiter.limit("60/minute")
def search():
    # Your search logic
    pass
```

### Step 5: Add AI Capabilities Endpoint

```python
@app.route('/.well-known/ai-capabilities')
def ai_capabilities():
    return {
        "version": "1.0",
        "supported_protocols": ["HTTP/1.1", "HTTP/2"],
        "auth_methods": ["session", "api_key"],
        "rate_limits": {
            "requests_per_minute": 60,
            "burst_limit": 10
        },
        "features": [
            "structured_actions",
            "workflow_support"
        ]
    }
```

### Step 6: Enhance robots.txt

Update your `robots.txt`:

```
# Standard rules
User-agent: *
Allow: /

# AI Browser agents
User-agent: AtlasBot
User-agent: CometBot
User-agent: AI-Browser/*
Disallow: /checkout/
Disallow: /payment/
Allow: /products/
Allow: /api/public/

# AWAS Discovery
# agentic-manifest: /.well-known/ai-actions.json
# ai-capabilities: /.well-known/ai-capabilities
# ai-rate-limit: 60/minute
# ai-allowed-actions: search, filter, view, compare
# ai-restricted-actions: purchase, checkout, payment
# ai-respect-privacy: true

Sitemap: https://yoursite.com/sitemap.xml
```

**✅ Checkpoint**: You now have Level 3 compliance!

## Phase 4: Testing (2-4 hours)

### Step 1: Validate Manifest

Use the AWAS validator:

```bash
npx awas-validator validate .well-known/ai-actions.json
```

### Step 2: Test Endpoints

Test each action endpoint:

```bash
# Test search action
curl -X GET "https://yoursite.com/api/search?q=headphones" \\
  -H "X-AI-Agent: true" \\
  -H "X-AI-Agent-Name: TestBot/1.0"

# Test add to cart
curl -X POST "https://yoursite.com/api/cart/add" \\
  -H "Content-Type: application/json" \\
  -H "X-AI-Agent: true" \\
  -d '{"product_id": "PROD-123", "quantity": 2}'
```

### Step 3: Test Rate Limiting

Verify rate limits are enforced:

```bash
# Send 65 requests (should see 429 after 60)
for i in {1..65}; do
  curl -w "%{http_code}\\n" https://yoursite.com/api/search?q=test
done
```

### Step 4: Browser Compatibility Test

Ensure traditional browsers work normally:
1. Open your site in Chrome, Firefox, Safari
2. Test all interactive features
3. Verify no console errors
4. Confirm visual appearance unchanged

### Step 5: AI Agent Test

If you have access to an AI browser:
1. Have it discover your manifest
2. Execute actions through the AI agent
3. Verify proper functionality
4. Check server logs for AI agent requests

## Framework-Specific Guides

### WordPress

```php
// functions.php
add_action('wp_head', 'add_awas_discovery');
function add_awas_discovery() {
    echo '<link rel="ai-actions" href="' . 
         site_url('/.well-known/ai-actions.json') . 
         '" type="application/json">';
}

// Serve manifest
add_action('init', 'serve_awas_manifest');
function serve_awas_manifest() {
    if ($_SERVER['REQUEST_URI'] === '/.well-known/ai-actions.json') {
        header('Content-Type: application/json');
        readfile(ABSPATH . '.well-known/ai-actions.json');
        exit;
    }
}
```

### React

```jsx
// App.js
import { Helmet } from 'react-helmet';

function App() {
  return (
    <>
      <Helmet>
        <link 
          rel="ai-actions" 
          href="/.well-known/ai-actions.json" 
          type="application/json" 
        />
      </Helmet>
      
      <form 
        data-ai-action="search_products"
        data-ai-action-type="search">
        {/* form content */}
      </form>
    </>
  );
}
```

### Vue.js

```vue
<template>
  <div>
    <component :is="'script'" type="application/ld+json">
      {{ manifestLink }}
    </component>
    
    <form 
      data-ai-action="search_products"
      data-ai-action-type="search"
      @submit="handleSubmit">
      <!-- form content -->
    </form>
  </div>
</template>

<script>
export default {
  head() {
    return {
      link: [
        {
          rel: 'ai-actions',
          href: '/.well-known/ai-actions.json',
          type: 'application/json'
        }
      ]
    }
  }
}
</script>
```

## Troubleshooting

### Manifest Not Found (404)

- Check file permissions
- Verify web server configuration
- Ensure `.well-known` directory exists
- Check for URL rewrite rules blocking access

### CORS Errors

Add CORS headers:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, X-AI-Agent
```

### Rate Limiting Not Working

- Verify middleware is installed correctly
- Check rate limit configuration
- Ensure IP detection is working
- Review server logs for errors

### Actions Not Recognized

- Validate manifest JSON syntax
- Ensure action IDs match between manifest and HTML
- Check for typos in data attribute names
- Verify selectors are correct

## Best Practices

1. **Start Small**: Implement one or two actions first
2. **Test Thoroughly**: Verify both human and AI access work
3. **Monitor Logs**: Watch for AI agent activity and errors
4. **Iterate**: Add more actions based on usage patterns
5. **Document**: Keep your manifest up-to-date with changes
6. **Security**: Always validate inputs server-side
7. **Performance**: Cache manifest files appropriately
8. **Analytics**: Track AI agent usage separately

## Next Steps

- Add more actions to your manifest
- Implement workflow definitions
- Set up monitoring and analytics
- Join the AWAS community
- Share your implementation experience

## Support

- [GitHub Issues](https://github.com/TamTunnel/awas/issues)
- [Documentation](https://awas.dev/docs)
- [Community Forum](https://github.com/TamTunnel/awas/discussions)

---

*Last Updated: October 29, 2025*
'''

print("Created IMPLEMENTATION.md")
print(f"Length: {len(files['docs/IMPLEMENTATION.md'])} characters")
