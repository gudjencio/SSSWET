(() => {
  "use strict";

  const root = document.getElementById("vt-keyframe-results");
  if (!root) return;

  const copy = {
    en: { label: "Local visual correspondences", matched: "candidate matches", distribution: "spatial distribution", note: "Screening heuristic only; matches are not camera poses, tracked features, or proof of 3D overlap.", displacement: "median shift", spread: "median spread", displacementNote: "Displacement consistency is a local image-grid heuristic, not optical flow, camera motion, geometric verification, or 3D evidence." },
    fr: { label: "Correspondances visuelles locales", matched: "correspondances candidates", distribution: "distribution spatiale", note: "Heuristique de présélection uniquement ; ces correspondances ne sont ni des poses caméra, ni des points suivis, ni une preuve de recouvrement 3D.", displacement: "déplacement médian", spread: "dispersion médiane", displacementNote: "La cohérence du déplacement est une heuristique sur une grille d’image ; ce n’est ni un flux optique, ni un mouvement de caméra, ni une vérification géométrique ou une preuve 3D." },
    es: { label: "Correspondencias visuales locales", matched: "correspondencias candidatas", distribution: "distribución espacial", note: "Solo es una heurística de selección; no representa poses de cámara, puntos rastreados ni prueba de solapamiento 3D.", displacement: "desplazamiento mediano", spread: "dispersión mediana", displacementNote: "La coherencia del desplazamiento es una heurística de cuadrícula de imagen; no es flujo óptico, movimiento de cámara, verificación geométrica ni evidencia 3D." },
    de: { label: "Lokale visuelle Übereinstimmungen", matched: "Kandidatenübereinstimmungen", distribution: "räumliche Verteilung", note: "Nur eine Auswahlheuristik; keine Kameraposen, verfolgten Merkmale oder ein Nachweis der 3D-Überlappung.", displacement: "mittlere Verschiebung", spread: "mittlere Streuung", displacementNote: "Die Verschiebungskonsistenz ist eine Bildraster-Heuristik, kein optischer Fluss, keine Kamerabewegung, keine geometrische Prüfung und kein 3D-Nachweis." },
    it: { label: "Corrispondenze visive locali", matched: "corrispondenze candidate", distribution: "distribuzione spaziale", note: "Solo un'euristica di preselezione; non rappresenta pose della fotocamera, punti tracciati o prova di sovrapposizione 3D.", displacement: "spostamento mediano", spread: "dispersione mediana", displacementNote: "La coerenza dello spostamento è un’euristica su griglia d’immagine, non flusso ottico, movimento della fotocamera, verifica geometrica o prova 3D." },
    pt: { label: "Correspondências visuais locais", matched: "correspondências candidatas", distribution: "distribuição espacial", note: "Apenas uma heurística de seleção; não representa poses de câmera, pontos rastreados nem prova de sobreposição 3D.", displacement: "deslocamento mediano", spread: "dispersão mediana", displacementNote: "A consistência do deslocamento é uma heurística de grade de imagem, não fluxo óptico, movimento da câmera, verificação geométrica ou evidência 3D." },
    nl: { label: "Lokale visuele overeenkomsten", matched: "kandidaat-overeenkomsten", distribution: "ruimtelijke spreiding", note: "Alleen een selectieheuristiek; geen cameraposities, gevolgde kenmerken of bewijs van 3D-overlap.", displacement: "mediane verplaatsing", spread: "mediane spreiding", displacementNote: "Verplaatsingsconsistentie is een beeldrasterheuristiek, geen optische stroom, camerabeweging, geometrische verificatie of 3D-bewijs." },
    ru: { label: "Локальные визуальные соответствия", matched: "кандидатных соответствий", distribution: "пространственное распределение", note: "Только эвристика отбора; это не положения камеры, не отслеженные признаки и не доказательство 3D-перекрытия.", displacement: "медианное смещение", spread: "медианный разброс", displacementNote: "Согласованность смещения — эвристика по сетке изображения, а не оптический поток, движение камеры, геометрическая проверка или доказательство 3D." },
    uk: { label: "Локальні візуальні відповідності", matched: "кандидатних відповідностей", distribution: "просторовий розподіл", note: "Лише евристика відбору; це не положення камери, не відстежені ознаки й не доказ 3D-перекриття.", displacement: "медіанне зміщення", spread: "медіанний розкид", displacementNote: "Узгодженість зміщення — це евристика сітки зображення, а не оптичний потік, рух камери, геометрична перевірка чи доказ 3D." },
    ar: { label: "المطابقات البصرية المحلية", matched: "مطابقات مرشحة", distribution: "التوزيع المكاني", note: "هذه إرشادية للاختيار فقط؛ ولا تمثل وضعيات الكاميرا أو النقاط المتتبعة أو إثبات التداخل ثلاثي الأبعاد.", displacement: "الإزاحة الوسيطة", spread: "التشتت الوسيط", displacementNote: "اتساق الإزاحة مجرد مؤشر استدلالي على شبكة الصورة، وليس تدفقًا بصريًا أو حركة كاميرا أو تحققًا هندسيًا أو دليلًا ثلاثي الأبعاد." },
    he: { label: "התאמות חזותיות מקומיות", matched: "התאמות מועמדות", distribution: "פיזור מרחבי", note: "זהו מדד סינון בלבד; הוא אינו מייצג תנוחות מצלמה, נקודות במעקב או הוכחת חפיפה תלת־ממדית.", displacement: "הסטה חציונית", spread: "פיזור חציוני", displacementNote: "עקביות ההסטה היא היוריסטיקה של רשת תמונה, ולא זרימה אופטית, תנועת מצלמה, אימות גאומטרי או ראיית תלת־ממד." },
    ja: { label: "局所的な視覚対応", matched: "候補対応", distribution: "空間分布", note: "これは選別用ヒューリスティックであり、カメラ姿勢、追跡特徴、3D重複の証明を示すものではありません。", displacement: "中央値の移動", spread: "中央値のばらつき", displacementNote: "移動の一貫性は画像グリッド上のヒューリスティックであり、オプティカルフロー、カメラ移動、幾何学的検証、3Dの証拠ではありません。" },
    ko: { label: "로컬 시각 대응", matched: "후보 대응", distribution: "공간 분포", note: "선별용 휴리스틱일 뿐이며 카메라 자세, 추적 특징 또는 3D 중첩을 증명하지 않습니다.", displacement: "중앙값 이동", spread: "중앙값 분산", displacementNote: "이동 일관성은 이미지 격자 기반 휴리스틱이며 광학 흐름, 카메라 움직임, 기하학적 검증 또는 3D 증거가 아닙니다." },
    zh: { label: "局部视觉对应", matched: "候选对应", distribution: "空间分布", note: "这只是筛选启发式指标，不代表相机姿态、跟踪特征，也不能证明三维重叠。", displacement: "中位位移", spread: "中位离散度", displacementNote: "位移一致性只是图像网格启发式指标，并非光流、相机运动、几何验证或三维证据。" },
    hi: { label: "स्थानीय दृश्य मिलान", matched: "उम्मीदवार मिलान", distribution: "स्थानिक वितरण", note: "यह केवल चयन ह्यूरिस्टिक है; यह कैमरा पोज़, ट्रैक किए गए फीचर या 3D ओवरलैप का प्रमाण नहीं है।", displacement: "माध्यिका विस्थापन", spread: "माध्यिका फैलाव", displacementNote: "विस्थापन संगति केवल छवि-ग्रिड ह्यूरिस्टिक है; यह ऑप्टिकल फ्लो, कैमरा गति, ज्यामितीय सत्यापन या 3D प्रमाण नहीं है。" }
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

  const median = values => {
    if (!values.length) return 0;
    const sorted = values.slice().sort((a, b) => a - b);
    const middle = Math.floor(sorted.length / 2);
    return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
  };

  const correspondenceDistribution = (a, b) => {
    if (!a.length || !b.length) return { count: 0, coverage: 0, dx: 0, dy: 0, spread: 0 };
    const occupiedA = new Set();
    const occupiedB = new Set();
    const shifts = [];
    for (let i = 0; i < a.length; i += 1) {
      let best = Infinity, second = Infinity, bestIndex = -1;
      for (let j = 0; j < b.length; j += 1) {
        const d = distance(a[i], b[j]);
        if (d < best) { second = best; best = d; bestIndex = j; }
        else if (d < second) second = d;
      }
      if (best >= 0.72 || best / Math.max(second, 1e-6) >= 0.82 || bestIndex < 0) continue;
      const ax = i % 10, ay = Math.floor(i / 10);
      const bx = bestIndex % 10, by = Math.floor(bestIndex / 10);
      occupiedA.add(`${Math.min(3, Math.floor(ax / 3))}:${Math.min(3, Math.floor(ay / 2))}`);
      occupiedB.add(`${Math.min(3, Math.floor(bx / 3))}:${Math.min(3, Math.floor(by / 2))}`);
      shifts.push({ dx: bx - ax, dy: by - ay });
    }
    const dx = median(shifts.map(item => item.dx));
    const dy = median(shifts.map(item => item.dy));
    const spread = median(shifts.map(item => Math.hypot(item.dx - dx, item.dy - dy)));
    const coverageA = occupiedA.size / 16;
    const coverageB = occupiedB.size / 16;
    return { count: shifts.length, coverage: Math.round(((coverageA + coverageB) / 2) * 100), dx, dy, spread };
  };

  let timer = 0;
  const render = () => {
    timer = 0;
    const images = [...root.querySelectorAll(".vt-keyframe-card img")];
    if (images.length < 2) return;
    const descriptors = images.map(patchDescriptors);
    const text = copy[language()];
    root.querySelectorAll(".vt-keyframe-correspondence, .vt-keyframe-correspondence-note, .vt-keyframe-displacement-note").forEach(node => node.remove());
    for (let i = 1; i < images.length; i += 1) {
      const result = correspondenceDistribution(descriptors[i - 1], descriptors[i]);
      const card = images[i].closest(".vt-keyframe-card");
      if (!card) continue;
      const metric = document.createElement("div");
      metric.className = "vt-keyframe-correspondence";
      metric.setAttribute("role", "note");
      metric.innerHTML = `<strong>${text.label}</strong><span>${result.count}</span><small>${text.matched}</small><small>${text.distribution}: ${result.coverage}%</small><small>${text.displacement}: (${result.dx.toFixed(1)}, ${result.dy.toFixed(1)}) grid cells</small><small>${text.spread}: ${result.spread.toFixed(2)} grid cells</small>`;
      card.appendChild(metric);
    }
    const note = document.createElement("p");
    note.className = "vt-keyframe-correspondence-note";
    note.textContent = text.note;
    root.appendChild(note);
    const displacementNote = document.createElement("p");
    displacementNote.className = "vt-keyframe-displacement-note";
    displacementNote.textContent = text.displacementNote;
    root.appendChild(displacementNote);
  };

  const schedule = () => { if (!timer) timer = requestAnimationFrame(render); };
  new MutationObserver(schedule).observe(root, { childList: true, subtree: true });
  document.getElementById("vt-language")?.addEventListener("change", schedule);
  schedule();
})();
