#!/usr/bin/env node
// server.mjs — Acme Travel demo merchant.
//
// A minimal website that adopted AWAS mandate authentication:
//   1. publishes its AI Action Manifest at /.well-known/ai-actions.json
//   2. accepts `Authorization: Mandate <JWS>` on booking endpoints
//      via lib/mandate-auth.mjs (the ~40-line website-side diff)
//
// Run:  npm install && npm start        (node server.mjs --port 8788)
// Test: npm run e2e
import express from "express";
import { readFileSync } from "node:fs";
import { requireMandate } from "./lib/mandate-auth.mjs";

const AUDIENCE = "acme.travel"; // this site's identity; mandates must name it in `aud`
const { required_scope, max_amount_usd } = JSON.parse(
  readFileSync(new URL("./well-known/ai-actions.json", import.meta.url))
).authentication.mandate;

// The merchant's replay ledger. Forced to the merchant's own directory:
// a client-supplied SI_WALLET_DIR must never leak in here.
process.env.SI_WALLET_DIR = new URL("./.merchant-data", import.meta.url).pathname;

const manifest = JSON.parse(
  readFileSync(new URL("./well-known/ai-actions.json", import.meta.url))
);

const FLIGHTS = [
  { id: "AC101", from: "SFO", to: "NRT", departs: "2026-10-04T09:15", price_usd: 320 },
  { id: "AC102", from: "SFO", to: "NRT", departs: "2026-10-04T17:40", price_usd: 410 },
  { id: "AC201", from: "NRT", to: "SFO", departs: "2026-10-11T11:05", price_usd: 335 },
];

const app = express();
app.use(express.json());
const short = (did) => did.slice(0, 24) + "…";

// --- manifest (RFC 8615) -------------------------------------------------
app.get("/.well-known/ai-actions.json", (req, res) => res.json(manifest));

// --- storefront ----------------------------------------------------------
app.get("/", (req, res) =>
  res.type("html").send(`<!doctype html><html><head><title>Acme Travel</title>
<style>body{font-family:system-ui;max-width:640px;margin:40px auto;padding:0 16px}</style>
</head><body>
<h1>✈️ Acme Travel</h1>
<p><strong>AI agents welcome.</strong> This site publishes an
<a href="/.well-known/ai-actions.json">AWAS manifest</a> and accepts
sovereign-identity mandates — no passwords, sessions, or OTP codes.</p>
<h2>Search flights</h2>
<form id="f">From <input name="from" value="SFO" size="4"> To <input name="to" value="NRT" size="4">
<button>Search</button></form><pre id="out"></pre>
<script>f.onsubmit=async e=>{e.preventDefault();
const q=new URLSearchParams(new FormData(f)).toString();
out.textContent=JSON.stringify(await (await fetch('/flights/search?'+q)).json(),null,2)}</script>
<h2>For agents</h2>
<p>Booking endpoints require <code>Authorization: Mandate &lt;JWS&gt;</code>.
Mint one with <code>@tamtunnel/si-wallet-mcp</code>, then:</p>
<pre>curl -X POST localhost:PORT/book \\
  -H "Authorization: Mandate $MANDATE" \\
  -H "Idempotency-Key: $RANDOM" \\
  -H "Content-Type: application/json" \\
  -d '{"flight_id":"AC101","amount":320}'</pre>
</body></html>`)
);

// --- read-only action: no auth -------------------------------------------
app.get("/flights/search", (req, res) => {
  const { from, to } = req.query;
  if (!from || !to) return res.status(400).json({ error: "from and to are required" });
  res.json({
    flights: FLIGHTS.filter(
      (f) => f.from === String(from).toUpperCase() && f.to === String(to).toUpperCase()
    ),
  });
});

const bookAuth = requireMandate({
  audience: AUDIENCE,
  requiredScope: required_scope[0],
  maxAmountUsd: max_amount_usd,
});

// --- dry-run: verify mandate, quote the itinerary, charge nothing ---------
app.post("/book/preview", bookAuth, (req, res) => {
  const flight = FLIGHTS.find((f) => f.id === req.body?.flight_id);
  if (!flight || req.body.amount !== flight.price_usd) {
    return res.status(422).json({ error: "flight_id/amount do not match a listed flight" });
  }
  res.json({ preview: true, flight, total_usd: flight.price_usd, authorized_for: short(req.mandate.owner) });
});

// --- L3: idempotent booking -----------------------------------------------
const idempotencyStore = new Map(); // prod: Redis/Postgres, not memory
app.post(
  "/book",
  (req, res, next) => {
    const key = req.get("Idempotency-Key");
    if (key && idempotencyStore.has(key)) return res.json(idempotencyStore.get(key));
    next();
  },
  bookAuth,
  (req, res) => {
    const flight = FLIGHTS.find((f) => f.id === req.body?.flight_id);
    if (!flight || req.body.amount !== flight.price_usd) {
      return res.status(422).json({ error: "flight_id/amount do not match a listed flight" });
    }
    const receipt = {
      booking_ref: "ACME-" + Math.random().toString(36).slice(2, 8).toUpperCase(),
      flight,
      amount_usd: flight.price_usd,
      charged_to_owner: short(req.mandate.owner),
      booked_by_agent: short(req.mandate.agent),
      delegation_hops: req.mandate.hops,
      mandate_scope: req.mandate.scope,
    };
    const key = req.get("Idempotency-Key");
    if (key) idempotencyStore.set(key, receipt);
    res.json(receipt);
  }
);

const port = Number(process.argv[process.argv.indexOf("--port") + 1]) || 8788;
const srv = app.listen(port, () => console.log(`READY port=${srv.address().port}`));
