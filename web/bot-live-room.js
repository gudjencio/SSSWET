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
  const phaseCopy = {"en":{"searching":"Thinking · searching scholarly publications","reviewing":"Thinking · independently reviewing a teammate’s output","thinking":"Thinking and analysing"},"fr":{"searching":"Réflexion · recherche de publications scientifiques","reviewing":"Réflexion · examen indépendant du travail d’un autre agent","thinking":"Réflexion et analyse"},"es":{"searching":"Pensando · buscando publicaciones científicas","reviewing":"Pensando · revisión independiente del trabajo de otro agente","thinking":"Pensando y analizando"},"de":{"searching":"Denkt nach · sucht wissenschaftliche Veröffentlichungen","reviewing":"Denkt nach · prüft unabhängig die Arbeit eines anderen Agenten","thinking":"Denkt nach und analysiert"},"it":{"searching":"Riflessione · ricerca di pubblicazioni scientifiche","reviewing":"Riflessione · revisione indipendente del lavoro di un altro agente","thinking":"Riflessione e analisi"},"pt":{"searching":"A refletir · a pesquisar publicações científicas","reviewing":"A refletir · a rever de forma independente o trabalho de outro agente","thinking":"A refletir e analisar"},"nl":{"searching":"Denkt na · zoekt wetenschappelijke publicaties","reviewing":"Denkt na · beoordeelt onafhankelijk het werk van een andere agent","thinking":"Denkt na en analyseert"},"ru":{"searching":"Размышление · поиск научных публикаций","reviewing":"Размышление · независимая проверка работы другого агента","thinking":"Размышление и анализ"},"uk":{"searching":"Міркування · пошук наукових публікацій","reviewing":"Міркування · незалежна перевірка роботи іншого агента","thinking":"Міркування й аналіз"},"ar":{"searching":"تفكير · البحث عن منشورات علمية","reviewing":"تفكير · مراجعة مستقلة لعمل وكيل آخر","thinking":"التفكير والتحليل"},"he":{"searching":"חשיבה · חיפוש פרסומים מדעיים","reviewing":"חשיבה · בדיקה עצמאית של עבודת סוכן אחר","thinking":"חשיבה וניתוח"},"ja":{"searching":"思考中 · 学術論文を検索","reviewing":"思考中 · 他のエージェントの成果を独立して確認","thinking":"思考・分析中"},"ko":{"searching":"생각 중 · 학술 논문 검색","reviewing":"생각 중 · 다른 에이전트의 결과를 독립적으로 검토","thinking":"생각하고 분석하는 중"},"zh":{"searching":"思考中 · 正在检索学术文献","reviewing":"思考中 · 正在独立审查另一智能体的成果","thinking":"正在思考和分析"},"hi":{"searching":"विचार जारी · वैज्ञानिक प्रकाशनों की खोज","reviewing":"विचार जारी · दूसरे एजेंट के काम की स्वतंत्र समीक्षा","thinking":"विचार और विश्लेषण"}};
  const phaseLabel = phase => {const c=phaseCopy[lang()]||phaseCopy.en;return phase==="literature_search"?c.searching:phase==="independent_review"?c.reviewing:c.thinking;};
  const t = () => copy[lang()] || copy.en;
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const pretty = (value) => String(value || "—").replace(/([a-z])([A-Z])/g,"$1 $2").replace(/[_-]+/g," ");
  const format = (s, values) => s.replace(/\{(\w+)\}/g, (_, k) => String(values[k] ?? ""));
  const roleLabels = {
    general_researcher:{en:"General researcher",fr:"Chercheur généraliste",es:"Investigador general",de:"Allgemeiner Forscher",it:"Ricercatore generale",pt:"Investigador geral",nl:"Algemeen onderzoeker",ru:"Общий исследователь",uk:"Загальний дослідник",ar:"باحث عام",he:"חוקר כללי",ja:"一般研究員",ko:"일반 연구원",zh:"通用研究员",hi:"सामान्य शोधकर्ता"},
    independent_verifier:{en:"Independent verifier",fr:"Vérificateur indépendant",es:"Verificador independiente",de:"Unabhängiger Prüfer",it:"Verificatore indipendente",pt:"Verificador independente",nl:"Onafhankelijke verificateur",ru:"Независимый проверяющий",uk:"Незалежний перевіряльник",ar:"مدقق مستقل",he:"בודק עצמאי",ja:"独立検証担当",ko:"독립 검증자",zh:"独立核查员",hi:"स्वतंत्र सत्यापक"},
    medical_researcher:{en:"Medical researcher",fr:"Chercheur en médecine",es:"Investigador médico",de:"Medizinischer Forscher",it:"Ricercatore medico",pt:"Investigador médico",nl:"Medisch onderzoeker",ru:"Медицинский исследователь",uk:"Медичний дослідник",ar:"باحث طبي",he:"חוקר רפואי",ja:"医学研究員",ko:"의학 연구원",zh:"医学研究员",hi:"चिकित्सा शोधकर्ता"},
    materials_scientist:{en:"Materials scientist",fr:"Spécialiste des matériaux",es:"Científico de materiales",de:"Materialwissenschaftler",it:"Scienziato dei materiali",pt:"Cientista de materiais",nl:"Materiaalkundige",ru:"Специалист по материалам",uk:"Фахівець із матеріалів",ar:"عالم مواد",he:"מדען חומרים",ja:"材料科学者",ko:"재료 과학자",zh:"材料科学家",hi:"सामग्री वैज्ञानिक"}
  };
  const roleName = (role) => roleLabels[role]?.[lang()] || roleLabels[role]?.en || pretty(role || t().role);
  const avatar = (index) => '<span class="agent-avatar agent-avatar-'+((index%3)+1)+'"><span class="agent-robot-head"><i></i><i></i></span><span class="agent-robot-body"></span></span>';
  const time = (value) => { const d=new Date(value); return value && !Number.isNaN(d.getTime()) ? d.toLocaleTimeString(lang(),{hour:"2-digit",minute:"2-digit"}) : ""; };
  let voiceEnabled = Boolean(window.speechSynthesis && typeof SpeechSynthesisUtterance !== "undefined");
  let initialized = false;
  let knownOutputIds = new Set();
  let spokenMessageIds = new Set();
  let spokenActivityKeys = new Set();
  let spokenOutputIds = new Set();
  let currentData = null;
  let requestBusy = false;
  let speechQueue = [];
  let speechBusy = false;
  let conversationTimer = null;
  let lastThinkingSound = 0;
  let speakerTurn = 0;
  const speechApi = window.speechSynthesis || null;

  function bestVoice(language, agentIndex) {
    if (!speechApi) return null;
    const base = String(language || "en").toLowerCase().split("-")[0];
    const voices = speechApi.getVoices().filter(voice => String(voice.lang || "").toLowerCase().split("-")[0] === base);
    if (!voices.length) return null;
    const quality = /natural|neural|online|premium|enhanced|google|microsoft|siri/i;
    const preferred = voices.slice().sort((a,b) =>
      Number(quality.test(b.name || "")) - Number(quality.test(a.name || "")) ||
      Number(!b.localService) - Number(!a.localService)
    );
    return preferred[Math.abs(agentIndex) % preferred.length] || null;
  }

  function drainSpeechQueue() {
    if (!voiceEnabled || speechBusy || !speechApi || !speechQueue.length) return;
    const item = speechQueue.shift();
    if (!item || !String(item.text || "").trim()) { drainSpeechQueue(); return; }
    speechBusy = true;
    const utterance = new SpeechSynthesisUtterance(String(item.text).replace(/\\s+/g," ").trim().slice(0,1100));
    const language = document.documentElement.lang || "en";
    utterance.lang = language;
    const voice = bestVoice(language,item.agentIndex || 0);
    if (voice) { utterance.voice = voice; utterance.lang = voice.lang || language; }
    utterance.rate = 0.91 + ((item.agentIndex || 0) % 3) * 0.025;
    utterance.pitch = item.agentIndex % 2 ? 0.96 : 1.02;
    utterance.volume = 1;
    const finish = () => { speechBusy = false; window.setTimeout(drainSpeechQueue,220); };
    utterance.onend = finish;
    utterance.onerror = finish;
    speechApi.speak(utterance);
  }

  function speak(message, agentIndex = 0) {
    if (!voiceEnabled || !speechApi || typeof SpeechSynthesisUtterance === "undefined") return;
    const text = String(message || "").trim();
    if (!text) return;
    speechQueue.push({text,agentIndex});
    drainSpeechQueue();
  }

  function scheduleBotConversation() {
    window.clearTimeout(conversationTimer);
    const delay = 26000 + Math.floor(Math.random()*15000);
    conversationTimer = window.setTimeout(() => {
      if (voiceEnabled && !document.hidden && currentData) {
        const active = Array.isArray(currentData.active_agents) ? currentData.active_agents : [];
        const handoffs = Array.isArray(currentData.agent_messages) ? currentData.agent_messages : [];
        const outputs = Array.isArray(currentData.recent_outputs) ? currentData.recent_outputs : [];
        const recent = handoffs.find(item => item.content && !spokenMessageIds.has(String(item.id || item.created_at || item.content)));
        if (recent) {
          const id = String(recent.id || recent.created_at || recent.content);
          spokenMessageIds.add(id);
          const role = roleName(recent.sender_role);
          speak(role + ". " + recent.content, speakerTurn++);
        } else if (active.length && Date.now()-lastThinkingSound > 65000 && Math.random() < 0.18) {
          speak(["Hmm…","Mhmm…"][Math.floor(Math.random()*2)],speakerTurn++);
          lastThinkingSound = Date.now();
        } else if (outputs.length && active.length) {
          const item = outputs.find(entry => entry.summary && String(entry.summary).trim() && !spokenOutputIds.has([entry.task_id,entry.agent_id,entry.created_at].join("|")));
          if (item) {
            spokenOutputIds.add([item.task_id,item.agent_id,item.created_at].join("|"));
            speak(roleName(item.role) + ". " + item.summary,speakerTurn++);
          }
        }
      }
      scheduleBotConversation();
    },delay);
  }

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
    const signature = JSON.stringify(selected.map(agent => ({
      id: agent.id || agent.agent_id,
      role: agent.role || "",
      active: isActive,
      review: !isActive && String(agent.role || "").includes("verif"),
      phase: agent.phase || "",
      language: lang()
    })));
    if (stage.dataset.renderSignature === signature) return;
    stage.dataset.renderSignature = signature;
    stage.innerHTML = selected.map((agent,index) => {
      const role = roleName(agent.role);
      const activeClass = isActive ? "is-active" : (String(agent.role||"").includes("verif") ? "is-review" : "");
      const id = agent.id || agent.agent_id;
      return '<article class="bot-stage-agent '+activeClass+'"><div class="bot-stage-agent-content">'+avatar(index)+'<div class="bot-stage-agent-label"><strong>'+esc(role)+'</strong><small>'+esc(id)+'</small><small class="bot-agent-phase">'+esc(isActive?phaseLabel(agent.phase):t().notActive)+'</small></div></div></article>';
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
    const activeAgents = Array.isArray(data.active_agents) ? data.active_agents : [];
    const activeCount = activeAgents.length;
    const thinking = {"en":"Research agents are thinking and working","fr":"Les agents réfléchissent et travaillent","es":"Los agentes están pensando y trabajando","de":"Die Forschungsagenten denken nach und arbeiten","it":"Gli agenti stanno riflettendo e lavorando","pt":"Os agentes estão a pensar e a trabalhar","nl":"Onderzoeksagenten denken na en werken","ru":"Исследовательские агенты размышляют и работают","uk":"Дослідницькі агенти міркують і працюють","ar":"وكلاء البحث يفكرون ويعملون","he":"סוכני המחקר חושבים ועובדים","ja":"研究エージェントが思考し作業中です","ko":"연구 에이전트가 생각하고 작업 중입니다","zh":"研究智能体正在思考和工作","hi":"अनुसंधान एजेंट सोच रहे हैं और काम कर रहे हैं"}[lang()] || "Research agents are thinking and working";
    const handoffCards = handoffs.slice(0,8).map((item,index) => {
      const isResponse = item.message_type === "peer_review_response";
      const heading = esc(roleName(item.sender_role))+' → '+esc(roleName(item.recipient_role));
      const handoffLabels = {
        en:{responseState:"literature review · provisional",requestState:"shared · awaiting review",response:"Independent review response",request:"Review request"},
        fr:{responseState:"examen documentaire · provisoire",requestState:"transmis · en attente d’examen",response:"Retour d’examen indépendant",request:"Demande d’examen"},
        es:{responseState:"revisión documental · provisional",requestState:"compartido · pendiente de revisión",response:"Respuesta de revisión independiente",request:"Solicitud de revisión"},
        de:{responseState:"Literaturprüfung · vorläufig",requestState:"geteilt · Prüfung ausstehend",response:"Unabhängige Prüfungsantwort",request:"Prüfungsanfrage"},
        it:{responseState:"revisione della letteratura · provvisoria",requestState:"condiviso · in attesa di revisione",response:"Risposta della revisione indipendente",request:"Richiesta di revisione"},
        pt:{responseState:"revisão bibliográfica · provisória",requestState:"partilhado · aguarda revisão",response:"Resposta da revisão independente",request:"Pedido de revisão"},
        nl:{responseState:"literatuurbeoordeling · voorlopig",requestState:"gedeeld · beoordeling in afwachting",response:"Onafhankelijke beoordelingsreactie",request:"Beoordelingsverzoek"},
        ru:{responseState:"обзор литературы · предварительно",requestState:"передано · ожидает проверки",response:"Ответ независимой проверки",request:"Запрос на проверку"},
        uk:{responseState:"огляд літератури · попередньо",requestState:"передано · очікує перевірки",response:"Відповідь незалежного огляду",request:"Запит на перевірку"},
        ar:{responseState:"مراجعة أدبية · أولية",requestState:"تمت المشاركة · بانتظار المراجعة",response:"رد المراجعة المستقلة",request:"طلب مراجعة"},
        he:{responseState:"סקירת ספרות · ראשונית",requestState:"שותף · ממתין לבדיקה",response:"תגובה לבדיקה עצמאית",request:"בקשת בדיקה"},
        ja:{responseState:"文献レビュー · 暫定",requestState:"共有済み · 確認待ち",response:"独立レビューの回答",request:"レビュー依頼"},
        ko:{responseState:"문헌 검토 · 잠정",requestState:"공유됨 · 검토 대기",response:"독립 검토 응답",request:"검토 요청"},
        zh:{responseState:"文献审查 · 暂定",requestState:"已共享 · 等待审查",response:"独立审查回复",request:"审查请求"},
        hi:{responseState:"साहित्य समीक्षा · प्रारंभिक",requestState:"साझा किया गया · समीक्षा लंबित",response:"स्वतंत्र समीक्षा का उत्तर",request:"समीक्षा अनुरोध"}
      }[lang()] || {responseState:"literature review · provisional",requestState:"shared · awaiting review",response:"Independent review response",request:"Review request"};
      const state = isResponse ? handoffLabels.responseState : handoffLabels.requestState;
      const label = isResponse ? handoffLabels.response : handoffLabels.request;
      return '<article class="bot-conversation-message bot-handoff-message '+(isResponse?"bot-review-response":"bot-review-request")+'"><div class="message-avatar" aria-hidden="true">'+(isResponse?"✓":"↗")+'</div><div><strong>'+heading+'</strong><p>'+esc(item.content)+'</p><small>'+esc(label)+' · '+esc(state)+' · '+esc(time(item.created_at))+'</small></div></article>';
    });
    const messages = handoffCards.concat(valid.slice(0,10).map((item,index) => {
      const count = Number(item.evidence_count || 0);
      const detail = count ? count+' '+t().evidence : t().noEvidence;
      return '<article class="bot-conversation-message"><div class="message-avatar" aria-hidden="true">'+(index+1)+'</div><div><strong>'+esc(roleName(item.role))+' · '+esc(item.agent_id || t().role)+'</strong><p>'+esc(item.summary)+'</p><small>'+esc(t().provisional)+' · '+esc(detail)+' · '+esc(time(item.created_at))+'</small></div></article>';
    }));
    if (!valid.length && !handoffCards.length) messages.push('<p class="bot-conversation-empty">'+esc(t().empty)+'</p>');
    if (activeCount) {
      const liveLines = activeAgents.slice(0,6).map(agent => '<li><strong>'+esc(roleName(agent.role))+'</strong><span>'+esc(phaseLabel(agent.phase))+'</span></li>').join("");
      messages.push('<div class="bot-thinking bot-live-activity" style="--agent-count:'+Math.max(1,activeCount)+'"><strong>'+esc(thinking)+' · '+activeCount+'</strong><ul>'+liveLines+'</ul><i></i><i></i><i></i></div>');
      if (speakNew && voiceEnabled) activeAgents.forEach(agent => {
        const key=[agent.id,agent.task_id,agent.phase||"thinking"].join("|");
        if (!spokenActivityKeys.has(key)) { spokenActivityKeys.add(key); speak(roleName(agent.role)+". "+phaseLabel(agent.phase),speakerTurn++); }
      });
    }
    feed.innerHTML = messages.join("");
    const visual = $("bot-command-visual");
    if (visual) {
      let bubbles = visual.querySelector(".bot-thought-bubbles");
      if (!bubbles) {
        bubbles = document.createElement("div");
        bubbles.className = "bot-thought-bubbles";
        bubbles.setAttribute("aria-label", ({fr:"Bulles de réflexion des agents",en:"Agent thought bubbles",es:"Burbujas de pensamiento de los agentes",de:"Gedankenblasen der Agenten",it:"Nuvolette di pensiero degli agenti",pt:"Balões de pensamento dos agentes",nl:"Denkballonnen van de agents",ru:"Облачка мыслей агентов",uk:"Хмаринки думок агентів",ar:"فقاعات أفكار الوكلاء",he:"בועות מחשבה של הסוכנים",ja:"エージェントの思考バブル",ko:"에이전트 생각 말풍선",zh:"智能体思考气泡",hi:"एजेंटों के विचार बुलबुले"})[lang()] || "Agent thought bubbles");
        visual.appendChild(bubbles);
      }
      const thoughts = handoffs.slice(0,2).map(item => item.content).concat(valid.slice(0,2).map(item => item.summary)).filter(Boolean).slice(0,3);
      bubbles.innerHTML = thoughts.map((message,index) => '<div class="bot-thought-bubble thought-'+index+'">'+esc(String(message).slice(0,150))+'</div>').join("");
    }
    if (speakNew && voiceEnabled && fresh.length) {
      const item=fresh[fresh.length-1];
      spokenOutputIds.add([item.task_id,item.agent_id,item.created_at].join("|"));
      speak(roleName(item.role) + ". " + item.summary,speakerTurn++);
    }
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
    if(voiceEnabled) speak(answer,speakerTurn++);
  }

  async function refresh() {
    if (requestBusy || document.hidden || typeof window.ssswetApiFetch!=="function") return;
    requestBusy=true;
    try {
      const response=await window.ssswetApiFetch("/api/bots");
      if(!response.ok) throw new Error("HTTP "+response.status);
      const data=await response.json();
      currentData=data;
      window.SSSWET_LIVE_RESEARCH_DATA=data;
      window.dispatchEvent(new CustomEvent("ssswet-bot-data",{detail:data}));
      renderStage(data);
      renderFeed(data,true);
    } catch (_) {
      /* The main dashboard owns connection and error states. */
    } finally { requestBusy=false; }
  }

  $("bot-voice-toggle").addEventListener("click",() => {
    voiceEnabled=!voiceEnabled;
    renderLabels();
    if(!voiceEnabled && speechApi) { speechQueue=[]; speechApi.cancel(); speechBusy=false; }
  });
  document.querySelectorAll("[data-bot-question]").forEach(button => {
    button.addEventListener("click",() => answerQuestion(button.dataset.botQuestion));
  });
  document.addEventListener("click",event => {
    const technologyButton=event.target.closest("button[data-tech]");
    if(!technologyButton) return;
    window.setTimeout(() => {
      const title=$("technology-dialog-title")?.textContent?.trim();
      const description=$("technology-dialog-description")?.textContent?.trim();
      if(voiceEnabled && title && description) {
        const intro = lang()==="fr" ? "Voici le résumé de cette technologie." :
          lang()==="es" ? "Este es el resumen de esta tecnología." :
          lang()==="de" ? "Hier ist die Zusammenfassung dieser Technologie." :
          lang()==="it" ? "Ecco il riepilogo di questa tecnologia." :
          lang()==="pt" ? "Aqui está o resumo desta tecnologia." :
          lang()==="nl" ? "Hier is de samenvatting van deze technologie." :
          lang()==="ru" ? "Краткое описание этой технологии." :
          lang()==="uk" ? "Ось короткий огляд цієї технології." :
          lang()==="ar" ? "إليك ملخص هذه التقنية." :
          lang()==="he" ? "הנה סיכום הטכנולוגיה הזו." :
          lang()==="ja" ? "この技術の概要です。" :
          lang()==="ko" ? "이 기술의 요약입니다." :
          lang()==="zh" ? "以下是这项技术的摘要。" :
          lang()==="hi" ? "यह इस तकनीक का सारांश है।" : "Here is a summary of this technology.";
        speak(intro + " " + title + ". " + description,speakerTurn++);
      }
    },180);
  });
  window.addEventListener("ssswet-language-changed",() => {
    renderLabels();
    if(currentData){renderStage(currentData);renderFeed(currentData,false);}
  });
  document.addEventListener("visibilitychange",() => {if(!document.hidden)refresh();});
  window.addEventListener("resize",() => {if(currentData)renderStage(currentData);});
  renderLabels();
  refresh();
  window.setInterval(refresh,5000);
  scheduleBotConversation();
})();