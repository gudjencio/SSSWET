(() => {
  "use strict";
  const copy = {
    en: {
      button:"Report", title:"Suggest a project improvement",
      intro:"Choose a useful improvement or correction. Reports enter the project review queue; nothing is changed automatically.",
      category:"Improvement area", titleLabel:"Short title", detail:"What should be improved?",
      send:"Send report", cancel:"Cancel", sending:"Sending…",
      success:"Thank you. Your suggestion was added to the project review queue.",
      unavailable:"Report submission is not configured yet. Please try again later.",
      error:"The report could not be sent. Please try again later.",
      placeholder:"Describe the improvement and, if possible, the expected result.",
      options:[
        ["bug","Bug or display correction"],["translation","Translation and language quality"],
        ["accessibility","Accessibility and inclusive design"],["performance","Performance and loading speed"],
        ["security","Security and privacy"],["documentation","Documentation and guidance"],
        ["research-quality","Scientific rigour and source traceability"],["reliability","Reliability and data integrity"],
        ["usability","Interface clarity and ease of use"],["new-feature","Useful new feature"],
        ["compatibility","Browser and device compatibility"],["other","Other useful improvement"]
      ]
    },
    fr: {
      button:"Signaler", title:"Proposer une amélioration du projet",
      intro:"Choisissez une amélioration utile ou une correction. Les signalements rejoignent la file d’examen du projet ; aucune modification n’est appliquée automatiquement.",
      category:"Domaine d’amélioration", titleLabel:"Titre court", detail:"Que faudrait-il améliorer ?",
      send:"Envoyer le signalement", cancel:"Annuler", sending:"Envoi…",
      success:"Merci. Votre suggestion a été ajoutée à la file d’examen du projet.",
      unavailable:"L’envoi des signalements n’est pas encore configuré. Réessayez plus tard.",
      error:"Le signalement n’a pas pu être envoyé. Réessayez plus tard.",
      placeholder:"Décrivez l’amélioration et, si possible, le résultat attendu.",
      options:[
        ["bug","Bug ou correction d’affichage"],["translation","Traductions et qualité linguistique"],
        ["accessibility","Accessibilité et conception inclusive"],["performance","Performances et vitesse de chargement"],
        ["security","Sécurité et confidentialité"],["documentation","Documentation et guides"],
        ["research-quality","Rigueur scientifique et traçabilité des sources"],["reliability","Fiabilité et intégrité des données"],
        ["usability","Clarté et facilité d’utilisation"],["new-feature","Nouvelle fonctionnalité utile"],
        ["compatibility","Compatibilité navigateurs et appareils"],["other","Autre amélioration utile"]
      ]
    }
  };
  const language = () => String(document.getElementById("language")?.value || document.documentElement.lang || "en").toLowerCase().split("-")[0];
  const text = () => copy[language()] || copy.en;
  const style = document.createElement("style");
  style.textContent = `
    .report-project-button{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:11px 18px;border:1px solid rgba(255,92,92,.55);border-radius:14px;color:#fff;background:linear-gradient(115deg,#9f242b,#65171d);font:650 12px inherit;cursor:pointer;box-shadow:0 8px 28px rgba(0,0,0,.24)}
    .report-project-button:hover{background:linear-gradient(115deg,#bd3038,#7c1d25);transform:translateY(-1px)}
    .repair-project-slot{display:flex;justify-content:center;align-items:center;gap:10px;flex-wrap:wrap}
    .ssswet-report-dialog{width:min(560px,calc(100% - 28px));max-height:85vh;overflow:auto;border:1px solid rgba(255,255,255,.14);border-radius:18px;background:#101116;color:#f5f5f7;padding:24px;box-shadow:0 24px 90px #000a}
    .ssswet-report-dialog::backdrop{background:#000b;backdrop-filter:blur(5px)}
    .ssswet-report-dialog h2{margin:0 0 8px}.ssswet-report-dialog p{color:#b8bac4;line-height:1.55}
    .ssswet-report-dialog label{display:grid;gap:7px;margin:15px 0;font-size:13px;color:#ddd}
    .ssswet-report-dialog input,.ssswet-report-dialog select,.ssswet-report-dialog textarea{width:100%;box-sizing:border-box;border:1px solid #383a45;border-radius:9px;background:#191b22;color:#fff;padding:11px;font:inherit}
    .ssswet-report-dialog textarea{min-height:120px;resize:vertical}
    .ssswet-report-actions{display:flex;justify-content:flex-end;gap:9px;flex-wrap:wrap;margin-top:18px}
    .ssswet-report-actions button{border:1px solid #555;border-radius:9px;padding:10px 15px;background:#242630;color:white;cursor:pointer}
    .ssswet-report-actions button[type=submit]{background:#a8242d;border-color:#a8242d}
    .ssswet-report-status{min-height:1.4em;font-size:13px}
  `;
  document.head.append(style);
  function init(){
    const slot=document.querySelector(".repair-project-slot");
    if(!slot || document.getElementById("ssswet-report-button")) return;
    const button=document.createElement("button");
    button.type="button";button.id="ssswet-report-button";button.className="report-project-button";
    const dialog=document.createElement("dialog");dialog.className="ssswet-report-dialog";dialog.id="ssswet-report-dialog";
    const form=document.createElement("form");
    const heading=document.createElement("h2"), intro=document.createElement("p");
    const categoryLabel=document.createElement("label"),category=document.createElement("select");
    const titleLabel=document.createElement("label"),title=document.createElement("input");
    const detailLabel=document.createElement("label"),detail=document.createElement("textarea");
    const status=document.createElement("p");status.className="ssswet-report-status";status.setAttribute("role","status");status.setAttribute("aria-live","polite");
    const actions=document.createElement("div");actions.className="ssswet-report-actions";
    const cancel=document.createElement("button");cancel.type="button";
    const submit=document.createElement("button");submit.type="submit";
    title.maxLength=160;title.required=true;detail.maxLength=3000;detail.required=true;
    category.name="category";title.name="title";detail.name="description";
    categoryLabel.append(document.createTextNode(""),category);
    titleLabel.append(document.createTextNode(""),title);
    detailLabel.append(document.createTextNode(""),detail);
    actions.append(cancel,submit);form.append(heading,intro,categoryLabel,titleLabel,detailLabel,status,actions);dialog.append(form);
    slot.append(button,dialog);
    function localize(){
      const t=text();button.textContent=t.button;button.setAttribute("aria-label",t.button);
      heading.textContent=t.title;intro.textContent=t.intro;
      categoryLabel.firstChild.textContent=t.category;titleLabel.firstChild.textContent=t.titleLabel;
      detailLabel.firstChild.textContent=t.detail;title.placeholder=t.titleLabel;detail.placeholder=t.placeholder;
      cancel.textContent=t.cancel;submit.textContent=t.send;
      const previous=category.value;category.replaceChildren();
      t.options.forEach(([value,label])=>{const option=document.createElement("option");option.value=value;option.textContent=label;category.append(option);});
      if(previous)category.value=previous;
    }
    button.addEventListener("click",()=>{localize();status.textContent="";dialog.showModal();});
    cancel.addEventListener("click",()=>dialog.close());
    form.addEventListener("submit",async event=>{
      event.preventDefault();const t=text();submit.disabled=true;submit.textContent=t.sending;status.textContent="";
      try{
        if(typeof window.ssswetApiFetch!=="function") throw new Error("unavailable");
        const response=await window.ssswetApiFetch("/api/project-reports",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({category:category.value,title:title.value.trim(),description:detail.value.trim(),language:language(),page:location.pathname})});
        const result=await response.json();
        if(!response.ok) throw new Error(result.error||"submission failed");
        status.textContent=t.success;form.reset();localize();
      }catch(error){status.textContent=error.message==="unavailable"||error.status===503?t.unavailable:t.error;}
      finally{submit.disabled=false;submit.textContent=text().send;}
    });
    document.getElementById("language")?.addEventListener("change",localize);
    window.addEventListener("ssswet-language-changed",localize);
    localize();
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();