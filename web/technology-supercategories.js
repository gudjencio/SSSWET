(() => {
  "use strict";
  const root=document.getElementById("technology-grid");
  const heading=document.querySelector(".technology-heading");
  const taxonomy=window.SSSWET_TECHNOLOGY_TAXONOMY;
  const data=window.SSSWET_SUPERCATEGORY_DATA;
  const baseEntries=window.SSSWET_TECHNOLOGY_ENTRIES;
  if(!root||!heading||!taxonomy||!data||!Array.isArray(baseEntries))return;
  let groups;
  try{groups=data.buildSupercategories(baseEntries);}
  catch(error){console.error("SSSWET grouped catalogue was not activated; the original catalogue remains available.",error);return;}

  heading.querySelector(".technology-catalogue-controls")?.remove();
  if(root.nextElementSibling?.classList.contains("technology-pagination"))root.nextElementSibling.remove();
  const toolbar=document.createElement("div");
  toolbar.className="technology-supercategory-tools";
  const searchLabel=document.createElement("label");
  searchLabel.className="technology-supercategory-search";
  const searchCaption=document.createElement("span");
  const search=document.createElement("input");
  search.type="search";search.id="technology-supercategory-search";search.autocomplete="off";
  search.setAttribute("aria-label","Search all research programmes");
  searchLabel.append(searchCaption,search);toolbar.append(searchLabel);heading.append(toolbar);
  const count=document.getElementById("technology-catalogue-count");
  const note=document.querySelector(".technology-catalogue-note");
  const translations={
    en:{search:"Search all 1,000 research programmes",count:"1,000 research programmes · 10 super-categories · 100 each",note:"Explore ten focused collections. Each collection contains 100 programmes; open only the areas you need. Search covers the complete catalogue.",explore:"Explore programme",empty:"No programmes match this search.",result:"matching programmes",all:"100 programmes"},
    fr:{search:"Rechercher parmi les 1 000 programmes",count:"1 000 programmes de recherche · 10 super-catégories · 100 chacune",note:"Explorez dix collections thématiques. Chaque collection contient 100 programmes ; ouvrez uniquement les domaines utiles. La recherche couvre tout le catalogue.",explore:"Explorer le programme",empty:"Aucun programme ne correspond à cette recherche.",result:"programmes correspondants",all:"100 programmes"}
  };
  function currentLanguage(){return(document.documentElement.lang||document.getElementById("language")?.value||"en").toLowerCase().split("-")[0];}
  function localized(entry,language){return entry.item?.[language]||entry.item?.en||entry.item?.fr||[entry.key,""];}
  function createCard(entry,index,group,language,copy){
    const values=localized(entry,language),card=document.createElement("article");
    card.className="technology-card";
    const number=document.createElement("span");number.className="technology-number";number.textContent=String(index+1).padStart(3,"0");
    const meta=document.createElement("small");meta.className="technology-category-tag";meta.textContent=language==="fr"?group.titleFr:group.title;
    const title=document.createElement("h3");title.textContent=values[0]||entry.key;
    const description=document.createElement("p");description.textContent=values[1]||"";
    const action=document.createElement("button");action.type="button";action.dataset.tech=entry.key;action.textContent=copy.explore;
    card.append(number,meta,title,description,action);return card;
  }
  function render(){
    const language=currentLanguage(),copy=translations[language]||translations.en;
    searchCaption.textContent=copy.search;search.setAttribute("aria-label",copy.search);
    if(count)count.textContent=copy.count;if(note)note.textContent=copy.note;
    const query=search.value.trim().toLocaleLowerCase(),fragment=document.createDocumentFragment();
    let matches=0,openedSearchGroup=false;
    groups.forEach(group=>{
      const matching=query?group.entries.filter(entry=>(entry.searchText||entry.key).toLocaleLowerCase().includes(query)):group.entries;
      if(query&&!matching.length)return;
      matches+=matching.length;
      const details=document.createElement("details");details.className="technology-supercategory";details.dataset.supercategory=group.id;details.open=Boolean(query&&matching.length&&!openedSearchGroup);
      if(details.open)openedSearchGroup=true;
      const summary=document.createElement("summary"),headingLine=document.createElement("span");headingLine.className="technology-supercategory-heading";
      const title=document.createElement("strong");title.textContent=language==="fr"?group.titleFr:group.title;
      const quantity=document.createElement("span");quantity.className="technology-supercategory-count";quantity.textContent=query?matching.length+" "+copy.result:copy.all;
      headingLine.append(title,quantity);
      const description=document.createElement("span");description.className="technology-supercategory-description";description.textContent=language==="fr"?group.descriptionFr:group.description;
      summary.append(headingLine,description);
      const cards=document.createElement("div");cards.className="technology-supercategory-cards";
      summary.setAttribute("aria-label",(language==="fr"?group.titleFr:group.title)+" — "+matching.length+" "+copy.result);
      details.append(summary,cards);
      const fillCards=()=>{
        if(cards.dataset.rendered==="true")return;
        const cardFragment=document.createDocumentFragment();
        matching.forEach((entry,index)=>cardFragment.append(createCard(entry,index+1,group,language,copy)));
        cards.append(cardFragment);cards.dataset.rendered="true";window.SSSWET_RENDER_PORTFOLIO?.();
      };
      details.addEventListener("toggle",()=>{if(details.open)fillCards();});
      if(details.open)fillCards();
      fragment.append(details);
    });
    root.replaceChildren(fragment);root.classList.add("technology-supercategory-grid");window.SSSWET_RENDER_PORTFOLIO?.();
    if(query&&!matches){const empty=document.createElement("p");empty.className="technology-catalogue-empty";empty.textContent=copy.empty;root.append(empty);}
  }
  let searchTimer=0;
  search.addEventListener("input",()=>{window.clearTimeout(searchTimer);searchTimer=window.setTimeout(render,90);});
  window.addEventListener("ssswet-language-changed",render);
  document.getElementById("language")?.addEventListener("change",render);
  render();
  window.SSSWET_SUPERCATEGORY_VIEW={groupCount:groups.length,programmeCount:groups.reduce((total,group)=>total+group.entries.length,0),groups:groups.map(group=>({id:group.id,count:group.entries.length}))};
})();