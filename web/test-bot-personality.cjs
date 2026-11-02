const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");

const source = fs.readFileSync(new URL("./bot-personality.js", `file://${__filename}`), "utf8");
new Function(source);
const listeners = {};
const document = {
  documentElement: { lang: "fr" }, body: null,
  head: { appendChild() {} },
  getElementById() { return null; }, querySelector() { return null; },
  addEventListener(name, callback) { listeners[name] = callback; }
};
class MockUtterance { constructor(text) { this.text=text; this.volume=1; this.rate=1; } }
let spoken = null;
const speechSynthesis = { speak(utterance) { spoken=utterance; }, cancel() {} };
class MockMutationObserver { observe() {} }
const window = { SSSWET_CURRENT_LANGUAGE:"fr", speechSynthesis, addEventListener() {} };
const context = { window, document, SpeechSynthesisUtterance:MockUtterance, MutationObserver:MockMutationObserver, Math, String, Object, Array };
vm.runInNewContext(source, context);
const api = window.SSSWET_BOT_PERSONALITY;
assert.ok(api);
assert.equal(api.agents.length,8);
assert.equal(new Set(api.agents.map(agent=>agent.role)).size,8);
assert.equal(new Set(api.agents.map(agent=>agent.approach)).size,8);
for (const role of ["general_researcher","independent_verifier","medical_researcher","materials_scientist","data_analyst","systems_engineer","ethics_reviewer","futures_analyst"]) assert.ok(api.styleForRole(role));
assert.match(api.getCopy().intro,/bienvenue/i);
assert.match(api.sayUncertain(),/ne le sais pas encore/i);
assert.match(api.correctSelf(),/correction/i);
assert.match(api.handoff({name:"Nadia El-Karim"}),/Nadia El-Karim/);
api.setSpeechContext("internal");
speechSynthesis.speak(new MockUtterance("Test"));
assert.equal(spoken.volume,0.32);
api.setSpeechContext("visitor");
speechSynthesis.speak(new MockUtterance("Test"));
assert.equal(spoken.volume,0.86);
console.log("Validated eight distinct agent personalities, uncertainty and correction language, specialist handoff, French introduction and internal/visitor voice levels.");
