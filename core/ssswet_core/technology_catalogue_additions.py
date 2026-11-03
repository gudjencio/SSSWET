"""Twelve curated research programmes added to the SSSWET portfolio.

These are research scopes, not validated technologies or operational products.
"""
from __future__ import annotations

ADDITIONAL_TECHNOLOGIES = [
    {"technology_id":"virtualTimeTravelMap","title":"Virtual Time Travel Mapping","domain":"society","subcategory":"spatiotemporalSystems","research_scope":["persistent local 3D geospatial mapping","consented video, audio and device-sensor capture","time-indexed event replay","trajectory and collision annotation","uncertainty-aware retrospective and forward scenario modelling"],"scientific_limitations":["Unrecorded past events cannot be recovered as observations; retrospective outputs are hypotheses constrained by evidence.","Future outputs are scenarios, not predictions with guaranteed accuracy.","Sensor data can be incomplete, biased, noisy or obstructed; bystanders' privacy and local recording laws must be respected."]},
    {"technology_id":"spatiotemporalDigitalTwin","title":"Spatiotemporal Digital Twin Systems","domain":"society","subcategory":"spatiotemporalSystems","research_scope":["time-indexed geospatial state models","versioned scene reconstruction","uncertainty propagation","multi-source sensor alignment"]},
    {"technology_id":"forensicSceneReconstruction","title":"Forensic Scene Reconstruction","domain":"protection","subcategory":"protectiveEngineering","research_scope":["evidence-preserving scene capture","object displacement and trajectory analysis","collision sequence hypotheses","chain-of-custody metadata"]},
    {"technology_id":"predictiveSceneSimulation","title":"Predictive Scene Simulation","domain":"robotics","subcategory":"autonomousResearch","research_scope":["short-horizon physical scenario simulation","explicit initial-condition recording","model comparison and error bounds","forecast calibration against later observations"]},
    {"technology_id":"geospatialSensorFusion","title":"Geospatial Sensor Fusion","domain":"society","subcategory":"spatiotemporalSystems","research_scope":["GNSS and inertial sensor fusion","camera pose estimation","coordinate-frame calibration","uncertainty-aware localization"]},
    {"technology_id":"persistent3DMapping","title":"Persistent 3D Environment Mapping","domain":"robotics","subcategory":"autonomousResearch","research_scope":["incremental 3D mapping","loop-closure and drift correction","change detection","user-controlled map retention"]},
    {"technology_id":"motionTrajectoryReconstruction","title":"Motion and Trajectory Reconstruction","domain":"robotics","subcategory":"autonomousResearch","research_scope":["multi-object tracking","trajectory smoothing","velocity and acceleration estimation","collision-event uncertainty"]},
    {"technology_id":"privacyPreservingCapture","title":"Privacy-Preserving Spatial Capture","domain":"society","subcategory":"spatiotemporalSystems","research_scope":["on-device processing","selective recording controls","face and voice redaction options","retention and deletion governance"]},
    {"technology_id":"environmentalEventReplay","title":"Environmental Event Replay","domain":"environment","subcategory":"climateResilience","research_scope":["weather and environmental sensor timelines","event annotation","sensor provenance","observed-versus-modelled state separation"]},
    {"technology_id":"uncertaintyAwareWorldModel","title":"Uncertainty-Aware World Models","domain":"society","subcategory":"spatiotemporalSystems","research_scope":["probabilistic scene state estimation","confidence interval visualization","alternative hypothesis comparison","calibration and model drift monitoring"]},
    {
        "technology_id": "sentientAI",
        "title": "Sentient AI",
        "domain": "society",
        "subcategory": "advancedComputing",
        "research_scope": [
            "Investigate competing scientific and philosophical theories of consciousness and their testable implications for artificial systems",
            "Study architectures and mechanisms associated with conscious-processing theories, including recurrent processing, global-workspace models and integrated information approaches, without treating any single theory as settled",
            "Develop operational evaluations that distinguish task competence, self-report, behavioural imitation, metacognition and other proposed indicators from evidence that could support or challenge claims of subjective experience",
            "Use mechanistic interpretability, controlled perturbations, adversarial tests and independent replication to examine whether internal processes match preregistered theoretical predictions",
            "Establish precautionary welfare review, monitoring, independent oversight and stop conditions before experiments that could plausibly create systems with morally relevant experiences"
        ],
        "scientific_limitations": [
            "No generally accepted test currently establishes whether an AI has subjective experience or consciousness",
            "Human-level performance, fluent self-reports, emotional language, self-models or behavioural resemblance do not by themselves demonstrate sentience",
            "Consciousness theories remain contested; results must report theory dependence, alternative explanations and uncertainty",
            "Research must not deliberately induce suffering or expose potentially sentient systems to harmful conditions; welfare review and independent ethical oversight are required",
            "Catalogue registration is a research objective only and does not claim that SSSWET has created, detected or validated a sentient AI"
        ]
    },
    {
        "technology_id": "humanLikeRobots",
        "title": "Human-like Robots",
        "domain": "robotics",
        "subcategory": "assistiveRobotics",
        "research_scope": [
            "Develop human-shaped or human-inspired robots for voluntary everyday assistance, accessibility, companionship, education, household support and collaborative work",
            "Study safe, expressive and context-appropriate communication, including clear disclosure that the robot is an artificial system and transparent limits on its capabilities",
            "Design human-centred mobility, manipulation and interaction with force, speed and workspace limits appropriate to the environment and nearby people or animals",
            "Integrate perception and navigation that prioritize collision avoidance, personal space, animal-aware movement, safe stopping and graceful shutdown",
            "Evaluate long-term reliability, maintainability, accessibility, privacy, cybersecurity, user consent and the social effects of human-robot relationships",
            "Explore optional interoperability with advanced conversational and potentially sentient AI research while keeping consciousness claims separate from robot appearance or social behaviour"
        ],
        "scientific_limitations": [
            "Human-like appearance, fluent conversation, emotional expression or apparent friendship do not establish consciousness, feelings or moral status",
            "No design may be intended to injure or kill humans or animals; harmful weaponization and attack functions are outside the programme",
            "Physical interaction requires validated risk assessment, emergency stops, force and speed limits, fail-safe states and independent safety testing",
            "Robots must identify themselves as artificial systems and must not use deceptive anthropomorphism to manipulate, coerce or exploit users",
            "Personal, biometric, household and conversational data require data minimization, informed consent, secure processing and user-controlled deletion",
            "Catalogue inclusion is a research objective, not evidence that a safe, generally capable or commercially available humanoid robot exists"
        ]
    }
]
