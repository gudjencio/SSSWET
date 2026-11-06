(function (root, factory) {
  const api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.SSSWET_SUPERCATEGORY_DATA = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";
  const families = {
    space: [["orbital","deep-space","planetary","lunar","interstellar"],["navigation","robotics","habitats","resource mapping","radiation monitoring","communications","autonomous operations","precision landing","thermal control","life support"]],
    protection: [["civil","industrial","rescue","extreme-environment","infrastructure"],["hazard detection","impact mitigation","thermal protection","radiation monitoring","structural monitoring","evacuation support","wearable safety","decontamination","emergency power","environmental sensing"]],
    energy: [["renewable","grid","portable","industrial","space"],["generation","storage","conversion","thermal management","power quality","load balancing","energy recovery","fault detection","demand forecasting","microgrid control"]],
    materials: [["advanced","bioinspired","structural","functional","recyclable"],["characterization","self-healing","damage detection","thermal management","lightweighting","recycling","surface engineering","fatigue monitoring","manufacturing control","durability prediction"]],
    life: [["cellular","tissue","organ","neural","assistive"],["monitoring","regeneration","drug delivery","biocompatibility","prosthetic control","rehabilitation","physiological sensing","clinical data","simulation","safety monitoring"]],
    environment: [["ecosystem","climate","marine","agricultural","atmospheric"],["monitoring","restoration","forecasting","water quality","soil sensing","biodiversity mapping","carbon accounting","pollution detection","wildfire detection","resilience planning"]],
    robotics: [["field","assistive","industrial","rescue","scientific"],["navigation","manipulation","mapping","inspection","coordination","human interaction","fault recovery","energy management","perception","safe autonomy"]],
    society: [["scientific","public","distributed","secure","accessible"],["computing","communication","translation","data provenance","knowledge discovery","privacy protection","education","health information","decision support","research coordination"]]
  };
  const domains = ["space","protection","energy","materials","life","environment","robotics","society"];
  const subcategories = {space:"advancedSpaceSystems",protection:"protectiveEngineering",energy:"energySystems",materials:"advancedMaterials",life:"lifeSciences",environment:"environmentalStewardship",robotics:"roboticsSystems",society:"knowledgeSystems"};
  const labels = {
    en: [
      ["Space science & exploration","Physics, spacecraft, propulsion, habitats and exploration systems."],
      ["Protection, rescue & resilience","Protective engineering, emergency response and civil resilience."],
      ["Energy & power systems","Clean generation, storage, conversion and dependable power infrastructure."],
      ["Advanced materials & manufacturing","Material characterization, fabrication, repair and lifecycle performance."],
      ["Health, biology & human support","Life sciences, assistive systems and human-centred research."],
      ["Environment, climate & ecosystems","Environmental monitoring, restoration and climate resilience."],
      ["Robotics, autonomy & mobility","Robotic systems, autonomous operations and assistive mobility."],
      ["Computing, knowledge & society","Computing, information systems, communication and public knowledge."],
      ["Sensing, monitoring & forecasting","Cross-domain sensing, observation, mapping, detection and prediction."],
      ["Systems integration & reliability","Cross-domain coordination, operations, fault recovery and system reliability."]
    ],
    fr: [
      ["Sciences et exploration spatiales","Physique, véhicules spatiaux, propulsion, habitats et exploration."],
      ["Protection, secours et résilience","Ingénierie de protection, réponse aux urgences et résilience civile."],
      ["Énergie et systèmes électriques","Production propre, stockage, conversion et infrastructures énergétiques fiables."],
      ["Matériaux avancés et fabrication","Caractérisation, fabrication, réparation et cycle de vie des matériaux."],
      ["Santé, biologie et assistance humaine","Sciences du vivant, systèmes d’assistance et recherche centrée sur l’humain."],
      ["Environnement, climat et écosystèmes","Surveillance environnementale, restauration et résilience climatique."],
      ["Robotique, autonomie et mobilité","Systèmes robotiques, opérations autonomes et mobilité assistée."],
      ["Calcul, connaissances et société","Informatique, systèmes d’information, communication et connaissances publiques."],
      ["Capteurs, surveillance et prévision","Capteurs transversaux, observation, cartographie, détection et prévision."],
      ["Intégration des systèmes et fiabilité","Coordination, opérations, récupération après panne et fiabilité des systèmes."]
    ]
  };
  function titleCase(value) { return value.replace(/-/g," ").replace(/\b[a-z]/g, c => c.toUpperCase()); }
  function identifier(value) { return value.replace(/-/g," ").split(/\s+/).filter(Boolean).map(p => p[0].toUpperCase()+p.slice(1)).join(""); }
  function generatedProgrammes() {
    const out = [];
    for (const domain of domains) {
      const [domainFamilies, capabilities] = families[domain];
      for (const family of domainFamilies) for (const capability of capabilities) {
        out.push({
          key:"program"+identifier(domain)+identifier(family)+identifier(capability),
          item:{
            en:[titleCase(family)+" "+titleCase(capability)+" Research","Research programme examining "+family.replace(/-/g," ")+" "+capability+" through measurable performance, reproducible methods and independent evaluation. This is a research objective, not a validated technology."],
            fr:["Recherche : "+titleCase(family)+" — "+titleCase(capability),"Programme de recherche consacré à "+capability+" pour le domaine "+family.replace(/-/g," ")+", avec des méthodes reproductibles et une évaluation indépendante. Il s’agit d’un objectif de recherche, pas d’une technologie validée."]
          },
          meta:{category:domain,subcategory:subcategories[domain]},
          searchText:(domain+" "+family+" "+capability+" "+titleCase(family)+" "+titleCase(capability)+" "+titleCase(capability)+" "+("recherche "+family.replace(/-/g," ")+" "+capability)).toLocaleLowerCase(),
          generated:true
        });
        if (out.length===394) return out;
      }
    }
    return out;
  }
  function sensingScore(entry) {
    const value=(entry.searchText||entry.key||"").toLocaleLowerCase();
    const patterns=[/monitor(?:ing)?/g,/sens(?:or|ing)/g,/detect(?:ion)?/g,/forecast(?:ing)?/g,/mapp(?:ing)?/g,/observ(?:ation|e)/g,/inspect(?:ion)?/g,/provenance/g,/measurement/g,/quality/g,/assessment/g,/prediction/g];
    return patterns.reduce((score,re)=>score+((value.match(re)||[]).length*2),0);
  }
  function buildSupercategories(baseEntries) {
    if(!Array.isArray(baseEntries)) throw new TypeError("Catalogue entries must be an array.");
    const seen=new Set();
    const base=baseEntries.map(entry=>{
      if(!entry||typeof entry.key!=="string"||!entry.meta||!domains.includes(entry.meta.category)) throw new TypeError("Every catalogue entry must have a stable key and a recognized domain.");
      if(seen.has(entry.key)) throw new Error("Duplicate catalogue identifier: "+entry.key);
      seen.add(entry.key); return entry;
    });
    const generated=generatedProgrammes();
    for(const entry of generated){if(seen.has(entry.key))throw new Error("Generated programme duplicates an existing identifier: "+entry.key);seen.add(entry.key);}
    const all=base.concat(generated);
    if(all.length!==1000)throw new Error("Expected exactly 1,000 unique research programmes; received "+all.length+".");
    const groups=[],remaining=[];
    for(const domain of domains){
      const domainBase=base.filter(entry=>entry.meta.category===domain);
      const domainGenerated=generated.filter(entry=>entry.meta.category===domain);
      const chosenBase=domainBase.slice(0,100);
      const chosenGenerated=domainGenerated.slice(0,Math.max(0,100-chosenBase.length));
      if(chosenBase.length+chosenGenerated.length!==100)throw new Error("Insufficient entries to fill the "+domain+" super-category.");
      remaining.push(...domainBase.slice(100),...domainGenerated.slice(chosenGenerated.length));
      const index=domains.indexOf(domain),label=labels.en[index];
      groups.push({id:domain,title:label[0],description:label[1],titleFr:labels.fr[index][0],descriptionFr:labels.fr[index][1],entries:chosenBase.concat(chosenGenerated)});
    }
    if(remaining.length!==200)throw new Error("Expected 200 cross-domain entries after the eight domain groups; received "+remaining.length+".");
    const ranked=remaining.slice().sort((a,b)=>sensingScore(b)-sensingScore(a)||a.key.localeCompare(b.key));
    groups.push({id:"sensing",title:labels.en[8][0],description:labels.en[8][1],titleFr:labels.fr[8][0],descriptionFr:labels.fr[8][1],entries:ranked.slice(0,100)});
    groups.push({id:"systems",title:labels.en[9][0],description:labels.en[9][1],titleFr:labels.fr[9][0],descriptionFr:labels.fr[9][1],entries:ranked.slice(100)});
    const grouped=groups.flatMap(group=>group.entries);
    if(groups.length!==10||groups.some(group=>group.entries.length!==100)||grouped.length!==1000||new Set(grouped.map(entry=>entry.key)).size!==1000)throw new Error("Super-category integrity check failed.");
    return groups;
  }
  return {buildSupercategories,generatedProgrammes,domains};
});