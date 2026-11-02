(() => {
  "use strict";
  const panel = document.getElementById("platform-downloads");
  if (!panel) return;

  const installButton = document.getElementById("ssswet-install-app");
  const desktopLink = document.getElementById("ssswet-desktop-download");
  const mobileLink = document.getElementById("ssswet-mobile-download");
  const hint = document.getElementById("ssswet-install-hint");
  const languageSelect = document.getElementById("language");
  const mobile = window.matchMedia("(max-width: 760px), (pointer: coarse)").matches;
  const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
  let installPrompt = null;

  const copy = message => { if (hint) hint.textContent = message; };
  const dictionaries = {
    en:{heading:"Take SSSWET with you",intro:"Install the mobile experience or download the official desktop application.",install:"Install SSSWET",addHome:"Add SSSWET to your Home Screen",desktop:"Download desktop application",mobileRelease:"Android application · releases",installed:"SSSWET is installed",already:"The SSSWET application is already installed on this device.",safari:"In Safari, tap Share, then choose “Add to Home Screen”.",browser:"Install the mobile app from this browser, or download the Android package from official releases.",desktopHint:"Download the desktop application for Windows, macOS or Linux from official releases.",menu:"If installation is not offered, open the browser menu and choose “Install app” or “Add to Home Screen”.",done:"The SSSWET application has been installed."},
    fr:{heading:"Emportez SSSWET partout",intro:"Installez l’application mobile ou téléchargez le logiciel officiel pour ordinateur.",install:"Installer SSSWET",addHome:"Ajouter SSSWET à l’écran d’accueil",desktop:"Télécharger le logiciel pour ordinateur",mobileRelease:"Application Android · versions",installed:"SSSWET est installé",already:"L’application SSSWET est déjà installée sur cet appareil.",safari:"Dans Safari, touchez Partager, puis « Sur l’écran d’accueil ».",browser:"Installez l’application depuis ce navigateur ou téléchargez le paquet Android depuis les versions officielles.",desktopHint:"Téléchargez l’application pour Windows, macOS ou Linux depuis les versions officielles.",menu:"Si l’installation n’est pas proposée, ouvrez le menu du navigateur et choisissez « Installer l’application » ou « Ajouter à l’écran d’accueil ».",done:"L’application SSSWET a été installée."},
    es:{heading:"Lleva SSSWET contigo",intro:"Instala la experiencia móvil o descarga la aplicación oficial para ordenador.",install:"Instalar SSSWET",addHome:"Añadir SSSWET a la pantalla de inicio",desktop:"Descargar aplicación de escritorio",mobileRelease:"Aplicación Android · versiones",installed:"SSSWET está instalado",already:"La aplicación SSSWET ya está instalada en este dispositivo.",safari:"En Safari, toca Compartir y después «Añadir a pantalla de inicio».",browser:"Instala la aplicación desde este navegador o descarga el paquete Android desde las versiones oficiales.",desktopHint:"Descarga la aplicación para Windows, macOS o Linux desde las versiones oficiales.",menu:"Si no se ofrece la instalación, abre el menú del navegador y elige «Instalar aplicación» o «Añadir a pantalla de inicio».",done:"La aplicación SSSWET se ha instalado."},
    de:{heading:"SSSWET überall dabei",intro:"Installiere die mobile Version oder lade die offizielle Desktop-Anwendung herunter.",install:"SSSWET installieren",addHome:"SSSWET zum Startbildschirm hinzufügen",desktop:"Desktop-Anwendung herunterladen",mobileRelease:"Android-Anwendung · Versionen",installed:"SSSWET ist installiert",already:"Die SSSWET-Anwendung ist auf diesem Gerät bereits installiert.",safari:"Öffne in Safari Teilen und wähle „Zum Home-Bildschirm“.",browser:"Installiere die mobile Anwendung über diesen Browser oder lade das Android-Paket aus den offiziellen Versionen herunter.",desktopHint:"Lade die Anwendung für Windows, macOS oder Linux aus den offiziellen Versionen herunter.",menu:"Wenn die Installation nicht angeboten wird, öffne das Browsermenü und wähle „App installieren“ oder „Zum Home-Bildschirm“.",done:"Die SSSWET-Anwendung wurde installiert."},
    it:{heading:"Porta SSSWET con te",intro:"Installa l’esperienza mobile o scarica l’applicazione ufficiale per desktop.",install:"Installa SSSWET",addHome:"Aggiungi SSSWET alla schermata Home",desktop:"Scarica l’applicazione desktop",mobileRelease:"Applicazione Android · versioni",installed:"SSSWET è installato",already:"L’applicazione SSSWET è già installata su questo dispositivo.",safari:"In Safari, tocca Condividi e poi «Aggiungi alla schermata Home».",browser:"Installa l’app da questo browser oppure scarica il pacchetto Android dalle versioni ufficiali.",desktopHint:"Scarica l’applicazione per Windows, macOS o Linux dalle versioni ufficiali.",menu:"Se l’installazione non viene proposta, apri il menu del browser e scegli «Installa app» o «Aggiungi alla schermata Home».",done:"L’applicazione SSSWET è stata installata."},
    pt:{heading:"Leve o SSSWET com você",intro:"Instale a experiência móvel ou baixe o aplicativo oficial para computador.",install:"Instalar SSSWET",addHome:"Adicionar SSSWET à tela inicial",desktop:"Baixar aplicativo para computador",mobileRelease:"Aplicativo Android · versões",installed:"SSSWET está instalado",already:"O aplicativo SSSWET já está instalado neste dispositivo.",safari:"No Safari, toque em Compartilhar e depois em «Adicionar à Tela de Início».",browser:"Instale o aplicativo neste navegador ou baixe o pacote Android nas versões oficiais.",desktopHint:"Baixe o aplicativo para Windows, macOS ou Linux nas versões oficiais.",menu:"Se a instalação não for oferecida, abra o menu do navegador e escolha «Instalar aplicativo» ou «Adicionar à tela inicial».",done:"O aplicativo SSSWET foi instalado."},
    nl:{heading:"Neem SSSWET met je mee",intro:"Installeer de mobiele ervaring of download de officiële desktopapplicatie.",install:"SSSWET installeren",addHome:"SSSWET aan je startscherm toevoegen",desktop:"Desktopapplicatie downloaden",mobileRelease:"Android-applicatie · versies",installed:"SSSWET is geïnstalleerd",already:"De SSSWET-applicatie is al op dit apparaat geïnstalleerd.",safari:"Tik in Safari op Delen en kies daarna «Zet op beginscherm».",browser:"Installeer de app vanuit deze browser of download het Android-pakket uit de officiële versies.",desktopHint:"Download de applicatie voor Windows, macOS of Linux uit de officiële versies.",menu:"Als installatie niet wordt aangeboden, open dan het browsermenu en kies «App installeren» of «Aan startscherm toevoegen».",done:"De SSSWET-applicatie is geïnstalleerd."},
    ru:{heading:"Берите SSSWET с собой",intro:"Установите мобильную версию или скачайте официальное приложение для компьютера.",install:"Установить SSSWET",addHome:"Добавить SSSWET на главный экран",desktop:"Скачать приложение для компьютера",mobileRelease:"Приложение Android · версии",installed:"SSSWET установлен",already:"Приложение SSSWET уже установлено на этом устройстве.",safari:"В Safari нажмите «Поделиться», затем выберите «На экран Домой».",browser:"Установите приложение из этого браузера или скачайте пакет Android из официальных версий.",desktopHint:"Скачайте приложение для Windows, macOS или Linux из официальных версий.",menu:"Если установка недоступна, откройте меню браузера и выберите «Установить приложение» или «Добавить на главный экран».",done:"Приложение SSSWET установлено."},
    uk:{heading:"Беріть SSSWET із собою",intro:"Встановіть мобільну версію або завантажте офіційний застосунок для комп’ютера.",install:"Встановити SSSWET",addHome:"Додати SSSWET на головний екран",desktop:"Завантажити застосунок для комп’ютера",mobileRelease:"Застосунок Android · версії",installed:"SSSWET встановлено",already:"Застосунок SSSWET уже встановлено на цьому пристрої.",safari:"У Safari натисніть «Поділитися», потім виберіть «На початковий екран».",browser:"Встановіть застосунок із цього браузера або завантажте пакет Android з офіційних версій.",desktopHint:"Завантажте застосунок для Windows, macOS або Linux з офіційних версій.",menu:"Якщо встановлення не пропонується, відкрийте меню браузера та виберіть «Встановити застосунок» або «Додати на головний екран».",done:"Застосунок SSSWET встановлено."},
    ar:{heading:"اصطحب SSSWET معك",intro:"ثبّت التجربة على الهاتف أو نزّل تطبيق سطح المكتب الرسمي.",install:"تثبيت SSSWET",addHome:"إضافة SSSWET إلى الشاشة الرئيسية",desktop:"تنزيل تطبيق سطح المكتب",mobileRelease:"تطبيق Android · الإصدارات",installed:"تم تثبيت SSSWET",already:"تطبيق SSSWET مثبت بالفعل على هذا الجهاز.",safari:"في Safari اضغط «مشاركة» ثم اختر «إضافة إلى الشاشة الرئيسية».",browser:"ثبّت التطبيق من هذا المتصفح أو نزّل حزمة Android من الإصدارات الرسمية.",desktopHint:"نزّل التطبيق لنظام Windows أو macOS أو Linux من الإصدارات الرسمية.",menu:"إذا لم يظهر خيار التثبيت، افتح قائمة المتصفح واختر «تثبيت التطبيق» أو «إضافة إلى الشاشة الرئيسية».",done:"تم تثبيت تطبيق SSSWET."},
    he:{heading:"קחו את SSSWET איתכם",intro:"התקינו את חוויית המובייל או הורידו את יישום שולחן העבודה הרשמי.",install:"התקנת SSSWET",addHome:"הוספת SSSWET למסך הבית",desktop:"הורדת יישום למחשב",mobileRelease:"יישום Android · גרסאות",installed:"SSSWET מותקן",already:"יישום SSSWET כבר מותקן במכשיר הזה.",safari:"ב-Safari הקישו על שיתוף ולאחר מכן «הוספה למסך הבית».",browser:"התקינו את היישום מהדפדפן הזה או הורידו את חבילת Android מהגרסאות הרשמיות.",desktopHint:"הורידו את היישום עבור Windows, macOS או Linux מהגרסאות הרשמיות.",menu:"אם ההתקנה אינה מוצעת, פתחו את תפריט הדפדפן ובחרו «התקנת יישום» או «הוספה למסך הבית».",done:"יישום SSSWET הותקן."},
    ja:{heading:"SSSWETを持ち歩く",intro:"モバイル版をインストールするか、公式デスクトップアプリをダウンロードしてください。",install:"SSSWETをインストール",addHome:"SSSWETをホーム画面に追加",desktop:"デスクトップアプリをダウンロード",mobileRelease:"Androidアプリ · リリース",installed:"SSSWETはインストール済みです",already:"SSSWETアプリはこの端末にすでにインストールされています。",safari:"Safariで共有をタップし、「ホーム画面に追加」を選択してください。",browser:"このブラウザからアプリをインストールするか、公式リリースからAndroidパッケージをダウンロードしてください。",desktopHint:"公式リリースからWindows、macOS、Linux用アプリをダウンロードしてください。",menu:"インストールが表示されない場合は、ブラウザのメニューから「アプリをインストール」または「ホーム画面に追加」を選択してください。",done:"SSSWETアプリをインストールしました。"},
    ko:{heading:"SSSWET을 함께 사용하세요",intro:"모바일 환경을 설치하거나 공식 데스크톱 애플리케이션을 다운로드하세요.",install:"SSSWET 설치",addHome:"SSSWET을 홈 화면에 추가",desktop:"데스크톱 애플리케이션 다운로드",mobileRelease:"Android 애플리케이션 · 릴리스",installed:"SSSWET이 설치되었습니다",already:"SSSWET 애플리케이션이 이 기기에 이미 설치되어 있습니다.",safari:"Safari에서 공유를 누른 다음 «홈 화면에 추가»를 선택하세요.",browser:"이 브라우저에서 앱을 설치하거나 공식 릴리스에서 Android 패키지를 다운로드하세요.",desktopHint:"공식 릴리스에서 Windows, macOS 또는 Linux용 애플리케이션을 다운로드하세요.",menu:"설치가 제공되지 않으면 브라우저 메뉴에서 «앱 설치» 또는 «홈 화면에 추가»를 선택하세요.",done:"SSSWET 애플리케이션이 설치되었습니다."},
    zh:{heading:"随身使用 SSSWET",intro:"安装移动版体验，或下载官方桌面应用。",install:"安装 SSSWET",addHome:"将 SSSWET 添加到主屏幕",desktop:"下载桌面应用",mobileRelease:"Android 应用 · 版本",installed:"SSSWET 已安装",already:"SSSWET 应用已安装在此设备上。",safari:"在 Safari 中点击“分享”，然后选择“添加到主屏幕”。",browser:"从此浏览器安装应用，或从官方版本下载 Android 软件包。",desktopHint:"从官方版本下载 Windows、macOS 或 Linux 应用。",menu:"如果没有提供安装选项，请打开浏览器菜单并选择“安装应用”或“添加到主屏幕”。",done:"SSSWET 应用已安装。"},
    hi:{heading:"SSSWET को अपने साथ रखें",intro:"मोबाइल अनुभव इंस्टॉल करें या आधिकारिक डेस्कटॉप ऐप डाउनलोड करें।",install:"SSSWET इंस्टॉल करें",addHome:"SSSWET को होम स्क्रीन पर जोड़ें",desktop:"डेस्कटॉप ऐप डाउनलोड करें",mobileRelease:"Android ऐप · रिलीज़",installed:"SSSWET इंस्टॉल है",already:"SSSWET ऐप इस डिवाइस पर पहले से इंस्टॉल है।",safari:"Safari में शेयर दबाएँ, फिर «होम स्क्रीन में जोड़ें» चुनें।",browser:"इस ब्राउज़र से ऐप इंस्टॉल करें या आधिकारिक रिलीज़ से Android पैकेज डाउनलोड करें।",desktopHint:"आधिकारिक रिलीज़ से Windows, macOS या Linux के लिए ऐप डाउनलोड करें।",menu:"यदि इंस्टॉल विकल्प नहीं दिखता है, तो ब्राउज़र मेनू खोलकर «ऐप इंस्टॉल करें» या «होम स्क्रीन में जोड़ें» चुनें।",done:"SSSWET ऐप इंस्टॉल हो गया है।"},
    id:{heading:"Bawa SSSWET bersama Anda",intro:"Pasang pengalaman seluler atau unduh aplikasi desktop resmi.",install:"Pasang SSSWET",addHome:"Tambahkan SSSWET ke layar utama",desktop:"Unduh aplikasi desktop",mobileRelease:"Aplikasi Android · rilis",installed:"SSSWET terpasang",already:"Aplikasi SSSWET sudah terpasang di perangkat ini.",safari:"Di Safari, ketuk Bagikan lalu pilih «Tambahkan ke Layar Utama».",browser:"Pasang aplikasi dari browser ini atau unduh paket Android dari rilis resmi.",desktopHint:"Unduh aplikasi untuk Windows, macOS, atau Linux dari rilis resmi.",menu:"Jika pemasangan tidak ditawarkan, buka menu browser dan pilih «Pasang aplikasi» atau «Tambahkan ke layar utama».",done:"Aplikasi SSSWET telah terpasang."},
    tr:{heading:"SSSWET’i yanınızda taşıyın",intro:"Mobil deneyimi yükleyin veya resmi masaüstü uygulamasını indirin.",install:"SSSWET’i yükle",addHome:"SSSWET’i ana ekrana ekle",desktop:"Masaüstü uygulamasını indir",mobileRelease:"Android uygulaması · sürümler",installed:"SSSWET yüklendi",already:"SSSWET uygulaması bu cihazda zaten yüklü.",safari:"Safari’de Paylaş’a dokunun ve ardından «Ana Ekrana Ekle»yi seçin.",browser:"Uygulamayı bu tarayıcıdan yükleyin veya Android paketini resmi sürümlerden indirin.",desktopHint:"Windows, macOS veya Linux uygulamasını resmi sürümlerden indirin.",menu:"Yükleme sunulmuyorsa tarayıcı menüsünü açıp «Uygulamayı yükle» veya «Ana ekrana ekle» seçeneğini seçin.",done:"SSSWET uygulaması yüklendi."},
    pl:{heading:"Zabierz SSSWET ze sobą",intro:"Zainstaluj wersję mobilną lub pobierz oficjalną aplikację na komputer.",install:"Zainstaluj SSSWET",addHome:"Dodaj SSSWET do ekranu głównego",desktop:"Pobierz aplikację na komputer",mobileRelease:"Aplikacja Android · wydania",installed:"SSSWET jest zainstalowany",already:"Aplikacja SSSWET jest już zainstalowana na tym urządzeniu.",safari:"W Safari wybierz Udostępnij, a następnie «Dodaj do ekranu początkowego».",browser:"Zainstaluj aplikację w tej przeglądarce lub pobierz pakiet Android z oficjalnych wydań.",desktopHint:"Pobierz aplikację dla Windows, macOS lub Linux z oficjalnych wydań.",menu:"Jeśli instalacja nie jest dostępna, otwórz menu przeglądarki i wybierz «Zainstaluj aplikację» lub «Dodaj do ekranu głównego».",done:"Aplikacja SSSWET została zainstalowana."},
    bn:{heading:"SSSWET সঙ্গে রাখুন",intro:"মোবাইল অভিজ্ঞতা ইনস্টল করুন অথবা অফিসিয়াল ডেস্কটপ অ্যাপ ডাউনলোড করুন।",install:"SSSWET ইনস্টল করুন",addHome:"হোম স্ক্রিনে SSSWET যোগ করুন",desktop:"ডেস্কটপ অ্যাপ ডাউনলোড করুন",mobileRelease:"Android অ্যাপ · রিলিজ",installed:"SSSWET ইনস্টল হয়েছে",already:"এই ডিভাইসে SSSWET অ্যাপ ইতিমধ্যে ইনস্টল করা আছে।",safari:"Safari-তে শেয়ার চাপুন, তারপর «হোম স্ক্রিনে যোগ করুন» নির্বাচন করুন।",browser:"এই ব্রাউজার থেকে অ্যাপ ইনস্টল করুন অথবা অফিসিয়াল রিলিজ থেকে Android প্যাকেজ ডাউনলোড করুন।",desktopHint:"অফিসিয়াল রিলিজ থেকে Windows, macOS বা Linux-এর অ্যাপ ডাউনলোড করুন।",menu:"ইনস্টলেশন না এলে ব্রাউজার মেনু খুলে «অ্যাপ ইনস্টল করুন» বা «হোম স্ক্রিনে যোগ করুন» নির্বাচন করুন।",done:"SSSWET অ্যাপ ইনস্টল হয়েছে।"},
    sw:{heading:"Beba SSSWET nawe",intro:"Sakinisha matumizi ya simu au pakua programu rasmi ya kompyuta.",install:"Sakinisha SSSWET",addHome:"Ongeza SSSWET kwenye skrini ya mwanzo",desktop:"Pakua programu ya kompyuta",mobileRelease:"Programu ya Android · matoleo",installed:"SSSWET imesakinishwa",already:"Programu ya SSSWET tayari imesakinishwa kwenye kifaa hiki.",safari:"Kwenye Safari, gusa Shiriki kisha uchague «Ongeza kwenye Skrini ya Mwanzo».",browser:"Sakinisha programu kutoka kivinjari hiki au pakua kifurushi cha Android kutoka matoleo rasmi.",desktopHint:"Pakua programu ya Windows, macOS au Linux kutoka matoleo rasmi.",menu:"Ikiwa usakinishaji haujatolewa, fungua menyu ya kivinjari na uchague «Sakinisha programu» au «Ongeza kwenye skrini ya mwanzo».",done:"Programu ya SSSWET imesakinishwa."},
    vi:{heading:"Mang SSSWET theo bạn",intro:"Cài đặt phiên bản di động hoặc tải ứng dụng máy tính chính thức.",install:"Cài đặt SSSWET",addHome:"Thêm SSSWET vào màn hình chính",desktop:"Tải ứng dụng máy tính",mobileRelease:"Ứng dụng Android · bản phát hành",installed:"SSSWET đã được cài đặt",already:"Ứng dụng SSSWET đã được cài đặt trên thiết bị này.",safari:"Trong Safari, chạm Chia sẻ rồi chọn «Thêm vào Màn hình chính».",browser:"Cài đặt ứng dụng từ trình duyệt này hoặc tải gói Android từ các bản phát hành chính thức.",desktopHint:"Tải ứng dụng cho Windows, macOS hoặc Linux từ các bản phát hành chính thức.",menu:"Nếu không có tùy chọn cài đặt, mở menu trình duyệt và chọn «Cài đặt ứng dụng» hoặc «Thêm vào màn hình chính».",done:"Ứng dụng SSSWET đã được cài đặt."},
    fa:{heading:"SSSWET را همراه خود داشته باشید",intro:"نسخه موبایل را نصب کنید یا برنامه رسمی دسکتاپ را دریافت کنید.",install:"نصب SSSWET",addHome:"افزودن SSSWET به صفحه اصلی",desktop:"دانلود برنامه دسکتاپ",mobileRelease:"برنامه Android · انتشارها",installed:"SSSWET نصب شده است",already:"برنامه SSSWET از قبل روی این دستگاه نصب شده است.",safari:"در Safari روی اشتراک‌گذاری بزنید و سپس «افزودن به صفحه اصلی» را انتخاب کنید.",browser:"برنامه را از این مرورگر نصب کنید یا بسته Android را از انتشارهای رسمی دریافت کنید.",desktopHint:"برنامه Windows، macOS یا Linux را از انتشارهای رسمی دانلود کنید.",menu:"اگر گزینه نصب نمایش داده نشد، منوی مرورگر را باز کنید و «نصب برنامه» یا «افزودن به صفحه اصلی» را انتخاب کنید.",done:"برنامه SSSWET نصب شد."},
    ur:{heading:"SSSWET کو اپنے ساتھ رکھیں",intro:"موبائل تجربہ انسٹال کریں یا سرکاری ڈیسک ٹاپ ایپ ڈاؤن لوڈ کریں۔",install:"SSSWET انسٹال کریں",addHome:"SSSWET کو ہوم اسکرین پر شامل کریں",desktop:"ڈیسک ٹاپ ایپ ڈاؤن لوڈ کریں",mobileRelease:"Android ایپ · ریلیزز",installed:"SSSWET انسٹال ہے",already:"SSSWET ایپ اس ڈیوائس پر پہلے سے انسٹال ہے۔",safari:"Safari میں شیئر دبائیں، پھر «ہوم اسکرین میں شامل کریں» منتخب کریں۔",browser:"اس براؤزر سے ایپ انسٹال کریں یا سرکاری ریلیزز سے Android پیکیج ڈاؤن لوڈ کریں۔",desktopHint:"سرکاری ریلیزز سے Windows، macOS یا Linux کے لیے ایپ ڈاؤن لوڈ کریں۔",menu:"اگر انسٹالیشن دستیاب نہ ہو تو براؤزر مینو کھولیں اور «ایپ انسٹال کریں» یا «ہوم اسکرین میں شامل کریں» منتخب کریں۔",done:"SSSWET ایپ انسٹال ہو گئی ہے۔"},
    ta:{heading:"SSSWET-ஐ உடன் எடுத்துச் செல்லுங்கள்",intro:"மொபைல் அனுபவத்தை நிறுவவும் அல்லது அதிகாரப்பூர்வ டெஸ்க்டாப் பயன்பாட்டைப் பதிவிறக்கவும்.",install:"SSSWET-ஐ நிறுவு",addHome:"SSSWET-ஐ முகப்புத் திரையில் சேர்",desktop:"டெஸ்க்டாப் பயன்பாட்டைப் பதிவிறக்கு",mobileRelease:"Android பயன்பாடு · வெளியீடுகள்",installed:"SSSWET நிறுவப்பட்டுள்ளது",already:"SSSWET பயன்பாடு இந்தச் சாதனத்தில் ஏற்கனவே நிறுவப்பட்டுள்ளது.",safari:"Safari-ல் பகிர் என்பதைத் தட்டி «முகப்புத் திரையில் சேர்» என்பதைத் தேர்ந்தெடுக்கவும்.",browser:"இந்த உலாவியில் இருந்து பயன்பாட்டை நிறுவவும் அல்லது அதிகாரப்பூர்வ வெளியீடுகளில் இருந்து Android தொகுப்பைப் பதிவிறக்கவும்.",desktopHint:"அதிகாரப்பூர்வ வெளியீடுகளில் இருந்து Windows, macOS அல்லது Linux பயன்பாட்டைப் பதிவிறக்கவும்.",menu:"நிறுவல் வழங்கப்படாவிட்டால், உலாவி மெனுவைத் திறந்து «பயன்பாட்டை நிறுவு» அல்லது «முகப்புத் திரையில் சேர்» என்பதைத் தேர்ந்தெடுக்கவும்.",done:"SSSWET பயன்பாடு நிறுவப்பட்டது."},
    te:{heading:"SSSWETను మీతో తీసుకెళ్లండి",intro:"మొబైల్ అనుభవాన్ని ఇన్‌స్టాల్ చేయండి లేదా అధికారిక డెస్క్‌టాప్ యాప్‌ను డౌన్‌లోడ్ చేయండి.",install:"SSSWETను ఇన్‌స్టాల్ చేయండి",addHome:"SSSWETను హోమ్ స్క్రీన్‌కు జోడించండి",desktop:"డెస్క్‌టాప్ యాప్‌ను డౌన్‌లోడ్ చేయండి",mobileRelease:"Android యాప్ · విడుదలలు",installed:"SSSWET ఇన్‌స్టాల్ చేయబడింది",already:"SSSWET యాప్ ఈ పరికరంలో ఇప్పటికే ఇన్‌స్టాల్ చేయబడింది.",safari:"Safariలో Share నొక్కి, «Add to Home Screen» ఎంచుకోండి.",browser:"ఈ బ్రౌజర్ నుంచి యాప్‌ను ఇన్‌స్టాల్ చేయండి లేదా అధికారిక విడుదలల నుంచి Android ప్యాకేజీని డౌన్‌లోడ్ చేయండి.",desktopHint:"అధికారిక విడుదలల నుంచి Windows, macOS లేదా Linux కోసం యాప్‌ను డౌన్‌లోడ్ చేయండి.",menu:"ఇన్‌స్టాల్ ఎంపిక కనిపించకపోతే, బ్రౌజర్ మెనూను తెరిచి «Install app» లేదా «Add to Home Screen» ఎంచుకోండి.",done:"SSSWET యాప్ ఇన్‌స్టాల్ చేయబడింది."}
  };

  const getLanguage = () => String(languageSelect?.value || document.documentElement.lang || navigator.language || "en").toLowerCase().split("-")[0];
  const labelsFor = () => dictionaries[getLanguage()] || dictionaries.en;
  const heading = document.getElementById("platform-downloads-title");
  const intro = panel.querySelector(".platform-downloads-copy > p:not(.eyebrow)");

  function applyLabels() {
    const labels = labelsFor();
    if (heading) heading.textContent = labels.heading;
    if (intro) intro.textContent = labels.intro;
    if (installButton) installButton.textContent = labels.install;
    if (mobileLink) mobileLink.textContent = labels.mobileRelease;
    if (desktopLink) desktopLink.textContent = labels.desktop;

    const isStandalone = window.matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;
    if (mobile) {
      panel.dataset.platform = "mobile";
      desktopLink.hidden = true;
      mobileLink.hidden = false;
      installButton.hidden = false;
      if (isStandalone) {
        installButton.textContent = labels.installed;
        installButton.disabled = true;
        copy(labels.already);
      } else if (isIOS) {
        installButton.textContent = labels.addHome;
        copy(labels.safari);
      } else {
        installButton.textContent = labels.install;
        copy(labels.browser);
      }
    } else {
      panel.dataset.platform = "desktop";
      mobileLink.hidden = true;
      desktopLink.hidden = false;
      installButton.hidden = true;
      copy(labels.desktopHint);
    }
  }

  applyLabels();
  languageSelect?.addEventListener("change", applyLabels);

  window.addEventListener("beforeinstallprompt", event => {
    event.preventDefault();
    installPrompt = event;
    if (mobile && installButton && !(window.matchMedia("(display-mode: standalone)").matches || navigator.standalone === true)) installButton.hidden = false;
  });

  installButton?.addEventListener("click", async () => {
    const labels = labelsFor();
    if (isIOS) {
      copy(labels.safari);
      return;
    }
    if (!installPrompt) {
      copy(labels.menu);
      return;
    }
    installPrompt.prompt();
    await installPrompt.userChoice;
    installPrompt = null;
  });

  window.addEventListener("appinstalled", () => {
    const labels = labelsFor();
    installButton.textContent = labels.installed;
    installButton.disabled = true;
    copy(labels.done);
  });
})();