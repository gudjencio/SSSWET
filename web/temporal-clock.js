(() => {
  "use strict";
  const DEFAULT_TOLERANCE_MS = 2000;
  const labels = {
    en: { within: "Wall-clock offset is within ±{tolerance} ms of this session clock.", diverged: "Device wall clock differs by {offset} ms from this session clock; timeline order uses the monotonic session clock.", unavailable: "Monotonic clock unavailable; this observation uses the device wall clock." },
    fr: { within: "L’écart de l’horloge système reste dans ±{tolerance} ms par rapport à l’horloge de cette session.", diverged: "L’horloge système diffère de {offset} ms de l’horloge monotone de cette session ; l’ordre utilise cette dernière.", unavailable: "Horloge monotone indisponible ; cette observation utilise l’horloge système." },
    es: { within: "La diferencia del reloj del sistema está dentro de ±{tolerance} ms respecto al reloj de esta sesión.", diverged: "El reloj del sistema difiere {offset} ms del reloj monótono de esta sesión; el orden usa el reloj monótono.", unavailable: "Reloj monótono no disponible; esta observación usa el reloj del sistema." },
    de: { within: "Die Abweichung der Systemuhr liegt innerhalb von ±{tolerance} ms gegenüber der Sitzungsuhr.", diverged: "Die Systemuhr weicht um {offset} ms von der monotonen Sitzungsuhr ab; die Reihenfolge folgt der monotonen Uhr.", unavailable: "Monotone Uhr nicht verfügbar; diese Beobachtung verwendet die Systemuhr." },
    it: { within: "Lo scarto dell’orologio di sistema rientra in ±{tolerance} ms rispetto all’orologio della sessione.", diverged: "L’orologio di sistema differisce di {offset} ms dall’orologio monotono della sessione; l’ordine usa quello monotono.", unavailable: "Orologio monotono non disponibile; questa osservazione usa l’orologio di sistema." },
    pt: { within: "A diferença do relógio do sistema está dentro de ±{tolerance} ms em relação ao relógio desta sessão.", diverged: "O relógio do sistema difere {offset} ms do relógio monotónico da sessão; a ordem usa o relógio monotónico.", unavailable: "Relógio monotónico indisponível; esta observação usa o relógio do sistema." },
    nl: { within: "De afwijking van de systeemklok valt binnen ±{tolerance} ms ten opzichte van de sessieklok.", diverged: "De systeemklok wijkt {offset} ms af van de monotone sessieklok; de tijdlijnvolgorde gebruikt de monotone klok.", unavailable: "Monotone klok niet beschikbaar; deze waarneming gebruikt de systeemklok." },
    ru: { within: "Отклонение системных часов находится в пределах ±{tolerance} мс относительно часов сеанса.", diverged: "Системные часы отличаются на {offset} мс от монотонных часов сеанса; порядок задаётся монотонными часами.", unavailable: "Монотонные часы недоступны; для этой записи используются системные часы." },
    uk: { within: "Відхилення системного годинника перебуває в межах ±{tolerance} мс відносно годинника сеансу.", diverged: "Системний годинник відрізняється на {offset} мс від монотонного годинника сеансу; порядок визначає монотонний годинник.", unavailable: "Монотонний годинник недоступний; для цього запису використано системний годинник." },
    ar: { within: "يقع اختلاف ساعة النظام ضمن ±{tolerance} مللي ثانية مقارنة بساعة الجلسة.", diverged: "تختلف ساعة النظام بمقدار {offset} مللي ثانية عن ساعة الجلسة الرتيبة؛ ويُستخدم توقيت الجلسة لترتيب السجل.", unavailable: "الساعة الرتيبة غير متاحة؛ يستخدم هذا الرصد ساعة النظام." },
    he: { within: "הפער בשעון המערכת נמצא בטווח של ±{tolerance} אלפיות השנייה ביחס לשעון הפעילות.", diverged: "שעון המערכת שונה ב־{offset} אלפיות השנייה מהשעון המונוטוני של הפעילות; הסדר נקבע לפי השעון המונוטוני.", unavailable: "שעון מונוטוני אינו זמין; תצפית זו משתמשת בשעון המערכת." },
    ja: { within: "システム時計とこのセッションの時計との差は ±{tolerance} ミリ秒以内です。", diverged: "システム時計はセッションの単調時計と {offset} ミリ秒異なります。時系列の順序には単調時計を使用します。", unavailable: "単調時計を利用できないため、この観測にはシステム時計を使用します。" },
    ko: { within: "시스템 시계와 이 세션 시계의 차이는 ±{tolerance}ms 이내입니다.", diverged: "시스템 시계가 세션의 단조 시계와 {offset}ms 차이 납니다. 타임라인 순서는 단조 시계를 사용합니다.", unavailable: "단조 시계를 사용할 수 없어 이 관측에는 시스템 시계를 사용합니다." },
    zh: { within: "系统时钟与本次会话时钟的偏差在 ±{tolerance} 毫秒以内。", diverged: "系统时钟与本次会话的单调时钟相差 {offset} 毫秒；时间线排序使用单调时钟。", unavailable: "单调时钟不可用；此观测使用设备系统时钟。" },
    hi: { within: "सिस्टम घड़ी और इस सत्र की घड़ी का अंतर ±{tolerance} मिलीसेकंड के भीतर है।", diverged: "सिस्टम घड़ी इस सत्र की मोनोटोनिक घड़ी से {offset} मिलीसेकंड अलग है; क्रम के लिए मोनोटोनिक घड़ी उपयोग होती है।", unavailable: "मोनोटोनिक घड़ी उपलब्ध नहीं; यह अवलोकन सिस्टम घड़ी का उपयोग करता है।" }
  };

  function createSessionClock(options = {}) {
    const wallNow = typeof options.wallNow === "function" ? options.wallNow : () => Date.now();
    const monotonicNow = typeof options.monotonicNow === "function"
      ? options.monotonicNow
      : (typeof performance !== "undefined" && typeof performance.now === "function" ? () => performance.now() : null);
    const wallOriginRaw = Number(wallNow());
    const wallOrigin = Number.isFinite(wallOriginRaw) ? Math.round(wallOriginRaw) : Date.now();
    const monotonicOriginRaw = monotonicNow ? Number(monotonicNow()) : NaN;
    const monotonicAvailable = Number.isFinite(monotonicOriginRaw);
    const toleranceRaw = Number(options.toleranceMs);
    const toleranceMs = Number.isFinite(toleranceRaw) && toleranceRaw >= 0 ? toleranceRaw : DEFAULT_TOLERANCE_MS;
    const sessionId = String(options.sessionId || ("vtclock-" + Math.random().toString(36).slice(2, 12)));
    let lastElapsedMs = 0;
    let lastTimestamp = wallOrigin;

    function elapsedNow() {
      if (!monotonicAvailable) return null;
      const current = Number(monotonicNow());
      if (!Number.isFinite(current)) return null;
      lastElapsedMs = Math.max(lastElapsedMs, current - monotonicOriginRaw, 0);
      return Math.round(lastElapsedMs * 1000) / 1000;
    }

    function capture() {
      const wallRaw = Number(wallNow());
      const wallTimestamp = Number.isFinite(wallRaw) ? Math.round(wallRaw) : null;
      const monotonicElapsedMs = elapsedNow();
      if (monotonicElapsedMs === null) {
        return { timestamp: wallTimestamp === null ? Date.now() : wallTimestamp, wallTimestamp, monotonicElapsedMs: null, clockOffsetMs: null, clockToleranceMs: toleranceMs, clockStatus: "monotonic_unavailable", clockSessionId: sessionId };
      }
      const projectedTimestamp = Math.round(wallOrigin + monotonicElapsedMs);
      const timestamp = Math.max(lastTimestamp, projectedTimestamp);
      lastTimestamp = timestamp;
      const clockOffsetMs = wallTimestamp === null ? null : Math.round(wallTimestamp - timestamp);
      const clockStatus = clockOffsetMs === null ? "monotonic_unavailable" : (Math.abs(clockOffsetMs) > toleranceMs ? "wall_clock_diverged" : "within_tolerance");
      return { timestamp, wallTimestamp, monotonicElapsedMs, clockOffsetMs, clockToleranceMs: toleranceMs, clockStatus, clockSessionId: sessionId };
    }

    function durationBetween(start, end) {
      if (start && end && start.clockSessionId === sessionId && end.clockSessionId === sessionId && Number.isFinite(start.monotonicElapsedMs) && Number.isFinite(end.monotonicElapsedMs)) {
        return Math.max(0, end.monotonicElapsedMs - start.monotonicElapsedMs);
      }
      const startTimestamp = Number(start && start.timestamp);
      const endTimestamp = Number(end && end.timestamp);
      return Number.isFinite(startTimestamp) && Number.isFinite(endTimestamp) ? Math.max(0, endTimestamp - startTimestamp) : 0;
    }

    return Object.freeze({ sessionId, monotonicAvailable, elapsedNow, capture, durationBetween, toleranceMs });
  }

  function describe(snapshot, locale = "en") {
    if (!snapshot || !snapshot.clockStatus) return "";
    const copy = labels[locale] || labels.en;
    if (snapshot.clockStatus === "wall_clock_diverged" && Number.isFinite(Number(snapshot.clockOffsetMs))) {
      const offset = Number(snapshot.clockOffsetMs);
      return copy.diverged.replace("{offset}", (offset > 0 ? "+" : "") + Math.round(offset));
    }
    if (snapshot.clockStatus === "within_tolerance") {
      const tolerance = Number.isFinite(Number(snapshot.clockToleranceMs)) ? Math.round(Number(snapshot.clockToleranceMs)) : DEFAULT_TOLERANCE_MS;
      return copy.within.replace("{tolerance}", String(tolerance));
    }
    return copy.unavailable;
  }

  const api = Object.freeze({ createSessionClock, describe, locales: Object.freeze(Object.keys(labels)), DEFAULT_TOLERANCE_MS });
  if (typeof window !== "undefined") window.SSSWETTemporalClock = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})();