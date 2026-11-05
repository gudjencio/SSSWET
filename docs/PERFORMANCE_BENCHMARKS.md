# Layout stability and responsive performance — 5 November 2026

## Measured issue

The first repeatable browser benchmark recorded cumulative layout shift (CLS)
medians of 0.248 on desktop and 0.208 on a 390 × 844 mobile viewport. The
largest recorded sources included the top header, language selector, project
action links and research command area.

These are laboratory measurements from a virtual Chromium runner, not field
telemetry. They identify a regression target; they do not describe every
visitor's device.

## Changes

1. The language control now remains in normal layout flow instead of inheriting
   conflicting absolute-position rules from older responsive styles.
2. The desktop header has a reserved 56 px block size.
3. The mobile header has a reserved 52 px block size.
4. The language control has a fixed 42 px height before and after options load.
5. The language selector has a bounded 320 px width and can shrink on narrow
   screens.
6. Long language labels no longer determine the selector's intrinsic width.
7. The selector uses a stable custom chevron while remaining a native,
   keyboard-operable HTML select.
8. The header layout no longer depends on left/right positioning rules, which
   also reduces direction-specific layout overrides for RTL languages.
9. The capitalization MutationObserver now edits only the changed text node
   instead of rescanning its entire parent subtree for each character-data
   mutation.
10. The browser benchmark now records navigation wait time separately from its
    post-load observation delay and reports header/select geometry plus
    horizontal-overflow diagnostics.

## Validation

The performance workflow runs three Chromium trials at desktop and mobile
viewports. It records CLS and the first ten layout-shift sources, alongside
header and selector dimensions. Geometry checks are advisory until repeated
runs establish stable baselines.

No performance improvement percentage is claimed until the updated benchmark
completes and comparable measurements can be examined. No production
deployment, payment flow, account operation or hosted-engine request is part
of this change.
