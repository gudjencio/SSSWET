(() => {
"use strict";
const labels={
en:"Try our Virtual Time Machine",fr:"Essayer notre machine temporelle virtuelle",es:"Probar nuestra máquina del tiempo virtual",de:"Unsere virtuelle Zeitmaschine testen",it:"Prova la nostra macchina del tempo virtuale",pt:"Experimentar a nossa máquina do tempo virtual",nl:"Probeer onze virtuele tijdmachine",ru:"Попробовать виртуальную машину времени",uk:"Спробувати нашу віртуальну машину часу",ar:"جرّب آلة الزمن الافتراضية",he:"נסו את מכונת הזמן הווירטואלית שלנו",ja:"バーチャルタイムマシンを試す",ko:"가상 타임머신 체험하기",zh:"体验虚拟时光机",hi:"हमारी वर्चुअल टाइम मशीन आज़माएँ"
};
function apply(){const code=(document.getElementById("language")?.value||document.documentElement.lang||"en").toLowerCase().split("-")[0];const node=document.getElementById("virtual-time-travel-launch");if(node)node.textContent=labels[code]||labels.en;}
document.addEventListener("DOMContentLoaded",apply,{once:true});
document.getElementById("language")?.addEventListener("change",apply);
window.addEventListener("ssswet-language-changed",apply);apply();
})();