// lib/mandate-auth.mjs — the website side of AWAS agent authentication.
//
// Drop this into any Express app, configure it from your AWAS manifest's
// `authentication.mandate` object, and your endpoints accept sovereign-identity
// mandates instead of passwords, sessions, or OTP codes.
//
// Normative verification steps: TamTunnel/AWAS AGENT-AUTHENTICATION.md
// (signature chain, expiry, audience, replay ledger, grant binding,
// scope/amount confinement). Cryptography via @tamtunnel/si-wallet-mcp.
import { verifyChain } from "@tamtunnel/si-wallet-mcp/lib/wallet.mjs";

function rejected(res, reason, status = 401) {
  res.set("WWW-Authenticate", 'Mandate realm="awas"');
  return res.status(status).json({ error: "mandate_rejected", reason });
}

// options: { audience, requiredScope, maxAmountUsd }
//   audience      — this site's identity; must match the mandate's `aud`
//   requiredScope — e.g. "travel.book"; the leaf mandate must include it
//   maxAmountUsd  — site-wide cap for the action (from the manifest)
export function requireMandate({ audience, requiredScope, maxAmountUsd }) {
  return async (req, res, next) => {
    const m = /^Mandate\s+(\S+)$/i.exec(req.get("authorization") || "");
    if (!m) return rejected(res, "missing or malformed Authorization: Mandate header");

    let v;
    try {
      v = await verifyChain({ mandateJws: m[1], expectedAudience: audience });
    } catch {
      return rejected(res, "mandate verification failed");
    }
    if (!v.ok) {
      return /replay/i.test(v.reason)
        ? rejected(res, v.reason, 409)
        : rejected(res, v.reason);
    }

    const leaf = v.chain[0];
    if (requiredScope && !leaf.scope.includes(requiredScope)) {
      return rejected(res, `mandate scope [${leaf.scope}] lacks required scope "${requiredScope}"`);
    }
    const amount = Number(req.body?.amount ?? 0);
    if (maxAmountUsd != null && amount > maxAmountUsd) {
      return rejected(res, `amount $${amount} exceeds site maximum $${maxAmountUsd}`);
    }
    if (amount > leaf.amount_limit) {
      return rejected(res, `amount $${amount} exceeds mandate limit $${leaf.amount_limit}`);
    }

    req.mandate = {
      owner: v.owner,
      agent: v.agent,
      hops: v.hops,
      task: v.task,
      scope: leaf.scope,
      amountLimit: leaf.amount_limit,
    };
    next();
  };
}
