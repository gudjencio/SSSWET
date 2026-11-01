(() => {
  "use strict";
  const root=document.getElementById("research-journal-list");
  if(!root) return;
  const status=document.getElementById("research-journal-status");
  const filter=document.getElementById("research-journal-filter");
  const form=document.getElementById("research-journal-form");
  const refresh=document.getElementById("research-journal-refresh");
  const labels={
    en:{empty:"No journal entries have been recorded.",unavailable:"The local research journal is unavailable. Start the SSSWET local engine to view or add entries.",chain:"Hash-chain integrity",intact:"Intact",broken:"Integrity issue detected",entries:"entries",validity:"Scientific validity established: no",refs:"References",author:"Recorded by",created:"Recorded",classification:"Classification",state:"State",write:"Entries can only be added from the local machine.",saved:"Entry recorded permanently.",error:"Could not record entry: "},
    fr:{empty:"Aucune entrée n’a encore été enregistrée.",unavailable:"Le journal local est indisponible. Démarrez le moteur local SSSWET pour consulter ou ajouter des entrées.",chain:"Intégrité de la chaîne de hachage",intact:"Intacte",broken:"Problème d’intégrité détecté",entries:"entrées",validity:"Validité scientifique établie : non",refs:"Références",author:"Enregistré par",created:"Enregistré le",classification:"Classification",state:"État",write:"Les entrées ne peuvent être ajoutées que depuis la machine locale.",saved:"Entrée ajoutée définitivement.",error:"Impossible d’enregistrer : "}
  };
  const t=()=>labels[document.documentElement.lang==="fr"?"fr":"en"];
  const names={cellular:"Cellular improvement",longevity:"Longevity",armor:"Armor",jetpack:"Jetpacks",translator:"Human–alien translators",spacetime:"Spacetime physics",timetravel:"Time travel"};
  function node(tag,className,value){const el=document.createElement(tag);if(className)el.className=className;if(value!==undefined)el.textContent=value;return el;}
  async function load(){
    root.replaceChildren();status.textContent="…";
    try{
      const query=filter.value?"?technology="+encodeURIComponent(filter.value):"";
      const response=await window.ssswetApiFetch("/api/research-journal"+query);
      if(!response.ok) throw new Error("HTTP "+response.status);
      const report=await response.json();const chain=report.chain_integrity||{};
      status.textContent=(chain.chain_intact?t().intact:t().broken)+" · "+t().chain+" · "+chain.entries_checked+" "+t().entries+" · "+t().validity;
      if(!report.entries.length){root.append(node("p","research-journal-empty",t().empty));return;}
      report.entries.forEach(entry=>{
        const card=node("article","research-journal-entry");
        const heading=node("div","research-journal-entry-heading");
        heading.append(node("strong","",entry.title),node("span","research-journal-classification",entry.classification.replaceAll("_"," ")));
        card.append(heading,node("p","research-journal-summary",entry.summary));
        const meta=node("div","research-journal-meta",names[entry.technology]||entry.technology+" · "+entry.event_type.replaceAll("_"," ")+" · "+entry.state.replaceAll("_"," ")+" · "+entry.created_at+" · "+entry.author_label);
        card.append(meta);
        if(entry.evidence_refs?.length) card.append(node("p","research-journal-refs",t().refs+": "+entry.evidence_refs.join(" · ")));
        card.append(node("code","research-journal-hash",entry.entry_hash));
        root.append(card);
      });
    }catch(error){status.textContent=t().unavailable;root.append(node("p","research-journal-empty",error.message));}
  }
  form?.addEventListener("submit",async event=>{
    event.preventDefault();const button=form.querySelector('button[type="submit"]');button.disabled=true;
    const data=new FormData(form);const payload=Object.fromEntries(data.entries());
    payload.evidence_refs=String(payload.evidence_refs||"").split("\n").map(value=>value.trim()).filter(Boolean);
    try{
      const response=await fetch("/api/research-journal",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
      const result=await response.json();if(!response.ok)throw new Error(result.error||"HTTP "+response.status);
      form.reset();await load();status.textContent=t().saved+" · "+result.entry.entry_id;
    }catch(error){status.textContent=t().error+error.message;}
    finally{button.disabled=false;}
  });
  refresh?.addEventListener("click",load);filter?.addEventListener("change",load);
  window.addEventListener("ssswet-language-changed",load);load();
})();
