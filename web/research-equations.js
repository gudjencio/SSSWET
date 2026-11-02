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
      .ssswet-equations{position:absolute;left:50%;bottom:58px;transform:translateX(-50%);z-index:5;width:min(420px,72%);margin:0;padding:8px 13px;border:1px solid rgba(190,166,119,.18);border-radius:13px;background:rgba(5,7,6,.78);backdrop-filter:blur(8px);overflow:hidden;min-height:0;text-align:center;pointer-events:none}
      .ssswet-equations::before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 50% 0,rgba(255,255,255,.08),transparent 58%);pointer-events:none}
      .ssswet-equations-label{position:relative;font-size:.58rem;letter-spacing:.13em;text-transform:uppercase;opacity:.5;margin-bottom:3px}
      .ssswet-equation{position:relative;min-height:22px;font-family:Georgia,"Times New Roman",serif;font-size:clamp(.78rem,1.5vw,1rem);letter-spacing:.025em;line-height:1.35}
      .ssswet-equation::after{content:"";display:inline-block;width:2px;height:1.05em;margin-left:3px;vertical-align:-.16em;background:currentColor;animation:ssswetCaret .8s steps(1) infinite}
      .ssswet-equation-caption{display:none}
      @keyframes ssswetCaret{50%{opacity:0}}
      @media(max-width:640px){.ssswet-equations{bottom:52px;width:min(360px,82%);padding:7px 10px}.ssswet-equation{font-size:.78rem}}
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
