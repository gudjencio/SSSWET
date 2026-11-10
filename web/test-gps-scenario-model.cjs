"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {estimate,audit,formatAudit,constants,sessionKey,listSessions,locales:auditLocales}=require("./gps-scenario-model.js");
const R=6371000;
function lonForEast(m,lat=0){return m/(R*Math.cos(lat*Math.PI/180))*180/Math.PI;}
function fixes(offsets,options={}){const interval=options.intervalMs??60000,lat=options.latitude??0,accuracy=options.accuracy??5;return offsets.map((east,i)=>({id:"fix-"+i,kind:"gps",timestamp:i*interval,accuracy:typeof accuracy==="function"?accuracy(i):accuracy,coords:{latitude:lat,longitude:lonForEast(east,lat)}}));}
function distance(a,b){const p1=a.latitude*Math.PI/180,p2=b.latitude*Math.PI/180,dp=(b.latitude-a.latitude)*Math.PI/180,dl=(b.longitude-a.longitude)*Math.PI/180,h=Math.sin(dp/2)**2+Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)**2;return 2*R*Math.atan2(Math.sqrt(h),Math.sqrt(1-h));}
const straight=fixes([0,100,200]),future=estimate(straight,{kind:"future",horizonSeconds:60});
assert.ok(future,"three consecutive quality fixes must produce a scenario");
assert.equal(future.sampleCount,3);assert.equal(future.segmentCount,2);
assert.ok(Math.abs(future.speedMps-100/60)<0.002);assert.ok(Math.abs(future.distanceM-100)<0.1);
assert.ok(Math.abs(distance(future.origin,future.target)-100)<0.1);
assert.equal(future.anchorAccuracyM,5);assert.equal(future.medianVelocityResidualMps,0);
assert.ok(Math.abs(future.accuracySensitivityMps-10/60)<0.0001);
assert.equal(future.uncertaintyRadiusM,15,"envelope must equal anchor accuracy plus the two explicit horizon terms");
const past=estimate(straight,{kind:"past",horizonSeconds:60});
assert.ok(past);assert.ok(Math.abs(distance(past.origin,past.target)-100)<0.1);
assert.ok(past.target.longitude<past.origin.longitude,"past scenario must extend opposite observed median velocity");
const robust=estimate(fixes([0,100,200,2300]),{kind:"future",horizonSeconds:60});
assert.ok(robust);assert.ok(Math.abs(robust.distanceM-100)<0.2,"component-wise median must resist one plausible extreme segment");
assert.equal(robust.sampleCount,4);
assert.equal(estimate(fixes([0,100]),{horizonSeconds:60}),null,"two fixes cannot estimate velocity variability");
assert.equal(estimate(fixes([0,100,200],{accuracy:i=>i===1?NaN:5}),{horizonSeconds:60}),null,"all selected fixes need finite reported accuracy");
const nullAccuracy=fixes([0,100,200]);nullAccuracy[1].accuracy=null;
assert.equal(estimate(nullAccuracy,{horizonSeconds:60}),null,"null accuracy metadata must not be coerced to a false zero-metre fix");
const emptyAccuracy=fixes([0,100,200]);emptyAccuracy[1].accuracy="";
assert.equal(estimate(emptyAccuracy,{horizonSeconds:60}),null,"empty accuracy metadata must not be coerced to a false zero-metre fix");
assert.equal(estimate(fixes([0,100,200],{accuracy:151}),{horizonSeconds:60}),null,"fixes above the 150 m threshold must be excluded");
assert.equal(estimate(fixes([0,100,200]),{horizonSeconds:901}),null,"horizon must remain bounded to 15 minutes");
assert.equal(estimate(fixes([0,100,200]),{horizonSeconds:0}),null);
const gap=[...fixes([0,100]),{...fixes([200])[0],id:"after-gap",timestamp:20*60*1000}];
assert.equal(estimate(gap,{horizonSeconds:60}),null,"a gap over 15 minutes must split the track");
assert.equal(estimate(fixes([0,100,6000]),{horizonSeconds:60}),null,"a segment over 5 km must split the track");
const speedBoundary=estimate(fixes([0,100,4299.9]),{horizonSeconds:60});
assert.ok(speedBoundary,"a segment just below the 70 m/s ceiling must remain eligible");
assert.equal(estimate(fixes([0,100,4301]),{horizonSeconds:60}),null,"a segment just above 70 m/s must split the track even below 5 km");
const duplicate=fixes([0,100,200]);duplicate[1].timestamp=duplicate[0].timestamp;
assert.equal(estimate(duplicate,{horizonSeconds:60}),null,"non-increasing timestamps must split the run");
const invalid=fixes([0,100,200]);invalid[1].coords.latitude=91;
assert.equal(estimate(invalid,{horizonSeconds:60}),null);
const longTrack=fixes([0,100,200,300,400,500,600,700]),bounded=estimate(longTrack,{horizonSeconds:60});
assert.equal(bounded.sampleCount,constants.MAX_FIXES,"scenario window must be capped at six fixes");
assert.deepEqual(bounded.sourceObservationIds,["fix-2","fix-3","fix-4","fix-5","fix-6","fix-7"]);
assert.deepEqual(estimate(straight,{kind:"future",horizonSeconds:60}),future,"identical inputs must be deterministic");
assert.equal(constants.MIN_FIXES,3);assert.equal(constants.MAX_ACCURACY_M,150);
assert.equal(estimate(straight,{kind:"future",horizonSeconds:60}).sessionKey,"legacy");
const sessionA=fixes([0,100,200]).map((event,index)=>({...event,id:"a-"+index,clockSessionId:"clock-A"}));
const sessionB=fixes([1000,1100,1200]).map((event,index)=>({...event,id:"b-"+index,clockSessionId:"clock-B"}));
const mixedSessions=[...sessionA,...sessionB];
assert.equal(estimate(mixedSessions,{kind:"future",horizonSeconds:60}),null,"multiple clock sessions must require an explicit session selection");
const selectedA=estimate(mixedSessions,{kind:"future",horizonSeconds:60,sessionKey:"session:clock-A"});
assert.ok(selectedA,"an explicitly selected session with three valid fixes must produce a scenario");
assert.equal(selectedA.clockSessionId,"clock-A");
assert.deepEqual(selectedA.sourceObservationIds,["a-0","a-1","a-2"],"a scenario must never include observations from another clock session");
const sessions=listSessions(mixedSessions);
assert.equal(sessions.length,2);
assert.deepEqual(sessions.map(item=>item.key),["session:clock-A","session:clock-B"]);
assert.deepEqual(sessions.map(item=>item.gpsCount),[3,3]);
assert.equal(sessionKey({timestamp:1}),"legacy","records without a clock session remain in an isolated legacy group");
const twoInA=fixes([0,100]).map((event,index)=>({...event,id:"two-a-"+index,clockSessionId:"clock-A"}));
const oneInB={...fixes([200])[0],id:"one-b",timestamp:120000,clockSessionId:"clock-B"};
assert.equal(estimate([...twoInA,oneInB],{kind:"future",horizonSeconds:60}),null,"two fixes from one session and one from another must not be combined into a fabricated three-fix track");
assert.equal(estimate([...twoInA,oneInB],{kind:"future",horizonSeconds:60,sessionKey:"session:clock-A"}),null);
assert.equal(estimate(mixedSessions,{kind:"future",horizonSeconds:60,sessionKey:"session:missing"}),null,"unknown session selection must not fall back to another session");
const withAnnotation=[...sessionA,{id:"annotation-a",kind:"annotation",timestamp:180000,clockSessionId:"clock-A"}];
assert.equal(listSessions(withAnnotation)[0].count,4,"session index must include non-GPS observations in the timeline count");
const app=fs.readFileSync(path.join(__dirname,"virtual-time-travel.js"),"utf8");
assert.match(app,/model\?\.estimate/);assert.match(app,/SSSWETGpsScenarioModel\?\.sessionKey/);assert.match(app,/refreshSessions/);assert.match(app,/function selectedSessionEvents\(\)/);assert.match(app,/const visible=selectedSessionEvents\(\)/);assert.match(app,/preferredSession=\$\("vt-session"\)\?\.value\|\|entrySession/);assert.match(app,/session_ordering_note/);assert.match(app,/sessionKey\(item\)===sessionKey\(previous\)/);assert.match(app,/currentSession!==previousSession/);assert.match(app,/markerBuckets\.get\(currentSession\+/);assert.match(app,/sessionMedia/);assert.match(app,/modelQualityDetails/);assert.match(app,/modelNeedQualityData/);assert.match(app,/words\.modelQualityDetails/);assert.match(app,/words\.modelNeedQualityData/);assert.doesNotMatch(app,/t\(\)\.modelQualityDetails|t\(\)\.modelNeedQualityData/);
const html=fs.readFileSync(path.join(__dirname,"virtual-time-travel.html"),"utf8");
assert.ok(html.indexOf('<script src="gps-scenario-model.js"></script>')<html.indexOf('<script src="virtual-time-travel.js"></script>'));assert.match(html,/id="vt-session"/);assert.match(html,/aria-describedby="vt-session-help"/);
const sw=fs.readFileSync(path.join(__dirname,"sw.js"),"utf8");
const cacheVersion=sw.match(/const CACHE = "ssswet-web-v(\d+)";/);
assert.ok(cacheVersion,"the service worker must use a versioned cache key");
assert.ok(Number(cacheVersion[1])>=193,"the cache version must be at least v193, when the temporal/GPS modules entered the precache");
assert.match(sw,/\.\/gps-scenario-model\.js/,"the GPS scenario model must be precached");
assert.match(sw,/cache\.addAll\(ASSETS\)/,"the declared assets must be installed into the versioned cache");
const extraStart=app.indexOf("const extraCopy=")+ "const extraCopy=".length,extraEnd=app.indexOf(";\n",extraStart),extra=JSON.parse(app.slice(extraStart,extraEnd));
const locales=["en","fr","es","de","it","pt","nl","ru","uk","ar","he","ja","ko","zh","hi"];
assert.deepEqual(Object.keys(extra),locales);
for(const locale of locales){for(const key of ["modelNeedQualityData","modelQualityDetails","sessionLabel","sessionSelectPrompt","sessionHelp","sessionNeedSelection","sessionOption","sessionUnknownTime","sessionLegacyPrefix"])assert.ok(extra[locale][key],"missing "+key+" translation for "+locale);for(const token of ["{distance}","{uncertainty}","{samples}","{speed}","{spread}","{sensitivity}"])assert.ok(extra[locale].modelQualityDetails.includes(token),"missing "+token+" in "+locale);for(const token of ["{start}","{end}","{count}","{gps}"])assert.ok(extra[locale].sessionOption.includes(token),"missing "+token+" in session option for "+locale);}

const straightAudit=audit(straight,{sessionKey:"legacy"});
assert.ok(straightAudit,"an explicit session audit must be available");
assert.equal(straightAudit.gpsObservationCount,3);
assert.equal(straightAudit.acceptedFixCount,3);
assert.equal(straightAudit.rejectedFixCount,0);
assert.equal(straightAudit.continuousRunCount,1);
assert.equal(straightAudit.longestRunFixes,3);
assert.equal(straightAudit.scenarioReady,true);
assert.equal(straightAudit.continuityBreaks,0);
assert.match(formatAudit(straightAudit,"fr"),/Audit GPS/);
assert.ok(!formatAudit(straightAudit,"fr").includes("0 coordonnées"),"zero-count rejection categories should stay out of the user summary");

const interrupted=fixes([0,100,200,300]);
interrupted[1].accuracy=null;
const interruptedAudit=audit(interrupted,{sessionKey:"legacy"});
assert.equal(interruptedAudit.acceptedFixCount,3);
assert.equal(interruptedAudit.rejectedFixCount,1);
assert.equal(interruptedAudit.rejectionCounts.missing_accuracy,1);
assert.equal(interruptedAudit.breakCounts.rejected_fix,1);
assert.equal(interruptedAudit.continuousRunCount,2);
assert.equal(interruptedAudit.longestRunFixes,2);
assert.equal(interruptedAudit.scenarioReady,false);
assert.equal(estimate(interrupted,{kind:"future",horizonSeconds:60}),null,
  "a rejected GPS observation must break the track rather than allowing the model to bridge across it");

const rejectedFixtures=[
  {id:"missing-coords",kind:"gps",timestamp:0,accuracy:5,coords:null},
  {id:"invalid-coords",kind:"gps",timestamp:1000,accuracy:5,coords:{latitude:91,longitude:0}},
  {id:"invalid-time",kind:"gps",timestamp:"bad",accuracy:5,coords:{latitude:0,longitude:0}},
  {id:"missing-accuracy",kind:"gps",timestamp:2000,accuracy:null,coords:{latitude:0,longitude:0}},
  {id:"invalid-accuracy",kind:"gps",timestamp:3000,accuracy:-1,coords:{latitude:0,longitude:0}},
  {id:"over-limit",kind:"gps",timestamp:4000,accuracy:151,coords:{latitude:0,longitude:0}}
];
const rejectedAudit=audit(rejectedFixtures,{sessionKey:"legacy"});
assert.equal(rejectedAudit.gpsObservationCount,6);
assert.equal(rejectedAudit.acceptedFixCount,0);
assert.equal(rejectedAudit.rejectedFixCount,6);
assert.equal(rejectedAudit.rejectionCounts.missing_coordinates,1);
assert.equal(rejectedAudit.rejectionCounts.invalid_coordinates,1);
assert.equal(rejectedAudit.rejectionCounts.invalid_timestamp,1);
assert.equal(rejectedAudit.rejectionCounts.missing_accuracy,1);
assert.equal(rejectedAudit.rejectionCounts.invalid_accuracy,1);
assert.equal(rejectedAudit.rejectionCounts.accuracy_over_limit,1);
assert.equal(rejectedAudit.scenarioReady,false);

const gapAudit=audit(gap,{sessionKey:"legacy"});
assert.equal(gapAudit.breakCounts.time_gap,1);
const distanceAudit=audit(fixes([0,100,6000]),{sessionKey:"legacy"});
assert.equal(distanceAudit.breakCounts.distance_jump,1);
const speedAudit=audit(fixes([0,100,4301]),{sessionKey:"legacy"});
assert.equal(speedAudit.breakCounts.speed_limit,1);
const duplicateAudit=audit(duplicate,{sessionKey:"legacy"});
assert.equal(duplicateAudit.breakCounts.non_increasing_time,1);
assert.equal(estimate(duplicate,{kind:"future",horizonSeconds:60}),null);

const monotonicTrack=fixes([0,100,200],{intervalMs:60000}).map((event,index)=>({
  ...event,clockSessionId:"monotonic-fixture",monotonicElapsedMs:index*30000,clockStatus:"within_tolerance"
}));
const monotonicEstimate=estimate(monotonicTrack,{kind:"future",horizonSeconds:60,sessionKey:"session:monotonic-fixture"});
assert.ok(monotonicEstimate);
assert.ok(Math.abs(monotonicEstimate.distanceM-200)<0.2,
  "same-session elapsed time must use monotonic readings instead of rounded epoch timestamps");

const mixedClockTrack=fixes([0,100,200]).map((event,index)=>({
  ...event,clockSessionId:"mixed-clock",monotonicElapsedMs:index===0?0:null,
  clockStatus:index===0?"within_tolerance":"monotonic_unavailable"
}));
const mixedClockAudit=audit(mixedClockTrack,{sessionKey:"session:mixed-clock"});
assert.equal(mixedClockAudit.breakCounts.clock_basis_change,1);
assert.equal(mixedClockAudit.clockFallbackCount,2);
assert.equal(estimate(mixedClockTrack,{kind:"future",horizonSeconds:60,sessionKey:"session:mixed-clock"}),null,
  "a change between monotonic and wall-clock time bases must split the track");

assert.equal(audit(mixedSessions),null,"an audit must not silently combine multiple capture sessions");
const sessionAudit=audit(mixedSessions,{sessionKey:"session:clock-A"});
assert.equal(sessionAudit.acceptedFixCount,3);
assert.equal(sessionAudit.scenarioReady,true);
assert.equal(auditLocales.length,15);
assert.deepEqual(auditLocales,["en","fr","es","de","it","pt","nl","ru","uk","ar","he","ja","ko","zh","hi"]);
for(const locale of auditLocales){
  const formatted=formatAudit(interruptedAudit,locale);
  assert.ok(formatted.length>20,"audit summary must be localized for "+locale);
  assert.ok(!formatted.includes("{accepted}")&&!formatted.includes("{items}"),"audit placeholders must be resolved for "+locale);
}
assert.equal(formatAudit(straightAudit,"fr"),formatAudit(audit(straight,{sessionKey:"legacy"}),"fr"),
  "the same audit inputs must produce a deterministic localized summary");

assert.match(app,/model\?\.audit/);
assert.match(app,/model\?\.formatAudit/);
assert.match(app,/const visible=selectedSessionEvents\(\)/);
console.log("GPS scenario-model regression tests passed (synthetic tracks; not a real-world positioning or forecast accuracy benchmark).");
