(() => {
  "use strict";
  const exact = {
    "Sentient AI":"IA sentiente","Human-like Robots":"Robots humanoïdes","Spacetime":"Espace-temps","Timetravel":"Voyage temporel","Artificial Gravity":"Gravité artificielle","Planetary Monitoring":"Surveillance planétaire","Black Hole Observation":"Observation des trous noirs","Event Horizon Imaging":"Imagerie des horizons des événements","Gravitational Wave Navigation":"Navigation par ondes gravitationnelles","Relativistic Spacecraft":"Vaisseaux spatiaux relativistes","Jetpack":"Système de propulsion individuel","Antimatter Research":"Recherche sur l'antimatière","Beamed Energy Propulsion":"Propulsion par énergie dirigée","Solar Sail Navigation":"Navigation par voile solaire","Plasma Propulsion":"Propulsion plasma","Space Life Support":"Support-vie spatial","Cosmic Ray Shielding":"Blindage contre les rayons cosmiques","Cryogenic Hibernation":"Hibernation cryogénique","Orbital Manufacturing":"Fabrication orbitale","Lunar Resource Systems":"Systèmes de ressources lunaires","Radiation Protection":"Protection contre les rayonnements","Armor":"Protection corporelle","Disaster Resilience":"Résilience aux catastrophes","Extreme Thermal Protection":"Protection thermique extrême","Impact Absorbing Materials":"Matériaux absorbant les impacts","Cleanenergy":"Énergie propre","Fusion Energy":"Énergie de fusion","Superconducting Grid":"Réseau supraconducteur","Energy Storage":"Stockage de l'énergie","Metamaterials":"Métamatériaux","Self Healing Materials":"Matériaux autoréparants","Smart Adaptive Materials":"Matériaux adaptatifs intelligents","Longevity":"Longévité en bonne santé","Medical Nanotechnology":"Nanotechnologies médicales","Organ Regeneration":"Régénération des organes","Precision Gene Therapies":"Thérapies géniques de précision","Artificial Organs":"Organes artificiels","Neurointerfaces":"Neurointerfaces","Robotics Exoskeletons":"Exosquelettes robotiques","Sensory Augmentation":"Augmentation sensorielle","Animal Health":"Santé animale","Climate":"Climat","Biodiversity":"Biodiversité","Wildlife":"Protection de la faune","Oceans":"Océans","Reforestation":"Reboisement","Agriculture":"Agriculture","Carbon Monitoring":"Surveillance du carbone","Pollinators":"Protection des pollinisateurs","Air Quality":"Qualité de l'air","Water":"Eau","Food Systems":"Systèmes alimentaires","Sanitation":"Assainissement","Wildfire Prediction":"Prévision des incendies de forêt","Autonomous Labs":"Laboratoires autonomes","Swarm Robotics":"Robotique en essaim","Autonomous Disaster Robots":"Robots autonomes pour les catastrophes","Mobility":"Mobilité","Accessibility":"Accessibilité","Advanced Computing":"Calcul avancé","Quantum Networks":"Réseaux quantiques","Quantum Sensing":"Capteurs quantiques","Neuromorphic Computing":"Calcul neuromorphique","Photonic Computing":"Calcul photonique","Distributed Scientific Computing":"Calcul scientifique distribué","Translator":"Traduction humain-machine","Interstellar Communication":"Communication interstellaire","Universal Translation Systems":"Systèmes de traduction universelle","Public Health":"Santé publique","Education":"Éducation"
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
    en:["1000 registered research programmes · 606 contribution themes","The scientific registry contains 1000 research dossiers. The contribution interface separately presents 606 selected themes. The 882 generated entries and twelve curated additions are research programmes, not demonstrated technologies."],
    fr:["1000 programmes de recherche enregistrés · 606 thèmes de contribution","Le registre scientifique comprend 1000 dossiers de recherche. L’interface de contribution présente séparément 606 thèmes sélectionnés. Les 882 entrées générées et les douze ajouts sélectionnés sont des programmes de recherche, pas des technologies démontrées."],
    es:["1000 programas de investigación registrados · 606 temas de contribución","El registro científico contiene 1000 expedientes de investigación. La interfaz de contribución presenta por separado 606 temas seleccionados. Las 882 entradas generadas y las doce incorporaciones seleccionadas son programas de investigación, no tecnologías demostradas."],
    de:["1000 registrierte Forschungsprogramme · 606 Beitragsthemen","Das wissenschaftliche Register enthält 1000 Forschungsakten. Die Beitragsoberfläche zeigt davon getrennt 606 ausgewählte Themen. Die 882 generierten Einträge und elf kuratierten Ergänzungen sind Forschungsprogramme, keine nachgewiesenen Technologien."],
    it:["1000 programmi di ricerca registrati · 606 temi di contributo","Il registro scientifico contiene 1000 dossier di ricerca. L’interfaccia dei contributi presenta separatamente 606 temi selezionati. Le 882 voci generate e le dodici aggiunte selezionate sono programmi di ricerca, non tecnologie dimostrate."],
    pt:["1000 programas de pesquisa registrados · 606 temas de contribuição","O registro científico contém 1000 dossiês de pesquisa. A interface de contribuição apresenta separadamente 606 temas selecionados. As 882 entradas geradas e as doze adições selecionadas são programas de pesquisa, não tecnologias demonstradas."],
    nl:["1000 geregistreerde onderzoeksprogramma’s · 606 bijdragethema’s","Het wetenschappelijke register bevat 1000 onderzoeksdossiers. De bijdrage-interface toont daarnaast 606 geselecteerde thema’s. De 882 gegenereerde items en twaalf geselecteerde toevoegingen zijn onderzoeksprogramma’s, geen bewezen technologieën."],
    ru:["1000 зарегистрированных исследовательских программ · 606 тем для поддержки","Научный реестр содержит 1000 исследовательских досье. Интерфейс поддержки отдельно представляет 606 выбранных тем. 882 сгенерированные записи и двенадцать отобранных дополнений — исследовательские программы, а не доказанные технологии."],
    uk:["1000 зареєстрованих дослідницьких програм · 606 тем для підтримки","Науковий реєстр містить 1000 дослідницьких досьє. Інтерфейс внесків окремо представляє 606 вибраних тем. 882 згенеровані записи та дванадцять відібраних доповнень — дослідницькі програми, а не доведені технології."],
    ar:["1000 برنامجًا بحثيًا مسجلًا · 606 موضوع للمساهمة","يضم السجل العلمي 1000 ملف بحثي. وتعرض واجهة المساهمات بشكل منفصل 606 موضوع مختار. الإدخالات الـ882 المولّدة والإضافات الاثنتا عشرة المختارة هي برامج بحثية وليست تقنيات مثبتة."],
    he:["1000 תוכניות מחקר רשומות · 606 נושאים לתרומה","המאגר המדעי כולל 1000 תיקי מחקר. ממשק התרומות מציג בנפרד 606 נושאים נבחרים. 882 הרשומות שנוצרו ושתים עשרה התוספות שנבחרו הן תוכניות מחקר, ולא טכנולוגיות מוכחות."],
    ja:["登録済み研究プログラム1000件 · 支援テーマ606件","科学研究レジストリには1000件の研究記録があります。寄付インターフェースでは別途606件のテーマを提示します。生成された882件と選定された12件の追加項目は研究プログラムであり、実証済みの技術ではありません。"],
    ko:["등록된 연구 프로그램 1000개 · 후원 주제 606개","과학 연구 레지스트리에는 1000개의 연구 기록이 있습니다. 기여 인터페이스에는 별도로 606개의 선택된 주제가 표시됩니다. 생성된 882개 항목과 선정된 12개 추가 항목은 연구 프로그램이며 입증된 기술이 아닙니다."],
    zh:["已登记的研究计划 1000 项 · 贡献主题 606 项","科学登记库包含 1000 份研究档案。贡献界面另行展示 606 个精选主题。生成的 882 项和精选新增的 12 项均为研究计划，并非已证实的技术。"],
    hi:["1000 पंजीकृत अनुसंधान कार्यक्रम · 606 योगदान विषय","वैज्ञानिक रजिस्टर में 1000 अनुसंधान अभिलेख हैं। योगदान इंटरफ़ेस अलग से 606 चुने हुए विषय दिखाता है। 882 उत्पन्न प्रविष्टियाँ और बारह चयनित अतिरिक्त प्रविष्टियाँ अनुसंधान कार्यक्रम हैं, प्रमाणित तकनीकें नहीं。"]
  };
  function updateCatalogueCopy() {
    const language = lang();
    const copy = catalogueCopy[language] || catalogueCopy.en;
    const count = document.getElementById("technology-catalogue-count");
    const note = document.querySelector(".technology-catalogue-note");
    if (count && count.textContent !== copy[0]) count.textContent = copy[0];
    if (note && note.textContent !== copy[1]) note.textContent = copy[1];
  }

  function translateTitle(element, language) {
    if (!element || element.nodeType !== 1) return;
    const original = element.dataset.ssswetOriginalTitle || element.textContent.trim();
    if (!element.dataset.ssswetOriginalTitle) element.dataset.ssswetOriginalTitle = original;
    const target = language === "fr" ? frenchTitle(original) : original;
    if (element.textContent !== target) element.textContent = target;
  }

  function translateTitles(root, language) {
    if (!root) return;
    if (root.nodeType === 1 && root.matches("#bot-current-technology-title,.technology-card h3,[data-technology-title]")) {
      translateTitle(root, language);
    }
    if (root.querySelectorAll) {
      root.querySelectorAll("#bot-current-technology-title,.technology-card h3,[data-technology-title]")
        .forEach(element => translateTitle(element, language));
    }
  }

  function applyAll() {
    const language = lang();
    updateCatalogueCopy();
    translateTitles(document.getElementById("technology-grid"), language);
    translateTitles(document.getElementById("bot-current-technology-title"), language);
    document.querySelectorAll("[data-technology-title]").forEach(element => translateTitle(element, language));
  }

  const start = () => {
    const catalogue = document.getElementById("technology-grid");
    let observerScheduled = false;
    let pendingRoots = new Set();

    applyAll();
    document.getElementById("language")?.addEventListener("change", () => setTimeout(applyAll, 0));
    window.addEventListener("ssswet-language-changed", () => setTimeout(applyAll, 0));

    if (catalogue) {
      const observer = new MutationObserver(records => {
        for (const record of records) {
          for (const node of record.addedNodes) {
            if (node.nodeType === 1) pendingRoots.add(node);
          }
        }
        if (observerScheduled || pendingRoots.size === 0) return;
        observerScheduled = true;
        requestAnimationFrame(() => {
          observerScheduled = false;
          const language = lang();
          for (const root of pendingRoots) translateTitles(root, language);
          pendingRoots.clear();
        });
      });
      observer.observe(catalogue, { childList: true, subtree: true });
    }
  };
  if (document.body) start(); else document.addEventListener("DOMContentLoaded", start, {once:true});
})();
