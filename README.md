# AWAS - AI Web Action Standard
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/TamTunnel/awas)

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
const mcpManifest = await fetch('https://example.com/.well-known/mcp-manifest.json');
const capabilities = await mcpManifest.json();

// Execute actions via MCP
const actionsUrl = capabilities.actions.discover;
const actions = await fetch(actionsUrl).then(r => r.json());
```

#### A2A/ADK (Agent-to-Agent / Agent Development Kit)
AWAS supports A2A protocol through `.well-known/a2a-manifest.json` for agent-to-agent coordination:

```json
{
  "protocol": "a2a",
  "version": "1.0",
  "capabilities": {
    "action_discovery": true,
    "action_execution": true,
    "delegation": false
  },
  "endpoints": {
    "actions": "/.well-known/ai-actions.json",
    "execute": "/api/ai-actions"
  }
}
```

**For AI Agents:**
```python
import httpx

# Discover A2A capabilities
async with httpx.AsyncClient() as client:
    a2a_manifest = await client.get('https://example.com/.well-known/a2a-manifest.json')
    manifest = a2a_manifest.json()
    
    # Load available actions
    actions_url = manifest['endpoints']['actions']
    actions = await client.get(actions_url)
```

### Discovery Mechanism

**For Site Implementers:**

1. Create both manifest files in `.well-known/` directory:
   - `.well-known/mcp-manifest.json`
   - `.well-known/a2a-manifest.json`

2. Add discovery links to your HTML `<head>`:
```html
<link rel="mcp-manifest" href="/.well-known/mcp-manifest.json" type="application/json" />
<link rel="a2a-manifest" href="/.well-known/a2a-manifest.json" type="application/json" />
<link rel="ai-actions" href="/.well-known/ai-actions.json" type="application/json" />
```

3. Ensure your AWAS action manifest is accessible and properly formatted.

**For Agent Developers:**

```javascript
// Multi-protocol discovery
async function discoverCapabilities(siteUrl) {
  const protocols = ['mcp-manifest', 'a2a-manifest', 'ai-actions'];
  const capabilities = {};
  
  for (const protocol of protocols) {
    try {
      const response = await fetch(`${siteUrl}/.well-known/${protocol}.json`);
      if (response.ok) {
        capabilities[protocol] = await response.json();
      }
    } catch (e) {
      console.log(`${protocol} not available`);
    }
  }
  
  return capabilities;
}
```

### Integration Examples

**Site Implementation:**
```javascript
// Express.js middleware for multi-protocol support
app.get('/.well-known/:manifest', (req, res) => {
  const manifests = {
    'mcp-manifest.json': mcpConfig,
    'a2a-manifest.json': a2aConfig,
    'ai-actions.json': awasActions
  };
  
  const manifest = manifests[req.params.manifest];
  if (manifest) {
    res.json(manifest);
  } else {
    res.status(404).send('Manifest not found');
  }
});
```

**Agent Usage:**
```python
# Python agent using AWAS with MCP/A2A
class AWASAgent:
    async def connect(self, site_url):
        # Check for protocol support
        self.mcp = await self.check_protocol(site_url, 'mcp-manifest')
        self.a2a = await self.check_protocol(site_url, 'a2a-manifest')
        self.awas = await self.load_actions(site_url)
        
    async def execute_action(self, action_id, params):
        # Use the most appropriate protocol
        if self.mcp and 'execute' in self.mcp['actions']:
            return await self.mcp_execute(action_id, params)
        elif self.a2a and 'execute' in self.a2a['endpoints']:
            return await self.a2a_execute(action_id, params)
        else:
            return await self.awas_execute(action_id, params)
```

For complete interoperability implementation details, see the [Interoperability Wiki Page](https://github.com/TamTunnel/awas/wiki/Interoperability).

## 🚀 Quick Start

### For Website Owners

1. **Create Action Manifest**
```bash
mkdir -p .well-known
# Copy examples/ai-actions.json to .well-known/ai-actions.json
```

2. **Add Discovery Link to HTML**
```html
<link rel="ai-actions" type="application/json" href="/.well-known/ai-actions.json" />
```

3. **Add Data Attributes to Interactive Elements**
```html
<button data-ai-action="add_to_cart"
    data-ai-action-type="form_submission">
    Add to Cart
</button>
```

4. **See full documentation:**
- [SPECIFICATION.md](./SPECIFICATION.md) - Complete technical spec
- [IMPLEMENTATION.md](./IMPLEMENTATION.md) - Implementation guide
- [Examples](./examples/) - Code samples

### For AI Agent Developers

1. **Discover Available Actions**
```javascript
const response = await fetch('https://example.com/.well-known/ai-actions.json');
const manifest = await response.json();
```

2. **Parse Action Definitions**
```javascript
const actions = manifest.actions;
const searchAction = actions.find(a => a.id === 'search');
```

3. **Execute Actions**
```javascript
const result = await fetch(searchAction.endpoint, {
  method: searchAction.method,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'laptops' })
});
```

4. **See full documentation:**
- [Agent Implementation Guide](./docs/AGENT_GUIDE.md)
- [API Reference](./docs/API.md)

## 📚 Documentation

- [SPECIFICATION.md](./SPECIFICATION.md) - Complete technical specification
- [IMPLEMENTATION.md](./IMPLEMENTATION.md) - Implementation guide for developers
- [SECURITY.md](./docs/SECURITY.md) - Security guidelines and best practices
- [FAQ.md](./FAQ.md) - Frequently asked questions
- [Examples](./examples/) - Working code examples

## 💼 Use Cases

### For Website Owners
- **Better SEO** - Rank higher in AI-powered search results
- **Reduced Server Load** - Efficient API calls vs. heavy DOM scraping
- **Controlled Access** - Define exactly what AI agents can do
- **Monetization** - Premium actions for authenticated agents
- **Analytics** - Track AI agent interactions separately
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

MIT License - see [LICENSE](./LICENSE) for details.

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
- [x] v1.0.1 - MCP and A2A/ADK interoperability
- [ ] v1.1 - Workflow definitions and multi-step actions
- [ ] v1.2 - Real-time update capabilities
- [ ] v1.3 - Advanced authentication mechanisms
- [ ] v2.0 - Extended protocol integrations

---
**Made with ❤️ for the AI-driven web**
