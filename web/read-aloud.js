(() => {
"use strict";
const labels={en:{read:"Read selected text",stop:"Stop reading",empty:"Select some text first."},fr:{read:"Lire le texte sélectionné",stop:"Arrêter la lecture",empty:"Sélectionnez d’abord un texte."},es:{read:"Leer el texto seleccionado",stop:"Detener lectura",empty:"Selecciona texto primero."},de:{read:"Ausgewählten Text vorlesen",stop:"Vorlesen beenden",empty:"Wähle zuerst Text aus."},it:{read:"Leggi il testo selezionato",stop:"Interrompi lettura",empty:"Seleziona prima del testo."},pt:{read:"Ler o texto selecionado",stop:"Parar leitura",empty:"Selecione algum texto primeiro."},nl:{read:"Geselecteerde tekst voorlezen",stop:"Voorlezen stoppen",empty:"Selecteer eerst tekst."},ru:{read:"Прочитать выделенный текст",stop:"Остановить чтение",empty:"Сначала выделите текст."},uk:{read:"Прочитати виділений текст",stop:"Зупинити читання",empty:"Спочатку виділіть текст."},ar:{read:"قراءة النص المحدد",stop:"إيقاف القراءة",empty:"حدد نصًا أولاً."},he:{read:"הקראת הטקסט המסומן",stop:"עצירת ההקראה",empty:"יש לבחור טקסט תחילה."},ja:{read:"選択したテキストを読み上げる",stop:"読み上げを停止",empty:"先にテキストを選択してください。"},ko:{read:"선택한 텍스트 읽기",stop:"읽기 중지",empty:"먼저 텍스트를 선택하세요."},zh:{read:"朗读所选文本",stop:"停止朗读",empty:"请先选择文本。"},hi:{read:"चयनित पाठ पढ़ें",stop:"पढ़ना रोकें",empty:"पहले कुछ पाठ चुनें。"}};
let selected="",speaking=false;
const button=document.createElement("button");button.id="ssswet-read-selection";button.type="button";button.disabled=true;button.textContent=labels.en.read;button.setAttribute("aria-label",labels.en.read);button.title=labels.en.read;document.body.appendChild(button);
function locale(){const code=(document.getElementById("language")?.value||document.documentElement.lang||"en").toLowerCase().split("-")[0];return labels[code]?code:"en"}
function update(){const t=labels[locale()];button.textContent=speaking?t.stop:t.read;button.setAttribute("aria-label",speaking?t.stop:t.read);button.title=speaking?t.stop:t.read}
function onSelection(){const value=String(window.getSelection?.()||"").trim();if(value.length>1){selected=value.slice(0,5000);button.disabled=false}else if(!speaking){selected="";button.disabled=true}}
button.addEventListener("mousedown",event=>event.preventDefault());
button.addEventListener("click",()=>{
 if(!("speechSynthesis" in window)||typeof SpeechSynthesisUtterance==="undefined")return;
 if(speaking){speechSynthesis.cancel();speaking=false;update();return}
 if(!selected){button.title=labels[locale()].empty;return}
 const lang=document.getElementById("language")?.value||document.documentElement.lang||"en";
 const voices=speechSynthesis.getVoices(),base=lang.toLowerCase().split("-")[0];
 const matches=voices.filter(v=>String(v.lang||"").toLowerCase().split("-")[0]===base);
 const pool=matches.length?matches:voices.filter(v=>v.default);
 const voice=pool.slice().sort((a,b)=>Number(/natural|neural|online|premium|enhanced|google|microsoft|siri/i.test(b.name||""))-Number(/natural|neural|online|premium|enhanced|google|microsoft|siri/i.test(a.name||"")))[0];
 const utterance=new SpeechSynthesisUtterance(selected.replace(/\s+/g," ").trim());utterance.lang=lang;if(voice){utterance.voice=voice;utterance.lang=voice.lang||lang}utterance.rate=.97;utterance.pitch=1;utterance.volume=.96;
 speaking=true;update();utterance.onend=utterance.onerror=()=>{speaking=false;update()};speechSynthesis.cancel();speechSynthesis.speak(utterance);
});
document.addEventListener("selectionchange",onSelection);document.getElementById("language")?.addEventListener("change",update);window.addEventListener("ssswet-language-changed",update);update();
})();