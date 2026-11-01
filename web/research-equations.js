(() => {
  "use strict";

  const sequences = {
    en: [
      ["Evidence coverage", "verified sources ÷ sources reviewed × 100", "Measure what is actually supported"],
      ["Priority score", "Σ(weight × criterion) ÷ 5 × 100", "Compare only when the assessment is complete"],
      ["Reproducibility", "Δ = |result A − result B|", "Smaller differences can indicate closer agreement"],
      ["Progress", "completed tasks ÷ total tasks × 100", "Track the research pass without guessing results"],
      ["Uncertainty", "U = 1 − confidence", "Keep uncertainty visible instead of hiding it"]
    ],
    fr: [
      ["Couverture des preuves", "sources vérifiées ÷ sources examinées × 100", "Mesurer ce qui est réellement étayé"],
      ["Score de priorité", "Σ(poids × critère) ÷ 5 × 100", "Comparer seulement lorsque l’évaluation est complète"],
      ["Reproductibilité", "Δ = |résultat A − résultat B|", "Une différence plus faible peut indiquer un accord plus proche"],
      ["Progression", "tâches terminées ÷ tâches totales × 100", "Suivre la campagne sans inventer de résultat"],
      ["Incertitude", "U = 1 − confiance", "Garder l’incertitude visible au lieu de la masquer"]
    ]
  };

  const injectStyle = () => {
    if (document.getElementById("ssswet-equations-style")) return;
    const style = document.createElement("style");
    style.id = "ssswet-equations-style";
    style.textContent = `
      .ssswet-equations{position:relative;margin:0 0 18px;padding:14px 16px;border:1px solid rgba(255,255,255,.08);border-radius:18px;background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.018));overflow:hidden;min-height:92px;text-align:center}
      .ssswet-equations::before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 50% 0,rgba(255,255,255,.08),transparent 58%);pointer-events:none}
      .ssswet-equations-label{position:relative;font-size:.67rem;letter-spacing:.16em;text-transform:uppercase;opacity:.52;margin-bottom:7px}
      .ssswet-equation{position:relative;min-height:31px;font-family:Georgia,"Times New Roman",serif;font-size:clamp(1rem,2.2vw,1.34rem);letter-spacing:.025em;line-height:1.4}
      .ssswet-equation::after{content:"";display:inline-block;width:2px;height:1.05em;margin-left:3px;vertical-align:-.16em;background:currentColor;animation:ssswetCaret .8s steps(1) infinite}
      .ssswet-equation-caption{position:relative;margin-top:5px;font-size:.72rem;opacity:.55}
      @keyframes ssswetCaret{50%{opacity:0}}
      @media(max-width:640px){.ssswet-equations{margin-inline:0;padding:12px}.ssswet-equation{font-size:1rem}}
    `;
    document.head.appendChild(style);
  };

  const mount = () => {
    injectStyle();
    if (document.getElementById("ssswet-equations")) return;
    const target = document.querySelector(".bot-status");
    if (!target) return;
    const panel = document.createElement("section");
    panel.id = "ssswet-equations";
    panel.className = "ssswet-equations";
    panel.setAttribute("aria-label", "Research calculations");
    panel.innerHTML = '<div class="ssswet-equations-label"></div><div class="ssswet-equation" aria-live="polite"></div><div class="ssswet-equation-caption"></div>';
    target.parentNode.insertBefore(panel, target);

    const label = panel.querySelector(".ssswet-equations-label");
    const equation = panel.querySelector(".ssswet-equation");
    const caption = panel.querySelector(".ssswet-equation-caption");
    let language = "en";
    let index = 0;
    let timer = null;

    const getLanguage = () => String(document.documentElement.lang || "en").toLowerCase().startsWith("fr") ? "fr" : "en";
    const render = () => {
      language = getLanguage();
      const item = sequences[language][index % sequences[language].length];
      label.textContent = item[0];
      caption.textContent = item[2];
      equation.textContent = "";
      let position = 0;
      window.clearInterval(timer);
      timer = window.setInterval(() => {
        equation.textContent = item[1].slice(0, position++);
        if (position > item[1].length) {
          window.clearInterval(timer);
          window.setTimeout(() => { index += 1; render(); }, 1700);
        }
      }, 28);
    };
    render();
    window.addEventListener("ssswet-language-changed", render);
    document.getElementById("language")?.addEventListener("change", () => window.setTimeout(render, 0));
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount, { once: true });
  else mount();
})();
