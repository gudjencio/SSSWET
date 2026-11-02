(() => {
  "use strict";
  const root = document.getElementById("version-center");
  if (!root) return;
  const status = document.getElementById("version-center-status");
  const current = document.getElementById("version-center-current");
  const history = document.getElementById("version-center-history");
  const integrity = document.getElementById("version-center-integrity");
  const languageSelect = document.getElementById("language");
  const api = "https://api.github.com/repos/gudjencio/SSSWET";
  const releasesUrl = api + "/releases?per_page=8";

  const base = {loading:"Checking official releases…",none:"No official release has been published yet.",current:"Latest official release",stable:"Published release",preview:"Preview release",published:"Published",files:"Available files",download:"Download",checksum:"SHA-256 checksums",noChecksum:"No SHA256SUMS file is attached to this release.",history:"Earlier releases",failed:"Release information is temporarily unavailable. Please try again later or visit the official releases page.",integrity:"SHA-256 checksums help compare downloaded files. They do not replace code signing or publisher verification.",notes:"Release notes",noFiles:"No installer is attached to this release."};
  const tr = {
    en:base,
    fr:{loading:"Vérification des versions officielles…",none:"Aucune version officielle n’a encore été publiée.",current:"Dernière version officielle",stable:"Version publiée",preview:"Version de prévisualisation",published:"Publiée le",files:"Fichiers disponibles",download:"Télécharger",checksum:"Sommes SHA-256",noChecksum:"Aucun fichier SHA256SUMS n’est joint à cette version.",history:"Versions précédentes",failed:"Les informations de version sont temporairement indisponibles. Réessayez plus tard ou consultez les publications officielles.",integrity:"Les sommes SHA-256 permettent de comparer les fichiers téléchargés. Elles ne remplacent pas la signature du code ni la vérification de l’éditeur.",notes:"Notes de version",noFiles:"Aucun installateur n’est joint à cette publication."},
    es:{loading:"Comprobando versiones oficiales…",none:"Todavía no se ha publicado ninguna versión oficial.",current:"Última versión oficial",stable:"Versión publicada",preview:"Versión de vista previa",published:"Publicada",files:"Archivos disponibles",download:"Descargar",checksum:"Sumas SHA-256",noChecksum:"Esta versión no incluye un archivo SHA256SUMS.",history:"Versiones anteriores",failed:"La información de versiones no está disponible temporalmente. Vuelve a intentarlo o consulta las versiones oficiales.",integrity:"Las sumas SHA-256 ayudan a comparar los archivos descargados. No sustituyen la firma del código ni la verificación del editor.",notes:"Notas de la versión",noFiles:"Esta publicación no incluye ningún instalador."},
    de:{loading:"Offizielle Versionen werden geprüft…",none:"Noch keine offizielle Version wurde veröffentlicht.",current:"Neueste offizielle Version",stable:"Veröffentlichte Version",preview:"Vorschauversion",published:"Veröffentlicht",files:"Verfügbare Dateien",download:"Herunterladen",checksum:"SHA-256-Prüfsummen",noChecksum:"Keine SHA256SUMS-Datei ist beigefügt.",history:"Frühere Versionen",failed:"Versionsinformationen sind vorübergehend nicht verfügbar. Bitte später erneut versuchen oder die offiziellen Veröffentlichungen öffnen.",integrity:"SHA-256-Prüfsummen helfen beim Vergleich heruntergeladener Dateien. Sie ersetzen weder Codesignatur noch Herausgeberprüfung.",notes:"Versionshinweise",noFiles:"Dieser Veröffentlichung ist kein Installer beigefügt."},
    it:{loading:"Verifica delle versioni ufficiali…",none:"Non è ancora stata pubblicata alcuna versione ufficiale.",current:"Ultima versione ufficiale",stable:"Versione pubblicata",preview:"Versione di anteprima",published:"Pubblicata",files:"File disponibili",download:"Scarica",checksum:"Checksum SHA-256",noChecksum:"Nessun file SHA256SUMS è allegato.",history:"Versioni precedenti",failed:"Le informazioni sulle versioni non sono temporaneamente disponibili. Riprova più tardi o consulta le pubblicazioni ufficiali.",integrity:"I checksum SHA-256 aiutano a confrontare i file scaricati. Non sostituiscono la firma del codice né la verifica dell’editore.",notes:"Note di rilascio",noFiles:"Nessun installatore è allegato a questa pubblicazione."},
    pt:{loading:"Verificando versões oficiais…",none:"Ainda não foi publicada nenhuma versão oficial.",current:"Última versão oficial",stable:"Versão publicada",preview:"Versão de pré-visualização",published:"Publicada",files:"Ficheiros disponíveis",download:"Transferir",checksum:"Somatórios SHA-256",noChecksum:"Não há ficheiro SHA256SUMS anexado.",history:"Versões anteriores",failed:"As informações de versão estão temporariamente indisponíveis. Tente novamente mais tarde ou consulte as versões oficiais.",integrity:"Os somatórios SHA-256 ajudam a comparar ficheiros transferidos. Não substituem a assinatura do código nem a verificação do editor.",notes:"Notas da versão",noFiles:"Esta publicação não inclui um instalador."},
    nl:{loading:"Officiële versies controleren…",none:"Er is nog geen officiële versie gepubliceerd.",current:"Laatste officiële versie",stable:"Gepubliceerde versie",preview:"Voorbeeldversie",published:"Gepubliceerd",files:"Beschikbare bestanden",download:"Downloaden",checksum:"SHA-256-controlesommen",noChecksum:"Geen SHA256SUMS-bestand toegevoegd.",history:"Eerdere versies",failed:"Versie-informatie is tijdelijk niet beschikbaar. Probeer het later opnieuw of bekijk de officiële releases.",integrity:"SHA-256-controlesommen helpen gedownloade bestanden te vergelijken. Ze vervangen geen codeondertekening of uitgeversverificatie.",notes:"Release-opmerkingen",noFiles:"Aan deze release is geen installatieprogramma toegevoegd."},
    ru:{loading:"Проверка официальных версий…",none:"Официальная версия ещё не опубликована.",current:"Последняя официальная версия",stable:"Опубликованная версия",preview:"Предварительная версия",published:"Опубликовано",files:"Доступные файлы",download:"Скачать",checksum:"Контрольные суммы SHA-256",noChecksum:"Файл SHA256SUMS не прикреплён.",history:"Предыдущие версии",failed:"Информация о версиях временно недоступна. Попробуйте позже или откройте официальные публикации.",integrity:"Контрольные суммы SHA-256 помогают сравнивать загруженные файлы. Они не заменяют подпись кода или проверку издателя.",notes:"Примечания к выпуску",noFiles:"К этой публикации не прикреплён установщик."},
    uk:{loading:"Перевірка офіційних версій…",none:"Офіційну версію ще не опубліковано.",current:"Остання офіційна версія",stable:"Опублікована версія",preview:"Попередня версія",published:"Опубліковано",files:"Доступні файли",download:"Завантажити",checksum:"Контрольні суми SHA-256",noChecksum:"Файл SHA256SUMS не додано.",history:"Попередні версії",failed:"Інформація про версії тимчасово недоступна. Спробуйте пізніше або перегляньте офіційні випуски.",integrity:"Контрольні суми SHA-256 допомагають порівнювати завантажені файли. Вони не замінюють підпис коду чи перевірку видавця.",notes:"Примітки до випуску",noFiles:"До цього випуску не додано інсталятор."},
    ar:{loading:"جارٍ التحقق من الإصدارات الرسمية…",none:"لم يُنشر أي إصدار رسمي بعد.",current:"أحدث إصدار رسمي",stable:"إصدار منشور",preview:"إصدار تجريبي",published:"نُشر في",files:"الملفات المتاحة",download:"تنزيل",checksum:"قيم SHA-256",noChecksum:"لا يوجد ملف SHA256SUMS مرفق.",history:"الإصدارات السابقة",failed:"معلومات الإصدار غير متاحة مؤقتًا. حاول لاحقًا أو راجع الإصدارات الرسمية.",integrity:"تساعد قيم SHA-256 على مقارنة الملفات التي تم تنزيلها، ولا تستبدل توقيع الشفرة أو التحقق من الناشر.",notes:"ملاحظات الإصدار",noFiles:"لا يوجد مثبت مرفق بهذا الإصدار."},
    he:{loading:"בודק גרסאות רשמיות…",none:"טרם פורסמה גרסה רשמית.",current:"הגרסה הרשמית האחרונה",stable:"גרסה שפורסמה",preview:"גרסת תצוגה מקדימה",published:"פורסם",files:"קבצים זמינים",download:"הורדה",checksum:"סכומי SHA-256",noChecksum:"אין קובץ SHA256SUMS מצורף.",history:"גרסאות קודמות",failed:"פרטי הגרסה אינם זמינים זמנית. נסו שוב מאוחר יותר או עיינו בגרסאות הרשמיות.",integrity:"סכומי SHA-256 מסייעים להשוות קבצים שהורדו. הם אינם מחליפים חתימת קוד או אימות מפרסם.",notes:"הערות גרסה",noFiles:"אין מתקין מצורף לפרסום זה."},
    ja:{loading:"公式リリースを確認中…",none:"公式リリースはまだ公開されていません。",current:"最新の公式リリース",stable:"公開版",preview:"プレビュー版",published:"公開日",files:"利用可能なファイル",download:"ダウンロード",checksum:"SHA-256チェックサム",noChecksum:"SHA256SUMSファイルはありません。",history:"以前のリリース",failed:"リリース情報を一時的に取得できません。後でもう一度お試しください。",integrity:"SHA-256チェックサムはファイル比較に役立ちます。コード署名や発行者確認の代わりにはなりません。",notes:"リリースノート",noFiles:"このリリースにはインストーラーがありません。"},
    ko:{loading:"공식 릴리스 확인 중…",none:"아직 공식 릴리스가 게시되지 않았습니다.",current:"최신 공식 릴리스",stable:"게시된 릴리스",preview:"미리보기 릴리스",published:"게시일",files:"사용 가능한 파일",download:"다운로드",checksum:"SHA-256 체크섬",noChecksum:"SHA256SUMS 파일이 없습니다.",history:"이전 릴리스",failed:"릴리스 정보를 일시적으로 가져올 수 없습니다. 나중에 다시 시도하세요.",integrity:"SHA-256 체크섬은 다운로드한 파일 비교에 도움이 되며 코드 서명이나 게시자 확인을 대신하지 않습니다.",notes:"릴리스 노트",noFiles:"이 릴리스에는 설치 프로그램이 없습니다."},
    zh:{loading:"正在检查官方版本…",none:"尚未发布官方版本。",current:"最新官方版本",stable:"已发布版本",preview:"预览版本",published:"发布日期",files:"可用文件",download:"下载",checksum:"SHA-256 校验和",noChecksum:"此版本未附带 SHA256SUMS 文件。",history:"以前的版本",failed:"版本信息暂时不可用，请稍后重试或查看官方版本发布页。",integrity:"SHA-256 校验和可帮助比较下载文件，但不能替代代码签名或发布者验证。",notes:"版本说明",noFiles:"此版本未附带安装程序。"},
    hi:{loading:"आधिकारिक रिलीज़ की जाँच हो रही है…",none:"अभी तक कोई आधिकारिक रिलीज़ प्रकाशित नहीं हुई है।",current:"नवीनतम आधिकारिक रिलीज़",stable:"प्रकाशित रिलीज़",preview:"पूर्वावलोकन रिलीज़",published:"प्रकाशित",files:"उपलब्ध फ़ाइलें",download:"डाउनलोड",checksum:"SHA-256 चेकसम",noChecksum:"इस रिलीज़ के साथ SHA256SUMS फ़ाइल नहीं है।",history:"पिछली रिलीज़",failed:"रिलीज़ जानकारी अस्थायी रूप से उपलब्ध नहीं है। बाद में फिर प्रयास करें।",integrity:"SHA-256 चेकसम डाउनलोड की गई फ़ाइलों की तुलना में मदद करते हैं। वे कोड साइनिंग या प्रकाशक सत्यापन का विकल्प नहीं हैं।",notes:"रिलीज़ नोट्स",noFiles:"इस रिलीज़ के साथ कोई इंस्टॉलर नहीं है।"},
    id:{loading:"Memeriksa rilis resmi…",none:"Belum ada rilis resmi yang diterbitkan.",current:"Rilis resmi terbaru",stable:"Rilis terbit",preview:"Rilis pratinjau",published:"Diterbitkan",files:"File tersedia",download:"Unduh",checksum:"Checksum SHA-256",noChecksum:"Tidak ada file SHA256SUMS pada rilis ini.",history:"Rilis sebelumnya",failed:"Informasi rilis sementara tidak tersedia. Coba lagi nanti atau lihat rilis resmi.",integrity:"Checksum SHA-256 membantu membandingkan file yang diunduh. Ini tidak menggantikan penandatanganan kode atau verifikasi penerbit.",notes:"Catatan rilis",noFiles:"Tidak ada pemasang pada rilis ini."},
    tr:{loading:"Resmi sürümler kontrol ediliyor…",none:"Henüz resmi bir sürüm yayımlanmadı.",current:"En son resmi sürüm",stable:"Yayımlanan sürüm",preview:"Önizleme sürümü",published:"Yayımlandı",files:"Kullanılabilir dosyalar",download:"İndir",checksum:"SHA-256 sağlama toplamları",noChecksum:"Bu sürüme SHA256SUMS dosyası eklenmemiş.",history:"Önceki sürümler",failed:"Sürüm bilgileri geçici olarak kullanılamıyor. Daha sonra tekrar deneyin veya resmi sürümlere bakın.",integrity:"SHA-256 sağlama toplamları dosyaları karşılaştırmaya yardımcı olur. Kod imzasının veya yayıncı doğrulamasının yerini tutmaz.",notes:"Sürüm notları",noFiles:"Bu sürüme yükleyici eklenmemiş."},
    pl:{loading:"Sprawdzanie oficjalnych wydań…",none:"Nie opublikowano jeszcze oficjalnego wydania.",current:"Najnowsze oficjalne wydanie",stable:"Wydane",preview:"Wydanie podglądowe",published:"Opublikowano",files:"Dostępne pliki",download:"Pobierz",checksum:"Sumy kontrolne SHA-256",noChecksum:"Nie dołączono pliku SHA256SUMS.",history:"Poprzednie wydania",failed:"Informacje o wydaniu są tymczasowo niedostępne. Spróbuj później lub sprawdź oficjalne wydania.",integrity:"Sumy SHA-256 pomagają porównywać pobrane pliki. Nie zastępują podpisu kodu ani weryfikacji wydawcy.",notes:"Informacje o wydaniu",noFiles:"Nie dołączono instalatora."},
    bn:{loading:"অফিসিয়াল রিলিজ পরীক্ষা করা হচ্ছে…",none:"এখনও কোনো অফিসিয়াল রিলিজ প্রকাশিত হয়নি।",current:"সর্বশেষ অফিসিয়াল রিলিজ",stable:"প্রকাশিত রিলিজ",preview:"প্রিভিউ রিলিজ",published:"প্রকাশিত",files:"উপলভ্য ফাইল",download:"ডাউনলোড",checksum:"SHA-256 চেকসম",noChecksum:"কোনো SHA256SUMS ফাইল নেই।",history:"আগের রিলিজ",failed:"রিলিজের তথ্য সাময়িকভাবে অনুপলভ্য। পরে আবার চেষ্টা করুন।",integrity:"SHA-256 চেকসম ডাউনলোড করা ফাইল তুলনা করতে সাহায্য করে; এটি কোড স্বাক্ষর বা প্রকাশক যাচাইয়ের বিকল্প নয়।",notes:"রিলিজ নোট",noFiles:"এই রিলিজে কোনো ইনস্টলার নেই।"},
    sw:{loading:"Inakagua matoleo rasmi…",none:"Hakuna toleo rasmi lililochapishwa bado.",current:"Toleo rasmi la hivi karibuni",stable:"Toleo lililochapishwa",preview:"Toleo la hakikisho",published:"Limechapishwa",files:"Faili zinazopatikana",download:"Pakua",checksum:"Checksum za SHA-256",noChecksum:"Hakuna faili ya SHA256SUMS iliyowekwa.",history:"Matoleo ya awali",failed:"Taarifa za toleo hazipatikani kwa muda. Jaribu tena baadaye au angalia matoleo rasmi.",integrity:"Checksum za SHA-256 husaidia kulinganisha faili zilizopakuliwa. Hazibadilishi sahihi ya msimbo wala uthibitishaji wa mchapishaji.",notes:"Maelezo ya toleo",noFiles:"Hakuna kisakinishaji kilichoambatishwa."},
    vi:{loading:"Đang kiểm tra bản phát hành chính thức…",none:"Chưa có bản phát hành chính thức nào được công bố.",current:"Bản phát hành chính thức mới nhất",stable:"Bản đã phát hành",preview:"Bản xem trước",published:"Đã phát hành",files:"Tệp khả dụng",download:"Tải xuống",checksum:"Mã kiểm tra SHA-256",noChecksum:"Không có tệp SHA256SUMS.",history:"Các bản phát hành trước",failed:"Thông tin bản phát hành tạm thời không khả dụng. Hãy thử lại sau.",integrity:"Mã kiểm tra SHA-256 giúp so sánh các tệp đã tải xuống. Chúng không thay thế chữ ký mã hoặc xác minh nhà phát hành.",notes:"Ghi chú phát hành",noFiles:"Không có trình cài đặt trong bản phát hành này."},
    fa:{loading:"در حال بررسی انتشارهای رسمی…",none:"هنوز هیچ نسخه رسمی منتشر نشده است.",current:"آخرین نسخه رسمی",stable:"نسخه منتشرشده",preview:"نسخه پیش‌نمایش",published:"منتشرشده",files:"فایل‌های موجود",download:"دانلود",checksum:"چک‌سام‌های SHA-256",noChecksum:"فایل SHA256SUMS پیوست نشده است.",history:"نسخه‌های قبلی",failed:"اطلاعات نسخه موقتاً در دسترس نیست. بعداً دوباره تلاش کنید.",integrity:"چک‌سام‌های SHA-256 به مقایسه فایل‌های دانلودشده کمک می‌کنند و جایگزین امضای کد یا تأیید ناشر نیستند.",notes:"یادداشت‌های انتشار",noFiles:"نصب‌کننده‌ای پیوست نشده است."},
    ur:{loading:"سرکاری ریلیزز چیک کی جا رہی ہیں…",none:"ابھی تک کوئی سرکاری ریلیز شائع نہیں ہوئی۔",current:"تازہ ترین سرکاری ریلیز",stable:"شائع شدہ ریلیز",preview:"پیش نظارہ ریلیز",published:"شائع شدہ",files:"دستیاب فائلیں",download:"ڈاؤن لوڈ",checksum:"SHA-256 چیک سم",noChecksum:"SHA256SUMS فائل منسلک نہیں ہے۔",history:"پچھلی ریلیزز",failed:"ریلیز کی معلومات عارضی طور پر دستیاب نہیں۔ بعد میں دوبارہ کوشش کریں۔",integrity:"SHA-256 چیک سم فائلوں کا موازنہ کرنے میں مدد دیتے ہیں۔ یہ کوڈ سائننگ یا ناشر کی تصدیق کا متبادل نہیں ہیں۔",notes:"ریلیز نوٹس",noFiles:"اس ریلیز کے ساتھ کوئی انسٹالر نہیں ہے۔"},
    ta:{loading:"அதிகாரப்பூர்வ வெளியீடுகளைச் சரிபார்க்கிறது…",none:"இன்னும் அதிகாரப்பூர்வ வெளியீடு வெளியிடப்படவில்லை.",current:"சமீபத்திய அதிகாரப்பூர்வ வெளியீடு",stable:"வெளியிடப்பட்ட பதிப்பு",preview:"முன்னோட்ட வெளியீடு",published:"வெளியிடப்பட்டது",files:"கிடைக்கும் கோப்புகள்",download:"பதிவிறக்கு",checksum:"SHA-256 சரிபார்ப்பு மதிப்புகள்",noChecksum:"SHA256SUMS கோப்பு இல்லை.",history:"முந்தைய வெளியீடுகள்",failed:"வெளியீட்டு தகவல் தற்காலிகமாக கிடைக்கவில்லை. பின்னர் முயற்சிக்கவும்.",integrity:"SHA-256 மதிப்புகள் பதிவிறக்கிய கோப்புகளை ஒப்பிட உதவுகின்றன. அவை குறியீட்டு கையொப்பம் அல்லது வெளியீட்டாளர் சரிபார்ப்பை மாற்றாது.",notes:"வெளியீட்டு குறிப்புகள்",noFiles:"இந்த வெளியீட்டில் நிறுவி இல்லை."},
    te:{loading:"అధికారిక విడుదలలను తనిఖీ చేస్తోంది…",none:"ఇంకా అధికారిక విడుదల ఏదీ ప్రచురించబడలేదు.",current:"తాజా అధికారిక విడుదల",stable:"ప్రచురించిన విడుదల",preview:"ప్రివ్యూ విడుదల",published:"ప్రచురించబడింది",files:"అందుబాటులో ఉన్న ఫైళ్లు",download:"డౌన్‌లోడ్",checksum:"SHA-256 చెక్‌సమ్‌లు",noChecksum:"SHA256SUMS ఫైల్ లేదు.",history:"మునుపటి విడుదలలు",failed:"విడుదల సమాచారం తాత్కాలికంగా అందుబాటులో లేదు. తర్వాత మళ్లీ ప్రయత్నించండి.",integrity:"SHA-256 చెక్‌సమ్‌లు డౌన్‌లోడ్ చేసిన ఫైళ్లను పోల్చడంలో సహాయపడతాయి. అవి కోడ్ సంతకం లేదా ప్రచురణకర్త ధృవీకరణకు ప్రత్యామ్నాయం కావు.",notes:"విడుదల గమనికలు",noFiles:"ఈ విడుదలకు ఇన్‌స్టాలర్ లేదు."}
  };

  const lang = () => String(languageSelect?.value || document.documentElement.lang || navigator.language || "en").toLowerCase().split("-")[0];
  const words = () => tr[lang()] || base;
  const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; };
  const safeDate = value => { const date = new Date(value); if (Number.isNaN(date.getTime())) return ""; return new Intl.DateTimeFormat(lang() === "en" ? "en-GB" : lang(), { dateStyle:"medium" }).format(date); };
  const link = (url, label) => { if (!/^https:\/\/github\.com\/gudjencio\/SSSWET\//i.test(url || "")) return null; const a = el("a", "", label); a.href=url; a.target="_blank"; a.rel="noopener noreferrer"; return a; };

  function renderRelease(release, featured) {
    const w = words();
    const card = el("article", "version-release-card");
    card.append(el("h3", "", release.name || release.tag_name || "SSSWET"));
    if (featured) card.append(el("p", "", w.current));
    const meta = el("div", "version-release-meta");
    meta.append(el("span", "", release.prerelease ? w.preview : w.stable));
    const date = safeDate(release.published_at);
    if (date) meta.append(el("span", "", w.published + " · " + date));
    if (release.tag_name) meta.append(el("span", "", release.tag_name));
    card.append(meta);
    const assets = Array.isArray(release.assets) ? release.assets : [];
    const checksum = assets.find(asset => /^SHA256SUMS\.txt$/i.test(asset.name));
    if (assets.length) {
      card.append(el("p", "", w.files));
      const links = el("div", "version-release-links");
      assets.forEach(asset => { const a = link(asset.browser_download_url, w.download + " · " + asset.name); if (a) links.append(a); });
      if (links.childElementCount) card.append(links);
    } else card.append(el("p", "", w.noFiles));
    const footer = el("div", "version-release-links");
    const notes = link(release.html_url, w.notes);
    if (notes) footer.append(notes);
    if (checksum) { const a = link(checksum.browser_download_url, w.checksum); if (a) footer.append(a); }
    if (footer.childElementCount) card.append(footer);
    return { card, checksum: Boolean(checksum) };
  }

  async function load() {
    const w = words();
    status.dataset.state = "loading";
    status.textContent = w.loading;
    current.replaceChildren();
    history.replaceChildren();
    integrity.textContent = w.integrity;
    try {
      const response = await fetch(releasesUrl, { headers:{Accept:"application/vnd.github+json"}, cache: "no-store" });
      if (!response.ok) throw new Error("GitHub Releases HTTP " + response.status);
      const releases = await response.json();
      const published = Array.isArray(releases) ? releases.filter(item => !item.draft && item.published_at) : [];
      if (!published.length) { status.dataset.state="empty"; status.textContent=w.none; integrity.textContent=w.integrity+" "+w.noChecksum; return; }
      const latest = renderRelease(published[0], true);
      current.append(latest.card);
      status.dataset.state="available";
      status.textContent=w.current+" · "+(published[0].tag_name || published[0].name || "SSSWET");
      if (!latest.checksum) integrity.textContent=w.integrity+" "+w.noChecksum;
      const previous = published.slice(1);
      if (previous.length) {
        history.append(el("p", "version-center-integrity", w.history));
        previous.forEach(release => { const row=el("div","version-history-item"); const a=link(release.html_url, release.name || release.tag_name || "SSSWET"); if(a) row.append(a); row.append(el("time","",safeDate(release.published_at))); history.append(row); });
      }
    } catch (_) { status.dataset.state="error"; status.textContent=w.failed; integrity.textContent=w.integrity; }
  }

  load();
  languageSelect?.addEventListener("change", load);
  window.addEventListener("online", load);
})();