(() => {
"use strict";
const root=document.getElementById("technology-feasibility-list");if(!root)return;
const status=document.getElementById("technology-feasibility-status"),refresh=document.getElementById("technology-feasibility-refresh");
const names={cellular:"Cellular improvement",longevity:"Longevity",armor:"Protective armor",jetpack:"Jetpacks",translator:"Human–alien translators",spacetime:"Spacetime physics",timetravel:"Time travel"};
const fr=document.documentElement.lang==="fr";
const text=fr?{empty:"Aucun dossier de recherche enregistré.",unavailable:"Observatoire indisponible : démarrez le moteur local SSSWET.",records:"entrées",refs:"références",stage:"Maturité des dossiers",feasibility:"Faisabilité technique",notAssessed:"Non évaluée",delivery:"Préparation à la livraison",missing:"Points restant à examiner",none:"Aucun point manquant dans les catégories suivies.",integrity:"Intégrité du journal",intact:"Intacte",broken:"Anomalie détectée"}:{empty:"No research records have been recorded.",unavailable:"Observatory unavailable: start the local SSSWET engine.",records:"records",refs:"references",stage:"Recorded research maturity",feasibility:"Technical feasibility",notAssessed:"Not assessed",delivery:"Delivery readiness",missing:"Areas still requiring review",none:"No missing area in the categories tracked.",integrity:"Journal integrity",intact:"Intact",broken:"Integrity issue detected"};
function el(tag,cls,value){const n=document.createElement(tag);if(cls)n.className=cls;if(value!==undefined)n.textContent=value;return n;}
async function load(){root.replaceChildren();status.textContent="…";try{
const response=await fetch("/api/technology-feasibility",{cache:"no-store"});if(!response.ok)throw new Error("HTTP "+response.status);
const report=await response.json(),integrity=report.journal_chain_integrity||{};
status.textContent=(integrity.chain_intact?text.intact:text.broken)+" · "+text.integrity+" · "+integrity.entries_checked+" "+text.records;
report.technologies.forEach(item=>{const card=el("article","technology-feasibility-card"),heading=el("div","technology-feasibility-card-heading");
heading.append(el("strong","",names[item.technology]||item.label),el("span","technology-feasibility-count",item.record_count+" "+text.records));card.append(heading);
const metrics=el("div","technology-feasibility-metrics");metrics.append(el("span","",text.stage+": "+item.recorded_maturity.replaceAll("_"," ")),el("span","",text.feasibility+": "+text.notAssessed),el("span","",text.delivery+": "+text.notAssessed),el("span","",item.evidence_reference_count+" "+text.refs));card.append(metrics,el("h4","",text.missing));
if(!item.missing_review_areas.length)card.append(el("p","technology-feasibility-empty",text.none));else{const list=el("ul","technology-feasibility-next");item.suggested_next_steps.forEach(step=>list.append(el("li","",step)));card.append(list);}root.append(card);});
if(!report.technologies.length)root.append(el("p","technology-feasibility-empty",text.empty));
}catch(error){status.textContent=text.unavailable;root.append(el("p","technology-feasibility-empty",error.message));}}
refresh?.addEventListener("click",load);window.addEventListener("ssswet-language-changed",load);load();
})();
