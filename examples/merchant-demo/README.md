# Demo merchant: the website side of AWAS mandate authentication

Acme Travel is a fictional flight-booking site that adopted AWAS agent
authentication end to end. It is the reference implementation for
[AGENT-AUTHENTICATION.md](../../AGENT-AUTHENTICATION.md): what a website
actually changes to accept AI-agent bookings without passwords, sessions,
or OTP codes.

## Run it

```bash
npm install
npm start                  # http://localhost:8788
npm run e2e                # 11/11 checks: booking flow + five attacks refused
```

The e2e script starts the merchant, fetches its AWAS manifest, builds a real
owner → agent mandate chain with `@tamtunnel/si-wallet-mcp`, and drives the
full agent flow: search → preview → book → receipt. Then it attacks:
replay, tampering, wrong audience, missing header — all refused — plus an
idempotent retry that returns the original receipt instead of double-charging.

## The website-side diff

Three things, and only three:

**1. Publish the manifest** (`well-known/ai-actions.json`, served at
`/.well-known/ai-actions.json`). The relevant part:

```json
"authentication": {
  "required": true,
  "methods": ["mandate"],
  "mandate": {
    "issuer": "https://github.com/TamTunnel/sovereign-identity",
    "required_scope": ["travel.book"],
    "max_amount_usd": 500
  }
}
```

**2. Drop in the middleware** (`lib/mandate-auth.mjs`, ~60 lines with
comments). On your booking routes:

```js
import { requireMandate } from "./lib/mandate-auth.mjs";

app.post("/book",
  requireMandate({ audience: "your-site.com", requiredScope: "travel.book", maxAmountUsd: 500 }),
  (req, res) => {
    // req.mandate = { owner, agent, hops, task, scope, amountLimit }
    // ... charge and fulfill, exactly as before
  });
```

It enforces the normative verification steps from AGENT-AUTHENTICATION.md:
signature chain, expiry, audience, replay ledger, grant binding, and
scope/amount confinement — all offline cryptography plus a local replay
store. No central authority, no account system, no shared secrets.

**3. Depend on the verifier**: `"@tamtunnel/si-wallet-mcp": "^0.1.0"`.
The middleware calls its `verifyChain`; the merchant keeps its own replay
ledger in `.merchant-data/` (forced server-side — a client-supplied
`SI_WALLET_DIR` must never leak in).

## Why a site would do this

The pitch is checkout reliability, not trust infrastructure:

- **Agents complete purchases.** Today an agent booking a flight needs the
  user's password, session cookies, or a one-time code texted mid-flow —
  and checkouts die at each of those steps. A mandate arrives in one
  `Authorization` header and the booking completes.
- **Every booking carries its authorization.** The receipt names the owner
  DID, the agent DID, the delegation hops, and the confined scope/amount.
  Chargebacks get harder to argue with: the signature chain *is* the proof
  of who authorized what.
- **Least privilege by construction.** The agent can't exceed the scope or
  amount its owner granted — the website enforces the owner's own limits,
  so the site never has to guess what the user would have allowed.
- **No credential handling.** The site never sees, stores, or leaks user
  passwords or sessions for agent traffic, because there aren't any.

## Adapting it to a real site

- Set `audience` to your site's identity (must match the mandate `aud`).
- Set `requiredScope`/`maxAmountUsd` per action from your manifest.
- Replace the in-memory idempotency store and `.merchant-data` replay
  ledger with Redis/Postgres — the demo keeps them in memory/file for
  clarity, not for production.
- Serve everything over TLS; bearer-style headers over plain HTTP are not
  enough.
- Agents mint one mandate per action (mandates are single-use and cheap to
  mint locally). Preview/dry-run calls get their own mandate — see the e2e.

## Layout

```
examples/merchant-demo/
  server.mjs               # Express app: manifest, storefront, search, preview, book
  lib/mandate-auth.mjs     # the website-side middleware (the diff)
  well-known/ai-actions.json
  scripts/e2e.mjs          # 11 end-to-end checks
```
