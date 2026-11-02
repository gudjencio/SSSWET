/* SSSWET platform routing and localized application guidance. */
(() => {
  "use strict";

  const panel = document.getElementById("platform-downloads");
  if (!panel) return;

  const install = document.getElementById("ssswet-install-app");
  const mobile = document.getElementById("ssswet-mobile-download");
  const desktop = document.getElementById("ssswet-desktop-download");
  const hint = document.getElementById("ssswet-install-hint");
  const heading = document.getElementById("platform-downloads-title");
  const intro = panel.querySelector(".platform-downloads-copy > p:not(.eyebrow)");
  const note = panel.querySelector(".platform-downloads-note");
  const eyebrow = panel.querySelector(".platform-downloads-copy .eyebrow");

  const language = () => {
    const selected = document.getElementById("language")?.value;
    const root = document.documentElement.dataset.language || document.documentElement.lang;
    return String(selected || root || navigator.language || "en").toLowerCase().split("-")[0];
  };

  const dictionaries = {
    en: { heading:"Take SSSWET with you", intro:"Install the official application for the device you are using.", android:"Android application", iphone:"iPhone application", pc:"PC application", install:"Install SSSWET", hintAndroid:"Android detected. Use the official Android release or install the web app from this browser.", hintIphone:"iPhone detected. Use Safari to add SSSWET to your Home Screen, or open the official iPhone web experience.", hintPc:"Computer detected. Download the official application for Windows, macOS or Linux.", note:"Official releases only. Availability depends on the published build and device compatibility.", web:"Open web application" },
    fr: { heading:"Emportez SSSWET partout", intro:"Installez l’application officielle adaptée à l’appareil que vous utilisez.", android:"Application Android", iphone:"Application iPhone", pc:"Application PC", install:"Installer SSSWET", hintAndroid:"Android détecté. Utilisez la version Android officielle ou installez l’application web depuis ce navigateur.", hintIphone:"iPhone détecté. Dans Safari, ajoutez SSSWET à l’écran d’accueil ou ouvrez l’expérience web officielle pour iPhone.", hintPc:"Ordinateur détecté. Téléchargez l’application officielle pour Windows, macOS ou Linux.", note:"Versions officielles uniquement. La disponibilité dépend de la version publiée et de la compatibilité de l’appareil.", web:"Ouvrir l’application web" },
    es: { heading:"Lleva SSSWET contigo", intro:"Instala la aplicación oficial adaptada al dispositivo que utilizas.", android:"Aplicación Android", iphone:"Aplicación para iPhone", pc:"Aplicación para PC", install:"Instalar SSSWET", hintAndroid:"Android detectado. Usa la versión oficial de Android o instala la aplicación web desde este navegador.", hintIphone:"iPhone detectado. En Safari, añade SSSWET a la pantalla de inicio o abre la experiencia web oficial para iPhone.", hintPc:"Ordenador detectado. Descarga la aplicación oficial para Windows, macOS o Linux.", note:"Solo versiones oficiales. La disponibilidad depende de la versión publicada y de la compatibilidad del dispositivo.", web:"Abrir aplicación web" },
    de: { heading:"SSSWET überall dabei", intro:"Installiere die offizielle Anwendung für das verwendete Gerät.", android:"Android-Anwendung", iphone:"iPhone-Anwendung", pc:"PC-Anwendung", install:"SSSWET installieren", hintAndroid:"Android erkannt. Verwende die offizielle Android-Version oder installiere die Web-App über diesen Browser.", hintIphone:"iPhone erkannt. Füge SSSWET in Safari zum Home-Bildschirm hinzu oder öffne die offizielle iPhone-Webversion.", hintPc:"Computer erkannt. Lade die offizielle Anwendung für Windows, macOS oder Linux herunter.", note:"Nur offizielle Versionen. Die Verfügbarkeit hängt von der veröffentlichten Version und der Gerätekompatibilität ab.", web:"Web-App öffnen" },
    it: { heading:"Porta SSSWET con te", intro:"Installa l’applicazione ufficiale per il dispositivo che stai utilizzando.", android:"Applicazione Android", iphone:"Applicazione iPhone", pc:"Applicazione PC", install:"Installa SSSWET", hintAndroid:"Android rilevato. Usa la versione Android ufficiale oppure installa l’app web da questo browser.", hintIphone:"iPhone rilevato. In Safari aggiungi SSSWET alla schermata Home oppure apri l’esperienza web ufficiale per iPhone.", hintPc:"Computer rilevato. Scarica l’applicazione ufficiale per Windows, macOS o Linux.", note:"Solo versioni ufficiali. La disponibilità dipende dalla versione pubblicata e dalla compatibilità del dispositivo.", web:"Apri l’applicazione web" },
    pt: { heading:"Leve o SSSWET com você", intro:"Instale o aplicativo oficial adequado ao dispositivo que você está usando.", android:"Aplicativo Android", iphone:"Aplicativo para iPhone", pc:"Aplicativo para PC", install:"Instalar SSSWET", hintAndroid:"Android detectado. Use a versão oficial do Android ou instale o aplicativo web neste navegador.", hintIphone:"iPhone detectado. No Safari, adicione o SSSWET à tela inicial ou abra a experiência web oficial para iPhone.", hintPc:"Computador detectado. Baixe o aplicativo oficial para Windows, macOS ou Linux.", note:"Somente versões oficiais. A disponibilidade depende da versão publicada e da compatibilidade do dispositivo.", web:"Abrir aplicativo web" },
    nl: { heading:"Neem SSSWET met je mee", intro:"Installeer de officiële toepassing voor het apparaat dat je gebruikt.", android:"Android-applicatie", iphone:"iPhone-applicatie", pc:"PC-applicatie", install:"SSSWET installeren", hintAndroid:"Android gedetecteerd. Gebruik de officiële Android-versie of installeer de webapp vanuit deze browser.", hintIphone:"iPhone gedetecteerd. Voeg SSSWET in Safari toe aan je beginscherm of open de officiële iPhone-webversie.", hintPc:"Computer gedetecteerd. Download de officiële toepassing voor Windows, macOS of Linux.", note:"Alleen officiële versies. Beschikbaarheid hangt af van de gepubliceerde versie en apparaatcompatibiliteit.", web:"Webapp openen" },
    ru: { heading:"Берите SSSWET с собой", intro:"Установите официальное приложение для используемого устройства.", android:"Приложение Android", iphone:"Приложение для iPhone", pc:"Приложение для ПК", install:"Установить SSSWET", hintAndroid:"Обнаружен Android. Используйте официальную версию Android или установите веб-приложение из этого браузера.", hintIphone:"Обнаружен iPhone. В Safari добавьте SSSWET на главный экран или откройте официальную веб-версию для iPhone.", hintPc:"Обнаружен компьютер. Скачайте официальное приложение для Windows, macOS или Linux.", note:"Только официальные версии. Доступность зависит от опубликованной сборки и совместимости устройства.", web:"Открыть веб-приложение" },
    uk: { heading:"Беріть SSSWET із собою", intro:"Встановіть офіційний застосунок для пристрою, яким ви користуєтеся.", android:"Застосунок Android", iphone:"Застосунок для iPhone", pc:"Застосунок для ПК", install:"Встановити SSSWET", hintAndroid:"Виявлено Android. Використовуйте офіційну версію Android або встановіть вебзастосунок із цього браузера.", hintIphone:"Виявлено iPhone. У Safari додайте SSSWET на початковий екран або відкрийте офіційну вебверсію для iPhone.", hintPc:"Виявлено комп’ютер. Завантажте офіційний застосунок для Windows, macOS або Linux.", note:"Лише офіційні версії. Доступність залежить від опублікованої збірки та сумісності пристрою.", web:"Відкрити вебзастосунок" },
    ar: { heading:"اصطحب SSSWET معك", intro:"ثبّت التطبيق الرسمي المناسب للجهاز الذي تستخدمه.", android:"تطبيق Android", iphone:"تطبيق iPhone", pc:"تطبيق الكمبيوتر", install:"تثبيت SSSWET", hintAndroid:"تم اكتشاف Android. استخدم إصدار Android الرسمي أو ثبّت تطبيق الويب من هذا المتصفح.", hintIphone:"تم اكتشاف iPhone. في Safari أضف SSSWET إلى الشاشة الرئيسية أو افتح تجربة الويب الرسمية لـ iPhone.", hintPc:"تم اكتشاف جهاز كمبيوتر. نزّل التطبيق الرسمي لنظام Windows أو macOS أو Linux.", note:"الإصدارات الرسمية فقط. يعتمد التوفر على الإصدار المنشور وتوافق الجهاز.", web:"فتح تطبيق الويب" },
    he: { heading:"קחו את SSSWET איתכם", intro:"התקינו את היישום הרשמי המתאים למכשיר שבו אתם משתמשים.", android:"יישום Android", iphone:"יישום iPhone", pc:"יישום למחשב", install:"התקנת SSSWET", hintAndroid:"זוהה Android. השתמשו בגרסה הרשמית או התקינו את יישום האינטרנט מהדפדפן הזה.", hintIphone:"זוהה iPhone. ב-Safari הוסיפו את SSSWET למסך הבית או פתחו את חוויית האינטרנט הרשמית ל-iPhone.", hintPc:"זוהה מחשב. הורידו את היישום הרשמי עבור Windows, macOS או Linux.", note:"גרסאות רשמיות בלבד. הזמינות תלויה בגרסה שפורסמה ובתאימות המכשיר.", web:"פתיחת יישום האינטרנט" },
    ja: { heading:"SSSWETを持ち歩く", intro:"使用している端末に対応する公式アプリをインストールしてください。", android:"Androidアプリ", iphone:"iPhoneアプリ", pc:"PCアプリ", install:"SSSWETをインストール", hintAndroid:"Androidを検出しました。公式Android版を使用するか、このブラウザからウェブアプリをインストールしてください。", hintIphone:"iPhoneを検出しました。SafariでSSSWETをホーム画面に追加するか、公式iPhoneウェブ版を開いてください。", hintPc:"コンピューターを検出しました。Windows、macOS、Linux用の公式アプリをダウンロードしてください。", note:"公式リリースのみ。利用可能かどうかは公開ビルドと端末の互換性によって決まります。", web:"ウェブアプリを開く" },
    ko: { heading:"SSSWET을 함께 사용하세요", intro:"사용 중인 기기에 맞는 공식 애플리케이션을 설치하세요.", android:"Android 애플리케이션", iphone:"iPhone 애플리케이션", pc:"PC 애플리케이션", install:"SSSWET 설치", hintAndroid:"Android가 감지되었습니다. 공식 Android 버전을 사용하거나 이 브라우저에서 웹 앱을 설치하세요.", hintIphone:"iPhone이 감지되었습니다. Safari에서 SSSWET을 홈 화면에 추가하거나 공식 iPhone 웹 버전을 여세요.", hintPc:"컴퓨터가 감지되었습니다. Windows, macOS 또는 Linux용 공식 애플리케이션을 다운로드하세요.", note:"공식 릴리스만 제공합니다. 사용 가능 여부는 게시된 빌드와 기기 호환성에 따라 달라집니다.", web:"웹 애플리케이션 열기" }
  };

  const t = () => dictionaries[language()] || dictionaries.en;
  const ua = navigator.userAgent || "";
  const platform = /android/i.test(ua) ? "android" : /iphone|ipad|ipod/i.test(ua) ? "iphone" : "pc";

  function apply() {
    const words = t();
    const mobileUrl = mobile?.href || "https://github.com/gudjencio/SSSWET/releases";
    if (heading) heading.textContent = words.heading;
    if (intro) intro.textContent = words.intro;
    if (eyebrow) eyebrow.textContent = "SSSWET · APPLICATIONS";
    if (note) note.textContent = words.note;
    if (install) install.textContent = words.install;

    panel.querySelectorAll(".ssswet-platform-option").forEach(el => el.remove());
    if (mobile) {
      mobile.classList.add("ssswet-platform-option");
      mobile.textContent = platform === "android" ? words.android : words.iphone;
      mobile.hidden = false;
      mobile.setAttribute("aria-label", mobile.textContent);
    }
    if (desktop) {
      desktop.classList.add("ssswet-platform-option");
      desktop.textContent = words.pc;
      desktop.hidden = false;
      desktop.setAttribute("aria-label", desktop.textContent);
    }

    if (platform === "iphone" && mobile) {
      mobile.href = mobileUrl;
      mobile.setAttribute("data-platform", "iphone");
    } else if (mobile) {
      mobile.href = "https://github.com/gudjencio/SSSWET/releases";
      mobile.setAttribute("data-platform", "android");
    }

    if (hint) hint.textContent = platform === "android" ? words.hintAndroid : platform === "iphone" ? words.hintIphone : words.hintPc;
    panel.dataset.platform = platform;
    panel.dataset.language = language();
  }

  document.addEventListener("DOMContentLoaded", apply, { once: true });
  document.getElementById("language")?.addEventListener("change", apply);
  window.addEventListener("ssswet-language-changed", apply);
  apply();
})();
