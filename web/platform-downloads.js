(() => {
  "use strict";
  const panel = document.getElementById("platform-downloads");
  if (!panel) return;
  const installButton = document.getElementById("ssswet-install-app");
  const desktopLink = document.getElementById("ssswet-desktop-download");
  const mobileLink = document.getElementById("ssswet-mobile-download");
  const hint = document.getElementById("ssswet-install-hint");
  const mobile = window.matchMedia("(max-width: 760px), (pointer: coarse)").matches;
  let installPrompt = null;
  const copy = message => { if (hint) hint.textContent = message; };
  const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
  const french = (document.documentElement.lang || "").toLowerCase().startsWith("fr");
  const labels = french ? {
    heading: "Emportez SSSWET partout",
    intro: "Installez l’application mobile ou téléchargez le logiciel officiel pour ordinateur.",
    install: "Installer SSSWET",
    addHome: "Ajouter SSSWET à l’écran d’accueil",
    desktop: "Télécharger le logiciel pour ordinateur",
    mobileRelease: "Application Android · téléchargements",
    installed: "SSSWET est installé",
    already: "L’application SSSWET est déjà installée sur cet appareil.",
    safari: "Dans Safari, touchez Partager, puis « Sur l’écran d’accueil ».",
    browser: "Installez l’application depuis ce navigateur ou téléchargez le paquet Android depuis les versions officielles.",
    desktopHint: "Téléchargez l’application pour Windows, macOS ou Linux depuis les versions officielles.",
    menu: "Si l’installation n’est pas proposée, ouvrez le menu du navigateur et choisissez « Installer l’application » ou « Ajouter à l’écran d’accueil ».",
    done: "L’application SSSWET a été installée."
  } : {
    heading: "Take SSSWET with you",
    intro: "Install the mobile experience or download the official desktop application.",
    install: "Install SSSWET",
    addHome: "Add SSSWET to your Home Screen",
    desktop: "Download desktop application",
    mobileRelease: "Android application · releases",
    installed: "SSSWET is installed",
    already: "The SSSWET application is already installed on this device.",
    safari: "In Safari, tap Share, then choose “Add to Home Screen”.",
    browser: "Install the mobile app from this browser, or download the Android package from official releases.",
    desktopHint: "Download the desktop application for Windows, macOS or Linux from official releases.",
    menu: "If installation is not offered, open the browser menu and choose “Install app” or “Add to Home Screen”.",
    done: "The SSSWET application has been installed."
  };
  const heading = document.getElementById("platform-downloads-title");
  const intro = panel.querySelector(".platform-downloads-copy > p:not(.eyebrow)");
  if (heading) heading.textContent = labels.heading;
  if (intro) intro.textContent = labels.intro;
  installButton.textContent = labels.install;
  mobileLink.textContent = labels.mobileRelease;
  desktopLink.textContent = labels.desktop;
  const isStandalone = window.matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;

  if (mobile) {
    panel.dataset.platform = "mobile";
    desktopLink.hidden = true;
    mobileLink.hidden = false;
    installButton.hidden = false;
    if (isStandalone) {
      installButton.textContent = labels.installed;
      installButton.disabled = true;
      copy(labels.already);
    } else if (isIOS) {
      installButton.textContent = labels.addHome;
      copy(labels.safari);
    } else {
      installButton.textContent = labels.install;
      copy(labels.browser);
    }
  } else {
    panel.dataset.platform = "desktop";
    mobileLink.hidden = true;
    desktopLink.hidden = false;
    installButton.hidden = true;
    copy(labels.desktopHint);
  }

  window.addEventListener("beforeinstallprompt", event => {
    event.preventDefault();
    installPrompt = event;
    if (mobile && installButton && !isStandalone) installButton.hidden = false;
  });
  installButton?.addEventListener("click", async () => {
    if (isIOS) {
      copy(labels.safari);
      return;
    }
    if (!installPrompt) {
      copy(labels.menu);
      return;
    }
    installPrompt.prompt();
    await installPrompt.userChoice;
    installPrompt = null;
  });
  window.addEventListener("appinstalled", () => {
    installButton.textContent = labels.installed;
    installButton.disabled = true;
    copy(labels.done);
  });
})();