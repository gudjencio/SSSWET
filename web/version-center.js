(() => {
  "use strict";

  const root = document.getElementById("version-center");
  if (!root) return;

  const status = document.getElementById("version-center-status");
  const current = document.getElementById("version-center-current");
  const history = document.getElementById("version-center-history");
  const integrity = document.getElementById("version-center-integrity");
  const languageSelect = document.getElementById("language");
  const api = "https://api.github.com/repos/gudjencio/SSSWET";
  const releasesUrl = api + "/releases?per_page=8";
  const french = () => (languageSelect?.value || document.documentElement.lang || navigator.language || "en").toLowerCase().startsWith("fr");

  const words = () => french() ? {
    loading: "Vérification des versions officielles…",
    none: "Aucune version officielle n’a encore été publiée. L’interface web reste accessible et installable sur les appareils compatibles.",
    current: "Dernière version officielle",
    prerelease: "Version de prévisualisation",
    stable: "Version publiée",
    published: "Publiée le",
    assets: "Fichiers disponibles",
    download: "Télécharger",
    checksums: "Sommes de contrôle SHA-256",
    noChecksum: "Aucun fichier SHA256SUMS n’est joint à cette version.",
    history: "Versions précédentes",
    failed: "Les informations de version ne sont pas accessibles pour le moment. Réessaie ultérieurement ou consulte les publications officielles.",
    integrity: "Les sommes de contrôle SHA-256 permettent de comparer les fichiers téléchargés. Elles ne remplacent pas la signature de code ni la vérification de l’éditeur.",
    releaseNotes: "Notes de version",
    noAssets: "Aucun installateur n’est joint à cette publication.",
    draft: "Brouillon exclu"
  } : {
    loading: "Checking official releases…",
    none: "No official release has been published yet. The web interface remains available and installable on supported devices.",
    current: "Latest official release",
    prerelease: "Preview release",
    stable: "Published release",
    published: "Published",
    assets: "Available files",
    download: "Download",
    checksums: "SHA-256 checksums",
    noChecksum: "No SHA256SUMS file is attached to this release.",
    history: "Earlier releases",
    failed: "Release information is temporarily unavailable. Please try again later or visit the official releases page.",
    integrity: "SHA-256 checksums help compare downloaded files. They do not replace code signing or publisher verification.",
    releaseNotes: "Release notes",
    noAssets: "No installer is attached to this release.",
    draft: "Draft excluded"
  };

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function safeDate(value) {
    if (!value) return "";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";
    return new Intl.DateTimeFormat(french() ? "fr-FR" : "en-GB", { dateStyle: "medium" }).format(date);
  }

  function externalLink(url, label) {
    if (!url || !/^https:\/\/github\.com\/gudjencio\/SSSWET\//i.test(url)) return null;
    const link = element("a", "", label);
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    return link;
  }

  function renderRelease(release, featured) {
    const w = words();
    const card = element("article", "version-release-card");
    const title = element("h3", "", release.name || release.tag_name || "SSSWET");
    card.append(title);
    const description = element("p", "", featured ? w.current : (release.name || release.tag_name || ""));
    if (featured) card.append(description);
    const meta = element("div", "version-release-meta");
    meta.append(element("span", "", release.prerelease ? w.prerelease : w.stable));
    const date = safeDate(release.published_at);
    if (date) meta.append(element("span", "", w.published + " · " + date));
    if (release.tag_name) meta.append(element("span", "", release.tag_name));
    card.append(meta);

    const assets = Array.isArray(release.assets) ? release.assets : [];
    const checksum = assets.find(asset => /^SHA256SUMS\.txt$/i.test(asset.name));
    if (assets.length) {
      card.append(element("p", "", w.assets));
      const links = element("div", "version-release-links");
      for (const asset of assets) {
        const link = externalLink(asset.browser_download_url, w.download + " · " + asset.name);
        if (link) links.append(link);
      }
      if (links.childElementCount) card.append(links);
    } else {
      card.append(element("p", "", w.noAssets));
    }

    const footer = element("div", "version-release-links");
    const notes = externalLink(release.html_url, w.releaseNotes);
    if (notes) footer.append(notes);
    if (checksum) {
      const checksumLink = externalLink(checksum.browser_download_url, w.checksums);
      if (checksumLink) footer.append(checksumLink);
    }
    if (footer.childElementCount) card.append(footer);
    return { card, checksum: Boolean(checksum), assets: assets.length };
  }

  async function load() {
    const w = words();
    status.dataset.state = "loading";
    status.textContent = w.loading;
    current.replaceChildren();
    history.replaceChildren();
    integrity.textContent = w.integrity;
    try {
      const response = await fetch(releasesUrl, {
        headers: { Accept: "application/vnd.github+json" },
        cache: "no-store"
      });
      if (!response.ok) throw new Error("GitHub Releases HTTP " + response.status);
      const releases = await response.json();
      const published = Array.isArray(releases) ? releases.filter(item => !item.draft && item.published_at) : [];
      if (!published.length) {
        status.dataset.state = "empty";
        status.textContent = w.none;
        integrity.textContent = w.integrity + " " + w.noChecksum;
        return;
      }

      const latest = published[0];
      const featured = renderRelease(latest, true);
      current.append(featured.card);
      status.dataset.state = "available";
      status.textContent = w.current + " · " + (latest.tag_name || latest.name || "SSSWET");
      if (!featured.checksum) integrity.textContent = w.integrity + " " + w.noChecksum;

      const previous = published.slice(1);
      if (previous.length) {
        history.append(element("p", "version-center-integrity", w.history));
        for (const release of previous) {
          const row = element("div", "version-history-item");
          const link = externalLink(release.html_url, release.name || release.tag_name || "SSSWET");
          if (link) row.append(link);
          row.append(element("time", "", safeDate(release.published_at)));
          history.append(row);
        }
      }
    } catch (error) {
      status.dataset.state = "error";
      status.textContent = w.failed;
      integrity.textContent = w.integrity;
    }
  }

  load();
  languageSelect?.addEventListener("change", load);
  window.addEventListener("online", load);
})();