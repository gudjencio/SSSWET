(() => {
  "use strict";
  const EARTH_RADIUS_M = 6371000;
  const MAX_ACCURACY_M = 150;
  const MAX_GAP_MS = 15 * 60 * 1000;
  const MAX_SEGMENT_DISTANCE_M = 5000;
  const MAX_SPEED_MPS = 70;
  const MAX_FIXES = 6;
  const MIN_FIXES = 3;

  const AUDIT_LABELS = {
    en: {
      summary: "GPS audit: {accepted}/{total} usable; {rejected} rejected; {runs} runs; longest {longest}.",
      ready: "Scenario threshold met: at least 3 contiguous eligible fixes.",
      notReady: "Scenario threshold not met: at least 3 contiguous eligible fixes are required.",
      rejected: "Rejected fixes: {items}.",
      breaks: "Track breaks: {items}.",
      clock: "Clock diagnostics: {fallback} wall-clock fallback fixes; {diverged} wall-clock divergence flags.",
      reasons: { missing_coordinates: "missing coordinates", invalid_coordinates: "invalid coordinates", invalid_timestamp: "invalid timestamp", missing_accuracy: "missing accuracy", invalid_accuracy: "invalid accuracy", accuracy_over_limit: "accuracy above 150 m" },
      breakReasons: { rejected_fix: "rejected-fix boundary", clock_basis_change: "clock-source change", non_increasing_time: "non-increasing time", time_gap: "gap over 15 min", distance_jump: "jump over 5 km", speed_limit: "speed over 70 m/s" }
    },
    fr: {
      summary: "Audit GPS : {accepted}/{total} positions exploitables ; {rejected} rejetées ; {runs} segments ; maximum : {longest}.",
      ready: "Seuil atteint : au moins 3 positions admissibles consécutives.",
      notReady: "Seuil non atteint : au moins 3 positions admissibles consécutives sont nécessaires.",
      rejected: "Positions rejetées : {items}.",
      breaks: "Ruptures de trajectoire : {items}.",
      clock: "Horloge : {fallback} relevés en repli système ; {diverged} divergences signalées.",
      reasons: { missing_coordinates: "coordonnées absentes", invalid_coordinates: "coordonnées invalides", invalid_timestamp: "horodatage invalide", missing_accuracy: "précision absente", invalid_accuracy: "précision invalide", accuracy_over_limit: "précision supérieure à 150 m" },
      breakReasons: { rejected_fix: "position rejetée", clock_basis_change: "changement d’horloge", non_increasing_time: "temps non croissant", time_gap: "intervalle supérieur à 15 min", distance_jump: "saut supérieur à 5 km", speed_limit: "vitesse supérieure à 70 m/s" }
    },
    es: {
      summary: "Auditoría GPS: {accepted}/{total} posiciones utilizables; {rejected} rechazadas; {runs} tramos; máximo {longest}.",
      ready: "Umbral alcanzado: al menos 3 posiciones válidas consecutivas.",
      notReady: "Umbral no alcanzado: se requieren al menos 3 posiciones válidas consecutivas.",
      rejected: "Posiciones rechazadas: {items}.",
      breaks: "Cortes de trayectoria: {items}.",
      clock: "Reloj: {fallback} registros con reloj del sistema; {diverged} divergencias detectadas.",
      reasons: { missing_coordinates: "coordenadas ausentes", invalid_coordinates: "coordenadas no válidas", invalid_timestamp: "hora no válida", missing_accuracy: "precisión ausente", invalid_accuracy: "precisión no válida", accuracy_over_limit: "precisión superior a 150 m" },
      breakReasons: { rejected_fix: "posición rechazada", clock_basis_change: "cambio de reloj", non_increasing_time: "tiempo no creciente", time_gap: "intervalo superior a 15 min", distance_jump: "salto superior a 5 km", speed_limit: "velocidad superior a 70 m/s" }
    },
    de: {
      summary: "GPS-Prüfung: {accepted}/{total} nutzbar; {rejected} verworfen; {runs} Abschnitte; längster {longest}.",
      ready: "Schwelle erreicht: mindestens 3 zusammenhängende gültige Messpunkte.",
      notReady: "Schwelle nicht erreicht: mindestens 3 zusammenhängende gültige Messpunkte erforderlich.",
      rejected: "Verworfene Messpunkte: {items}.",
      breaks: "Track-Unterbrechungen: {items}.",
      clock: "Uhr: {fallback} Messpunkte mit Systemzeit; {diverged} Abweichungen erkannt.",
      reasons: { missing_coordinates: "Koordinaten fehlen", invalid_coordinates: "ungültige Koordinaten", invalid_timestamp: "ungültiger Zeitstempel", missing_accuracy: "Genauigkeit fehlt", invalid_accuracy: "ungültige Genauigkeit", accuracy_over_limit: "Genauigkeit über 150 m" },
      breakReasons: { rejected_fix: "verworfenem Messpunkt", clock_basis_change: "Uhrquellenwechsel", non_increasing_time: "nicht steigender Zeit", time_gap: "Lücke über 15 Min.", distance_jump: "Sprung über 5 km", speed_limit: "Geschwindigkeit über 70 m/s" }
    },
    it: {
      summary: "Verifica GPS: {accepted}/{total} posizioni utilizzabili; {rejected} rifiutate; {runs} segmenti; massimo {longest}.",
      ready: "Soglia raggiunta: almeno 3 posizioni valide consecutive.",
      notReady: "Soglia non raggiunta: servono almeno 3 posizioni valide consecutive.",
      rejected: "Posizioni rifiutate: {items}.",
      breaks: "Interruzioni del tracciato: {items}.",
      clock: "Orologio: {fallback} rilevazioni con orologio di sistema; {diverged} divergenze segnalate.",
      reasons: { missing_coordinates: "coordinate mancanti", invalid_coordinates: "coordinate non valide", invalid_timestamp: "orario non valido", missing_accuracy: "precisione mancante", invalid_accuracy: "precisione non valida", accuracy_over_limit: "precisione oltre 150 m" },
      breakReasons: { rejected_fix: "posizione rifiutata", clock_basis_change: "cambio della sorgente oraria", non_increasing_time: "tempo non crescente", time_gap: "intervallo oltre 15 min", distance_jump: "salto oltre 5 km", speed_limit: "velocità oltre 70 m/s" }
    },
    pt: {
      summary: "Auditoria GPS: {accepted}/{total} posições utilizáveis; {rejected} rejeitadas; {runs} segmentos; máximo {longest}.",
      ready: "Limite atingido: pelo menos 3 posições válidas consecutivas.",
      notReady: "Limite não atingido: são necessárias pelo menos 3 posições válidas consecutivas.",
      rejected: "Posições rejeitadas: {items}.",
      breaks: "Interrupções do percurso: {items}.",
      clock: "Relógio: {fallback} registos com relógio do sistema; {diverged} divergências assinaladas.",
      reasons: { missing_coordinates: "coordenadas em falta", invalid_coordinates: "coordenadas inválidas", invalid_timestamp: "hora inválida", missing_accuracy: "precisão em falta", invalid_accuracy: "precisão inválida", accuracy_over_limit: "precisão acima de 150 m" },
      breakReasons: { rejected_fix: "posição rejeitada", clock_basis_change: "mudança da origem do relógio", non_increasing_time: "tempo não crescente", time_gap: "intervalo superior a 15 min", distance_jump: "salto superior a 5 km", speed_limit: "velocidade superior a 70 m/s" }
    },
    nl: {
      summary: "GPS-controle: {accepted}/{total} bruikbaar; {rejected} afgewezen; {runs} trajectdelen; langste {longest}.",
      ready: "Drempel bereikt: minstens 3 opeenvolgende geldige metingen.",
      notReady: "Drempel niet bereikt: minstens 3 opeenvolgende geldige metingen zijn vereist.",
      rejected: "Afgewezen metingen: {items}.",
      breaks: "Trajectonderbrekingen: {items}.",
      clock: "Klok: {fallback} metingen met systeemklok; {diverged} afwijkingen gemeld.",
      reasons: { missing_coordinates: "coördinaten ontbreken", invalid_coordinates: "ongeldige coördinaten", invalid_timestamp: "ongeldige tijdstempel", missing_accuracy: "nauwkeurigheid ontbreekt", invalid_accuracy: "ongeldige nauwkeurigheid", accuracy_over_limit: "nauwkeurigheid boven 150 m" },
      breakReasons: { rejected_fix: "afgewezen meting", clock_basis_change: "wisseling van klokbron", non_increasing_time: "niet-oplopende tijd", time_gap: "hiaat langer dan 15 min", distance_jump: "sprong groter dan 5 km", speed_limit: "snelheid boven 70 m/s" }
    },
    ru: {
      summary: "Проверка GPS: {accepted}/{total} пригодны; {rejected} отклонены; участков: {runs}; максимум {longest}.",
      ready: "Порог достигнут: не менее 3 последовательных допустимых точек.",
      notReady: "Порог не достигнут: нужны не менее 3 последовательных допустимых точек.",
      rejected: "Отклонённые точки: {items}.",
      breaks: "Разрывы трека: {items}.",
      clock: "Часы: {fallback} записей по системным часам; расхождений: {diverged}.",
      reasons: { missing_coordinates: "нет координат", invalid_coordinates: "неверные координаты", invalid_timestamp: "неверная отметка времени", missing_accuracy: "нет точности", invalid_accuracy: "неверная точность", accuracy_over_limit: "точность хуже 150 м" },
      breakReasons: { rejected_fix: "отклонённая точка", clock_basis_change: "смена источника времени", non_increasing_time: "время не возрастает", time_gap: "разрыв более 15 мин", distance_jump: "скачок более 5 км", speed_limit: "скорость выше 70 м/с" }
    },
    uk: {
      summary: "Перевірка GPS: {accepted}/{total} придатні; {rejected} відхилено; ділянок: {runs}; максимум {longest}.",
      ready: "Поріг досягнуто: щонайменше 3 послідовні придатні точки.",
      notReady: "Поріг не досягнуто: потрібно щонайменше 3 послідовні придатні точки.",
      rejected: "Відхилені точки: {items}.",
      breaks: "Розриви треку: {items}.",
      clock: "Годинник: {fallback} записів за системним часом; розбіжностей: {diverged}.",
      reasons: { missing_coordinates: "немає координат", invalid_coordinates: "некоректні координати", invalid_timestamp: "некоректний час", missing_accuracy: "немає точності", invalid_accuracy: "некоректна точність", accuracy_over_limit: "точність гірша за 150 м" },
      breakReasons: { rejected_fix: "відхилена точка", clock_basis_change: "зміна джерела часу", non_increasing_time: "час не зростає", time_gap: "розрив понад 15 хв", distance_jump: "стрибок понад 5 км", speed_limit: "швидкість понад 70 м/с" }
    },
    ar: {
      summary: "تدقيق GPS: {accepted}/{total} صالحة؛ {rejected} مرفوضة؛ المقاطع {runs}؛ الأطول {longest}.",
      ready: "تحقق الحد: ثلاث نقاط صالحة متصلة على الأقل.",
      notReady: "لم يتحقق الحد: يلزم ثلاث نقاط صالحة متصلة على الأقل.",
      rejected: "النقاط المرفوضة: {items}.",
      breaks: "انقطاعات المسار: {items}.",
      clock: "الساعة: {fallback} سجلات بساعة النظام؛ حالات اختلاف {diverged}.",
      reasons: { missing_coordinates: "إحداثيات مفقودة", invalid_coordinates: "إحداثيات غير صالحة", invalid_timestamp: "وقت غير صالح", missing_accuracy: "دقة مفقودة", invalid_accuracy: "دقة غير صالحة", accuracy_over_limit: "دقة تتجاوز 150 مترًا" },
      breakReasons: { rejected_fix: "نقطة مرفوضة", clock_basis_change: "تغيير مصدر الساعة", non_increasing_time: "وقت غير متزايد", time_gap: "فجوة تتجاوز 15 دقيقة", distance_jump: "قفزة تتجاوز 5 كم", speed_limit: "سرعة تتجاوز 70 م/ث" }
    },
    he: {
      summary: "בדיקת GPS: {accepted}/{total} תקינות; {rejected} נדחו; מקטעים: {runs}; הארוך ביותר: {longest}.",
      ready: "הסף הושג: לפחות 3 נקודות תקינות רצופות.",
      notReady: "הסף לא הושג: נדרשות לפחות 3 נקודות תקינות רצופות.",
      rejected: "נקודות שנדחו: {items}.",
      breaks: "קטיעות מסלול: {items}.",
      clock: "שעון: {fallback} רשומות לפי שעון המערכת; סטיות שזוהו: {diverged}.",
      reasons: { missing_coordinates: "קואורדינטות חסרות", invalid_coordinates: "קואורדינטות לא תקינות", invalid_timestamp: "חותמת זמן לא תקינה", missing_accuracy: "נתון דיוק חסר", invalid_accuracy: "נתון דיוק לא תקין", accuracy_over_limit: "דיוק מעל 150 מטר" },
      breakReasons: { rejected_fix: "נקודה שנדחתה", clock_basis_change: "שינוי מקור השעון", non_increasing_time: "זמן שאינו עולה", time_gap: "פער מעל 15 דקות", distance_jump: "קפיצה מעל 5 ק״מ", speed_limit: "מהירות מעל 70 מ׳/ש׳" }
    },
    ja: {
      summary: "GPS監査: {total}件中{accepted}件を使用可能、{rejected}件を除外。区間{runs}、最長{longest}件。",
      ready: "条件達成: 有効な連続測位が3件以上あります。",
      notReady: "条件未達: 有効な連続測位が3件以上必要です。",
      rejected: "除外した測位: {items}。",
      breaks: "軌跡の分割: {items}。",
      clock: "時計診断: システム時計を使った測位{fallback}件、時計のずれ{diverged}件。",
      reasons: { missing_coordinates: "座標なし", invalid_coordinates: "座標不正", invalid_timestamp: "時刻不正", missing_accuracy: "精度情報なし", invalid_accuracy: "精度情報不正", accuracy_over_limit: "精度が150 mを超過" },
      breakReasons: { rejected_fix: "除外測位", clock_basis_change: "時計基準の変更", non_increasing_time: "時刻が増加しない", time_gap: "15分超の間隔", distance_jump: "5 km超の移動", speed_limit: "70 m/s超の速度" }
    },
    ko: {
      summary: "GPS 점검: {total}개 중 {accepted}개 사용 가능, {rejected}개 제외; 구간 {runs}개, 최장 {longest}개.",
      ready: "기준 충족: 유효한 연속 위치가 3개 이상입니다.",
      notReady: "기준 미충족: 유효한 연속 위치가 3개 이상 필요합니다.",
      rejected: "제외된 위치: {items}.",
      breaks: "경로 분할: {items}.",
      clock: "시계 진단: 시스템 시계 사용 {fallback}개, 시계 차이 감지 {diverged}개.",
      reasons: { missing_coordinates: "좌표 없음", invalid_coordinates: "잘못된 좌표", invalid_timestamp: "잘못된 시각", missing_accuracy: "정확도 정보 없음", invalid_accuracy: "잘못된 정확도", accuracy_over_limit: "정확도 150 m 초과" },
      breakReasons: { rejected_fix: "제외된 위치", clock_basis_change: "시계 기준 변경", non_increasing_time: "증가하지 않는 시각", time_gap: "15분 초과 간격", distance_jump: "5 km 초과 이동", speed_limit: "70 m/s 초과 속도" }
    },
    zh: {
      summary: "GPS审查：{total}个点中{accepted}个可用，{rejected}个已排除；轨迹段{runs}段，最长{longest}个点。",
      ready: "达到条件：至少有3个连续有效定位点。",
      notReady: "未达到条件：至少需要3个连续有效定位点。",
      rejected: "排除的定位点：{items}。",
      breaks: "轨迹中断：{items}。",
      clock: "时钟诊断：{fallback}个点使用系统时钟；检测到{diverged}次时钟偏差。",
      reasons: { missing_coordinates: "缺少坐标", invalid_coordinates: "坐标无效", invalid_timestamp: "时间戳无效", missing_accuracy: "缺少精度", invalid_accuracy: "精度无效", accuracy_over_limit: "精度超过150米" },
      breakReasons: { rejected_fix: "定位点被排除", clock_basis_change: "时钟来源改变", non_increasing_time: "时间未递增", time_gap: "间隔超过15分钟", distance_jump: "位移超过5公里", speed_limit: "速度超过70米/秒" }
    },
    hi: {
      summary: "GPS जाँच: {total} में से {accepted} उपयोग योग्य; {rejected} अस्वीकृत; खंड {runs}; सबसे लंबा {longest}।",
      ready: "सीमा पूरी: कम से कम 3 लगातार मान्य स्थान उपलब्ध हैं।",
      notReady: "सीमा पूरी नहीं: कम से कम 3 लगातार मान्य स्थान आवश्यक हैं।",
      rejected: "अस्वीकृत स्थान: {items}।",
      breaks: "मार्ग में विराम: {items}।",
      clock: "घड़ी जाँच: {fallback} रिकॉर्ड में सिस्टम घड़ी; घड़ी-विचलन संकेत {diverged}।",
      reasons: { missing_coordinates: "निर्देशांक अनुपलब्ध", invalid_coordinates: "अमान्य निर्देशांक", invalid_timestamp: "अमान्य समय", missing_accuracy: "सटीकता अनुपलब्ध", invalid_accuracy: "अमान्य सटीकता", accuracy_over_limit: "सटीकता 150 मीटर से अधिक" },
      breakReasons: { rejected_fix: "अस्वीकृत स्थान", clock_basis_change: "घड़ी स्रोत बदला", non_increasing_time: "समय नहीं बढ़ा", time_gap: "15 मिनट से बड़ा अंतराल", distance_jump: "5 किमी से बड़ी छलांग", speed_limit: "70 मीटर/सेकंड से अधिक गति" }
    }
  };

  function normalizeLongitude(value) { return ((value + 540) % 360) - 180; }
  function haversine(a, b) {
    const lat1=a.latitude*Math.PI/180,lat2=b.latitude*Math.PI/180;
    const dLat=(b.latitude-a.latitude)*Math.PI/180,dLon=normalizeLongitude(b.longitude-a.longitude)*Math.PI/180;
    const h=Math.sin(dLat/2)**2+Math.cos(lat1)*Math.cos(lat2)*Math.sin(dLon/2)**2;
    return 2*EARTH_RADIUS_M*Math.atan2(Math.sqrt(Math.min(1,h)),Math.sqrt(Math.max(0,1-h)));
  }
  function bearing(a,b) {
    const lat1=a.latitude*Math.PI/180,lat2=b.latitude*Math.PI/180,dLon=normalizeLongitude(b.longitude-a.longitude)*Math.PI/180;
    return Math.atan2(Math.sin(dLon)*Math.cos(lat2),Math.cos(lat1)*Math.sin(lat2)-Math.sin(lat1)*Math.cos(lat2)*Math.cos(dLon));
  }
  function median(values) {
    if(!values.length)return null;
    const sorted=values.slice().sort((a,b)=>a-b),middle=Math.floor(sorted.length/2);
    return sorted.length%2?sorted[middle]:(sorted[middle-1]+sorted[middle])/2;
  }
  function hasFiniteNumber(value) {
    return value!==null&&value!==undefined&&value!==""&&Number.isFinite(Number(value));
  }
  function fixRejectionReason(event) {
    if(!event||typeof event!=="object")return "invalid_coordinates";
    if(event.kind&&event.kind!=="gps")return "invalid_coordinates";
    if(!event.coords||typeof event.coords!=="object")return "missing_coordinates";
    if(!hasFiniteNumber(event.coords.latitude)||!hasFiniteNumber(event.coords.longitude))return "invalid_coordinates";
    const latitude=Number(event.coords.latitude),longitude=Number(event.coords.longitude);
    if(latitude< -90||latitude>90||longitude< -180||longitude>180)return "invalid_coordinates";
    if(!hasFiniteNumber(event.timestamp))return "invalid_timestamp";
    if(event.accuracy===null||event.accuracy===undefined||event.accuracy==="")return "missing_accuracy";
    if(!hasFiniteNumber(event.accuracy)||Number(event.accuracy)<0)return "invalid_accuracy";
    if(Number(event.accuracy)>MAX_ACCURACY_M)return "accuracy_over_limit";
    return null;
  }
  function validFix(event) { return fixRejectionReason(event)===null; }
  function sessionKey(event) {
    const id=event&&event.clockSessionId;
    return id===null||id===undefined||String(id)===""?"legacy":"session:"+String(id);
  }
  function listSessions(events) {
    const groups=new Map();
    for(const event of Array.isArray(events)?events:[]){
      if(!event||typeof event!=="object")continue;
      const key=sessionKey(event);
      if(!groups.has(key))groups.set(key,{key,clockSessionId:key==="legacy"?null:String(event.clockSessionId),count:0,gpsCount:0,gpsObservationCount:0,firstTimestamp:null,lastTimestamp:null});
      const group=groups.get(key);group.count++;
      if(event.kind==="gps"){group.gpsObservationCount++;if(validFix(event))group.gpsCount++;}
      if(hasFiniteNumber(event.timestamp)){
        const timestamp=Number(event.timestamp);
        group.firstTimestamp=group.firstTimestamp===null?timestamp:Math.min(group.firstTimestamp,timestamp);
        group.lastTimestamp=group.lastTimestamp===null?timestamp:Math.max(group.lastTimestamp,timestamp);
      }
    }
    return Array.from(groups.values()).sort((a,b)=>a.key<b.key?-1:a.key>b.key?1:0).map(group=>Object.freeze(group));
  }
  function eventClockBasis(event) {
    return hasFiniteNumber(event&&event.monotonicElapsedMs)?"monotonic":"wall";
  }
  function elapsedMilliseconds(start,end) {
    if(eventClockBasis(start)==="monotonic"&&eventClockBasis(end)==="monotonic"&&sessionKey(start)===sessionKey(end)){
      return Number(end.monotonicElapsedMs)-Number(start.monotonicElapsedMs);
    }
    return Number(end.timestamp)-Number(start.timestamp);
  }
  function createTrackAnalysis(events) {
    const rejectionCounts={missing_coordinates:0,invalid_coordinates:0,invalid_timestamp:0,missing_accuracy:0,invalid_accuracy:0,accuracy_over_limit:0};
    const breakCounts={rejected_fix:0,clock_basis_change:0,non_increasing_time:0,time_gap:0,distance_jump:0,speed_limit:0};
    const gps=(Array.isArray(events)?events:[]).map((event,index)=>({event,index})).filter(item=>item.event&&(item.event.kind==="gps"||!item.event.kind));
    gps.sort((a,b)=>{
      const am=Number(a.event.monotonicElapsedMs),bm=Number(b.event.monotonicElapsedMs);
      if(Number.isFinite(am)&&Number.isFinite(bm))return am-bm||a.index-b.index;
      const at=Number(a.event.timestamp),bt=Number(b.event.timestamp);
      if(Number.isFinite(at)&&Number.isFinite(bt))return at-bt||a.index-b.index;
      return a.index-b.index;
    });
    const runs=[];let current=[],acceptedFixCount=0,rejectedFixCount=0,clockFallbackCount=0,clockDivergedCount=0;
    const flush=()=>{if(current.length)runs.push(current);current=[];};
    for(const item of gps){
      const event=item.event,reason=fixRejectionReason(event);
      if(reason){
        rejectionCounts[reason]=(rejectionCounts[reason]||0)+1;rejectedFixCount++;
        if(current.length){breakCounts.rejected_fix++;flush();}
        continue;
      }
      acceptedFixCount++;
      if(eventClockBasis(event)==="wall")clockFallbackCount++;
      if(event.clockStatus==="wall_clock_diverged")clockDivergedCount++;
      const point={
        id:event.id==null?null:String(event.id),timestamp:Number(event.timestamp),accuracy:Number(event.accuracy),
        monotonicElapsedMs:hasFiniteNumber(event.monotonicElapsedMs)?Number(event.monotonicElapsedMs):null,
        clockSessionId:event.clockSessionId==null?null:String(event.clockSessionId),
        coords:{latitude:Number(event.coords.latitude),longitude:Number(event.coords.longitude)}
      };
      const previous=current[current.length-1];
      if(previous){
        let breakReason=null;
        if(eventClockBasis(previous)!==eventClockBasis(point))breakReason="clock_basis_change";
        else{
          const elapsedMs=elapsedMilliseconds(previous,point),distanceM=haversine(previous.coords,point.coords);
          const speedMps=elapsedMs>0?distanceM/(elapsedMs/1000):Infinity;
          if(!(elapsedMs>0))breakReason="non_increasing_time";
          else if(elapsedMs>MAX_GAP_MS)breakReason="time_gap";
          else if(distanceM>MAX_SEGMENT_DISTANCE_M)breakReason="distance_jump";
          else if(speedMps>MAX_SPEED_MPS)breakReason="speed_limit";
        }
        if(breakReason){breakCounts[breakReason]++;flush();}
      }
      current.push(point);
    }
    flush();
    const longestRunFixes=runs.reduce((maximum,run)=>Math.max(maximum,run.length),0);
    const audit=Object.freeze({
      gpsObservationCount:gps.length,acceptedFixCount,rejectedFixCount,
      rejectionCounts:Object.freeze({...rejectionCounts}),breakCounts:Object.freeze({...breakCounts}),
      continuityBreaks:Object.values(breakCounts).reduce((sum,value)=>sum+value,0),
      continuousRunCount:runs.length,longestRunFixes,clockFallbackCount,clockDivergedCount,
      scenarioReady:runs.some(run=>run.length>=MIN_FIXES)
    });
    return {runs,audit};
  }
  function audit(events,options={}) {
    const all=Array.isArray(events)?events:[],keys=Array.from(new Set(all.filter(event=>event&&typeof event==="object").map(sessionKey))).sort();
    const requested=options.sessionKey===undefined||options.sessionKey===null||options.sessionKey===""?null:String(options.sessionKey);
    const selected=requested||(keys.length===1?keys[0]:null);
    if(!selected||!keys.includes(selected))return null;
    return createTrackAnalysis(all.filter(event=>sessionKey(event)===selected)).audit;
  }
  function formatAudit(result,locale="en") {
    if(!result)return "";
    const copy=AUDIT_LABELS[locale]||AUDIT_LABELS.en;
    const fill=(template,values)=>template.replace(/\{(\w+)\}/g,(match,key)=>String(values[key]??match));
    const parts=[fill(copy.summary,{accepted:result.acceptedFixCount,total:result.gpsObservationCount,rejected:result.rejectedFixCount,runs:result.continuousRunCount,longest:result.longestRunFixes})];
    const rejected=Object.entries(result.rejectionCounts).filter(([,count])=>count>0).map(([key,count])=>(copy.reasons[key]||key)+": "+count);
    if(rejected.length)parts.push(fill(copy.rejected,{items:rejected.join(", ")}));
    const breaks=Object.entries(result.breakCounts).filter(([,count])=>count>0).map(([key,count])=>(copy.breakReasons[key]||key)+": "+count);
    if(breaks.length)parts.push(fill(copy.breaks,{items:breaks.join(", ")}));
    if(result.clockFallbackCount||result.clockDivergedCount)parts.push(fill(copy.clock,{fallback:result.clockFallbackCount,diverged:result.clockDivergedCount}));
    parts.push(result.scenarioReady?copy.ready:copy.notReady);
    return parts.join(" ");
  }
  function localMeters(point,origin) {
    const distance=haversine(origin,point),angle=bearing(origin,point);
    return {east:distance*Math.sin(angle),north:distance*Math.cos(angle)};
  }
  function offsetPoint(origin,eastM,northM) {
    const distance=Math.hypot(eastM,northM);
    if(!distance)return {latitude:origin.latitude,longitude:origin.longitude};
    const angular=distance/EARTH_RADIUS_M,initialBearing=Math.atan2(eastM,northM);
    const lat1=origin.latitude*Math.PI/180,lon1=origin.longitude*Math.PI/180;
    const lat2=Math.asin(Math.sin(lat1)*Math.cos(angular)+Math.cos(lat1)*Math.sin(angular)*Math.cos(initialBearing));
    const lon2=lon1+Math.atan2(Math.sin(initialBearing)*Math.sin(angular)*Math.cos(lat1),Math.cos(angular)-Math.sin(lat1)*Math.sin(lat2));
    return {latitude:lat2*180/Math.PI,longitude:normalizeLongitude(lon2*180/Math.PI)};
  }
  function estimate(events,options={}) {
    const kind=options.kind==="past"?"past":"future",horizonSeconds=Number(options.horizonSeconds);
    if(!Number.isFinite(horizonSeconds)||horizonSeconds<=0||horizonSeconds>900)return null;
    const all=Array.isArray(events)?events:[],availableKeys=Array.from(new Set(all.filter(event=>event&&typeof event==="object").map(sessionKey))).sort();
    const requestedKey=options.sessionKey===undefined||options.sessionKey===null||options.sessionKey===""?null:String(options.sessionKey);
    const selectedKey=requestedKey||(availableKeys.length===1?availableKeys[0]:null);
    if(!selectedKey||!availableKeys.includes(selectedKey))return null;
    const analysis=createTrackAnalysis(all.filter(event=>sessionKey(event)===selectedKey));
    const eligibleRuns=analysis.runs.filter(run=>run.length>=MIN_FIXES);
    if(!eligibleRuns.length)return null;
    const selectedRun=kind==="past"?eligibleRuns[0]:eligibleRuns[eligibleRuns.length-1];
    const fixes=kind==="past"?selectedRun.slice(0,MAX_FIXES):selectedRun.slice(-MAX_FIXES);
    if(fixes.length<MIN_FIXES)return null;
    const projectionOrigin=fixes[0].coords,projected=fixes.map(fix=>localMeters(fix.coords,projectionOrigin));
    const velocities=[],accuracySensitivityRates=[];
    for(let index=0;index<fixes.length-1;index++){
      const start=fixes[index],end=fixes[index+1],elapsedSeconds=elapsedMilliseconds(start,end)/1000;
      if(!(elapsedSeconds>0))return null;
      velocities.push({
        east:(projected[index+1].east-projected[index].east)/elapsedSeconds,
        north:(projected[index+1].north-projected[index].north)/elapsedSeconds
      });
      accuracySensitivityRates.push((start.accuracy+end.accuracy)/elapsedSeconds);
    }
    const medianEastMps=median(velocities.map(item=>item.east)),medianNorthMps=median(velocities.map(item=>item.north));
    const speedMps=Math.hypot(medianEastMps,medianNorthMps);
    const medianVelocityResidualMps=median(velocities.map(item=>{const residual=Math.hypot(item.east-medianEastMps,item.north-medianNorthMps);return residual<1e-9?0:residual;}));
    const accuracySensitivityMps=median(accuracySensitivityRates);
    const anchor=kind==="past"?fixes[0]:fixes[fixes.length-1],direction=kind==="past"?-1:1;
    const target=offsetPoint(anchor.coords,medianEastMps*horizonSeconds*direction,medianNorthMps*horizonSeconds*direction);
    const variabilityContributionM=medianVelocityResidualMps*horizonSeconds;
    const accuracySensitivityContributionM=accuracySensitivityMps*horizonSeconds;
    const uncertaintyRadiusM=Math.ceil(anchor.accuracy+variabilityContributionM+accuracySensitivityContributionM);
    return Object.freeze({
      kind,method:"median-local-velocity",sessionKey:selectedKey,clockSessionId:fixes[0].clockSessionId==null?null:String(fixes[0].clockSessionId),
      origin:Object.freeze({...anchor.coords}),target:Object.freeze(target),
      distanceM:speedMps*horizonSeconds,speedMps,sampleCount:fixes.length,segmentCount:velocities.length,
      sourceObservationIds:Object.freeze(fixes.map(fix=>fix.id).filter(Boolean)),anchorAccuracyM:anchor.accuracy,
      medianVelocityResidualMps,accuracySensitivityMps,variabilityContributionM,accuracySensitivityContributionM,
      uncertaintyRadiusM,horizonSeconds
    });
  }
  function closeRing(points) {
    if(points.length<3)return null;
    const ring=points.map(point=>[point[0],point[1]]);
    ring.push([ring[0][0],ring[0][1]]);
    return ring;
  }
  function clipLongitude(ring,boundary,keepLess) {
    const points=ring.slice(0,-1),output=[];
    for(let index=0;index<points.length;index++){
      const current=points[index],previous=points[(index+points.length-1)%points.length];
      const currentInside=keepLess?current[0]<=boundary:current[0]>=boundary;
      const previousInside=keepLess?previous[0]<=boundary:previous[0]>=boundary;
      if(currentInside!==previousInside){
        const fraction=(boundary-previous[0])/(current[0]-previous[0]);
        output.push([boundary,previous[1]+fraction*(current[1]-previous[1])]);
      }
      if(currentInside)output.push(current);
    }
    return closeRing(output);
  }
  function destinationPoint(origin,bearingRadians,distanceM) {
    const angularDistance=distanceM/EARTH_RADIUS_M;
    const latitude1=origin.latitude*Math.PI/180;
    const longitude1=origin.longitude*Math.PI/180;
    const latitude2=Math.asin(Math.max(-1,Math.min(1,
      Math.sin(latitude1)*Math.cos(angularDistance)
      +Math.cos(latitude1)*Math.sin(angularDistance)*Math.cos(bearingRadians)
    )));
    const longitude2=longitude1+Math.atan2(
      Math.sin(bearingRadians)*Math.sin(angularDistance)*Math.cos(latitude1),
      Math.cos(angularDistance)-Math.sin(latitude1)*Math.sin(latitude2)
    );
    return {
      latitude:latitude2*180/Math.PI,
      longitude:normalizeLongitude(longitude2*180/Math.PI)
    };
  }
  function accuracyFootprint(center,radiusM,steps=36) {
    const numeric=value=>(typeof value==="number"&&Number.isFinite(value))
      ||(typeof value==="string"&&value.trim()!==""&&Number.isFinite(Number(value)));
    if(!center||typeof center!=="object"
      ||!numeric(center.latitude)||!numeric(center.longitude)||!numeric(radiusM)
      ||!Number.isInteger(steps)||steps<12||steps>72)return null;
    const latitude=Number(center.latitude),longitude=Number(center.longitude),radius=Number(radiusM);
    if(latitude < -90||latitude > 90||longitude < -180||longitude > 180
      ||radius<=0||radius>MAX_ACCURACY_M)return null;
    const poleClearanceM=(90-Math.abs(latitude))*Math.PI/180*EARTH_RADIUS_M;
    if(radius>=poleClearanceM)return null;
    const origin={latitude,longitude},unwrapped=[];
    for(let index=0;index<steps;index++){
      const point=destinationPoint(origin,2*Math.PI*index/steps,radius);
      const longitudeOffset=normalizeLongitude(point.longitude-longitude);
      unwrapped.push([longitude+longitudeOffset,point.latitude]);
    }
    const minLongitude=Math.min(...unwrapped.map(point=>point[0]));
    const maxLongitude=Math.max(...unwrapped.map(point=>point[0]));
    const ring=closeRing(unwrapped);
    if(!ring)return null;
    if(maxLongitude>180){
      const western=clipLongitude(ring,180,true);
      const eastern=clipLongitude(ring,180,false);
      const shiftedEastern=eastern?.map(([lon,lat])=>[lon-360,lat]);
      const easternRing=shiftedEastern?closeRing(shiftedEastern):null;
      if(!western||!easternRing)return null;
      return {type:"MultiPolygon",coordinates:[[western],[easternRing]]};
    }
    if(minLongitude < -180){
      const eastern=clipLongitude(ring,-180,false);
      const western=clipLongitude(ring,-180,true);
      const shiftedWestern=western?.map(([lon,lat])=>[lon+360,lat]);
      const westernRing=shiftedWestern?closeRing(shiftedWestern):null;
      if(!eastern||!westernRing)return null;
      return {type:"MultiPolygon",coordinates:[[eastern],[westernRing]]};
    }
    return {type:"Polygon",coordinates:[ring.map(([lon,lat])=>[normalizeLongitude(lon),lat])]};
  }
  const api=Object.freeze({
    estimate,audit,formatAudit,median,sessionKey,listSessions,accuracyFootprint,
    locales:Object.freeze(Object.keys(AUDIT_LABELS)),
    constants:Object.freeze({MAX_ACCURACY_M,MAX_GAP_MS,MAX_SEGMENT_DISTANCE_M,MAX_SPEED_MPS,MAX_FIXES,MIN_FIXES})
  });
  if(typeof window!=="undefined")window.SSSWETGpsScenarioModel=api;
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
})();