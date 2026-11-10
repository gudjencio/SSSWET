(() => {
  "use strict";

  const STORAGE_KEY = "ssswet.research-ledger.v1";
  const MAX_EVENTS = 1000;
  const TYPES = new Set(["proposal", "result", "review", "approval"]);
  const CLASSIFICATIONS = new Set(["observation", "derived", "simulation", "hypothesis"]);
  const ACTORS = new Set(["agent", "human", "system"]);

  function canonical(value) {
    if (Array.isArray(value)) return "[" + value.map(canonical).join(",") + "]";
    if (value && typeof value === "object") {
      return "{" + Object.keys(value).sort().map((key) =>
        JSON.stringify(key) + ":" + canonical(value[key])
      ).join(",") + "}";
    }
    return JSON.stringify(value);
  }

  function cleanText(value, field, max) {
    if (typeof value !== "string" || !value.trim() || value.length > max) {
      throw new TypeError(field + " must be a non-empty string of at most " + max + " characters");
    }
    return value.trim();
  }

  function createResearchLedger(options = {}) {
    const storage = options.storage || (typeof localStorage !== "undefined" ? localStorage : null);
    const cryptoApi = options.crypto || (typeof crypto !== "undefined" ? crypto : null);
    const now = options.now || (() => new Date().toISOString());
    const makeId = options.makeId || (() => cryptoApi.randomUUID());
    if (!storage || !cryptoApi?.subtle || typeof storage.getItem !== "function" ||
        typeof storage.setItem !== "function") {
      throw new Error("A local storage adapter and Web Crypto SHA-256 are required");
    }

    function read() {
      const raw = storage.getItem(STORAGE_KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw);
      if (!Array.isArray(parsed) || parsed.length > MAX_EVENTS) {
        throw new Error("Research ledger storage is invalid or exceeds its event limit");
      }
      return parsed;
    }

    async function digest(value) {
      const bytes = new TextEncoder().encode(canonical(value));
      const hash = await cryptoApi.subtle.digest("SHA-256", bytes);
      return Array.from(new Uint8Array(hash), (b) => b.toString(16).padStart(2, "0")).join("");
    }

    async function verify() {
      let events;
      try { events = read(); } catch (error) {
        return { intact: false, checked: 0, reason: "storage_invalid", detail: error.message };
      }
      let previousHash = "GENESIS";
      const ids = new Set();
      for (let index = 0; index < events.length; index += 1) {
        const event = events[index];
        if (!event || event.sequence !== index + 1 || event.previousHash !== previousHash ||
            typeof event.id !== "string" || ids.has(event.id) || typeof event.hash !== "string") {
          return { intact: false, checked: index, reason: "chain_structure_invalid" };
        }
        const { hash, ...body } = event;
        if (await digest(body) !== hash) {
          return { intact: false, checked: index, reason: "hash_mismatch" };
        }
        ids.add(event.id);
        previousHash = hash;
      }
      return { intact: true, checked: events.length, head: previousHash, reason: "verified" };
    }

    async function append(input) {
      if (!input || typeof input !== "object" || Array.isArray(input)) throw new TypeError("An event object is required");
      const allowed = new Set(["type", "actorType", "actorId", "actorRole", "classification", "summary", "references", "proposalId", "decision"]);
      if (Object.keys(input).some((key) => !allowed.has(key))) {
        throw new TypeError("Unsupported event field; raw prompts, datasets and personal data are not accepted");
      }
      const type = input.type;
      const actorType = input.actorType;
      const classification = input.classification;
      if (!TYPES.has(type) || !ACTORS.has(actorType) || !CLASSIFICATIONS.has(classification)) {
        throw new TypeError("Unsupported event type, actor type or evidence classification");
      }
      const actorId = cleanText(input.actorId, "actorId", 80);
      if (!/^[a-zA-Z0-9._:-]+$/.test(actorId)) throw new TypeError("actorId must be a non-identifying agent or system key");
      const actorRole = cleanText(input.actorRole, "actorRole", 80);
      const summary = cleanText(input.summary, "summary", 500);
      const references = input.references === undefined ? [] : input.references;
      if (!Array.isArray(references) || references.length > 20 ||
          references.some((ref) => typeof ref !== "string" || !ref.trim() || ref.length > 300)) {
        throw new TypeError("references must contain at most 20 short source identifiers");
      }
      const events = read();
      if (events.length >= MAX_EVENTS) throw new Error("Research ledger is full; export it before starting a new ledger");
      const verified = await verify();
      if (!verified.intact) throw new Error("Cannot append to an invalid ledger: " + verified.reason);

      let proposalId;
      let decision;
      if (type === "approval" || type === "review") {
        proposalId = cleanText(input.proposalId, "proposalId", 100);
        if (!events.some((event) => event.id === proposalId && event.type === "proposal")) {
          throw new Error("Review or approval must reference an existing proposal");
        }
      }
      if (type === "approval") {
        if (actorType !== "human") throw new Error("Only a human actor may record an approval decision");
        if (!["approved", "rejected"].includes(input.decision)) throw new TypeError("Approval decision must be approved or rejected");
        decision = input.decision;
      } else if (input.decision !== undefined) {
        throw new TypeError("decision is only valid on approval events");
      }

      const body = {
        schemaVersion: 1,
        id: cleanText(makeId(), "event id", 100),
        sequence: events.length + 1,
        recordedAt: cleanText(now(), "recordedAt", 40),
        type,
        actorType,
        actorId,
        actorRole,
        classification,
        summary,
        references: references.map((ref) => ref.trim()),
        ...(proposalId ? { proposalId } : {}),
        ...(decision ? { decision } : {}),
        previousHash: events.length ? events[events.length - 1].hash : "GENESIS"
      };
      if (events.some((event) => event.id === body.id)) throw new Error("Duplicate event id");
      const event = { ...body, hash: await digest(body) };
      storage.setItem(STORAGE_KEY, JSON.stringify([...events, event]));
      return Object.freeze(event);
    }

    return Object.freeze({
      append,
      verify,
      list: () => read().map((event) => Object.freeze({ ...event, references: [...event.references] })),
      exportJSON: () => JSON.stringify({ format: "SSSWET-RESEARCH-LEDGER", schemaVersion: 1, events: read() }, null, 2),
      limits: Object.freeze({ maxEvents: MAX_EVENTS, maxSummaryCharacters: 500, maxReferences: 20 })
    });
  }

  const api = Object.freeze({ createResearchLedger, storageKey: STORAGE_KEY, maxEvents: MAX_EVENTS });
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof window !== "undefined") window.SSSWETResearchLedger = api;
})();