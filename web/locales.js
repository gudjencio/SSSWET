/* SSSWET interface localization catalogue.
 * Keep keys aligned across locales. Missing entries fall back to English.
 * Translations are interface drafts and should receive native-speaker review.
 */
window.SSSWET_LOCALES = {
  en: {
    name: "English", dir: "ltr",
    mapTitle: "Knowledge network", mapCaption: "Recorded nodes and declared relationships",
    mapEmpty: "No knowledge nodes have been recorded yet.", mapAccessible: "A network diagram of recorded knowledge nodes and relationships",
    mapNodes: "nodes shown", mapRelations: "recorded links", mapDisclaimer: "Only declared graph relationships are drawn.",
    opportunityTitle: "Research opportunities", opportunityCaption: "Human review required · no automatic scientific conclusions",
    opportunityEmpty: "No review opportunities are currently available.", gapSignal: "Research gap", linkSignal: "Possible interdisciplinary link",
    suggestedAction: "Suggested review", references: "Graph records", campaignsShort: "Campaigns",
    opportunityDisclaimer: "These are review leads, not discoveries. Similar wording does not prove a scientific connection.",
    recordedRelation: "Recorded relationship",
    inspectorEmpty: "Select a node to inspect its details and recorded connections.",
    unknownType: "Unknown type", unverifiedState: "Unverified", noDescription: "No description has been recorded.",
    nodeIdentifier: "Record ID", recordedConnections: "Recorded connections", noRecordedConnections: "No recorded connection for this node.",
    nodeDisclaimer: "Connections shown here are explicit graph records, not proof that a claim is true.",
    selectNode: "Inspect node", noNodeOpportunities: "No current review lead references this node.",
    labReproTitle: "Reproducibility & data provenance", labReproCaption: "Recorded runs, pending comparisons and dataset integrity",
    labMatrixTitle: "Cross-campaign reproduction matrix", labDatasetsTitle: "Dataset provenance",
    labReproDisclaimer: "A matching result or intact fingerprint does not establish scientific validity or independent reproduction.",
    labProtocolGroups: "protocol groups", labRecordedRuns: "recorded runs", labPendingPairs: "pending comparisons",
    labCampaigns: "campaigns", labNoRuns: "No recorded laboratory runs yet.", labCompared: "comparison recorded",
    labComparisonPending: "comparison pending", labDatasetVersions: "dataset versions", labIntegrityChecks: "integrity checks",
    labFingerprintsIntact: "Recorded fingerprints intact", labIntegrityWarning: "Integrity review required",
    labSharedContentCandidates: "Identical-content candidates", labNoSharedContent: "No repeated content fingerprints recorded.",
    labFilesNotStored: "The registry stores dataset metadata and declared digests, not the dataset files.",
    timelineTitle: "Research history", timelineFilter: "Campaign", allCampaigns: "All campaigns",
    timelineSearchLabel: "Search history", timelineSearchPlaceholder: "Search titles, descriptions or references",
    timelineTypeFilter: "Event type", allEventTypes: "All event types", timelineNoMatches: "No events match these filters.",
    timelineCaption: "Recorded changes in chronological order. A timeline is not scientific validation.",
    timelineEmpty: "No dated research events are available.", timelineUnavailable: "Research history is temporarily unavailable.",
    timelineEvent: "Research event", dateUnavailable: "Date unavailable", timelineNotValidation: "Historical record · not scientific validation",
    timelineShown: "events shown", timelineUndated: "Records without reliable dates are omitted rather than assigned invented dates.",
    dashboard: "Global science dashboard", dashboardNote: "Live overview from the local research engine. Missing connections are shown explicitly.", refresh: "Refresh",
    dashTimeline: "Research timeline", dashTimelineEvents: "recorded events", dashTimelineCampaigns: "campaigns represented", dashTimelineKinds: "event categories", dashScientificMemory: "Versioned scientific memory", dashMemoryVersions: "stored versions", dashCurrentMemory: "current entries", dashContestedMemory: "entries with contradictions", dashDisputes: "Scientific dispute review", dashDetectedContradictions: "detected contradictions", dashOpenReviews: "open reviews", dashClosedReviews: "closed reviews", dashPeerReviews: "Independent peer review", dashReviewOpen: "open review requests", dashReviewCompleted: "completed requests", dashReviewSubmissions: "submitted assessments", dashCollaboration: "Cross-campaign cooperation", dashRecommendations: "collaboration proposals", dashTargets: "target campaigns", dashUnverified: "unverified items", dashCampaignWatch: "Campaign literature monitoring", dashSubscriptions: "active subscriptions", dashNewLeads: "new publications", dashWatchRuns: "monitoring runs", dashLiteratureWatch: "Literature watch", dashCandidates: "review candidates", dashDuplicates: "possible DOI duplicates", dashTitleMatches: "possible title matches", dashCampaigns: "Research campaigns", dashResources: "Resource coordination", dashTransfers: "Knowledge transfers", dashDigitalLab: "Shared digital laboratory", dashLabProtocols: "published protocols", dashLabRuns: "recorded runs", dashLabComparisons: "saved comparisons", dashLabPublished: "shared protocols", dashExperiments: "Experiments", dashOptimization: "Adaptive proposals", dashGaps: "Research gaps", dashGraph: "Knowledge graph", dashActivity: "Recent activity", dashConflicts: "Contradictions to review", dashUnavailable: "UNAVAILABLE", dashNoRecords: "NO RECORDS", dashLive: "LIVE DATA", dashActive: "active", dashBlocked: "blocked", dashQueued: "queued", dashCompleted: "completed", dashPending: "pending", dashAccepted: "accepted", dashRejected: "rejected", dashPlans: "plans", dashRecords: "records", dashNodes: "nodes", dashRelations: "relationships", dashHigh: "high", dashMedium: "medium", dashLow: "low", dashCycles: "cycles", dashRecent: "recent entries", dashEndpointUnavailable: "This local API endpoint is unavailable.", dashNoData: "No data recorded.",
    tagline: "Super Soldier Space Warping Engeriening Tech",
    status: "RESEARCH INTERFACE", statusOnline: "LOCAL RESEARCH ENGINE CONNECTED",
    statusOffline: "LOCAL RESEARCH ENGINE NOT CONNECTED",
    mission: "Research ideas. Test them. Verify them. Never confuse a hypothesis with reality.",
    agents: "Research agents", verification: "verification-first",
    discover: "What did you discover?", working: "What are you working on?",
    verified: "Latest verified results", ready: "The interface is ready. Connect the local engine to display live research data.",
    footer: "ETDESS is the French translation of SSSWET. Public results remain subject to verification.",
    offline: "The local research engine is not connected. GitHub Pages is a static preview; run the local application for live research data.",
    noDiscoveries: "No research outputs are stored yet.", noActivity: "No research activity has been recorded yet.",
    noVerified: "No independently verified knowledge is available yet.",
    language: "Language", social: "SSSWET social networks", contact: "Contact"
  },
  fr: {
    name: "Français", dir: "ltr",
    mapTitle: "Réseau des connaissances", mapCaption: "Nœuds enregistrés et relations déclarées",
    mapEmpty: "Aucun nœud de connaissance n’a encore été enregistré.", mapAccessible: "Schéma du réseau des connaissances enregistrées et de leurs relations",
    mapNodes: "nœuds affichés", mapRelations: "liens enregistrés", mapDisclaimer: "Seules les relations déclarées dans le graphe sont représentées.",
    opportunityTitle: "Pistes de recherche", opportunityCaption: "Examen humain requis · aucune conclusion scientifique automatique",
    opportunityEmpty: "Aucune piste à examiner pour le moment.", gapSignal: "Lacune de recherche", linkSignal: "Lien interdisciplinaire possible",
    suggestedAction: "Examen suggéré", references: "Éléments du graphe", campaignsShort: "Campagnes",
    opportunityDisclaimer: "Ces éléments sont des pistes à examiner, pas des découvertes. Une similarité de vocabulaire ne prouve pas un lien scientifique.",
    recordedRelation: "Relation enregistrée",
    inspectorEmpty: "Sélectionnez un nœud pour consulter ses détails et ses connexions enregistrées.",
    unknownType: "Type inconnu", unverifiedState: "Non vérifié", noDescription: "Aucune description n’a été enregistrée.",
    nodeIdentifier: "Identifiant du nœud", recordedConnections: "Connexions enregistrées", noRecordedConnections: "Aucune connexion enregistrée pour ce nœud.",
    nodeDisclaimer: "Les connexions affichées sont des relations explicites du graphe ; elles ne prouvent pas la véracité d’une affirmation.",
    selectNode: "Examiner le nœud", noNodeOpportunities: "Aucune piste à examiner ne référence ce nœud pour le moment.",
    labReproTitle: "Reproductibilité et provenance des données", labReproCaption: "Exécutions enregistrées, comparaisons en attente et intégrité des jeux de données",
    labMatrixTitle: "Matrice de reproduction inter-campagnes", labDatasetsTitle: "Provenance des jeux de données",
    labReproDisclaimer: "Des résultats concordants ou une empreinte intacte ne démontrent ni la validité scientifique ni une reproduction indépendante.",
    labProtocolGroups: "groupes de protocoles", labRecordedRuns: "exécutions enregistrées", labPendingPairs: "comparaisons en attente",
    labCampaigns: "campagnes", labNoRuns: "Aucune exécution de laboratoire enregistrée.", labCompared: "comparaison enregistrée",
    labComparisonPending: "comparaison en attente", labDatasetVersions: "versions de jeux de données", labIntegrityChecks: "contrôles d’intégrité",
    labFingerprintsIntact: "Empreintes enregistrées intactes", labIntegrityWarning: "Vérification d’intégrité nécessaire",
    labSharedContentCandidates: "Contenus identiques potentiels", labNoSharedContent: "Aucune empreinte de contenu répétée enregistrée.",
    labFilesNotStored: "Le registre conserve les métadonnées et empreintes déclarées, pas les fichiers des jeux de données.",
    timelineTitle: "Historique des recherches", timelineFilter: "Campagne", allCampaigns: "Toutes les campagnes",
    timelineSearchLabel: "Rechercher dans l’historique", timelineSearchPlaceholder: "Titres, descriptions ou références",
    timelineTypeFilter: "Type d’événement", allEventTypes: "Tous les types", timelineNoMatches: "Aucun événement ne correspond à ces filtres.",
    timelineCaption: "Évolutions enregistrées dans l’ordre chronologique. Une chronologie ne constitue pas une validation scientifique.",
    timelineEmpty: "Aucun événement de recherche daté n’est disponible.", timelineUnavailable: "L’historique des recherches est momentanément indisponible.",
    timelineEvent: "Événement de recherche", dateUnavailable: "Date indisponible", timelineNotValidation: "Trace historique · pas une validation scientifique",
    timelineShown: "événements affichés", timelineUndated: "Les éléments sans date fiable sont omis plutôt que de recevoir une date inventée.",
    dashboard: "Tableau de bord scientifique global", dashboardNote: "Vue d'ensemble en direct du moteur de recherche local. Les connexions indisponibles sont signalées explicitement.", refresh: "Actualiser",
    dashTimeline: "Chronologie scientifique", dashTimelineEvents: "événements enregistrés", dashTimelineCampaigns: "campagnes représentées", dashTimelineKinds: "catégories d’événements", dashScientificMemory: "Mémoire scientifique versionnée", dashMemoryVersions: "versions conservées", dashCurrentMemory: "entrées actuelles", dashContestedMemory: "entrées en contradiction", dashDisputes: "Examen des désaccords scientifiques", dashDetectedContradictions: "contradictions détectées", dashOpenReviews: "examens ouverts", dashClosedReviews: "examens clôturés", dashPeerReviews: "Évaluation scientifique indépendante", dashReviewOpen: "demandes ouvertes", dashReviewCompleted: "demandes terminées", dashReviewSubmissions: "évaluations reçues", dashCollaboration: "Coopération inter-campagnes", dashRecommendations: "propositions de collaboration", dashTargets: "campagnes destinataires", dashUnverified: "éléments non vérifiés", dashCampaignWatch: "Veille scientifique par campagne", dashSubscriptions: "abonnements actifs", dashNewLeads: "nouvelles publications", dashWatchRuns: "passages de veille", dashLiteratureWatch: "Veille scientifique", dashCandidates: "publications à examiner", dashDuplicates: "doublons DOI possibles", dashTitleMatches: "titres similaires possibles", dashCampaigns: "Campagnes de recherche", dashResources: "Coordination des ressources", dashTransfers: "Transferts de connaissances", dashDigitalLab: "Laboratoire numérique partagé", dashLabProtocols: "protocoles publiés", dashLabRuns: "exécutions enregistrées", dashLabComparisons: "comparaisons conservées", dashLabPublished: "protocoles partagés", dashExperiments: "Expériences", dashOptimization: "Propositions adaptatives", dashGaps: "Lacunes de recherche", dashGraph: "Graphe des connaissances", dashActivity: "Activité récente", dashConflicts: "Contradictions à examiner", dashUnavailable: "INDISPONIBLE", dashNoRecords: "AUCUNE DONNÉE", dashLive: "DONNÉES EN DIRECT", dashActive: "actives", dashBlocked: "bloquées", dashQueued: "en attente", dashCompleted: "terminées", dashPending: "en attente", dashAccepted: "acceptés", dashRejected: "refusés", dashPlans: "plans", dashRecords: "enregistrements", dashNodes: "nœuds", dashRelations: "relations", dashHigh: "élevée", dashMedium: "moyenne", dashLow: "faible", dashCycles: "cycles", dashRecent: "événements récents", dashEndpointUnavailable: "Point d'accès local indisponible.", dashNoData: "Aucune donnée enregistrée.",
    tagline: "Super Soldier Space Warping Engeriening Tech",
    status: "INTERFACE DE RECHERCHE", statusOnline: "MOTEUR DE RECHERCHE LOCAL CONNECTÉ",
    statusOffline: "MOTEUR DE RECHERCHE LOCAL NON CONNECTÉ",
    mission: "Rechercher des idées. Les tester. Les vérifier. Ne jamais confondre une hypothèse avec la réalité.",
    agents: "Agents de recherche", verification: "vérification prioritaire",
    discover: "Qu'avez-vous découvert ?", working: "Sur quoi travaillez-vous ?",
    verified: "Derniers résultats vérifiés", ready: "L'interface est prête. Connectez le moteur local pour afficher les données de recherche en direct.",
    footer: "ETDESS est la traduction française de SSSWET. Les résultats publics restent soumis à vérification.",
    offline: "Le moteur local n'est pas connecté. GitHub Pages affiche un aperçu statique ; lancez l'application locale pour accéder aux données en direct.",
    noDiscoveries: "Aucun résultat de recherche n'est encore enregistré.", noActivity: "Aucune activité de recherche n'a encore été enregistrée.",
    noVerified: "Aucune connaissance vérifiée indépendamment n'est encore disponible.",
    language: "Langue", social: "Réseaux sociaux de SSSWET", contact: "Contact"
  },
  es: {
    name: "Español", dir: "ltr", tagline: "Super Soldier Space Warping Engeriening Tech",
    dashboard: "Panel científico global", dashboardNote: "Resumen en directo del motor de investigación local. Las conexiones no disponibles se indican explícitamente.", refresh: "Actualizar",
    dashCampaigns: "Campañas de investigación", dashResources: "Coordinación de recursos", dashTransfers: "Transferencias de conocimiento", dashExperiments: "Experimentos", dashOptimization: "Propuestas adaptativas", dashGaps: "Vacíos de investigación", dashGraph: "Grafo de conocimiento", dashActivity: "Actividad reciente", dashConflicts: "Contradicciones por revisar", dashUnavailable: "NO DISPONIBLE", dashNoRecords: "SIN REGISTROS", dashLive: "DATOS EN DIRECTO", dashActive: "activas", dashBlocked: "bloqueadas", dashQueued: "en cola", dashCompleted: "completadas", dashPending: "pendientes", dashAccepted: "aceptadas", dashRejected: "rechazadas", dashPlans: "planes", dashRecords: "registros", dashNodes: "nodos", dashRelations: "relaciones", dashHigh: "alta", dashMedium: "media", dashLow: "baja", dashCycles: "ciclos", dashRecent: "eventos recientes", dashEndpointUnavailable: "Este punto de la API local no está disponible.", dashNoData: "No hay datos registrados.",
    status: "INTERFAZ DE INVESTIGACIÓN", statusOnline: "MOTOR DE INVESTIGACIÓN LOCAL CONECTADO",
    statusOffline: "MOTOR DE INVESTIGACIÓN LOCAL NO CONECTADO",
    mission: "Investigar ideas. Ponerlas a prueba. Verificarlas. Nunca confundir una hipótesis con la realidad.",
    agents: "Agentes de investigación", verification: "verificación prioritaria",
    discover: "¿Qué han descubierto?", working: "¿En qué están trabajando?",
    verified: "Últimos resultados verificados", ready: "La interfaz está lista. Conecta el motor local para mostrar datos de investigación en directo.",
    footer: "ETDESS es la traducción francesa de SSSWET. Los resultados públicos siguen sujetos a verificación.",
    offline: "El motor local no está conectado. GitHub Pages muestra una vista previa estática; ejecuta la aplicación local para ver datos en directo.",
    noDiscoveries: "Todavía no hay resultados de investigación guardados.", noActivity: "Todavía no se ha registrado actividad de investigación.",
    noVerified: "Todavía no hay conocimientos verificados de forma independiente.",
    language: "Idioma", social: "Redes sociales de SSSWET", contact: "Contacto"
  },
  de: {
    name: "Deutsch", dir: "ltr", tagline: "Super Soldier Space Warping Engeriening Tech",
    dashboard: "Globales Wissenschafts-Dashboard", dashboardNote: "Live-Übersicht der lokalen Forschungsumgebung. Fehlende Verbindungen werden ausdrücklich angezeigt.", refresh: "Aktualisieren",
    dashCampaigns: "Forschungskampagnen", dashResources: "Ressourcenkoordination", dashTransfers: "Wissensübertragungen", dashExperiments: "Experimente", dashOptimization: "Adaptive Vorschläge", dashGaps: "Forschungslücken", dashGraph: "Wissensgraph", dashActivity: "Letzte Aktivitäten", dashConflicts: "Zu prüfende Widersprüche", dashUnavailable: "NICHT VERFÜGBAR", dashNoRecords: "KEINE DATEN", dashLive: "LIVE-DATEN", dashActive: "aktiv", dashBlocked: "blockiert", dashQueued: "in Warteschlange", dashCompleted: "abgeschlossen", dashPending: "ausstehend", dashAccepted: "akzeptiert", dashRejected: "abgelehnt", dashPlans: "Pläne", dashRecords: "Einträge", dashNodes: "Knoten", dashRelations: "Beziehungen", dashHigh: "hoch", dashMedium: "mittel", dashLow: "niedrig", dashCycles: "Zyklen", dashRecent: "letzte Ereignisse", dashEndpointUnavailable: "Dieser lokale API-Endpunkt ist nicht verfügbar.", dashNoData: "Keine Daten erfasst.",
    status: "FORSCHUNGSSCHNITTSTELLE", statusOnline: "LOKALE FORSCHUNGSUMGEBUNG VERBUNDEN",
    statusOffline: "LOKALE FORSCHUNGSUMGEBUNG NICHT VERBUNDEN",
    mission: "Ideen erforschen. Sie testen. Sie überprüfen. Eine Hypothese niemals mit der Realität verwechseln.",
    agents: "Forschungsagenten", verification: "Verifizierung hat Vorrang",
    discover: "Was habt ihr entdeckt?", working: "Woran arbeitet ihr?",
    verified: "Neueste verifizierte Ergebnisse", ready: "Die Oberfläche ist bereit. Verbinde die lokale Engine, um aktuelle Forschungsdaten anzuzeigen.",
    footer: "ETDESS ist die französische Übersetzung von SSSWET. Öffentliche Ergebnisse müssen weiterhin überprüft werden.",
    offline: "Die lokale Forschungsumgebung ist nicht verbunden. GitHub Pages zeigt eine statische Vorschau.",
    noDiscoveries: "Noch keine Forschungsergebnisse gespeichert.", noActivity: "Noch keine Forschungsaktivität aufgezeichnet.",
    noVerified: "Noch keine unabhängig verifizierten Erkenntnisse verfügbar.",
    language: "Sprache", social: "SSSWET soziale Netzwerke", contact: "Kontakt"
  },
  it: {
    name: "Italiano", dir: "ltr", tagline: "Super Soldier Space Warping Engeriening Tech",
    dashboard: "Dashboard scientifico globale", dashboardNote: "Panoramica in tempo reale del motore di ricerca locale. Le connessioni mancanti sono indicate chiaramente.", refresh: "Aggiorna",
    dashCampaigns: "Campagne di ricerca", dashResources: "Coordinamento delle risorse", dashTransfers: "Trasferimenti di conoscenza", dashExperiments: "Esperimenti", dashOptimization: "Proposte adattive", dashGaps: "Lacune nella ricerca", dashGraph: "Grafo della conoscenza", dashActivity: "Attività recente", dashConflicts: "Contraddizioni da esaminare", dashUnavailable: "NON DISPONIBILE", dashNoRecords: "NESSUN DATO", dashLive: "DATI IN DIRETTA", dashActive: "attive", dashBlocked: "bloccate", dashQueued: "in coda", dashCompleted: "completate", dashPending: "in attesa", dashAccepted: "accettati", dashRejected: "rifiutati", dashPlans: "piani", dashRecords: "registrazioni", dashNodes: "nodi", dashRelations: "relazioni", dashHigh: "alta", dashMedium: "media", dashLow: "bassa", dashCycles: "cicli", dashRecent: "eventi recenti", dashEndpointUnavailable: "Questo endpoint API locale non è disponibile.", dashNoData: "Nessun dato registrato.",
    status: "INTERFACCIA DI RICERCA", statusOnline: "MOTORE DI RICERCA LOCALE CONNESSO",
    statusOffline: "MOTORE DI RICERCA LOCALE NON CONNESSO",
    mission: "Studiare le idee. Metterle alla prova. Verificarle. Non confondere mai un'ipotesi con la realtà.",
    agents: "Agenti di ricerca", verification: "verifica prioritaria",
    discover: "Che cosa avete scoperto?", working: "Su cosa state lavorando?",
    verified: "Ultimi risultati verificati", ready: "L'interfaccia è pronta. Collega il motore locale per visualizzare i dati di ricerca in tempo reale.",
    footer: "ETDESS è la traduzione francese di SSSWET. I risultati pubblici devono essere verificati.",
    offline: "Il motore locale non è connesso. GitHub Pages mostra un'anteprima statica.",
    noDiscoveries: "Non sono ancora presenti risultati di ricerca.", noActivity: "Non è ancora stata registrata attività di ricerca.",
    noVerified: "Non sono ancora disponibili conoscenze verificate in modo indipendente.",
    language: "Lingua", social: "Social network SSSWET", contact: "Contatto"
  },
  pt: {
    name: "Português", dir: "ltr", tagline: "Super Soldier Space Warping Engeriening Tech",
    dashboard: "Painel científico global", dashboardNote: "Visão geral em tempo real do mecanismo de pesquisa local. As conexões indisponíveis são indicadas explicitamente.", refresh: "Atualizar",
    dashCampaigns: "Campanhas de pesquisa", dashResources: "Coordenação de recursos", dashTransfers: "Transferências de conhecimento", dashExperiments: "Experimentos", dashOptimization: "Propostas adaptativas", dashGaps: "Lacunas de pesquisa", dashGraph: "Grafo de conhecimento", dashActivity: "Atividade recente", dashConflicts: "Contradições para analisar", dashUnavailable: "INDISPONÍVEL", dashNoRecords: "SEM REGISTROS", dashLive: "DADOS AO VIVO", dashActive: "ativas", dashBlocked: "bloqueadas", dashQueued: "na fila", dashCompleted: "concluídas", dashPending: "pendentes", dashAccepted: "aceitas", dashRejected: "rejeitadas", dashPlans: "planos", dashRecords: "registros", dashNodes: "nós", dashRelations: "relações", dashHigh: "alta", dashMedium: "média", dashLow: "baixa", dashCycles: "ciclos", dashRecent: "eventos recentes", dashEndpointUnavailable: "Este endpoint da API local está indisponível.", dashNoData: "Nenhum dado registrado.",
    status: "INTERFACE DE PESQUISA", statusOnline: "MOTOR DE PESQUISA LOCAL CONECTADO",
    statusOffline: "MOTOR DE PESQUISA LOCAL NÃO CONECTADO",
    mission: "Pesquisar ideias. Testá-las. Verificá-las. Nunca confundir uma hipótese com a realidade.",
    agents: "Agentes de pesquisa", verification: "verificação em primeiro lugar",
    discover: "O que vocês descobriram?", working: "Em que estão trabalhando?",
    verified: "Resultados verificados mais recentes", ready: "A interface está pronta. Conecte o mecanismo local para exibir dados de pesquisa em tempo real.",
    footer: "ETDESS é a tradução francesa de SSSWET. Os resultados públicos continuam sujeitos a verificação.",
    offline: "O mecanismo local não está conectado. O GitHub Pages apresenta uma prévia estática.",
    noDiscoveries: "Ainda não há resultados de pesquisa armazenados.", noActivity: "Ainda não há atividades de pesquisa registradas.",
    noVerified: "Ainda não há conhecimento verificado de forma independente.",
    language: "Idioma", social: "Redes sociais da SSSWET", contact: "Contato"
  },
  nl: {
    name: "Nederlands", dir: "ltr", tagline: "Super Soldier Space Warping Engeriening Tech",
    dashboard: "Wereldwijd wetenschappelijk dashboard", dashboardNote: "Liveoverzicht van de lokale onderzoeksmotor. Ontbrekende verbindingen worden expliciet weergegeven.", refresh: "Vernieuwen",
    dashCampaigns: "Onderzoekscampagnes", dashResources: "Resourcecoördinatie", dashTransfers: "Kennisoverdrachten", dashExperiments: "Experimenten", dashOptimization: "Adaptieve voorstellen", dashGaps: "Onderzoekshiaten", dashGraph: "Kennisgrafiek", dashActivity: "Recente activiteit", dashConflicts: "Te beoordelen tegenstrijdigheden", dashUnavailable: "NIET BESCHIKBAAR", dashNoRecords: "GEEN GEGEVENS", dashLive: "LIVEGEGEVENS", dashActive: "actief", dashBlocked: "geblokkeerd", dashQueued: "in wachtrij", dashCompleted: "voltooid", dashPending: "in afwachting", dashAccepted: "geaccepteerd", dashRejected: "afgewezen", dashPlans: "plannen", dashRecords: "records", dashNodes: "knopen", dashRelations: "relaties", dashHigh: "hoog", dashMedium: "gemiddeld", dashLow: "laag", dashCycles: "cycli", dashRecent: "recente gebeurtenissen", dashEndpointUnavailable: "Dit lokale API-eindpunt is niet beschikbaar.", dashNoData: "Geen gegevens geregistreerd.",
    status: "ONDERZOEKSINTERFACE", statusOnline: "LOKALE ONDERZOEKSMOTOR VERBONDEN",
    statusOffline: "LOKALE ONDERZOEKSMOTOR NIET VERBONDEN",
    mission: "Ideeën onderzoeken. Ze testen. Ze verifiëren. Een hypothese nooit verwarren met de werkelijkheid.",
    agents: "Onderzoeksagenten", verification: "verificatie staat voorop",
    discover: "Wat hebben jullie ontdekt?", working: "Waaraan werken jullie?",
    verified: "Nieuwste geverifieerde resultaten", ready: "De interface is klaar. Verbind de lokale engine om live onderzoeksgegevens te tonen.",
    footer: "ETDESS is de Franse vertaling van SSSWET. Openbare resultaten moeten worden geverifieerd.",
    offline: "De lokale onderzoeksmotor is niet verbonden. GitHub Pages toont een statische preview.",
    noDiscoveries: "Er zijn nog geen onderzoeksresultaten opgeslagen.", noActivity: "Er is nog geen onderzoeksactiviteit geregistreerd.",
    noVerified: "Er is nog geen onafhankelijk geverifieerde kennis beschikbaar.",
    language: "Taal", social: "SSSWET sociale netwerken", contact: "Contact"
  },
  ru: {
    name: "Русский", dir: "ltr", tagline: "Super Soldier Space Warping Engeriening Tech",
    dashboard: "Глобальная научная панель", dashboardNote: "Обзор локальной исследовательской системы в реальном времени. Отсутствующие подключения отмечаются явно.", refresh: "Обновить",
    dashCampaigns: "Исследовательские кампании", dashResources: "Координация ресурсов", dashTransfers: "Передача знаний", dashExperiments: "Эксперименты", dashOptimization: "Адаптивные предложения", dashGaps: "Пробелы в исследованиях", dashGraph: "Граф знаний", dashActivity: "Недавняя активность", dashConflicts: "Противоречия для проверки", dashUnavailable: "НЕДОСТУПНО", dashNoRecords: "НЕТ ДАННЫХ", dashLive: "АКТУАЛЬНЫЕ ДАННЫЕ", dashActive: "активно", dashBlocked: "заблокировано", dashQueued: "в очереди", dashCompleted: "завершено", dashPending: "ожидает", dashAccepted: "принято", dashRejected: "отклонено", dashPlans: "планы", dashRecords: "записи", dashNodes: "узлы", dashRelations: "связи", dashHigh: "высокий", dashMedium: "средний", dashLow: "низкий", dashCycles: "циклы", dashRecent: "последние события", dashEndpointUnavailable: "Эта локальная конечная точка API недоступна.", dashNoData: "Данные не зарегистрированы.",
    status: "ИНТЕРФЕЙС ИССЛЕДОВАНИЙ", statusOnline: "ЛОКАЛЬНАЯ ИССЛЕДОВАТЕЛЬСКАЯ СИСТЕМА ПОДКЛЮЧЕНА",
    statusOffline: "ЛОКАЛЬНАЯ ИССЛЕДОВАТЕЛЬСКАЯ СИСТЕМА НЕ ПОДКЛЮЧЕНА",
    mission: "Исследовать идеи. Проверять их. Подтверждать их. Никогда не путать гипотезу с реальностью.",
    agents: "Исследовательские агенты", verification: "приоритет проверки",
    discover: "Что удалось обнаружить?", working: "Над чем идёт работа?",
    verified: "Последние проверенные результаты", ready: "Интерфейс готов. Подключите локальный движок для отображения актуальных исследовательских данных.",
    footer: "ETDESS — французский перевод SSSWET. Публичные результаты требуют проверки.",
    offline: "Локальный исследовательский движок не подключён. GitHub Pages показывает статический предварительный просмотр.",
    noDiscoveries: "Исследовательские результаты пока не сохранены.", noActivity: "Исследовательская активность ещё не зарегистрирована.",
    noVerified: "Независимо проверенные знания пока отсутствуют.",
    language: "Язык", social: "Социальные сети SSSWET", contact: "Контакт"
  },
  uk: {
    name: "Українська", dir: "ltr", tagline: "Super Soldier Space Warping Engeriening Tech",
    dashboard: "Глобальна наукова панель", dashboardNote: "Огляд локальної дослідницької системи наживо. Відсутні підключення позначаються явно.", refresh: "Оновити",
    dashCampaigns: "Дослідницькі кампанії", dashResources: "Координація ресурсів", dashTransfers: "Передавання знань", dashExperiments: "Експерименти", dashOptimization: "Адаптивні пропозиції", dashGaps: "Прогалини досліджень", dashGraph: "Граф знань", dashActivity: "Остання активність", dashConflicts: "Суперечності для перевірки", dashUnavailable: "НЕДОСТУПНО", dashNoRecords: "НЕМАЄ ДАНИХ", dashLive: "АКТУАЛЬНІ ДАНІ", dashActive: "активні", dashBlocked: "заблоковані", dashQueued: "у черзі", dashCompleted: "завершені", dashPending: "очікують", dashAccepted: "прийняті", dashRejected: "відхилені", dashPlans: "плани", dashRecords: "записи", dashNodes: "вузли", dashRelations: "зв’язки", dashHigh: "високий", dashMedium: "середній", dashLow: "низький", dashCycles: "цикли", dashRecent: "останні події", dashEndpointUnavailable: "Ця локальна кінцева точка API недоступна.", dashNoData: "Дані не зареєстровано.",
    status: "ДОСЛІДНИЦЬКИЙ ІНТЕРФЕЙС", statusOnline: "ЛОКАЛЬНИЙ ДОСЛІДНИЦЬКИЙ РУШІЙ ПІДКЛЮЧЕНО",
    statusOffline: "ЛОКАЛЬНИЙ ДОСЛІДНИЦЬКИЙ РУШІЙ НЕ ПІДКЛЮЧЕНО",
    mission: "Досліджувати ідеї. Перевіряти їх. Підтверджувати їх. Не плутати гіпотезу з реальністю.",
    agents: "Дослідницькі агенти", verification: "перевірка передусім",
    discover: "Що вдалося відкрити?", working: "Над чим триває робота?",
    verified: "Останні перевірені результати", ready: "Інтерфейс готовий. Підключіть локальний рушій, щоб переглядати актуальні дослідницькі дані.",
    footer: "ETDESS — французький переклад SSSWET. Публічні результати потребують перевірки.",
    offline: "Локальний дослідницький рушій не підключено. GitHub Pages показує статичний попередній перегляд.",
    noDiscoveries: "Результати досліджень ще не збережено.", noActivity: "Дослідницьку активність ще не зафіксовано.",
    noVerified: "Незалежно перевірені знання поки що відсутні.",
    language: "Мова", social: "Соціальні мережі SSSWET", contact: "Контакт"
  },
  ar: {
    name: "العربية", dir: "rtl", tagline: "Super Soldier Space Warping Engeriening Tech",
    dashboard: "لوحة العلوم العالمية", dashboardNote: "نظرة مباشرة من محرك البحث المحلي. يتم توضيح الاتصالات غير المتاحة.", refresh: "تحديث",
    dashCampaigns: "حملات البحث", dashResources: "تنسيق الموارد", dashTransfers: "نقل المعرفة", dashExperiments: "التجارب", dashOptimization: "مقترحات تكيفية", dashGaps: "فجوات البحث", dashGraph: "الرسم المعرفي", dashActivity: "النشاط الأخير", dashConflicts: "تناقضات للمراجعة", dashUnavailable: "غير متاح", dashNoRecords: "لا توجد بيانات", dashLive: "بيانات مباشرة", dashActive: "نشطة", dashBlocked: "محظورة", dashQueued: "في قائمة الانتظار", dashCompleted: "مكتملة", dashPending: "قيد الانتظار", dashAccepted: "مقبولة", dashRejected: "مرفوضة", dashPlans: "خطط", dashRecords: "سجلات", dashNodes: "عُقد", dashRelations: "علاقات", dashHigh: "عالية", dashMedium: "متوسطة", dashLow: "منخفضة", dashCycles: "دورات", dashRecent: "أحداث حديثة", dashEndpointUnavailable: "نقطة واجهة API المحلية هذه غير متاحة.", dashNoData: "لا توجد بيانات مسجلة.",
    status: "واجهة البحث", statusOnline: "محرك البحث المحلي متصل",
    statusOffline: "محرك البحث المحلي غير متصل",
    mission: "ابحث عن الأفكار. اختبرها. تحقق منها. لا تخلط أبدًا بين الفرضية والواقع.",
    agents: "وكلاء البحث", verification: "التحقق أولاً",
    discover: "ما الذي اكتشفتموه؟", working: "على ماذا تعملون؟",
    verified: "أحدث النتائج التي تم التحقق منها", ready: "الواجهة جاهزة. اربط محرك البحث المحلي لعرض بيانات البحث المباشرة.",
    footer: "ETDESS هي الترجمة الفرنسية لـ SSSWET. تظل النتائج العامة بحاجة إلى التحقق.",
    offline: "محرك البحث المحلي غير متصل. تعرض GitHub Pages معاينة ثابتة.",
    noDiscoveries: "لم يتم حفظ نتائج بحث بعد.", noActivity: "لم يتم تسجيل أي نشاط بحث بعد.",
    noVerified: "لا تتوفر بعد معرفة تم التحقق منها بشكل مستقل.",
    language: "اللغة", social: "شبكات SSSWET الاجتماعية", contact: "اتصل بنا"
  },
  he: {
    name: "עברית", dir: "rtl", tagline: "Super Soldier Space Warping Engeriening Tech",
    dashboard: "לוח מחקר מדעי גלובלי", dashboardNote: "תצוגה חיה ממנוע המחקר המקומי. חיבורים חסרים מסומנים במפורש.", refresh: "רענון",
    dashCampaigns: "קמפיינים מחקריים", dashResources: "תיאום משאבים", dashTransfers: "העברות ידע", dashExperiments: "ניסויים", dashOptimization: "הצעות אדפטיביות", dashGaps: "פערי מחקר", dashGraph: "גרף ידע", dashActivity: "פעילות אחרונה", dashConflicts: "סתירות לבדיקה", dashUnavailable: "לא זמין", dashNoRecords: "אין נתונים", dashLive: "נתונים חיים", dashActive: "פעילים", dashBlocked: "חסומים", dashQueued: "בתור", dashCompleted: "הושלמו", dashPending: "ממתינים", dashAccepted: "התקבלו", dashRejected: "נדחו", dashPlans: "תוכניות", dashRecords: "רשומות", dashNodes: "צמתים", dashRelations: "קשרים", dashHigh: "גבוה", dashMedium: "בינוני", dashLow: "נמוך", dashCycles: "מחזורים", dashRecent: "אירועים אחרונים", dashEndpointUnavailable: "נקודת API מקומית זו אינה זמינה.", dashNoData: "לא נרשמו נתונים.",
    status: "ממשק מחקר", statusOnline: "מנוע המחקר המקומי מחובר",
    statusOffline: "מנוע המחקר המקומי אינו מחובר",
    mission: "חוקרים רעיונות. בודקים אותם. מאמתים אותם. לעולם אין לבלבל בין השערה למציאות.",
    agents: "סוכני מחקר", verification: "האימות קודם לכול",
    discover: "מה גיליתם?", working: "על מה אתם עובדים?",
    verified: "התוצאות המאומתות האחרונות", ready: "הממשק מוכן. חברו את המנוע המקומי כדי להציג נתוני מחקר בזמן אמת.",
    footer: "ETDESS הוא התרגום לצרפתית של SSSWET. יש לאמת תוצאות ציבוריות.",
    offline: "מנוע המחקר המקומי אינו מחובר. GitHub Pages מציג תצוגה מקדימה סטטית.",
    noDiscoveries: "עדיין לא נשמרו תוצאות מחקר.", noActivity: "עדיין לא נרשמה פעילות מחקר.",
    noVerified: "עדיין אין ידע שאומת באופן עצמאי.",
    language: "שפה", social: "הרשתות החברתיות של SSSWET", contact: "יצירת קשר"
  },
  ja: {
    name: "日本語", dir: "ltr", tagline: "Super Soldier Space Warping Engeriening Tech",
    dashboard: "グローバル科学ダッシュボード", dashboardNote: "ローカル研究エンジンのライブ概要です。利用できない接続は明示されます。", refresh: "更新",
    dashCampaigns: "研究キャンペーン", dashResources: "リソース調整", dashTransfers: "知識の共有", dashExperiments: "実験", dashOptimization: "適応型提案", dashGaps: "研究課題", dashGraph: "知識グラフ", dashActivity: "最近の活動", dashConflicts: "確認が必要な矛盾", dashUnavailable: "利用不可", dashNoRecords: "データなし", dashLive: "ライブデータ", dashActive: "進行中", dashBlocked: "ブロック", dashQueued: "待機中", dashCompleted: "完了", dashPending: "保留中", dashAccepted: "承認", dashRejected: "却下", dashPlans: "計画", dashRecords: "記録", dashNodes: "ノード", dashRelations: "関係", dashHigh: "高", dashMedium: "中", dashLow: "低", dashCycles: "サイクル", dashRecent: "最近のイベント", dashEndpointUnavailable: "このローカルAPIエンドポイントは利用できません。", dashNoData: "記録されたデータはありません。",
    status: "研究インターフェース", statusOnline: "ローカル研究エンジンに接続済み",
    statusOffline: "ローカル研究エンジンに未接続",
    mission: "アイデアを研究し、検証し、確かめる。仮説と現実を決して混同しない。",
    agents: "研究エージェント", verification: "検証を最優先",
    discover: "何を発見しましたか？", working: "何に取り組んでいますか？",
    verified: "最新の検証済み結果", ready: "インターフェースの準備ができました。ローカルエンジンに接続すると研究データが表示されます。",
    footer: "ETDESSはSSSWETのフランス語訳です。公開結果は引き続き検証が必要です。",
    offline: "ローカル研究エンジンに接続されていません。GitHub Pagesは静的プレビューを表示します。",
    noDiscoveries: "研究結果はまだ保存されていません。", noActivity: "研究活動はまだ記録されていません。",
    noVerified: "独立して検証された知識はまだありません。",
    language: "言語", social: "SSSWETのソーシャルネットワーク", contact: "お問い合わせ"
  },
  ko: {
    name: "한국어", dir: "ltr", tagline: "Super Soldier Space Warping Engeriening Tech",
    dashboard: "글로벌 과학 대시보드", dashboardNote: "로컬 연구 엔진의 실시간 개요입니다. 연결되지 않은 항목은 명확하게 표시됩니다.", refresh: "새로고침",
    dashCampaigns: "연구 캠페인", dashResources: "자원 조정", dashTransfers: "지식 이전", dashExperiments: "실험", dashOptimization: "적응형 제안", dashGaps: "연구 공백", dashGraph: "지식 그래프", dashActivity: "최근 활동", dashConflicts: "검토할 모순", dashUnavailable: "사용 불가", dashNoRecords: "데이터 없음", dashLive: "실시간 데이터", dashActive: "활성", dashBlocked: "차단됨", dashQueued: "대기열", dashCompleted: "완료", dashPending: "대기 중", dashAccepted: "수락됨", dashRejected: "거부됨", dashPlans: "계획", dashRecords: "기록", dashNodes: "노드", dashRelations: "관계", dashHigh: "높음", dashMedium: "중간", dashLow: "낮음", dashCycles: "주기", dashRecent: "최근 이벤트", dashEndpointUnavailable: "이 로컬 API 엔드포인트를 사용할 수 없습니다.", dashNoData: "기록된 데이터가 없습니다.",
    status: "연구 인터페이스", statusOnline: "로컬 연구 엔진 연결됨",
    statusOffline: "로컬 연구 엔진 연결되지 않음",
    mission: "아이디어를 연구하고 시험하고 검증합니다. 가설을 현실과 혼동하지 않습니다.",
    agents: "연구 에이전트", verification: "검증 우선",
    discover: "무엇을 발견했나요?", working: "무엇을 연구하고 있나요?",
    verified: "최근 검증된 결과", ready: "인터페이스가 준비되었습니다. 실시간 연구 데이터를 보려면 로컬 엔진을 연결하세요.",
    footer: "ETDESS는 SSSWET의 프랑스어 번역입니다. 공개 결과는 검증이 필요합니다.",
    offline: "로컬 연구 엔진이 연결되지 않았습니다. GitHub Pages는 정적 미리보기를 표시합니다.",
    noDiscoveries: "저장된 연구 결과가 아직 없습니다.", noActivity: "기록된 연구 활동이 아직 없습니다.",
    noVerified: "독립적으로 검증된 지식이 아직 없습니다.",
    language: "언어", social: "SSSWET 소셜 네트워크", contact: "문의"
  },
  zh: {
    name: "中文", dir: "ltr", tagline: "Super Soldier Space Warping Engeriening Tech",
    dashboard: "全球科学仪表板", dashboardNote: "本地研究引擎的实时概览。不可用的连接会明确标示。", refresh: "刷新",
    dashCampaigns: "研究项目", dashResources: "资源协调", dashTransfers: "知识转移", dashExperiments: "实验", dashOptimization: "自适应提案", dashGaps: "研究空白", dashGraph: "知识图谱", dashActivity: "近期活动", dashConflicts: "待审查的矛盾", dashUnavailable: "不可用", dashNoRecords: "暂无记录", dashLive: "实时数据", dashActive: "进行中", dashBlocked: "已阻止", dashQueued: "排队中", dashCompleted: "已完成", dashPending: "待处理", dashAccepted: "已接受", dashRejected: "已拒绝", dashPlans: "计划", dashRecords: "记录", dashNodes: "节点", dashRelations: "关系", dashHigh: "高", dashMedium: "中", dashLow: "低", dashCycles: "周期", dashRecent: "近期事件", dashEndpointUnavailable: "此本地 API 端点不可用。", dashNoData: "尚无记录数据。",
    status: "研究界面", statusOnline: "本地研究引擎已连接",
    statusOffline: "本地研究引擎未连接",
    mission: "研究想法、测试想法、验证想法。绝不把假设与现实混为一谈。",
    agents: "研究代理", verification: "验证优先",
    discover: "你们发现了什么？", working: "你们正在研究什么？",
    verified: "最新已验证结果", ready: "界面已就绪。连接本地引擎即可显示实时研究数据。",
    footer: "ETDESS 是 SSSWET 的法语译名。公开结果仍需经过验证。",
    offline: "本地研究引擎尚未连接。GitHub Pages 当前显示静态预览。",
    noDiscoveries: "尚未保存研究结果。", noActivity: "尚未记录研究活动。",
    noVerified: "目前没有经过独立验证的知识。",
    language: "语言", social: "SSSWET 社交网络", contact: "联系"
  },
  hi: {
    name: "हिन्दी", dir: "ltr", tagline: "Super Soldier Space Warping Engeriening Tech",
    dashboard: "वैश्विक विज्ञान डैशबोर्ड", dashboardNote: "स्थानीय अनुसंधान इंजन का लाइव अवलोकन। अनुपलब्ध कनेक्शन स्पष्ट रूप से दिखाए जाते हैं।", refresh: "रीफ़्रेश",
    dashCampaigns: "अनुसंधान अभियान", dashResources: "संसाधन समन्वय", dashTransfers: "ज्ञान हस्तांतरण", dashExperiments: "प्रयोग", dashOptimization: "अनुकूली प्रस्ताव", dashGaps: "अनुसंधान अंतराल", dashGraph: "ज्ञान ग्राफ", dashActivity: "हाल की गतिविधि", dashConflicts: "समीक्षा हेतु विरोधाभास", dashUnavailable: "उपलब्ध नहीं", dashNoRecords: "कोई रिकॉर्ड नहीं", dashLive: "लाइव डेटा", dashActive: "सक्रिय", dashBlocked: "अवरुद्ध", dashQueued: "कतार में", dashCompleted: "पूर्ण", dashPending: "लंबित", dashAccepted: "स्वीकृत", dashRejected: "अस्वीकृत", dashPlans: "योजनाएँ", dashRecords: "रिकॉर्ड", dashNodes: "नोड", dashRelations: "संबंध", dashHigh: "उच्च", dashMedium: "मध्यम", dashLow: "निम्न", dashCycles: "चक्र", dashRecent: "हाल की घटनाएँ", dashEndpointUnavailable: "यह स्थानीय API एंडपॉइंट उपलब्ध नहीं है।", dashNoData: "कोई डेटा दर्ज नहीं है।",
    status: "अनुसंधान इंटरफ़ेस", statusOnline: "स्थानीय अनुसंधान इंजन जुड़ा हुआ है",
    statusOffline: "स्थानीय अनुसंधान इंजन जुड़ा नहीं है",
    mission: "विचारों पर शोध करें। उनका परीक्षण करें। सत्यापन करें। परिकल्पना को वास्तविकता न समझें।",
    agents: "अनुसंधान एजेंट", verification: "सत्यापन सर्वोपरि",
    discover: "आपने क्या खोजा?", working: "आप किस पर काम कर रहे हैं?",
    verified: "नवीनतम सत्यापित परिणाम", ready: "इंटरफ़ेस तैयार है। लाइव शोध डेटा देखने के लिए स्थानीय इंजन कनेक्ट करें।",
    footer: "ETDESS, SSSWET का फ्रांसीसी अनुवाद है। सार्वजनिक परिणामों का सत्यापन आवश्यक है।",
    offline: "स्थानीय अनुसंधान इंजन कनेक्ट नहीं है। GitHub Pages स्थिर पूर्वावलोकन दिखाता है।",
    noDiscoveries: "अभी तक कोई शोध परिणाम सहेजा नहीं गया है।", noActivity: "अभी तक कोई शोध गतिविधि दर्ज नहीं हुई है।",
    noVerified: "अभी तक स्वतंत्र रूप से सत्यापित ज्ञान उपलब्ध नहीं है।",
    language: "भाषा", social: "SSSWET सोशल नेटवर्क", contact: "संपर्क"
  }
};


/* Complete selectable language catalogue. Interface strings not yet translated use the English fallback. */
window.SSSWET_LANGUAGE_CATALOG = [
"af|Afrikaans","sq|Shqip","de|Deutsch","am|አማርኛ","en|English","ar|العربية","hy|Հայերեն","as|অসমীয়া","ay|Aymar aru","az|Azərbaycanca","bm|Bamanankan","bn|বাংলা","bho|भोजपुरी","be|Беларуская","my|မြန်မာ","bs|Bosanski","br|Brezhoneg","bg|Български","yue|粵語","ca|Català","ceb|Cebuano","ny|Chichewa","zh-CN|简体中文","zh-TW|繁體中文","si|සිංහල","ko|한국어","co|Corsu","ht|Kreyòl ayisyen","hr|Hrvatski","da|Dansk","dv|ދިވެހި","doi|डोगरी","es|Español","eo|Esperanto","et|Eesti","ee|Eʋegbe","fi|Suomi","fon|Fɔngbè","fr|Français","fy|Frysk","gd|Gàidhlig","gl|Galego","cy|Cymraeg","ka|ქართული","el|Ελληνικά","gn|Avañe'ẽ","gu|ગુજરાતી","ha|Hausa","haw|ʻŌlelo Hawaiʻi","he|עברית","hi|हिन्दी","hmn|Hmoob","hu|Magyar","ig|Asụsụ Igbo","ilo|Ilokano","id|Bahasa Indonesia","ga|Gaeilge","is|Íslenska","it|Italiano","ja|日本語","jv|Basa Jawa","kn|ಕನ್ನಡ","kk|Қазақша","km|ខ្មែរ","rw|Ikinyarwanda","kok|कोंकणी","kri|Krio","ku|Kurdî (Kurmancî)","ckb|کوردیی ناوەندی","ky|Кыргызча","lo|ລາວ","la|Latina","lv|Latviešu","ln|Lingála","lt|Lietuvių","lg|Luganda","lb|Lëtzebuergesch","mk|Македонски","mai|मैथिली","mg|Malagasy","ms|Bahasa Melayu","ml|മലയാളം","mt|Malti","mi|Māori","mr|मराठी","mni|মৈতৈলোন্","lus|Mizo ṭawng","mn|Монгол","nl|Nederlands","ne|नेपाली","no|Norsk","oc|Occitan","or|ଓଡ଼ିଆ","om|Afaan Oromoo","uz|Oʻzbekcha","ug|ئۇيغۇرچە","ps|پښتو","pa|ਪੰਜਾਬੀ","fa|فارسی","pl|Polski","pt|Português","qu|Runa Simi","ro|Română","ru|Русский","sa|संस्कृतम्","sm|Gagana Sāmoa","sg|Sängö","sr|Српски","st|Sesotho","sn|chiShona","sd|سنڌي","sk|Slovenčina","sl|Slovenščina","so|Soomaali","su|Basa Sunda","sv|Svenska","sw|Kiswahili","tg|Тоҷикӣ","ta|தமிழ்","tt|Татарча","cs|Čeština","te|తెలుగు","th|ไทย","bo|བོད་སྐད་","ti|ትግርኛ","ts|Xitsonga","tr|Türkçe","tk|Türkmençe","tw|Twi","uk|Українська","ur|اردو","vi|Tiếng Việt","xh|isiXhosa","yi|ייִדיש","yo|Yorùbá","zu|isiZulu","ab|Аҧсуа","aa|Qafár af","ace|Bahsa Acèh","ban|Basa Bali","btx|Batak Karo","bts|Batak Simalungun","bbc|Batak Toba","bci|Wawle","bem|Ichibemba","eu|Euskara","bxr|Буряад хэлэн","ce|Нохчийн","crs|Kreol Seselwa","mfe|Kreol Morisien","kg|Kikongo","luo|Dholuo","gv|Gaelg","pap|Papiamentu","ber|Tamaziɣt","tpi|Tok Pisin","fr-CA|Français canadien / québécois","fur|Furlan","gsw|Südfränkisch","crh|Qırımtatarca","ca-valencia|Valencià","ach|Lwo","alz|Alur","chr|ᏣᎳᎩ","din|Thuɔŋjäŋ","dmk|Dombe","dyu|Julakan","ff|Fulfulde","gaa|Gã","nqo|ߒߞߏ","ss|SiSwati","ve|Tshivenḓa","wo|Wolof","av|МагӀарул мацӀ","awa|अवधी","bal|بلوچی","ba|Башҡортса","bew|Betawi","bik|Bikol","prs|دری","dz|རྫོང་ཁ","cnh|Laiṭong","hil|Ilonggo","os|Ирон","pnb|پنجابی (شاہ مکھی)","cv|Чӑвашла","ch|Chamoru","chk|Chuukese","fj|Vosa Vakaviti","hrx|Hunsrik"
]; 
for (const item of window.SSSWET_LANGUAGE_CATALOG) {
  const [code, name] = item.split("|");
  if (!window.SSSWET_LOCALES[code]) window.SSSWET_LOCALES[code] = { name, dir: /^(ar|he|dv|ckb|fa|ps|ur|ug|sd|nqo|prs|bal|pnb)$/.test(code) ? "rtl" : "ltr" };
}


/* Additional interface translations. Specialized research terminology falls back to English until reviewed. */
const SSSWET_EN = window.SSSWET_LOCALES.en;
window.SSSWET_LOCALES.id = {
  ...SSSWET_EN, name: "Bahasa Indonesia", dir: "ltr",
  tagline: "Teknologi Perang Antariksa Pelengkungan Ruang Prajurit Super",
  status: "ANTARMUKA PENELITIAN", statusOnline: "MESIN PENELITIAN LOKAL TERHUBUNG",
  statusOffline: "MESIN PENELITIAN LOKAL TIDAK TERHUBUNG",
  mission: "Teliti gagasan. Uji. Verifikasi. Jangan pernah menyamakan hipotesis dengan kenyataan.",
  agents: "Agen penelitian", verification: "utamakan verifikasi",
  discover: "Apa yang ditemukan?", working: "Apa yang sedang dikerjakan?",
  verified: "Hasil terverifikasi terbaru", ready: "Antarmuka siap. Hubungkan mesin lokal untuk menampilkan data penelitian langsung.",
  footer: "ETDESS adalah terjemahan bahasa Prancis dari SSSWET. Hasil publik tetap harus diverifikasi.",
  offline: "Mesin penelitian lokal belum terhubung. GitHub Pages adalah pratinjau statis; jalankan aplikasi lokal untuk data langsung.",
  noDiscoveries: "Belum ada hasil penelitian yang tersimpan.", noActivity: "Belum ada aktivitas penelitian yang tercatat.",
  noVerified: "Belum ada pengetahuan yang diverifikasi secara independen.",
  language: "Bahasa", social: "Media sosial SSSWET", contact: "Kontak",
  dashboard: "Dasbor sains global", dashboardNote: "Ringkasan langsung dari mesin penelitian lokal. Koneksi yang tidak tersedia ditampilkan secara jelas.", refresh: "Muat ulang",
  timelineTitle: "Riwayat penelitian", timelineFilter: "Kampanye", allCampaigns: "Semua kampanye",
  timelineSearchLabel: "Cari riwayat", timelineSearchPlaceholder: "Cari judul, deskripsi, atau referensi",
  timelineTypeFilter: "Jenis peristiwa", allEventTypes: "Semua jenis peristiwa", timelineNoMatches: "Tidak ada peristiwa yang cocok dengan filter ini.",
  timelineCaption: "Perubahan yang tercatat secara kronologis. Linimasa bukan validasi ilmiah.",
  timelineEmpty: "Belum ada peristiwa penelitian bertanggal."
};
window.SSSWET_LOCALES.tr = {
  ...SSSWET_EN, name: "Türkçe", dir: "ltr",
  tagline: "Süper Asker Uzay Bükme Savaş Teknolojisi",
  status: "ARAŞTIRMA ARAYÜZÜ", statusOnline: "YEREL ARAŞTIRMA MOTORU BAĞLI",
  statusOffline: "YEREL ARAŞTIRMA MOTORU BAĞLI DEĞİL",
  mission: "Fikirleri araştır. Test et. Doğrula. Bir hipotezi asla gerçekle karıştırma.",
  agents: "Araştırma ajanları", verification: "önce doğrulama",
  discover: "Ne keşfettiniz?", working: "Ne üzerinde çalışıyorsunuz?",
  verified: "En son doğrulanmış sonuçlar", ready: "Arayüz hazır. Canlı araştırma verilerini görüntülemek için yerel motoru bağlayın.",
  footer: "ETDESS, SSSWET'in Fransızca çevirisidir. Herkese açık sonuçlar doğrulamaya tabidir.",
  offline: "Yerel araştırma motoru bağlı değil. GitHub Pages statik bir önizlemedir; canlı araştırma verileri için uygulamayı yerel olarak çalıştırın.",
  noDiscoveries: "Henüz araştırma çıktısı kaydedilmedi.", noActivity: "Henüz araştırma etkinliği kaydedilmedi.",
  noVerified: "Henüz bağımsız olarak doğrulanmış bilgi bulunmuyor.",
  language: "Dil", social: "SSSWET sosyal medya", contact: "İletişim",
  dashboard: "Küresel bilim panosu", dashboardNote: "Yerel araştırma motorundan canlı genel bakış. Eksik bağlantılar açıkça gösterilir.", refresh: "Yenile",
  timelineTitle: "Araştırma geçmişi", timelineFilter: "Kampanya", allCampaigns: "Tüm kampanyalar",
  timelineSearchLabel: "Geçmişte ara", timelineSearchPlaceholder: "Başlık, açıklama veya referans ara",
  timelineTypeFilter: "Olay türü", allEventTypes: "Tüm olay türleri", timelineNoMatches: "Bu filtrelerle eşleşen olay yok.",
  timelineCaption: "Kronolojik sırayla kaydedilen değişiklikler. Zaman çizelgesi bilimsel doğrulama değildir.",
  timelineEmpty: "Tarihli araştırma olayı bulunmuyor."
};
window.SSSWET_LOCALES.pl = {
  ...SSSWET_EN, name: "Polski", dir: "ltr",
  tagline: "Technologia Wojny Kosmicznej z Zakrzywianiem Przestrzeni Superżołnierzy",
  status: "INTERFEJS BADAWCZY", statusOnline: "LOKALNY SILNIK BADAWCZY POŁĄCZONY",
  statusOffline: "LOKALNY SILNIK BADAWCZY NIE JEST POŁĄCZONY",
  mission: "Badaj pomysły. Testuj je. Weryfikuj. Nigdy nie myl hipotezy z rzeczywistością.",
  agents: "Agenci badawczy", verification: "najpierw weryfikacja",
  discover: "Co udało się odkryć?", working: "Nad czym obecnie pracujesz?",
  verified: "Najnowsze zweryfikowane wyniki", ready: "Interfejs jest gotowy. Połącz lokalny silnik, aby wyświetlać bieżące dane badawcze.",
  footer: "ETDESS to francuskie tłumaczenie nazwy SSSWET. Wyniki publiczne nadal wymagają weryfikacji.",
  offline: "Lokalny silnik badawczy nie jest połączony. GitHub Pages to statyczny podgląd; uruchom aplikację lokalnie, aby korzystać z bieżących danych.",
  noDiscoveries: "Nie zapisano jeszcze żadnych wyników badań.", noActivity: "Nie odnotowano jeszcze aktywności badawczej.",
  noVerified: "Brak wiedzy zweryfikowanej niezależnie.",
  language: "Język", social: "Media społecznościowe SSSWET", contact: "Kontakt",
  dashboard: "Globalny panel naukowy", dashboardNote: "Bieżący przegląd z lokalnego silnika badawczego. Brakujące połączenia są wyraźnie oznaczone.", refresh: "Odśwież",
  timelineTitle: "Historia badań", timelineFilter: "Kampania", allCampaigns: "Wszystkie kampanie",
  timelineSearchLabel: "Przeszukaj historię", timelineSearchPlaceholder: "Szukaj tytułów, opisów lub odnośników",
  timelineTypeFilter: "Rodzaj zdarzenia", allEventTypes: "Wszystkie rodzaje zdarzeń", timelineNoMatches: "Żadne zdarzenia nie pasują do tych filtrów.",
  timelineCaption: "Zarejestrowane zmiany w porządku chronologicznym. Oś czasu nie stanowi walidacji naukowej.",
  timelineEmpty: "Brak dostępnych datowanych zdarzeń badawczych."
};
window.SSSWET_LOCALES.bn = {
  ...SSSWET_EN, name: "বাংলা", dir: "ltr",
  tagline: "সুপার সোলজার স্পেস ওয়ার্পিং ইঞ্জিনিয়ারিং টেক",
  status: "গবেষণা ইন্টারফেস", statusOnline: "স্থানীয় গবেষণা ইঞ্জিন সংযুক্ত",
  statusOffline: "স্থানীয় গবেষণা ইঞ্জিন সংযুক্ত নয়",
  mission: "ধারণা নিয়ে গবেষণা করুন। পরীক্ষা করুন। যাচাই করুন। অনুমানকে কখনো বাস্তবতার সঙ্গে গুলিয়ে ফেলবেন না।",
  agents: "গবেষণা এজেন্ট", verification: "যাচাই অগ্রাধিকার",
  discover: "কী আবিষ্কার হয়েছে?", working: "আপনি কী নিয়ে কাজ করছেন?",
  verified: "সর্বশেষ যাচাইকৃত ফলাফল", ready: "ইন্টারফেস প্রস্তুত। সরাসরি গবেষণার তথ্য দেখতে স্থানীয় ইঞ্জিন সংযুক্ত করুন।",
  footer: "ETDESS হলো SSSWET-এর ফরাসি অনুবাদ। প্রকাশ্য ফলাফল যাচাইসাপেক্ষ।",
  offline: "স্থানীয় গবেষণা ইঞ্জিন সংযুক্ত নয়। GitHub Pages একটি স্থির প্রিভিউ; সরাসরি গবেষণার তথ্যের জন্য স্থানীয় অ্যাপ চালু করুন।",
  noDiscoveries: "এখনও কোনো গবেষণার ফল সংরক্ষিত হয়নি।", noActivity: "এখনও কোনো গবেষণা কার্যক্রম নথিভুক্ত হয়নি।",
  noVerified: "এখনও স্বাধীনভাবে যাচাইকৃত কোনো জ্ঞান উপলব্ধ নেই।",
  language: "ভাষা", social: "SSSWET সামাজিক মাধ্যম", contact: "যোগাযোগ",
  dashboard: "বৈশ্বিক বিজ্ঞান ড্যাশবোর্ড", dashboardNote: "স্থানীয় গবেষণা ইঞ্জিনের সরাসরি সারসংক্ষেপ। অনুপস্থিত সংযোগ স্পষ্টভাবে দেখানো হয়।", refresh: "রিফ্রেশ",
  timelineTitle: "গবেষণার ইতিহাস", timelineFilter: "ক্যাম্পেইন", allCampaigns: "সব ক্যাম্পেইন",
  timelineSearchLabel: "ইতিহাস খুঁজুন", timelineSearchPlaceholder: "শিরোনাম, বিবরণ বা রেফারেন্স খুঁজুন",
  timelineTypeFilter: "ঘটনার ধরন", allEventTypes: "সব ধরনের ঘটনা", timelineNoMatches: "এই ফিল্টারের সঙ্গে মেলে এমন কোনো ঘটনা নেই।",
  timelineCaption: "কালানুক্রমিকভাবে নথিভুক্ত পরিবর্তন। টাইমলাইন বৈজ্ঞানিক যাচাই নয়।",
  timelineEmpty: "তারিখসহ কোনো গবেষণা ঘটনা উপলব্ধ নেই।"
};
window.SSSWET_LOCALES.sw = {
  ...SSSWET_EN, name: "Kiswahili", dir: "ltr",
  tagline: "Teknolojia ya Vita vya Anga na Kupinda Nafasi ya Askari Bingwa",
  status: "KIUNGANISHI CHA UTAFITI", statusOnline: "MFUMO WA UTAFITI WA NDANI UMEUNGANISHWA",
  statusOffline: "MFUMO WA UTAFITI WA NDANI HAUJAUNGANISHWA",
  mission: "Chunguza mawazo. Yajaribu. Yathibitishe. Usichanganye kamwe dhana na ukweli.",
  agents: "Wakala wa utafiti", verification: "uthibitishaji kwanza",
  discover: "Umegundua nini?", working: "Unafanyia kazi nini?",
  verified: "Matokeo ya hivi karibuni yaliyothibitishwa", ready: "Kiolesura kiko tayari. Unganisha mfumo wa ndani ili kuonyesha data hai ya utafiti.",
  footer: "ETDESS ni tafsiri ya Kifaransa ya SSSWET. Matokeo ya umma bado yanahitaji uthibitishaji.",
  offline: "Mfumo wa utafiti wa ndani haujaunganishwa. GitHub Pages ni onyesho tuli; endesha programu ya ndani ili kupata data hai ya utafiti.",
  noDiscoveries: "Bado hakuna matokeo ya utafiti yaliyohifadhiwa.", noActivity: "Bado hakuna shughuli za utafiti zilizorekodiwa.",
  noVerified: "Bado hakuna maarifa yaliyothibitishwa kwa kujitegemea.",
  language: "Lugha", social: "Mitandao ya kijamii ya SSSWET", contact: "Mawasiliano",
  dashboard: "Dashibodi ya sayansi ya kimataifa", dashboardNote: "Muhtasari wa moja kwa moja kutoka kwenye mfumo wa utafiti wa ndani. Miunganisho inayokosekana huonyeshwa wazi.", refresh: "Onyesha upya",
  timelineTitle: "Historia ya utafiti", timelineFilter: "Kampeni", allCampaigns: "Kampeni zote",
  timelineSearchLabel: "Tafuta historia", timelineSearchPlaceholder: "Tafuta vichwa, maelezo au marejeo",
  timelineTypeFilter: "Aina ya tukio", allEventTypes: "Aina zote za matukio", timelineNoMatches: "Hakuna matukio yanayolingana na vichujio hivi.",
  timelineCaption: "Mabadiliko yaliyorekodiwa kwa mpangilio wa muda. Ratiba si uthibitisho wa kisayansi.",
  timelineEmpty: "Hakuna matukio ya utafiti yenye tarehe yanayopatikana."
};

/* Localized first-load introduction for the research roles. */
window.SSSWET_AGENT_COPY = {
  "en": {
    "welcome": "Welcome to SSSWET.",
    "summary": "A research coordination environment for exploring ideas, planning studies, comparing evidence and documenting uncertainty. Hypotheses, simulations and recorded observations remain distinct from independently verified findings.",
    "roles": [
      [
        "Research coordination",
        "Organizes questions, campaigns, milestones and next steps."
      ],
      [
        "Evidence and methods",
        "Tracks sources, protocols, comparisons, limitations and reproducibility."
      ],
      [
        "Integrity and review",
        "Flags missing information, discrepancies and risks requiring qualified human review."
      ]
    ],
    "steps": [
      "Define a question and its scope.",
      "Review sources, assumptions and existing evidence.",
      "Prepare a documented protocol and reproducible plan.",
      "Record observations or simulation outputs with provenance.",
      "Compare results, assess uncertainty and limitations.",
      "Submit interpretations and safety or ethics issues for human review."
    ],
    "questions": [
      "What are you working on right now?",
      "What evidence and sources are recorded?",
      "What needs verification or human review?"
    ],
    "disclaimer": "These are defined project roles, not proof that autonomous AI agents are currently running. Live activity requires the local research engine. GitHub Pages is a static preview."
  },
  "fr": {
    "welcome": "Bienvenue dans SSSWET.",
    "summary": "Un environnement de coordination de la recherche pour explorer des idées, préparer des études, comparer les preuves et documenter les incertitudes. Les hypothèses, simulations et observations enregistrées restent distinctes des résultats vérifiés indépendamment.",
    "roles": [
      [
        "Coordination de la recherche",
        "Organise les questions, campagnes, étapes et prochaines pistes."
      ],
      [
        "Preuves et méthodes",
        "Suit les sources, protocoles, comparaisons, limites et reproductibilité."
      ],
      [
        "Intégrité et examen",
        "Signale les informations manquantes, divergences et risques nécessitant un examen humain qualifié."
      ]
    ],
    "steps": [
      "Définir une question et son périmètre.",
      "Examiner les sources, hypothèses et preuves existantes.",
      "Préparer un protocole documenté et un plan reproductible.",
      "Enregistrer les observations ou simulations avec leur provenance.",
      "Comparer les résultats, évaluer les incertitudes et les limites.",
      "Soumettre les interprétations et questions de sécurité ou d’éthique à un examen humain."
    ],
    "questions": [
      "Sur quoi travaillez-vous actuellement ?",
      "Quelles preuves et sources sont enregistrées ?",
      "Que faut-il vérifier ou soumettre à un examen humain ?"
    ],
    "disclaimer": "Ces rôles sont définis pour le projet ; cela ne signifie pas que des agents IA autonomes fonctionnent déjà. L’activité en direct nécessite le moteur local. GitHub Pages est un aperçu statique."
  },
  "es": {
    "welcome": "Te damos la bienvenida a SSSWET.",
    "summary": "Un entorno de coordinación de investigación para explorar ideas, planificar estudios, comparar pruebas y documentar incertidumbres. Las hipótesis, simulaciones y observaciones registradas se distinguen de los resultados verificados independientemente.",
    "roles": [
      [
        "Coordinación de investigación",
        "Organiza preguntas, campañas, etapas y próximos pasos."
      ],
      [
        "Pruebas y métodos",
        "Registra fuentes, protocolos, comparaciones, límites y reproducibilidad."
      ],
      [
        "Integridad y revisión",
        "Señala datos faltantes, discrepancias y riesgos que requieren revisión humana cualificada."
      ]
    ],
    "steps": [
      "Definir una pregunta y su alcance.",
      "Revisar fuentes, supuestos y pruebas existentes.",
      "Preparar un protocolo documentado y un plan reproducible.",
      "Registrar observaciones o simulaciones con su procedencia.",
      "Comparar resultados y evaluar incertidumbres y límites.",
      "Someter interpretaciones y cuestiones de seguridad o ética a revisión humana."
    ],
    "questions": [
      "¿En qué estáis trabajando ahora?",
      "¿Qué pruebas y fuentes están registradas?",
      "¿Qué requiere verificación o revisión humana?"
    ],
    "disclaimer": "Estos son roles definidos del proyecto, no una afirmación de que haya agentes autónomos activos. La actividad en directo requiere el motor local. GitHub Pages es una vista previa estática."
  },
  "de": {
    "welcome": "Willkommen bei SSSWET.",
    "summary": "Eine Forschungsumgebung zur Koordination von Ideen, Studienplanung, Evidenzvergleichen und Unsicherheitsdokumentation. Hypothesen, Simulationen und aufgezeichnete Beobachtungen bleiben von unabhängig überprüften Ergebnissen getrennt.",
    "roles": [
      [
        "Forschungskoordination",
        "Organisiert Fragen, Kampagnen, Meilensteine und nächste Schritte."
      ],
      [
        "Evidenz und Methoden",
        "Erfasst Quellen, Protokolle, Vergleiche, Einschränkungen und Reproduzierbarkeit."
      ],
      [
        "Integrität und Prüfung",
        "Meldet fehlende Informationen, Abweichungen und Risiken für eine qualifizierte menschliche Prüfung."
      ]
    ],
    "steps": [
      "Frage und Umfang festlegen.",
      "Quellen, Annahmen und vorhandene Evidenz prüfen.",
      "Dokumentiertes Protokoll und reproduzierbaren Plan erstellen.",
      "Beobachtungen oder Simulationen samt Herkunft erfassen.",
      "Ergebnisse vergleichen und Unsicherheit sowie Grenzen bewerten.",
      "Interpretationen und Sicherheits- oder Ethikfragen menschlich prüfen lassen."
    ],
    "questions": [
      "Woran arbeitet ihr gerade?",
      "Welche Belege und Quellen sind erfasst?",
      "Was muss überprüft oder menschlich begutachtet werden?"
    ],
    "disclaimer": "Dies sind definierte Projektrollen und keine Behauptung aktiver autonomer KI-Agenten. Live-Aktivitäten erfordern die lokale Forschungs-Engine. GitHub Pages ist eine statische Vorschau."
  },
  "it": {
    "welcome": "Benvenuto in SSSWET.",
    "summary": "Un ambiente di coordinamento della ricerca per esplorare idee, pianificare studi, confrontare prove e documentare incertezze. Ipotesi, simulazioni e osservazioni registrate restano distinte dai risultati verificati in modo indipendente.",
    "roles": [
      [
        "Coordinamento della ricerca",
        "Organizza domande, campagne, tappe e attività successive."
      ],
      [
        "Prove e metodi",
        "Traccia fonti, protocolli, confronti, limiti e riproducibilità."
      ],
      [
        "Integrità e revisione",
        "Segnala informazioni mancanti, discrepanze e rischi da sottoporre a revisione umana qualificata."
      ]
    ],
    "steps": [
      "Definire una domanda e il suo ambito.",
      "Esaminare fonti, ipotesi e prove disponibili.",
      "Preparare un protocollo documentato e un piano riproducibile.",
      "Registrare osservazioni o simulazioni con la relativa provenienza.",
      "Confrontare i risultati e valutare incertezze e limiti.",
      "Sottoporre interpretazioni e questioni di sicurezza o etica a revisione umana."
    ],
    "questions": [
      "Su cosa state lavorando adesso?",
      "Quali prove e fonti sono registrate?",
      "Che cosa richiede verifica o revisione umana?"
    ],
    "disclaimer": "Questi sono ruoli definiti del progetto, non la prova che agenti IA autonomi siano attivi. L'attività in tempo reale richiede il motore locale. GitHub Pages è un'anteprima statica."
  },
  "pt": {
    "welcome": "Boas-vindas ao SSSWET.",
    "summary": "Um ambiente de coordenação de pesquisa para explorar ideias, planejar estudos, comparar evidências e documentar incertezas. Hipóteses, simulações e observações registradas permanecem distintas de resultados verificados de forma independente.",
    "roles": [
      [
        "Coordenação da pesquisa",
        "Organiza perguntas, campanhas, etapas e próximos passos."
      ],
      [
        "Evidências e métodos",
        "Acompanha fontes, protocolos, comparações, limitações e reprodutibilidade."
      ],
      [
        "Integridade e revisão",
        "Sinaliza informações ausentes, divergências e riscos que exigem revisão humana qualificada."
      ]
    ],
    "steps": [
      "Definir uma pergunta e seu escopo.",
      "Analisar fontes, pressupostos e evidências existentes.",
      "Preparar um protocolo documentado e um plano reproduzível.",
      "Registrar observações ou simulações com sua procedência.",
      "Comparar resultados e avaliar incertezas e limitações.",
      "Encaminhar interpretações e questões de segurança ou ética para revisão humana."
    ],
    "questions": [
      "Em que vocês estão trabalhando agora?",
      "Quais evidências e fontes estão registradas?",
      "O que precisa de verificação ou revisão humana?"
    ],
    "disclaimer": "Estas são funções definidas para o projeto, não uma afirmação de que agentes autônomos de IA estejam ativos. A atividade ao vivo exige o mecanismo local. O GitHub Pages é uma prévia estática."
  },
  "nl": {
    "welcome": "Welkom bij SSSWET.",
    "summary": "Een onderzoeksomgeving voor het verkennen van ideeën, plannen van studies, vergelijken van bewijs en documenteren van onzekerheid. Hypothesen, simulaties en vastgelegde waarnemingen blijven onderscheiden van onafhankelijk geverifieerde resultaten.",
    "roles": [
      [
        "Onderzoekscoördinatie",
        "Organiseert vragen, campagnes, mijlpalen en vervolgstappen."
      ],
      [
        "Bewijs en methoden",
        "Volgt bronnen, protocollen, vergelijkingen, beperkingen en reproduceerbaarheid."
      ],
      [
        "Integriteit en beoordeling",
        "Signaleert ontbrekende informatie, afwijkingen en risico's die deskundige menselijke beoordeling vereisen."
      ]
    ],
    "steps": [
      "Bepaal een vraag en de reikwijdte.",
      "Beoordeel bronnen, aannames en bestaand bewijs.",
      "Maak een gedocumenteerd protocol en reproduceerbaar plan.",
      "Leg waarnemingen of simulaties met herkomst vast.",
      "Vergelijk resultaten en beoordeel onzekerheid en beperkingen.",
      "Leg interpretaties en veiligheids- of ethische kwesties voor aan mensen."
    ],
    "questions": [
      "Waar werken jullie momenteel aan?",
      "Welk bewijs en welke bronnen zijn vastgelegd?",
      "Wat moet worden geverifieerd of menselijk beoordeeld?"
    ],
    "disclaimer": "Dit zijn gedefinieerde projectrollen, geen bewering dat autonome AI-agenten actief zijn. Live activiteit vereist de lokale onderzoeksengine. GitHub Pages is een statische preview."
  },
  "ru": {
    "welcome": "Добро пожаловать в SSSWET.",
    "summary": "Исследовательская среда для изучения идей, планирования исследований, сопоставления доказательств и документирования неопределённости. Гипотезы, симуляции и записанные наблюдения отделены от независимо проверенных результатов.",
    "roles": [
      [
        "Координация исследований",
        "Организует вопросы, кампании, этапы и дальнейшие задачи."
      ],
      [
        "Доказательства и методы",
        "Отслеживает источники, протоколы, сравнения, ограничения и воспроизводимость."
      ],
      [
        "Добросовестность и проверка",
        "Выявляет пробелы, расхождения и риски для квалифицированной проверки человеком."
      ]
    ],
    "steps": [
      "Сформулировать вопрос и определить его границы.",
      "Изучить источники, допущения и имеющиеся данные.",
      "Подготовить документированный протокол и воспроизводимый план.",
      "Записать наблюдения или результаты моделирования с указанием происхождения.",
      "Сравнить результаты, оценить неопределённость и ограничения.",
      "Передать интерпретации и вопросы безопасности или этики на проверку человеку."
    ],
    "questions": [
      "Над чем вы сейчас работаете?",
      "Какие доказательства и источники зарегистрированы?",
      "Что требует проверки или участия человека?"
    ],
    "disclaimer": "Это определённые роли проекта, а не утверждение о работе автономных ИИ-агентов. Текущая активность требует локального исследовательского движка. GitHub Pages — статический просмотр."
  },
  "uk": {
    "welcome": "Вітаємо у SSSWET.",
    "summary": "Середовище координації досліджень для вивчення ідей, планування досліджень, порівняння доказів і документування невизначеності. Гіпотези, симуляції та зафіксовані спостереження відокремлені від незалежно перевірених результатів.",
    "roles": [
      [
        "Координація досліджень",
        "Організовує запитання, кампанії, етапи та наступні кроки."
      ],
      [
        "Докази й методи",
        "Відстежує джерела, протоколи, порівняння, обмеження та відтворюваність."
      ],
      [
        "Доброчесність і перевірка",
        "Позначає прогалини, розбіжності й ризики для фахового людського перегляду."
      ]
    ],
    "steps": [
      "Сформулювати запитання та визначити його межі.",
      "Переглянути джерела, припущення й наявні докази.",
      "Підготувати документований протокол і відтворюваний план.",
      "Зафіксувати спостереження або результати моделювання з їхнім походженням.",
      "Порівняти результати, оцінити невизначеність та обмеження.",
      "Передати інтерпретації й питання безпеки чи етики на людський розгляд."
    ],
    "questions": [
      "Над чим ви зараз працюєте?",
      "Які докази та джерела зареєстровано?",
      "Що потребує перевірки або людського розгляду?"
    ],
    "disclaimer": "Це визначені ролі проєкту, а не твердження про роботу автономних ШІ-агентів. Поточна активність потребує локального дослідницького рушія. GitHub Pages — статичний попередній перегляд."
  },
  "ar": {
    "welcome": "مرحبًا بك في SSSWET.",
    "summary": "بيئة لتنسيق البحث واستكشاف الأفكار وتخطيط الدراسات ومقارنة الأدلة وتوثيق عدم اليقين. وتظل الفرضيات والمحاكاة والملاحظات المسجلة منفصلة عن النتائج التي جرى التحقق منها بشكل مستقل.",
    "roles": [
      [
        "تنسيق البحث",
        "ينظم الأسئلة والحملات والمراحل والخطوات التالية."
      ],
      [
        "الأدلة والمنهجيات",
        "يتتبع المصادر والبروتوكولات والمقارنات والقيود وقابلية إعادة الإنتاج."
      ],
      [
        "النزاهة والمراجعة",
        "يرصد المعلومات الناقصة والتباينات والمخاطر التي تتطلب مراجعة بشرية متخصصة."
      ]
    ],
    "steps": [
      "صياغة سؤال وتحديد نطاقه.",
      "مراجعة المصادر والافتراضات والأدلة المتاحة.",
      "إعداد بروتوكول موثق وخطة قابلة لإعادة الإنتاج.",
      "تسجيل الملاحظات أو نتائج المحاكاة مع مصدرها.",
      "مقارنة النتائج وتقييم عدم اليقين والقيود.",
      "إحالة التفسيرات ومسائل السلامة والأخلاقيات إلى مراجعة بشرية."
    ],
    "questions": [
      "ما الذي تعملون عليه الآن؟",
      "ما الأدلة والمصادر المسجلة؟",
      "ما الذي يحتاج إلى تحقق أو مراجعة بشرية؟"
    ],
    "disclaimer": "هذه أدوار محددة للمشروع وليست ادعاءً بعمل وكلاء ذكاء اصطناعي مستقلين. يتطلب النشاط المباشر محرك البحث المحلي. GitHub Pages معاينة ثابتة."
  },
  "he": {
    "welcome": "ברוכים הבאים ל-SSSWET.",
    "summary": "סביבת תיאום מחקר לחקר רעיונות, תכנון מחקרים, השוואת ראיות ותיעוד אי־ודאות. השערות, סימולציות ותצפיות מתועדות נשארות נפרדות מממצאים שאומתו באופן עצמאי.",
    "roles": [
      [
        "תיאום מחקר",
        "מארגן שאלות, קמפיינים, אבני דרך ושלבי המשך."
      ],
      [
        "ראיות ושיטות",
        "עוקב אחר מקורות, פרוטוקולים, השוואות, מגבלות ושחזוריות."
      ],
      [
        "יושרה ובקרה",
        "מזהה מידע חסר, פערים וסיכונים הדורשים בדיקה אנושית מקצועית."
      ]
    ],
    "steps": [
      "ניסוח שאלה והגדרת היקפה.",
      "בחינת מקורות, הנחות וראיות קיימות.",
      "הכנת פרוטוקול מתועד ותוכנית ניתנת לשחזור.",
      "תיעוד תצפיות או תוצאות סימולציה ומקורן.",
      "השוואת תוצאות והערכת אי־ודאות ומגבלות.",
      "העברת פרשנויות ושאלות בטיחות או אתיקה לבדיקה אנושית."
    ],
    "questions": [
      "על מה אתם עובדים כרגע?",
      "אילו ראיות ומקורות מתועדים?",
      "מה דורש אימות או בדיקה אנושית?"
    ],
    "disclaimer": "אלה תפקידי פרויקט מוגדרים, ולא טענה שסוכני AI אוטונומיים פועלים. פעילות בזמן אמת דורשת את מנוע המחקר המקומי. GitHub Pages הוא תצוגה מקדימה סטטית."
  },
  "ja": {
    "welcome": "SSSWETへようこそ。",
    "summary": "アイデアの探索、研究計画、証拠の比較、不確実性の記録を行う研究調整環境です。仮説、シミュレーション、記録された観察結果と独立して検証された結果を区別します。",
    "roles": [
      [
        "研究コーディネーション",
        "研究課題、キャンペーン、段階、次の作業を整理します。"
      ],
      [
        "証拠と方法",
        "情報源、プロトコル、比較、制約、再現性を追跡します。"
      ],
      [
        "研究公正とレビュー",
        "不足情報、相違点、人間の専門的確認が必要なリスクを示します。"
      ]
    ],
    "steps": [
      "問いと対象範囲を定める。",
      "情報源、前提条件、既存の証拠を確認する。",
      "文書化されたプロトコルと再現可能な計画を作成する。",
      "観察結果やシミュレーション出力を出所とともに記録する。",
      "結果を比較し、不確実性と限界を評価する。",
      "解釈や安全・倫理上の論点を人間の審査に提出する。"
    ],
    "questions": [
      "現在取り組んでいることは何ですか？",
      "どの証拠や情報源が記録されていますか？",
      "何を検証または人間による審査に回す必要がありますか？"
    ],
    "disclaimer": "これはプロジェクトで定義された役割であり、自律型AIエージェントが稼働中という意味ではありません。リアルタイムの活動にはローカル研究エンジンが必要です。GitHub Pagesは静的プレビューです。"
  },
  "ko": {
    "welcome": "SSSWET에 오신 것을 환영합니다.",
    "summary": "아이디어 탐색, 연구 계획, 증거 비교 및 불확실성 기록을 위한 연구 조정 환경입니다. 가설, 시뮬레이션, 기록된 관찰과 독립적으로 검증된 결과를 구분합니다.",
    "roles": [
      [
        "연구 조정",
        "연구 질문, 캠페인, 단계 및 다음 작업을 구성합니다."
      ],
      [
        "증거와 방법",
        "출처, 프로토콜, 비교, 한계 및 재현성을 추적합니다."
      ],
      [
        "연구 무결성과 검토",
        "누락 정보, 불일치 및 전문가의 인간 검토가 필요한 위험을 표시합니다."
      ]
    ],
    "steps": [
      "질문과 범위를 정의합니다.",
      "출처, 가정 및 기존 증거를 검토합니다.",
      "문서화된 프로토콜과 재현 가능한 계획을 준비합니다.",
      "관찰 또는 시뮬레이션 결과와 출처를 기록합니다.",
      "결과를 비교하고 불확실성과 한계를 평가합니다.",
      "해석 및 안전·윤리 문제를 인간 검토에 제출합니다."
    ],
    "questions": [
      "현재 무엇을 연구하고 있나요?",
      "어떤 증거와 출처가 기록되어 있나요?",
      "무엇을 검증하거나 사람이 검토해야 하나요?"
    ],
    "disclaimer": "이는 프로젝트에 정의된 역할이며 자율 AI 에이전트가 실행 중이라는 뜻은 아닙니다. 실시간 활동에는 로컬 연구 엔진 연결이 필요합니다. GitHub Pages는 정적 미리보기입니다."
  },
  "zh": {
    "welcome": "欢迎来到 SSSWET。",
    "summary": "这是一个研究协作环境，用于探索想法、规划研究、比较证据并记录不确定性。假设、模拟和已记录的观察与经过独立验证的结果保持区分。",
    "roles": [
      [
        "研究协调",
        "组织研究问题、研究活动、里程碑和后续步骤。"
      ],
      [
        "证据与方法",
        "跟踪来源、方案、比较、局限性和可重复性。"
      ],
      [
        "诚信与审查",
        "标记缺失信息、差异以及需要合格人员审查的风险。"
      ]
    ],
    "steps": [
      "提出问题并明确研究范围。",
      "审查来源、假设和现有证据。",
      "制定有记录的方案和可重复的研究计划。",
      "记录观察结果或模拟输出及其来源。",
      "比较结果，评估不确定性并识别局限。",
      "将解释以及安全或伦理问题提交人工审查。"
    ],
    "questions": [
      "你们目前正在研究什么？",
      "记录了哪些证据和来源？",
      "哪些内容需要验证或人工审查？"
    ],
    "disclaimer": "这些是项目定义的角色，并不表示自主 AI 代理目前正在运行。实时活动需要连接本地研究引擎。公开 GitHub Pages 界面是静态预览。"
  },
  "hi": {
    "welcome": "SSSWET में आपका स्वागत है।",
    "summary": "विचारों की खोज, अध्ययन की योजना, साक्ष्यों की तुलना और अनिश्चितता के दस्तावेज़ीकरण के लिए शोध समन्वय वातावरण। परिकल्पनाएँ, सिमुलेशन और दर्ज अवलोकन स्वतंत्र रूप से सत्यापित परिणामों से अलग रखे जाते हैं।",
    "roles": [
      [
        "शोध समन्वय",
        "शोध प्रश्नों, अभियानों, चरणों और अगले कार्यों का आयोजन करता है।"
      ],
      [
        "साक्ष्य और विधियाँ",
        "स्रोतों, प्रोटोकॉल, तुलनाओं, सीमाओं और पुनरुत्पादकता को दर्ज करता है।"
      ],
      [
        "अखंडता और समीक्षा",
        "अधूरी जानकारी, विसंगतियों और विशेषज्ञ मानवीय समीक्षा वाले जोखिमों को चिह्नित करता है।"
      ]
    ],
    "steps": [
      "प्रश्न तय करें और उसका दायरा निर्धारित करें।",
      "स्रोतों, मान्यताओं और मौजूदा साक्ष्यों की समीक्षा करें।",
      "दस्तावेज़ित प्रोटोकॉल और पुनरुत्पादित योजना तैयार करें।",
      "अवलोकनों या सिमुलेशन परिणामों को उनके स्रोत सहित दर्ज करें।",
      "परिणामों की तुलना करें और अनिश्चितता तथा सीमाओं का आकलन करें।",
      "व्याख्याओं तथा सुरक्षा या नैतिकता के प्रश्नों को मानवीय समीक्षा के लिए भेजें।"
    ],
    "questions": [
      "आप अभी किस पर काम कर रहे हैं?",
      "कौन से साक्ष्य और स्रोत दर्ज हैं?",
      "किस चीज़ को सत्यापन या मानवीय समीक्षा की आवश्यकता है?"
    ],
    "disclaimer": "ये परियोजना में निर्धारित भूमिकाएँ हैं; इसका अर्थ यह नहीं कि स्वायत्त AI एजेंट अभी चल रहे हैं। लाइव गतिविधि के लिए स्थानीय शोध इंजन आवश्यक है। GitHub Pages स्थिर पूर्वावलोकन है।"
  }
};
