(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const stage = $("bot-visual-agents");
  const feed = $("bot-conversation-feed");
  if (!stage || !feed) return;

  const copy = {
    en: {
      stageActive:"Live agent activity",stageRecent:"Recently active agents",stageEmpty:"Waiting for the first agent report",
      channel:"BOT-ONLY CHANNEL",title:"Research exchange",caption:"Recorded research outputs from the local engine — not scripted dialogue",
      voiceOn:"Voice · On",voiceOff:"Voice · Off",questions:"Ask the research team",
      qWorking:"What are you working on?",qDiscoveries:"What did you discover?",qVerification:"How are results checked?",
      empty:"No research output has been recorded yet. The room will fill as the local engine completes work.",
      provisional:"Provisional output · independent review required",evidence:"evidence items",noEvidence:"No evidence items attached",
      answerWorking:"The engine is currently processing {topic}. {active} agent(s) are reported active. {done} tasks are recorded as complete; {pending} outputs remain pending review.",
      answerDiscoveries:"Most recent recorded research output: {summary} This is a provisional research note, not a verified scientific discovery.",
      answerNone:"No research output has been recorded yet. The engine has not published a new result.",
      answerVerification:"Research outputs remain unverified until their sources, methods and reasoning receive independent review. The dashboard currently reports {pending} outputs awaiting review. No percentage can establish absolute certainty.",
      role:"Research agent",talking:"Processing",notActive:"Recent contribution",voiceUnavailable:"Speech synthesis is unavailable in this browser."
    },
    fr: {
      stageActive:"Activité des agents en direct",stageRecent:"Agents récemment intervenus",stageEmpty:"En attente du premier rapport des agents",
      channel:"CANAL RÉSERVÉ AUX BOTS",title:"Échanges de recherche",caption:"Résultats réellement enregistrés par le moteur local — pas de dialogue scénarisé",
      voiceOn:"Voix · Activée",voiceOff:"Voix · Désactivée",questions:"Interroger l’équipe de recherche",
      qWorking:"Sur quoi travaillez-vous ?",qDiscoveries:"Qu’avez-vous découvert ?",qVerification:"Comment vérifiez-vous les résultats ?",
      empty:"Aucun résultat de recherche n’a encore été enregistré. Les échanges apparaîtront au fur et à mesure des travaux du moteur local.",
      provisional:"Résultat provisoire · vérification indépendante requise",evidence:"éléments de preuve",noEvidence:"Aucun élément de preuve joint",
      answerWorking:"Le moteur traite actuellement le programme « {topic} ». {active} agent(s) sont signalés actifs. {done} tâches sont enregistrées comme terminées ; {pending} résultats restent à examiner.",
      answerDiscoveries:"Dernier résultat de recherche enregistré : {summary} Il s’agit d’une note de recherche provisoire, et non d’une découverte scientifique vérifiée.",
      answerNone:"Aucun résultat de recherche n’a encore été enregistré. Le moteur n’a pas publié de nouveau résultat.",
      answerVerification:"Les résultats restent non vérifiés tant que leurs sources, méthodes et raisonnements n’ont pas fait l’objet d’un examen indépendant. Le tableau de bord indique actuellement {pending} résultats en attente d’examen. Aucun pourcentage ne peut établir une certitude absolue.",
      role:"Agent de recherche",talking:"En cours de traitement",notActive:"Contribution récente",voiceUnavailable:"La synthèse vocale n’est pas disponible dans ce navigateur."
    },
    es: {
      stageActive:"Actividad de agentes en directo",stageRecent:"Agentes activos recientemente",stageEmpty:"Esperando el primer informe de los agentes",
      channel:"CANAL SOLO PARA BOTS",title:"Intercambio de investigación",caption:"Resultados registrados por el motor local, no diálogos guionizados",
      voiceOn:"Voz · Activada",voiceOff:"Voz · Desactivada",questions:"Preguntar al equipo de investigación",
      qWorking:"¿En qué están trabajando?",qDiscoveries:"¿Qué han descubierto?",qVerification:"¿Cómo verifican los resultados?",
      empty:"Aún no se han registrado resultados de investigación.",provisional:"Resultado provisional · requiere revisión independiente",evidence:"elementos de evidencia",noEvidence:"Sin elementos de evidencia adjuntos",
      answerWorking:"El motor procesa actualmente {topic}. Hay {active} agente(s) activos. {done} tareas completadas y {pending} resultados pendientes de revisión.",
      answerDiscoveries:"Último resultado registrado: {summary} Es una nota provisional, no un descubrimiento científico verificado.",
      answerNone:"Todavía no se ha registrado ningún resultado nuevo.",
      answerVerification:"Los resultados requieren una revisión independiente de sus fuentes, métodos y razonamiento. Hay {pending} resultados pendientes de revisión. Ningún porcentaje demuestra certeza absoluta.",
      role:"Agente de investigación",talking:"Procesando",notActive:"Contribución reciente",voiceUnavailable:"La síntesis de voz no está disponible."
    },
    de: {
      stageActive:"Live-Aktivität der Agenten",stageRecent:"Kürzlich aktive Agenten",stageEmpty:"Warte auf den ersten Agentenbericht",
      channel:"NUR FÜR BOTS",title:"Forschungsaustausch",caption:"Aufgezeichnete Ergebnisse der lokalen Engine, kein geskripteter Dialog",
      voiceOn:"Stimme · Ein",voiceOff:"Stimme · Aus",questions:"Forschungsteam fragen",
      qWorking:"Woran arbeitet ihr?",qDiscoveries:"Was habt ihr entdeckt?",qVerification:"Wie werden Ergebnisse geprüft?",
      empty:"Noch wurden keine Forschungsergebnisse aufgezeichnet.",provisional:"Vorläufiges Ergebnis · unabhängige Prüfung erforderlich",evidence:"Belege",noEvidence:"Keine Belege angehängt",
      answerWorking:"Die Engine bearbeitet derzeit {topic}. {active} Agent(en) sind aktiv. {done} Aufgaben sind abgeschlossen; {pending} Ergebnisse warten auf Prüfung.",
      answerDiscoveries:"Letztes aufgezeichnetes Ergebnis: {summary} Dies ist eine vorläufige Forschungsnotiz, keine bestätigte wissenschaftliche Entdeckung.",
      answerNone:"Es wurde noch kein neues Forschungsergebnis aufgezeichnet.",
      answerVerification:"Quellen, Methoden und Argumentation müssen unabhängig geprüft werden. {pending} Ergebnisse warten auf Prüfung. Absolute Gewissheit lässt sich nicht durch Prozentwerte belegen.",
      role:"Forschungsagent",talking:"In Bearbeitung",notActive:"Letzter Beitrag",voiceUnavailable:"Sprachausgabe ist in diesem Browser nicht verfügbar."
    },
    it: {
      stageActive:"Attività degli agenti in diretta",stageRecent:"Agenti attivi di recente",stageEmpty:"In attesa del primo rapporto degli agenti",
      channel:"CANALE SOLO BOT",title:"Scambio di ricerca",caption:"Risultati registrati dal motore locale, non dialoghi preimpostati",
      voiceOn:"Voce · Attiva",voiceOff:"Voce · Disattivata",questions:"Chiedi al gruppo di ricerca",
      qWorking:"A cosa state lavorando?",qDiscoveries:"Cosa avete scoperto?",qVerification:"Come verificate i risultati?",
      empty:"Non è ancora stato registrato alcun risultato di ricerca.",provisional:"Risultato provvisorio · revisione indipendente necessaria",evidence:"elementi di prova",noEvidence:"Nessuna prova allegata",
      answerWorking:"Il motore sta elaborando {topic}. {active} agente/i attivo/i. {done} attività completate; {pending} risultati in attesa di revisione.",
      answerDiscoveries:"Ultimo risultato registrato: {summary} È una nota provvisoria, non una scoperta scientifica verificata.",
      answerNone:"Non è ancora stato registrato alcun nuovo risultato.",
      answerVerification:"Fonti, metodi e ragionamento richiedono una revisione indipendente. {pending} risultati sono in attesa di revisione. Nessuna percentuale dimostra una certezza assoluta.",
      role:"Agente di ricerca",talking:"In elaborazione",notActive:"Contributo recente",voiceUnavailable:"La sintesi vocale non è disponibile."
    },
    pt: {
      stageActive:"Atividade dos agentes em direto",stageRecent:"Agentes ativos recentemente",stageEmpty:"À espera do primeiro relatório dos agentes",
      channel:"CANAL APENAS PARA BOTS",title:"Intercâmbio de investigação",caption:"Resultados registados pelo motor local, não diálogos encenados",
      voiceOn:"Voz · Ligada",voiceOff:"Voz · Desligada",questions:"Perguntar à equipa de investigação",
      qWorking:"Em que estão a trabalhar?",qDiscoveries:"O que descobriram?",qVerification:"Como verificam os resultados?",
      empty:"Ainda não foi registado qualquer resultado de investigação.",provisional:"Resultado provisório · revisão independente necessária",evidence:"elementos de prova",noEvidence:"Sem provas anexadas",
      answerWorking:"O motor está a processar {topic}. {active} agente(s) ativo(s). {done} tarefas concluídas; {pending} resultados aguardam revisão.",
      answerDiscoveries:"Último resultado registado: {summary} É uma nota provisória, não uma descoberta científica verificada.",
      answerNone:"Ainda não foi registado nenhum resultado novo.",
      answerVerification:"As fontes, métodos e raciocínio exigem revisão independente. {pending} resultados aguardam revisão. Nenhuma percentagem prova certeza absoluta.",
      role:"Agente de investigação",talking:"A processar",notActive:"Contributo recente",voiceUnavailable:"A síntese de voz não está disponível."
    },
    nl: {
      stageActive:"Live activiteit van agents",stageRecent:"Recent actieve agents",stageEmpty:"Wachten op het eerste agentrapport",
      channel:"ALLEEN VOOR BOTS",title:"Onderzoeksuitwisseling",caption:"Geregistreerde resultaten van de lokale engine, geen gescript gesprek",
      voiceOn:"Stem · Aan",voiceOff:"Stem · Uit",questions:"Vraag het onderzoeksteam",
      qWorking:"Waar werken jullie aan?",qDiscoveries:"Wat hebben jullie ontdekt?",qVerification:"Hoe worden resultaten gecontroleerd?",
      empty:"Er zijn nog geen onderzoeksresultaten vastgelegd.",provisional:"Voorlopig resultaat · onafhankelijke beoordeling vereist",evidence:"bewijsitems",noEvidence:"Geen bewijsitems gekoppeld",
      answerWorking:"De engine verwerkt {topic}. {active} agent(en) zijn actief. {done} taken zijn voltooid; {pending} resultaten wachten op beoordeling.",
      answerDiscoveries:"Laatst vastgelegde onderzoeksresultaat: {summary} Dit is een voorlopige notitie, geen geverifieerde wetenschappelijke ontdekking.",
      answerNone:"Er is nog geen nieuw onderzoeksresultaat vastgelegd.",
      answerVerification:"Bronnen, methoden en redeneringen vereisen onafhankelijke beoordeling. {pending} resultaten wachten op beoordeling. Geen percentage bewijst absolute zekerheid.",
      role:"Onderzoeksagent",talking:"Bezig",notActive:"Recente bijdrage",voiceUnavailable:"Spraaksynthese is niet beschikbaar."
    },
    ru: {
      stageActive:"Текущая активность агентов",stageRecent:"Недавно работавшие агенты",stageEmpty:"Ожидание первого отчёта агентов",
      channel:"КАНАЛ ТОЛЬКО ДЛЯ БОТОВ",title:"Обмен исследовательскими результатами",caption:"Записанные результаты локального движка, а не постановочный диалог",
      voiceOn:"Голос · Вкл.",voiceOff:"Голос · Выкл.",questions:"Задать вопрос исследовательской группе",
      qWorking:"Над чем вы работаете?",qDiscoveries:"Что удалось обнаружить?",qVerification:"Как проверяются результаты?",
      empty:"Результаты исследований ещё не записаны.",provisional:"Предварительный результат · требуется независимая проверка",evidence:"доказательств",noEvidence:"Доказательства не приложены",
      answerWorking:"Движок обрабатывает программу {topic}. Активных агентов: {active}. Завершено задач: {done}; результатов ожидают проверки: {pending}.",
      answerDiscoveries:"Последний записанный результат: {summary} Это предварительная исследовательская заметка, а не подтверждённое научное открытие.",
      answerNone:"Новый результат пока не записан.",
      answerVerification:"Источники, методы и выводы требуют независимой проверки. Ожидают проверки результатов: {pending}. Процент не доказывает абсолютную достоверность.",
      role:"Исследовательский агент",talking:"Выполняется",notActive:"Последний вклад",voiceUnavailable:"Синтез речи недоступен."
    },
    uk: {
      stageActive:"Поточна активність агентів",stageRecent:"Нещодавно активні агенти",stageEmpty:"Очікування першого звіту агентів",
      channel:"КАНАЛ ЛИШЕ ДЛЯ БОТІВ",title:"Обмін дослідженнями",caption:"Записані результати локального рушія, а не сценарний діалог",
      voiceOn:"Голос · Увімк.",voiceOff:"Голос · Вимк.",questions:"Запитати дослідницьку команду",
      qWorking:"Над чим ви працюєте?",qDiscoveries:"Що ви виявили?",qVerification:"Як перевіряються результати?",
      empty:"Результатів досліджень ще не записано.",provisional:"Попередній результат · потрібна незалежна перевірка",evidence:"доказів",noEvidence:"Докази не додано",
      answerWorking:"Рушій обробляє програму {topic}. Активних агентів: {active}. Завершено завдань: {done}; результатів очікують перевірки: {pending}.",
      answerDiscoveries:"Останній записаний результат: {summary} Це попередня дослідницька нотатка, а не підтверджене наукове відкриття.",
      answerNone:"Новий результат ще не записано.",
      answerVerification:"Джерела, методи та міркування потребують незалежної перевірки. Очікують перевірки результатів: {pending}. Відсоток не доводить абсолютної достовірності.",
      role:"Дослідницький агент",talking:"Обробка",notActive:"Нещодавній внесок",voiceUnavailable:"Синтез мовлення недоступний."
    },
    ar: {
      stageActive:"نشاط الوكلاء المباشر",stageRecent:"الوكلاء النشطون مؤخرًا",stageEmpty:"بانتظار أول تقرير من الوكلاء",
      channel:"قناة مخصصة للروبوتات",title:"تبادل الأبحاث",caption:"نتائج مسجلة من المحرك المحلي وليست محادثة مكتوبة مسبقًا",
      voiceOn:"الصوت · تشغيل",voiceOff:"الصوت · إيقاف",questions:"اسأل فريق البحث",
      qWorking:"على ماذا تعملون؟",qDiscoveries:"ماذا اكتشفتم؟",qVerification:"كيف تتحققون من النتائج؟",
      empty:"لم تُسجّل نتائج بحثية بعد.",provisional:"نتيجة أولية · تتطلب مراجعة مستقلة",evidence:"عناصر أدلة",noEvidence:"لا توجد أدلة مرفقة",
      answerWorking:"يعالج المحرك حاليًا {topic}. عدد الوكلاء النشطين {active}. المهام المكتملة {done} والنتائج قيد المراجعة {pending}.",
      answerDiscoveries:"أحدث نتيجة مسجلة: {summary} هذه ملاحظة بحثية أولية وليست اكتشافًا علميًا موثقًا.",
      answerNone:"لم تُسجّل نتيجة جديدة بعد.",
      answerVerification:"تتطلب المصادر والأساليب والاستدلال مراجعة مستقلة. هناك {pending} نتيجة بانتظار المراجعة. لا تثبت النسبة المئوية اليقين المطلق.",
      role:"وكيل بحث",talking:"قيد المعالجة",notActive:"مساهمة حديثة",voiceUnavailable:"تحويل النص إلى كلام غير متاح."
    },
    he: {
      stageActive:"פעילות סוכנים בזמן אמת",stageRecent:"סוכנים שפעלו לאחרונה",stageEmpty:"ממתינים לדוח הסוכנים הראשון",
      channel:"ערוץ לבוטים בלבד",title:"חילופי מחקר",caption:"תוצאות מחקר שנרשמו במנוע המקומי, לא שיחה מתוסרטת",
      voiceOn:"קול · מופעל",voiceOff:"קול · כבוי",questions:"שאלו את צוות המחקר",
      qWorking:"על מה אתם עובדים?",qDiscoveries:"מה גיליתם?",qVerification:"כיצד בודקים תוצאות?",
      empty:"עדיין לא נרשמו תוצאות מחקר.",provisional:"תוצאה ראשונית · נדרשת בדיקה עצמאית",evidence:"פריטי ראיות",noEvidence:"לא צורפו ראיות",
      answerWorking:"המנוע מעבד כעת את {topic}. {active} סוכנים פעילים. {done} משימות הושלמו; {pending} תוצאות ממתינות לבדיקה.",
      answerDiscoveries:"תוצאת המחקר האחרונה שנרשמה: {summary} זוהי הערת מחקר ראשונית, לא תגלית מדעית מאומתת.",
      answerNone:"עדיין לא נרשמה תוצאה חדשה.",
      answerVerification:"המקורות, השיטות והנימוקים דורשים בדיקה עצמאית. {pending} תוצאות ממתינות לבדיקה. אחוזים אינם מוכיחים ודאות מוחלטת.",
      role:"סוכן מחקר",talking:"בעיבוד",notActive:"תרומה אחרונה",voiceUnavailable:"הקראת טקסט אינה זמינה בדפדפן זה."
    },
    ja: {
      stageActive:"エージェントのライブ活動",stageRecent:"最近活動したエージェント",stageEmpty:"最初のエージェント報告を待機中",
      channel:"ボット専用チャンネル",title:"研究情報の共有",caption:"ローカルエンジンに記録された研究結果。台本による会話ではありません",
      voiceOn:"音声 · オン",voiceOff:"音声 · オフ",questions:"研究チームに質問",
      qWorking:"何に取り組んでいますか？",qDiscoveries:"何を発見しましたか？",qVerification:"結果はどのように検証しますか？",
      empty:"研究結果はまだ記録されていません。",provisional:"暫定結果 · 独立した検証が必要",evidence:"証拠項目",noEvidence:"証拠は添付されていません",
      answerWorking:"エンジンは現在 {topic} を処理中です。稼働中のエージェントは {active}、完了タスクは {done}、確認待ちの結果は {pending} 件です。",
      answerDiscoveries:"最新の記録結果：{summary} これは暫定的な研究メモであり、検証済みの科学的発見ではありません。",
      answerNone:"新しい結果はまだ記録されていません。",
      answerVerification:"情報源、方法、推論には独立した審査が必要です。{pending} 件の結果が審査待ちです。割合で絶対的な確実性を証明することはできません。",
      role:"研究エージェント",talking:"処理中",notActive:"最近の貢献",voiceUnavailable:"このブラウザーでは音声合成を利用できません。"
    },
    ko: {
      stageActive:"실시간 에이전트 활동",stageRecent:"최근 활동한 에이전트",stageEmpty:"첫 에이전트 보고 대기 중",
      channel:"봇 전용 채널",title:"연구 결과 교류",caption:"로컬 엔진에 기록된 연구 결과이며 대본으로 만든 대화가 아닙니다",
      voiceOn:"음성 · 켜짐",voiceOff:"음성 · 꺼짐",questions:"연구팀에 질문하기",
      qWorking:"무엇을 연구하고 있나요?",qDiscoveries:"무엇을 발견했나요?",qVerification:"결과를 어떻게 검증하나요?",
      empty:"아직 기록된 연구 결과가 없습니다.",provisional:"잠정 결과 · 독립 검토 필요",evidence:"증거 항목",noEvidence:"첨부된 증거 없음",
      answerWorking:"엔진은 현재 {topic}을 처리하고 있습니다. 활성 에이전트 {active}명, 완료된 작업 {done}개, 검토 대기 결과 {pending}개입니다.",
      answerDiscoveries:"가장 최근에 기록된 결과: {summary} 이는 잠정 연구 메모이며 검증된 과학적 발견이 아닙니다.",
      answerNone:"아직 새로운 결과가 기록되지 않았습니다.",
      answerVerification:"출처, 방법 및 추론은 독립적인 검토가 필요합니다. {pending}개 결과가 검토 대기 중입니다. 백분율로 절대적 확실성을 증명할 수 없습니다.",
      role:"연구 에이전트",talking:"처리 중",notActive:"최근 기여",voiceUnavailable:"이 브라우저에서는 음성 합성을 사용할 수 없습니다."
    },
    zh: {
      stageActive:"智能体实时活动",stageRecent:"近期活动的智能体",stageEmpty:"等待智能体的第一份报告",
      channel:"仅限机器人频道",title:"研究交流",caption:"本地引擎记录的研究成果，并非编排的对话",
      voiceOn:"语音 · 开启",voiceOff:"语音 · 关闭",questions:"向研究团队提问",
      qWorking:"你们正在研究什么？",qDiscoveries:"你们发现了什么？",qVerification:"如何核查结果？",
      empty:"尚未记录研究成果。",provisional:"初步结果 · 需要独立审查",evidence:"证据项",noEvidence:"未附证据",
      answerWorking:"引擎目前正在处理 {topic}。活跃智能体：{active}；已完成任务：{done}；待审查结果：{pending}。",
      answerDiscoveries:"最近记录的研究结果：{summary} 这是初步研究记录，并非经过验证的科学发现。",
      answerNone:"尚未记录新的研究结果。",
      answerVerification:"来源、方法和推理都需要独立审查。目前有 {pending} 项结果等待审查。百分比无法证明绝对确定性。",
      role:"研究智能体",talking:"处理中",notActive:"近期贡献",voiceUnavailable:"此浏览器不支持语音合成。"
    },
    hi: {
      stageActive:"एजेंटों की लाइव गतिविधि",stageRecent:"हाल में सक्रिय एजेंट",stageEmpty:"एजेंटों की पहली रिपोर्ट की प्रतीक्षा",
      channel:"केवल बॉट चैनल",title:"अनुसंधान आदान-प्रदान",caption:"स्थानीय इंजन में दर्ज परिणाम, कोई लिखित काल्पनिक संवाद नहीं",
      voiceOn:"आवाज़ · चालू",voiceOff:"आवाज़ · बंद",questions:"अनुसंधान टीम से पूछें",
      qWorking:"आप किस पर काम कर रहे हैं?",qDiscoveries:"आपने क्या खोजा?",qVerification:"परिणामों की जाँच कैसे होती है?",
      empty:"अभी तक कोई अनुसंधान परिणाम दर्ज नहीं हुआ है।",provisional:"अस्थायी परिणाम · स्वतंत्र समीक्षा आवश्यक",evidence:"साक्ष्य",noEvidence:"कोई साक्ष्य संलग्न नहीं",
      answerWorking:"इंजन अभी {topic} पर काम कर रहा है। सक्रिय एजेंट {active}, पूर्ण कार्य {done}, समीक्षा की प्रतीक्षा में परिणाम {pending} हैं।",
      answerDiscoveries:"हाल में दर्ज परिणाम: {summary} यह प्रारंभिक शोध टिप्पणी है, सत्यापित वैज्ञानिक खोज नहीं।",
      answerNone:"अभी कोई नया परिणाम दर्ज नहीं हुआ है।",
      answerVerification:"स्रोतों, विधियों और तर्क की स्वतंत्र समीक्षा आवश्यक है। {pending} परिणाम समीक्षा की प्रतीक्षा में हैं। कोई प्रतिशत पूर्ण निश्चितता सिद्ध नहीं करता।",
      role:"अनुसंधान एजेंट",talking:"प्रक्रिया जारी",notActive:"हाल का योगदान",voiceUnavailable:"इस ब्राउज़र में वाक् संश्लेषण उपलब्ध नहीं है।"
    }
  };

  const lang = () => (document.documentElement.lang || "en").toLowerCase().split("-")[0];
  const t = () => copy[lang()] || copy.en;
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const pretty = (value) => String(value || "—").replace(/([a-z])([A-Z])/g,"$1 $2").replace(/[_-]+/g," ");
  const format = (s, values) => s.replace(/\{(\w+)\}/g, (_, k) => String(values[k] ?? ""));
  const roleLabels = {
    general_researcher:{fr:"Chercheur généraliste",en:"General researcher"},
    independent_verifier:{fr:"Vérificateur indépendant",en:"Independent verifier"},
    medical_researcher:{fr:"Chercheur en médecine",en:"Medical researcher"},
    materials_scientist:{fr:"Spécialiste des matériaux",en:"Materials scientist"}
  };
  const roleName = (role) => roleLabels[role]?.[lang()] || roleLabels[role]?.en || pretty(role || t().role);
  const avatar = (index) => '<span class="agent-avatar agent-avatar-'+((index%3)+1)+'"><span class="agent-robot-head"><i></i><i></i></span><span class="agent-robot-body"></span></span>';
  const time = (value) => { const d=new Date(value); return value && !Number.isNaN(d.getTime()) ? d.toLocaleTimeString(lang(),{hour:"2-digit",minute:"2-digit"}) : ""; };
  let voiceEnabled = false;
  let initialized = false;
  let knownOutputIds = new Set();
  let currentData = null;
  let requestBusy = false;

  function renderStage(data) {
    const active = Array.isArray(data.active_agents) ? data.active_agents : [];
    const recent = Array.isArray(data.recent_agents) ? data.recent_agents : [];
    const source = active.length ? active : recent;
    const unique = [];
    const seen = new Set();
    source.forEach(agent => {
      const key = agent.id || agent.agent_id;
      if (!key || seen.has(key)) return;
      seen.add(key); unique.push(agent);
    });
    const selected = unique.slice(0, 8);
    const isActive = active.length > 0;
    $("bot-command-visual").dataset.active = isActive ? "true" : "false";
    $("bot-stage-caption").textContent = selected.length
      ? (isActive ? t().stageActive : t().stageRecent)
      : t().stageEmpty;
    const width = stage.clientWidth || 700;
    const height = stage.clientHeight || 400;
    const rx = Math.min(width * .39, 330);
    const ry = Math.min(height * .34, 165);
    stage.innerHTML = selected.map((agent,index) => {
      const angle = (-Math.PI/2) + (Math.PI*2*index/selected.length);
      const x = 50 + (Math.cos(angle)*rx/width*100);
      const y = 50 + (Math.sin(angle)*ry/height*100);
      const role = roleName(agent.role);
      const activeClass = isActive ? "is-active" : (String(agent.role||"").includes("verif") ? "is-review" : "");
      const id = agent.id || agent.agent_id;
      return '<div class="bot-stage-agent '+activeClass+'" style="--x:'+x.toFixed(2)+'%;--y:'+y.toFixed(2)+'%;--delay:'+(-index*.43)+'s;--float-duration:'+(4.2+(index%4)*.7)+'s"><div class="bot-stage-agent-content">'+avatar(index)+'<strong>'+esc(role)+'</strong><small>'+esc(id)+'</small></div></div>';
    }).join("");
  }

  function renderFeed(data, speakNew) {
    const handoffs = Array.isArray(data.agent_messages) ? data.agent_messages : [];
    const outputs = Array.isArray(data.recent_outputs) ? data.recent_outputs : [];
    const valid = outputs.filter(item => item.summary && String(item.summary).trim());
    const latestIds = new Set(valid.map(item => [item.task_id,item.agent_id,item.created_at].join("|")));
    const fresh = valid.filter(item => !knownOutputIds.has([item.task_id,item.agent_id,item.created_at].join("|")));
    if (!initialized) {
      knownOutputIds = latestIds;
      initialized = true;
    } else {
      fresh.forEach(item => knownOutputIds.add([item.task_id,item.agent_id,item.created_at].join("|")));
    }
    const activeCount = Array.isArray(data.active_agents) ? data.active_agents.length : 0;
    const thinking = {
      en:"Research agents are working",fr:"Les agents travaillent en ce moment",es:"Los agentes están trabajando",
      de:"Die Forschungsagenten arbeiten",it:"Gli agenti stanno lavorando",pt:"Os agentes estão a trabalhar",
      nl:"Onderzoeksagenten zijn aan het werk",ru:"Исследовательские агенты работают",uk:"Дослідницькі агенти працюють",
      ar:"وكلاء البحث يعملون الآن",he:"סוכני המחקר עובדים כעת",ja:"研究エージェントが作業中です",
      ko:"연구 에이전트가 작업 중입니다",zh:"研究智能体正在工作",hi:"अनुसंधान एजेंट काम कर रहे हैं"
    }[lang()] || "Research agents are working";
    const handoffCards = handoffs.slice(0,8).map((item,index) => {
      const heading = esc(roleName(item.sender_role))+' → '+esc(roleName(item.recipient_role));
      const state = item.review_state === "awaiting_review" ? (lang()==="fr"?"transmis · en attente d’examen":"shared · awaiting review") : esc(item.review_state);
      return '<article class="bot-conversation-message bot-handoff-message"><div class="message-avatar" aria-hidden="true">↗</div><div><strong>'+heading+'</strong><p>'+esc(item.content)+'</p><small>'+esc(item.message_type.replaceAll("_"," "))+' · '+esc(state)+' · '+esc(time(item.created_at))+'</small></div></article>';
    });
    const messages = handoffCards.concat(valid.slice(0,10).map((item,index) => {
      const count = Number(item.evidence_count || 0);
      const detail = count ? count+' '+t().evidence : t().noEvidence;
      return '<article class="bot-conversation-message"><div class="message-avatar" aria-hidden="true">'+(index+1)+'</div><div><strong>'+esc(roleName(item.role))+' · '+esc(item.agent_id || t().role)+'</strong><p>'+esc(item.summary)+'</p><small>'+esc(t().provisional)+' · '+esc(detail)+' · '+esc(time(item.created_at))+'</small></div></article>';
    }));
    if (!valid.length && !handoffCards.length) messages.push('<p class="bot-conversation-empty">'+esc(t().empty)+'</p>');
    if (activeCount) messages.push('<div class="bot-thinking" style="--agent-count:'+Math.max(1,activeCount)+'"><span>'+esc(thinking)+' · '+activeCount+'</span><i></i><i></i><i></i></div>');
    feed.innerHTML = messages.join("");
    if (speakNew && voiceEnabled && fresh.length) speak(fresh[fresh.length-1].summary);
  }

  function speak(message) {
    if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) {
      const answer=$("bot-visitor-answer"); answer.hidden=false; answer.textContent=t().voiceUnavailable; return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(String(message).slice(0,1200));
    utterance.lang = document.documentElement.lang || "en";
    utterance.rate = 1.02;
    window.speechSynthesis.speak(utterance);
  }

  function renderLabels() {
    const c=t();
    $("bot-conversation-kicker").textContent=c.channel;
    $("bot-conversation-title").textContent=c.title;
    $("bot-conversation-caption").textContent=c.caption;
    $("bot-questions-label").textContent=c.questions;
    $("bot-voice-toggle").textContent=voiceEnabled?c.voiceOn:c.voiceOff;
    $("bot-voice-toggle").setAttribute("aria-pressed",voiceEnabled?"true":"false");
    const buttons = [...document.querySelectorAll("[data-bot-question]")];
    buttons.forEach(button => {
      const key=button.dataset.botQuestion;
      button.textContent=key==="working"?c.qWorking:key==="discoveries"?c.qDiscoveries:c.qVerification;
    });
  }

  function answerQuestion(kind) {
    const data=currentData || {};
    const worker=data.worker || {};
    const outputs=Array.isArray(data.recent_outputs)?data.recent_outputs:[];
    const latest=outputs.find(item=>item.summary && String(item.summary).trim());
    const values={
      topic: pretty(worker.current_objective || worker.current_technology || "—"),
      active:(data.active_agents||[]).length,
      done:data.completed_tasks||0,
      pending:data.pending_review_outputs||0,
      summary:latest ? latest.summary : t().answerNone
    };
    let answer=kind==="working"
      ? format(t().answerWorking,values)
      : kind==="discoveries"
        ? (latest?format(t().answerDiscoveries,values):t().answerNone)
        : format(t().answerVerification,values);
    const node=$("bot-visitor-answer");
    node.hidden=false; node.textContent=answer;
    if(voiceEnabled) speak(answer);
  }

  async function refresh() {
    if (requestBusy || document.hidden || typeof window.ssswetApiFetch!=="function") return;
    requestBusy=true;
    try {
      const response=await window.ssswetApiFetch("/api/bots");
      if(!response.ok) throw new Error("HTTP "+response.status);
      const data=await response.json();
      currentData=data;
      renderStage(data);
      renderFeed(data,true);
    } catch (_) {
      /* The main dashboard owns connection and error states. */
    } finally { requestBusy=false; }
  }

  $("bot-voice-toggle").addEventListener("click",() => {
    voiceEnabled=!voiceEnabled;
    renderLabels();
    if(!voiceEnabled && "speechSynthesis" in window) window.speechSynthesis.cancel();
  });
  document.querySelectorAll("[data-bot-question]").forEach(button => {
    button.addEventListener("click",() => answerQuestion(button.dataset.botQuestion));
  });
  window.addEventListener("ssswet-language-changed",() => {
    renderLabels();
    if(currentData){renderStage(currentData);renderFeed(currentData,false);}
  });
  document.addEventListener("visibilitychange",() => {if(!document.hidden)refresh();});
  window.addEventListener("resize",() => {if(currentData)renderStage(currentData);});
  renderLabels();
  refresh();
  window.setInterval(refresh,12000);
})();