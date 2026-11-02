(() => {
  "use strict";
  const groups = {"space":{"astrophysics":["spacetime","timetravel","artificialGravity","planetaryMonitoring","blackHoleObservation","blackHoleProbeSystems","blackHoleResilientVehicles","eventHorizonImaging","gravitationalWaveNavigation","relativisticSpacecraft"],"propulsion":["jetpack","antimatterResearch","beamedEnergyPropulsion","solarSailNavigation","plasmaPropulsion","interstellarProbeArchitecture"],"spaceHabitats":["spaceLifeSupport","deepSpaceRadiationShelters","cosmicRayShielding","cryogenicHibernation","orbitalManufacturing","lunarResourceSystems","marsTerraformingAssessment"]},"protection":{"nuclearProtection":["nuclearBlastResilience","radiationProtection","radiationDosimetryNetworks","nuclearFalloutDecontamination","electromagneticPulseResilience"],"protectiveEngineering":["armor","disasterResilience","extremeThermalProtection","impactAbsorbingMaterials","modularProtectiveArmor","blastAndImpactProtection","environmentalProtectionSuit","protectivePhysiologicalMonitoring"]},"energy":{"cleanGeneration":["cleanenergy","fusionEnergy","superconductingGrid","ambientEnergyHarvesting","spaceSolarPower","zeroCarbonIndustrialHeat"],"energyStorage":["energyStorage","thermoelectricSystems","gridScaleThermalStorage"]},"materials":{"adaptiveMaterials":["materials","metamaterials","selfHealingMaterials","aerogelSystems","smartAdaptiveMaterials"],"structuralMaterials":["circularEconomy","ultraHighTemperatureMaterials","transparentCeramics"]},"life":{"regenerativeMedicine":["cellular","longevity","medicalNanotechnology","organRegeneration","syntheticBiologyBiosafety","precisionGeneTherapies","bioelectronicMedicine","artificialOrgans","medicalDigitalTwins"],"humanAugmentation":["neurointerfaces","roboticsExoskeletons","sensoryAugmentation","adaptiveExosuits","closedLoopNeuroprosthetics","poweredLoadAssistExoskeletons","rescueMobilityExoskeletons"],"animalCare":["animalHealth"]},"environment":{"ecosystemRestoration":["climate","biodiversity","wildlife","oceans","reforestation","agriculture","carbonMonitoring","pollinators","atmosphericRestoration","carbonRemoval","oceanAlkalinityMonitoring","geoengineeringAssessment","ecosystemDigitalTwins"],"climateResilience":["airQuality","water","foodSystems","sanitation","wildfirePrediction","environmentalEventReplay"]},"robotics":{"autonomousResearch":["autonomousLabs","swarmRobotics","embodiedAI","autonomousDisasterRobots"],"assistiveRobotics":["mobility","accessibility"],"sceneSimulation":["forensicSceneReconstruction","predictiveSceneSimulation","persistent3DMapping","motionTrajectoryReconstruction"]},"society":{"advancedComputing":["advancedComputing","quantumNetworks","quantumSensing","neuromorphicComputing","photonicComputing","faultTolerantQuantumComputing","distributedScientificComputing"],"communication":["translator","interstellarCommunication","universalTranslationSystems"],"publicKnowledge":["publicHealth","education"],"spatiotemporalSystems":["virtualTimeTravelMap","spatiotemporalDigitalTwin","geospatialSensorFusion","privacyPreservingCapture","uncertaintyAwareWorldModel"]}};
  const categoryKeys = Object.keys(groups);
  const subKeys = [...new Set(Object.values(groups).flatMap(group => Object.keys(group)))];
  const translations = {"en":["Space science and exploration","Civilian protection and resilience","Energy systems","Advanced materials","Life sciences and human systems","Environmental stewardship","Robotics and autonomous systems","Knowledge and communication","Astrophysics and extreme gravity","Propulsion and interstellar travel","Space habitats and life support","Nuclear-event protection","Protective engineering","Clean energy generation","Energy storage and conversion","Adaptive and functional materials","Structural and high-temperature materials","Regenerative medicine","Human augmentation and assistive systems","Animal health and welfare","Ecosystem restoration","Climate resilience and monitoring","Autonomous research and field robotics","Assistive robotics and mobility","Advanced scientific computing","Communication and translation","Public knowledge and health"],"fr":["Sciences et exploration spatiales","Protection civile et résilience","Systèmes énergétiques","Matériaux avancés","Sciences du vivant et systèmes humains","Protection de l’environnement","Robotique et systèmes autonomes","Connaissances et communication","Astrophysique et gravité extrême","Propulsion et voyage interstellaire","Habitats spatiaux et support-vie","Protection contre les événements nucléaires","Ingénierie de protection","Production d’énergie propre","Stockage et conversion de l’énergie","Matériaux adaptatifs et fonctionnels","Matériaux structurels et haute température","Médecine régénérative","Augmentation humaine et assistance","Santé et bien-être animal","Restauration des écosystèmes","Résilience et surveillance climatiques","Recherche autonome et robotique de terrain","Robotique d’assistance et mobilité","Calcul scientifique avancé","Communication et traduction","Connaissances publiques et santé"],"es":["Ciencia y exploración espacial","Protección civil y resiliencia","Sistemas energéticos","Materiales avanzados","Ciencias de la vida y sistemas humanos","Protección ambiental","Robótica y sistemas autónomos","Conocimiento y comunicación","Astrofísica y gravedad extrema","Propulsión y viajes interestelares","Hábitats espaciales y soporte vital","Protección ante eventos nucleares","Ingeniería de protección","Generación de energía limpia","Almacenamiento y conversión de energía","Materiales adaptativos y funcionales","Materiales estructurales y de alta temperatura","Medicina regenerativa","Aumento humano y sistemas de asistencia","Salud y bienestar animal","Restauración de ecosistemas","Resiliencia y seguimiento climático","Investigación autónoma y robótica de campo","Robótica asistencial y movilidad","Computación científica avanzada","Comunicación y traducción","Conocimiento público y salud"],"de":["Weltraumwissenschaft und Erforschung","Zivilschutz und Resilienz","Energiesysteme","Fortschrittliche Materialien","Lebenswissenschaften und menschliche Systeme","Umweltschutz","Robotik und autonome Systeme","Wissen und Kommunikation","Astrophysik und extreme Gravitation","Antrieb und interstellare Reisen","Weltraumhabitate und Lebenserhaltung","Schutz vor nuklearen Ereignissen","Schutztechnik","Saubere Energieerzeugung","Energiespeicherung und -umwandlung","Adaptive und funktionale Materialien","Struktur- und Hochtemperaturmaterialien","Regenerative Medizin","Menschliche Erweiterung und Assistenzsysteme","Tiergesundheit und Wohlergehen","Ökosystemwiederherstellung","Klimaanpassung und Überwachung","Autonome Forschung und Feldrobotik","Assistenzrobotik und Mobilität","Fortgeschrittenes wissenschaftliches Rechnen","Kommunikation und Übersetzung","Öffentliches Wissen und Gesundheit"],"it":["Scienza ed esplorazione spaziale","Protezione civile e resilienza","Sistemi energetici","Materiali avanzati","Scienze della vita e sistemi umani","Tutela ambientale","Robotica e sistemi autonomi","Conoscenza e comunicazione","Astrofisica e gravità estrema","Propulsione e viaggi interstellari","Habitat spaziali e supporto vitale","Protezione dagli eventi nucleari","Ingegneria della protezione","Generazione di energia pulita","Accumulo e conversione energetica","Materiali adattivi e funzionali","Materiali strutturali e per alte temperature","Medicina rigenerativa","Potenziamento umano e sistemi assistivi","Salute e benessere animale","Ripristino degli ecosistemi","Resilienza e monitoraggio climatico","Ricerca autonoma e robotica sul campo","Robotica assistiva e mobilità","Calcolo scientifico avanzato","Comunicazione e traduzione","Conoscenza pubblica e salute"],"pt":["Ciência e exploração espacial","Proteção civil e resiliência","Sistemas energéticos","Materiais avançados","Ciências da vida e sistemas humanos","Proteção ambiental","Robótica e sistemas autónomos","Conhecimento e comunicação","Astrofísica e gravidade extrema","Propulsão e viagens interestelares","Habitats espaciais e suporte de vida","Proteção contra eventos nucleares","Engenharia de proteção","Geração de energia limpa","Armazenamento e conversão de energia","Materiais adaptativos e funcionais","Materiais estruturais e de alta temperatura","Medicina regenerativa","Aumento humano e sistemas de assistência","Saúde e bem-estar animal","Restauro de ecossistemas","Resiliência e monitorização climática","Investigação autónoma e robótica de campo","Robótica assistiva e mobilidade","Computação científica avançada","Comunicação e tradução","Conhecimento público e saúde"],"nl":["Ruimtewetenschap en verkenning","Civiele bescherming en veerkracht","Energiesystemen","Geavanceerde materialen","Levenswetenschappen en menselijke systemen","Milieubeheer","Robotica en autonome systemen","Kennis en communicatie","Astrofysica en extreme zwaartekracht","Voortstuwing en interstellaire reizen","Ruimtehabitats en levensondersteuning","Bescherming tegen nucleaire gebeurtenissen","Beschermingstechniek","Schone energieopwekking","Energieopslag en -omzetting","Adaptieve en functionele materialen","Structurele materialen en materialen voor hoge temperaturen","Regeneratieve geneeskunde","Menselijke uitbreiding en hulpmiddelen","Diergezondheid en welzijn","Herstel van ecosystemen","Klimaatbestendigheid en monitoring","Autonoom onderzoek en veldrobotica","Assisterende robotica en mobiliteit","Geavanceerde wetenschappelijke computing","Communicatie en vertaling","Publieke kennis en gezondheid"],"ru":["Космическая наука и исследования","Гражданская защита и устойчивость","Энергетические системы","Передовые материалы","Науки о жизни и человеческие системы","Охрана окружающей среды","Робототехника и автономные системы","Знания и коммуникации","Астрофизика и экстремальная гравитация","Движение и межзвёздные путешествия","Космические жилые системы и жизнеобеспечение","Защита от ядерных событий","Защитная инженерия","Чистая генерация энергии","Хранение и преобразование энергии","Адаптивные и функциональные материалы","Конструкционные и высокотемпературные материалы","Регенеративная медицина","Расширение возможностей человека и ассистивные системы","Здоровье и благополучие животных","Восстановление экосистем","Климатическая устойчивость и мониторинг","Автономные исследования и полевая робототехника","Вспомогательная робототехника и мобильность","Передовые научные вычисления","Связь и перевод","Общественные знания и здоровье"],"uk":["Космічна наука та дослідження","Цивільний захист і стійкість","Енергетичні системи","Передові матеріали","Науки про життя та людські системи","Охорона довкілля","Робототехніка й автономні системи","Знання та комунікація","Астрофізика й екстремальна гравітація","Рушійні системи та міжзоряні подорожі","Космічні середовища та життєзабезпечення","Захист від ядерних подій","Захисна інженерія","Чисте виробництво енергії","Зберігання та перетворення енергії","Адаптивні й функціональні матеріали","Конструкційні та високотемпературні матеріали","Регенеративна медицина","Розширення можливостей людини й допоміжні системи","Здоров’я та добробут тварин","Відновлення екосистем","Кліматична стійкість і моніторинг","Автономні дослідження та польова робототехніка","Допоміжна робототехніка та мобільність","Передові наукові обчислення","Комунікація та переклад","Громадські знання та здоров’я"],"ar":["علوم الفضاء واستكشافه","الحماية المدنية والقدرة على الصمود","أنظمة الطاقة","المواد المتقدمة","علوم الحياة والأنظمة البشرية","رعاية البيئة","الروبوتات والأنظمة المستقلة","المعرفة والاتصالات","الفيزياء الفلكية والجاذبية القصوى","الدفع والرحلات بين النجوم","الموائل الفضائية ودعم الحياة","الحماية من الأحداث النووية","هندسة الحماية","توليد الطاقة النظيفة","تخزين الطاقة وتحويلها","المواد التكيفية والوظيفية","المواد الإنشائية ومواد درجات الحرارة العالية","الطب التجديدي","تعزيز القدرات البشرية والأنظمة المساعدة","صحة الحيوان ورفاهيته","استعادة النظم البيئية","القدرة المناخية على الصمود والرصد","البحث المستقل وروبوتات الميدان","الروبوتات المساعدة والتنقل","الحوسبة العلمية المتقدمة","الاتصالات والترجمة","المعرفة العامة والصحة"],"he":["מדעי החלל והחקירה","הגנה אזרחית וחוסן","מערכות אנרגיה","חומרים מתקדמים","מדעי החיים ומערכות אנושיות","שמירה על הסביבה","רובוטיקה ומערכות אוטונומיות","ידע ותקשורת","אסטרופיזיקה וכבידה קיצונית","הנעה ומסעות בין-כוכביים","בתי גידול בחלל ותמיכת חיים","הגנה מפני אירועים גרעיניים","הנדסת מיגון","ייצור אנרגיה נקייה","אגירת אנרגיה והמרתה","חומרים מסתגלים ותפקודיים","חומרים מבניים וחומרים לטמפרטורות גבוהות","רפואה רגנרטיבית","הרחבת יכולות אנושיות ומערכות מסייעות","בריאות ורווחת בעלי חיים","שיקום מערכות אקולוגיות","חוסן אקלימי וניטור","מחקר אוטונומי ורובוטיקה בשטח","רובוטיקה מסייעת וניידות","מחשוב מדעי מתקדם","תקשורת ותרגום","ידע ציבורי ובריאות"],"ja":["宇宙科学と探査","市民保護とレジリエンス","エネルギーシステム","先端材料","生命科学と人間システム","環境保全","ロボット工学と自律システム","知識とコミュニケーション","天体物理学と極限重力","推進と恒星間航行","宇宙居住施設と生命維持","核事象からの保護","保護工学","クリーンエネルギー生成","エネルギー貯蔵と変換","適応型・機能性材料","構造材料と超高温材料","再生医療","人間拡張と支援システム","動物の健康と福祉","生態系の回復","気候レジリエンスと監視","自律型研究と現場ロボット","支援ロボットと移動支援","高度な科学計算","通信と翻訳","公共知識と健康"],"ko":["우주 과학 및 탐사","시민 보호 및 회복력","에너지 시스템","첨단 소재","생명과학 및 인간 시스템","환경 관리","로봇공학 및 자율 시스템","지식 및 커뮤니케이션","천체물리학 및 극한 중력","추진 및 성간 여행","우주 거주지 및 생명 유지","핵 사건 보호","보호 공학","청정 에너지 생산","에너지 저장 및 변환","적응형 및 기능성 소재","구조 및 초고온 소재","재생 의학","인간 능력 확장 및 보조 시스템","동물 건강 및 복지","생태계 복원","기후 회복력 및 모니터링","자율 연구 및 현장 로봇","보조 로봇 및 이동성","첨단 과학 컴퓨팅","통신 및 번역","공공 지식 및 보건"],"zh":["空间科学与探索","民用防护与韧性","能源系统","先进材料","生命科学与人体系统","环境保护","机器人与自主系统","知识与通信","天体物理与极端引力","推进与星际旅行","空间栖息地与生命保障","核事件防护","防护工程","清洁能源发电","能源储存与转换","自适应与功能材料","结构与超高温材料","再生医学","人体增强与辅助系统","动物健康与福利","生态系统修复","气候韧性与监测","自主研究与现场机器人","辅助机器人与移动能力","先进科学计算","通信与翻译","公共知识与健康"],"hi":["अंतरिक्ष विज्ञान और अन्वेषण","नागरिक सुरक्षा और लचीलापन","ऊर्जा प्रणालियाँ","उन्नत सामग्री","जीवन विज्ञान और मानव प्रणालियाँ","पर्यावरण संरक्षण","रोबोटिक्स और स्वायत्त प्रणालियाँ","ज्ञान और संचार","खगोल भौतिकी और चरम गुरुत्व","प्रणोदन और अंतरतारकीय यात्रा","अंतरिक्ष आवास और जीवन समर्थन","परमाणु घटनाओं से सुरक्षा","सुरक्षात्मक अभियांत्रिकी","स्वच्छ ऊर्जा उत्पादन","ऊर्जा भंडारण और रूपांतरण","अनुकूली और कार्यात्मक सामग्री","संरचनात्मक और उच्च-तापमान सामग्री","पुनर्योजी चिकित्सा","मानव क्षमता-वृद्धि और सहायक प्रणालियाँ","पशु स्वास्थ्य और कल्याण","पारिस्थितिकी तंत्र की बहाली","जलवायु लचीलापन और निगरानी","स्वायत्त अनुसंधान और फील्ड रोबोटिक्स","सहायक रोबोटिक्स और गतिशीलता","उन्नत वैज्ञानिक कंप्यूटिंग","संचार और अनुवाद","सार्वजनिक ज्ञान और स्वास्थ्य"]};
  const root = document.getElementById("technology-grid");
  if (!root) return;
  const controls = document.createElement("div");
  controls.className = "technology-catalogue-controls";
  controls.innerHTML = '<label><span id="tech-search-label">Search technologies</span><input id="tech-search" type="search" autocomplete="off"></label><label><span id="tech-category-label">Category</span><select id="tech-category"></select></label><label><span id="tech-subcategory-label">Subcategory</span><select id="tech-subcategory"></select></label>';
  const heading = document.querySelector(".technology-heading");
  heading?.append(controls);
  const labels = () => {
    const lang = (document.documentElement.lang || document.getElementById("language")?.value || "en").toLowerCase().split("-")[0];
    const values = translations[lang] || translations.en;
    return {
      lang, values,
      search: ({en:"Search technologies",fr:"Rechercher une technologie",es:"Buscar tecnologías",de:"Technologien suchen",it:"Cerca tecnologie",pt:"Pesquisar tecnologias",nl:"Technologieën zoeken",ru:"Поиск технологий",uk:"Пошук технологій",ar:"البحث عن التقنيات",he:"חיפוש טכנולוגיות",ja:"技術を検索",ko:"기술 검색",zh:"搜索技术",hi:"तकनीक खोजें"})[lang] || "Search technologies",
      category: ({en:"Category",fr:"Catégorie",es:"Categoría",de:"Kategorie",it:"Categoria",pt:"Categoria",nl:"Categorie",ru:"Категория",uk:"Категорія",ar:"الفئة",he:"קטגוריה",ja:"カテゴリー",ko:"카테고리",zh:"类别",hi:"श्रेणी"})[lang] || "Category",
      subcategory: ({en:"Subcategory",fr:"Sous-catégorie",es:"Subcategoría",de:"Unterkategorie",it:"Sottocategoria",pt:"Subcategoria",nl:"Subcategorie",ru:"Подкатегория",uk:"Підкатегорія",ar:"الفئة الفرعية",he:"תת-קטגוריה",ja:"サブカテゴリー",ko:"하위 범주",zh:"子类别",hi:"उपश्रेणी"})[lang] || "Subcategory",
      all: ({en:"All",fr:"Toutes",es:"Todas",de:"Alle",it:"Tutte",pt:"Todas",nl:"Alle",ru:"Все",uk:"Усі",ar:"الكل",he:"הכול",ja:"すべて",ko:"전체",zh:"全部",hi:"सभी"})[lang] || "All"
    };
  };
  const cardMeta = new Map();
  Object.entries(groups).forEach(([category, subgroups]) => Object.entries(subgroups).forEach(([subcategory, keys]) => keys.forEach(key => cardMeta.set(key,{category,subcategory}))));
  const categorySelect = controls.querySelector("#tech-category");
  const subcategorySelect = controls.querySelector("#tech-subcategory");
  const searchInput = controls.querySelector("#tech-search");
  const categoryNodes = new Map();
  const subcategoryNodes = new Map();
  const sourceCards = [...root.querySelectorAll(".technology-card")];
  function buildOptions(select, values, selected, allLabel, localized) {
    select.replaceChildren();
    const all = document.createElement("option"); all.value=""; all.textContent=allLabel; select.append(all);
    values.forEach((key,index) => { const option=document.createElement("option"); option.value=key; option.textContent=localized[index]; select.append(option); });
    if (values.includes(selected)) select.value=selected;
  }
  function localizeAndArrange() {
    const l=labels();
    document.getElementById("tech-search-label").textContent=l.search;
    document.getElementById("tech-category-label").textContent=l.category;
    document.getElementById("tech-subcategory-label").textContent=l.subcategory;
    buildOptions(categorySelect,categoryKeys,categorySelect.value,l.all,l.values.slice(0,8));
    const subLabels=l.values.slice(8);
    buildOptions(subcategorySelect,subKeys,subcategorySelect.value,l.all,subKeys.map(key=>subLabels[["astrophysics","propulsion","spaceHabitats","nuclearProtection","protectiveEngineering","cleanGeneration","energyStorage","adaptiveMaterials","structuralMaterials","regenerativeMedicine","humanAugmentation","animalCare","ecosystemRestoration","climateResilience","autonomousResearch","assistiveRobotics","advancedComputing","communication","publicKnowledge"].indexOf(key)]));
    const lang=l.lang;
    sourceCards.forEach(card=>{
      const button=card.querySelector("button[data-tech]");
      if(!button)return;
      const key=button.dataset.tech;
      const meta=cardMeta.get(key);
      if(!meta)return;
      const item=(window.SSSWET_TECHNOLOGIES||{})[key];
      const name=item?.[lang]?.[0] || item?.en?.[0] || key;
      const description=item?.[lang]?.[1] || item?.en?.[1] || "";
      card.querySelector("h3").textContent=name;
      card.querySelector("p").textContent=description;
      let tag=card.querySelector(".technology-category-tag");
      if(!tag){tag=document.createElement("small");tag.className="technology-category-tag";card.insertBefore(tag,card.querySelector("h3"));}
      tag.textContent=l.values[categoryKeys.indexOf(meta.category)]+" · "+l.values[8+["astrophysics","propulsion","spaceHabitats","nuclearProtection","protectiveEngineering","cleanGeneration","energyStorage","adaptiveMaterials","structuralMaterials","regenerativeMedicine","humanAugmentation","animalCare","ecosystemRestoration","climateResilience","autonomousResearch","assistiveRobotics","advancedComputing","communication","publicKnowledge"].indexOf(meta.subcategory)];
      button.textContent=lang==="fr"?"Découvrir et contribuer":lang==="es"?"Explorar y contribuir":lang==="de"?"Entdecken & beitragen":lang==="it"?"Esplora e contribuisci":lang==="pt"?"Explorar e contribuir":lang==="nl"?"Ontdek & draag bij":lang==="ru"?"Изучить и поддержать":lang==="uk"?"Дізнатися й підтримати":lang==="ar"?"استكشف وساهم":lang==="he"?"לגלות ולתרום":lang==="ja"?"詳しく見る・支援する":lang==="ko"?"살펴보고 참여하기":lang==="zh"?"了解并支持":lang==="hi"?"जानें और योगदान दें":"Explore & contribute";
    });
    renderFilters();
  }
  function renderFilters() {
    const selectedCategory=categorySelect.value;
    const selectedSubcategory=subcategorySelect.value;
    const query=searchInput.value.trim().toLocaleLowerCase();
    const categoryGroups = new Map();
    for(const [category,subgroups] of Object.entries(groups)){
      let visibleCount=0;
      for(const [subcategory,keys] of Object.entries(subgroups)){
        const cards=keys.map(key=>sourceCards.find(card=>card.querySelector("button[data-tech]")?.dataset.tech===key)).filter(Boolean);
        let count=0;
        cards.forEach(card=>{
          const button=card.querySelector("button[data-tech]");
          const key=button.dataset.tech;
          const item=(window.SSSWET_TECHNOLOGIES||{})[key]||{};
          const searchable=[item.en?.[0],item.en?.[1],item.fr?.[0],item.fr?.[1],key].join(" ").toLocaleLowerCase();
          const visible=(!selectedCategory||selectedCategory===category)&&(!selectedSubcategory||selectedSubcategory===subcategory)&&(!query||searchable.includes(query));
          card.hidden=!visible;
          count+=visible?1:0;
        });
        visibleCount+=count;
      }
      const section=categoryNodes.get(category);
      if(section)section.hidden=visibleCount===0;
    }
    for(const [key,node] of subcategoryNodes){const count=[...node.querySelectorAll(".technology-card")].filter(card=>!card.hidden).length;node.hidden=count===0;}
  }
  function constructGroups(){
    const fragment=document.createDocumentFragment();
    for(const [category,subgroups] of Object.entries(groups)){
      const section=document.createElement("section");section.className="technology-category-group";section.dataset.category=category;
      const title=document.createElement("h3");title.className="technology-category-heading";section.append(title);
      categoryNodes.set(category,section);
      for(const [subcategory,keys] of Object.entries(subgroups)){
        const sub=document.createElement("div");sub.className="technology-subcategory-group";sub.dataset.subcategory=subcategory;
        const subTitle=document.createElement("h4");subTitle.className="technology-subcategory-heading";sub.append(subTitle);
        subcategoryNodes.set(category+":"+subcategory,sub);
        keys.forEach(key=>{const card=sourceCards.find(item=>item.querySelector("button[data-tech]")?.dataset.tech===key);if(card)sub.append(card);});
        section.append(sub);
      }
      fragment.append(section);
    }
    root.replaceChildren(fragment);
  }
  function refreshHeadings(){
    const l=labels();
    [...categoryNodes.entries()].forEach(([key,node])=>{node.querySelector(".technology-category-heading").textContent=l.values[categoryKeys.indexOf(key)];});
    const subNames=["astrophysics","propulsion","spaceHabitats","nuclearProtection","protectiveEngineering","cleanGeneration","energyStorage","adaptiveMaterials","structuralMaterials","regenerativeMedicine","humanAugmentation","animalCare","ecosystemRestoration","climateResilience","autonomousResearch","assistiveRobotics","advancedComputing","communication","publicKnowledge"];
    for(const [id,node] of subcategoryNodes){const key=id.split(":")[1];node.querySelector(".technology-subcategory-heading").textContent=l.values[8+subNames.indexOf(key)];}
  }
  categorySelect.addEventListener("change",()=>{subcategorySelect.value="";renderFilters();});
  subcategorySelect.addEventListener("change",renderFilters);
  searchInput.addEventListener("input",renderFilters);
  constructGroups();
  localizeAndArrange();
  window.addEventListener("ssswet-language-changed",()=>{localizeAndArrange();refreshHeadings();});
  document.getElementById("language")?.addEventListener("change",()=>{localizeAndArrange();refreshHeadings();});
  refreshHeadings();
  window.SSSWET_TECHNOLOGY_TAXONOMY={groups, count:cardMeta.size};
})();