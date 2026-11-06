(() => {
  "use strict";

  const dictionaries = {
    en: {
      qualityTitle: "Temporal coverage and data quality",
      qualityIntro: "Review the spacing of recorded observations. A gap means no observation was stored in that interval; it does not prove that an event occurred.",
      qualityEmpty: "No timestamped observations are available yet.",
      qualitySummary: "{count} observations · median interval {median} · {gaps} intervals longer than {threshold}",
      gapHeading: "Longest unrecorded intervals",
      gapItem: "{from} → {to} · {duration}",
      trackSummary: "{accepted} GPS samples accepted · {segments} track segments · {rejected} samples rejected",
      trackDetails: "Low accuracy: {accuracy} · invalid coordinates: {invalid} · gap breaks: {gaps} · jump breaks: {jumps} · speed breaks: {speed}",
      noGps: "No usable GPS observations are available.",
      privacyExport: "Export privacy-safe copy",
      coarseLocation: "Include approximate locations (about 100 m); otherwise remove locations",
      privacyDone: "Privacy-safe copy exported. Original local records were not changed.",
      privacyNote: "The privacy-safe export rounds timestamps to the nearest minute, omits descriptions and sensor values, and excludes media. Approximate locations are optional.",
      durationMinutes: "min",
      durationHours: "h",
      durationSeconds: "s"
    },
    fr: {
      qualityTitle: "Couverture temporelle et qualité des données",
      qualityIntro: "Examinez l’espacement des observations enregistrées. Un intervalle indique qu’aucune observation n’y a été stockée, pas qu’un événement s’est produit.",
      qualityEmpty: "Aucune observation horodatée n’est disponible pour le moment.",
      qualitySummary: "{count} observations · intervalle médian {median} · {gaps} intervalles supérieurs à {threshold}",
      gapHeading: "Plus longs intervalles sans observation",
      gapItem: "{from} → {to} · {duration}",
      trackSummary: "{accepted} positions GPS retenues · {segments} segments de trajet · {rejected} positions écartées",
      trackDetails: "Précision insuffisante : {accuracy} · coordonnées invalides : {invalid} · coupures temporelles : {gaps} · sauts : {jumps} · vitesses : {speed}",
      noGps: "Aucune observation GPS exploitable n’est disponible.",
      privacyExport: "Exporter une copie respectueuse de la vie privée",
      coarseLocation: "Inclure des positions approximatives (environ 100 m) ; sinon les supprimer",
      privacyDone: "Copie respectueuse de la vie privée exportée. Les données locales originales sont inchangées.",
      privacyNote: "L’export arrondit les heures à la minute, omet les descriptions et les valeurs des capteurs, et exclut les médias. Les positions approximatives sont facultatives.",
      durationMinutes: "min",
      durationHours: "h",
      durationSeconds: "s"
    },
    es: {
      qualityTitle: "Cobertura temporal y calidad de datos",
      qualityIntro: "Revisa el espaciado de las observaciones registradas. Un intervalo indica que no se guardaron observaciones, no que ocurriera un evento.",
      qualityEmpty: "Aún no hay observaciones con marca temporal.",
      qualitySummary: "{count} observaciones · intervalo mediano {median} · {gaps} intervalos superiores a {threshold}",
      gapHeading: "Intervalos sin observaciones más largos",
      gapItem: "{from} → {to} · {duration}",
      trackSummary: "{accepted} muestras GPS aceptadas · {segments} segmentos · {rejected} muestras rechazadas",
      trackDetails: "Precisión baja: {accuracy} · coordenadas inválidas: {invalid} · cortes por intervalo: {gaps} · saltos: {jumps} · velocidad: {speed}",
      noGps: "No hay observaciones GPS utilizables.",
      privacyExport: "Exportar copia segura para la privacidad",
      coarseLocation: "Incluir ubicaciones aproximadas (unos 100 m); de lo contrario, eliminarlas",
      privacyDone: "Copia segura para la privacidad exportada. Los registros originales no cambiaron.",
      privacyNote: "La exportación redondea las horas al minuto, omite descripciones y valores de sensores, y excluye medios. Las ubicaciones aproximadas son opcionales.",
      durationMinutes: "min",
      durationHours: "h",
      durationSeconds: "s"
    },
    de: {
      qualityTitle: "Zeitliche Abdeckung und Datenqualität",
      qualityIntro: "Prüfe die Abstände aufgezeichneter Beobachtungen. Eine Lücke bedeutet, dass in diesem Zeitraum keine Beobachtung gespeichert wurde.",
      qualityEmpty: "Noch keine Beobachtungen mit Zeitstempel verfügbar.",
      qualitySummary: "{count} Beobachtungen · mittlerer Abstand {median} · {gaps} Intervalle länger als {threshold}",
      gapHeading: "Längste unbeobachtete Intervalle",
      gapItem: "{from} → {to} · {duration}",
      trackSummary: "{accepted} GPS-Messungen akzeptiert · {segments} Streckenabschnitte · {rejected} Messungen verworfen",
      trackDetails: "Geringe Genauigkeit: {accuracy} · ungültige Koordinaten: {invalid} · Zeitlücken: {gaps} · Sprünge: {jumps} · Geschwindigkeit: {speed}",
      noGps: "Keine verwendbaren GPS-Beobachtungen verfügbar.",
      privacyExport: "Datenschutzfreundliche Kopie exportieren",
      coarseLocation: "Ungefähre Standorte (ca. 100 m) einschließen; andernfalls entfernen",
      privacyDone: "Datenschutzfreundliche Kopie exportiert. Die lokalen Originaldaten blieben unverändert.",
      privacyNote: "Der Export rundet Zeitangaben auf Minuten, lässt Beschreibungen und Sensorwerte weg und schließt Medien aus. Ungefähre Standorte sind optional.",
      durationMinutes: "Min",
      durationHours: "Std.",
      durationSeconds: "s"
    },
    it: {
      qualityTitle: "Copertura temporale e qualità dei dati",
      qualityIntro: "Esamina gli intervalli tra le osservazioni registrate. Un intervallo indica che non è stata salvata alcuna osservazione, non che si sia verificato un evento.",
      qualityEmpty: "Non sono ancora disponibili osservazioni con data e ora.",
      qualitySummary: "{count} osservazioni · intervallo mediano {median} · {gaps} intervalli oltre {threshold}",
      gapHeading: "Intervalli non osservati più lunghi",
      gapItem: "{from} → {to} · {duration}",
      trackSummary: "{accepted} campioni GPS accettati · {segments} segmenti · {rejected} campioni esclusi",
      trackDetails: "Precisione insufficiente: {accuracy} · coordinate non valide: {invalid} · interruzioni temporali: {gaps} · salti: {jumps} · velocità: {speed}",
      noGps: "Non sono disponibili osservazioni GPS utilizzabili.",
      privacyExport: "Esporta una copia rispettosa della privacy",
      coarseLocation: "Includi posizioni approssimative (circa 100 m); altrimenti rimuovile",
      privacyDone: "Copia rispettosa della privacy esportata. I dati locali originali non sono stati modificati.",
      privacyNote: "L’esportazione arrotonda gli orari al minuto, omette descrizioni e valori dei sensori ed esclude i media. Le posizioni approssimative sono facoltative.",
      durationMinutes: "min",
      durationHours: "h",
      durationSeconds: "s"
    },
    pt: {
      qualityTitle: "Cobertura temporal e qualidade dos dados",
      qualityIntro: "Revise os intervalos entre observações gravadas. Um intervalo significa que nenhuma observação foi armazenada nesse período.",
      qualityEmpty: "Ainda não há observações com data e hora.",
      qualitySummary: "{count} observações · intervalo mediano {median} · {gaps} intervalos acima de {threshold}",
      gapHeading: "Maiores intervalos sem observações",
      gapItem: "{from} → {to} · {duration}",
      trackSummary: "{accepted} amostras GPS aceitas · {segments} segmentos · {rejected} amostras rejeitadas",
      trackDetails: "Baixa precisão: {accuracy} · coordenadas inválidas: {invalid} · pausas temporais: {gaps} · saltos: {jumps} · velocidade: {speed}",
      noGps: "Não há observações GPS utilizáveis.",
      privacyExport: "Exportar cópia com proteção de privacidade",
      coarseLocation: "Incluir localizações aproximadas (cerca de 100 m); caso contrário, removê-las",
      privacyDone: "Cópia com proteção de privacidade exportada. Os registos locais originais não foram alterados.",
      privacyNote: "A exportação arredonda os horários ao minuto, omite descrições e valores dos sensores e exclui mídia. Localizações aproximadas são opcionais.",
      durationMinutes: "min",
      durationHours: "h",
      durationSeconds: "s"
    },
    nl: {
      qualityTitle: "Tijddekking en gegevenskwaliteit",
      qualityIntro: "Bekijk de tussenpozen tussen opgeslagen waarnemingen. Een hiaat betekent dat in die periode geen waarneming is opgeslagen.",
      qualityEmpty: "Er zijn nog geen waarnemingen met tijdstempel.",
      qualitySummary: "{count} waarnemingen · mediaaninterval {median} · {gaps} intervallen langer dan {threshold}",
      gapHeading: "Langste perioden zonder waarneming",
      gapItem: "{from} → {to} · {duration}",
      trackSummary: "{accepted} GPS-metingen geaccepteerd · {segments} trajectsegmenten · {rejected} metingen afgewezen",
      trackDetails: "Lage nauwkeurigheid: {accuracy} · ongeldige coördinaten: {invalid} · tijdsonderbrekingen: {gaps} · sprongen: {jumps} · snelheid: {speed}",
      noGps: "Er zijn geen bruikbare GPS-waarnemingen.",
      privacyExport: "Privacyvriendelijke kopie exporteren",
      coarseLocation: "Geschatte locaties opnemen (ongeveer 100 m); anders locaties verwijderen",
      privacyDone: "Privacyvriendelijke kopie geëxporteerd. De oorspronkelijke lokale gegevens zijn niet gewijzigd.",
      privacyNote: "De export rondt tijden af op minuten, laat beschrijvingen en sensorwaarden weg en sluit media uit. Geschatte locaties zijn optioneel.",
      durationMinutes: "min",
      durationHours: "u",
      durationSeconds: "s"
    },
    ru: {
      qualityTitle: "Временной охват и качество данных",
      qualityIntro: "Проверьте интервалы между записанными наблюдениями. Промежуток означает отсутствие сохранённого наблюдения, а не доказательство события.",
      qualityEmpty: "Пока нет наблюдений с временными метками.",
      qualitySummary: "{count} наблюдений · медианный интервал {median} · {gaps} интервалов длиннее {threshold}",
      gapHeading: "Самые длинные интервалы без наблюдений",
      gapItem: "{from} → {to} · {duration}",
      trackSummary: "Принято GPS-точек: {accepted} · сегментов маршрута: {segments} · отклонено точек: {rejected}",
      trackDetails: "Низкая точность: {accuracy} · неверные координаты: {invalid} · разрывы времени: {gaps} · скачки: {jumps} · скорость: {speed}",
      noGps: "Нет пригодных GPS-наблюдений.",
      privacyExport: "Экспортировать копию с защитой конфиденциальности",
      coarseLocation: "Включить приблизительное местоположение (около 100 м); иначе удалить",
      privacyDone: "Копия с защитой конфиденциальности экспортирована. Исходные локальные записи не изменены.",
      privacyNote: "В экспорте время округляется до минуты, описания и значения датчиков исключаются, медиа не включаются. Приблизительное местоположение необязательно.",
      durationMinutes: "мин",
      durationHours: "ч",
      durationSeconds: "с"
    },
    uk: {
      qualityTitle: "Часове охоплення та якість даних",
      qualityIntro: "Перевірте інтервали між записаними спостереженнями. Проміжок означає, що спостереження не зберігалося, а не доводить подію.",
      qualityEmpty: "Записів із часовими мітками поки немає.",
      qualitySummary: "{count} спостережень · медіанний інтервал {median} · {gaps} інтервалів довше за {threshold}",
      gapHeading: "Найдовші проміжки без спостережень",
      gapItem: "{from} → {to} · {duration}",
      trackSummary: "Прийнято GPS-точок: {accepted} · сегментів маршруту: {segments} · відхилено точок: {rejected}",
      trackDetails: "Низька точність: {accuracy} · некоректні координати: {invalid} · часові розриви: {gaps} · стрибки: {jumps} · швидкість: {speed}",
      noGps: "Немає придатних GPS-спостережень.",
      privacyExport: "Експортувати копію із захистом приватності",
      coarseLocation: "Додати приблизні місця (близько 100 м); інакше вилучити",
      privacyDone: "Копію із захистом приватності експортовано. Початкові локальні записи не змінено.",
      privacyNote: "Час округлюється до хвилини, описи й показники сенсорів вилучаються, медіа не додаються. Приблизне місце необов’язкове.",
      durationMinutes: "хв",
      durationHours: "год",
      durationSeconds: "с"
    },
    ar: {
      qualityTitle: "التغطية الزمنية وجودة البيانات",
      qualityIntro: "راجع الفواصل بين الملاحظات المسجلة. تعني الفجوة عدم حفظ ملاحظة في تلك الفترة، ولا تثبت وقوع حدث.",
      qualityEmpty: "لا توجد ملاحظات مؤرخة بعد.",
      qualitySummary: "{count} ملاحظة · الفاصل الوسيط {median} · {gaps} فواصل أطول من {threshold}",
      gapHeading: "أطول الفترات بلا ملاحظات",
      gapItem: "{from} → {to} · {duration}",
      trackSummary: "عينات GPS المقبولة: {accepted} · مقاطع المسار: {segments} · العينات المرفوضة: {rejected}",
      trackDetails: "دقة منخفضة: {accuracy} · إحداثيات غير صالحة: {invalid} · فواصل زمنية: {gaps} · قفزات: {jumps} · السرعة: {speed}",
      noGps: "لا توجد ملاحظات GPS قابلة للاستخدام.",
      privacyExport: "تصدير نسخة تحمي الخصوصية",
      coarseLocation: "تضمين مواقع تقريبية (نحو 100 متر)، وإلا فاحذف المواقع",
      privacyDone: "تم تصدير نسخة تحمي الخصوصية. لم تتغير السجلات المحلية الأصلية.",
      privacyNote: "يقرّب التصدير الوقت إلى أقرب دقيقة، ويحذف الأوصاف وقيم المستشعرات والوسائط. المواقع التقريبية اختيارية.",
      durationMinutes: "د",
      durationHours: "س",
      durationSeconds: "ث"
    },
    he: {
      qualityTitle: "כיסוי זמני ואיכות נתונים",
      qualityIntro: "בדקו את המרווחים בין תצפיות שנשמרו. פער פירושו שלא נשמרה תצפית באותו פרק זמן, ולא הוכחה לאירוע.",
      qualityEmpty: "אין עדיין תצפיות עם חותמת זמן.",
      qualitySummary: "{count} תצפיות · מרווח חציוני {median} · {gaps} מרווחים ארוכים מ־{threshold}",
      gapHeading: "המרווחים הארוכים ביותר ללא תצפית",
      gapItem: "{from} → {to} · {duration}",
      trackSummary: "{accepted} דגימות GPS התקבלו · {segments} מקטעי מסלול · {rejected} דגימות נדחו",
      trackDetails: "דיוק נמוך: {accuracy} · קואורדינטות שגויות: {invalid} · הפסקות זמן: {gaps} · קפיצות: {jumps} · מהירות: {speed}",
      noGps: "אין תצפיות GPS שימושיות.",
      privacyExport: "ייצוא עותק המגן על הפרטיות",
      coarseLocation: "לכלול מיקומים מקורבים (כ־100 מ׳); אחרת להסיר מיקומים",
      privacyDone: "עותק המגן על הפרטיות יוצא. הרשומות המקומיות המקוריות לא שונו.",
      privacyNote: "הייצוא מעגל זמנים לדקה הקרובה, משמיט תיאורים וערכי חיישנים ואינו כולל מדיה. מיקומים מקורבים הם אפשרות בלבד.",
      durationMinutes: "דק׳",
      durationHours: "שע׳",
      durationSeconds: "ש׳"
    },
    ja: {
      qualityTitle: "時間的なカバレッジとデータ品質",
      qualityIntro: "記録された観測の間隔を確認します。空白区間はその間に観測が保存されなかったことを示すだけで、事象の発生を証明しません。",
      qualityEmpty: "タイムスタンプ付きの観測はまだありません。",
      qualitySummary: "{count} 件の観測 · 中央間隔 {median} · {threshold} を超える区間 {gaps} 件",
      gapHeading: "観測がない最長区間",
      gapItem: "{from} → {to} · {duration}",
      trackSummary: "採用 GPS サンプル {accepted} 件 · 軌跡セグメント {segments} 件 · 除外サンプル {rejected} 件",
      trackDetails: "精度不足: {accuracy} · 無効な座標: {invalid} · 時間による分割: {gaps} · 飛躍: {jumps} · 速度: {speed}",
      noGps: "利用可能な GPS 観測はありません。",
      privacyExport: "プライバシー保護コピーをエクスポート",
      coarseLocation: "およその位置（約 100 m）を含める。含めない場合は位置を削除",
      privacyDone: "プライバシー保護コピーをエクスポートしました。元のローカル記録は変更されていません。",
      privacyNote: "エクスポートでは時刻を分単位に丸め、説明とセンサー値を省略し、メディアを除外します。およその位置情報は任意です。",
      durationMinutes: "分",
      durationHours: "時間",
      durationSeconds: "秒"
    },
    ko: {
      qualityTitle: "시간 범위 및 데이터 품질",
      qualityIntro: "기록된 관측 사이의 간격을 확인합니다. 공백은 해당 기간에 관측이 저장되지 않았다는 뜻이며 사건 발생을 증명하지 않습니다.",
      qualityEmpty: "아직 시간 정보가 있는 관측이 없습니다.",
      qualitySummary: "관측 {count}개 · 중앙 간격 {median} · {threshold} 초과 간격 {gaps}개",
      gapHeading: "관측이 없는 가장 긴 구간",
      gapItem: "{from} → {to} · {duration}",
      trackSummary: "수락된 GPS 샘플 {accepted}개 · 경로 구간 {segments}개 · 거부된 샘플 {rejected}개",
      trackDetails: "정확도 낮음: {accuracy} · 잘못된 좌표: {invalid} · 시간 분할: {gaps} · 급격한 점프: {jumps} · 속도: {speed}",
      noGps: "사용 가능한 GPS 관측이 없습니다.",
      privacyExport: "개인정보 보호 사본 내보내기",
      coarseLocation: "대략적인 위치(약 100m) 포함; 그렇지 않으면 위치 제거",
      privacyDone: "개인정보 보호 사본을 내보냈습니다. 원본 로컬 기록은 변경되지 않았습니다.",
      privacyNote: "내보내기는 시간을 분 단위로 반올림하고 설명과 센서 값을 제외하며 미디어를 포함하지 않습니다. 대략적인 위치는 선택 사항입니다.",
      durationMinutes: "분",
      durationHours: "시간",
      durationSeconds: "초"
    },
    zh: {
      qualityTitle: "时间覆盖与数据质量",
      qualityIntro: "检查已记录观测之间的间隔。空档仅表示该时段没有保存观测，并不能证明发生了事件。",
      qualityEmpty: "目前没有带时间戳的观测。",
      qualitySummary: "{count} 条观测 · 中位间隔 {median} · 超过 {threshold} 的间隔 {gaps} 个",
      gapHeading: "最长无观测间隔",
      gapItem: "{from} → {to} · {duration}",
      trackSummary: "接受的 GPS 样本 {accepted} 个 · 轨迹段 {segments} 个 · 拒绝样本 {rejected} 个",
      trackDetails: "精度过低：{accuracy} · 无效坐标：{invalid} · 时间断点：{gaps} · 跳变：{jumps} · 速度：{speed}",
      noGps: "没有可用的 GPS 观测。",
      privacyExport: "导出隐私保护副本",
      coarseLocation: "包含近似位置（约 100 米）；否则删除位置",
      privacyDone: "已导出隐私保护副本。原始本地记录未更改。",
      privacyNote: "导出时将时间四舍五入到分钟，省略描述和传感器数值，并排除媒体。近似位置为可选项。",
      durationMinutes: "分钟",
      durationHours: "小时",
      durationSeconds: "秒"
    },
    hi: {
      qualityTitle: "समय कवरेज और डेटा गुणवत्ता",
      qualityIntro: "रिकॉर्ड किए गए अवलोकनों के बीच का अंतर देखें। अंतराल का अर्थ है कि उस अवधि में कोई अवलोकन सहेजा नहीं गया; यह किसी घटना का प्रमाण नहीं है।",
      qualityEmpty: "अभी समय-मुद्रित अवलोकन उपलब्ध नहीं हैं।",
      qualitySummary: "{count} अवलोकन · मध्य अंतराल {median} · {threshold} से लंबे अंतराल {gaps}",
      gapHeading: "सबसे लंबे बिना-अवलोकन अंतराल",
      gapItem: "{from} → {to} · {duration}",
      trackSummary: "{accepted} GPS नमूने स्वीकार · {segments} मार्ग खंड · {rejected} नमूने अस्वीकार",
      trackDetails: "कम सटीकता: {accuracy} · अमान्य निर्देशांक: {invalid} · समय-विराम: {gaps} · छलांग: {jumps} · गति: {speed}",
      noGps: "कोई उपयोगी GPS अवलोकन उपलब्ध नहीं है।",
      privacyExport: "गोपनीयता-सुरक्षित प्रति निर्यात करें",
      coarseLocation: "अनुमानित स्थान (लगभग 100 मीटर) शामिल करें; अन्यथा स्थान हटाएँ",
      privacyDone: "गोपनीयता-सुरक्षित प्रति निर्यात की गई। मूल स्थानीय रिकॉर्ड नहीं बदले गए।",
      privacyNote: "निर्यात समय को निकटतम मिनट तक गोल करता है, विवरण और सेंसर मान हटाता है तथा मीडिया शामिल नहीं करता। अनुमानित स्थान वैकल्पिक हैं।",
      durationMinutes: "मिनट",
      durationHours: "घंटे",
      durationSeconds: "से"
    }
  };

  function dictionary(locale) {
    return dictionaries[locale] || dictionaries.en;
  }

  function median(values) {
    if (!values.length) return null;
    const sorted = [...values].sort((a, b) => a - b);
    const middle = Math.floor(sorted.length / 2);
    return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
  }

  function formatDuration(milliseconds, words) {
    const seconds = Math.max(0, milliseconds) / 1000;
    if (seconds >= 3600) return (seconds / 3600).toFixed(1) + " " + words.durationHours;
    if (seconds >= 60) return (seconds / 60).toFixed(1) + " " + words.durationMinutes;
    return Math.round(seconds) + " " + words.durationSeconds;
  }

  function analyzeCoverage(events, options = {}) {
    if (!Array.isArray(events) || events.length > 100000) throw new Error("events must be an array of at most 100000 records");
    const maxGapMs = Number.isFinite(options.maxGapMs) ? options.maxGapMs : 15 * 60 * 1000;
    if (maxGapMs <= 0) throw new Error("maxGapMs must be positive");
    const times = events
      .filter(item => item && item.timestamp !== null && item.timestamp !== undefined && item.timestamp !== "")
      .map(item => Number(item.timestamp))
      .filter(Number.isFinite);
    if (!options.assumeSorted) times.sort((a, b) => a - b);
    const intervals = [];
    const gaps = [];
    for (let index = 1; index < times.length; index++) {
      const durationMs = times[index] - times[index - 1];
      if (durationMs < 0) continue;
      intervals.push(durationMs);
      if (durationMs > maxGapMs) {
        gaps.push({ from: times[index - 1], to: times[index], durationMs });
      }
    }
    gaps.sort((a, b) => b.durationMs - a.durationMs);
    return {
      observationCount: events.length,
      timestampedCount: times.length,
      startTimestamp: times.length ? times[0] : null,
      endTimestamp: times.length ? times[times.length - 1] : null,
      medianIntervalMs: median(intervals),
      gapCount: gaps.length,
      longestGapMs: gaps.length ? gaps[0].durationMs : 0,
      gaps,
      maxGapMs,
      interpolationPerformed: false
    };
  }

  function distanceMeters(a, b) {
    const radians = Math.PI / 180;
    const p1 = a.latitude * radians;
    const p2 = b.latitude * radians;
    const dp = (b.latitude - a.latitude) * radians;
    const dl = (b.longitude - a.longitude) * radians;
    const q = Math.sin(dp / 2) ** 2 + Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) ** 2;
    const bounded = Math.max(0, Math.min(1, q));
    return 6371000 * 2 * Math.atan2(Math.sqrt(bounded), Math.sqrt(1 - bounded));
  }

  function segmentGpsTrack(events, options = {}) {
    if (!Array.isArray(events) || events.length > 100000) throw new Error("events must be an array of at most 100000 records");
    const maxAccuracy = Number.isFinite(options.maxAccuracy) ? options.maxAccuracy : 150;
    const maxGapMs = Number.isFinite(options.maxGapMs) ? options.maxGapMs : 15 * 60 * 1000;
    const maxJumpMeters = Number.isFinite(options.maxJumpMeters) ? options.maxJumpMeters : 5000;
    const maxSpeedMps = Number.isFinite(options.maxSpeedMps) ? options.maxSpeedMps : 70;
    if (maxAccuracy <= 0 || maxGapMs <= 0 || maxJumpMeters <= 0 || maxSpeedMps <= 0) throw new Error("track thresholds must be positive");
    const gps = events.filter(item => item && item.kind === "gps");
    const diagnostics = {
      inputGpsCount: gps.length,
      invalidCoordinates: 0,
      lowAccuracy: 0,
      gapBreaks: 0,
      jumpBreaks: 0,
      speedBreaks: 0,
      nonPositiveTimeBreaks: 0
    };
    const accepted = gps.filter(item => {
      const coords = item.coords || {};
      const valid = Number.isFinite(coords.latitude) && coords.latitude >= -90 && coords.latitude <= 90 &&
        Number.isFinite(coords.longitude) && coords.longitude >= -180 && coords.longitude <= 180;
      if (!valid) {
        diagnostics.invalidCoordinates++;
        return false;
      }
      if (Number.isFinite(item.accuracy) && item.accuracy > maxAccuracy) {
        diagnostics.lowAccuracy++;
        return false;
      }
      return item.timestamp !== null && item.timestamp !== undefined && item.timestamp !== "" && Number.isFinite(Number(item.timestamp));
    });
    if (!options.assumeSorted) accepted.sort((a, b) => Number(a.timestamp) - Number(b.timestamp));
    const segments = [];
    let segment = [];
    const flush = () => {
      if (segment.length > 1) segments.push(segment);
      segment = [];
    };
    accepted.forEach((event, index) => {
      const previous = accepted[index - 1];
      if (previous) {
        const elapsed = Number(event.timestamp) - Number(previous.timestamp);
        const distance = distanceMeters(previous.coords, event.coords);
        if (elapsed <= 0) {
          diagnostics.nonPositiveTimeBreaks++;
          flush();
        } else if (elapsed > maxGapMs) {
          diagnostics.gapBreaks++;
          flush();
        } else if (distance > maxJumpMeters) {
          diagnostics.jumpBreaks++;
          flush();
        } else if (distance / Math.max(elapsed / 1000, 1) > maxSpeedMps) {
          diagnostics.speedBreaks++;
          flush();
        }
      }
      segment.push(event);
    });
    flush();
    diagnostics.acceptedCount = accepted.length;
    diagnostics.rejectedCount = gps.length - accepted.length;
    diagnostics.segmentCount = segments.length;
    return { accepted, segments, diagnostics, thresholds: { maxAccuracy, maxGapMs, maxJumpMeters, maxSpeedMps } };
  }

  function analyze(events, options = {}) {
    return {
      coverage: analyzeCoverage(events, options),
      track: segmentGpsTrack(events, options)
    };
  }

  function createPrivacySafeExport(events, options = {}) {
    if (!Array.isArray(events) || events.length > 100000) throw new Error("events must be an array of at most 100000 records");
    const includeCoarseLocation = options.includeCoarseLocation === true;
    const observations = events
      .filter(item => item && item.timestamp !== null && item.timestamp !== undefined && item.timestamp !== "" && Number.isFinite(Number(item.timestamp)))
      .map(item => {
        const result = {
          kind: String(item.kind || "observation"),
          timestamp: Math.round(Number(item.timestamp) / 60000) * 60000
        };
        if (item.eventType) result.eventType = String(item.eventType);
        if (includeCoarseLocation && item.coords &&
            Number.isFinite(item.coords.latitude) && item.coords.latitude >= -90 && item.coords.latitude <= 90 &&
            Number.isFinite(item.coords.longitude) && item.coords.longitude >= -180 && item.coords.longitude <= 180) {
          result.coords = {
            latitude: Math.round(item.coords.latitude * 1000) / 1000,
            longitude: Math.round(item.coords.longitude * 1000) / 1000
          };
        }
        return result;
      });
    return {
      format: "ssswet-virtual-time-map-privacy-safe-v1",
      exported_at: new Date().toISOString(),
      privacy: {
        location_precision: includeCoarseLocation ? "rounded_to_0.001_degrees" : "omitted",
        timestamps: "rounded_to_nearest_minute",
        free_text: "omitted",
        sensor_values: "omitted",
        media_included: false
      },
      observation_count: observations.length,
      observations,
      warning: "This export is a privacy-reduced derivative, not an anonymization guarantee. Review it before sharing."
    };
  }

  function message(locale, key) {
    return dictionary(locale)[key] || dictionary("en")[key] || key;
  }

  function localize(locale) {
    const words = dictionary(locale);
    document.querySelectorAll("[data-tq]").forEach(node => {
      const value = words[node.getAttribute("data-tq")];
      if (value) node.textContent = value;
    });
  }

  function render(events, locale, analysis) {
    const words = dictionary(locale);
    const summary = document.getElementById("vt-quality-summary");
    const gapsNode = document.getElementById("vt-quality-gaps");
    const trackNode = document.getElementById("vt-track-quality");
    if (!summary || !gapsNode || !trackNode) return;
    const report = analysis || analyze(events);
    const coverage = report.coverage;
    const track = report.track;
    if (!coverage.timestampedCount) {
      summary.textContent = words.qualityEmpty;
      gapsNode.replaceChildren();
    } else {
      summary.textContent = words.qualitySummary
        .replace("{count}", String(coverage.timestampedCount))
        .replace("{median}", coverage.medianIntervalMs === null ? "—" : formatDuration(coverage.medianIntervalMs, words))
        .replace("{gaps}", String(coverage.gapCount))
        .replace("{threshold}", formatDuration(coverage.maxGapMs, words));
      gapsNode.replaceChildren();
      if (coverage.gaps.length) {
        const heading = document.createElement("strong");
        heading.textContent = words.gapHeading;
        gapsNode.appendChild(heading);
        coverage.gaps.slice(0, 5).forEach(gap => {
          const item = document.createElement("li");
          item.textContent = words.gapItem
            .replace("{from}", new Date(gap.from).toLocaleString(locale || "en"))
            .replace("{to}", new Date(gap.to).toLocaleString(locale || "en"))
            .replace("{duration}", formatDuration(gap.durationMs, words));
          gapsNode.appendChild(item);
        });
      }
    }
    const d = track.diagnostics;
    trackNode.textContent = d.inputGpsCount
      ? words.trackSummary
          .replace("{accepted}", String(d.acceptedCount))
          .replace("{segments}", String(d.segmentCount))
          .replace("{rejected}", String(d.rejectedCount)) + " · " +
        words.trackDetails
          .replace("{accuracy}", String(d.lowAccuracy))
          .replace("{invalid}", String(d.invalidCoordinates))
          .replace("{gaps}", String(d.gapBreaks))
          .replace("{jumps}", String(d.jumpBreaks))
          .replace("{speed}", String(d.speedBreaks))
      : words.noGps;
  }

  window.SSSWETTemporalQuality = {
    analyzeCoverage,
    segmentGpsTrack,
    analyze,
    createPrivacySafeExport,
    message,
    localize,
    render
  };
})();