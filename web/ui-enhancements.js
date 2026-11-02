(() => {
  "use strict";

  if (window.__SSSWET_UI_ENHANCEMENTS__) return;
  window.__SSSWET_UI_ENHANCEMENTS__ = true;

  const style = document.createElement("style");
  style.dataset.ssswetUiEnhancements = "true";
  style.textContent = `
    .topbar {
      position: relative;
      justify-content: center;
      min-height: 58px;
      padding-inline: 180px;
    }
    .brand {
      position: absolute;
      inset-inline-start: 0;
      top: 0;
    }
    .language-control {
      position: relative;
      z-index: 6;
      display: inline-flex;
      justify-content: center;
      padding: 4px;
      border: 1px solid rgba(255,255,255,.11);
      border-radius: 999px;
      background: linear-gradient(135deg, rgba(255,255,255,.075), rgba(255,255,255,.018));
      box-shadow: 0 14px 40px rgba(0,0,0,.34), inset 0 1px rgba(255,255,255,.07);
      backdrop-filter: blur(18px) saturate(130%);
    }
    .language-control::before {
      content: "";
      position: absolute;
      inset: 0;
      border-radius: inherit;
      pointer-events: none;
      background: radial-gradient(circle at 50% 0, rgba(255,255,255,.12), transparent 62%);
      opacity: .7;
    }
    #language {
      position: relative;
      min-width: 190px;
      max-width: 240px;
      padding: 10px 40px 10px 16px;
      border: 1px solid rgba(255,255,255,.12);
      background: rgba(5,5,5,.72);
      color: #f7f7f7;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .04em;
      text-align: center;
      text-align-last: center;
      box-shadow: inset 0 1px rgba(255,255,255,.04);
    }
    #language:hover { border-color: rgba(255,255,255,.28); background: rgba(18,18,18,.9); }
    #language:focus-visible { border-color: #aaa; box-shadow: 0 0 0 3px rgba(255,255,255,.08); }
    html[dir="rtl"] .topbar { justify-content: center; }
    html[dir="rtl"] .brand { inset-inline-start: auto; inset-inline-end: 0; text-align: right; }
    @media (max-width: 620px) {
      .topbar { min-height: 102px; padding: 44px 0 0; justify-content: center; }
      .brand { inset-inline: 0; top: 0; text-align: center; }
      .brand-subtitle { margin-inline: auto; }
      .language-control { width: min(92vw, 300px); }
      #language { width: 100%; max-width: none; min-width: 0; }
    }
    @media (max-width: 420px) {
      .topbar { min-height: 94px; }
      .language-control { width: min(94vw, 280px); }
      #language { padding: 9px 34px 9px 12px; font-size: 11px; }
    }
    .bot-control-fast-mode {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      margin-inline-start: 8px;
      padding: 5px 9px;
      border: 1px solid #303030;
      border-radius: 999px;
      color: #aaa;
      background: rgba(255,255,255,.025);
      font-size: 9px;
      letter-spacing: .06em;
      text-transform: uppercase;
    }
    .bot-control-fast-mode::before {
      content: "";
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: #fff;
      box-shadow: 0 0 9px rgba(255,255,255,.6);
    }
  `;
  (document.head || document.documentElement).appendChild(style);

  const applyFastMode = () => {
    const host = document.getElementById("bot-control-status");
    if (!host || host.querySelector(".bot-control-fast-mode")) return;
    const badge = document.createElement("span");
    badge.className = "bot-control-fast-mode";
    badge.setAttribute("aria-label", "Fast response mode");
    badge.textContent = "FAST RESPONSE";
    host.appendChild(badge);
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", applyFastMode, { once: true });
  else applyFastMode();
})();
