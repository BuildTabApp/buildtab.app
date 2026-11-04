BuildTab 2026.8.2 (3) — iPhone, iPad and iPhone Duo screenshots

Open preview.html to review the final compositions. English copy is in
source/metadata.json. en-US/raw contains real simulator captures; en-US/final
contains opaque RGB PNGs composed with local BuildTab fonts and brand colours.
No screenshot is a generated recreation of the app UI.

UPLOAD SETS (extract the ZIP before uploading)
- en-US/iphone-app-store.zip: ten iPhone screenshots, 1320 x 2868.
- en-US/ipad-app-store.zip: ten iPad screenshots, 2064 x 2752.
- en-US/duo-mixed-app-store.zip: ten features, alternating inner/outer, inner first.
- en-US/duo-inner-app-store.zip: alternative complete inner-display set.
- en-US/duo-outer-app-store.zip: alternative complete outer-display set.
For Duo, use one of its three sets in the ten-image Duo slot.

Outer: 1398 x 2034. Inner: 2853 x 2007, landscape.
https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/

ORDER
Dashboard; project; partial expense; materials; time; pricing; spending;
expense history; export; dark mode.

SOURCE AND ISOLATION
The capture build is a disposable copy of the current app working tree,
including the Duo layout changes and version bump. source/source-revision.json
identifies the base commit. production-changes.patch captures the uncommitted
app changes. offline-fixture.patch applies only to that copy: independent
app.buildtab.listingdemo bundle, empty entitlements, an in-memory store with
CloudKit disabled, sample data and demo Pro access without StoreKit requests.
Do not archive or distribute the fixture. Production files were not patched.

REPRODUCE
1. Extract the base commit from the app repository into a fresh temporary
   directory with git archive. Apply source/production-changes.patch with
   patch -p1, then source/offline-fixture.patch with patch -p1.
2. Build the BuildTab target for iphonesimulator with CODE_SIGNING_ALLOWED=NO.
   Alternatively source/prepare-fixture.py creates a new disposable copy of
   the current local working tree; its output directory must not exist.
3. Boot the dedicated BuildTab Duo QA simulator. In Device Hub select that
   device. Use Closed for outer portrait, Open and Rotate Right for inner
   landscape. Keep the default text size. Use xcrun simctl io UUID enumerate
   to identify the active display; do not rely on the default display.
4. Run source/capture.py --device UUID --app /path/BuildTab.app
   --profile duo-outer --display DISPLAY_ID, then repeat for duo-inner.
   The script checks dimensions. Inspect every capture for alerts or startup
   screens. Sample project dates are in November 2026; dashboard month totals
   are relative to the device's current date.
   For iPhone and iPad, boot dedicated iPhone 17 Pro Max / iPad Pro 13-inch
   (M5) simulators with iOS 27.0. Use --profile iphone or --profile ipad
   in portrait orientation; the default display is 1. Duo uses iOS 27.1.
5. Compile source/ocr.swift, then run source/check-captures.py --ocr /path/ocr.
6. Run python3 source/render.py, then python3 source/package.py.
   Requires Google Chrome and Pillow. No network fonts or image assets.

The source files include the capture, render, packaging and OCR validation
scripts. source/validation.json records final dimensions, colour mode and
SHA-256 checksums. Contact sheets and preview.html are for review, not upload.

These assets are prepared locally. Nothing has been uploaded or published.
