(() => {
  "use strict";

  const translations = {
    en: "Repair if broken",
    ur: "اگر پروجیکٹ خراب ہو تو دوبارہ کھولیں",
    fr: "Réparer le projet s’il ne fonctionne plus",
    es: "Reiniciar el proyecto si está dañado",
    pt: "Reiniciar o projeto se estiver com problemas",
    it: "Riavvia il progetto se non funziona",
    de: "Projekt neu starten, wenn es nicht funktioniert",
    nl: "Project opnieuw starten als het niet werkt",
    ja: "プロジェクトが壊れている場合は再起動",
    ko: "프로젝트가 고장났다면 다시 시작",
    zh: "如果项目出现问题，请重新打开",
    gcf: "Relansé pwojé-la si i kasé",
    ku: "Heke projey têk çû, ji nû ve bide destpêkirin",
    da: "Genstart projektet, hvis det er gået i stykker",
    tr: "Proje bozulduysa yeniden başlat",
    sv: "Starta om projektet om det inte fungerar",
    jv: "Bukak maneh proyek yen rusak",
    la: "Proiectum iterum aperi si fractum est",
    el: "Επανεκκινήστε το έργο αν έχει πρόβλημα",
    he: "הפעל מחדש את הפרויקט אם הוא התקלקל",
    ms: "Mulakan semula projek jika rosak",
    ru: "Перезапустить проект, если он сломан",
    uk: "Перезапустити проєкт, якщо він не працює",
    fa: "اگر پروژه خراب است، دوباره آن را باز کنید",
    cs: "Restartovat projekt, pokud nefunguje",
    hi: "प्रोजेक्ट खराब हो तो उसे फिर से खोलें",
    th: "เปิดโครงการใหม่หากโครงการมีปัญหา",
    yo: "Tun iṣẹ́ náà bẹ́ẹ̀rẹ̀ bí ó bá bàjẹ́",
    ar: "إعادة تشغيل المشروع إذا كان معطلاً"
  };

  const projectUrl = "https://gudjencio.github.io/SSSWET/";

  function languageCode() {
    const select = document.getElementById("language");
    return String(select?.value || document.documentElement.lang || navigator.language || "en")
      .toLowerCase()
      .replace("_", "-")
      .split("-")[0];
  }

  function updateLabel() {
    const button = document.getElementById("repair-project-button");
    if (!button) return;
    button.textContent = translations[languageCode()] || translations.en;
  }

  function init() {
    const button = document.getElementById("repair-project-button");
    if (!button) return;
    button.href = projectUrl;
    button.target = "_blank";
    button.rel = "noopener noreferrer";
    button.setAttribute("aria-label", translations[languageCode()] || translations.en);
    updateLabel();
    document.getElementById("language")?.addEventListener("change", updateLabel);
    window.addEventListener("ssswet-language-changed", updateLabel);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
