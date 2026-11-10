"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { createSessionClock, describe, locales, DEFAULT_TOLERANCE_MS } = require("./temporal-clock.js");

let wall = 1_800_000_000_000;
let mono = 100;
const clock = createSessionClock({ wallNow: () => wall, monotonicNow: () => mono, sessionId: "test-session" });
const first = clock.capture();
mono += 1250;
wall += 1250;
const second = clock.capture();
assert.equal(second.timestamp - first.timestamp, 1250, "epoch timestamps must follow monotonic elapsed time");
assert.equal(second.monotonicElapsedMs - first.monotonicElapsedMs, 1250);
assert.equal(second.clockStatus, "within_tolerance");
assert.equal(second.clockSessionId, "test-session");

let unstableMono = 20;
let unstableWall = 90_000;
const monotonicClamp = createSessionClock({ wallNow: () => unstableWall, monotonicNow: () => unstableMono, sessionId: "clamp" });
monotonicClamp.capture();
unstableMono += 500;
unstableWall += 500;
const beforeMonotonicRegression = monotonicClamp.capture();
unstableMono -= 1000;
unstableWall += 10;
const afterMonotonicRegression = monotonicClamp.capture();
assert.equal(afterMonotonicRegression.monotonicElapsedMs, beforeMonotonicRegression.monotonicElapsedMs,
  "a non-increasing monotonic reading must be clamped rather than reversing elapsed time");
assert.equal(afterMonotonicRegression.timestamp, beforeMonotonicRegression.timestamp,
  "a non-increasing monotonic reading must not reorder the timeline");


const beforeBackwardJump = second;
mono += 5000;
wall -= 60_000;
const afterBackwardJump = clock.capture();
assert.equal(afterBackwardJump.timestamp - beforeBackwardJump.timestamp, 5000, "backward wall-clock changes must not reorder same-session observations");
assert.equal(afterBackwardJump.wallTimestamp, wall, "the raw wall-clock reading must remain available for audit");
assert.equal(afterBackwardJump.clockOffsetMs, -65_000);
assert.equal(afterBackwardJump.clockStatus, "wall_clock_diverged");
assert.equal(clock.durationBetween(beforeBackwardJump, afterBackwardJump), 5000, "media duration must use monotonic elapsed time");
assert.match(describe(afterBackwardJump, "fr"), /diffère de -65000 ms/);

const beforeForwardJump = afterBackwardJump;
mono += 250;
wall += 120_250;
const afterForwardJump = clock.capture();
assert.equal(afterForwardJump.timestamp - beforeForwardJump.timestamp, 250, "forward wall-clock changes must not create same-session timeline gaps");
assert.equal(afterForwardJump.clockOffsetMs, 55_000);
assert.equal(afterForwardJump.clockStatus, "wall_clock_diverged");
assert.match(describe(afterForwardJump, "en"), /\+55000 ms/);

assert.equal(DEFAULT_TOLERANCE_MS, 2000, "the documented default diagnostic tolerance must remain 2 seconds");
let boundaryWall = 10_000;
const boundary = createSessionClock({ wallNow: () => boundaryWall, monotonicNow: () => 0, toleranceMs: 2000 });
boundary.capture();
boundaryWall += 2000;
const atBoundary = boundary.capture();
assert.equal(atBoundary.clockOffsetMs, 2000);
assert.equal(atBoundary.clockStatus, "within_tolerance", "the tolerance boundary is inclusive");
boundaryWall += 1;
assert.equal(boundary.capture().clockStatus, "wall_clock_diverged", "an offset beyond tolerance must be flagged");

let fallbackWall = 50_000;
const fallback = createSessionClock({ wallNow: () => fallbackWall, monotonicNow: () => NaN, sessionId: "fallback" });
const fallbackA = fallback.capture();
fallbackWall += 900;
const fallbackB = fallback.capture();
assert.equal(fallbackA.clockStatus, "monotonic_unavailable");
assert.equal(fallbackB.timestamp - fallbackA.timestamp, 900);
assert.equal(fallback.durationBetween(fallbackA, fallbackB), 900);
assert.match(describe(fallbackA, "fr"), /Horloge monotone indisponible/);
assert.equal(describe({ timestamp: 1 }, "en"), "", "legacy observations without clock metadata remain supported");

const otherSession = createSessionClock({ wallNow: () => 70_000, monotonicNow: () => 0, sessionId: "other" });
const otherA = otherSession.capture();
assert.equal(clock.durationBetween(first, otherA), Math.max(0, otherA.timestamp - first.timestamp), "cross-session duration falls back to epoch timestamps");

assert.equal(locales.length, 15, "clock diagnostics must cover all 15 module locales");
for (const locale of locales) {
  const message = describe({ clockStatus: "wall_clock_diverged", clockOffsetMs: 321, clockToleranceMs: 2000 }, locale);
  const stable = describe({ clockStatus: "within_tolerance", clockToleranceMs: 2000 }, locale);
  const unavailable = describe({ clockStatus: "monotonic_unavailable" }, locale);
  assert.ok(message && message.includes("321"), "missing localized divergence diagnostic for " + locale);
  assert.ok(stable && stable.includes("2000"), "missing localized tolerance diagnostic for " + locale);
  assert.ok(unavailable, "missing localized fallback diagnostic for " + locale);
  if (locale !== "en") assert.notEqual(message, describe({ clockStatus: "wall_clock_diverged", clockOffsetMs: 321 }, "en"),
    "locale " + locale + " must not silently fall back to English");
}

const appPath = path.join(__dirname, "virtual-time-travel.js");
const app = fs.readFileSync(appPath, "utf8");
assert.match(app, /captureClockSnapshot\(\)/, "capture records must use the session clock");
assert.match(app, /elapsedClockNow\(\)/, "sensor throttling must use monotonic elapsed time");
assert.match(app, /durationBetween\(clipStart,clipEnd\)/, "media durations must use monotonic elapsed time");
assert.match(app, /clockDescription\(e\)/, "timeline details must expose the clock diagnostic");
assert.match(app, /lastGpsWrite=-Infinity,lastMotionWrite=-Infinity,lastOrientationWrite=-Infinity/, "first sensor samples must not be suppressed by the monotonic clock origin");
assert.doesNotMatch(app, /Date\.now\(\)-last(?:Gps|Motion|Orientation)Write/, "wall-clock time must not be used for sensor throttles");

const html = fs.readFileSync(path.join(__dirname, "virtual-time-travel.html"), "utf8");
assert.ok(html.indexOf('<script src="temporal-clock.js"></script>') < html.indexOf('<script src="virtual-time-travel.js"></script>'),
  "the clock helper must load before the mapping application");
const serviceWorker = fs.readFileSync(path.join(__dirname, "sw.js"), "utf8");
assert.match(serviceWorker, /ssswet-web-v196/, "the service-worker cache must be bumped for the new asset");
assert.match(serviceWorker, /\.\/temporal-clock\.js/, "the new clock helper must be precached");

console.log("Temporal clock regression tests passed (synthetic clock probes; not a real-world clock-accuracy benchmark).");
