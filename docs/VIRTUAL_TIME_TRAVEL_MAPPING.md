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

The current baseline model extrapolates a short trajectory using constant velocity from two recorded GPS samples. Its displayed uncertainty radius grows with horizon and distance. It does not yet perform multi-object tracking, image-based reconstruction, collision solving, scene understanding, long-range historical inference, or reliable long-range forecasting. Those capabilities require separate research, calibration datasets, validation and independent review.

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
