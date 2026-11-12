const fs=require("fs");const path=require("path");const assert=require("assert");
const html=fs.readFileSync(path.join(__dirname,"virtual-time-travel.html"),"utf8");
for(const id of ["vt-map","vt-start","vt-stop","vt-time","vt-session","vt-model","vt-export","vt-delete"])assert.match(html,new RegExp('id="'+id+'"'));
const sw=fs.readFileSync(path.join(__dirname,"sw.js"),"utf8");
const cacheVersion=sw.match(/const CACHE = "([^"]+)"/)?.[1];
assert.match(cacheVersion||"",/^ssswet-web-v\d+$/);
assert.notEqual(cacheVersion,"ssswet-web-v196","The service-worker cache must be advanced when the web shell changes.");
assert.match(sw,/\.\/gps-scenario-model\.js/);
