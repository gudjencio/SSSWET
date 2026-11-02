(() => {
  "use strict";

  const copy = {
    en:{button:"Report",title:"Suggest a project improvement",intro:"Choose a useful improvement or correction. Reports enter the project review queue; nothing is changed automatically.",category:"Improvement area",titleLabel:"Short title",detail:"What should be improved?",send:"Send report",cancel:"Cancel",sending:"Sending…",success:"Thank you. Your suggestion was added to the project review queue.",unavailable:"Report submission is not configured yet. Please try again later.",error:"The report could not be sent. Please try again later.",placeholder:"Describe the improvement and, if possible, the expected result.",options:[["bug","Bug or display correction"],["translation","Translation and language quality"],["accessibility","Accessibility and inclusive design"],["performance","Performance and loading speed"],["security","Security and privacy"],["documentation","Documentation and guidance"],["research-quality","Scientific rigour and source traceability"],["reliability","Reliability and data integrity"],["usability","Interface clarity and ease of use"],["new-feature","Useful new feature"],["compatibility","Browser and device compatibility"],["other","Other useful improvement"]]},
    fr:{button:"Signaler",title:"Proposer une amélioration du projet",intro:"Choisissez une amélioration utile ou une correction. Les signalements rejoignent la file d’examen du projet ; aucune modification n’est appliquée automatiquement.",category:"Domaine d’amélioration",titleLabel:"Titre court",detail:"Que faudrait-il améliorer ?",send:"Envoyer le signalement",cancel:"Annuler",sending:"Envoi…",success:"Merci. Votre suggestion a été ajoutée à la file d’examen du projet.",unavailable:"L’envoi des signalements n’est pas encore configuré. Réessayez plus tard.",error:"Le signalement n’a pas pu être envoyé. Réessayez plus tard.",placeholder:"Décrivez l’amélioration et, si possible, le résultat attendu.",options:[["bug","Bug ou correction d’affichage"],["translation","Traductions et qualité linguistique"],["accessibility","Accessibilité et conception inclusive"],["performance","Performances et vitesse de chargement"],["security","Sécurité et confidentialité"],["documentation","Documentation et guides"],["research-quality","Rigueur scientifique et traçabilité des sources"],["reliability","Fiabilité et intégrité des données"],["usability","Clarté et facilité d’utilisation"],["new-feature","Nouvelle fonctionnalité utile"],["compatibility","Compatibilité navigateurs et appareils"],["other","Autre amélioration utile"]]},
    es:{button:"Informar",title:"Proponer una mejora del proyecto",intro:"Elige una mejora útil o una corrección. Los informes se añaden a la cola de revisión; no se modifica nada automáticamente.",category:"Área de mejora",titleLabel:"Título breve",detail:"¿Qué se debería mejorar?",send:"Enviar informe",cancel:"Cancelar",sending:"Enviando…",success:"Gracias. Tu sugerencia se ha añadido a la cola de revisión.",unavailable:"El envío de informes aún no está configurado. Inténtalo más tarde.",error:"No se pudo enviar el informe. Inténtalo de nuevo.",placeholder:"Describe la mejora y, si es posible, el resultado esperado.",options:[["bug","Error o corrección visual"],["translation","Traducción y calidad lingüística"],["accessibility","Accesibilidad y diseño inclusivo"],["performance","Rendimiento y velocidad de carga"],["security","Seguridad y privacidad"],["documentation","Documentación y guías"],["research-quality","Rigor científico y trazabilidad de fuentes"],["reliability","Fiabilidad e integridad de datos"],["usability","Claridad y facilidad de uso"],["new-feature","Nueva función útil"],["compatibility","Compatibilidad con navegadores y dispositivos"],["other","Otra mejora útil"]]},
    de:{button:"Melden",title:"Projektverbesserung vorschlagen",intro:"Wähle eine sinnvolle Verbesserung oder Korrektur. Meldungen werden geprüft; Änderungen erfolgen nicht automatisch.",category:"Verbesserungsbereich",titleLabel:"Kurzer Titel",detail:"Was sollte verbessert werden?",send:"Meldung senden",cancel:"Abbrechen",sending:"Wird gesendet…",success:"Vielen Dank. Dein Vorschlag wurde zur Prüfung eingereicht.",unavailable:"Das Melden ist noch nicht eingerichtet. Bitte später erneut versuchen.",error:"Die Meldung konnte nicht gesendet werden. Bitte erneut versuchen.",placeholder:"Beschreibe die Verbesserung und möglichst das gewünschte Ergebnis.",options:[["bug","Fehler oder Darstellungsproblem"],["translation","Übersetzung und Sprachqualität"],["accessibility","Barrierefreiheit und inklusives Design"],["performance","Leistung und Ladegeschwindigkeit"],["security","Sicherheit und Datenschutz"],["documentation","Dokumentation und Anleitungen"],["research-quality","Wissenschaftliche Sorgfalt und Quellenprüfung"],["reliability","Zuverlässigkeit und Datenintegrität"],["usability","Übersichtlichkeit und Bedienbarkeit"],["new-feature","Nützliche neue Funktion"],["compatibility","Browser- und Gerätekompatibilität"],["other","Sonstige sinnvolle Verbesserung"]]},
    it:{button:"Segnala",title:"Suggerisci un miglioramento del progetto",intro:"Scegli un miglioramento utile o una correzione. Le segnalazioni vengono esaminate; nessuna modifica viene applicata automaticamente.",category:"Area di miglioramento",titleLabel:"Titolo breve",detail:"Che cosa dovrebbe essere migliorato?",send:"Invia segnalazione",cancel:"Annulla",sending:"Invio…",success:"Grazie. Il suggerimento è stato aggiunto alla coda di revisione.",unavailable:"L’invio delle segnalazioni non è ancora configurato. Riprova più tardi.",error:"Impossibile inviare la segnalazione. Riprova.",placeholder:"Descrivi il miglioramento e, se possibile, il risultato atteso.",options:[["bug","Errore o problema di visualizzazione"],["translation","Traduzione e qualità linguistica"],["accessibility","Accessibilità e design inclusivo"],["performance","Prestazioni e velocità di caricamento"],["security","Sicurezza e privacy"],["documentation","Documentazione e guide"],["research-quality","Rigore scientifico e tracciabilità delle fonti"],["reliability","Affidabilità e integrità dei dati"],["usability","Chiarezza e facilità d’uso"],["new-feature","Nuova funzione utile"],["compatibility","Compatibilità con browser e dispositivi"],["other","Altro miglioramento utile"]]},
    pt:{button:"Denunciar",title:"Sugerir uma melhoria do projeto",intro:"Escolha uma melhoria útil ou correção. Os relatos entram na fila de análise; nenhuma alteração é aplicada automaticamente.",category:"Área de melhoria",titleLabel:"Título curto",detail:"O que deve ser melhorado?",send:"Enviar relato",cancel:"Cancelar",sending:"Enviando…",success:"Obrigado. Sua sugestão foi adicionada à fila de análise.",unavailable:"O envio de relatos ainda não está configurado. Tente novamente mais tarde.",error:"Não foi possível enviar o relato. Tente novamente.",placeholder:"Descreva a melhoria e, se possível, o resultado esperado.",options:[["bug","Erro ou problema de exibição"],["translation","Tradução e qualidade linguística"],["accessibility","Acessibilidade e design inclusivo"],["performance","Desempenho e velocidade de carregamento"],["security","Segurança e privacidade"],["documentation","Documentação e orientações"],["research-quality","Rigor científico e rastreabilidade das fontes"],["reliability","Confiabilidade e integridade dos dados"],["usability","Clareza e facilidade de uso"],["new-feature","Novo recurso útil"],["compatibility","Compatibilidade com navegadores e dispositivos"],["other","Outra melhoria útil"]]},
    nl:{button:"Melden",title:"Een projectverbetering voorstellen",intro:"Kies een nuttige verbetering of correctie. Meldingen worden beoordeeld; er worden niet automatisch wijzigingen aangebracht.",category:"Verbetergebied",titleLabel:"Korte titel",detail:"Wat moet worden verbeterd?",send:"Melding verzenden",cancel:"Annuleren",sending:"Verzenden…",success:"Bedankt. Je voorstel is aan de beoordelingswachtrij toegevoegd.",unavailable:"Meldingen versturen is nog niet ingesteld. Probeer het later opnieuw.",error:"De melding kon niet worden verzonden. Probeer het opnieuw.",placeholder:"Beschrijf de verbetering en indien mogelijk het gewenste resultaat.",options:[["bug","Fout of weergaveprobleem"],["translation","Vertaling en taalkwaliteit"],["accessibility","Toegankelijkheid en inclusief ontwerp"],["performance","Prestaties en laadsnelheid"],["security","Beveiliging en privacy"],["documentation","Documentatie en handleidingen"],["research-quality","Wetenschappelijke zorgvuldigheid en bronvermelding"],["reliability","Betrouwbaarheid en gegevensintegriteit"],["usability","Duidelijkheid en gebruiksgemak"],["new-feature","Nuttige nieuwe functie"],["compatibility","Compatibiliteit met browsers en apparaten"],["other","Andere nuttige verbetering"]]},
    ru:{button:"Сообщить",title:"Предложить улучшение проекта",intro:"Выберите полезное улучшение или исправление. Сообщения поступают на рассмотрение; изменения автоматически не применяются.",category:"Область улучшения",titleLabel:"Краткий заголовок",detail:"Что следует улучшить?",send:"Отправить сообщение",cancel:"Отмена",sending:"Отправка…",success:"Спасибо. Предложение добавлено в очередь на рассмотрение.",unavailable:"Отправка сообщений пока не настроена. Повторите попытку позже.",error:"Не удалось отправить сообщение. Попробуйте ещё раз.",placeholder:"Опишите улучшение и, по возможности, ожидаемый результат.",options:[["bug","Ошибка или проблема отображения"],["translation","Перевод и качество языка"],["accessibility","Доступность и инклюзивный дизайн"],["performance","Производительность и скорость загрузки"],["security","Безопасность и конфиденциальность"],["documentation","Документация и инструкции"],["research-quality","Научная строгость и проверяемость источников"],["reliability","Надёжность и целостность данных"],["usability","Понятность и удобство интерфейса"],["new-feature","Полезная новая функция"],["compatibility","Совместимость с браузерами и устройствами"],["other","Другое полезное улучшение"]]},
    uk:{button:"Повідомити",title:"Запропонувати покращення проєкту",intro:"Оберіть корисне покращення або виправлення. Повідомлення надходять на розгляд; зміни автоматично не застосовуються.",category:"Напрям покращення",titleLabel:"Коротка назва",detail:"Що варто покращити?",send:"Надіслати повідомлення",cancel:"Скасувати",sending:"Надсилання…",success:"Дякуємо. Пропозицію додано до черги на розгляд.",unavailable:"Надсилання повідомлень ще не налаштовано. Спробуйте пізніше.",error:"Не вдалося надіслати повідомлення. Спробуйте ще раз.",placeholder:"Опишіть покращення та, якщо можливо, очікуваний результат.",options:[["bug","Помилка або проблема відображення"],["translation","Переклад і мовна якість"],["accessibility","Доступність та інклюзивний дизайн"],["performance","Продуктивність і швидкість завантаження"],["security","Безпека та конфіденційність"],["documentation","Документація та інструкції"],["research-quality","Наукова обґрунтованість і простежуваність джерел"],["reliability","Надійність і цілісність даних"],["usability","Зрозумілість і зручність інтерфейсу"],["new-feature","Корисна нова функція"],["compatibility","Сумісність із браузерами та пристроями"],["other","Інше корисне покращення"]]},
    ar:{button:"إبلاغ",title:"اقتراح تحسين للمشروع",intro:"اختر تحسينًا مفيدًا أو تصحيحًا. تُضاف البلاغات إلى قائمة المراجعة ولا تُطبّق أي تغييرات تلقائيًا.",category:"مجال التحسين",titleLabel:"عنوان مختصر",detail:"ما الذي ينبغي تحسينه؟",send:"إرسال البلاغ",cancel:"إلغاء",sending:"جارٍ الإرسال…",success:"شكرًا لك. أُضيف اقتراحك إلى قائمة مراجعة المشروع.",unavailable:"لم يتم إعداد إرسال البلاغات بعد. يرجى المحاولة لاحقًا.",error:"تعذّر إرسال البلاغ. يرجى المحاولة مجددًا.",placeholder:"صف التحسين والنتيجة المتوقعة إن أمكن.",options:[["bug","خلل أو مشكلة في العرض"],["translation","الترجمة وجودة اللغة"],["accessibility","إمكانية الوصول والتصميم الشامل"],["performance","الأداء وسرعة التحميل"],["security","الأمان والخصوصية"],["documentation","التوثيق والإرشادات"],["research-quality","الدقة العلمية وإمكانية تتبع المصادر"],["reliability","الموثوقية وسلامة البيانات"],["usability","وضوح الواجهة وسهولة الاستخدام"],["new-feature","ميزة جديدة مفيدة"],["compatibility","التوافق مع المتصفحات والأجهزة"],["other","تحسين مفيد آخر"]]},
    he:{button:"דיווח",title:"הצעת שיפור לפרויקט",intro:"בחרו שיפור מועיל או תיקון. הדיווחים מועברים לבדיקה; שינויים אינם מתבצעים באופן אוטומטי.",category:"תחום השיפור",titleLabel:"כותרת קצרה",detail:"מה כדאי לשפר?",send:"שליחת דיווח",cancel:"ביטול",sending:"שולח…",success:"תודה. ההצעה נוספה לתור הבדיקה של הפרויקט.",unavailable:"שליחת דיווחים עדיין אינה מוגדרת. נסו שוב מאוחר יותר.",error:"לא ניתן לשלוח את הדיווח. נסו שוב.",placeholder:"תארו את השיפור ואם אפשר גם את התוצאה הרצויה.",options:[["bug","תקלה או בעיית תצוגה"],["translation","תרגום ואיכות שפה"],["accessibility","נגישות ועיצוב מכליל"],["performance","ביצועים ומהירות טעינה"],["security","אבטחה ופרטיות"],["documentation","תיעוד והנחיות"],["research-quality","קפדנות מדעית ומעקב אחר מקורות"],["reliability","אמינות ושלמות נתונים"],["usability","בהירות הממשק וקלות השימוש"],["new-feature","תכונה חדשה ומועילה"],["compatibility","תאימות לדפדפנים ולמכשירים"],["other","שיפור מועיל אחר"]]},
    ja:{button:"報告",title:"プロジェクトの改善を提案",intro:"役立つ改善案または修正点を選んでください。報告は確認待ちリストに追加され、自動的に変更が適用されることはありません。",category:"改善分野",titleLabel:"短いタイトル",detail:"何を改善すべきですか？",send:"報告を送信",cancel:"キャンセル",sending:"送信中…",success:"ありがとうございます。提案がプロジェクトの確認待ちリストに追加されました。",unavailable:"報告機能はまだ設定されていません。後でもう一度お試しください。",error:"報告を送信できませんでした。もう一度お試しください。",placeholder:"改善案と、可能であれば期待する結果を記入してください。",options:[["bug","不具合・表示の修正"],["translation","翻訳と言語品質"],["accessibility","アクセシビリティとインクルーシブデザイン"],["performance","性能と読み込み速度"],["security","セキュリティとプライバシー"],["documentation","ドキュメントとガイド"],["research-quality","科学的厳密性と情報源の追跡可能性"],["reliability","信頼性とデータ整合性"],["usability","分かりやすさと使いやすさ"],["new-feature","役立つ新機能"],["compatibility","ブラウザー・端末との互換性"],["other","その他の有用な改善"]]},
    ko:{button:"신고",title:"프로젝트 개선 제안",intro:"유용한 개선 사항이나 수정 사항을 선택하세요. 제안은 검토 대기열에 추가되며 변경 사항이 자동으로 적용되지는 않습니다.",category:"개선 분야",titleLabel:"짧은 제목",detail:"무엇을 개선해야 하나요?",send:"신고 보내기",cancel:"취소",sending:"전송 중…",success:"감사합니다. 제안이 프로젝트 검토 대기열에 추가되었습니다.",unavailable:"신고 제출 기능이 아직 설정되지 않았습니다. 나중에 다시 시도하세요.",error:"신고를 보내지 못했습니다. 다시 시도하세요.",placeholder:"개선 사항과 가능하면 기대하는 결과를 설명해 주세요.",options:[["bug","오류 또는 화면 표시 수정"],["translation","번역 및 언어 품질"],["accessibility","접근성 및 포용적 디자인"],["performance","성능 및 로딩 속도"],["security","보안 및 개인정보 보호"],["documentation","문서 및 안내"],["research-quality","과학적 엄밀성 및 출처 추적성"],["reliability","신뢰성 및 데이터 무결성"],["usability","인터페이스의 명확성과 사용 편의성"],["new-feature","유용한 새 기능"],["compatibility","브라우저 및 기기 호환성"],["other","기타 유용한 개선 사항"]]},
    zh:{button:"报告",title:"提出项目改进建议",intro:"请选择一项有用的改进或修正。报告将进入项目审核队列，不会自动应用任何更改。",category:"改进领域",titleLabel:"简短标题",detail:"需要改进什么？",send:"发送报告",cancel:"取消",sending:"正在发送…",success:"谢谢！您的建议已加入项目审核队列。",unavailable:"报告提交功能尚未配置，请稍后重试。",error:"报告发送失败，请重试。",placeholder:"请描述改进内容，并尽可能说明预期结果。",options:[["bug","错误或显示问题"],["translation","翻译与语言质量"],["accessibility","无障碍与包容性设计"],["performance","性能与加载速度"],["security","安全与隐私"],["documentation","文档与使用指南"],["research-quality","科学严谨性与来源可追溯性"],["reliability","可靠性与数据完整性"],["usability","界面清晰度与易用性"],["new-feature","实用的新功能"],["compatibility","浏览器与设备兼容性"],["other","其他有用的改进"]]},
    hi:{button:"रिपोर्ट करें",title:"परियोजना में सुधार सुझाएँ",intro:"कोई उपयोगी सुधार या त्रुटि-सुधार चुनें। रिपोर्ट समीक्षा कतार में जोड़ी जाएगी; कोई बदलाव अपने-आप लागू नहीं होगा।",category:"सुधार का क्षेत्र",titleLabel:"संक्षिप्त शीर्षक",detail:"किस चीज़ में सुधार होना चाहिए?",send:"रिपोर्ट भेजें",cancel:"रद्द करें",sending:"भेजा जा रहा है…",success:"धन्यवाद। आपका सुझाव परियोजना की समीक्षा कतार में जोड़ दिया गया है।",unavailable:"रिपोर्ट भेजने की सुविधा अभी कॉन्फ़िगर नहीं है। बाद में फिर प्रयास करें।",error:"रिपोर्ट नहीं भेजी जा सकी। कृपया फिर प्रयास करें।",placeholder:"सुधार का वर्णन करें और संभव हो तो अपेक्षित परिणाम भी बताएँ।",options:[["bug","त्रुटि या प्रदर्शन संबंधी समस्या"],["translation","अनुवाद और भाषा की गुणवत्ता"],["accessibility","सुलभता और समावेशी डिज़ाइन"],["performance","प्रदर्शन और लोड होने की गति"],["security","सुरक्षा और गोपनीयता"],["documentation","दस्तावेज़ और मार्गदर्शिका"],["research-quality","वैज्ञानिक कठोरता और स्रोतों की पहचान"],["reliability","विश्वसनीयता और डेटा अखंडता"],["usability","इंटरफ़ेस की स्पष्टता और उपयोग में आसानी"],["new-feature","उपयोगी नई सुविधा"],["compatibility","ब्राउज़र और उपकरण संगतता"],["other","अन्य उपयोगी सुधार"]]},
    id:{button:"Laporkan",title:"Usulkan peningkatan proyek",intro:"Pilih peningkatan atau koreksi yang bermanfaat. Laporan akan masuk antrean peninjauan; tidak ada perubahan yang diterapkan secara otomatis.",category:"Bidang peningkatan",titleLabel:"Judul singkat",detail:"Apa yang perlu ditingkatkan?",send:"Kirim laporan",cancel:"Batal",sending:"Mengirim…",success:"Terima kasih. Saran Anda telah ditambahkan ke antrean peninjauan.",unavailable:"Pengiriman laporan belum dikonfigurasi. Silakan coba lagi nanti.",error:"Laporan tidak dapat dikirim. Silakan coba lagi.",placeholder:"Jelaskan peningkatan dan, jika memungkinkan, hasil yang diharapkan.",options:[["bug","Bug atau masalah tampilan"],["translation","Terjemahan dan kualitas bahasa"],["accessibility","Aksesibilitas dan desain inklusif"],["performance","Kinerja dan kecepatan pemuatan"],["security","Keamanan dan privasi"],["documentation","Dokumentasi dan panduan"],["research-quality","Ketelitian ilmiah dan keterlacakan sumber"],["reliability","Keandalan dan integritas data"],["usability","Kejelasan dan kemudahan penggunaan"],["new-feature","Fitur baru yang bermanfaat"],["compatibility","Kompatibilitas browser dan perangkat"],["other","Peningkatan bermanfaat lainnya"]]},
    tr:{button:"Bildir",title:"Proje iyileştirmesi önerin",intro:"Yararlı bir iyileştirme veya düzeltme seçin. Bildirimler inceleme kuyruğuna eklenir; hiçbir değişiklik otomatik olarak uygulanmaz.",category:"İyileştirme alanı",titleLabel:"Kısa başlık",detail:"Neler iyileştirilmeli?",send:"Bildirimi gönder",cancel:"İptal",sending:"Gönderiliyor…",success:"Teşekkürler. Öneriniz proje inceleme kuyruğuna eklendi.",unavailable:"Bildirim gönderimi henüz yapılandırılmadı. Lütfen daha sonra tekrar deneyin.",error:"Bildirim gönderilemedi. Lütfen tekrar deneyin.",placeholder:"İyileştirmeyi ve mümkünse beklenen sonucu açıklayın.",options:[["bug","Hata veya görüntüleme sorunu"],["translation","Çeviri ve dil kalitesi"],["accessibility","Erişilebilirlik ve kapsayıcı tasarım"],["performance","Performans ve yükleme hızı"],["security","Güvenlik ve gizlilik"],["documentation","Belgeler ve kılavuzlar"],["research-quality","Bilimsel titizlik ve kaynak izlenebilirliği"],["reliability","Güvenilirlik ve veri bütünlüğü"],["usability","Arayüzün açıklığı ve kullanım kolaylığı"],["new-feature","Yararlı yeni özellik"],["compatibility","Tarayıcı ve cihaz uyumluluğu"],["other","Diğer yararlı iyileştirme"]]},
    pl:{button:"Zgłoś",title:"Zaproponuj ulepszenie projektu",intro:"Wybierz przydatne ulepszenie lub poprawkę. Zgłoszenia trafiają do kolejki przeglądu; zmiany nie są wprowadzane automatycznie.",category:"Obszar ulepszenia",titleLabel:"Krótki tytuł",detail:"Co należy poprawić?",send:"Wyślij zgłoszenie",cancel:"Anuluj",sending:"Wysyłanie…",success:"Dziękujemy. Twoja propozycja została dodana do kolejki przeglądu.",unavailable:"Wysyłanie zgłoszeń nie jest jeszcze skonfigurowane. Spróbuj ponownie później.",error:"Nie udało się wysłać zgłoszenia. Spróbuj ponownie.",placeholder:"Opisz ulepszenie i, jeśli to możliwe, oczekiwany rezultat.",options:[["bug","Błąd lub problem z wyświetlaniem"],["translation","Tłumaczenie i jakość językowa"],["accessibility","Dostępność i projektowanie włączające"],["performance","Wydajność i szybkość ładowania"],["security","Bezpieczeństwo i prywatność"],["documentation","Dokumentacja i instrukcje"],["research-quality","Rzetelność naukowa i identyfikowalność źródeł"],["reliability","Niezawodność i integralność danych"],["usability","Przejrzystość i łatwość obsługi"],["new-feature","Przydatna nowa funkcja"],["compatibility","Zgodność z przeglądarkami i urządzeniami"],["other","Inne przydatne ulepszenie"]]},
    bn:{button:"রিপোর্ট করুন",title:"প্রকল্পের উন্নতির প্রস্তাব দিন",intro:"একটি উপযোগী উন্নতি বা সংশোধন বেছে নিন। প্রতিবেদন পর্যালোচনার তালিকায় যাবে; কোনো পরিবর্তন স্বয়ংক্রিয়ভাবে প্রয়োগ হবে না।",category:"উন্নতির ক্ষেত্র",titleLabel:"সংক্ষিপ্ত শিরোনাম",detail:"কী উন্নত করা উচিত?",send:"প্রতিবেদন পাঠান",cancel:"বাতিল",sending:"পাঠানো হচ্ছে…",success:"ধন্যবাদ। আপনার প্রস্তাব প্রকল্পের পর্যালোচনা তালিকায় যোগ করা হয়েছে।",unavailable:"প্রতিবেদন পাঠানোর ব্যবস্থা এখনও কনফিগার করা হয়নি। পরে আবার চেষ্টা করুন।",error:"প্রতিবেদন পাঠানো যায়নি। আবার চেষ্টা করুন।",placeholder:"উন্নতির বর্ণনা দিন এবং সম্ভব হলে প্রত্যাশিত ফলাফল লিখুন।",options:[["bug","ত্রুটি বা প্রদর্শন সমস্যা"],["translation","অনুবাদ ও ভাষার মান"],["accessibility","অ্যাক্সেসিবিলিটি ও অন্তর্ভুক্তিমূলক নকশা"],["performance","কর্মক্ষমতা ও লোডের গতি"],["security","নিরাপত্তা ও গোপনীয়তা"],["documentation","নথিপত্র ও নির্দেশিকা"],["research-quality","বৈজ্ঞানিক কঠোরতা ও উৎসের অনুসরণযোগ্যতা"],["reliability","নির্ভরযোগ্যতা ও তথ্যের অখণ্ডতা"],["usability","ইন্টারফেসের স্বচ্ছতা ও ব্যবহারের সহজতা"],["new-feature","উপযোগী নতুন বৈশিষ্ট্য"],["compatibility","ব্রাউজার ও ডিভাইসের সামঞ্জস্য"],["other","অন্য উপযোগী উন্নতি"]]},
    sw:{button:"Ripoti",title:"Pendekeza uboreshaji wa mradi",intro:"Chagua uboreshaji au marekebisho yenye manufaa. Ripoti zitaongezwa kwenye foleni ya ukaguzi; hakuna mabadiliko yatakayotekelezwa kiotomatiki.",category:"Eneo la uboreshaji",titleLabel:"Kichwa kifupi",detail:"Ni nini kinapaswa kuboreshwa?",send:"Tuma ripoti",cancel:"Ghairi",sending:"Inatuma…",success:"Asante. Pendekezo lako limeongezwa kwenye foleni ya ukaguzi wa mradi.",unavailable:"Uwasilishaji wa ripoti bado haujasanidiwa. Jaribu tena baadaye.",error:"Ripoti haikuweza kutumwa. Tafadhali jaribu tena.",placeholder:"Eleza uboreshaji na, ikiwezekana, matokeo yanayotarajiwa.",options:[["bug","Hitilafu au tatizo la mwonekano"],["translation","Tafsiri na ubora wa lugha"],["accessibility","Ufikivu na usanifu jumuishi"],["performance","Utendaji na kasi ya kupakia"],["security","Usalama na faragha"],["documentation","Nyaraka na miongozo"],["research-quality","Umakini wa kisayansi na ufuatiliaji wa vyanzo"],["reliability","Uaminifu na uadilifu wa data"],["usability","Uwazi na urahisi wa matumizi"],["new-feature","Kipengele kipya chenye manufaa"],["compatibility","Ulinganifu wa vivinjari na vifaa"],["other","Uboreshaji mwingine wenye manufaa"]]},
    vi:{button:"Báo cáo",title:"Đề xuất cải tiến dự án",intro:"Chọn một cải tiến hữu ích hoặc một lỗi cần sửa. Báo cáo sẽ được đưa vào hàng đợi xem xét; không có thay đổi nào được tự động áp dụng.",category:"Lĩnh vực cần cải tiến",titleLabel:"Tiêu đề ngắn",detail:"Điều gì cần được cải thiện?",send:"Gửi báo cáo",cancel:"Hủy",sending:"Đang gửi…",success:"Cảm ơn bạn. Đề xuất đã được thêm vào hàng đợi xem xét của dự án.",unavailable:"Chức năng gửi báo cáo chưa được cấu hình. Vui lòng thử lại sau.",error:"Không thể gửi báo cáo. Vui lòng thử lại.",placeholder:"Mô tả cải tiến và kết quả mong đợi nếu có thể.",options:[["bug","Lỗi hoặc vấn đề hiển thị"],["translation","Bản dịch và chất lượng ngôn ngữ"],["accessibility","Khả năng tiếp cận và thiết kế toàn diện"],["performance","Hiệu suất và tốc độ tải"],["security","Bảo mật và quyền riêng tư"],["documentation","Tài liệu và hướng dẫn"],["research-quality","Tính chặt chẽ khoa học và khả năng truy xuất nguồn"],["reliability","Độ tin cậy và tính toàn vẹn dữ liệu"],["usability","Độ rõ ràng và dễ sử dụng"],["new-feature","Tính năng mới hữu ích"],["compatibility","Khả năng tương thích trình duyệt và thiết bị"],["other","Cải tiến hữu ích khác"]]},
    fa:{button:"گزارش",title:"پیشنهاد بهبود پروژه",intro:"یک بهبود یا اصلاح مفید انتخاب کنید. گزارش‌ها در صف بررسی قرار می‌گیرند و هیچ تغییری به‌صورت خودکار اعمال نمی‌شود.",category:"حوزهٔ بهبود",titleLabel:"عنوان کوتاه",detail:"چه چیزی باید بهتر شود؟",send:"ارسال گزارش",cancel:"لغو",sending:"در حال ارسال…",success:"سپاسگزاریم. پیشنهاد شما به صف بررسی پروژه افزوده شد.",unavailable:"ارسال گزارش هنوز پیکربندی نشده است. بعداً دوباره تلاش کنید.",error:"ارسال گزارش انجام نشد. دوباره تلاش کنید.",placeholder:"بهبود موردنظر و در صورت امکان نتیجهٔ مورد انتظار را شرح دهید.",options:[["bug","اشکال یا مشکل نمایش"],["translation","ترجمه و کیفیت زبانی"],["accessibility","دسترس‌پذیری و طراحی فراگیر"],["performance","کارایی و سرعت بارگذاری"],["security","امنیت و حریم خصوصی"],["documentation","مستندات و راهنماها"],["research-quality","دقت علمی و قابلیت ردیابی منابع"],["reliability","قابلیت اطمینان و یکپارچگی داده‌ها"],["usability","شفافیت و سهولت استفاده"],["new-feature","قابلیت جدید و مفید"],["compatibility","سازگاری مرورگر و دستگاه"],["other","بهبود مفید دیگر"]]},
    ur:{button:"رپورٹ کریں",title:"منصوبے میں بہتری تجویز کریں",intro:"کوئی مفید بہتری یا اصلاح منتخب کریں۔ رپورٹس جائزے کی قطار میں شامل ہوں گی؛ کوئی تبدیلی خودکار طور پر نافذ نہیں ہوگی۔",category:"بہتری کا شعبہ",titleLabel:"مختصر عنوان",detail:"کس چیز کو بہتر بنایا جانا چاہیے؟",send:"رپورٹ بھیجیں",cancel:"منسوخ کریں",sending:"بھیجا جا رہا ہے…",success:"شکریہ۔ آپ کی تجویز منصوبے کی جائزہ فہرست میں شامل کر دی گئی ہے۔",unavailable:"رپورٹ بھیجنے کی سہولت ابھی ترتیب نہیں دی گئی۔ بعد میں دوبارہ کوشش کریں۔",error:"رپورٹ نہیں بھیجی جا سکی۔ دوبارہ کوشش کریں۔",placeholder:"بہتری کی وضاحت کریں اور ممکن ہو تو متوقع نتیجہ بھی بتائیں۔",options:[["bug","خرابی یا ڈسپلے کا مسئلہ"],["translation","ترجمہ اور زبان کا معیار"],["accessibility","رسائی اور جامع ڈیزائن"],["performance","کارکردگی اور لوڈ ہونے کی رفتار"],["security","سیکیورٹی اور رازداری"],["documentation","دستاویزات اور رہنما ہدایات"],["research-quality","سائنسی معیار اور ماخذ کی سراغ رسانی"],["reliability","اعتماد اور ڈیٹا کی سالمیت"],["usability","انٹرفیس کی وضاحت اور آسان استعمال"],["new-feature","نئی مفید سہولت"],["compatibility","براؤزر اور آلات کی مطابقت"],["other","دیگر مفید بہتری"]]},
    ta:{button:"புகாரளிக்கவும்",title:"திட்ட மேம்பாட்டைப் பரிந்துரைக்கவும்",intro:"பயனுள்ள மேம்பாடு அல்லது திருத்தத்தைத் தேர்ந்தெடுக்கவும். அறிக்கைகள் மதிப்பாய்வுப் பட்டியலில் சேர்க்கப்படும்; மாற்றங்கள் தானாகச் செயல்படுத்தப்படாது.",category:"மேம்பாட்டுப் பகுதி",titleLabel:"சுருக்கமான தலைப்பு",detail:"எதை மேம்படுத்த வேண்டும்?",send:"அறிக்கையை அனுப்பு",cancel:"ரத்து செய்",sending:"அனுப்பப்படுகிறது…",success:"நன்றி. உங்கள் பரிந்துரை திட்ட மதிப்பாய்வுப் பட்டியலில் சேர்க்கப்பட்டது.",unavailable:"அறிக்கை அனுப்பும் வசதி இன்னும் அமைக்கப்படவில்லை. பின்னர் மீண்டும் முயற்சிக்கவும்.",error:"அறிக்கையை அனுப்ப முடியவில்லை. மீண்டும் முயற்சிக்கவும்.",placeholder:"மேம்பாட்டையும் முடிந்தால் எதிர்பார்க்கப்படும் விளைவையும் விவரிக்கவும்.",options:[["bug","பிழை அல்லது காட்சி சிக்கல்"],["translation","மொழிபெயர்ப்பு மற்றும் மொழித் தரம்"],["accessibility","அணுகல்தன்மை மற்றும் அனைவரையும் உள்ளடக்கும் வடிவமைப்பு"],["performance","செயல்திறன் மற்றும் ஏற்ற வேகம்"],["security","பாதுகாப்பு மற்றும் தனியுரிமை"],["documentation","ஆவணங்கள் மற்றும் வழிகாட்டிகள்"],["research-quality","அறிவியல் துல்லியம் மற்றும் மூலத் தடமறிதல்"],["reliability","நம்பகத்தன்மை மற்றும் தரவு ஒருமைப்பாடு"],["usability","இடைமுகத் தெளிவு மற்றும் பயன்பாட்டு எளிமை"],["new-feature","பயனுள்ள புதிய அம்சம்"],["compatibility","உலாவி மற்றும் சாதன இணக்கத்தன்மை"],["other","வேறு பயனுள்ள மேம்பாடு"]]},
    te:{button:"నివేదించండి",title:"ప్రాజెక్ట్ మెరుగుదలను సూచించండి",intro:"ఉపయోగకరమైన మెరుగుదల లేదా సవరణను ఎంచుకోండి. నివేదికలు సమీక్ష క్యూలో చేరతాయి; మార్పులు స్వయంచాలకంగా అమలు కావు.",category:"మెరుగుదల విభాగం",titleLabel:"చిన్న శీర్షిక",detail:"ఏది మెరుగుపరచాలి?",send:"నివేదిక పంపండి",cancel:"రద్దు చేయండి",sending:"పంపుతోంది…",success:"ధన్యవాదాలు. మీ సూచన ప్రాజెక్ట్ సమీక్ష క్యూలో చేర్చబడింది.",unavailable:"నివేదిక సమర్పణ ఇంకా కాన్ఫిగర్ కాలేదు. తర్వాత మళ్లీ ప్రయత్నించండి.",error:"నివేదికను పంపలేకపోయాం. మళ్లీ ప్రయత్నించండి.",placeholder:"మెరుగుదలను, సాధ్యమైతే ఆశించిన ఫలితాన్ని వివరించండి.",options:[["bug","లోపం లేదా ప్రదర్శన సమస్య"],["translation","అనువాదం మరియు భాషా నాణ్యత"],["accessibility","ప్రాప్యత మరియు సమగ్ర రూపకల్పన"],["performance","పనితీరు మరియు లోడింగ్ వేగం"],["security","భద్రత మరియు గోప్యత"],["documentation","పత్రాలు మరియు మార్గదర్శకాలు"],["research-quality","శాస్త్రీయ కట్టుదిట్టత మరియు మూలాల అనుసరణ"],["reliability","విశ్వసనీయత మరియు డేటా సమగ్రత"],["usability","ఇంటర్‌ఫేస్ స్పష్టత మరియు వాడుక సౌలభ్యం"],["new-feature","ఉపయోగకరమైన కొత్త ఫీచర్"],["compatibility","బ్రౌజర్ మరియు పరికర అనుకూలత"],["other","ఇతర ఉపయోగకరమైన మెరుగుదల"]]}
  };

  const actionLabels = {
    en:{view:"View my improvements",close:"Close",empty:"No reports have been submitted from this browser yet.",history:"Your submitted improvements"},
    fr:{view:"Voir mes améliorations",close:"Fermer",empty:"Aucun signalement n’a encore été envoyé depuis ce navigateur.",history:"Vos améliorations signalées"},
    es:{view:"Ver mis mejoras",close:"Cerrar",empty:"Todavía no se han enviado informes desde este navegador.",history:"Mis mejoras enviadas"},
    de:{view:"Meine Verbesserungen ansehen",close:"Schließen",empty:"Über diesen Browser wurden noch keine Meldungen gesendet.",history:"Meine eingereichten Verbesserungen"},
    it:{view:"Visualizza i miei miglioramenti",close:"Chiudi",empty:"Da questo browser non è ancora stata inviata alcuna segnalazione.",history:"I miei miglioramenti inviati"},
    pt:{view:"Ver minhas melhorias",close:"Fechar",empty:"Nenhum relato foi enviado por este navegador ainda.",history:"Minhas melhorias enviadas"},
    nl:{view:"Mijn verbeteringen bekijken",close:"Sluiten",empty:"Er zijn nog geen meldingen verzonden vanuit deze browser.",history:"Mijn ingediende verbeteringen"},
    ru:{view:"Мои предложения",close:"Закрыть",empty:"Из этого браузера ещё не отправлялись сообщения.",history:"Мои отправленные предложения"},
    uk:{view:"Переглянути мої покращення",close:"Закрити",empty:"З цього браузера ще не надсилалися повідомлення.",history:"Мої надіслані пропозиції"},
    ar:{view:"عرض تحسيناتي",close:"إغلاق",empty:"لم يتم إرسال أي بلاغ من هذا المتصفح بعد.",history:"التحسينات التي أرسلتها"},
    he:{view:"הצגת השיפורים שלי",close:"סגירה",empty:"עדיין לא נשלחו דיווחים מדפדפן זה.",history:"השיפורים ששלחתי"},
    ja:{view:"自分の改善提案を見る",close:"閉じる",empty:"このブラウザーからの報告はまだありません。",history:"送信した改善提案"},
    ko:{view:"내 개선 제안 보기",close:"닫기",empty:"이 브라우저에서 제출한 신고가 아직 없습니다.",history:"내가 제출한 개선 제안"},
    zh:{view:"查看我的改进",close:"关闭",empty:"尚未通过此浏览器提交报告。",history:"我提交的改进建议"},
    hi:{view:"मेरे सुधार देखें",close:"बंद करें",empty:"इस ब्राउज़र से अभी तक कोई रिपोर्ट नहीं भेजी गई है।",history:"मेरे भेजे गए सुधार"},
    id:{view:"Lihat peningkatan saya",close:"Tutup",empty:"Belum ada laporan yang dikirim dari browser ini.",history:"Peningkatan yang saya kirim"},
    tr:{view:"İyileştirmelerimi gör",close:"Kapat",empty:"Bu tarayıcıdan henüz bildirim gönderilmedi.",history:"Gönderdiğim iyileştirmeler"},
    pl:{view:"Zobacz moje ulepszenia",close:"Zamknij",empty:"Z tej przeglądarki nie wysłano jeszcze żadnego zgłoszenia.",history:"Wysłane przeze mnie ulepszenia"},
    bn:{view:"আমার উন্নতিগুলো দেখুন",close:"বন্ধ করুন",empty:"এই ব্রাউজার থেকে এখনও কোনো প্রতিবেদন পাঠানো হয়নি।",history:"আমার পাঠানো উন্নতিগুলো"},
    sw:{view:"Tazama maboresho yangu",close:"Funga",empty:"Hakuna ripoti iliyotumwa kutoka kwenye kivinjari hiki bado.",history:"Maboresho niliyotuma"},
    vi:{view:"Xem cải tiến của tôi",close:"Đóng",empty:"Chưa có báo cáo nào được gửi từ trình duyệt này.",history:"Các cải tiến tôi đã gửi"},
    fa:{view:"مشاهدهٔ بهبودهای من",close:"بستن",empty:"هنوز گزارشی از این مرورگر ارسال نشده است.",history:"بهبودهای ارسال‌شدهٔ من"},
    ur:{view:"میری تجاویز دیکھیں",close:"بند کریں",empty:"اس براؤزر سے ابھی تک کوئی رپورٹ نہیں بھیجی گئی۔",history:"میری بھیجی گئی تجاویز"},
    ta:{view:"எனது மேம்பாடுகளைக் காண்க",close:"மூடு",empty:"இந்த உலாவியில் இருந்து இன்னும் அறிக்கை எதுவும் அனுப்பப்படவில்லை.",history:"நான் அனுப்பிய மேம்பாடுகள்"},
    te:{view:"నా మెరుగుదలలను చూడండి",close:"మూసివేయండి",empty:"ఈ బ్రౌజర్ నుండి ఇంకా నివేదికలు పంపలేదు.",history:"నేను పంపిన మెరుగుదలలు"}
  };
  const reportStatusCopy = {
    en:{received:"Received · awaiting review",review:"Needs human review",proposed:"Improvement proposed",integrated:"Integrated into the project",closed:"Closed · not integrated",unavailable:"Live status is temporarily unavailable",issue:"Report",proposal:"Proposed change"},
    fr:{received:"Reçu · en attente d’examen",review:"À examiner par l’équipe",proposed:"Amélioration proposée",integrated:"Intégrée au projet",closed:"Clôturé · non intégré",unavailable:"Statut en direct temporairement indisponible",issue:"Signalement",proposal:"Modification proposée"},
    es:{received:"Recibido · pendiente de revisión",review:"Requiere revisión humana",proposed:"Mejora propuesta",integrated:"Integrada en el proyecto",closed:"Cerrado · no integrado",unavailable:"Estado en directo no disponible temporalmente",issue:"Informe",proposal:"Cambio propuesto"},
    de:{received:"Eingegangen · wartet auf Prüfung",review:"Menschliche Prüfung erforderlich",proposed:"Verbesserung vorgeschlagen",integrated:"In das Projekt integriert",closed:"Geschlossen · nicht integriert",unavailable:"Live-Status vorübergehend nicht verfügbar",issue:"Meldung",proposal:"Vorgeschlagene Änderung"},
    it:{received:"Ricevuta · in attesa di revisione",review:"Richiede revisione umana",proposed:"Miglioramento proposto",integrated:"Integrato nel progetto",closed:"Chiuso · non integrato",unavailable:"Stato in tempo reale temporaneamente non disponibile",issue:"Segnalazione",proposal:"Modifica proposta"},
    pt:{received:"Recebido · aguardando análise",review:"Requer análise humana",proposed:"Melhoria proposta",integrated:"Integrada ao projeto",closed:"Encerrado · não integrado",unavailable:"Estado ao vivo temporariamente indisponível",issue:"Relato",proposal:"Alteração proposta"},
    nl:{received:"Ontvangen · wacht op beoordeling",review:"Menselijke beoordeling nodig",proposed:"Verbetering voorgesteld",integrated:"Opgenomen in het project",closed:"Gesloten · niet opgenomen",unavailable:"Live status tijdelijk niet beschikbaar",issue:"Melding",proposal:"Voorgestelde wijziging"},
    ru:{received:"Получено · ожидает проверки",review:"Требуется проверка человеком",proposed:"Предложено улучшение",integrated:"Включено в проект",closed:"Закрыто · не включено",unavailable:"Текущий статус временно недоступен",issue:"Сообщение",proposal:"Предлагаемое изменение"},
    uk:{received:"Отримано · очікує перевірки",review:"Потрібна перевірка людиною",proposed:"Запропоновано покращення",integrated:"Додано до проєкту",closed:"Закрито · не додано",unavailable:"Поточний статус тимчасово недоступний",issue:"Повідомлення",proposal:"Запропонована зміна"},
    ar:{received:"تم الاستلام · بانتظار المراجعة",review:"يتطلب مراجعة بشرية",proposed:"تم اقتراح تحسين",integrated:"تم دمجه في المشروع",closed:"مغلق · لم يتم الدمج",unavailable:"الحالة المباشرة غير متاحة مؤقتًا",issue:"البلاغ",proposal:"التغيير المقترح"},
    he:{received:"התקבל · ממתין לבדיקה",review:"נדרשת בדיקה אנושית",proposed:"הוצע שיפור",integrated:"שולב בפרויקט",closed:"נסגר · לא שולב",unavailable:"הסטטוס החי אינו זמין זמנית",issue:"דיווח",proposal:"השינוי המוצע"},
    ja:{received:"受付済み · 審査待ち",review:"担当者による確認が必要",proposed:"改善案を提案済み",integrated:"プロジェクトに統合済み",closed:"終了 · 未統合",unavailable:"現在の状態を一時的に取得できません",issue:"報告",proposal:"提案された変更"},
    ko:{received:"접수됨 · 검토 대기",review:"담당자 검토 필요",proposed:"개선안 제안됨",integrated:"프로젝트에 반영됨",closed:"종료 · 미반영",unavailable:"실시간 상태를 일시적으로 확인할 수 없습니다",issue:"신고",proposal:"제안된 변경"},
    zh:{received:"已收到 · 等待审核",review:"需要人工审核",proposed:"已提出改进方案",integrated:"已纳入项目",closed:"已关闭 · 未纳入",unavailable:"暂时无法获取实时状态",issue:"报告",proposal:"拟议更改"},
    hi:{received:"प्राप्त · समीक्षा की प्रतीक्षा",review:"मानवीय समीक्षा आवश्यक",proposed:"सुधार प्रस्तावित",integrated:"परियोजना में शामिल",closed:"बंद · शामिल नहीं",unavailable:"लाइव स्थिति अस्थायी रूप से उपलब्ध नहीं",issue:"रिपोर्ट",proposal:"प्रस्तावित बदलाव"},
    id:{received:"Diterima · menunggu peninjauan",review:"Perlu tinjauan manusia",proposed:"Perbaikan diusulkan",integrated:"Diintegrasikan ke proyek",closed:"Ditutup · tidak diintegrasikan",unavailable:"Status langsung sementara tidak tersedia",issue:"Laporan",proposal:"Perubahan yang diusulkan"},
    tr:{received:"Alındı · inceleme bekliyor",review:"İnsan incelemesi gerekiyor",proposed:"İyileştirme önerildi",integrated:"Projeye eklendi",closed:"Kapatıldı · eklenmedi",unavailable:"Canlı durum geçici olarak kullanılamıyor",issue:"Bildirim",proposal:"Önerilen değişiklik"},
    pl:{received:"Odebrano · oczekuje na przegląd",review:"Wymaga weryfikacji przez człowieka",proposed:"Zaproponowano ulepszenie",integrated:"Zintegrowano z projektem",closed:"Zamknięto · nie zintegrowano",unavailable:"Status na żywo jest chwilowo niedostępny",issue:"Zgłoszenie",proposal:"Proponowana zmiana"},
    bn:{received:"গৃহীত · পর্যালোচনার অপেক্ষায়",review:"মানবীয় পর্যালোচনা প্রয়োজন",proposed:"উন্নয়নের প্রস্তাব দেওয়া হয়েছে",integrated:"প্রকল্পে যুক্ত হয়েছে",closed:"বন্ধ · যুক্ত হয়নি",unavailable:"লাইভ অবস্থা সাময়িকভাবে অনুপলব্ধ",issue:"প্রতিবেদন",proposal:"প্রস্তাবিত পরিবর্তন"},
    sw:{received:"Imepokelewa · inasubiri ukaguzi",review:"Ukaguzi wa binadamu unahitajika",proposed:"Uboreshaji umependekezwa",integrated:"Imejumuishwa kwenye mradi",closed:"Imefungwa · haikujumuishwa",unavailable:"Hali ya moja kwa moja haipatikani kwa muda",issue:"Ripoti",proposal:"Mabadiliko yaliyopendekezwa"},
    vi:{received:"Đã nhận · đang chờ xem xét",review:"Cần người kiểm duyệt",proposed:"Đã đề xuất cải tiến",integrated:"Đã tích hợp vào dự án",closed:"Đã đóng · chưa tích hợp",unavailable:"Trạng thái trực tiếp tạm thời không khả dụng",issue:"Báo cáo",proposal:"Thay đổi được đề xuất"},
    fa:{received:"دریافت شد · در انتظار بررسی",review:"نیازمند بررسی انسانی",proposed:"بهبود پیشنهاد شد",integrated:"در پروژه ادغام شد",closed:"بسته شد · ادغام نشد",unavailable:"وضعیت زنده موقتاً در دسترس نیست",issue:"گزارش",proposal:"تغییر پیشنهادی"},
    ur:{received:"موصول · جائزے کا منتظر",review:"انسانی جائزہ درکار ہے",proposed:"بہتری تجویز کی گئی",integrated:"منصوبے میں شامل",closed:"بند · شامل نہیں کیا گیا",unavailable:"براہِ راست حالت عارضی طور پر دستیاب نہیں",issue:"رپورٹ",proposal:"تجویز کردہ تبدیلی"},
    ta:{received:"பெறப்பட்டது · மதிப்பாய்வுக்காகக் காத்திருக்கிறது",review:"மனித மதிப்பாய்வு தேவை",proposed:"மேம்பாடு முன்மொழியப்பட்டது",integrated:"திட்டத்தில் இணைக்கப்பட்டது",closed:"மூடப்பட்டது · இணைக்கப்படவில்லை",unavailable:"நேரடி நிலை தற்காலிகமாக கிடைக்கவில்லை",issue:"அறிக்கை",proposal:"முன்மொழியப்பட்ட மாற்றம்"},
    te:{received:"అందింది · సమీక్ష కోసం వేచి ఉంది",review:"మానవ సమీక్ష అవసరం",proposed:"మెరుగుదల ప్రతిపాదించబడింది",integrated:"ప్రాజెక్ట్‌లో చేర్చబడింది",closed:"మూసివేయబడింది · చేర్చలేదు",unavailable:"ప్రస్తుత స్థితి తాత్కాలికంగా అందుబాటులో లేదు",issue:"నివేదిక",proposal:"ప్రతిపాదిత మార్పు"}
  };

  const reportStorageKey = "ssswet:submitted-improvements:v1";
  function readSubmittedReports() {
    try { const value=JSON.parse(localStorage.getItem(reportStorageKey)||"[]"); return Array.isArray(value)?value:[]; }
    catch (_) { return []; }
  }
  function saveSubmittedReport(report) {
    const reports=readSubmittedReports();
    reports.unshift(report);
    try { localStorage.setItem(reportStorageKey,JSON.stringify(reports.slice(0,100))); } catch (_) {}
  }

  const language = () => String(document.documentElement.lang || document.getElementById("language")?.value || "en").toLowerCase().split("-")[0];
  const text = () => copy[language()] || copy.en;
  const style = document.createElement("style");
  style.textContent = `
    .report-project-button{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:11px 18px;border:1px solid rgba(255,92,92,.55);border-radius:14px;color:#fff;background:linear-gradient(115deg,#9f242b,#65171d);font-family:inherit;font-size:12px;font-weight:650;cursor:pointer;box-shadow:0 8px 28px rgba(0,0,0,.24)}
    .report-project-button:hover{background:linear-gradient(115deg,#bd3038,#7c1d25);transform:translateY(-1px)}
    .repair-project-slot{display:flex;justify-content:center;align-items:center;gap:10px;flex-wrap:wrap}
    .ssswet-report-dialog{width:min(560px,calc(100% - 28px));max-height:85vh;overflow:auto;border:1px solid rgba(255,255,255,.14);border-radius:18px;background:#101116;color:#f5f5f7;padding:24px;box-shadow:0 24px 90px #000a}
    .ssswet-report-dialog::backdrop{background:#000b;backdrop-filter:blur(5px)}
    .ssswet-report-dialog h2{margin:0 0 8px}.ssswet-report-dialog p{color:#b8bac4;line-height:1.55}
    .ssswet-report-dialog label{display:grid;gap:7px;margin:15px 0;font-size:13px;color:#ddd}
    .ssswet-report-dialog input,.ssswet-report-dialog select,.ssswet-report-dialog textarea{width:100%;box-sizing:border-box;border:1px solid #383a45;border-radius:9px;background:#191b22;color:#fff;padding:11px;font:inherit}
    .ssswet-report-dialog textarea{min-height:120px;resize:vertical}
    .ssswet-report-actions{display:flex;justify-content:flex-end;gap:9px;flex-wrap:wrap;margin-top:18px}
    .ssswet-report-actions button{border:1px solid #555;border-radius:9px;padding:10px 15px;background:#242630;color:white;cursor:pointer}
    .ssswet-report-actions button[type=submit]{background:#a8242d;border-color:#a8242d}
    .ssswet-report-status{min-height:1.4em;font-size:13px}
    .ssswet-report-history{margin:16px 0}.ssswet-report-history-list{padding-inline-start:22px;display:grid;gap:10px}
    .ssswet-report-history-list a{color:#f0a1a5;text-decoration:underline}.ssswet-report-history-list li{overflow-wrap:anywhere}.ssswet-report-live-status{margin:5px 0;color:#d7d9e2;font-size:12px}.ssswet-report-history-links{margin:4px 0;font-size:12px}
    [dir="rtl"] .ssswet-report-dialog{text-align:right}
  `;
  document.head.append(style);

  function init(){
    if(document.getElementById("ssswet-report-button")) return;
    const slot=document.querySelector(".repair-project-slot");
    if(!slot) return;
    const button=document.createElement("button");
    button.type="button";button.id="ssswet-report-button";button.className="report-project-button";
    const dialog=document.createElement("dialog");dialog.className="ssswet-report-dialog";dialog.id="ssswet-report-dialog";
    const form=document.createElement("form");
    const heading=document.createElement("h2"),intro=document.createElement("p");
    const categoryLabel=document.createElement("label"),category=document.createElement("select");
    const titleLabel=document.createElement("label"),title=document.createElement("input");
    const detailLabel=document.createElement("label"),detail=document.createElement("textarea");
    const status=document.createElement("p");status.className="ssswet-report-status";status.setAttribute("role","status");status.setAttribute("aria-live","polite");
    const history=document.createElement("section");history.className="ssswet-report-history";history.hidden=true;
    const historyHeading=document.createElement("h3");const historyList=document.createElement("ul");historyList.className="ssswet-report-history-list";
    history.append(historyHeading,historyList);
    const actions=document.createElement("div");actions.className="ssswet-report-actions";
    const cancel=document.createElement("button");cancel.type="button";
    const submit=document.createElement("button");submit.type="submit";
    title.maxLength=160;title.required=true;detail.maxLength=3000;detail.required=true;
    category.name="category";title.name="title";detail.name="description";
    categoryLabel.append(document.createTextNode(""),category);
    titleLabel.append(document.createTextNode(""),title);
    detailLabel.append(document.createTextNode(""),detail);
    actions.append(cancel,submit);form.append(heading,intro,categoryLabel,titleLabel,detailLabel,status,history,actions);dialog.append(form);
    slot.append(button,dialog);

    function localize(){
      const t=text();
      button.textContent=t.button;button.setAttribute("aria-label",t.button);
      heading.textContent=t.title;intro.textContent=t.intro;
      categoryLabel.firstChild.textContent=t.category;titleLabel.firstChild.textContent=t.titleLabel;
      detailLabel.firstChild.textContent=t.detail;title.placeholder=t.titleLabel;detail.placeholder=t.placeholder;
      const a=actionLabels[language()]||actionLabels.en;
      cancel.textContent=a.close;
      if(submit.dataset.mode==="history") submit.textContent=a.view;
      else submit.textContent=t.send;
      historyHeading.textContent=a.history;
      const previous=category.value;category.replaceChildren();
      t.options.forEach(([value,label])=>{const option=document.createElement("option");option.value=value;option.textContent=label;category.append(option);});
      if(previous)category.value=previous;
      const rtl=["ar","he"].includes(language());dialog.dir=rtl?"rtl":"ltr";
    }

    async function getLiveReportStatus(report) {
      const labels = reportStatusCopy[language()] || reportStatusCopy.en;
      const number = Number(report.issue_number);
      if (!Number.isSafeInteger(number) || number < 1) return {key:"received"};
      const base = "https://api.github.com/repos/gudjencio/SSSWET";
      try {
        const headers = {Accept:"application/vnd.github+json"};
        const [issueResponse, commentsResponse] = await Promise.all([
          fetch(base+"/issues/"+number,{headers}),
          fetch(base+"/issues/"+number+"/comments?per_page=100",{headers})
        ]);
        if (!issueResponse.ok) throw new Error("Issue status unavailable");
        const issue = await issueResponse.json();
        const comments = commentsResponse.ok ? await commentsResponse.json() : [];
        const prMatch = (Array.isArray(comments)?comments:[]).map(comment =>
          String(comment.body||"").match(/https:\/\/github\.com\/gudjencio\/SSSWET\/pull\/(\d+)/i)
        ).find(Boolean);
        if (prMatch) {
          const prResponse = await fetch(base+"/pulls/"+Number(prMatch[1]),{headers});
          if (prResponse.ok) {
            const pr = await prResponse.json();
            if (pr.merged_at || pr.merged) return {key:"integrated",pr_url:pr.html_url};
            if (pr.state === "open") return {key:"proposed",pr_url:pr.html_url};
          }
        }
        const issueLabels = (issue.labels||[]).map(label=>String(label.name||"").toLowerCase());
        if (issueLabels.some(label=>label.includes("human-review")||label.includes("needs-review"))) return {key:"review"};
        if (issue.state === "closed") return {key:"closed"};
        return {key:"received"};
      } catch (_) { return {key:"received",unavailable:true}; }
    }

    async function showHistory(){
      const a=actionLabels[language()]||actionLabels.en;
      const labels=reportStatusCopy[language()]||reportStatusCopy.en;
      historyList.replaceChildren();
      const reports=readSubmittedReports().slice(0,20);
      if(!reports.length){const empty=document.createElement("li");empty.textContent=a.empty;historyList.append(empty);}
      categoryLabel.hidden=true;titleLabel.hidden=true;detailLabel.hidden=true;intro.hidden=true;history.hidden=false;
      submit.dataset.mode="history";submit.type="button";submit.textContent=a.view;
      status.textContent="";
      const rows=reports.map(report=>{
        const item=document.createElement("li");
        const title=document.createElement("strong");title.textContent=report.title+" · "+(report.category||"");
        const state=document.createElement("p");state.textContent=labels.received;state.className="ssswet-report-live-status";
        const links=document.createElement("p");links.className="ssswet-report-history-links";
        if(report.issue_url && /^https:\/\/github\.com\/gudjencio\/SSSWET\/issues\/\d+$/i.test(report.issue_url)){
          const link=document.createElement("a");link.href=report.issue_url;link.target="_blank";link.rel="noopener noreferrer";link.textContent=labels.issue;links.append(link);
        }
        item.append(title,state,links);historyList.append(item);
        return {report,state,links};
      });
      const refresh=async row=>{
        const live=await getLiveReportStatus(row.report);
        row.state.textContent=labels[live.key]||labels.received;
        if(live.unavailable) row.state.textContent+=" · "+labels.unavailable;
        if(live.pr_url && /^https:\/\/github\.com\/gudjencio\/SSSWET\/pull\/\d+$/i.test(live.pr_url)){
          const link=document.createElement("a");link.href=live.pr_url;link.target="_blank";link.rel="noopener noreferrer";link.textContent=labels.proposal;
          if(row.links.childNodes.length) row.links.append(" · ");
          row.links.append(link);
        }
      };
      await Promise.all(rows.map(refresh));
    }
    button.addEventListener("click",()=>{localize();status.textContent="";history.hidden=true;categoryLabel.hidden=false;titleLabel.hidden=false;detailLabel.hidden=false;intro.hidden=false;submit.dataset.mode="";submit.type="submit";submit.textContent=text().send;dialog.showModal();});
    cancel.addEventListener("click",()=>dialog.close());
    submit.addEventListener("click",()=>{if(submit.dataset.mode==="history")showHistory();});
    form.addEventListener("submit",async event=>{
      event.preventDefault();const t=text();submit.disabled=true;submit.textContent=t.sending;status.textContent="";
      try{
        if(typeof window.ssswetApiFetch!=="function") throw new Error("unavailable");
        const response=await window.ssswetApiFetch("/api/project-reports",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({category:category.value,title:title.value.trim(),description:detail.value.trim(),language:language(),page:location.pathname})});
        const result=await response.json();
        if(!response.ok){const error=new Error(result.error||"submission failed");error.status=response.status;throw error;}
        saveSubmittedReport({title:title.value.trim(),category:category.value,issue_url:result.issue_url||"",issue_number:result.issue_number||null,submitted_at:new Date().toISOString()});
        status.textContent=t.success;form.reset();localize();
        categoryLabel.hidden=true;titleLabel.hidden=true;detailLabel.hidden=true;intro.hidden=true;history.hidden=true;
        submit.dataset.mode="history";submit.type="button";submit.textContent=(actionLabels[language()]||actionLabels.en).view;
      }catch(error){status.textContent=error.message==="unavailable"||error.status===503?t.unavailable:t.error;}
      finally{submit.disabled=false;if(submit.dataset.mode!=="history")submit.textContent=text().send;}
    });
    document.getElementById("language")?.addEventListener("change",localize);
    window.addEventListener("ssswet-language-changed",localize);
    localize();
  }
  function waitForRepairSlot(){
    init();
    if(document.getElementById("ssswet-report-button")) return;
    const observer=new MutationObserver(()=>{
      if(document.querySelector(".repair-project-slot")){observer.disconnect();init();}
    });
    observer.observe(document.documentElement,{childList:true,subtree:true});
    window.addEventListener("ssswet-language-changed",init,{once:true});
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",waitForRepairSlot,{once:true});else waitForRepairSlot();
})();