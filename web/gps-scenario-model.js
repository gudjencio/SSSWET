(() => {
  "use strict";
  const EARTH_RADIUS_M = 6371000;
  const MAX_ACCURACY_M = 150;
  const MAX_GAP_MS = 15 * 60 * 1000;
  const MAX_SEGMENT_DISTANCE_M = 5000;
  const MAX_SPEED_MPS = 70;
  const MAX_FIXES = 6;
  const MIN_FIXES = 3;
  function normalizeLongitude(value) { return ((value + 540) % 360) - 180; }
  function haversine(a, b) {
    const lat1=a.latitude*Math.PI/180,lat2=b.latitude*Math.PI/180;
    const dLat=(b.latitude-a.latitude)*Math.PI/180,dLon=normalizeLongitude(b.longitude-a.longitude)*Math.PI/180;
    const h=Math.sin(dLat/2)**2+Math.cos(lat1)*Math.cos(lat2)*Math.sin(dLon/2)**2;
    return 2*EARTH_RADIUS_M*Math.atan2(Math.sqrt(Math.min(1,h)),Math.sqrt(Math.max(0,1-h)));
  }
  function bearing(a,b) {
    const lat1=a.latitude*Math.PI/180,lat2=b.latitude*Math.PI/180,dLon=normalizeLongitude(b.longitude-a.longitude)*Math.PI/180;
    return Math.atan2(Math.sin(dLon)*Math.cos(lat2),Math.cos(lat1)*Math.sin(lat2)-Math.sin(lat1)*Math.cos(lat2)*Math.cos(dLon));
  }
  function median(values) {
    if(!values.length)return null;
    const sorted=values.slice().sort((a,b)=>a-b),middle=Math.floor(sorted.length/2);
    return sorted.length%2?sorted[middle]:(sorted[middle-1]+sorted[middle])/2;
  }
  function hasFiniteNumber(value) {
    return value!==null&&value!==undefined&&value!==""&&Number.isFinite(Number(value));
  }
  function validFix(event) {
    if(!event||(event.kind&&event.kind!=="gps")||!event.coords)return false;
    const latitude=Number(event.coords.latitude),longitude=Number(event.coords.longitude),timestamp=Number(event.timestamp),accuracy=Number(event.accuracy);
    return hasFiniteNumber(event.coords.latitude)&&latitude>=-90&&latitude<=90
      &&hasFiniteNumber(event.coords.longitude)&&longitude>=-180&&longitude<=180
      &&hasFiniteNumber(event.timestamp)&&hasFiniteNumber(event.accuracy)&&accuracy>=0&&accuracy<=MAX_ACCURACY_M;
  }
  function sessionKey(event) {
    const id=event&&event.clockSessionId;
    return id===null||id===undefined||String(id)===""?"legacy":"session:"+String(id);
  }
  function listSessions(events) {
    const groups=new Map();
    for(const event of Array.isArray(events)?events:[]){
      if(!event||typeof event!=="object")continue;
      const key=sessionKey(event);
      if(!groups.has(key)){
        groups.set(key,{key,clockSessionId:key==="legacy"?null:String(event.clockSessionId),count:0,gpsCount:0,firstTimestamp:null,lastTimestamp:null});
      }
      const group=groups.get(key);
      group.count++;
      if(event.kind==="gps"&&validFix(event))group.gpsCount++;
      if(hasFiniteNumber(event.timestamp)){
        const timestamp=Number(event.timestamp);
        group.firstTimestamp=group.firstTimestamp===null?timestamp:Math.min(group.firstTimestamp,timestamp);
        group.lastTimestamp=group.lastTimestamp===null?timestamp:Math.max(group.lastTimestamp,timestamp);
      }
    }
    return Array.from(groups.values()).sort((a,b)=>a.key<b.key?-1:a.key>b.key?1:0).map(group=>Object.freeze(group));
  }
  function splitContinuousRuns(events) {
    const points=(Array.isArray(events)?events:[]).filter(validFix).map(event=>({
      id:event.id==null?null:String(event.id),timestamp:Number(event.timestamp),accuracy:Number(event.accuracy),
      clockSessionId:event.clockSessionId==null?null:String(event.clockSessionId),
      coords:{latitude:Number(event.coords.latitude),longitude:Number(event.coords.longitude)}
    })).sort((a,b)=>a.timestamp-b.timestamp);
    const runs=[];let current=[];
    for(const point of points){
      const previous=current[current.length-1];
      if(previous){
        const elapsedMs=point.timestamp-previous.timestamp,distanceM=haversine(previous.coords,point.coords);
        const speedMps=elapsedMs>0?distanceM/(elapsedMs/1000):Infinity;
        const continuous=elapsedMs>0&&elapsedMs<=MAX_GAP_MS&&distanceM<=MAX_SEGMENT_DISTANCE_M&&speedMps<=MAX_SPEED_MPS;
        if(!continuous){if(current.length)runs.push(current);current=[];}
      }
      current.push(point);
    }
    if(current.length)runs.push(current);
    return runs;
  }
  function localMeters(point,origin) {
    const distance=haversine(origin,point),angle=bearing(origin,point);
    return {east:distance*Math.sin(angle),north:distance*Math.cos(angle)};
  }
  function offsetPoint(origin,eastM,northM) {
    const distance=Math.hypot(eastM,northM);
    if(!distance)return {latitude:origin.latitude,longitude:origin.longitude};
    const angular=distance/EARTH_RADIUS_M,initialBearing=Math.atan2(eastM,northM);
    const lat1=origin.latitude*Math.PI/180,lon1=origin.longitude*Math.PI/180;
    const lat2=Math.asin(Math.sin(lat1)*Math.cos(angular)+Math.cos(lat1)*Math.sin(angular)*Math.cos(initialBearing));
    const lon2=lon1+Math.atan2(Math.sin(initialBearing)*Math.sin(angular)*Math.cos(lat1),Math.cos(angular)-Math.sin(lat1)*Math.sin(lat2));
    return {latitude:lat2*180/Math.PI,longitude:normalizeLongitude(lon2*180/Math.PI)};
  }
  function estimate(events,options={}) {
    const kind=options.kind==="past"?"past":"future",horizonSeconds=Number(options.horizonSeconds);
    if(!Number.isFinite(horizonSeconds)||horizonSeconds<=0||horizonSeconds>900)return null;
    const validEvents=(Array.isArray(events)?events:[]).filter(validFix);
    const availableKeys=Array.from(new Set(validEvents.map(sessionKey))).sort();
    const requestedKey=options.sessionKey===undefined||options.sessionKey===null||options.sessionKey===""?null:String(options.sessionKey);
    const selectedKey=requestedKey||(availableKeys.length===1?availableKeys[0]:null);
    if(!selectedKey||!availableKeys.includes(selectedKey))return null;
    const selectedEvents=validEvents.filter(event=>sessionKey(event)===selectedKey);
    const eligibleRuns=splitContinuousRuns(selectedEvents).filter(run=>run.length>=MIN_FIXES);
    if(!eligibleRuns.length)return null;
    const selectedRun=kind==="past"?eligibleRuns[0]:eligibleRuns[eligibleRuns.length-1];
    const fixes=kind==="past"?selectedRun.slice(0,MAX_FIXES):selectedRun.slice(-MAX_FIXES);
    if(fixes.length<MIN_FIXES)return null;
    const projectionOrigin=fixes[0].coords,projected=fixes.map(fix=>localMeters(fix.coords,projectionOrigin));
    const velocities=[],accuracySensitivityRates=[];
    for(let index=0;index<fixes.length-1;index++){
      const start=fixes[index],end=fixes[index+1],elapsedSeconds=(end.timestamp-start.timestamp)/1000;
      if(!(elapsedSeconds>0))return null;
      velocities.push({
        east:(projected[index+1].east-projected[index].east)/elapsedSeconds,
        north:(projected[index+1].north-projected[index].north)/elapsedSeconds
      });
      accuracySensitivityRates.push((start.accuracy+end.accuracy)/elapsedSeconds);
    }
    const medianEastMps=median(velocities.map(item=>item.east)),medianNorthMps=median(velocities.map(item=>item.north));
    const speedMps=Math.hypot(medianEastMps,medianNorthMps);
    const medianVelocityResidualMps=median(velocities.map(item=>{const residual=Math.hypot(item.east-medianEastMps,item.north-medianNorthMps);return residual<1e-9?0:residual;}));
    const accuracySensitivityMps=median(accuracySensitivityRates);
    const anchor=kind==="past"?fixes[0]:fixes[fixes.length-1],direction=kind==="past"?-1:1;
    const target=offsetPoint(anchor.coords,medianEastMps*horizonSeconds*direction,medianNorthMps*horizonSeconds*direction);
    const variabilityContributionM=medianVelocityResidualMps*horizonSeconds;
    const accuracySensitivityContributionM=accuracySensitivityMps*horizonSeconds;
    const uncertaintyRadiusM=Math.ceil(anchor.accuracy+variabilityContributionM+accuracySensitivityContributionM);
    return Object.freeze({
      kind,method:"median-local-velocity",sessionKey:selectedKey,clockSessionId:fixes[0].clockSessionId==null?null:String(fixes[0].clockSessionId),
      origin:Object.freeze({...anchor.coords}),target:Object.freeze(target),
      distanceM:speedMps*horizonSeconds,speedMps,sampleCount:fixes.length,segmentCount:velocities.length,
      sourceObservationIds:Object.freeze(fixes.map(fix=>fix.id).filter(Boolean)),anchorAccuracyM:anchor.accuracy,
      medianVelocityResidualMps,accuracySensitivityMps,variabilityContributionM,accuracySensitivityContributionM,
      uncertaintyRadiusM,horizonSeconds
    });
  }
  const api=Object.freeze({estimate,median,sessionKey,listSessions,constants:Object.freeze({MAX_ACCURACY_M,MAX_GAP_MS,MAX_SEGMENT_DISTANCE_M,MAX_SPEED_MPS,MAX_FIXES,MIN_FIXES})});
  if(typeof window!=="undefined")window.SSSWETGpsScenarioModel=api;
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
})();
