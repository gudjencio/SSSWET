(() => {
  "use strict";

  const root = document.getElementById("vt-keyframe-results");
  if (!root) return;

  const copy = {
    en: { label: "Local visual correspondences", matched: "candidate matches", note: "Screening heuristic only; matches are not camera poses, tracked features, or proof of 3D overlap." },
    fr: { label: "Correspondances visuelles locales", matched: "correspondances candidates", note: "Heuristique de présélection uniquement ; ces correspondances ne sont ni des poses caméra, ni des points suivis, ni une preuve de recouvrement 3D." },
    es: { label: "Correspondencias visuales locales", matched: "correspondencias candidatas", note: "Solo es una heurística de selección; no representa poses de cámara, puntos rastreados ni prueba de solapamiento 3D." },
    de: { label: "Lokale visuelle Übereinstimmungen", matched: "Kandidatenübereinstimmungen", note: "Nur eine Auswahlheuristik; keine Kameraposen, verfolgten Merkmale oder ein Nachweis der 3D-Überlappung." },
    it: { label: "Corrispondenze visive locali", matched: "corrispondenze candidate", note: "Solo un'euristica di preselezione; non rappresenta pose della fotocamera, punti tracciati o prova di sovrapposizione 3D." },
    pt: { label: "Correspondências visuais locais", matched: "correspondências candidatas", note: "Apenas uma heurística de seleção; não representa poses de câmera, pontos rastreados nem prova de sobreposição 3D." },
    nl: { label: "Lokale visuele overeenkomsten", matched: "kandidaat-overeenkomsten", note: "Alleen een selectieheuristiek; geen cameraposities, gevolgde kenmerken of bewijs van 3D-overlap." },
    ru: { label: "Локальные визуальные соответствия", matched: "кандидатных соответствий", note: "Только эвристика отбора; это не положения камеры, не отслеженные признаки и не доказательство 3D-перекрытия." },
    uk: { label: "Локальні візуальні відповідності", matched: "кандидатних відповідностей", note: "Лише евристика відбору; це не положення камери, не відстежені ознаки й не доказ 3D-перекриття." },
    ar: { label: "المطابقات البصرية المحلية", matched: "مطابقات مرشحة", note: "هذه إرشادية للاختيار فقط؛ ولا تمثل وضعيات الكاميرا أو النقاط المتتبعة أو إثبات التداخل ثلاثي الأبعاد." },
    he: { label: "התאמות חזותיות מקומיות", matched: "התאמות מועמדות", note: "זהו מדד סינון בלבד; הוא אינו מייצג תנוחות מצלמה, נקודות במעקב או הוכחת חפיפה תלת־ממדית." },
    ja: { label: "局所的な視覚対応", matched: "候補対応", note: "これは選別用ヒューリスティックであり、カメラ姿勢、追跡特徴、3D重複の証明を示すものではありません。" },
    ko: { label: "로컬 시각 대응", matched: "후보 대응", note: "선별용 휴리스틱일 뿐이며 카메라 자세, 추적 특징 또는 3D 중첩을 증명하지 않습니다." },
    zh: { label: "局部视觉对应", matched: "候选对应", note: "这只是筛选启发式指标，不代表相机姿态、跟踪特征，也不能证明三维重叠。" },
    hi: { label: "स्थानीय दृश्य मिलान", matched: "उम्मीदवार मिलान", note: "यह केवल चयन ह्यूरिस्टिक है; यह कैमरा पोज़, ट्रैक किए गए फीचर या 3D ओवरलैप का प्रमाण नहीं है।" }
  };

  const language = () => {
    const selected = document.getElementById("vt-language");
    return copy[selected?.value] ? selected.value : "en";
  };

  const patchDescriptors = img => {
    if (!img.complete || !img.naturalWidth || !img.naturalHeight) return [];
    const canvas = document.createElement("canvas");
    canvas.width = 128; canvas.height = 96;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    if (!ctx) return [];
    try { ctx.drawImage(img, 0, 0, 128, 96); } catch (_) { return []; }
    let data;
    try { data = ctx.getImageData(0, 0, 128, 96).data; } catch (_) { return []; }
    const descriptors = [];
    for (let y = 8; y < 88; y += 12) for (let x = 8; x < 120; x += 12) {
      const values = [];
      for (let dy = -4; dy <= 4; dy += 2) for (let dx = -4; dx <= 4; dx += 2) {
        const p = ((y + dy) * 128 + (x + dx)) * 4;
        values.push((0.2126 * data[p] + 0.7152 * data[p + 1] + 0.0722 * data[p + 2]) / 255);
      }
      const mean = values.reduce((a, b) => a + b, 0) / values.length;
      let norm = 0;
      for (const value of values) norm += (value - mean) ** 2;
      norm = Math.sqrt(norm) || 1;
      descriptors.push(values.map(value => (value - mean) / norm));
    }
    return descriptors;
  };

  const distance = (a, b) => {
    let sum = 0;
    for (let i = 0; i < a.length; i += 1) sum += (a[i] - b[i]) ** 2;
    return Math.sqrt(sum / a.length);
  };

  const correspondenceCount = (a, b) => {
    if (!a.length || !b.length) return 0;
    let matches = 0;
    for (const descriptor of a) {
      let best = Infinity, second = Infinity;
      for (const candidate of b) {
        const d = distance(descriptor, candidate);
        if (d < best) { second = best; best = d; }
        else if (d < second) second = d;
      }
      if (best < 0.72 && best / Math.max(second, 1e-6) < 0.82) matches += 1;
    }
    return matches;
  };

  let timer = 0;
  const render = () => {
    timer = 0;
    const images = [...root.querySelectorAll(".vt-keyframe-card img")];
    if (images.length < 2) return;
    const descriptors = images.map(patchDescriptors);
    const text = copy[language()];
    root.querySelectorAll(".vt-keyframe-correspondence, .vt-keyframe-correspondence-note").forEach(node => node.remove());
    for (let i = 1; i < images.length; i += 1) {
      const count = correspondenceCount(descriptors[i - 1], descriptors[i]);
      const card = images[i].closest(".vt-keyframe-card");
      if (!card) continue;
      const metric = document.createElement("div");
      metric.className = "vt-keyframe-correspondence";
      metric.setAttribute("role", "note");
      metric.innerHTML = `<strong>${text.label}</strong><span>${count}</span><small>${text.matched}</small>`;
      card.appendChild(metric);
    }
    const note = document.createElement("p");
    note.className = "vt-keyframe-correspondence-note";
    note.textContent = text.note;
    root.appendChild(note);
  };

  const schedule = () => { if (!timer) timer = requestAnimationFrame(render); };
  new MutationObserver(schedule).observe(root, { childList: true, subtree: true });
  document.getElementById("vt-language")?.addEventListener("change", schedule);
  schedule();
})();
