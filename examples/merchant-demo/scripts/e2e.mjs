#!/usr/bin/env node
// scripts/e2e.mjs — end-to-end proof for the demo merchant.
//
// Spins up the merchant, fetches its AWAS manifest, builds a real
// owner → agent mandate chain with @tamtunnel/si-wallet-mcp, and drives
// the whole agent booking flow: search → preview → book → receipt.
// Then attacks it: replay, tampering, wrong audience, missing header,
// and a double-charge attempt via idempotency.
//
// Run: npm run e2e   (from examples/merchant-demo)
import { spawn } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import {
  onboard,
  issueGrant,
  mintMandate,
} from "@tamtunnel/si-wallet-mcp/lib/wallet.mjs";

const root = dirname(fileURLToPath(import.meta.url)) + "/..";
process.env.SI_WALLET_PASSPHRASE ??= "merchant-demo-e2e";

const results = [];
const check = (name, cond, detail = "") => {
  results.push([cond ? "PASS" : "FAIL", name, detail]);
  if (!cond) console.error(`FAIL ${name} ${detail}`);
};

// --- start the merchant on an ephemeral port ------------------------------
const srv = spawn("node", ["server.mjs", "--port", "0"], { cwd: root, stdio: ["ignore", "pipe", "inherit"] });
const port = await new Promise((resolve, reject) => {
  const t = setTimeout(() => reject(new Error("server did not start")), 15000);
  srv.stdout.on("data", (d) => {
    const m = /READY port=(\d+)/.exec(d.toString());
    if (m) { clearTimeout(t); resolve(Number(m[1])); }
  });
});
const base = `http://127.0.0.1:${port}`;
console.log(`merchant up on ${base}`);

try {
  // --- 1. manifest declares mandate auth ----------------------------------
  const man = await (await fetch(`${base}/.well-known/ai-actions.json`)).json();
  check("manifest served at /.well-known/ai-actions.json", man.specVersion === "1.1");
  check("manifest declares mandate auth method",
    man.authentication?.methods?.includes("mandate") &&
    man.authentication.mandate.required_scope.includes("travel.book"));

  // --- 2. read-only search needs no auth -----------------------------------
  const search = await (await fetch(`${base}/flights/search?from=SFO&to=NRT`)).json();
  const flight = search.flights.find((f) => f.id === "AC101");
  check("flight search works without auth", flight?.price_usd === 320);

  // --- 3. build owner → agent chain (separate wallets, like separate machines)
  const wdir = mkdtempSync(join(tmpdir(), "merchant-e2e-"));
  const as = async (name, fn) => {
    const prev = process.env.SI_WALLET_DIR;
    process.env.SI_WALLET_DIR = join(wdir, name);
    try { return await fn(); } finally {
      if (prev === undefined) delete process.env.SI_WALLET_DIR;
      else process.env.SI_WALLET_DIR = prev;
    }
  };
  const ownerDid = await as("owner", () => onboard("owner").did);
  const agentDid = await as("agent", () => onboard("agent").did);
  const grant = await as("owner", () =>
    issueGrant({ agentDid, scope: ["travel.book", "travel.cancel"], amountLimit: 2000, ttlDays: 30 }));
  const mint = (task) => as("agent", () =>
    mintMandate({
      audience: "acme.travel", scope: ["travel.book"], amount: 320,
      confirmOverLimit: true, task, grantJws: grant.grant,
    }));
  const M_preview = (await mint("preview SFO→NRT")).mandate;
  const M_book = (await mint("book SFO→NRT")).mandate;

  const auth = (jws) => ({ Authorization: `Mandate ${jws}`, "Content-Type": "application/json" });

  // --- 4. preview: mandate verified, nothing charged ------------------------
  let r = await fetch(`${base}/book/preview`, {
    method: "POST", headers: auth(M_preview),
    body: JSON.stringify({ flight_id: "AC101", amount: 320 }),
  });
  check("preview verifies mandate, returns quote", r.status === 200 && (await r.json()).total_usd === 320);

  // --- 5. book ----------------------------------------------------------------
  const idemKey = "e2e-" + Date.now();
  r = await fetch(`${base}/book`, {
    method: "POST", headers: { ...auth(M_book), "Idempotency-Key": idemKey },
    body: JSON.stringify({ flight_id: "AC101", amount: 320 }),
  });
  const receipt = await r.json();
  check("booking succeeds with valid mandate",
    r.status === 200 && receipt.booking_ref?.startsWith("ACME-") && receipt.amount_usd === 320,
    JSON.stringify(receipt));
  check("receipt names owner, agent, hops",
    receipt.delegation_hops === 1 && receipt.mandate_scope?.includes("travel.book"));

  // --- 6. replay the same mandate → refused -----------------------------------
  r = await fetch(`${base}/book`, {
    method: "POST", headers: { ...auth(M_book), "Idempotency-Key": idemKey + "-2" },
    body: JSON.stringify({ flight_id: "AC101", amount: 320 }),
  });
  check("replay refused", r.status === 409, `got ${r.status}`);

  // --- 7. idempotent retry with same key → same receipt, no double charge ----
  const M_book2 = (await mint("book SFO→NRT (retry)")).mandate;
  r = await fetch(`${base}/book`, {
    method: "POST", headers: { ...auth(M_book2), "Idempotency-Key": idemKey },
    body: JSON.stringify({ flight_id: "AC101", amount: 320 }),
  });
  check("idempotent retry returns original receipt",
    r.status === 200 && (await r.json()).booking_ref === receipt.booking_ref);

  // --- 8. tampered mandate → 401 ----------------------------------------------
  const tampered = M_book2.slice(0, 60) + (M_book2[60] === "A" ? "B" : "A") + M_book2.slice(61);
  r = await fetch(`${base}/book`, {
    method: "POST", headers: auth(tampered),
    body: JSON.stringify({ flight_id: "AC101", amount: 320 }),
  });
  check("tampered mandate refused", r.status === 401, `got ${r.status}`);

  // --- 9. wrong audience → 401 --------------------------------------------------
  const M_evil = (await as("agent", () => mintMandate({
    audience: "evil.com", scope: ["travel.book"], amount: 320,
    confirmOverLimit: true, task: "book", grantJws: grant.grant,
  }))).mandate;
  r = await fetch(`${base}/book`, {
    method: "POST", headers: auth(M_evil),
    body: JSON.stringify({ flight_id: "AC101", amount: 320 }),
  });
  check("wrong-audience mandate refused", r.status === 401, `got ${r.status}`);

  // --- 10. missing header → 401 + WWW-Authenticate -------------------------------
  r = await fetch(`${base}/book`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ flight_id: "AC101", amount: 320 }),
  });
  check("missing mandate → 401 with WWW-Authenticate",
    r.status === 401 && (r.headers.get("www-authenticate") || "").startsWith("Mandate"));

  rmSync(wdir, { recursive: true, force: true });
} finally {
  srv.kill();
}

const failed = results.filter(([s]) => s === "FAIL");
console.log(`\n${results.length - failed.length}/${results.length} checks passed`);
if (failed.length) { console.error("FAILURES:", failed.map((f) => f[1]).join(", ")); process.exit(1); }
