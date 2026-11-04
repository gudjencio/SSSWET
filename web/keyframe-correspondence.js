(() => {
  "use strict";

  const root = document.getElementById("vt-keyframe-results");
  const copy = {
    en: { label: "Local visual correspondences", matched: "mutual matches", distribution: "spatial distribution", note: "Screening heuristic only; matches are not camera poses, tracked features, or proof of 3D overlap.", displacement: "median shift", spread: "median spread", displacementNote: "Displacement consistency is a local image-grid heuristic, not optical flow, camera motion, geometric verification, or 3D evidence." , forward: "forward candidates", descriptorDistance: "median descriptor distance", ratio: "median best/second ratio", diagnosticNote: "Descriptor distance and best/second ratio describe this matcher only; neither is calibrated confidence nor a probability of a correct match.", notAvailable: "—", mutualNote: "A pair is counted only when each patch selects the other as its best match and both directional ratio tests pass; this is not geometric verification."},
    fr: { label: "Correspondances visuelles locales", matched: "correspondances réciproques", distribution: "distribution spatiale", note: "Heuristique de présélection uniquement ; ces correspondances ne sont ni des poses caméra, ni des points suivis, ni une preuve de recouvrement 3D.", displacement: "déplacement médian", spread: "dispersion médiane", displacementNote: "La cohérence du déplacement est une heuristique sur une grille d’image ; ce n’est ni un flux optique, ni un mouvement de caméra, ni une vérification géométrique ou une preuve 3D." , forward: "candidats dans le sens direct", descriptorDistance: "distance médiane des descripteurs", ratio: "rapport médian meilleur/deuxième", diagnosticNote: "La distance des descripteurs et le rapport meilleur/deuxième décrivent uniquement cet appariement ; aucun des deux n’est une confiance calibrée ni une probabilité de correspondance correcte.", notAvailable: "—", mutualNote: "Une paire n’est comptée que si chaque patch désigne l’autre comme meilleur appariement et si les deux tests de ratio réussissent ; cela ne constitue pas une vérification géométrique."},
    es: { label: "Correspondencias visuales locales", matched: "coincidencias mutuas", distribution: "distribución espacial", note: "Solo es una heurística de selección; no representa poses de cámara, puntos rastreados ni prueba de solapamiento 3D.", displacement: "desplazamiento mediano", spread: "dispersión mediana", displacementNote: "La coherencia del desplazamiento es una heurística de cuadrícula de imagen; no es flujo óptico, movimiento de cámara, verificación geométrica ni evidencia 3D." , forward: "candidatos directos", descriptorDistance: "distancia mediana del descriptor", ratio: "relación mediana mejor/segundo", diagnosticNote: "La distancia del descriptor y la relación mejor/segundo describen únicamente este método; ninguna es una confianza calibrada ni una probabilidad de acierto.", notAvailable: "—", mutualNote: "Una pareja solo se cuenta si cada parche elige al otro como su mejor coincidencia y ambas pruebas de razón se superan; esto no es una verificación geométrica."},
    de: { label: "Lokale visuelle Übereinstimmungen", matched: "gegenseitige Treffer", distribution: "räumliche Verteilung", note: "Nur eine Auswahlheuristik; keine Kameraposen, verfolgten Merkmale oder ein Nachweis der 3D-Überlappung.", displacement: "mittlere Verschiebung", spread: "mittlere Streuung", displacementNote: "Die Verschiebungskonsistenz ist eine Bildraster-Heuristik, kein optischer Fluss, keine Kamerabewegung, keine geometrische Prüfung und kein 3D-Nachweis." , forward: "Vorwärtskandidaten", descriptorDistance: "mediane Deskriptor-Distanz", ratio: "mediales Best-/Zweitbest-Verhältnis", diagnosticNote: "Deskriptor-Distanz und Best-/Zweitbest-Verhältnis beschreiben nur diesen Matcher; sie sind weder kalibrierte Konfidenz noch eine Wahrscheinlichkeit für eine korrekte Zuordnung.", notAvailable: "—", mutualNote: "Ein Paar zählt nur, wenn jedes Patch das andere als besten Treffer auswählt und beide Richtungs-Quotiententests bestehen; dies ist keine geometrische Verifikation."},
    it: { label: "Corrispondenze visive locali", matched: "corrispondenze reciproche", distribution: "distribuzione spaziale", note: "Solo un'euristica di preselezione; non rappresenta pose della fotocamera, punti tracciati o prova di sovrapposizione 3D.", displacement: "spostamento mediano", spread: "dispersione mediana", displacementNote: "La coerenza dello spostamento è un’euristica su griglia d’immagine, non flusso ottico, movimento della fotocamera, verifica geometrica o prova 3D." , forward: "candidati diretti", descriptorDistance: "distanza mediana dei descrittori", ratio: "rapporto mediano migliore/secondo", diagnosticNote: "La distanza dei descrittori e il rapporto migliore/secondo descrivono solo questo metodo; non sono una confidenza calibrata né una probabilità di corrispondenza corretta.", notAvailable: "—", mutualNote: "Una coppia viene conteggiata solo se ciascuna patch sceglie l’altra come migliore corrispondenza e supera entrambi i test di rapporto; non è una verifica geometrica."},
    pt: { label: "Correspondências visuais locais", matched: "correspondências recíprocas", distribution: "distribuição espacial", note: "Apenas uma heurística de seleção; não representa poses de câmera, pontos rastreados nem prova de sobreposição 3D.", displacement: "deslocamento mediano", spread: "dispersão mediana", displacementNote: "A consistência do deslocamento é uma heurística de grade de imagem, não fluxo óptico, movimento da câmera, verificação geométrica ou evidência 3D." , forward: "candidatos diretos", descriptorDistance: "distância mediana do descritor", ratio: "razão mediana melhor/segundo", diagnosticNote: "A distância do descritor e a razão melhor/segundo descrevem apenas este método; não são confiança calibrada nem probabilidade de correspondência correta.", notAvailable: "—", mutualNote: "Um par só é contado quando cada bloco escolhe o outro como melhor correspondência e ambos os testes de razão são aprovados; isso não é verificação geométrica."},
    nl: { label: "Lokale visuele overeenkomsten", matched: "wederzijdse overeenkomsten", distribution: "ruimtelijke spreiding", note: "Alleen een selectieheuristiek; geen cameraposities, gevolgde kenmerken of bewijs van 3D-overlap.", displacement: "mediane verplaatsing", spread: "mediane spreiding", displacementNote: "Verplaatsingsconsistentie is een beeldrasterheuristiek, geen optische stroom, camerabeweging, geometrische verificatie of 3D-bewijs." , forward: "voorwaartse kandidaten", descriptorDistance: "mediane descriptorafstand", ratio: "mediane beste/tweede-verhouding", diagnosticNote: "Descriptorafstand en beste/tweede-verhouding beschrijven alleen deze matcher; ze zijn geen gekalibreerde betrouwbaarheid of kans op een juiste overeenkomst.", notAvailable: "—", mutualNote: "Een paar telt alleen als elk patch het andere als beste overeenkomst kiest en beide richtingsgebonden ratiotests doorstaat; dit is geen geometrische verificatie."},
    ru: { label: "Локальные визуальные соответствия", matched: "взаимные соответствия", distribution: "пространственное распределение", note: "Только эвристика отбора; это не положения камеры, не отслеженные признаки и не доказательство 3D-перекрытия.", displacement: "медианное смещение", spread: "медианный разброс", displacementNote: "Согласованность смещения — эвристика по сетке изображения, а не оптический поток, движение камеры, геометрическая проверка или доказательство 3D." , forward: "прямые кандидаты", descriptorDistance: "медианное расстояние дескрипторов", ratio: "медианное отношение лучшего ко второму", diagnosticNote: "Расстояние дескрипторов и отношение лучшего результата ко второму описывают только этот алгоритм; это не калиброванная уверенность и не вероятность правильного совпадения.", notAvailable: "—", mutualNote: "Пара учитывается, только если каждый фрагмент выбирает другой как наилучшее соответствие и оба направленных теста отношения пройдены; это не геометрическая проверка."},
    uk: { label: "Локальні візуальні відповідності", matched: "взаємні відповідності", distribution: "просторовий розподіл", note: "Лише евристика відбору; це не положення камери, не відстежені ознаки й не доказ 3D-перекриття.", displacement: "медіанне зміщення", spread: "медіанний розкид", displacementNote: "Узгодженість зміщення — це евристика сітки зображення, а не оптичний потік, рух камери, геометрична перевірка чи доказ 3D." , forward: "прямі кандидати", descriptorDistance: "медіанна відстань дескрипторів", ratio: "медіанне відношення найкращого до другого", diagnosticNote: "Відстань дескрипторів і відношення найкращого результату до другого описують лише цей алгоритм; це не калібрована впевненість і не ймовірність правильного збігу.", notAvailable: "—", mutualNote: "Пара враховується лише тоді, коли кожен фрагмент обирає інший як найкращу відповідність і обидва напрямлені тести відношення пройдено; це не геометрична перевірка."},
    ar: { label: "المطابقات البصرية المحلية", matched: "تطابقات متبادلة", distribution: "التوزيع المكاني", note: "هذه إرشادية للاختيار فقط؛ ولا تمثل وضعيات الكاميرا أو النقاط المتتبعة أو إثبات التداخل ثلاثي الأبعاد.", displacement: "الإزاحة الوسيطة", spread: "التشتت الوسيط", displacementNote: "اتساق الإزاحة مجرد مؤشر استدلالي على شبكة الصورة، وليس تدفقًا بصريًا أو حركة كاميرا أو تحققًا هندسيًا أو دليلًا ثلاثي الأبعاد." , forward: "مرشحات الاتجاه الأمامي", descriptorDistance: "وسيط مسافة الواصفات", ratio: "وسيط نسبة الأفضل إلى الثاني", diagnosticNote: "تصف مسافة الواصفات ونسبة الأفضل إلى الثاني هذا المطابق فقط؛ ولا تمثلان ثقة معايرة أو احتمالًا لصحة المطابقة.", notAvailable: "—", mutualNote: "لا تُحتسب الأزواج إلا إذا اختارت كل رقعة الأخرى بوصفها أفضل تطابق واجتازت اختبارات النسبة في الاتجاهين؛ وهذا ليس تحققًا هندسيًا."},
    he: { label: "התאמות חזותיות מקומיות", matched: "התאמות הדדיות", distribution: "פיזור מרחבי", note: "זהו מדד סינון בלבד; הוא אינו מייצג תנוחות מצלמה, נקודות במעקב או הוכחת חפיפה תלת־ממדית.", displacement: "הסטה חציונית", spread: "פיזור חציוני", displacementNote: "עקביות ההסטה היא היוריסטיקה של רשת תמונה, ולא זרימה אופטית, תנועת מצלמה, אימות גאומטרי או ראיית תלת־ממד." , forward: "מועמדים בכיוון קדימה", descriptorDistance: "חציון מרחק המתארים", ratio: "חציון יחס הטוב ביותר לשני", diagnosticNote: "מרחק המתארים והיחס בין ההתאמה הטובה לשנייה מתארים את האלגוריתם הזה בלבד; הם אינם רמת ביטחון מכוילת או הסתברות להתאמה נכונה.", notAvailable: "—", mutualNote: "זוג נספר רק אם כל טלאי בוחר בשני כהתאמה הטובה ביותר ושני מבחני היחס בשני הכיוונים עוברים; אין בכך אימות גאומטרי."},
    ja: { label: "局所的な視覚対応", matched: "相互対応", distribution: "空間分布", note: "これは選別用ヒューリスティックであり、カメラ姿勢、追跡特徴、3D重複の証明を示すものではありません。", displacement: "中央値の移動", spread: "中央値のばらつき", displacementNote: "移動の一貫性は画像グリッド上のヒューリスティックであり、オプティカルフロー、カメラ移動、幾何学的検証、3Dの証拠ではありません。" , forward: "順方向の候補", descriptorDistance: "記述子距離の中央値", ratio: "最良／第2候補比の中央値", diagnosticNote: "記述子距離と最良／第2候補比はこの照合器だけを記述します。校正済み信頼度でも、正しい一致の確率でもありません。", notAvailable: "—", mutualNote: "各パッチが互いを最良の一致として選び、両方向の比率テストに合格した場合のみペアを数えます。これは幾何学的検証ではありません。"},
    ko: { label: "로컬 시각 대응", matched: "상호 대응", distribution: "공간 분포", note: "선별용 휴리스틱일 뿐이며 카메라 자세, 추적 특징 또는 3D 중첩을 증명하지 않습니다.", displacement: "중앙값 이동", spread: "중앙값 분산", displacementNote: "이동 일관성은 이미지 격자 기반 휴리스틱이며 광학 흐름, 카메라 움직임, 기하학적 검증 또는 3D 증거가 아닙니다." , forward: "순방향 후보", descriptorDistance: "기술자 거리 중앙값", ratio: "최상위/차상위 비율 중앙값", diagnosticNote: "기술자 거리와 최상위/차상위 비율은 이 매처만을 설명합니다. 보정된 신뢰도나 올바른 일치의 확률이 아닙니다.", notAvailable: "—", mutualNote: "각 패치가 서로를 최적 일치로 선택하고 양방향 비율 검사를 모두 통과한 경우에만 쌍으로 계산합니다. 이는 기하학적 검증이 아닙니다."},
    zh: { label: "局部视觉对应", matched: "双向互选匹配", distribution: "空间分布", note: "这只是筛选启发式指标，不代表相机姿态、跟踪特征，也不能证明三维重叠。", displacement: "中位位移", spread: "中位离散度", displacementNote: "位移一致性只是图像网格启发式指标，并非光流、相机运动、几何验证或三维证据。" , forward: "正向候选", descriptorDistance: "描述子距离中位数", ratio: "最佳/次佳比值中位数", diagnosticNote: "描述子距离和最佳/次佳比值仅描述当前匹配器；它们不是经过校准的置信度，也不是匹配正确的概率。", notAvailable: "—", mutualNote: "只有两个图像块互相选为最佳匹配且双向比率检验均通过时才计为一对；这并非几何验证。"},
    hi: { label: "स्थानीय दृश्य मिलान", matched: "पारस्परिक मिलान", distribution: "स्थानिक वितरण", note: "यह केवल चयन ह्यूरिस्टिक है; यह कैमरा पोज़, ट्रैक किए गए फीचर या 3D ओवरलैप का प्रमाण नहीं है।", displacement: "माध्यिका विस्थापन", spread: "माध्यिका फैलाव", displacementNote: "विस्थापन संगति केवल छवि-ग्रिड ह्यूरिस्टिक है; यह ऑप्टिकल फ्लो, कैमरा गति, ज्यामितीय सत्यापन या 3D प्रमाण नहीं है。" , forward: "आगे की दिशा के उम्मीदवार", descriptorDistance: "डिस्क्रिप्टर दूरी का माध्यिका", ratio: "सर्वोत्तम/दूसरे अनुपात का माध्यिका", diagnosticNote: "डिस्क्रिप्टर दूरी और सर्वोत्तम/दूसरे का अनुपात केवल इस मिलानकर्ता का वर्णन करते हैं; ये कैलिब्रेटेड विश्वास या सही मिलान की संभावना नहीं हैं।", notAvailable: "—", mutualNote: "किसी जोड़ी को तभी गिना जाता है जब हर पैच दूसरे को अपना सर्वोत्तम मिलान चुने और दोनों दिशाओं की अनुपात जाँच सफल हो; यह ज्यामितीय सत्यापन नहीं है।"}
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
    if (!Array.isArray(a) || !Array.isArray(b) || !a.length || a.length !== b.length) return Infinity;
    let sum = 0;
    for (let i = 0; i < a.length; i += 1) {
      const delta = a[i] - b[i];
      if (!Number.isFinite(delta)) return Infinity;
      sum += delta ** 2;
    }
    return Math.sqrt(sum / a.length);
  };

  const median = values => {
    if (!values.length) return null;
    const sorted = values.slice().sort((a, b) => a - b);
    const middle = Math.floor(sorted.length / 2);
    return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
  };

  const MAX_DESCRIPTOR_DISTANCE = 0.72;
  const MAX_NEAREST_RATIO = 0.82;
  const MIN_SECOND_DISTANCE = 1e-6;

  const nearestMatchDetails = (source, target) => {
    if (!Array.isArray(source)) return [];
    if (!Array.isArray(target) || target.length < 2) {
      return source.map(() => ({ index: -1, bestDistance: null, secondDistance: null, ratio: null }));
    }
    return source.map(descriptor => {
      let best = Infinity, second = Infinity, bestIndex = -1;
      for (let j = 0; j < target.length; j += 1) {
        const candidateDistance = distance(descriptor, target[j]);
        if (!Number.isFinite(candidateDistance)) continue;
        if (candidateDistance < best) { second = best; best = candidateDistance; bestIndex = j; }
        else if (candidateDistance < second) second = candidateDistance;
      }
      const ratio = Number.isFinite(best) && Number.isFinite(second) && second > MIN_SECOND_DISTANCE
        ? best / second
        : null;
      const accepted = Number.isFinite(best) &&
        Number.isFinite(second) &&
        best < MAX_DESCRIPTOR_DISTANCE &&
        ratio !== null &&
        ratio < MAX_NEAREST_RATIO;
      return {
        index: accepted ? bestIndex : -1,
        bestDistance: Number.isFinite(best) ? best : null,
        secondDistance: Number.isFinite(second) ? second : null,
        ratio
      };
    });
  };

  const nearestMatches = (source, target) => nearestMatchDetails(source, target).map(item => item.index);

  const correspondenceDistribution = (a, b) => {
    if (!Array.isArray(a) || !Array.isArray(b) || !a.length || !b.length) {
      return { count: 0, forwardCandidates: 0, coverage: 0, dx: null, dy: null, spread: null, medianDescriptorDistance: null, medianRatio: null };
    }
    const forward = nearestMatchDetails(a, b);
    const backward = nearestMatchDetails(b, a);
    const forwardCandidates = forward.filter(item => item.index >= 0).length;
    const occupiedA = new Set();
    const occupiedB = new Set();
    const shifts = [];
    const descriptorDistances = [];
    const ratios = [];
    for (let i = 0; i < forward.length; i += 1) {
      const forwardMatch = forward[i];
      const bestIndex = forwardMatch.index;
      if (bestIndex < 0) continue;
      const backwardMatch = backward[bestIndex];
      if (!backwardMatch || backwardMatch.index !== i) continue;
      const ax = i % 10, ay = Math.floor(i / 10);
      const bx = bestIndex % 10, by = Math.floor(bestIndex / 10);
      occupiedA.add(Math.min(3, Math.floor(ax / 3)) + ":" + Math.min(3, Math.floor(ay / 2)));
      occupiedB.add(Math.min(3, Math.floor(bx / 3)) + ":" + Math.min(3, Math.floor(by / 2)));
      shifts.push({ dx: bx - ax, dy: by - ay });
      descriptorDistances.push((forwardMatch.bestDistance + backwardMatch.bestDistance) / 2);
      ratios.push(forwardMatch.ratio, backwardMatch.ratio);
    }
    const dx = median(shifts.map(item => item.dx));
    const dy = median(shifts.map(item => item.dy));
    const spread = shifts.length ? median(shifts.map(item => Math.hypot(item.dx - dx, item.dy - dy))) : null;
    const coverageA = occupiedA.size / 16;
    const coverageB = occupiedB.size / 16;
    return {
      count: shifts.length,
      forwardCandidates,
      coverage: Math.round(((coverageA + coverageB) / 2) * 100),
      dx,
      dy,
      spread,
      medianDescriptorDistance: median(descriptorDistances),
      medianRatio: median(ratios)
    };
  };

  const api = Object.freeze({ distance, median, nearestMatchDetails, nearestMatches, correspondenceDistribution });
  if (typeof window !== "undefined") window.SSSWETKeyframeCorrespondence = api;
  if (!root) return;

  let timer = 0;
  const render = () => {
    timer = 0;
    const images = [...root.querySelectorAll(".vt-keyframe-card img")];
    if (images.length < 2) return;
    const descriptors = images.map(patchDescriptors);
    const text = copy[language()];
    root.querySelectorAll(".vt-keyframe-correspondence, .vt-keyframe-correspondence-note, .vt-keyframe-displacement-note, .vt-keyframe-mutual-note, .vt-keyframe-diagnostic-note").forEach(node => node.remove());
    for (let i = 1; i < images.length; i += 1) {
      const result = correspondenceDistribution(descriptors[i - 1], descriptors[i]);
      const card = images[i].closest(".vt-keyframe-card");
      if (!card) continue;
      const metric = document.createElement("div");
      metric.className = "vt-keyframe-correspondence";
      metric.setAttribute("role", "note");
      const formatMetric = (value, digits) => value == null ? text.notAvailable : value.toFixed(digits);
      metric.innerHTML = `<strong>${text.label}</strong><span>${result.count}</span><small>${text.matched}</small><small>${text.forward}: ${result.forwardCandidates}</small><small>${text.distribution}: ${result.coverage}%</small><small>${text.descriptorDistance}: ${formatMetric(result.medianDescriptorDistance, 3)}</small><small>${text.ratio}: ${formatMetric(result.medianRatio, 3)}</small><small>${text.displacement}: (${formatMetric(result.dx, 1)}, ${formatMetric(result.dy, 1)}) grid cells</small><small>${text.spread}: ${formatMetric(result.spread, 2)} grid cells</small>`;
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
    const mutualNote = document.createElement("p");
    mutualNote.className = "vt-keyframe-mutual-note";
    mutualNote.textContent = text.mutualNote;
    root.appendChild(mutualNote);
    const diagnosticNote = document.createElement("p");
    diagnosticNote.className = "vt-keyframe-diagnostic-note";
    diagnosticNote.textContent = text.diagnosticNote;
    root.appendChild(diagnosticNote);
  };

  const schedule = () => { if (!timer) timer = requestAnimationFrame(render); };
  new MutationObserver(schedule).observe(root, { childList: true, subtree: true });
  document.getElementById("vt-language")?.addEventListener("change", schedule);
  schedule();
})();
