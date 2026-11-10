"use strict";
const assert = require("node:assert/strict");
const { webcrypto } = require("node:crypto");
const { createResearchLedger, storageKey } = require("./research-ledger.js");

class MemoryStorage {
  constructor() { this.values = new Map(); }
  getItem(key) { return this.values.has(key) ? this.values.get(key) : null; }
  setItem(key, value) { this.values.set(key, value); }
}

(async () => {
  const storage = new MemoryStorage();
  let id = 0;
  const ledger = createResearchLedger({
    storage,
    crypto: webcrypto,
    now: () => "2026-11-10T12:00:00.000Z",
    makeId: () => "event-" + (++id)
  });

  assert.deepEqual(await ledger.verify(), {
    intact: true, checked: 0, head: "GENESIS", reason: "verified"
  });

  const proposal = await ledger.append({
    type: "proposal", actorType: "agent", actorId: "agent.analysis",
    actorRole: "researcher", classification: "hypothesis",
    summary: "Test whether a frozen input set reproduces the same result",
    references: ["dataset:fixture-01", "method:median-v1"]
  });
  const result = await ledger.append({
    type: "result", actorType: "agent", actorId: "agent.analysis",
    actorRole: "researcher", classification: "simulation",
    summary: "Synthetic fixture reproduced the expected deterministic output",
    references: ["test:fixture-01"]
  });
  const review = await ledger.append({
    type: "review", actorType: "human", actorId: "reviewer.local",
    actorRole: "independent-reviewer", classification: "derived",
    summary: "Reviewed the method and fixture; no real-world validation implied",
    proposalId: proposal.id
  });
  const approval = await ledger.append({
    type: "approval", actorType: "human", actorId: "owner.local",
    actorRole: "project-owner", classification: "derived",
    summary: "Approved a bounded synthetic test only",
    proposalId: proposal.id, decision: "approved"
  });

  assert.equal(result.sequence, 2);
  assert.equal(review.proposalId, proposal.id);
  assert.equal(approval.decision, "approved");
  assert.equal((await ledger.verify()).intact, true);
  assert.equal(ledger.list().length, 4);
  assert.match(ledger.exportJSON(), /SSSWET-RESEARCH-LEDGER/);

  await assert.rejects(() => ledger.append({
    type: "approval", actorType: "agent", actorId: "agent.bot",
    actorRole: "researcher", classification: "derived",
    summary: "An agent must not self-approve", proposalId: proposal.id, decision: "approved"
  }), /Only a human actor/);
  await assert.rejects(() => ledger.append({
    type: "approval", actorType: "human", actorId: "reviewer.local",
    actorRole: "reviewer", classification: "derived",
    summary: "Unknown proposal", proposalId: "missing", decision: "approved"
  }), /existing proposal/);
  await assert.rejects(() => ledger.append({
    type: "result", actorType: "agent", actorId: "agent.bot",
    actorRole: "researcher", classification: "observation",
    summary: "Do not store raw material", prompt: "private prompt"
  }), /Unsupported event field/);
  await assert.rejects(() => ledger.append({
    type: "result", actorType: "agent", actorId: "agent.bot",
    actorRole: "researcher", classification: "observation",
    summary: " ".repeat(501)
  }), /summary/);

  const corrupted = JSON.parse(storage.getItem(storageKey));
  corrupted[1].summary = "tampered";
  storage.setItem(storageKey, JSON.stringify(corrupted));
  const audit = await ledger.verify();
  assert.equal(audit.intact, false);
  assert.equal(audit.reason, "hash_mismatch");
  await assert.rejects(() => ledger.append({
    type: "result", actorType: "agent", actorId: "agent.bot",
    actorRole: "researcher", classification: "derived",
    summary: "Cannot append after integrity failure"
  }), /invalid ledger/);

  const malformedStorage = new MemoryStorage();
  malformedStorage.setItem(storageKey, "{not-json");
  const malformed = createResearchLedger({ storage: malformedStorage, crypto: webcrypto });
  assert.equal((await malformed.verify()).reason, "storage_invalid");

  console.log("Research-ledger tests passed: hash chain, bounded schema, proposal linkage, human-only approval, tamper detection and fail-closed append.");
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});