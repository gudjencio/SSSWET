(() => {
"use strict";
const labels={
  "en": "Explore Virtual Time Travel Mapping",
  "fr": "Explorer la cartographie spatio-temporelle virtuelle",
  "es": "Explorar la cartografía virtual del espacio-tiempo",
  "de": "Virtuelle Raumzeitkartierung erkunden",
  "it": "Esplora la mappatura virtuale dello spaziotempo",
  "pt": "Explorar o mapeamento virtual do espaço-tempo",
  "nl": "Virtuele ruimtetijdkartering verkennen",
  "ru": "Изучить виртуальное картирование пространства-времени",
  "uk": "Дослідити віртуальне картографування простору-часу",
  "ar": "استكشف رسم خرائط الزمكان الافتراضي",
  "he": "לחקור מיפוי מרחב־זמן וירטואלי",
  "ja": "仮想時空マッピングを探索する",
  "ko": "가상 시공간 매핑 살펴보기",
  "zh": "探索虚拟时空映射",
  "hi": "आभासी अंतरिक्ष-समय मानचित्रण देखें",
  "id": "Jelajahi pemetaan ruang-waktu virtual",
  "tr": "Sanal uzay-zaman haritalamasını keşfet",
  "pl": "Poznaj wirtualne mapowanie czasoprzestrzeni",
  "bn": "ভার্চুয়াল স্থান-কালের মানচিত্রায়ন অন্বেষণ করুন",
  "sw": "Chunguza ramani pepe ya muda na anga",
  "vi": "Khám phá bản đồ không-thời gian ảo",
  "fa": "نقشه‌برداری مجازی فضا-زمان را کاوش کنید",
  "ur": "مجازی خلائی وقت کی نقشہ سازی دریافت کریں",
  "ta": "மெய்நிகர் காலவெளி வரைபடத்தை ஆராயுங்கள்",
  "te": "వర్చువల్ స్థల-కాల మ్యాపింగ్‌ను అన్వేషించండి"
};
function currentLanguage(){
  const detail=window.__SSSWET_ACTIVE_LANGUAGE__;
  const candidates=[
    detail,
    document.documentElement.dataset.language,
    document.getElementById("language")?.value,
    document.documentElement.lang
  ];
  for(const candidate of candidates){
    const code=String(candidate||"").toLowerCase().replace("_","-").split("-")[0];
    if(labels[code])return code;
  }
  return "en";
}
function apply(){
  const node=document.getElementById("virtual-time-travel-launch");
  if(node)node.textContent=labels[currentLanguage()];
}
window.addEventListener("ssswet-language-changed",event=>{
  window.__SSSWET_ACTIVE_LANGUAGE__=event.detail?.language||document.documentElement.dataset.language||"";
  apply();
});
document.addEventListener("DOMContentLoaded",apply,{once:true});
document.getElementById("language")?.addEventListener("change",apply);
const languageObserver=new MutationObserver(apply);
languageObserver.observe(document.documentElement,{attributes:true,attributeFilter:["lang","data-language"]});
apply();
})();