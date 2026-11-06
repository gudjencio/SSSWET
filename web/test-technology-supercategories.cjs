"use strict";
const assert=require("node:assert/strict");
const {buildSupercategories,generatedProgrammes,coreCatalogueEntries,domains}=require("./technology-supercategories-data.js");
const domainCounts={space:61,protection:62,energy:61,materials:61,life:61,environment:62,robotics:65,society:67};
const base=[];
for(const domain of domains)for(let index=0;index<domainCounts[domain];index++){
 const key="expanded_"+domain+"_"+String(index).padStart(3,"0"),title=domain+" expansion "+index;
 base.push({key,item:{en:[title,"Synthetic baseline record for taxonomy validation."]},meta:{category:domain,subcategory:"baseline"},searchText:(key+" "+title).toLowerCase()});
}
assert.equal(base.length,500,"the browser supplies 488 expanded and 12 curated programmes");
const canonical=coreCatalogueEntries();
assert.equal(canonical.length,106,"the 106 canonical core records must be restored to the browser catalogue");
const generated=generatedProgrammes();
assert.equal(generated.length,394,"the deterministic generated expansion must match the core registry");
assert.equal(generated[0].key,"programSpaceOrbitalNavigation");
assert.equal(generated[393].meta.category,"society");
const groups=buildSupercategories(base);
assert.equal(groups.length,10);
assert.deepEqual(groups.map(group=>group.entries.length),Array(10).fill(100));
const flattened=groups.flatMap(group=>group.entries);
assert.equal(flattened.length,1000);
assert.equal(new Set(flattened.map(entry=>entry.key)).size,1000,"every programme must appear exactly once");
assert.equal(flattened.filter(entry=>entry.generated).length,394);
assert.equal(flattened.filter(entry=>entry.canonical).length,106);
assert.equal(groups[8].id,"sensing");
assert.equal(groups[9].id,"systems");
assert.throws(()=>buildSupercategories(base.concat(base[0])),/Duplicate catalogue identifier/);
assert.throws(()=>buildSupercategories(base.slice(1)),/exactly 1,000/);
console.log("Technology super-category tests passed: 500 browser entries + 106 canonical + 394 generated = 1,000 unique programmes in 10 groups of 100.");