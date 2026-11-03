(() => {
  "use strict";
  const exact = {
    "Sentient AI":"IA sentiente","Spacetime":"Espace-temps","Timetravel":"Voyage temporel","Artificial Gravity":"Gravité artificielle","Planetary Monitoring":"Surveillance planétaire","Black Hole Observation":"Observation des trous noirs","Event Horizon Imaging":"Imagerie des horizons des événements","Gravitational Wave Navigation":"Navigation par ondes gravitationnelles","Relativistic Spacecraft":"Vaisseaux spatiaux relativistes","Jetpack":"Système de propulsion individuel","Antimatter Research":"Recherche sur l'antimatière","Beamed Energy Propulsion":"Propulsion par énergie dirigée","Solar Sail Navigation":"Navigation par voile solaire","Plasma Propulsion":"Propulsion plasma","Space Life Support":"Support-vie spatial","Cosmic Ray Shielding":"Blindage contre les rayons cosmiques","Cryogenic Hibernation":"Hibernation cryogénique","Orbital Manufacturing":"Fabrication orbitale","Lunar Resource Systems":"Systèmes de ressources lunaires","Radiation Protection":"Protection contre les rayonnements","Armor":"Protection corporelle","Disaster Resilience":"Résilience aux catastrophes","Extreme Thermal Protection":"Protection thermique extrême","Impact Absorbing Materials":"Matériaux absorbant les impacts","Cleanenergy":"Énergie propre","Fusion Energy":"Énergie de fusion","Superconducting Grid":"Réseau supraconducteur","Energy Storage":"Stockage de l'énergie","Metamaterials":"Métamatériaux","Self Healing Materials":"Matériaux autoréparants","Smart Adaptive Materials":"Matériaux adaptatifs intelligents","Longevity":"Longévité en bonne santé","Medical Nanotechnology":"Nanotechnologies médicales","Organ Regeneration":"Régénération des organes","Precision Gene Therapies":"Thérapies géniques de précision","Artificial Organs":"Organes artificiels","Neurointerfaces":"Neurointerfaces","Robotics Exoskeletons":"Exosquelettes robotiques","Sensory Augmentation":"Augmentation sensorielle","Animal Health":"Santé animale","Climate":"Climat","Biodiversity":"Biodiversité","Wildlife":"Protection de la faune","Oceans":"Océans","Reforestation":"Reboisement","Agriculture":"Agriculture","Carbon Monitoring":"Surveillance du carbone","Pollinators":"Protection des pollinisateurs","Air Quality":"Qualité de l'air","Water":"Eau","Food Systems":"Systèmes alimentaires","Sanitation":"Assainissement","Wildfire Prediction":"Prévision des incendies de forêt","Autonomous Labs":"Laboratoires autonomes","Swarm Robotics":"Robotique en essaim","Autonomous Disaster Robots":"Robots autonomes pour les catastrophes","Mobility":"Mobilité","Accessibility":"Accessibilité","Advanced Computing":"Calcul avancé","Quantum Networks":"Réseaux quantiques","Quantum Sensing":"Capteurs quantiques","Neuromorphic Computing":"Calcul neuromorphique","Photonic Computing":"Calcul photonique","Distributed Scientific Computing":"Calcul scientifique distribué","Translator":"Traduction humain-machine","Interstellar Communication":"Communication interstellaire","Universal Translation Systems":"Systèmes de traduction universelle","Public Health":"Santé publique","Education":"Éducation"
  };
  const phrases = {
    "resource mapping":"cartographie des ressources","radiation monitoring":"surveillance des rayonnements",
    "autonomous operations":"opérations autonomes","precision landing":"atterrissage de précision",
    "life support":"support-vie","hazard detection":"détection des risques","impact mitigation":"atténuation des impacts",
    "thermal protection":"protection thermique","structural monitoring":"surveillance structurelle",
    "evacuation support":"assistance à l’évacuation","wearable safety":"sécurité portable",
    "emergency power":"alimentation de secours","environmental sensing":"capteurs environnementaux",
    "thermal management":"gestion thermique","power quality":"qualité de l’alimentation",
    "load balancing":"équilibrage de charge","energy recovery":"récupération d’énergie",
    "fault detection":"détection des défaillances","demand forecasting":"prévision de la demande",
    "microgrid control":"contrôle des micro-réseaux","self-healing":"autoréparateur",
    "damage detection":"détection des dommages","surface engineering":"ingénierie des surfaces",
    "fatigue monitoring":"surveillance de la fatigue","manufacturing control":"contrôle de fabrication",
    "durability prediction":"prédiction de durabilité","drug delivery":"administration de médicaments",
    "prosthetic control":"contrôle prothétique","physiological sensing":"capteurs physiologiques",
    "clinical data":"données cliniques","safety monitoring":"surveillance de la sécurité",
    "water quality":"qualité de l’eau","soil sensing":"capteurs des sols",
    "biodiversity mapping":"cartographie de la biodiversité","carbon accounting":"comptabilité carbone",
    "pollution detection":"détection de la pollution","wildfire detection":"détection des incendies",
    "resilience planning":"planification de la résilience","human interaction":"interaction humaine",
    "fault recovery":"récupération après défaillance","energy management":"gestion énergétique",
    "safe autonomy":"autonomie sûre","data provenance":"provenance des données",
    "knowledge discovery":"découverte des connaissances","privacy protection":"protection de la vie privée",
    "health information":"informations de santé","decision support":"aide à la décision",
    "research coordination":"coordination de la recherche"
  };
  const words = {"orbital":"orbital","deep-space":"espace profond","planetary":"planétaire","lunar":"lunaire","interstellar":"interstellaire","civil":"civile","industrial":"industrielle","rescue":"de secours","extreme-environment":"en environnement extrême","infrastructure":"d'infrastructure","renewable":"renouvelable","grid":"réseau","portable":"portable","space":"spatiale","advanced":"avancée","bioinspired":"bio-inspirée","structural":"structurelle","functional":"fonctionnelle","recyclable":"recyclable","cellular":"cellulaire","tissue":"tissulaire","organ":"organique","neural":"neuronale","assistive":"assistive","ecosystem":"écosystémique","climate":"climatique","marine":"marine","agricultural":"agricole","atmospheric":"atmosphérique","field":"de terrain","scientific":"scientifique","public":"publique","distributed":"distribuée","secure":"sécurisée","accessible":"accessible","navigation":"navigation","robotics":"robotique","habitats":"habitats","monitoring":"surveillance","restoration":"restauration","forecasting":"prévision","mapping":"cartographie","detection":"détection","protection":"protection","research":"recherche","computing":"calcul","communication":"communication","translation":"traduction","coordination":"coordination","support":"assistance"};
  const lang = () => (document.getElementById("language")?.value || document.documentElement.lang || "en").toLowerCase().split("-")[0];
  const frenchTitle = text => {
    const raw = String(text || "").trim();
    if (!raw || exact[raw]) return exact[raw] || raw;
    let value = raw;
    for (const [en, fr] of Object.entries(phrases)) {
      value = value.replace(new RegExp("\\b" + en + "\\b", "gi"), fr);
    }
    for (const [en, fr] of Object.entries(words)) {
      value = value.replace(new RegExp("\\b" + en + "\\b", "gi"), fr);
    }
    return value;
  };
  const catalogueCopy = {
    en:["511 registered research programmes · 117 contribution themes","The scientific registry contains 511 research dossiers. The contribution interface separately presents 117 selected themes. The 394 generated entries and eleven curated additions are research programmes, not demonstrated technologies."],
    fr:["511 programmes de recherche enregistrés · 117 thèmes de contribution","Le registre scientifique comprend 511 dossiers de recherche. L’interface de contribution présente séparément 117 thèmes sélectionnés. Les 394 entrées générées et les onze ajouts sélectionnés sont des programmes de recherche, pas des technologies démontrées."],
    es:["511 programas de investigación registrados · 117 temas de contribución","El registro científico contiene 511 expedientes de investigación. La interfaz de contribución presenta por separado 117 temas seleccionados. Las 394 entradas generadas y las once incorporaciones seleccionadas son programas de investigación, no tecnologías demostradas."],
    de:["511 registrierte Forschungsprogramme · 117 Beitragsthemen","Das wissenschaftliche Register enthält 511 Forschungsakten. Die Beitragsoberfläche zeigt davon getrennt 117 ausgewählte Themen. Die 394 generierten Einträge und elf kuratierten Ergänzungen sind Forschungsprogramme, keine nachgewiesenen Technologien."],
    it:["511 programmi di ricerca registrati · 117 temi di contributo","Il registro scientifico contiene 511 dossier di ricerca. L’interfaccia dei contributi presenta separatamente 117 temi selezionati. Le 394 voci generate e le undici aggiunte selezionate sono programmi di ricerca, non tecnologie dimostrate."],
    pt:["511 programas de pesquisa registrados · 117 temas de contribuição","O registro científico contém 511 dossiês de pesquisa. A interface de contribuição apresenta separadamente 117 temas selecionados. As 394 entradas geradas e as onze adições selecionadas são programas de pesquisa, não tecnologias demonstradas."],
    nl:["511 geregistreerde onderzoeksprogramma’s · 117 bijdragethema’s","Het wetenschappelijke register bevat 511 onderzoeksdossiers. De bijdrage-interface toont daarnaast 117 geselecteerde thema’s. De 394 gegenereerde items en elf geselecteerde toevoegingen zijn onderzoeksprogramma’s, geen bewezen technologieën."],
    ru:["511 зарегистрированных исследовательских программ · 117 тем для поддержки","Научный реестр содержит 511 исследовательских досье. Интерфейс поддержки отдельно представляет 117 выбранных тем. 394 сгенерированные записи и одиннадцать отобранных дополнений — исследовательские программы, а не доказанные технологии."],
    uk:["511 зареєстрованих дослідницьких програм · 117 тем для підтримки","Науковий реєстр містить 511 дослідницьких досьє. Інтерфейс внесків окремо представляє 117 вибраних тем. 394 згенеровані записи та одинадцять відібраних доповнень — дослідницькі програми, а не доведені технології."],
    ar:["511 برنامجًا بحثيًا مسجلًا · 117 موضوع للمساهمة","يضم السجل العلمي 511 ملف بحثي. وتعرض واجهة المساهمات بشكل منفصل 117 موضوع مختار. الإدخالات الـ394 المولّدة والإضافات الإحدى عشرة المختارة هي برامج بحثية وليست تقنيات مثبتة."],
    he:["511 תוכניות מחקר רשומות · 117 נושאים לתרומה","המאגר המדעי כולל 511 תיקי מחקר. ממשק התרומות מציג בנפרד 117 נושאים נבחרים. 394 הרשומות שנוצרו ואחת עשרה התוספות שנבחרו הן תוכניות מחקר, ולא טכנולוגיות מוכחות."],
    ja:["登録済み研究プログラム511件 · 支援テーマ117件","科学研究レジストリには511件の研究記録があります。寄付インターフェースでは別途117件のテーマを提示します。生成された394件と選定された11件の追加項目は研究プログラムであり、実証済みの技術ではありません。"],
    ko:["등록된 연구 프로그램 511개 · 후원 주제 117개","과학 연구 레지스트리에는 511개의 연구 기록이 있습니다. 기여 인터페이스에는 별도로 117개의 선택된 주제가 표시됩니다. 생성된 394개 항목과 선정된 11개 추가 항목은 연구 프로그램이며 입증된 기술이 아닙니다."],
    zh:["已登记的研究计划 511 项 · 贡献主题 117 项","科学登记库包含 511 份研究档案。贡献界面另行展示 117 个精选主题。生成的 394 项和精选新增的 10 项均为研究计划，并非已证实的技术。"],
    hi:["511 पंजीकृत अनुसंधान कार्यक्रम · 117 योगदान विषय","वैज्ञानिक रजिस्टर में 511 अनुसंधान अभिलेख हैं। योगदान इंटरफ़ेस अलग से 117 चुने हुए विषय दिखाता है। 394 उत्पन्न प्रविष्टियाँ और ग्यारह चयनित अतिरिक्त प्रविष्टियाँ अनुसंधान कार्यक्रम हैं, प्रमाणित तकनीकें नहीं。"]
  };
  function apply() {
    const language = lang();
    const copy = catalogueCopy[language] || catalogueCopy.en;
    const count = document.getElementById("technology-catalogue-count");
    const note = document.querySelector(".technology-catalogue-note");
    if (count && count.textContent !== copy[0]) count.textContent = copy[0];
    if (note && note.textContent !== copy[1]) note.textContent = copy[1];
    document.querySelectorAll("#bot-current-technology-title,.technology-card h3,[data-technology-title]").forEach(el => {
      const original = el.dataset.ssswetOriginalTitle || el.textContent.trim();
      if (!el.dataset.ssswetOriginalTitle) el.dataset.ssswetOriginalTitle = original;
      const target = isFr ? frenchTitle(original) : original;
      if (el.textContent !== target) el.textContent = target;
    });
    document.querySelectorAll("body *:not(script):not(style)").forEach(el => {
      if (el.children.length) return;
      const text = el.textContent || "";
      const next = text.replace(/64\s*\/\s*117/g, "64 / 511").replace(/\/\s*117(\s+programmes?\b)/gi, "/ 511$1");
      if (next !== text) el.textContent = next;
    });
  }
  const start = () => {
    apply();
    document.getElementById("language")?.addEventListener("change", () => setTimeout(apply, 0));
    window.addEventListener("ssswet-language-changed", () => setTimeout(apply, 0));
    const observer = new MutationObserver(() => apply());
    observer.observe(document.body, {childList:true, subtree:true});
  };
  if (document.body) start(); else document.addEventListener("DOMContentLoaded", start, {once:true});
})();
