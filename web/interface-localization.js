/* Multilingual labels for the research assessment and journal forms. */
(() => {
  "use strict";
  const language = () => (document.getElementById("language")?.value || document.documentElement.lang || "en").toLowerCase().split("-")[0];
  const keys = {
    priority: ["programme","societal","ecological","maturity","feasibility","resources","safety","reviewer","rationale","refs","save"],
    journal: ["technology","entry","title","summary","classification","state","refs","author","add"]
  };
  const copy = {
    en: { priority:["Research programme","Societal benefit","Ecological and animal benefit","Evidence maturity","Technical feasibility","Resource accessibility","Safety and legal readiness","Reviewer or team","Assessment rationale","Evidence references","Save assessment to local research history"], journal:["Technology","Entry type","Title","Summary","Evidence classification","Progress state","Evidence references","Author label","Add immutable journal entry"] },
    fr: { priority:["Programme de recherche","Bénéfice sociétal","Bénéfice écologique et animal","Maturité des preuves","Faisabilité technique","Accessibilité des ressources","Préparation en matière de sécurité et de légalité","Évaluateur ou équipe","Justification de l’évaluation","Références des preuves","Enregistrer l’évaluation dans l’historique local"], journal:["Technologie","Type d’entrée","Titre","Résumé","Classification des éléments","État d’avancement","Références des preuves","Nom de l’auteur","Ajouter une entrée immuable au journal"] },
    es: { priority:["Programa de investigación","Beneficio social","Beneficio ecológico y animal","Madurez de las pruebas","Viabilidad técnica","Accesibilidad de los recursos","Preparación en seguridad y legalidad","Revisor o equipo","Justificación de la evaluación","Referencias de las pruebas","Guardar evaluación en el historial local"], journal:["Tecnología","Tipo de entrada","Título","Resumen","Clasificación de las pruebas","Estado de progreso","Referencias de las pruebas","Nombre del autor","Añadir una entrada inmutable al diario"] },
    de: { priority:["Forschungsprogramm","Gesellschaftlicher Nutzen","Ökologischer Nutzen und Tierschutz","Reifegrad der Nachweise","Technische Machbarkeit","Verfügbarkeit von Ressourcen","Sicherheits- und Rechtslage","Prüfer oder Team","Begründung der Bewertung","Nachweisreferenzen","Bewertung im lokalen Verlauf speichern"], journal:["Technologie","Eintragstyp","Titel","Zusammenfassung","Nachweisklassifizierung","Fortschrittsstatus","Nachweisreferenzen","Autorenangabe","Unveränderlichen Journaleintrag hinzufügen"] },
    it: { priority:["Programma di ricerca","Beneficio sociale","Beneficio ecologico e animale","Maturità delle prove","Fattibilità tecnica","Accessibilità delle risorse","Preparazione in materia di sicurezza e legalità","Revisore o gruppo","Motivazione della valutazione","Riferimenti delle prove","Salva la valutazione nella cronologia locale"], journal:["Tecnologia","Tipo di voce","Titolo","Riepilogo","Classificazione delle prove","Stato di avanzamento","Riferimenti delle prove","Nome dell’autore","Aggiungi una voce immutabile al diario"] },
    pt: { priority:["Programa de pesquisa","Benefício social","Benefício ecológico e animal","Maturidade das evidências","Viabilidade técnica","Acesso a recursos","Preparação em segurança e legalidade","Revisor ou equipe","Justificativa da avaliação","Referências das evidências","Salvar avaliação no histórico local"], journal:["Tecnologia","Tipo de registro","Título","Resumo","Classificação das evidências","Estado do progresso","Referências das evidências","Nome do autor","Adicionar registro imutável ao diário"] },
    nl: { priority:["Onderzoeksprogramma","Maatschappelijk voordeel","Ecologisch en dierenwelzijnsvoordeel","Bewijsmaturiteit","Technische haalbaarheid","Toegang tot middelen","Veiligheids- en juridische gereedheid","Beoordelaar of team","Onderbouwing van de beoordeling","Bewijsreferenties","Beoordeling opslaan in lokale geschiedenis"], journal:["Technologie","Type invoer","Titel","Samenvatting","Bewijsclassificatie","Voortgangsstatus","Bewijsreferenties","Auteursnaam","Onveranderlijke journaalpost toevoegen"] },
    ru: { priority:["Исследовательская программа","Общественная польза","Экологическая польза и благополучие животных","Зрелость доказательств","Техническая осуществимость","Доступность ресурсов","Готовность в области безопасности и права","Рецензент или команда","Обоснование оценки","Ссылки на доказательства","Сохранить оценку в локальной истории"], journal:["Технология","Тип записи","Название","Краткое описание","Классификация доказательств","Состояние выполнения","Ссылки на доказательства","Имя автора","Добавить неизменяемую запись в журнал"] },
    uk: { priority:["Дослідницька програма","Суспільна користь","Екологічна користь і добробут тварин","Зрілість доказів","Технічна здійсненність","Доступність ресурсів","Готовність щодо безпеки та законності","Рецензент або команда","Обґрунтування оцінки","Посилання на докази","Зберегти оцінку в локальній історії"], journal:["Технологія","Тип запису","Назва","Короткий опис","Класифікація доказів","Стан виконання","Посилання на докази","Ім’я автора","Додати незмінний запис до журналу"] },
    ar: { priority:["برنامج بحثي","منفعة اجتماعية","منفعة بيئية ورعاية الحيوان","نضج الأدلة","الجدوى التقنية","إمكانية الوصول إلى الموارد","الجاهزية للسلامة والامتثال القانوني","المراجع أو الفريق","مبررات التقييم","مراجع الأدلة","حفظ التقييم في السجل المحلي"], journal:["التقنية","نوع الإدخال","العنوان","الملخص","تصنيف الأدلة","حالة التقدم","مراجع الأدلة","اسم المؤلف","إضافة إدخال غير قابل للتعديل إلى السجل"] },
    he: { priority:["תוכנית מחקר","תועלת חברתית","תועלת סביבתית ורווחת בעלי חיים","בשלות הראיות","היתכנות טכנית","נגישות למשאבים","מוכנות בטיחותית ומשפטית","בודק או צוות","נימוק ההערכה","הפניות לראיות","שמירת ההערכה בהיסטוריה המקומית"], journal:["טכנולוגיה","סוג רשומה","כותרת","תקציר","סיווג ראיות","מצב התקדמות","הפניות לראיות","שם המחבר","הוספת רשומה בלתי ניתנת לשינוי ליומן"] },
    ja: { priority:["研究プログラム","社会的利益","環境・動物福祉への利益","証拠の成熟度","技術的実現可能性","資源へのアクセス性","安全性・法令順守の準備状況","評価者またはチーム","評価理由","証拠の参照先","評価をローカル履歴に保存"], journal:["技術","記録の種類","タイトル","概要","証拠の分類","進捗状況","証拠の参照先","作成者名","変更不可の記録を追加"] },
    ko: { priority:["연구 프로그램","사회적 편익","생태 및 동물 복지 편익","증거 성숙도","기술적 실현 가능성","자원 접근성","안전 및 법적 준비 상태","검토자 또는 팀","평가 근거","증거 참조","평가를 로컬 기록에 저장"], journal:["기술","항목 유형","제목","요약","증거 분류","진행 상태","증거 참조","작성자 이름","변경할 수 없는 기록 추가"] },
    zh: { priority:["研究计划","社会效益","生态与动物福利效益","证据成熟度","技术可行性","资源可及性","安全与法律准备情况","评审者或团队","评估理由","证据参考资料","将评估保存到本地历史记录"], journal:["技术","条目类型","标题","摘要","证据分类","进度状态","证据参考资料","作者名称","添加不可更改的日志条目"] },
    hi: { priority:["अनुसंधान कार्यक्रम","सामाजिक लाभ","पारिस्थितिक और पशु कल्याण लाभ","साक्ष्य की परिपक्वता","तकनीकी व्यवहार्यता","संसाधनों तक पहुँच","सुरक्षा और कानूनी तैयारी","समीक्षक या टीम","मूल्यांकन का औचित्य","साक्ष्य संदर्भ","मूल्यांकन को स्थानीय इतिहास में सहेजें"], journal:["प्रौद्योगिकी","प्रविष्टि का प्रकार","शीर्षक","सारांश","साक्ष्य वर्गीकरण","प्रगति स्थिति","साक्ष्य संदर्भ","लेखक का नाम","अपरिवर्तनीय जर्नल प्रविष्टि जोड़ें"] }
  };
  const optionLabels = {
    fr: {"Not assessed":"Non évalué","Planned":"Planifié","In progress":"En cours","Completed":"Terminé","Blocked":"Bloqué","Superseded":"Remplacé","Hypothesis":"Hypothèse","Literature":"Littérature scientifique","Observation":"Observation","Independent review":"Examen indépendant","Project update":"Mise à jour du projet"},
    es: {"Not assessed":"Sin evaluar","Planned":"Planificado","In progress":"En curso","Completed":"Completado","Blocked":"Bloqueado","Superseded":"Sustituido","Hypothesis":"Hipótesis","Literature":"Literatura científica","Observation":"Observación","Independent review":"Revisión independiente","Project update":"Actualización del proyecto"},
    de: {"Not assessed":"Nicht bewertet","Planned":"Geplant","In progress":"In Bearbeitung","Completed":"Abgeschlossen","Blocked":"Blockiert","Superseded":"Ersetzt","Hypothesis":"Hypothese","Literature":"Wissenschaftliche Literatur","Observation":"Beobachtung","Independent review":"Unabhängige Prüfung","Project update":"Projektaktualisierung"},
    it: {"Not assessed":"Non valutato","Planned":"Pianificato","In progress":"In corso","Completed":"Completato","Blocked":"Bloccato","Superseded":"Sostituito","Hypothesis":"Ipotesi","Literature":"Letteratura scientifica","Observation":"Osservazione","Independent review":"Revisione indipendente","Project update":"Aggiornamento del progetto"},
    pt: {"Not assessed":"Não avaliado","Planned":"Planejado","In progress":"Em andamento","Completed":"Concluído","Blocked":"Bloqueado","Superseded":"Substituído","Hypothesis":"Hipótese","Literature":"Literatura científica","Observation":"Observação","Independent review":"Revisão independente","Project update":"Atualização do projeto"},
    nl: {"Not assessed":"Niet beoordeeld","Planned":"Gepland","In progress":"In uitvoering","Completed":"Voltooid","Blocked":"Geblokkeerd","Superseded":"Vervangen","Hypothesis":"Hypothese","Literature":"Wetenschappelijke literatuur","Observation":"Waarneming","Independent review":"Onafhankelijke beoordeling","Project update":"Projectupdate"},
    ru: {"Not assessed":"Не оценено","Planned":"Запланировано","In progress":"В процессе","Completed":"Завершено","Blocked":"Заблокировано","Superseded":"Заменено","Hypothesis":"Гипотеза","Literature":"Научная литература","Observation":"Наблюдение","Independent review":"Независимая проверка","Project update":"Обновление проекта"},
    uk: {"Not assessed":"Не оцінено","Planned":"Заплановано","In progress":"У процесі","Completed":"Завершено","Blocked":"Заблоковано","Superseded":"Замінено","Hypothesis":"Гіпотеза","Literature":"Наукова література","Observation":"Спостереження","Independent review":"Незалежна перевірка","Project update":"Оновлення проєкту"},
    ar: {"Not assessed":"غير مُقيّم","Planned":"مخطط","In progress":"قيد التنفيذ","Completed":"مكتمل","Blocked":"محظور","Superseded":"مستبدل","Hypothesis":"فرضية","Literature":"أدبيات علمية","Observation":"ملاحظة","Independent review":"مراجعة مستقلة","Project update":"تحديث المشروع"},
    he: {"Not assessed":"לא הוערך","Planned":"מתוכנן","In progress":"בתהליך","Completed":"הושלם","Blocked":"חסום","Superseded":"הוחלף","Hypothesis":"השערה","Literature":"ספרות מדעית","Observation":"תצפית","Independent review":"בדיקה עצמאית","Project update":"עדכון פרויקט"},
    ja: {"Not assessed":"未評価","Planned":"計画済み","In progress":"進行中","Completed":"完了","Blocked":"停止","Superseded":"置換済み","Hypothesis":"仮説","Literature":"科学文献","Observation":"観察","Independent review":"独立レビュー","Project update":"プロジェクト更新"},
    ko: {"Not assessed":"평가되지 않음","Planned":"계획됨","In progress":"진행 중","Completed":"완료","Blocked":"차단됨","Superseded":"대체됨","Hypothesis":"가설","Literature":"과학 문헌","Observation":"관찰","Independent review":"독립 검토","Project update":"프로젝트 업데이트"},
    zh: {"Not assessed":"未评估","Planned":"计划中","In progress":"进行中","Completed":"已完成","Blocked":"已阻止","Superseded":"已取代","Hypothesis":"假设","Literature":"科学文献","Observation":"观察","Independent review":"独立审查","Project update":"项目更新"},
    hi: {"Not assessed":"मूल्यांकन नहीं हुआ","Planned":"नियोजित","In progress":"प्रगति पर","Completed":"पूर्ण","Blocked":"अवरुद्ध","Superseded":"प्रतिस्थापित","Hypothesis":"परिकल्पना","Literature":"वैज्ञानिक साहित्य","Observation":"अवलोकन","Independent review":"स्वतंत्र समीक्षा","Project update":"परियोजना अपडेट"}
  };
  function setLabel(form, name, value) {
    const label = form.querySelector('[name="' + name + '"]')?.closest("label");
    if (!label) return;
    const node = [...label.childNodes].find(item => item.nodeType === Node.TEXT_NODE && item.textContent.trim());
    if (node && node.textContent.trim() !== value) node.textContent = value + " ";
  }
  function apply() {
    const code = language();
    const words = copy[code] || copy.en;
    const priority = document.getElementById("priority-assessment-form");
    if (priority) {
      const names = ["programme_id","societal_benefit","ecological_benefit","evidence_maturity","technical_feasibility","resource_accessibility","safety_legal_readiness","reviewer_label","rationale","evidence_refs"];
      names.forEach((name,index) => setLabel(priority,name,words.priority[index]));
      const submit = priority.querySelector('button[type="submit"]');
      if (submit && submit.textContent !== words.priority[10]) submit.textContent = words.priority[10];
      const note = priority.querySelector(".priority-assessment-note");
      if (note && code === "fr") { const value = "Chaque envoi crée une entrée permanente dans l’historique. Les critères sans note restent non évalués. Cet outil n’autorise ni financement, ni expérience, ni produit."; if (note.textContent !== value) note.textContent = value; }
      const placeholders = {
        en:["e.g. SSSWET research team","Explain the judgement and note uncertainties.","One URL or reference per line (optional)"],
        fr:["ex. : équipe de recherche SSSWET","Expliquez le jugement et signalez les incertitudes.","Une URL ou une référence par ligne (facultatif)"]
      }[code];
      if (placeholders) ["reviewer_label","rationale","evidence_refs"].forEach((name,i)=>{const el=priority.querySelector('[name="'+name+'"]');if(el)el.placeholder=placeholders[i];});
    }
    const journal = document.getElementById("research-journal-form");
    if (journal) {
      ["technology","event_type","title","summary","classification","state","evidence_refs","author_label"].forEach((name,index)=>setLabel(journal,name,words.journal[index]));
      const submit = journal.querySelector('button[type="submit"]');
      if (submit && submit.textContent !== words.journal[8]) submit.textContent = words.journal[8];
      const note = journal.querySelector(".research-journal-note");
      if (note && code === "fr") { const value = "La saisie est limitée à la machine locale. Les entrées ne peuvent être ni modifiées ni supprimées. Une chaîne de hachage détecte les modifications ultérieures, sans établir la validité scientifique."; if (note.textContent !== value) note.textContent = value; }
    }
    const filters = document.getElementById("research-journal-filter");
    const options = optionLabels[code] || {};
    [priority,journal,filters].filter(Boolean).forEach(root=>root.querySelectorAll("option").forEach(option=>{const translated=options[option.textContent.trim()];if(translated)option.textContent=translated;}));
    const summary = document.querySelector(".priority-assessment-editor > summary");
    if (summary) { const value = code === "fr" ? "Enregistrer ou actualiser une évaluation" : "Record or update an assessment"; if (summary.textContent !== value) summary.textContent = value; }
    const heading = document.querySelector("#research-journal-form h4");
    if (heading) { const value = code === "fr" ? "Enregistrer une mise à jour du projet" : "Record a project update"; if (heading.textContent !== value) heading.textContent = value; }
    document.documentElement.dataset.interfaceLanguage = code;
  }
  document.addEventListener("DOMContentLoaded",apply,{once:true});
  document.getElementById("language")?.addEventListener("change",apply);
  window.addEventListener("ssswet-language-changed",apply);
  const observer = new MutationObserver(()=>apply());
  const start=()=>{if(document.body)observer.observe(document.body,{childList:true,subtree:true});apply();};
  if(document.body)start();else document.addEventListener("DOMContentLoaded",start,{once:true});
})();
