# AWAS - AI Web Action Standard

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[![Version](https://img.shields.io/badge/version-1.1-blue.svg)](https://github.com/TamTunnel/awas)

**AI Web Action Standard (AWAS)** is an open-source specification that enables AI browsers like Atlas, Comet, and other AI agents to interact with websites through machine-readable action definitions—without disrupting traditional human browsing.

## 🎯 Problem Statement

Current AI browsers resort to slow, fragile browser automation that mimics human clicking. This approach:

- Is computationally expensive
- Breaks with UI changes
- Provides no semantic understanding
- Creates high server load
- Offers poor user experience

## 💡 Solution

AWAS provides a **dual-interface web architecture** where:

- **Human users** browse normally through visual UI
- **AI agents** interact through structured, machine-readable actions

This is achieved through:

1. **AI Action Manifest** - JSON specification of available actions
2. **HTML Data Attributes** - Inline semantic hints for AI agents
3. **Extended Robots.txt** - AI-specific policies and discovery
4. **Discovery Endpoints** - Capability negotiation and metadata
5. **Server Middleware** - Request handling and rate limiting

## ✨ Key Features

- ✅ **Zero Breaking Changes** - Works alongside existing HTML/CSS/JS
- ✅ **Progressive Enhancement** - Add incrementally, page by page
- ✅ **Backwards Compatible** - Traditional browsers unaffected
- ✅ **Security First** - Built-in rate limiting, auth, and permissions
- ✅ **Open Standard** - Royalty-free, community-driven
- ✅ **Framework Agnostic** - Works with any backend/frontend stack

## 🔗 Interoperability

AWAS is designed to be **MCP (Model Context Protocol), A2A (Agent-to-Agent), and ADK (Agent Development Kit) ready**, enabling seamless integration with modern AI agent ecosystems.

### Protocol Support

#### MCP (Model Context Protocol)

AWAS supports MCP through `.well-known/mcp-manifest.json` for standardized AI agent communication:

```json
{
  "name": "awas-site",
  "version": "1.0.0",
  "description": "AWAS-enabled site with MCP support",
  "actions": {
    "discover": "/.well-known/ai-actions.json",
    "execute": "/api/ai-actions/{action_id}"
  },
  "capabilities": ["action-discovery", "action-execution", "state-management"]
}
```

**For AI Agents:**
```javascript
// Discover MCP capabilities
const manifest = await fetch('https://example.com/.well-known/mcp-manifest.json');
const actions = await fetch(manifest.actions.discover);
```

#### A2A & ADK Integration

AWAS can be used as a provider in agent-to-agent communication:

```python
# ADK Integration Example
from agent_dev_kit import Provider

class AWASProvider(Provider):
    def discover_actions(self):
        return fetch_awas_manifest(self.base_url)
    
    def execute_action(self, action_id, params):
        return call_awas_action(action_id, params)
```

## 🚀 Quick Start

### For Website Owners

1. **Create AI Action Manifest** (`/.well-known/ai-actions.json`):

```json
{
  "specVersion": "1.1",
  "lastUpdated": "2025-12-01T00:00:00Z",
  "actions": [
    {
      "id": "search_products",
      "name": "Search Products",
      "description": "Search for products in the catalog",
      "method": "GET",
      "endpoint": "/api/search",
      "intent": "read",
      "sideEffect": "safe",
      "conformanceLevel": "L1",
      "parameters": [
        {
          "name": "query",
          "type": "string",
          "required": true,
          "description": "Search query"
        },
        {
          "name": "category",
          "type": "string",
          "enum": ["electronics", "clothing", "books"],
          "description": "Filter by category"
        }
      ],
      "inputSchema": {
        "type": "object",
        "properties": {
          "query": { "type": "string" },
          "category": { "type": "string", "enum": ["electronics", "clothing", "books"] }
        },
        "required": ["query"]
      },
      "outputSchema": {
        "type": "object",
        "properties": {
          "results": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "id": { "type": "string" },
                "name": { "type": "string" },
                "price": { "type": "number" }
              }
            }
          }
        }
      }
    }
  ]
}

```

2. **Add HTML Data Attributes** (optional enhancement):

```html
<div data-awas-action="search_products" data-awas-element="search-form">
  <input type="text" name="query" data-awas-param="query">
  <select name="category" data-awas-param="category">
    <option value="electronics">Electronics</option>
    <option value="clothing">Clothing</option>
  </select>
  <button data-awas-trigger>Search</button>
</div>
```

3. **Update robots.txt**:

```
User-agent: *
Allow: /

# AI Agent Directives
AI-Action-Manifest: /.well-known/ai-actions.json
AI-Rate-Limit: 60/minute
AI-Auth-Required: Bearer
```

### For AI Browser Developers

```javascript
const AWAS = require('@awas/client');

const client = new AWAS.Client('https://example.com');

// Discover available actions
const manifest = await client.discover();

// Execute an action
const results = await client.executeAction('search_products', {
  query: 'laptop',
  category: 'electronics'
});

console.log(results);
```

## 📖 Documentation

- [Full Specification](./docs/SPECIFICATION.md)
- [Implementation Guide](./docs/IMPLEMENTATION.md)
- [Examples](./examples/)
- [API Reference](./docs/API.md)
- [Security Best Practices](./docs/SECURITY.md)

## 💪 Benefits

### For Website Owners

- **Better AI Rankings** - Structured data helps AI understand your site
- **Reduced Server Load** - Efficient API calls vs. page scraping
- **Control & Visibility** - Define what AI can and cannot do
- **Future-Proof** - Adapt to AI-driven web without redesign
- **Competitive Advantage** - Early adopters rank higher in AI results

### For AI Developers

- **Faster Execution** - Direct action calls vs. DOM automation
- **Reliable Operation** - Resilient to UI changes
- **Rich Semantics** - Understand intent, not just pixels
- **Standard Protocol** - One integration works everywhere

### For Users

- **Faster Results** - AI completes tasks in seconds
- **More Reliable** - Fewer failures and retries
- **Better Privacy** - Explicit permissions and audit trails
- **Improved Experience** - Seamless AI assistance

## 🔐 Security

AWAS includes security features:

- Rate limiting specifications
- Authentication requirements
- Action permission system
- Audit trail capabilities
- Privacy-respecting directives
- CSRF protection guidelines

See [SECURITY.md](./docs/SECURITY.md) for details.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

- Report bugs via [GitHub Issues](https://github.com/TamTunnel/awas/issues)
- Suggest features via [Discussions](https://github.com/TamTunnel/awas/discussions)
- Submit pull requests for improvements

## 📄 License

AWAS is licensed under the **Apache License, Version 2.0**.  
You must include NOTICE and this license when redistributing or creating derivative works.

See [LICENSE](./LICENSE) and [NOTICE](./NOTICE) for details.

> This project was formerly MIT licensed; as of October 29, 2025, AWAS is under Apache 2.0.

## 🙏 Acknowledgments

- Inspired by Schema.org, OpenAPI, and WAI-ARIA standards
- Built for compatibility with MCP (Model Context Protocol) and A2A (Agent2Agent)
- Community feedback from AI browser developers and web developers

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/TamTunnel/awas/issues)
- **Discussions**: [GitHub Discussions](https://github.com/TamTunnel/awas/discussions)
- **Website**: Coming soon

## 🗺️ Roadmap

- [x] v1.0 - Core specification and basic examples
- [x] v1.1 - MCP and A2A/ADK interoperability
- [x] v1.1 - Enhanced discovery, typing, and safety contracts (specVersion, conformance levels L1/L2/L3, typed I/O)
- [ ] v1.2 - Real-time update capabilities
- [ ] v1.3 - Advanced authentication mechanisms
- [ ] v2.0 - Extended protocol integrations

---

**Made with ❤️ for the AI-driven web**
