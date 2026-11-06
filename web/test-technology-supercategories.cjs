"use strict";
const assert=require("node:assert/strict");
const {buildSupercategories,generatedProgrammes,domains}=require("./technology-supercategories-data.js");
const domainCounts={space:84,protection:75,energy:70,materials:69,life:78,environment:80,robotics:71,society:79};
const base=[];
for(const domain of domains)for(let index=0;index<domainCounts[domain];index++){
 const key="base_"+domain+"_"+String(index).padStart(3,"0"),title=domain+" research "+index;
 base.push({key,item:{en:[title,"Synthetic baseline record for taxonomy validation."]},meta:{category:domain,subcategory:"baseline"},searchText:(key+" "+title).toLowerCase()});
}
assert.equal(base.length,606);
const generated=generatedProgrammes();
assert.equal(generated.length,394);
assert.equal(generated[0].key,"programSpaceOrbitalNavigation");
assert.equal(generated[393].meta.category,"society");
const groups=buildSupercategories(base);
assert.equal(groups.length,10);
assert.deepEqual(groups.map(group=>group.entries.length),Array(10).fill(100));
const flattened=groups.flatMap(group=>group.entries);
assert.equal(flattened.length,1000);
assert.equal(new Set(flattened.map(entry=>entry.key)).size,1000);
assert.equal(flattened.filter(entry=>entry.generated).length,394);
assert.equal(groups[8].id,"sensing");
assert.equal(groups[9].id,"systems");
assert.throws(()=>buildSupercategories(base.concat(base[0])),/Duplicate catalogue identifier/);
assert.throws(()=>buildSupercategories(base.slice(1)),/exactly 1,000/);
console.log("Technology super-category tests passed: 10 groups × 100 programmes; 1,000 unique entries; no omissions or duplicates.");