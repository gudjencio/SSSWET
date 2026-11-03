/* SSSWET shared interface translations — voice controls.
 * These strings are merged before the application initializes.
 * Native-speaker review is welcome; missing translations retain the English fallback.
 */
(function () {
  "use strict";
  const locales = window.SSSWET_LOCALES || {};
  const translations = {
    id: { voiceDisable: "Matikan suara", voiceRead: "Bacakan konten", voicePause: "Jeda", voiceResume: "Lanjutkan", voiceStop: "Hentikan" },
    tr: { voiceDisable: "Sesi kapat", voiceRead: "İçeriği sesli oku", voicePause: "Duraklat", voiceResume: "Devam et", voiceStop: "Durdur" },
    pl: { voiceDisable: "Wyłącz głos", voiceRead: "Odczytaj treść", voicePause: "Wstrzymaj", voiceResume: "Wznów", voiceStop: "Zatrzymaj" },
    bn: { voiceDisable: "কণ্ঠস্বর বন্ধ করুন", voiceRead: "লেখা পড়ে শোনান", voicePause: "বিরতি দিন", voiceResume: "আবার শুরু করুন", voiceStop: "থামান" },
    sw: { voiceDisable: "Zima sauti", voiceRead: "Soma maudhui kwa sauti", voicePause: "Sitisha kwa muda", voiceResume: "Endelea", voiceStop: "Simamisha" },
    vi: { voiceDisable: "Tắt giọng đọc", voiceRead: "Đọc nội dung", voicePause: "Tạm dừng", voiceResume: "Tiếp tục", voiceStop: "Dừng" },
    fa: { voiceDisable: "خاموش کردن صدا", voiceRead: "خواندن محتوا", voicePause: "مکث", voiceResume: "ادامه", voiceStop: "توقف" },
    ur: { voiceDisable: "آواز بند کریں", voiceRead: "مواد پڑھ کر سنائیں", voicePause: "وقفہ کریں", voiceResume: "دوبارہ شروع کریں", voiceStop: "رک جائیں" },
    ta: { voiceDisable: "குரலை அணைக்கவும்", voiceRead: "உள்ளடக்கத்தைப் படிக்கவும்", voicePause: "இடைநிறுத்தவும்", voiceResume: "மீண்டும் தொடரவும்", voiceStop: "நிறுத்தவும்" },
    te: { voiceDisable: "వాయిస్‌ను ఆపివేయండి", voiceRead: "కంటెంట్‌ను చదివి వినిపించండి", voicePause: "పాజ్ చేయండి", voiceResume: "కొనసాగించండి", voiceStop: "ఆపండి" }
  };
  for (const [code, copy] of Object.entries(translations)) {
    if (!locales[code]) continue;
    for (const [key, value] of Object.entries(copy)) {
      if (!locales[code][key]) locales[code][key] = value;
    }
  }
})();
