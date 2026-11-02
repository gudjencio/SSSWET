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
  const isStandalone = window.matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;

  if (mobile) {
    panel.dataset.platform = "mobile";
    desktopLink.hidden = true;
    mobileLink.hidden = false;
    installButton.hidden = false;
    if (isStandalone) {
      installButton.textContent = "SSSWET is installed";
      installButton.disabled = true;
      copy("The SSSWET application is already installed on this device.");
    } else if (isIOS) {
      installButton.textContent = "Add SSSWET to your Home Screen";
      copy("In Safari, tap Share, then choose “Add to Home Screen”.");
    } else {
      installButton.textContent = "Install SSSWET";
      copy("Install the mobile app from this browser, or download the Android package from official releases.");
    }
  } else {
    panel.dataset.platform = "desktop";
    mobileLink.hidden = true;
    desktopLink.hidden = false;
    installButton.hidden = true;
    copy("Download the desktop application for Windows, macOS or Linux from official releases.");
  }

  window.addEventListener("beforeinstallprompt", event => {
    event.preventDefault();
    installPrompt = event;
    if (mobile && installButton && !isStandalone) installButton.hidden = false;
  });
  installButton?.addEventListener("click", async () => {
    if (isIOS) {
      copy("Open the Share menu in Safari, then select “Add to Home Screen”.");
      return;
    }
    if (!installPrompt) {
      copy("If installation is not offered, open the browser menu and choose “Install app” or “Add to Home Screen”.");
      return;
    }
    installPrompt.prompt();
    await installPrompt.userChoice;
    installPrompt = null;
  });
  window.addEventListener("appinstalled", () => {
    installButton.textContent = "SSSWET is installed";
    installButton.disabled = true;
    copy("The SSSWET application has been installed.");
  });
})();