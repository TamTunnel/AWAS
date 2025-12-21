# Frequently Asked Questions (FAQ)

## General Questions

### What is AWAS?

AWAS (AI Web Action Standard) is an open-source specification that enables AI browsers and agents to interact with websites through machine-readable action definitions, without disrupting traditional human browsing.

### Why do we need AWAS?

Current AI browsers resort to slow browser automation that mimics human clicking. AWAS provides a structured, efficient way for AI agents to understand and execute website actions, similar to how Schema.org helps search engines understand content.

### Is AWAS compatible with existing web standards?

Yes! AWAS is designed to work alongside existing standards like HTML5, Schema.org, OpenAPI, and WAI-ARIA. It uses HTML data attributes and .well-known URIs that are ignored by traditional browsers.

### Who should implement AWAS?

- **Website owners** who want their sites to work with AI browsers
- **E-commerce platforms** looking to enable AI-assisted shopping
- **SaaS applications** wanting AI agent integration
- **AI browser developers** building agentic browsing experiences

## Implementation Questions

### How long does it take to implement AWAS?

- **Basic (Level 1)**: 30 minutes - Just add the manifest file
- **Standard (Level 2)**: 2-4 hours - Add HTML attributes
- **Complete (Level 3)**: 4-8 hours - Full server integration

### Do I need to change my existing code?

No! AWAS uses progressive enhancement. You add new attributes and files alongside your existing code without modifying it.

### Will AWAS break my website for regular users?

No. Traditional browsers completely ignore AWAS attributes and files. Your site works exactly the same for human users.

### Can I implement AWAS incrementally?

Yes! Start with one or two actions, test them, then gradually add more. You don't need to implement everything at once.

### What programming languages are supported?

AWAS is language-agnostic. We provide reference implementations for:
- JavaScript (client-side)
- Python/Flask
- Node.js/Express
- PHP
- Ruby/Rails

### Do I need to expose new APIs?

Not necessarily. AWAS can work with your existing APIs. The manifest simply describes how to call them in a machine-readable way.

## Security Questions

### Is AWAS secure?

Yes, when implemented correctly. AWAS includes:
- Built-in rate limiting
- Authentication requirements
- Input validation specifications
- Action permission systems
- Audit logging capabilities

See [SECURITY.md](./SECURITY.md) for detailed guidelines.

### How do I prevent abuse by AI agents?

1. Implement rate limiting (built into AWAS)
2. Require authentication for sensitive actions
3. Use action-level permissions
4. Monitor AI agent activity through logs
5. Restrict sensitive actions (checkout, payment) to human verification

### Can malicious AI agents exploit my site?

No more than traditional bots. AWAS doesn't create new attack vectors—all the same security practices apply. In fact, AWAS makes it easier to identify and control AI agents.

### Should I allow AI agents to make purchases?

We recommend requiring human verification for sensitive actions like checkout and payment. AWAS supports marking actions as requiring human confirmation.

## Technical Questions

### What's the difference between AWAS and OpenAPI?

- **OpenAPI**: Describes API endpoints and contracts
- **AWAS**: Bridges HTML interfaces with AI-executable actions

AWAS complements OpenAPI by adding web page context and UI element mapping.

### How does AWAS relate to Schema.org?

- **Schema.org**: Describes *what* something is (entities, content)
- **AWAS**: Describes *what you can do* (actions, interactions)

They work together—use both for best results.

### Does AWAS work with Single Page Applications (SPAs)?

Yes! AWAS works with React, Vue, Angular, and other SPA frameworks. You can add attributes to your components and serve the manifest from your server.

### Can AWAS handle dynamic content?

Yes. For dynamically loaded content, AI agents can re-parse the DOM to find new actions, or you can provide API endpoints that return action definitions.

### What about WebSockets and real-time features?

AWAS v1.0 focuses on HTTP-based actions. Real-time capabilities are planned for future versions. You can currently expose WebSocket endpoints in your manifest.

## Compatibility Questions

### Which AI browsers support AWAS?

AWAS is a new standard. As AI browsers like Atlas and Comet mature, we expect them to adopt AWAS. Early adoption helps drive standardization.

### Does AWAS work with voice assistants?

While designed for AI browsers, the structured action format can benefit voice assistants, chatbots, and other AI agents.

### Is AWAS mobile-friendly?

Yes! AWAS works identically on desktop and mobile. The manifest and attributes are device-agnostic.

### Can I use AWAS with my CMS (WordPress, Drupal, etc.)?

Yes! AWAS can be added to any CMS. We provide specific guides for popular platforms in the implementation docs.

## Business Questions

### What are the benefits for my business?

- **Better discoverability**: AI browsers find and understand your site
- **Reduced server load**: Efficient API calls vs. DOM scraping
- **Future-proof**: Ready for the AI-driven web
- **Competitive advantage**: Early adopters rank higher in AI results
- **Better analytics**: Track AI agent interactions separately

### Will implementing AWAS improve my SEO?

Indirectly, yes. While traditional SEO focuses on search engines, AWAS helps with "AI SEO"—ranking in AI browser results and recommendations.

### Do I need to pay to use AWAS?

No! AWAS is completely free and open-source under the Apache 2.0 license. No fees, no royalties.

### Can I contribute to AWAS development?

Absolutely! AWAS is community-driven. See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## Privacy Questions

### Does AWAS respect user privacy?

Yes. AWAS includes privacy directives like:
- `ai-respect-privacy: true`
- `ai-no-data-training: true`
- Human verification for sensitive actions

### How do I comply with GDPR/CCPA when using AWAS?

AWAS doesn't change your privacy obligations. Apply the same privacy practices you use for traditional users. The audit logging features can help with compliance.

### Can AI agents access private user data?

Only if you explicitly allow it. AWAS respects your existing authentication and authorization systems. Sensitive data should require authentication just like for human users.

## Troubleshooting

### My manifest isn't being recognized

Check:
1. File is at `/.well-known/ai-actions.json`
2. Server returns correct content-type: `application/json`
3. File is valid JSON (use a validator)
4. Discovery link is in HTML `<head>`

### Rate limiting isn't working

Ensure:
1. Middleware is properly installed
2. AI agent detection is working (check for `X-AI-Agent` header)
3. Rate limit configuration is correct
4. Redis or other storage backend is running (if used)

### Actions aren't executing

Verify:
1. Action IDs match between manifest and HTML
2. Endpoints are accessible
3. CORS headers are set correctly
4. Input validation passes
5. Check server logs for errors

### Getting CORS errors

Add appropriate headers:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, X-AI-Agent
```

## Future of AWAS

### What's next for AWAS?

Roadmap includes:
- Workflow definitions (multi-step actions)
- Real-time update capabilities
- WebSocket support
- Integration with MCP and A2A protocols
- Visual editor for manifest creation
- Testing and validation tools

### How can I stay updated?

- Watch the [GitHub repository](https://github.com/TamTunnel/awas)
- Join [Discussions](https://github.com/TamTunnel/awas/discussions)
- Follow release notes and changelog

### Can AWAS become a W3C standard?

That's the goal!! Community adoption and feedback will help AWAS evolve into a formal web standard.

## Still Have Questions?

- Check the [full documentation](./SPECIFICATION.md)
- Ask in [GitHub Discussions](https://github.com/TamTunnel/awas/discussions)
- Open an [issue](https://github.com/TamTunnel/awas/issues)

---

*Last Updated: October 29, 2025*
