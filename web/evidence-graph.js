(() => {
  "use strict";

  const palette = {
    source: "#8d8d8d", protocol: "#b7a06a", dataset: "#7e9b9b", run: "#8b7eaa",
    comparison: "#9a8c67", objection: "#a56f6f", review: "#718e71", dispute: "#9a7777",
    event: "#777", center: "#e5e5e5"
  };
  const labels = () => {
    const code = (document.documentElement.lang || "en").toLowerCase().split("-")[0];
    const dictionaries = {
      en: ["Source","Protocol","Dataset","Run","Comparison","Objection","Review","Dispute","Event","Dossier","Legend","Recorded relationships only","The graph does not infer relationships missing from the records.","Select a node to inspect its details and direct links.","Direct connections","Clear selection","There are no records to display for this dossier."],
      fr: ["Source","Protocole","Jeu de données","Exécution","Comparaison","Objection","Revue","Litige","Événement","Dossier","Légende","Relations enregistrées uniquement","Le graphe ne déduit pas de relations absentes des enregistrements.","Sélectionnez un nœud pour examiner ses informations et ses liens directs.","Liens directs","Réinitialiser la sélection","Aucun élément à représenter dans ce dossier."],
      es: ["Fuente","Protocolo","Conjunto de datos","Ejecución","Comparación","Objeción","Revisión","Disputa","Evento","Expediente","Leyenda","Solo relaciones registradas","El grafo no infiere relaciones que no estén registradas.","Seleccione un nodo para consultar sus datos y conexiones directas.","Conexiones directas","Borrar selección","No hay registros que mostrar en este expediente."],
      de: ["Quelle","Protokoll","Datensatz","Durchlauf","Vergleich","Einwand","Prüfung","Streitfall","Ereignis","Dossier","Legende","Nur dokumentierte Beziehungen","Der Graph leitet keine nicht dokumentierten Beziehungen ab.","Wählen Sie einen Knoten, um Details und direkte Verbindungen anzuzeigen.","Direkte Verbindungen","Auswahl zurücksetzen","Für dieses Dossier liegen keine darstellbaren Einträge vor."],
      it: ["Fonte","Protocollo","Dataset","Esecuzione","Confronto","Obiezione","Revisione","Controversia","Evento","Dossier","Legenda","Solo relazioni registrate","Il grafo non deduce relazioni non presenti nei registri.","Seleziona un nodo per esaminarne i dettagli e i collegamenti diretti.","Collegamenti diretti","Reimposta selezione","Nessun elemento da visualizzare in questo dossier."],
      pt: ["Fonte","Protocolo","Conjunto de dados","Execução","Comparação","Objeção","Revisão","Disputa","Evento","Dossiê","Legenda","Apenas relações registadas","O grafo não infere relações ausentes dos registos.","Selecione um nó para consultar os detalhes e as ligações diretas.","Ligações diretas","Limpar seleção","Não há registos para apresentar neste dossiê."],
      nl: ["Bron","Protocol","Dataset","Uitvoering","Vergelijking","Bezwaar","Beoordeling","Geschil","Gebeurtenis","Dossier","Legenda","Alleen vastgelegde relaties","De grafiek leidt geen relaties af die niet zijn vastgelegd.","Selecteer een knooppunt om details en directe verbindingen te bekijken.","Directe verbindingen","Selectie wissen","Er zijn geen gegevens om in dit dossier weer te geven."],
      ru: ["Источник","Протокол","Набор данных","Запуск","Сравнение","Возражение","Проверка","Спор","Событие","Досье","Обозначения","Только зарегистрированные связи","Граф не выводит связи, отсутствующие в записях.","Выберите узел, чтобы просмотреть сведения и прямые связи.","Прямые связи","Сбросить выбор","В этом досье нет записей для отображения."],
      uk: ["Джерело","Протокол","Набір даних","Запуск","Порівняння","Заперечення","Перевірка","Суперечка","Подія","Досьє","Позначення","Лише зафіксовані зв’язки","Граф не виводить зв’язки, відсутні в записах.","Виберіть вузол, щоб переглянути його дані та прямі зв’язки.","Прямі зв’язки","Скинути вибір","У цьому досьє немає записів для відображення."],
      ar: ["المصدر","البروتوكول","مجموعة البيانات","التشغيل","المقارنة","اعتراض","مراجعة","نزاع","حدث","ملف الأدلة","المفتاح","العلاقات المسجلة فقط","لا يستنتج الرسم علاقات غير موجودة في السجلات.","اختر عقدة لفحص تفاصيلها وروابطها المباشرة.","الروابط المباشرة","مسح التحديد","لا توجد سجلات لعرضها في هذا الملف."],
      he: ["מקור","פרוטוקול","מערך נתונים","הרצה","השוואה","השגה","סקירה","מחלוקת","אירוע","תיק ראיות","מקרא","קשרים מתועדים בלבד","התרשים אינו מסיק קשרים שאינם מופיעים ברשומות.","בחרו צומת כדי לעיין בפרטים ובקישורים הישירים שלו.","קישורים ישירים","איפוס הבחירה","אין רשומות להצגה בתיק זה."],
      ja: ["情報源","プロトコル","データセット","実行","比較","異議","レビュー","紛争","イベント","証拠資料","凡例","記録された関係のみ","記録にない関係をグラフが推測することはありません。","ノードを選択して詳細と直接リンクを確認してください。","直接リンク","選択を解除","この資料に表示できる記録はありません。"],
      ko: ["출처","프로토콜","데이터 세트","실행","비교","이의","검토","분쟁","이벤트","증거 자료","범례","기록된 관계만 표시","그래프는 기록에 없는 관계를 추론하지 않습니다.","노드를 선택해 세부 정보와 직접 연결을 확인하세요.","직접 연결","선택 초기화","이 자료에 표시할 기록이 없습니다."],
      zh: ["来源","协议","数据集","运行","比较","异议","审查","争议","事件","证据档案","图例","仅显示已记录的关系","图表不会推断记录中不存在的关系。","选择一个节点以查看详细信息和直接关联。","直接关联","清除选择","此档案没有可显示的记录。"],
      hi: ["स्रोत","प्रोटोकॉल","डेटासेट","रन","तुलना","आपत्ति","समीक्षा","विवाद","घटना","साक्ष्य dossier","संकेत सूची","केवल दर्ज संबंध","ग्राफ़ उन संबंधों का अनुमान नहीं लगाता जो रिकॉर्ड में मौजूद नहीं हैं।","विवरण और सीधे संबंध देखने के लिए कोई नोड चुनें।","सीधे संबंध","चयन रीसेट करें","इस dossier में दिखाने के लिए कोई रिकॉर्ड नहीं है।"]
    };
    const v = dictionaries[code] || dictionaries.en;
    return { source:v[0], protocol:v[1], dataset:v[2], run:v[3], comparison:v[4], objection:v[5], review:v[6], dispute:v[7], event:v[8], center:v[9], legend:v[10], trace:v[11], note:v[12], choose:v[13], connected:v[14], reset:v[15], empty:v[16] };
  };
  const value = (v) => v === undefined || v === null || v === "" ? "—" : String(v);
  function makeNodes(dossier) {
    const nodes = [{ id: "dossier", label: value(dossier.title || dossier.dossier_id), type: "center", detail: value(dossier.dossier_id) }];
    const add = (items, type, idKey, labelKey) => {
      if (!Array.isArray(items)) return;
      items.forEach((item, i) => {
        const rawId = item && typeof item === "object" ? item[idKey] : null;
        const id = type + ":" + value(rawId || i);
        const label = item && typeof item === "object" ? (item[labelKey] || rawId || id) : item;
        nodes.push({ id, label: value(label), type, detail: item && typeof item === "object" ? Object.entries(item).map(([k,v]) => k + ": " + value(v)).join("\n") : value(item) });
      });
    };
    add(dossier.sources, "source", "source_id", "title");
    add(dossier.protocols, "protocol", "protocol_id", "version");
    add(dossier.datasets, "dataset", "dataset_id", "version");
    add(dossier.runs, "run", "run_id", "status");
    add(dossier.comparisons, "comparison", "comparison_id", "status");
    add(dossier.objections, "objection", "id", "summary");
    add(dossier.disputes, "dispute", "case_id", "status");
    add((dossier.events || []).filter((e) => e.kind === "review"), "review", "event_id", "decision");
    return nodes;
  }
  function makeEdges(dossier, nodes) {
    const ids = new Set(nodes.map(n => n.id)); const edges = [];
    const link = (a,b) => { if (ids.has(a) && ids.has(b) && !edges.some(e => (e[0]===a&&e[1]===b)||(e[0]===b&&e[1]===a))) edges.push([a,b]); };
    nodes.filter(n => n.id !== "dossier").forEach(n => link("dossier", n.id));
    (dossier.runs || []).forEach(r => {
      const id = "run:" + value(r.run_id);
      if (r.protocol_id) link("protocol:" + value(r.protocol_id), id);
      if (r.dataset_id) link("dataset:" + value(r.dataset_id), id);
    });
    (dossier.comparisons || []).forEach(c => {
      const id = "comparison:" + value(c.comparison_id);
      if (c.reference_run_id) link("run:" + value(c.reference_run_id), id);
      if (c.candidate_run_id) link("run:" + value(c.candidate_run_id), id);
    });
    return edges;
  }
  function render(container, dossier) {
    if (!container || !dossier) return;
    const t = labels(); container.replaceChildren();
    const nodes = makeNodes(dossier); const edges = makeEdges(dossier, nodes);
    if (nodes.length <= 1) { const p=document.createElement("p"); p.className="visual-empty"; p.textContent=t.empty; container.append(p); return; }
    const width=760, height=Math.max(300,Math.min(680,170+nodes.length*26));
    const svg=document.createElementNS("http://www.w3.org/2000/svg","svg");
    svg.setAttribute("viewBox",`0 0 ${width} ${height}`); svg.setAttribute("role","group"); svg.setAttribute("aria-label",t.trace); svg.classList.add("evidence-graph-svg");
    const center={x:width/2,y:height/2}; const positions=new Map([["dossier",center]]);
    const peripheral=nodes.filter(n=>n.id!=="dossier");
    peripheral.forEach((n,i)=>{ const a=-Math.PI/2+i/peripheral.length*Math.PI*2; const r=Math.min(width,height)*.35; positions.set(n.id,{x:center.x+Math.cos(a)*r,y:center.y+Math.sin(a)*r}); });
    const edgeEls=[];
    edges.forEach(([a,b])=>{ const p=positions.get(a),q=positions.get(b); const line=document.createElementNS("http://www.w3.org/2000/svg","line"); line.setAttribute("x1",p.x);line.setAttribute("y1",p.y);line.setAttribute("x2",q.x);line.setAttribute("y2",q.y);line.classList.add("evidence-graph-edge");line.dataset.a=a;line.dataset.b=b;svg.append(line);edgeEls.push(line); });
    const nodeEls=new Map();
    nodes.forEach(n=>{
      const p=positions.get(n.id),g=document.createElementNS("http://www.w3.org/2000/svg","g");
      g.classList.add("evidence-graph-node");g.setAttribute("tabindex","0");g.setAttribute("role","button");g.setAttribute("aria-label",n.type+": "+n.label);g.dataset.nodeId=n.id;
      const c=document.createElementNS("http://www.w3.org/2000/svg","circle");c.setAttribute("cx",p.x);c.setAttribute("cy",p.y);c.setAttribute("r",n.type==="center"?25:14);c.setAttribute("fill",palette[n.type]);c.setAttribute("fill-opacity",".17");c.setAttribute("stroke",palette[n.type]);g.append(c);
      const label=document.createElementNS("http://www.w3.org/2000/svg","text");label.setAttribute("x",p.x);label.setAttribute("y",p.y+(n.type==="center"?42:31));label.setAttribute("text-anchor","middle");label.textContent=n.label.slice(0,26);g.append(label);
      const select=()=>selectNode(n.id);g.addEventListener("click",select);g.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();select();}});
      svg.append(g);nodeEls.set(n.id,g);
    });
    const detail=document.createElement("div");detail.className="evidence-graph-selection";detail.setAttribute("aria-live","polite");
    const legend=document.createElement("div");legend.className="evidence-graph-legend";
    ["source","protocol","dataset","run","comparison","objection","review","dispute"].forEach(type=>{const item=document.createElement("span");item.textContent=t[type];item.style.setProperty("--evidence-node-color",palette[type]);legend.append(item);});
    const note=document.createElement("p");note.className="evidence-graph-note";note.textContent=t.note;
    const reset=document.createElement("button");reset.type="button";reset.className="evidence-graph-reset";reset.textContent=t.reset;reset.addEventListener("click",()=>selectNode(null));
    container.append(svg,detail,reset,legend,note);
    function selectNode(id) {
      const selected=nodes.find(n=>n.id===id); const neighbors=new Set();
      if(selected) edges.forEach(([a,b])=>{if(a===id)neighbors.add(b);if(b===id)neighbors.add(a);});
      nodeEls.forEach((el,nodeId)=>{el.classList.toggle("is-selected",nodeId===id);el.classList.toggle("is-dimmed",!!selected&&nodeId!==id&&!neighbors.has(nodeId));});
      edgeEls.forEach(el=>{const connected=!!selected&&(el.dataset.a===id||el.dataset.b===id);el.classList.toggle("is-highlighted",connected);el.classList.toggle("is-dimmed",!!selected&&!connected);});
      detail.replaceChildren();
      if(!selected){const p=document.createElement("p");p.textContent=t.choose;detail.append(p);return;}
      const heading=document.createElement("strong");heading.textContent=t[selected.type]+": "+selected.label;detail.append(heading);
      const content=document.createElement("pre");content.textContent=selected.detail;detail.append(content);
      const connected=document.createElement("p");connected.className="evidence-graph-connections";connected.textContent=t.connected+": "+(neighbors.size?[...neighbors].map(id=>{const n=nodes.find(x=>x.id===id);return n?t[n.type]+": "+n.label:id;}).join(" · "):"—");detail.append(connected);
    }
    selectNode(null);
  }
  window.SSSWETRenderEvidenceGraph = render;
})();