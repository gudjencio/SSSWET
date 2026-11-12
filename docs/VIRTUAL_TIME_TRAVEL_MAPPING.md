# Virtual Time Travel Mapping

## Purpose

Virtual Time Travel Mapping is an experimental, local-first SSSWET research programme. It combines persistent geospatial mapping, consent-based sensor capture, recorded-event replay, and explicitly uncertain models of intervals that were not recorded.

The web prototype is available at [Virtual Time Travel Mapping](../web/virtual-time-travel.html).

## What the prototype does

- Displays an interactive 3D-capable map using MapLibre GL JS and OpenFreeMap map tiles.
- Requests geolocation only after the user asks to locate or starts a scan.
- Optionally records camera video and/or microphone audio only after the user explicitly selects those sources and grants browser permission.
- Records device orientation and motion when the browser exposes those sensors.
- Stores observations and media in the browser's IndexedDB; it does not upload those recordings to the SSSWET API.
- Keeps previously scanned GPS observations in the local map across sessions.
- Supports event annotations, timeline scrubbing, and playback of recorded media segments.
- Exports an observation index (metadata only) and lets the user delete local data.

## Observation versus inference

The interface distinguishes three categories:

1. **Recorded observation:** sensor samples, media segments and annotations captured by the user at a known time.
2. **Retrospective estimate:** a model-generated scenario constrained by available measurements. It is not a recovered historical recording.
3. **Forward scenario:** a model-generated continuation of measured motion. It is not a guaranteed prediction.

The current GPS scenario model uses a bounded component-wise median of local segment velocities from one continuous run containing at least three and at most six eligible fixes. Its displayed uncertainty envelope is a heuristic built from reported anchor accuracy, velocity spread and pair-accuracy sensitivity; it is not a calibrated confidence interval. It does not yet perform multi-object tracking, image-based reconstruction, collision solving, scene understanding, long-range historical inference, or reliable long-range forecasting. Those capabilities require separate research, calibration datasets, validation and independent review.

No algorithm can uniquely recover an unrecorded past from incomplete present-day observations without additional evidence and assumptions. Future states are likewise conditional on unknown actions and disturbances. The product must never label generated scenarios as observed facts.

## Privacy and safety

- Capture is opt-in and initiated by a visible user action.
- Camera and microphone are separate optional permissions.
- The prototype stores sensor data and media locally in the browser. It does not send them to SSSWET.
- The basemap is fetched from OpenFreeMap/OpenStreetMap infrastructure. Tile requests disclose the map area being viewed to the tile provider.
- Browser storage may be cleared by the user or browser; this prototype does not provide cloud backup.
- Users must follow local recording, privacy and data-protection laws and obtain consent where required. Avoid recording private conversations or identifiable bystanders without permission.
- Do not use this prototype as forensic evidence, an emergency dispatch tool, a navigation safety system or a source of legal/medical conclusions.

## Local media storage

The prototype caps locally stored media at 150 MiB per browser database. Once the cap is reached, further media chunks are stopped with a localized notice; location and motion observations can continue. Users can delete local data to free space.

## Current limitations

- GPS accuracy depends on the device, environment and permissions; the interface displays the reported accuracy rather than claiming exact positioning.
- Device orientation and motion sensors are not available in every browser and may require a secure context or a permission prompt.
- 3D building detail depends on map coverage and the map style. A pitched map is not a complete photogrammetric reconstruction.
- Data remains local to the current browser profile and device.
- The initial extrapolation is intentionally simple and short-horizon. It is a demonstrator, not a validated physical simulator.

## Research roadmap

1. Add map-area coverage tracking, duplicate-sample filtering and drift-aware pose estimation.
2. Add calibration and quality metadata for each sensor stream.
3. Introduce consent-aware redaction, storage quotas, retention controls and encrypted export.
4. Add multi-object annotation and uncertainty-aware trajectory reconstruction.
5. Compare competing physical models against later recorded observations and publish calibration metrics.
6. Require independent review before any model is described as validated.

## Local correspondence distribution screening

The keyframe review also reports how candidate visual correspondences are distributed across a coarse image grid. The metric compares occupied grid regions in the two sampled frames and reports spatial coverage alongside the candidate-match count. This helps flag a high match count concentrated in a small image region, which can be misleading when repeated textures dominate.

This is a screening heuristic only. It does not estimate camera pose, optical flow, geometric overlap, depth, metric scale, a homography, epipolar geometry or a 3D reconstruction. It must not be used as proof that a scene can be reconstructed. The result is sensitive to image content, repeated patterns, blur, exposure and viewpoint changes; independent calibration and geometric validation remain necessary.

## Local displacement consistency screening

For each adjacent pair of candidate frames, the local correspondence heuristic now records matched patch-grid coordinates and reports the median horizontal and vertical grid displacement, plus the median radial deviation from that displacement. These robust summaries can help identify whether candidate matches suggest a broadly consistent image-grid shift or highly dispersed local changes.

The values are expressed in coarse descriptor-grid cells, not pixels or physical distance. This is not optical flow, camera motion estimation, feature tracking, homography fitting, epipolar geometry, geometric verification or a 3D reconstruction. Repeated textures, blur, exposure changes, parallax and viewpoint changes can produce misleading matches. Treat the values only as a triage aid; they do not validate camera motion or scene geometry.

## Scientific status

**Status: research concept and early web prototype.** No claim is made that virtual time travel, exact reconstruction of unrecorded history or reliable prediction of arbitrarily distant future events has been achieved.

## Terrain and 3D detail

The interactive map combines the OpenFreeMap Liberty vector style with optional MapLibre demonstration elevation tiles. When the elevation source is available, the interface enables terrain elevation, hillshading and a more pronounced 3D camera angle. Building footprints are extruded where the basemap supplies building geometry and height attributes; missing height attributes use a conservative visual fallback and must not be interpreted as surveyed building measurements. Coverage and detail vary by location. Demonstration elevation tiles are not a survey-grade terrain dataset, and the map must not be presented as a precise 3D scan of a property or street. OpenStreetMap/OpenFreeMap and MapLibre demo tile attribution is displayed in the interface.

## Camera capture and 3D reconstruction status

Camera access is opt-in and begins only after the user explicitly starts a local scan. The current browser prototype records a local video stream when camera capture is selected; it also records GPS and device motion/orientation when those sources are selected and available. **The current camera stream is not yet converted into a metrically scaled 3D mesh or point cloud and is not automatically fused with the basemap.** The video must therefore be treated as source evidence, not as a completed 3D scan.

A defensible reconstruction pipeline requires calibrated camera intrinsics, overlapping frames, visual feature matching, camera-pose estimation, scale recovery (for example from depth sensing or surveyed references), georeferencing, confidence metadata, and validation against independent measurements. Where supported, a future depth-sensing integration may provide per-frame depth; devices without depth support will need a separate photogrammetry workflow. The basemap geometry, camera-derived geometry, and unobserved areas must remain visually and semantically distinct. No synthetic fill should be displayed as measured structure.

The interface starts with every sensor permission unchecked. Opening the page loads the map and local timeline only; it does not request camera, microphone, location, or motion access. The user must select sources and press the start control.

## Local candidate keyframe extraction

The prototype can analyse one previously recorded local video after the user selects that clip and explicitly starts analysis. It samples at the selected interval, with a maximum of 60 sample positions per analysis. A lightweight grayscale Laplacian-variance score estimates image sharpness, while normalized frame-to-frame pixel difference estimates visual change. These are screening heuristics, not calibrated image-quality measurements.

Candidate frames are exported individually as JPEG images at the source video dimensions when the browser supports full-resolution canvas export. Candidate images remain in memory during the session and are not automatically written to IndexedDB or uploaded. The extraction process limits exported candidate data to 100 MiB per analysis; the existing local media database remains subject to its separate 150 MiB cap.

## Visual continuity screening

After candidate frames are rendered, the browser performs a second local-only screening pass over the visible frame previews. Each preview is reduced to a small grayscale luminance vector, normalized for overall brightness, and compared with the preceding candidate using a normalized Euclidean image distance. The displayed **visual continuity** score is `100 × (1 − normalized change)` and is intended only to highlight sequences that may contain moderate visual continuity or unusually large visual changes.

A higher score means the adjacent previews are more visually similar under this simple representation; a lower score means the adjacent previews differ more. The score is deliberately presented as a heuristic rather than an overlap measurement. It does not estimate feature correspondence, camera pose, lens geometry, depth, scale, or true geometric overlap. Exposure changes, motion blur, repeated textures and viewpoint changes can all affect the result. A high score can therefore still be useless for reconstruction, while a lower score can occur between genuinely useful frames.

## Local correspondence screening

The prototype now performs an additional local-only screening pass on adjacent candidate previews. Each preview is reduced to a 128×96 luminance image, divided into a regular grid of small normalized intensity patches, and compared against patches in the neighboring frame. A conservative nearest-neighbor plus ratio test counts only distinctive candidate patch matches.

The displayed **local visual correspondences** count is a screening signal for whether two frames contain repeated local intensity patterns. It is not an implementation of a production feature detector such as SIFT/ORB/SURF, and it does not establish feature tracks, epipolar geometry, camera poses, depth, metric scale or 3D overlap. Repeated textures, low texture, blur, exposure changes and viewpoint changes can create false positives or false negatives. The result must therefore be treated as a candidate-ranking aid rather than reconstruction evidence.

The correspondence pass is deliberately bounded to the small preview representation so it can run locally in an ordinary browser without uploading images. It is intended to prepare the dataset for a future calibrated feature-matching and pose-estimation stage.

## Reconstruction readiness boundary

The current workflow is intentionally staged:

1. **Recorded evidence:** retain the original local video and sensor observations.
2. **Candidate selection:** screen frames for sharpness, visual change, visual continuity and local correspondence candidates.
3. **Geometric reconstruction:** future work must establish robust feature correspondences, calibrated camera poses and depth/scale constraints.
4. **Spatial registration:** future work must distinguish measured geometry from basemap geometry and establish georeferencing uncertainty.
5. **Validation:** reconstructed geometry must be compared with independent measurements before being described as validated.

Until stages 3–5 exist and are independently evaluated, the interface must not describe candidate frames or map extrusions as a reconstructed physical scene.

This feature is only a preparatory image-selection aid. A sharp frame is not necessarily geometrically useful, and a large visual change or correspondence count does not prove that two frames overlap appropriately. Any later reconstruction pipeline will require calibrated capture, robust feature matching, pose estimation, scale recovery, georeferencing and independent validation.


## Reciprocal local correspondence screening

The adjacent-frame patch matcher now applies its nearest-neighbour and descriptor-ratio checks in both directions. A pair is counted only when patch A selects patch B as its best candidate, patch B selects patch A as its best candidate, and both directional ratio checks pass. A zero-distance tie in the second-best comparison is rejected as ambiguous rather than divided by an arbitrary epsilon. The interface reports the forward candidate count separately from the reciprocal count. Spatial coverage and median grid displacement are calculated from reciprocal pairs only; displacement and spread are shown as unavailable when no reciprocal pair survives.

This mutual-nearest-neighbour constraint prevents several source patches from all being counted against the same destination patch. It is a deterministic one-to-one consistency screen, not a geometric outlier filter. It does not fit a translation, homography, essential matrix or camera pose; it does not use RANSAC; and it does not identify geometric inliers. It can reject valid correspondences under occlusion, repeated texture, viewpoint change, parallax or appearance change. A reciprocal match is still only a candidate intensity-patch association, not a tracked physical feature or evidence of 3D overlap.

Regression acceptance criteria cover: (1) three distinctive synthetic descriptor pairs produce three reciprocal matches; (2) a many-to-one ambiguity is reduced from three forward candidates to one reciprocal pair; (3) a one-candidate target cannot pass a two-neighbour ratio test; (4) equal zero-distance alternatives are rejected as ambiguous; and (5) empty results do not display a zero displacement as if it were measured. Tests use synthetic descriptors and do not claim real-world reconstruction accuracy.


## Descriptor-distance and ambiguity diagnostics

For every retained reciprocal patch pair, the local matcher now records two additional descriptive statistics. **Median descriptor distance** is the median RMS distance between the normalized intensity descriptors for the retained pairs. **Median best/second ratio** is the median of both directional nearest-to-second-nearest distance ratios across those same pairs. The matcher accepts only candidates with descriptor distance below 0.72 and a ratio below 0.82 in each direction; a second-nearest distance at or below 1e-6 is treated as ambiguous and rejected.

These values expose how the current descriptor matcher behaved on the sampled previews. They are not a calibrated confidence score, probability of correctness, physical measurement, or cross-device quality scale. Lower descriptor distance means more similar descriptors under this representation; a lower best/second ratio means the best candidate is more separated from its next alternative. Neither proves that the associated patches represent the same physical point. The median ratio aggregates both directions for reciprocal pairs only. If no reciprocal pair survives, both diagnostics are shown as unavailable rather than zero.

Regression acceptance criteria use deterministic synthetic descriptors: (1) three distinctive pairs must yield a median descriptor distance of 0.01 for a known 0.01 descriptor offset; (2) the median directional ratio must remain below the 0.82 acceptance threshold; (3) a many-to-one ambiguity must not contribute to reciprocal diagnostics; (4) a best distance equal to the exclusive 0.72 threshold must be rejected; (5) empty or ambiguous results must report unavailable diagnostics; and (6) repeated evaluation of the same inputs must produce identical results. These tests validate implementation behavior on synthetic vectors only, not real-world matching accuracy.

## Keyframe preview observer lifecycle

The local correspondence review now refreshes only when its source previews can have changed: a keyframe card is inserted or removed, an image is inserted or removed within a card, an image `src` changes, or a keyframe preview finishes loading. Multiple changes are coalesced into one animation-frame update.

The observer deliberately ignores the diagnostic elements generated by the matcher itself. This prevents its own output from repeatedly scheduling another render. Existing diagnostic elements are also cleared when fewer than two candidate previews remain, so stale results are not left visible after a sequence is shortened.

This change only observes the existing local preview DOM. It does not add a capture source, permission request, upload, persistent storage path or background processing service. Pixel descriptors continue to be calculated locally from the preview images.

Regression acceptance criteria are: (1) diagnostic-note and metric mutations do not schedule a new render; (2) keyframe-card insertion and image insertion/removal do schedule a refresh; (3) image `src` changes and completed image loads schedule a refresh; (4) unrelated attributes and text-only changes are ignored; (5) repeated source changes are coalesced by the existing animation-frame scheduler; and (6) stale diagnostics are removed when fewer than two previews remain. The automated observer tests use a deterministic DOM test double; they verify event filtering and scheduling logic, not browser-specific performance or visual quality.


## Session-monotonic capture timestamps

New observations and local media segments now carry a session-scoped clock envelope. At page-session start, the browser records a wall-clock origin and a monotonic-clock origin. Within that session, the timeline timestamp is derived from the wall-clock origin plus monotonic elapsed time, so a later manual/system wall-clock jump does not reorder same-session observations or inflate/shorten media segment durations.

Each new record retains the raw `wallTimestamp`, `monotonicElapsedMs`, `clockOffsetMs`, `clockToleranceMs`, `clockStatus` and a non-identifying `clockSessionId`. The offset is the raw device wall-clock reading minus the session's monotonic-derived epoch timestamp. A difference greater than 2,000 ms is labelled as wall-clock divergence; this threshold is a diagnostic convention, not a measurement of UTC accuracy. Sensor sampling intervals also use monotonic elapsed time, and the first sensor sample is not suppressed by the session clock's near-zero origin.

The monotonic clock is comparable only within one page session. Across reloads or separate sessions, ordering still relies on each session's initial device wall-clock anchor. The prototype does not synchronize with an external time service, certify UTC, correct a wrong initial device clock, or guarantee continuity across browser/device restarts. Browser and operating-system behavior during device sleep or page suspension can also affect monotonic-clock progression; a detected offset does not identify its cause or establish which clock is correct. Older stored records remain readable and retain their original timestamp behavior. If a browser lacks a usable monotonic clock, the record explicitly reports that fallback and uses the device wall clock.

Regression acceptance criteria use synthetic clocks: a backward wall-clock jump must not reorder same-session events; a forward jump must not create a false same-session gap; media duration must follow monotonic elapsed time; raw wall-clock values and divergence offsets must remain inspectable; the configured 2,000 ms boundary must be deterministic; non-increasing monotonic readings must not reverse elapsed time; fallback and legacy records must remain readable; and all 15 module locales must have distinct labels for divergence, within-tolerance and fallback states. These tests validate the clock-handling implementation, not real-world clock accuracy or geospatial reconstruction.


## Robust local GPS scenario envelope

The unrecorded-interval scenario now uses a bounded robust local-velocity estimator rather than extrapolating from only the nearest two fixes. It requires at least three consecutive GPS observations with finite reported horizontal accuracy no greater than 150 m. It selects one continuous track run, using the earliest eligible run for a retrospective scenario and the latest eligible run for a forward scenario. A run is split when timestamps are non-increasing, the gap exceeds 15 minutes, a segment exceeds 5 km, or its implied speed exceeds 70 m/s. The model uses at most six fixes per scenario.

Each selected fix is projected into a local east/north plane relative to the first selected fix. Segment velocity components are calculated from adjacent projected positions and elapsed timestamps. The component-wise median east and north velocities reduce the influence of one extreme segment. The median radial residual from that median velocity vector is reported as an observed velocity-spread descriptor; it is not a standard deviation or a calibrated noise estimate.

The displayed **heuristic scenario envelope** is calculated as:

`anchor accuracy + horizon × (median vector residual + median pair-accuracy sensitivity)`

where pair-accuracy sensitivity is the median of `(accuracy_start + accuracy_end) / segment_duration` across the selected adjacent pairs. The terms are displayed separately so the calculation is inspectable. This envelope is a deterministic screening indicator, not a confidence interval, guaranteed error bound, probability, or surveyed spatial uncertainty. Browser-reported accuracy is device/provider metadata and is not independently verified. The median velocity is a short-window constant-velocity hypothesis; acceleration, turns, obstacles, map matching, multipath errors and unrecorded events remain unknown.

The model does not join separate track runs. It returns no scenario unless one run contains at least three eligible fixes. The horizon is bounded to the interface maximum of 15 minutes, and the input window is capped at six fixes. Legacy GPS records without a finite reported accuracy remain visible in the recorded timeline but are not used by this uncertainty-aware scenario estimator.

Regression acceptance criteria use synthetic tracks: (1) a straight 100 m per-minute track produces a 100 m one-minute scenario; (2) the retrospective scenario extends opposite the observed median velocity; (3) one plausible extreme segment among three is resisted by the component-wise median; (4) the envelope components and formula reproduce a deterministic 15 m result for the defined 5 m accuracy fixture; (5) fewer than three eligible fixes, missing/over-limit accuracy, invalid coordinates, non-increasing timestamps, long gaps, excessive jumps and horizons above 15 minutes produce no scenario; (6) the estimator uses no more than six fixes; and (7) repeated inputs produce identical output. These are implementation tests on synthetic data, not real-world GPS accuracy, forecast validation or evidence of reconstructed historical geometry.


## Capture-session isolation and timeline comparability

The timeline, recorded map tracks and GPS scenario estimator now keep capture sessions separate. Each new record already carries a session identifier from the session clock; records created before this metadata existed are grouped into a separate legacy session. The session selector filters timeline playback and scenario input to exactly one selected session. If more than one session exists, the user must choose one rather than silently combining records.

Recorded map polylines are also broken at session boundaries. Marker deduplication and timeline media playback are scoped to the selected capture session, so a later visit or an overlapping clip from another session is not silently merged into the current replay. The exported observation index includes a note that timestamps are directly comparable within a session, but cross-session chronology cannot be inferred from device wall-clock anchors alone.

This isolation is necessary because the monotonic clock is only comparable within one page session. The initial wall-clock anchor of another session may be wrong, shifted or changed by the operating system. The selector's displayed dates are descriptive device timestamps, not a trusted global ordering. Legacy records remain grouped together because no reliable session boundary can be reconstructed for them. Records captured without a usable monotonic clock still carry their session identifier, but their within-session ordering retains the previously documented wall-clock fallback limitation.

Regression acceptance criteria include: (1) two sessions with overlapping or reversed device timestamps are never combined into one GPS scenario; (2) two fixes from one session plus a third fix from another cannot satisfy the three-fix minimum; (3) an explicitly selected session uses only its own source observation IDs; (4) multiple sessions without an explicit selection produce no scenario; (5) unknown session selections do not fall back to another session; (6) legacy observations remain selectable as their own group; (7) map track lines flush at session boundaries; (8) marker deduplication does not cross session boundaries; and (9) all 15 module locales contain the session selector, help, prompt and option-template strings. These tests validate data isolation and deterministic selection, not UTC synchronization or cross-session chronological accuracy.

## GPS track-integrity audit and rejected-fix boundaries

The scenario panel now audits the GPS observations from the explicitly selected capture session before showing a retrospective or forward scenario. The audit reports the number of GPS observations, accepted fixes, rejected fixes, continuous runs, longest run, continuity-break reasons, and records using the wall-clock fallback or carrying a wall-clock-divergence flag. Rejection categories include missing coordinates, invalid coordinates, invalid timestamps, missing accuracy, invalid accuracy, and reported accuracy above 150 m. The summary contains counts only; it does not repeat coordinates or annotation text.

A rejected GPS observation now terminates the current continuous run. The estimator does not silently connect the valid fix before a rejected sample to the valid fix after it. Continuous runs are also split when elapsed time is non-increasing, the gap exceeds 15 minutes, displacement exceeds 5 km, implied speed exceeds 70 m/s, or the session changes between monotonic and wall-clock time bases. When both adjacent fixes have monotonic elapsed readings from the same session, segment duration is calculated from those readings; otherwise it uses the stored session timestamp. A switch between time bases is treated as a discontinuity rather than mixed into one velocity estimate.

The audit is an explainability and data-quality diagnostic, not an independent validation of the GPS provider, a statistical confidence measure, or proof that an accepted position is physically correct. Browser-reported accuracy remains unverified provider metadata. A continuous run only means that the recorded samples passed the prototype's explicit continuity rules; it does not establish the exact path between observations. The short-horizon constant-velocity scenario remains a hypothesis, and its displayed uncertainty envelope remains a heuristic rather than a calibrated confidence interval.

Regression acceptance criteria use deterministic fixtures: (1) a three-fix continuous track reports three accepted fixes and one run; (2) a rejected GPS fix between valid observations creates a run boundary and cannot be bridged by the estimator; (3) each rejection category is counted separately; (4) time-gap, distance, speed, non-increasing-time and clock-basis changes report distinct break reasons; (5) same-session elapsed duration uses monotonic readings when both endpoints provide them; (6) mixed time bases split the run; (7) audits require an explicit selection when multiple sessions exist; (8) the audit output contains counts rather than location coordinates; and (9) all 15 supported module locales provide a complete diagnostic summary. These tests verify deterministic implementation behavior on synthetic data, not real-world positioning accuracy or reconstruction quality.


## Reported GPS accuracy footprints on the map

The map no longer draws a fixed 40 m circle and labels it as a scanned or visited zone. It now renders a geodesic footprint for a deduplicated GPS marker only when that observation contains a finite, positive browser-reported accuracy value no greater than 150 m. The footprint radius is taken directly from that observation's reported value; it is not inferred, averaged or substituted with a default. The spherical direct-geodesic calculation produces a closed 36-edge ring with counterclockwise exterior winding as required by GeoJSON. A footprint crossing the antimeridian is split into two GeoJSON polygons so no ring contains a world-spanning longitude jump; footprints that would cross a geographic pole are omitted rather than distorted. At most 500 evenly spaced representatives from the deterministic session/time ordering receive accuracy polygons. This is a display-sampling rule, not a claim that timestamps from separate sessions are comparable; all deduplicated map markers remain visible as recorded points and segmented connecting lines.

The map legend explicitly states that these circles show browser-reported GPS accuracy, not surveyed coverage. The line between two recorded fixes is only a straight visual connector; it does not establish the route travelled between them. Missing, zero, invalid and over-limit accuracy values produce no accuracy polygon. Existing observations and media remain local, and no new sensor permission, upload or background capture path is introduced.

Regression acceptance criteria use deterministic geometry fixtures: (1) an ordinary footprint has 37 coordinates including a closed ring; (2) every ordinary vertex lies within 0.02 m of the supplied radius under the same spherical Earth model and exterior rings use counterclockwise winding; (3) footprints remain valid near 89.9° latitude; (4) eastward and westward antimeridian crossings become two closed GeoJSON polygons with normalized longitudes and no world-spanning edge; (5) footprints that cross a geographic pole are omitted; (6) zero, invalid and greater-than-150 m accuracy values produce no polygon; (7) polygon edge count is bounded to 12–72; (8) deterministic even sampling returns at most 500 unique markers, retains the first and final markers when sampling is needed, and leaves all deduplicated map markers visible as points and segmented connectors; and (9) all 15 module locales explain that the circles are reported GPS accuracy, not surveyed areas, and that lines connect recorded fixes. These tests verify deterministic geometry and UI wiring on synthetic inputs, not provider accuracy, physical coverage or reconstructed paths.


## Anchor-bounded clock alignment and provenance

The Python research core now provides a version-2 clock-alignment model that retains the evidence used to align one recorded source clock with one reference clock. It is a derived research utility; it does not rewrite the browser's original IndexedDB observations or automatically change the visible web timeline.

- A model accepts 2–500 paired anchors from exactly one session and one source. Both timestamps must include an explicit timezone. Anchors are ordered by source timestamp, and both source and reference times must be strictly increasing.
- Every anchor receives a stable identifier. A caller may supply an identifier; otherwise the model assigns one after deterministic chronological sorting. An optional bounded \`reference_evidence_ref\` can point to the log, frame, or other record used to establish the reference timestamp.
- The model records drift in parts per million for each adjacent anchor interval. Drift is a diagnostic calculated from the supplied pairs; it does not establish which clock is correct or certify UTC.
- Event timestamps are aligned only by piecewise-linear interpolation inside the anchor range. Each aligned result names its left and right anchors, interpolation fraction, interval drift, and available reference-evidence references. Events from another session/source and events outside the anchor range remain unaligned. Extrapolation is never performed.
- Anchor and event uncertainty values are interpreted only as user-declared conservative absolute bounds in seconds. Under the explicit piecewise-linear clock-mapping assumption between adjacent anchors, the model reports a conditional uncertainty envelope by linearly combining the interpolated anchor bounds and event bound. This does not bound unmodelled non-linear clock behaviour between anchors. It is not a standard-deviation calculation, confidence interval, probability, or empirically calibrated error distribution. The output field `declared_uncertainty_envelope_seconds` is populated only when all required inputs were declared; `declared_uncertainty_inputs_complete` means only that those inputs were supplied, not that the clock model has been independently validated. Missing values are not silently represented as measured zero.
- The canonical SHA-256 digest detects accidental changes to a model payload. It is not a digital signature, proof of source authenticity, or evidence that the supplied anchors are correct.
- Version-1 models remain verifiable for compatibility, but their earlier schema did not record whether zero-valued uncertainty was explicitly declared or retain anchor provenance. Version-1 alignments therefore do not claim a complete uncertainty bound or complete anchor provenance.

The browser timeline continues to use its existing session-monotonic capture timestamps. This core utility is not yet wired to automatically align or rewrite browser records; an explicit, consent-aware interface and a source-specific evidence workflow are required before that integration.

**Regression acceptance criteria:** (1) reversing the input order of the same identified anchors produces the same model digest; (2) every aligned event reports its bracketing anchor IDs and interpolation fraction; (3) exact-anchor events cite one anchor once, not twice; (4) adjacent-interval drift is reproducible from the supplied pairs; (5) missing anchor or event uncertainty prevents a numeric declared envelope; (6) a complete declared-bound fixture reproduces the linear-sum result; (7) a model with extrapolation enabled or confidence-interval semantics is rejected even if its digest is recomputed; (8) duplicate/oversized IDs and evidence references are rejected; (9) out-of-range and cross-session/source events remain unaligned; and (10) version-1 models remain readable without overstating their uncertainty or provenance. These tests validate deterministic model behavior, not the accuracy of the external reference clock, the correctness of user-supplied anchors, or recovery of unrecorded history.


## Local browser clock-calibration workspace

The browser module now provides a local-only clock-calibration workspace for one selected capture session. It reads the existing events object store through a read-only IndexedDB transaction. It does not modify, replace, delete, upload, or automatically export source observations, and it does not read or include media blobs.

The researcher selects at least two distinct recorded observations as clock anchors and enters the corresponding independently established reference timestamps. Reference timestamps must be full ISO 8601 date-time values including seconds and an explicit Z or ±HH:MM timezone offset; local-time-only strings are rejected. Optional fractional seconds are limited to three digits (millisecond precision). Both source-anchor times and reference-anchor times must be strictly increasing after source-time sorting. The interface supports at most 20 anchors per preview and refuses sessions containing more than 5,000 observations rather than silently truncating them.

Only sessions with a stable clockSessionId are eligible. The older legacy grouping is intentionally excluded because it cannot reliably establish a unique capture-session clock. The workspace also requires every selected event to have a finite numeric timestamp, a unique bounded event ID, one consistent clock basis, and the same session clock ID. A session mixing monotonic and wall-clock records is rejected rather than silently combined. The browser model labels the source as browser-session-clock-monotonic or browser-session-clock-wall to preserve that distinction; it never combines events from other sessions or sources.

The browser implementation uses the same schema-v2 anchor model, piecewise-linear interpolation assumptions, diagnostic drift calculations, declared absolute-bound semantics, and canonical SHA-256 model fingerprint as core/ssswet_core/temporal_clock_alignment.py. A deterministic regression fixture verifies that the browser and Python implementations produce the same model digest. This cross-runtime check covers the declared model representation; it does not authenticate source timestamps or user-supplied reference evidence.

No extrapolation is performed. Events outside the first and last anchor timestamps receive an outside_anchor_range status and no derived reference time. Interval drift in parts per million is diagnostic only and is not used as proof of clock stability between anchors. The browser rounds derived timestamps to its 1 ms resolution; this is a representation limit, not a clock-accuracy claim.

Anchor uncertainty bounds are optional and must be user-declared. An optional event timestamp bound can be supplied once for the session; if supplied, the workspace applies that same absolute bound uniformly to every event in that session. The interface limits entered anchor and event bounds to 31,536,000 seconds (one year). This uniform-bound choice is an explicit user assumption and should not be used when event uncertainty varies materially. Missing required bounds are not treated as zero: the numerical uncertainty envelope is withheld. When present, the envelope is a conditional sum of declared absolute bounds under the piecewise-linear model, not a standard deviation or confidence interval.

Reference-evidence identifiers are optional user-supplied strings. The workspace records them for provenance but does not inspect or authenticate the referenced material. A complete identifier list is therefore not proof that the underlying evidence is genuine or correctly interpreted.

The preview table displays at most the first 100 aligned-event reports for usability; the downloaded JSON contains all processed reports, the schema-v2 model, the model fingerprint, the assumptions, and compact observation metadata (IDs, event kinds and timestamps). The export contains no media. It is created only after the user explicitly presses the export button. The derived alignment is not written back into IndexedDB.

### Evidence categories and limits

- **Measured/recorded observation:** the original event timestamp and event metadata stored by the browser.
- **User-supplied reference:** a reference timestamp and optional evidence identifier entered by the researcher; not independently verified by the application.
- **Derived result:** the aligned reference timestamp calculated between declared anchors.
- **Heuristic/diagnostic:** interval drift in ppm; it is not a probability or validation score.
- **Model assumption:** piecewise-linear clock behaviour between anchors.
- **Unknown:** clock behaviour outside the anchor range, undocumented timestamp corrections, authenticity of reference evidence, and any unrecorded event history.

This workspace calibrates a recorded session's timeline under explicit assumptions. It does not recover unrecorded history, establish event identity, predict future events, or create a real time machine.
