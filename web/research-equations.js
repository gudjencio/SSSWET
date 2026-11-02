(() => {
  "use strict";
  const translations = {
    en:{label:"LIVE RESEARCH EXCHANGE",waiting:"Waiting for live agent messages",evidence:"outputs with evidence",outputs:"recent outputs",pending:"awaiting review",active:"active agents",completed:"completed tasks",total:"total tasks",ratio:"evidence coverage",handoff:"shared by",note:"research note",roles:{general_researcher:"General researcher",independent_verifier:"Independent verifier",medical_researcher:"Medical researcher",materials_scientist:"Materials scientist"}},
    fr:{label:"ÉCHANGES DE RECHERCHE EN DIRECT",waiting:"En attente des messages des agents",evidence:"résultats avec preuves jointes",outputs:"résultats récents",pending:"en attente d’examen",active:"agents actifs",completed:"tâches terminées",total:"tâches au total",ratio:"couverture des preuves jointes",handoff:"transmis par",note:"note de recherche",roles:{general_researcher:"Chercheur généraliste",independent_verifier:"Vérificateur indépendant",medical_researcher:"Chercheur en médecine",materials_scientist:"Spécialiste des matériaux"}},
    es:{label:"INTERCAMBIO DE INVESTIGACIÓN EN DIRECTO",waiting:"Esperando mensajes de los agentes",evidence:"resultados con pruebas adjuntas",outputs:"resultados recientes",pending:"pendientes de revisión",active:"agentes activos",completed:"tareas completadas",total:"tareas totales",ratio:"cobertura de pruebas",handoff:"compartido por",note:"nota de investigación",roles:{general_researcher:"Investigador general",independent_verifier:"Verificador independiente",medical_researcher:"Investigador médico",materials_scientist:"Científico de materiales"}},
    de:{label:"LIVE-FORSCHUNGSAUSTAUSCH",waiting:"Warte auf Nachrichten der Agenten",evidence:"Ergebnisse mit Belegen",outputs:"aktuelle Ergebnisse",pending:"zur Prüfung ausstehend",active:"aktive Agenten",completed:"abgeschlossene Aufgaben",total:"Aufgaben insgesamt",ratio:"Belegabdeckung",handoff:"geteilt von",note:"Forschungsnotiz",roles:{general_researcher:"Allgemeiner Forscher",independent_verifier:"Unabhängiger Prüfer",medical_researcher:"Medizinischer Forscher",materials_scientist:"Materialwissenschaftler"}},
    it:{label:"SCAMBIO DI RICERCA IN DIRETTA",waiting:"In attesa dei messaggi degli agenti",evidence:"risultati con prove allegate",outputs:"risultati recenti",pending:"in attesa di revisione",active:"agenti attivi",completed:"attività completate",total:"attività totali",ratio:"copertura delle prove",handoff:"condiviso da",note:"nota di ricerca",roles:{general_researcher:"Ricercatore generale",independent_verifier:"Verificatore indipendente",medical_researcher:"Ricercatore medico",materials_scientist:"Scienziato dei materiali"}},
    pt:{label:"TROCA DE PESQUISA AO VIVO",waiting:"À espera de mensagens dos agentes",evidence:"resultados com provas anexadas",outputs:"resultados recentes",pending:"a aguardar revisão",active:"agentes ativos",completed:"tarefas concluídas",total:"tarefas totais",ratio:"cobertura de provas",handoff:"partilhado por",note:"nota de investigação",roles:{general_researcher:"Investigador geral",independent_verifier:"Verificador independente",medical_researcher:"Investigador médico",materials_scientist:"Cientista de materiais"}},
    nl:{label:"LIVE ONDERZOEKSUITWISSELING",waiting:"Wachten op berichten van agents",evidence:"resultaten met bewijs",outputs:"recente resultaten",pending:"wacht op beoordeling",active:"actieve agents",completed:"voltooide taken",total:"totaal aantal taken",ratio:"bewijsdekking",handoff:"gedeeld door",note:"onderzoeksnotitie",roles:{general_researcher:"Algemeen onderzoeker",independent_verifier:"Onafhankelijke verificateur",medical_researcher:"Medisch onderzoeker",materials_scientist:"Materiaalkundige"}},
    ru:{label:"ОБМЕН ИССЛЕДОВАНИЯМИ В РЕАЛЬНОМ ВРЕМЕНИ",waiting:"Ожидание сообщений агентов",evidence:"результатов с доказательствами",outputs:"недавние результаты",pending:"ожидают проверки",active:"активных агентов",completed:"выполненные задачи",total:"всего задач",ratio:"охват доказательствами",handoff:"передано агентом",note:"исследовательская заметка",roles:{general_researcher:"Общий исследователь",independent_verifier:"Независимый проверяющий",medical_researcher:"Медицинский исследователь",materials_scientist:"Специалист по материалам"}},
    uk:{label:"ОБМІН ДОСЛІДЖЕННЯМИ В РЕАЛЬНОМУ ЧАСІ",waiting:"Очікування повідомлень агентів",evidence:"результатів із доказами",outputs:"останні результати",pending:"очікують перевірки",active:"активних агентів",completed:"виконані завдання",total:"усього завдань",ratio:"охоплення доказами",handoff:"передано агентом",note:"дослідницька нотатка",roles:{general_researcher:"Загальний дослідник",independent_verifier:"Незалежний перевіряльник",medical_researcher:"Медичний дослідник",materials_scientist:"Фахівець із матеріалів"}},
    ar:{label:"تبادل الأبحاث المباشر",waiting:"بانتظار رسائل الوكلاء",evidence:"نتائج مرفقة بأدلة",outputs:"النتائج الأخيرة",pending:"بانتظار المراجعة",active:"الوكلاء النشطون",completed:"المهام المكتملة",total:"إجمالي المهام",ratio:"تغطية الأدلة",handoff:"مشاركة من",note:"ملاحظة بحثية",roles:{general_researcher:"باحث عام",independent_verifier:"مدقق مستقل",medical_researcher:"باحث طبي",materials_scientist:"عالم مواد"}},
    he:{label:"חילופי מחקר בזמן אמת",waiting:"ממתינים להודעות מהסוכנים",evidence:"תוצאות עם ראיות מצורפות",outputs:"תוצאות אחרונות",pending:"ממתינות לבדיקה",active:"סוכנים פעילים",completed:"משימות שהושלמו",total:"סך המשימות",ratio:"כיסוי ראיות",handoff:"שותף על ידי",note:"הערת מחקר",roles:{general_researcher:"חוקר כללי",independent_verifier:"בודק עצמאי",medical_researcher:"חוקר רפואי",materials_scientist:"מדען חומרים"}},
    ja:{label:"リアルタイム研究共有",waiting:"エージェントのメッセージを待機中",evidence:"証拠が添付された結果",outputs:"最近の結果",pending:"確認待ち",active:"稼働中のエージェント",completed:"完了したタスク",total:"タスク総数",ratio:"証拠の網羅率",handoff:"共有者",note:"研究メモ",roles:{general_researcher:"一般研究員",independent_verifier:"独立検証担当",medical_researcher:"医学研究員",materials_scientist:"材料科学者"}},
    ko:{label:"실시간 연구 교류",waiting:"에이전트 메시지 대기 중",evidence:"근거가 첨부된 결과",outputs:"최근 결과",pending:"검토 대기",active:"활성 에이전트",completed:"완료된 작업",total:"전체 작업",ratio:"근거 범위",handoff:"공유한 에이전트",note:"연구 메모",roles:{general_researcher:"일반 연구원",independent_verifier:"독립 검증자",medical_researcher:"의학 연구원",materials_scientist:"재료 과학자"}},
    zh:{label:"实时研究交流",waiting:"正在等待智能体消息",evidence:"附有证据的结果",outputs:"近期结果",pending:"等待审核",active:"活跃智能体",completed:"已完成任务",total:"任务总数",ratio:"证据覆盖率",handoff:"分享者",note:"研究记录",roles:{general_researcher:"通用研究员",independent_verifier:"独立核查员",medical_researcher:"医学研究员",materials_scientist:"材料科学家"}},
    hi:{label:"लाइव अनुसंधान संवाद",waiting:"एजेंट संदेशों की प्रतीक्षा",evidence:"साक्ष्य वाले परिणाम",outputs:"हाल के परिणाम",pending:"समीक्षा की प्रतीक्षा",active:"सक्रिय एजेंट",completed:"पूर्ण कार्य",total:"कुल कार्य",ratio:"साक्ष्य कवरेज",handoff:"द्वारा साझा",note:"शोध टिप्पणी",roles:{general_researcher:"सामान्य शोधकर्ता",independent_verifier:"स्वतंत्र सत्यापक",medical_researcher:"चिकित्सा शोधकर्ता",materials_scientist:"सामग्री वैज्ञानिक"}}
  };
  const language=()=>String(document.documentElement.lang||"en").toLowerCase().split("-")[0];
  const copy=()=>translations[language()]||translations.en;
  const escapeHTML=value=>String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const role=key=>copy().roles[key]||String(key||"Research agent").replace(/[_-]+/g," ");
  let data=window.SSSWET_LIVE_RESEARCH_DATA||null;
  let rotation=0, timer=null, panel=null, label=null, line=null, caption=null;
  const style=()=>{
    if(document.getElementById("ssswet-equations-style"))return;
    const node=document.createElement("style");node.id="ssswet-equations-style";
    node.textContent=".ssswet-equations{position:absolute;left:50%;bottom:43px;transform:translateX(-50%);z-index:7;width:min(360px,60%);padding:8px 11px;border:1px solid rgba(190,166,119,.28);border-radius:11px;background:rgba(5,7,6,.91);backdrop-filter:blur(8px);overflow:hidden;text-align:center;pointer-events:none}.ssswet-equations-label{font:600 .52rem/1.4 system-ui,sans-serif;letter-spacing:.1em;opacity:.7;margin-bottom:4px}.ssswet-equation{font: .68rem/1.45 system-ui,sans-serif;overflow-wrap:anywhere;min-height:1.4em}.ssswet-equation-main{font-family:Georgia,serif;font-size:.75rem}.ssswet-equation-caption{font-size:.58rem;opacity:.72;margin-top:4px;overflow-wrap:anywhere}@media(max-width:640px){.ssswet-equations{bottom:36px;width:min(310px,70%);padding:6px 8px}.ssswet-equation{font-size:.62rem}}";
    document.head.appendChild(node);
  };
  function typeText(node,text){
    window.clearInterval(timer);
    const value=String(text||"");node.textContent="";let i=0;
    timer=window.setInterval(()=>{node.textContent=value.slice(0,i++);if(i>value.length)window.clearInterval(timer);},17);
  }
  function records(){
    const messages=Array.isArray(data?.agent_messages)?data.agent_messages:[];
    const outputs=Array.isArray(data?.recent_outputs)?data.recent_outputs:[];
    const active=Array.isArray(data?.active_agents)?data.active_agents:[];
    return {messages,outputs,active};
  }
  function render(){
    if(!panel||!data){if(label)label.textContent=copy().label;if(line)line.textContent=copy().waiting;return;}
    const {messages,outputs,active}=records();
    const validMessages=messages.filter(item=>item&&item.content);
    const validOutputs=outputs.filter(item=>item&&item.summary);
    const total=validOutputs.length;
    const withEvidence=validOutputs.filter(item=>Number(item.evidence_count||0)>0).length;
    const ratio=total?Math.round(withEvidence/total*100):0;
    const pending=Number(data.pending_review_outputs||0);
    const selected=validMessages.length?validMessages[rotation%validMessages.length]:null;
    const output=validOutputs.length?validOutputs[rotation%validOutputs.length]:null;
    let shared=copy().waiting;
    if(selected){
      const sender=role(selected.sender_role),recipient=role(selected.recipient_role);
      shared=sender+" → "+recipient+" · "+String(selected.content).slice(0,190);
    }else if(output){
      shared=role(output.role)+" · "+copy().note+" : "+String(output.summary).slice(0,190);
    }
    label.textContent=copy().label;
    typeText(line,shared);
    const equation=withEvidence+" / "+total+" "+copy().evidence+" = "+ratio+"% · "+pending+" "+copy().pending+" · "+active.length+" "+copy().active;
    caption.textContent=equation;
    panel.setAttribute("aria-label",copy().label+". "+shared+". "+equation);
  }
  function mount(){
    style();
    const target=document.querySelector(".bot-command-visual");if(!target)return;
    panel=document.getElementById("ssswet-equations");
    if(!panel){
      panel=document.createElement("section");panel.id="ssswet-equations";panel.className="ssswet-equations";
      panel.innerHTML='<div class="ssswet-equations-label"></div><div class="ssswet-equation ssswet-equation-main" aria-live="polite"></div><div class="ssswet-equation-caption"></div>';
      target.appendChild(panel);
    }
    label=panel.querySelector(".ssswet-equations-label");line=panel.querySelector(".ssswet-equation");caption=panel.querySelector(".ssswet-equation-caption");
    render();
    window.addEventListener("ssswet-bot-data",event=>{data=event.detail||data;rotation=0;render();});
    window.addEventListener("ssswet-language-changed",render);
    document.getElementById("language")?.addEventListener("change",()=>window.setTimeout(render,0));
    window.setInterval(()=>{const {messages,outputs}=records();if(messages.length+outputs.length>1){rotation=(rotation+1)%(messages.length+outputs.length);render();}},8500);
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",mount,{once:true});else mount();
})();