(() => {
  "use strict";
  const sequences = {"en":[["Evidence coverage","verified sources ÷ sources reviewed × 100"],["Priority score","Σ(weight × criterion) ÷ 5 × 100"],["Reproducibility","Δ = |result A − result B|"],["Progress","completed tasks ÷ total tasks × 100"],["Uncertainty","U = 1 − confidence"]],"fr":[["Couverture des preuves","sources vérifiées ÷ sources examinées × 100"],["Score de priorité","Σ(poids × critère) ÷ 5 × 100"],["Reproductibilité","Δ = |résultat A − résultat B|"],["Progression","tâches terminées ÷ tâches totales × 100"],["Incertitude","U = 1 − confiance"]],"es":[["Cobertura de evidencias","fuentes verificadas ÷ fuentes revisadas × 100"],["Puntuación de prioridad","Σ(peso × criterio) ÷ 5 × 100"],["Reproducibilidad","Δ = |resultado A − resultado B|"],["Progreso","tareas completadas ÷ tareas totales × 100"],["Incertidumbre","U = 1 − confianza"]],"de":[["Belegabdeckung","geprüfte Quellen ÷ untersuchte Quellen × 100"],["Prioritätswert","Σ(Gewicht × Kriterium) ÷ 5 × 100"],["Reproduzierbarkeit","Δ = |Ergebnis A − Ergebnis B|"],["Fortschritt","abgeschlossene Aufgaben ÷ alle Aufgaben × 100"],["Unsicherheit","U = 1 − Vertrauen"]],"it":[["Copertura delle prove","fonti verificate ÷ fonti esaminate × 100"],["Punteggio di priorità","Σ(peso × criterio) ÷ 5 × 100"],["Riproducibilità","Δ = |risultato A − risultato B|"],["Avanzamento","attività completate ÷ attività totali × 100"],["Incertezza","U = 1 − fiducia"]],"pt":[["Cobertura das provas","fontes verificadas ÷ fontes analisadas × 100"],["Pontuação de prioridade","Σ(peso × critério) ÷ 5 × 100"],["Reprodutibilidade","Δ = |resultado A − resultado B|"],["Progresso","tarefas concluídas ÷ tarefas totais × 100"],["Incerteza","U = 1 − confiança"]],"nl":[["Bewijsdekking","geverifieerde bronnen ÷ onderzochte bronnen × 100"],["Prioriteitsscore","Σ(gewicht × criterium) ÷ 5 × 100"],["Reproduceerbaarheid","Δ = |resultaat A − resultaat B|"],["Voortgang","voltooide taken ÷ alle taken × 100"],["Onzekerheid","U = 1 − vertrouwen"]],"ru":[["Охват доказательствами","проверенные источники ÷ изученные источники × 100"],["Приоритетный балл","Σ(вес × критерий) ÷ 5 × 100"],["Воспроизводимость","Δ = |результат A − результат B|"],["Прогресс","завершённые задачи ÷ все задачи × 100"],["Неопределённость","U = 1 − уверенность"]],"uk":[["Охоплення доказами","перевірені джерела ÷ опрацьовані джерела × 100"],["Оцінка пріоритету","Σ(вага × критерій) ÷ 5 × 100"],["Відтворюваність","Δ = |результат A − результат B|"],["Прогрес","виконані завдання ÷ усі завдання × 100"],["Невизначеність","U = 1 − впевненість"]],"ar":[["تغطية الأدلة","المصادر المتحقق منها ÷ المصادر التي تمت مراجعتها × 100"],["درجة الأولوية","Σ(الوزن × المعيار) ÷ 5 × 100"],["قابلية التكرار","Δ = |النتيجة A − النتيجة B|"],["التقدم","المهام المكتملة ÷ إجمالي المهام × 100"],["عدم اليقين","U = 1 − الثقة"]],"he":[["כיסוי ראיות","מקורות שאומתו ÷ מקורות שנבדקו × 100"],["ציון עדיפות","Σ(משקל × קריטריון) ÷ 5 × 100"],["יכולת שחזור","Δ = |תוצאה A − תוצאה B|"],["התקדמות","משימות שהושלמו ÷ כלל המשימות × 100"],["אי־ודאות","U = 1 − ביטחון"]],"ja":[["証拠の網羅率","検証済み情報源 ÷ 調査した情報源 × 100"],["優先度スコア","Σ(重み × 評価基準) ÷ 5 × 100"],["再現性","Δ = |結果 A − 結果 B|"],["進捗","完了タスク ÷ 全タスク × 100"],["不確実性","U = 1 − 信頼度"]],"ko":[["근거 범위","검증된 출처 ÷ 검토한 출처 × 100"],["우선순위 점수","Σ(가중치 × 기준) ÷ 5 × 100"],["재현성","Δ = |결과 A − 결과 B|"],["진행률","완료된 작업 ÷ 전체 작업 × 100"],["불확실성","U = 1 − 신뢰도"]],"zh":[["证据覆盖率","已核实来源 ÷ 已审查来源 × 100"],["优先级评分","Σ(权重 × 指标) ÷ 5 × 100"],["可重复性","Δ = |结果 A − 结果 B|"],["进度","已完成任务 ÷ 总任务数 × 100"],["不确定性","U = 1 − 置信度"]],"hi":[["साक्ष्य कवरेज","सत्यापित स्रोत ÷ समीक्षित स्रोत × 100"],["प्राथमिकता स्कोर","Σ(भार × मानदंड) ÷ 5 × 100"],["पुनरुत्पादकता","Δ = |परिणाम A − परिणाम B|"],["प्रगति","पूर्ण कार्य ÷ कुल कार्य × 100"],["अनिश्चितता","U = 1 − विश्वास"]]};
  const injectStyle = () => {
    if (document.getElementById("ssswet-equations-style")) return;
    const style = document.createElement("style");
    style.id = "ssswet-equations-style";
    style.textContent = `
      .ssswet-equations{position:absolute;left:50%;bottom:43px;transform:translateX(-50%);z-index:7;width:min(330px,54%);margin:0;padding:6px 10px;border:1px solid rgba(190,166,119,.17);border-radius:11px;background:rgba(5,7,6,.84);backdrop-filter:blur(8px);overflow:hidden;min-height:0;text-align:center;pointer-events:none}
      .ssswet-equations::before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 50% 0,rgba(255,255,255,.06),transparent 58%);pointer-events:none}
      .ssswet-equations-label{position:relative;font-size:.54rem;letter-spacing:.11em;text-transform:uppercase;opacity:.52;margin-bottom:2px}
      .ssswet-equation{position:relative;min-height:18px;font-family:Georgia,"Times New Roman",serif;font-size:clamp(.68rem,1vw,.85rem);letter-spacing:.01em;line-height:1.3}
      .ssswet-equation::after{content:"";display:inline-block;width:2px;height:1em;margin-left:3px;vertical-align:-.14em;background:currentColor;animation:ssswetCaret .8s steps(1) infinite}
      .ssswet-equation-caption{display:none}
      @keyframes ssswetCaret{50%{opacity:0}}
      @media(max-width:640px){.ssswet-equations{bottom:36px;width:min(290px,64%);padding:5px 8px}.ssswet-equation{font-size:.67rem}}
    `;
    document.head.appendChild(style);
  };
  const mount = () => {
    injectStyle();
    if (document.getElementById("ssswet-equations")) return;
    const target = document.querySelector(".bot-command-visual");
    if (!target) return;
    const panel = document.createElement("section");
    panel.id = "ssswet-equations";
    panel.className = "ssswet-equations";
    panel.setAttribute("aria-label", "Research calculations");
    panel.innerHTML = '<div class="ssswet-equations-label"></div><div class="ssswet-equation" aria-live="polite"></div><div class="ssswet-equation-caption"></div>';
    target.appendChild(panel);
    const label = panel.querySelector(".ssswet-equations-label");
    const equation = panel.querySelector(".ssswet-equation");
    let index = 0, timer = null;
    const getLanguage = () => {
      const code = String(document.documentElement.lang || "en").toLowerCase().split("-")[0];
      return sequences[code] ? code : "en";
    };
    const render = () => {
      const language = getLanguage();
      const item = sequences[language][index % sequences[language].length];
      label.textContent = item[0];
      panel.setAttribute("aria-label", item[0]);
      equation.textContent = "";
      let position = 0;
      window.clearInterval(timer);
      timer = window.setInterval(() => {
        equation.textContent = item[1].slice(0, position++);
        if (position > item[1].length) {
          window.clearInterval(timer);
          window.setTimeout(() => { index += 1; render(); }, 1900);
        }
      }, 24);
    };
    render();
    window.addEventListener("ssswet-language-changed", render);
    document.getElementById("language")?.addEventListener("change", () => window.setTimeout(render, 0));
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount, { once: true });
  else mount();
})();