(() => {
"use strict";
const labels={
en:"Try our Virtual Time Machine",
fr:"Découvrir le voyage virtuel dans le temps",
es:"Probar nuestra máquina del tiempo virtual",
de:"Unsere virtuelle Zeitmaschine testen",
it:"Prova la nostra macchina del tempo virtuale",
pt:"Experimentar a nossa máquina do tempo virtual",
nl:"Probeer onze virtuele tijdmachine",
ru:"Попробовать виртуальную машину времени",
uk:"Спробувати нашу віртуальну машину часу",
ar:"جرّب آلة الزمن الافتراضية",
he:"נסו את מכונת הזמן הווירטואלית שלנו",
ja:"バーチャルタイムマシンを試す",
ko:"가상 타임머신 체험하기",
zh:"体验虚拟时光机",
hi:"हमारी वर्चुअल टाइम मशीन आज़माएँ",
id:"Coba Mesin Waktu Virtual Kami",
tr:"Sanal Zaman Makinemizi Deneyin",
pl:"Wypróbuj naszą wirtualną maszynę czasu",
bn:"আমাদের ভার্চুয়াল টাইম মেশিন ব্যবহার করে দেখুন",
sw:"Jaribu Mashine Yetu ya Muda ya Mtandaoni",
vi:"Trải nghiệm cỗ máy thời gian ảo",
fa:"ماشین زمان مجازی ما را امتحان کنید",
ur:"ہماری ورچوئل ٹائم مشین آزمائیں",
ta:"எங்கள் மெய்நிகர் கால இயந்திரத்தை முயற்சிக்கவும்",
te:"మా వర్చువల్ టైమ్ మెషీన్‌ను ప్రయత్నించండి"
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