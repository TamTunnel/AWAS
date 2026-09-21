# Agent Authentication with Sovereign-Identity Mandates

Status: proposal. This document describes how a website that publishes an
AWAS manifest can authenticate AI agents **without passwords, sessions, or
OTP codes**, using signed mandates from
[sovereign-identity](https://github.com/TamTunnel/sovereign-identity).
AWAS and sovereign-identity are separate specifications; this document defines
how they compose. AWAS describes *what an agent may do* on a website;
sovereign-identity proves *who the agent is and what its owner allowed*.

## The problem

AWAS gives agents structured actions (intent, schemas, idempotency, dry-run)
but does not define authentication. Today an agent acting for a user on a
website needs the user's passwords, sessions, or one-time codes. That does not
scale, and it trains users to hand credentials to software.

## The binding

A site declares mandate authentication in its manifest's
`authentication` object:

```json
"authentication": {
  "required": true,
  "methods": ["mandate"],
  "mandate": {
    "issuer": "https://github.com/TamTunnel/sovereign-identity",
    "required_scope": ["purchase"],
    "max_amount_usd": 500
  }
}
```

`"mandate"` is a registered value of `authentication.methods` (see
SPECIFICATION.md, Authentication Object). An agent acting for an owner presents
a **mandate chain**:

```
Owner DID --(agency grant, JWS)--> Agent DID --(task mandate, JWS)--> Website
```

The task mandate is sent on the action request:

```http
Authorization: Mandate <compact JWS of the task mandate>
```

The task mandate embeds the agency grant (in its `grant` claim), so one header
carries the whole chain. No login endpoint, no token exchange, no shared
secret.

## Mandate contents

Task mandate (signed by the agent's `did:key`, short-lived):

```json
{
  "iss": "did:key:z...agent",
  "sub": "did:key:z...agent",
  "aud": "example-shop.com",
  "iat": 1758490000,
  "exp": 1758493600,
  "jti": "uuid",
  "claims": { "task": "Buy coffee beans", "scope": ["purchase"],
              "amount_limit": 45, "currency": "USD" },
  "grant": "<compact JWS of the agency grant>"
}
```

Agency grant (signed by the owner's `did:key`, long-lived, issued once):

```json
{
  "iss": "did:key:z...owner",
  "sub": "did:key:z...agent",
  "aud": "sovereign-identity/agency",
  "iat": 1758400000,
  "exp": 1789936000,
  "jti": "uuid",
  "claims": { "scope": ["purchase", "read"], "amount_limit": 500,
              "currency": "USD" }
}
```

JWS headers use `alg: EdDSA`, `kid: <did>#key-1`. Full field semantics and the
normative binding live in
[`docs/AWAS-BINDING.md`](https://github.com/TamTunnel/sovereign-identity/blob/main/docs/AWAS-BINDING.md)
in the sovereign-identity repo.

## Website verification (normative)

On receiving an action request with a mandate, the site MUST:

1. Verify the task mandate's EdDSA signature by resolving the `iss` `did:key`
   (offline: base58btc-decode the identifier, check the `0xed01` Ed25519
   multicodec prefix).
2. Reject if `exp` is past or `iat` is implausibly in the future (allow ~60s
   clock skew).
3. Reject if `aud` does not match the site's own identity.
4. Reject if `jti` was seen before (replay ledger, server-side).
5. Verify the embedded agency grant's signature against the owner's `did:key`;
   reject if its `aud` is not `sovereign-identity/agency`, if it is expired,
   or if its `sub` does not equal the task mandate's `iss`.
6. Reject if the task's `scope` is not a subset of the grant's `scope`, if the
   task's `amount_limit` exceeds the grant's, or if the action's
   `required_scope` is not satisfied.

All checks are offline cryptography plus a local replay store. No central
authority, no account system, no shared secrets. A reference verifier is part
of the sovereign-identity repo.

## Privacy

- Agents SHOULD use a fresh **pairwise DID** per site for browsing and
  read-only access, and only present the authorized agent DID (with mandate)
  when performing actions. This prevents cross-site correlation of the owner's
  activity.
- Mandates SHOULD carry short expiries (minutes to hours). The agency grant
  carries the long-lived authority and can be rotated by the owner at any time.

## Worked example

`example-shop.com` publishes an AWAS manifest with a `purchase` action whose
`authentication.methods` is `["mandate"]`, `required_scope: ["purchase"]`,
`max_amount_usd: 500`. An owner grants their agent scope `["purchase",
"read"]` with a $500 limit. The agent wants to buy coffee beans ($45):

1. Agent builds a task mandate: `aud=example-shop.com`, `scope=["purchase"]`,
   `amount_limit=45`, TTL 1 hour, embeds the grant, signs with its key.
2. Agent calls the AWAS `purchase` action with
   `Authorization: Mandate <jws>`.
3. The site runs the six verification steps, checks `purchase` against the
   action's `required_scope`, and executes. On success it MAY return a
   countersigned receipt for the owner's audit trail.

## Open questions

- **Revocation:** short TTLs bound the damage; a revocation list / OCSP-style
  check is future work.
- **Owner DID discovery:** how a website learns the owner's DID out of band
  (published profile, `.well-known`, first-contact pairing).
- **Selective disclosure:** SD-JWT attribute proofs (age, residency) as a
  complement to mandates for read-only actions.
