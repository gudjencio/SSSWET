(() => {
  "use strict";

  const root = document.getElementById("vt-keyframe-results");
  if (!root) return;

  const copy = {
    en: { label: "Visual continuity", summary: "Visual continuity aid", high: "good overlap candidate", low: "large visual change", note: "Heuristic only; it does not prove geometric overlap or camera-pose compatibility." },
    fr: { label: "Continuité visuelle", summary: "Aide à la continuité visuelle", high: "candidat à bon recouvrement", low: "fort changement visuel", note: "Heuristique uniquement ; elle ne prouve ni le recouvrement géométrique ni la compatibilité des poses caméra." },
    es: { label: "Continuidad visual", summary: "Ayuda de continuidad visual", high: "candidato con buen solapamiento", low: "gran cambio visual", note: "Solo es una heurística; no demuestra solapamiento geométrico ni compatibilidad de la pose de cámara." },
    de: { label: "Visuelle Kontinuität", summary: "Hilfe zur visuellen Kontinuität", high: "Kandidat mit guter Überlappung", low: "große visuelle Änderung", note: "Nur eine Heuristik; sie beweist weder geometrische Überlappung noch Kameraposen-Kompatibilität." },
    it: { label: "Continuità visiva", summary: "Supporto alla continuità visiva", high: "candidato con buona sovrapposizione", low: "grande cambiamento visivo", note: "Solo un'euristica; non dimostra sovrapposizione geometrica né compatibilità della posa della fotocamera." },
    pt: { label: "Continuidade visual", summary: "Auxílio à continuidade visual", high: "candidato com boa sobreposição", low: "grande mudança visual", note: "Apenas uma heurística; não prova sobreposição geométrica nem compatibilidade da pose da câmera." },
    nl: { label: "Visuele continuïteit", summary: "Hulp bij visuele continuïteit", high: "kandidaat met goede overlap", low: "grote visuele verandering", note: "Alleen een heuristiek; bewijst geen geometrische overlap of compatibiliteit van de camerastand." },
    ru: { label: "Визуальная непрерывность", summary: "Оценка визуальной непрерывности", high: "кандидат с хорошим перекрытием", low: "сильное визуальное изменение", note: "Только эвристика; она не доказывает геометрическое перекрытие или совместимость положения камеры." },
    uk: { label: "Візуальна безперервність", summary: "Оцінка візуальної безперервності", high: "кандидат із хорошим перекриттям", low: "велика візуальна зміна", note: "Лише евристика; вона не доводить геометричного перекриття чи сумісності положення камери." },
    ar: { label: "الاستمرارية البصرية", summary: "مؤشر الاستمرارية البصرية", high: "مرشح بتداخل بصري جيد", low: "تغير بصري كبير", note: "هذه إرشادية فقط؛ ولا تثبت التداخل الهندسي أو توافق وضعية الكاميرا." },
    he: { label: "רציפות חזותית", summary: "סיוע לרציפות חזותית", high: "מועמד עם חפיפה טובה", low: "שינוי חזותי גדול", note: "זהו מדד היוריסטי בלבד; הוא אינו מוכיח חפיפה גאומטרית או תאימות תנוחת המצלמה." },
    ja: { label: "視覚的連続性", summary: "視覚的連続性の補助指標", high: "重なりが良好な候補", low: "視覚的変化が大きい", note: "ヒューリスティックな指標であり、幾何学的な重なりやカメラ姿勢の互換性を証明するものではありません。" },
    ko: { label: "시각적 연속성", summary: "시각적 연속성 보조 지표", high: "겹침이 양호한 후보", low: "시각적 변화가 큼", note: "휴리스틱일 뿐이며 기하학적 중첩이나 카메라 자세 호환성을 증명하지 않습니다." },
    zh: { label: "视觉连续性", summary: "视觉连续性辅助指标", high: "重叠度较好的候选帧", low: "视觉变化较大", note: "这只是启发式指标，不能证明几何重叠或相机姿态兼容性。" },
    hi: { label: "दृश्य निरंतरता", summary: "दृश्य निरंतरता सहायक", high: "अच्छे ओवरलैप का उम्मीदवार", low: "बड़ा दृश्य परिवर्तन", note: "यह केवल एक ह्यूरिस्टिक है; यह ज्यामितीय ओवरलैप या कैमरा-पोज़ संगतता सिद्ध नहीं करता।" }
  };

  let lastSignature = "";
  let scheduled = false;

  const language = () => {
    const selected = document.getElementById("vt-language");
    return copy[selected?.value] ? selected.value : "en";
  };

  const luminance = (r, g, b) => (0.2126 * r + 0.7152 * g + 0.0722 * b);

  const imageVector = img => {
    if (!img.complete || !img.naturalWidth || !img.naturalHeight) return null;
    const canvas = document.createElement("canvas");
    canvas.width = 32;
    canvas.height = 24;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    if (!ctx) return null;
    try {
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
      const vector = new Float32Array(32 * 24);
      let mean = 0;
      for (let i = 0, p = 0; i < data.length; i += 4, p += 1) {
        const value = luminance(data[i], data[i + 1], data[i + 2]);
        vector[p] = value;
        mean += value;
      }
      mean /= vector.length;
      let norm = 0;
      for (let i = 0; i < vector.length; i += 1) {
        vector[i] -= mean;
        norm += vector[i] * vector[i];
      }
      const scale = Math.sqrt(norm) || 1;
      for (let i = 0; i < vector.length; i += 1) vector[i] /= scale;
      return vector;
    } catch (_) {
      return null;
    }
  };

  const distance = (a, b) => {
    if (!a || !b || a.length !== b.length) return null;
    let sum = 0;
    for (let i = 0; i < a.length; i += 1) {
      const d = a[i] - b[i];
      sum += d * d;
    }
    return Math.min(1, Math.sqrt(sum / a.length) / 2);
  };

  const render = () => {
    scheduled = false;
    const images = [...root.querySelectorAll(".vt-keyframe-card img")];
    if (!images.length) return;
    const signature = images.map(img => `${img.currentSrc || img.src}|${img.naturalWidth}x${img.naturalHeight}`).join(";");
    if (signature === lastSignature && root.querySelector(".vt-keyframe-continuity")) return;
    lastSignature = signature;

    const vectors = images.map(imageVector);
    const scores = images.map((_, index) => {
      if (index === 0) return null;
      const change = distance(vectors[index - 1], vectors[index]);
      return change == null ? null : Math.max(0, Math.min(100, (1 - change) * 100));
    });
    const text = copy[language()];

    root.querySelectorAll(".vt-keyframe-continuity").forEach(node => node.remove());
    images.forEach((img, index) => {
      const card = img.closest(".vt-keyframe-card");
      if (!card || scores[index] == null) return;
      const score = scores[index];
      const metric = document.createElement("div");
      metric.className = "vt-keyframe-continuity";
      metric.setAttribute("role", "note");
      metric.innerHTML = `<strong>${text.label}</strong><span>${score.toFixed(0)}%</span><small>${score >= 70 ? text.high : text.low}</small>`;
      card.appendChild(metric);
    });

    const note = document.createElement("p");
    note.className = "vt-keyframe-continuity-note";
    note.textContent = text.note;
    root.prepend(note);
  };

  const schedule = () => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(render);
  };

  new MutationObserver(schedule).observe(root, { childList: true, subtree: true });
  document.getElementById("vt-language")?.addEventListener("change", schedule);
  schedule();
})();
