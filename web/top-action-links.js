/* Localized labels for the top-level project support actions. */
(() => {
"use strict";
const labels = {
en:"Fund our techs for free",
fr:"Financer gratuitement nos travaux",
es:"Financia nuestros proyectos tecnológicos gratis",
de:"Unsere Technologieprojekte kostenlos unterstützen",
it:"Sostieni gratuitamente i nostri progetti tecnologici",
pt:"Apoie gratuitamente os nossos projetos tecnológicos",
nl:"Steun onze technologieprojecten gratis",
ru:"Бесплатно поддержите наши технологические проекты",
uk:"Безкоштовно підтримайте наші технологічні проєкти",
ar:"ادعموا مشاريعنا التقنية مجانًا",
he:"תמכו בפרויקטים הטכנולוגיים שלנו בחינם",
ja:"私たちの技術プロジェクトを無料で応援",
ko:"우리의 기술 프로젝트를 무료로 후원하세요",
zh:"免费支持我们的技术项目",
hi:"हमारी तकनीकी परियोजनाओं का निःशुल्क समर्थन करें",
id:"Dukung proyek teknologi kami secara gratis",
tr:"Teknoloji projelerimizi ücretsiz destekleyin",
pl:"Wesprzyj bezpłatnie nasze projekty technologiczne",
bn:"আমাদের প্রযুক্তি প্রকল্পগুলো বিনামূল্যে সহায়তা করুন",
sw:"Saidia miradi yetu ya teknolojia bila malipo",
vi:"Ủng hộ miễn phí các dự án công nghệ của chúng tôi",
fa:"از پروژه‌های فناوری ما به‌صورت رایگان حمایت کنید",
ur:"ہمارے ٹیکنالوجی منصوبوں کی مفت معاونت کریں",
ta:"எங்கள் தொழில்நுட்பத் திட்டங்களுக்கு இலவசமாக ஆதரவளியுங்கள்",
te:"మా సాంకేతిక ప్రాజెక్టులకు ఉచితంగా మద్దతు ఇవ్వండి"
};
function language(){
 const candidates=[window.__SSSWET_ACTIVE_LANGUAGE__,document.documentElement.dataset.language,document.getElementById("language")?.value,document.documentElement.lang];
 for(const value of candidates){const code=String(value||"").toLowerCase().replace("_","-").split("-")[0];if(labels[code])return code;}
 return "en";
}
function apply(){
 const node=document.getElementById("fund-techs-button");
 if(!node)return;
 const label=labels[language()];
 node.textContent=label;
 node.setAttribute("aria-label",label);
}
window.addEventListener("ssswet-language-changed",event=>{
 window.__SSSWET_ACTIVE_LANGUAGE__=event.detail?.language||document.documentElement.dataset.language||"";
 apply();
});
document.addEventListener("DOMContentLoaded",apply,{once:true});
document.getElementById("language")?.addEventListener("change",apply);
new MutationObserver(apply).observe(document.documentElement,{attributes:true,attributeFilter:["lang","data-language"]});
apply();
})();
