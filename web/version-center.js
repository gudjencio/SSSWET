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

  const copy = {
    en:{loading:"Checking official releases…",none:"No official release has been published yet. The web interface remains available and installable on supported devices.",current:"Latest official release",prerelease:"Preview release",stable:"Published release",published:"Published",assets:"Available files",download:"Download",checksums:"SHA-256 checksums",noChecksum:"No SHA256SUMS file is attached to this release.",history:"Earlier releases",failed:"Release information is temporarily unavailable. Please try again later or visit the official releases page.",integrity:"SHA-256 checksums help compare downloaded files. They do not replace code signing or publisher verification.",releaseNotes:"Release notes",noAssets:"No installer is attached to this release.",draft:"Draft excluded"},
    fr:{loading:"Vérification des versions officielles…",none:"Aucune version officielle n’a encore été publiée. L’interface web reste accessible et installable sur les appareils compatibles.",current:"Dernière version officielle",prerelease:"Version de prévisualisation",stable:"Version publiée",published:"Publiée le",assets:"Fichiers disponibles",download:"Télécharger",checksums:"Sommes de contrôle SHA-256",noChecksum:"Aucun fichier SHA256SUMS n’est joint à cette version.",history:"Versions précédentes",failed:"Les informations de version sont temporairement indisponibles. Réessayez plus tard ou consultez les publications officielles.",integrity:"Les sommes de contrôle SHA-256 permettent de comparer les fichiers téléchargés. Elles ne remplacent pas la signature du code ni la vérification de l’éditeur.",releaseNotes:"Notes de version",noAssets:"Aucun installateur n’est joint à cette publication.",draft:"Brouillon exclu"},
    es:{loading:"Comprobando versiones oficiales…",none:"Todavía no se ha publicado ninguna versión oficial. La interfaz web sigue disponible e instalable en dispositivos compatibles.",current:"Última versión oficial",prerelease:"Versión de vista previa",stable:"Versión publicada",published:"Publicada",assets:"Archivos disponibles",download:"Descargar",checksums:"Sumas SHA-256",noChecksum:"Esta versión no incluye un archivo SHA256SUMS.",history:"Versiones anteriores",failed:"La información de versiones no está disponible temporalmente. Vuelve a intentarlo o consulta las versiones oficiales.",integrity:"Las sumas SHA-256 ayudan a comparar los archivos descargados. No sustituyen la firma del código ni la verificación del editor.",releaseNotes:"Notas de la versión",noAssets:"Esta publicación no incluye ningún instalador.",draft:"Borrador excluido"},
    de:{loading:"Offizielle Versionen werden geprüft…",none:"Noch keine offizielle Version wurde veröffentlicht. Die Weboberfläche bleibt auf unterstützten Geräten verfügbar und installierbar.",current:"Neueste offizielle Version",prerelease:"Vorschauversion",stable:"Veröffentlichte Version",published:"Veröffentlicht",assets:"Verfügbare Dateien",download:"Herunterladen",checksums:"SHA-256-Prüfsummen",noChecksum:"Dieser Version ist keine SHA256SUMS-Datei beigefügt.",history:"Frühere Versionen",failed:"Versionsinformationen sind vorübergehend nicht verfügbar. Bitte später erneut versuchen oder die offiziellen Veröffentlichungen aufrufen.",integrity:"SHA-256-Prüfsummen helfen beim Vergleich heruntergeladener Dateien. Sie ersetzen weder Codesignatur noch Herausgeberprüfung.",releaseNotes:"Versionshinweise",noAssets:"Dieser Veröffentlichung ist kein Installer beigefügt.",draft:"Entwurf ausgeschlossen"},
    it:{loading:"Verifica delle versioni ufficiali…",none:"Non è ancora stata pubblicata alcuna versione ufficiale. L’interfaccia web resta disponibile e installabile sui dispositivi compatibili.",current:"Ultima versione ufficiale",prerelease:"Versione di anteprima",stable:"Versione pubblicata",published:"Pubblicata",assets:"File disponibili",download:"Scarica",checksums:"Checksum SHA-256",noChecksum:"Questa versione non contiene un file SHA256SUMS.",history:"Versioni precedenti",failed:"Le informazioni sulle versioni non sono temporaneamente disponibili. Riprova più tardi o consulta le pubblicazioni ufficiali.",integrity:"I checksum SHA-256 aiutano a confrontare i file scaricati. Non sostituiscono la firma del codice né la verifica dell’editore.",releaseNotes:"Note di rilascio",noAssets:"Nessun programma di installazione è allegato a questa pubblicazione.",draft:"Bozza esclusa"},
    pt:{loading:"Verificando versões oficiais…",none:"Ainda não foi publicada nenhuma versão oficial. A interface web continua disponível e instalável em dispositivos compatíveis.",current:"Última versão oficial",prerelease:"Versão de pré-visualização",stable:"Versão publicada",published:"Publicada",assets:"Ficheiros disponíveis",download:"Transferir",checksums:"Somatórios SHA-256",noChecksum:"Esta versão não inclui um ficheiro SHA256SUMS.",history:"Versões anteriores",failed:"As informações de versão estão temporariamente indisponíveis. Tente novamente mais tarde ou consulte as versões oficiais.",integrity:"Os somatórios SHA-256 ajudam a comparar ficheiros transferidos. Não substituem a assinatura do código nem a verificação do editor.",releaseNotes:"Notas da versão",noAssets:"Esta publicação não inclui um instalador.",draft:"Rascunho excluído"},
    nl:{loading:"Officiële versies controleren…",none:"Er is nog geen officiële versie gepubliceerd. De webinterface blijft beschikbaar en installeerbaar op ondersteunde apparaten.",current:"Laatste officiële versie",prerelease:"Voorbeeldversie",stable:"Gepubliceerde versie",published:"Gepubliceerd",assets:"Beschikbare bestanden",download:"Downloaden",checksums:"SHA-256-controlesommen",noChecksum:"Aan deze versie is geen SHA256SUMS-bestand toegevoegd.",history:"Eerdere versies",failed:"Versie-informatie is tijdelijk niet beschikbaar. Probeer het later opnieuw of bekijk de officiële releases.",integrity:"SHA-256-controlesommen helpen gedownloade bestanden te vergelijken. Ze vervangen geen codeondertekening of uitgeversverificatie.",releaseNotes:"Release-opmerkingen",noAssets:"Aan deze release is geen installatieprogramma toegevoegd.",draft:"Concept uitgesloten"},
    ru:{loading:"Проверка официальных версий…",none:"Официальная версия ещё не опубликована. Веб-интерфейс остаётся доступным и устанавливаемым на поддерживаемых устройствах.",current:"Последняя официальная версия",prerelease:"Предварительная версия",stable:"Опубликованная версия",published:"Опубликовано",assets:"Доступные файлы",download:"Скачать",checksums:"Контрольные суммы SHA-256",noChecksum:"К этой версии не прикреплён файл SHA256SUMS.",history:"Предыдущие версии",failed:"Информация о версиях временно недоступна. Попробуйте позже или откройте официальные публикации.",integrity:"Контрольные суммы SHA-256 помогают сравнивать загруженные файлы. Они не заменяют подпись кода или проверку издателя.",releaseNotes:"Примечания к выпуску",noAssets:"К этой публикации не прикреплён установщик.",draft:"Черновик исключён"},
    uk:{loading:"Перевірка офіційних версій…",none:"Офіційну версію ще не опубліковано. Вебінтерфейс залишається доступним і придатним для встановлення на сумісних пристроях.",current:"Остання офіційна версія",prerelease:"Попередня версія",stable:"Опублікована версія",published:"Опубліковано",assets:"Доступні файли",download:"Завантажити",checksums:"Контрольні суми SHA-256",noChecksum:"До цієї версії не додано файл SHA256SUMS.",history:"Попередні версії",failed:"Інформація про версії тимчасово недоступна. Спробуйте пізніше або перегляньте офіційні випуски.",integrity:"Контрольні суми SHA-256 допомагають порівнювати завантажені файли. Вони не замінюють підпис коду чи перевірку видавця.",releaseNotes:"Примітки до випуску",noAssets:"До цього випуску не додано інсталятор.",draft:"Чернетку виключено"},
    ar:{loading:"جارٍ التحقق من الإصدارات الرسمية…",none:"لم يُنشر أي إصدار رسمي بعد. تظل واجهة الويب متاحة وقابلة للتثبيت على الأجهزة المدعومة.",current:"أحدث إصدار رسمي",prerelease:"إصدار تجريبي",stable:"إصدار منشور",published:"نُشر في",assets:"الملفات المتاحة",download:"تنزيل",checksums:"قيم تحقق SHA-256",noChecksum:"لا يوجد ملف SHA256SUMS مرفق بهذا الإصدار.",history:"الإصدارات السابقة",failed:"معلومات الإصدار غير متاحة مؤقتًا. حاول لاحقًا أو راجع الإصدارات الرسمية.",integrity:"تساعد قيم SHA-256 على مقارنة الملفات التي تم تنزيلها. ولا تستبدل توقيع الشفرة أو التحقق من الناشر.",releaseNotes:"ملاحظات الإصدار",noAssets:"لا يوجد مثبت مرفق بهذا الإصدار.",draft:"تم استبعاد المسودة"},
    he:{loading:"בודק גרסאות רשמיות…",none:"טרם פורסמה גרסה רשמית. ממשק האינטרנט נשאר זמין וניתן להתקנה במכשירים נתמכים.",current:"הגרסה הרשמית האחרונה",prerelease:"גרסת תצוגה מקדימה",stable:"גרסה שפורסמה",published:"פורסם",assets:"קבצים זמינים",download:"הורדה",checksums:"סכומי ביקורת SHA-256",noChecksum:"אין קובץ SHA256SUMS מצורף לגרסה זו.",history:"גרסאות קודמות",failed:"פרטי הגרסה אינם זמינים זמנית. נסו שוב מאוחר יותר או עיינו בגרסאות הרשמיות.",integrity:"סכומי SHA-256 מסייעים להשוות קבצים שהורדו. הם אינם מחליפים חתימת קוד או אימות מפרסם.",releaseNotes:"הערות גרסה",noAssets:"אין מתקין מצורף לפרסום זה.",draft:"טיוטה לא נכללה"},
    ja:{loading:"公式リリースを確認中…",none:"公式リリースはまだ公開されていません。Webインターフェースは対応端末で引き続き利用・インストールできます。",current:"最新の公式リリース",prerelease:"プレビュー版",stable:"公開版",published:"公開日",assets:"利用可能なファイル",download:"ダウンロード",checksums:"SHA-256チェックサム",noChecksum:"このリリースにはSHA256SUMSファイルがありません。",history:"以前のリリース",failed:"リリース情報を一時的に取得できません。後でもう一度試すか、公式リリースを確認してください。",integrity:"SHA-256チェックサムはダウンロードしたファイルの比較に役立ちます。コード署名や発行者確認の代わりにはなりません。",releaseNotes:"リリースノート",noAssets:"このリリースにはインストーラーがありません。",draft:"下書きは除外"},
    ko:{loading:"공식 릴리스 확인 중…",none:"아직 공식 릴리스가 게시되지 않았습니다. 웹 인터페이스는 지원되는 기기에서 계속 이용하고 설치할 수 있습니다.",current:"최신 공식 릴리스",prerelease:"미리보기 릴리스",stable:"게시된 릴리스",published:"게시일",assets:"사용 가능한 파일",download:"다운로드",checksums:"SHA-256 체크섬",noChecksum:"이 릴리스에는 SHA256SUMS 파일이 없습니다.",history:"이전 릴리스",failed:"릴리스 정보를 일시적으로 가져올 수 없습니다. 나중에 다시 시도하거나 공식 릴리스를 확인하세요.",integrity:"SHA-256 체크섬은 다운로드한 파일을 비교하는 데 도움이 됩니다. 코드 서명이나 게시자 확인을 대신하지 않습니다.",releaseNotes:"릴리스 노트",noAssets:"이 릴리스에는 설치 프로그램이 없습니다.",draft:"초안 제외"},
    zh:{loading:"正在检查官方版本…",none:"尚未发布官方版本。网页界面仍可在受支持的设备上使用和安装。",current:"最新官方版本",prerelease:"预览版本",stable:"已发布版本",published:"发布日期",assets:"可用文件",download:"下载",checksums:"SHA-256 校验和",noChecksum:"此版本未附带 SHA256SUMS 文件。",history:"以前的版本",failed:"版本信息暂时不可用。请稍后重试或查看官方版本发布页。",integrity:"SHA-256 校验和可帮助比较下载文件，但不能替代代码签名或发布者验证。",releaseNotes:"版本说明",noAssets:"此版本未附带安装程序。",draft:"已排除草稿"},
    hi:{loading:"आधिकारिक रिलीज़ की जाँच हो रही है…",none:"अभी तक कोई आधिकारिक रिलीज़ प्रकाशित नहीं हुई है। वेब इंटरफ़ेस समर्थित उपकरणों पर उपलब्ध और इंस्टॉल करने योग्य है।",current:"नवीनतम आधिकारिक रिलीज़",prerelease:"पूर्वावलोकन रिलीज़",stable:"प्रकाशित रिलीज़",published:"प्रकाशित",assets:"उपलब्ध फ़ाइलें",download:"डाउनलोड",checksums:"SHA-256 चेकसम",noChecksum:"इस रिलीज़ के साथ SHA256SUMS फ़ाइल नहीं है।",history:"पिछली रिलीज़",failed:"रिलीज़ जानकारी अस्थायी रूप से उपलब्ध नहीं है। बाद में फिर प्रयास करें या आधिकारिक रिलीज़ देखें।",integrity:"SHA-256 चेकसम डाउनलोड की गई फ़ाइलों की तुलना में मदद करते हैं। वे कोड साइनिंग या प्रकाशक सत्यापन का विकल्प नहीं हैं।",releaseNotes:"रिलीज़ नोट्स",noAssets:"इस रिलीज़ के साथ कोई इंस्टॉलर नहीं है।",draft:"ड्राफ्ट बाहर रखा गया"},
    id:{loading:"Memeriksa rilis resmi…",none:"Belum ada rilis resmi yang diterbitkan. Antarmuka web tetap tersedia dan dapat dipasang pada perangkat yang didukung.",current:"Rilis resmi terbaru",prerelease:"Rilis pratinjau",stable:"Rilis terbit",published:"Diterbitkan",assets:"File tersedia",download:"Unduh",checksums:"Checksum SHA-256",noChecksum:"Tidak ada file SHA256SUMS pada rilis ini.",history:"Rilis sebelumnya",failed:"Informasi rilis sementara tidak tersedia. Coba lagi nanti atau lihat rilis resmi.",integrity:"Checksum SHA-256 membantu membandingkan file yang diunduh. Ini tidak menggantikan penandatanganan kode atau verifikasi penerbit.",releaseNotes:"Catatan rilis",noAssets:"Tidak ada pemasang pada rilis ini.",draft:"Draf dikecualikan"},
    tr:{loading:"Resmi sürümler kontrol ediliyor…",none:"Henüz resmi bir sürüm yayımlanmadı. Web arayüzü desteklenen cihazlarda kullanılabilir ve kurulabilir durumda.",current:"En son resmi sürüm",prerelease:"Önizleme sürümü",stable:"Yayımlanan sürüm",published:"Yayımlandı",assets:"Kullanılabilir dosyalar",download:"İndir",checksums:"SHA-256 sağlama toplamları",noChecksum:"Bu sürüme SHA256SUMS dosyası eklenmemiş.",history:"Önceki sürümler",failed:"Sürüm bilgileri geçici olarak kullanılamıyor. Daha sonra tekrar deneyin veya resmi sürümlere bakın.",integrity:"SHA-256 sağlama toplamları indirilen dosyaları karşılaştırmaya yardımcı olur. Kod imzasının veya yayıncı doğrulamasının yerini tutmaz.",releaseNotes:"Sürüm notları",noAssets:"Bu sürüme yükleyici eklenmemiş.",draft:"Taslak hariç"},
    pl:{loading:"Sprawdzanie oficjalnych wydań…",none:"Nie opublikowano jeszcze oficjalnego wydania. Interfejs webowy pozostaje dostępny i możliwy do zainstalowania na obsługiwanych urządzeniach.",current:"Najnowsze oficjalne wydanie",prerelease:"Wydanie podglądowe",stable:"Wydane",published:"Opublikowano",assets:"Dostępne pliki",download:"Pobierz",checksums:"Sumy kontrolne SHA-256",noChecksum:"Do tego wydania nie dołączono pliku SHA256SUMS.",history:"Poprzednie wydania",failed:"Informacje o wydaniu są tymczasowo niedostępne. Spróbuj ponownie później lub sprawdź oficjalne wydania.",integrity:"Sumy SHA-256 pomagają porównywać pobrane pliki. Nie zastępują podpisu kodu ani weryfikacji wydawcy.",releaseNotes:"Informacje o wydaniu",noAssets:"Do tego wydania nie dołączono instalatora.",draft:"Pominięto wersję roboczą"},
    bn:{loading:"অফিসিয়াল রিলিজ পরীক্ষা করা হচ্ছে…",none:"এখনও কোনো অফিসিয়াল রিলিজ প্রকাশিত হয়নি। সমর্থিত ডিভাইসে ওয়েব ইন্টারফেস ব্যবহার ও ইনস্টল করা যাবে।",current:"সর্বশেষ অফিসিয়াল রিলিজ",prerelease:"প্রিভিউ রিলিজ",stable:"প্রকাশিত রিলিজ",published:"প্রকাশিত",assets:"উপলভ্য ফাইল",download:"ডাউনলোড",checksums:"SHA-256 চেকসম",noChecksum:"এই রিলিজে কোনো SHA256SUMS ফাইল নেই।",history:"আগের রিলিজ",failed:"রিলিজের তথ্য সাময়িকভাবে অনুপলভ্য। পরে আবার চেষ্টা করুন বা অফিসিয়াল রিলিজ দেখুন।",integrity:"SHA-256 চেকসম ডাউনলোড করা ফাইল তুলনা করতে সাহায্য করে। এগুলো কোড স্বাক্ষর বা প্রকাশক যাচাইয়ের বিকল্প নয়।",releaseNotes:"রিলিজ নোট",noAssets:"এই রিলিজে কোনো ইনস্টলার নেই।",draft:"ড্রাফট বাদ"},
    sw:{loading:"Inakagua matoleo rasmi…",none:"Hakuna toleo rasmi lililochapishwa bado. Kiolesura cha wavuti kinaendelea kupatikana na kusakinishwa kwenye vifaa vinavyotumika.",current:"Toleo rasmi la hivi karibuni",prerelease:"Toleo la hakikisho",stable:"Toleo lililochapishwa",published:"Limechapishwa",assets:"Faili zinazopatikana",download:"Pakua",checksums:"Checksum za SHA-256",noChecksum:"Hakuna faili ya SHA256SUMS iliyoambatishwa kwenye toleo hili.",history:"Matoleo ya awali",failed:"Taarifa za toleo hazipatikani kwa muda. Jaribu tena baadaye au angalia matoleo rasmi.",integrity:"Checksum za SHA-256 husaidia kulinganisha faili zilizopakuliwa. Hazibadilishi sahihi ya msimbo wala uthibitishaji wa mchapishaji.",releaseNotes:"Maelezo ya toleo",noAssets:"Hakuna kisakinishaji kilichoambatishwa kwenye toleo hili.",draft:"Rasimu imeondolewa"},
    vi:{loading:"Đang kiểm tra bản phát hành chính thức…",none:"Chưa có bản phát hành chính thức nào được công bố. Giao diện web vẫn có thể sử dụng và cài đặt trên thiết bị được hỗ trợ.",current:"Bản phát hành chính thức mới nhất",prerelease:"Bản xem trước",stable:"Bản đã phát hành",published:"Đã phát hành",assets:"Tệp khả dụng",download:"Tải xuống",checksums:"Mã kiểm tra SHA-256",noChecksum:"Bản phát hành này không có tệp SHA256SUMS.",history:"Các bản phát hành trước",failed:"Thông tin bản phát hành tạm thời không khả dụng. Hãy thử lại sau hoặc xem các bản phát hành chính thức.",integrity:"Mã kiểm tra SHA-256 giúp so sánh các tệp đã tải xuống. Chúng không thay thế chữ ký mã hoặc xác minh nhà phát hành.",releaseNotes:"Ghi chú phát hành",noAssets:"Bản phát hành này không có trình cài đặt.",draft:"Đã loại bản nháp"},
    fa:{loading:"در حال بررسی انتشارهای رسمی…",none:"هنوز هیچ نسخه رسمی منتشر نشده است. رابط وب روی دستگاه‌های پشتیبانی‌شده همچنان در دسترس و قابل نصب است.",current:"آخرین نسخه رسمی",prerelease:"نسخه پیش‌نمایش",stable:"نسخه منتشرشده",published:"منتشرشده",assets:"فایل‌های موجود",download:"دانلود",checksums:"چک‌سام‌های SHA-256",noChecksum:"فایل SHA256SUMS برای این نسخه پیوست نشده است.",history:"نسخه‌های قبلی",failed:"اطلاعات نسخه موقتاً در دسترس نیست. بعداً دوباره تلاش کنید یا انتشارهای رسمی را ببینید.",integrity:"چک‌سام‌های SHA-256 به مقایسه فایل‌های دانلودشده کمک می‌کنند. آن‌ها جایگزین امضای کد یا تأیید ناشر نیستند.",releaseNotes:"یادداشت‌های انتشار",noAssets:"نصب‌کننده‌ای برای این انتشار پیوست نشده است.",draft:"پیش‌نویس حذف شد"},
    ur:{loading:"سرکاری ریلیزز چیک کی جا رہی ہیں…",none:"ابھی تک کوئی سرکاری ریلیز شائع نہیں ہوئی۔ ویب انٹرفیس معاون آلات پر دستیاب اور قابل تنصیب ہے۔",current:"تازہ ترین سرکاری ریلیز",prerelease:"پیش نظارہ ریلیز",stable:"شائع شدہ ریلیز",published:"شائع شدہ",assets:"دستیاب فائلیں",download:"ڈاؤن لوڈ",checksums:"SHA-256 چیک سم",noChecksum:"اس ریلیز کے ساتھ SHA256SUMS فائل منسلک نہیں ہے۔",history:"پچھلی ریلیزز",failed:"ریلیز کی معلومات عارضی طور پر دستیاب نہیں۔ بعد میں دوبارہ کوشش کریں یا سرکاری ریلیزز دیکھیں۔",integrity:"SHA-256 چیک سم ڈاؤن لوڈ شدہ فائلوں کا موازنہ کرنے میں مدد دیتے ہیں۔ یہ کوڈ سائننگ یا ناشر کی تصدیق کا متبادل نہیں ہیں۔",releaseNotes:"ریلیز نوٹس",noAssets:"اس ریلیز کے ساتھ کوئی انسٹالر منسلک نہیں ہے۔",draft:"مسودہ خارج"},
    ta:{loading:"அதிகாரப்பூர்வ வெளியீடுகளைச் சரிபார்க்கிறது…",none:"இன்னும் அதிகாரப்பூர்வ வெளியீடு வெளியிடப்படவில்லை. ஆதரிக்கப்படும் சாதனங்களில் இணைய இடைமுகம் தொடர்ந்து கிடைக்கும் மற்றும் நிறுவலாம்.",current:"சமீபத்திய அதிகாரப்பூர்வ வெளியீடு",prerelease:"முன்னோட்ட வெளியீடு",stable:"வெளியிடப்பட்ட பதிப்பு",published:"வெளியிடப்பட்டது",assets:"கிடைக்கும் கோப்புகள்",download:"பதிவிறக்கு",checksums:"SHA-256 சரிபார்ப்பு மதிப்புகள்",noChecksum:"இந்த வெளியீட்டில் SHA256SUMS கோப்பு இல்லை.",history:"முந்தைய வெளியீடுகள்",failed:"வெளியீட்டு தகவல் தற்காலிகமாக கிடைக்கவில்லை. பின்னர் முயற்சிக்கவும் அல்லது அதிகாரப்பூர்வ வெளியீடுகளைப் பார்க்கவும்.",integrity:"SHA-256 மதிப்புகள் பதிவிறக்கிய கோப்புகளை ஒப்பிட உதவுகின்றன. அவை குறியீட்டு கையொப்பம் அல்லது வெளியீட்டாளர் சரிபார்ப்பை மாற்றாது.",releaseNotes:"வெளியீட்டு குறிப்புகள்",noAssets:"இந்த வெளியீட்டில் நிறுவி இல்லை.",draft:"வரைவு நீக்கப்பட்டது"},
    te:{loading:"అధికారిక విడుదలలను తనిఖీ చేస్తోంది…",none:"ఇంకా అధికారిక విడుదల ఏదీ ప్రచురించబడలేదు. మద్దతు ఉన్న పరికరాల్లో వెబ్ ఇంటర్‌ఫేస్ అందుబాటులో ఉంటుంది మరియు ఇన్‌స్టాల్ చేయవచ్చు.",current:"తాజా అధికారిక విడుదల",prerelease:"ప్రివ్యూ విడుదల",stable:"ప్రచురించిన విడుదల",published:"ప్రచురించబడింది",assets:"అందుబాటులో ఉన్న ఫైళ్లు",download:"డౌన్‌లోడ్",checksums:"SHA-256 చెక్‌సమ్‌లు",noChecksum:"ఈ విడుదలకు SHA256SUMS ఫైల్ జతచేయలేదు.",history:"మునుపటి విడుదలలు",failed:"విడుదల సమాచారం తాత్కాలికంగా అందుబాటులో లేదు. తర్వాత మళ్లీ ప్రయత్నించండి లేదా అధికారిక విడుదలలను చూడండి.",integrity:"SHA-256 చెక్‌సమ్‌లు డౌన్‌లోడ్ చేసిన ఫైళ్లను పోల్చడంలో సహాయపడతాయి. అవి కోడ్ సంతకం లేదా ప్రచురణకర్త ధృవీకరణకు ప్రత్యామ్నాయం కావు.",releaseNotes:"విడుదల గమనికలు",noAssets:"ఈ విడుదలకు ఇన్‌స్టాలర్ జతచేయలేదు.",draft:"డ్రాఫ్ట్ మినహాయించబడింది"}
  };

  const getLanguage = () => String(languageSelect?.value || document.documentElement.lang || navigator.language || "en").toLowerCase().split("-")[0];
  const words = () => copy[getLanguage()] || copy.en;

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function safeDate(value) {
    if (!value) return "";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";
    const locale = getLanguage() === "en" ? "en-GB" : getLanguage() + "-" + getLanguage().toUpperCase();
    return new Intl.DateTimeFormat(locale, { dateStyle: "medium" }).format(date);
  }

  function externalLink(url, label) {
    if (!url || !/^https:\/\/github\.com\/gudjencio\/SSSWET\//i.test(url)) return null;
    const link = element("a", "", label);
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    return link;
  }

  function renderRelease(release, featured) {
    const w = words();
    const card = element("article", "version-release-card");
    const title = element("h3", "", release.name || release.tag_name || "SSSWET");
    card.append(title);
    if (featured) card.append(element("p", "", w.current));
    const meta = element("div", "version-release-meta");
    meta.append(element("span", "", release.prerelease ? w.prerelease : w.stable));
    const date = safeDate(release.published_at);
    if (date) meta.append(element("span", "", w.published + " · " + date));
    if (release.tag_name) meta.append(element("span", "", release.tag_name));
    card.append(meta);

    const assets = Array.isArray(release.assets) ? release.assets : [];
    const checksum = assets.find(asset => /^SHA256SUMS\.txt$/i.test(asset.name));
    if (assets.length) {
      card.append(element("p", "", w.assets));
      const links = element("div", "version-release-links");
      for (const asset of assets) {
        const link = externalLink(asset.browser_download_url, w.download + " · " + asset.name);
        if (link) links.append(link);
      }
      if (links.childElementCount) card.append(links);
    } else card.append(element("p", "", w.noAssets));

    const footer = element("div", "version-release-links");
    const notes = externalLink(release.html_url, w.releaseNotes);
    if (notes) footer.append(notes);
    if (checksum) {
      const checksumLink = externalLink(checksum.browser_download_url, w.checksums);
      if (checksumLink) footer.append(checksumLink);
    }
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
      const response = await fetch(releasesUrl, { headers:{Accept:"application/vnd.github+json"}, cache:"no-store" });
      if (!response.ok) throw new Error("GitHub Releases HTTP " + response.status);
      const releases = await response.json();
      const published = Array.isArray(releases) ? releases.filter(item => !item.draft && item.published_at) : [];
      if (!published.length) {
        status.dataset.state = "empty";
        status.textContent = w.none;
        integrity.textContent = w.integrity + " " + w.noChecksum;
        return;
      }
      const latest = published[0];
      const featured = renderRelease(latest, true);
      current.append(featured.card);
      status.dataset.state = "available";
      status.textContent = w.current + " · " + (latest.tag_name || latest.name || "SSSWET");
      if (!featured.checksum) integrity.textContent = w.integrity + " " + w.noChecksum;
      const previous = published.slice(1);
      if (previous.length) {
        history.append(element("p", "version-center-integrity", w.history));
        for (const release of previous) {
          const row = element("div", "version-history-item");
          const link = externalLink(release.html_url, release.name || release.tag_name || "SSSWET");
          if (link) row.append(link);
          row.append(element("time", "", safeDate(release.published_at)));
          history.append(row);
        }
      }
    } catch (_) {
      status.dataset.state = "error";
      status.textContent = w.failed;
      integrity.textContent = w.integrity;
    }
  }

  load();
  languageSelect?.addEventListener("change", load);
  window.addEventListener("online", load);
})();