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

## Scientific status

**Status: research concept and early web prototype.** No claim is made that virtual time travel, exact reconstruction of unrecorded history or reliable prediction of arbitrarily distant future events has been achieved.
