# Generalized correction and verification catalog

Use on every new reference, adapting dimensions, times, and tolerances. This catalog preserves lessons from user corrections across projects; it does not imply every failure occurred in the included example. No finite list anticipates every possible error. Add new reported failures with evidence and a reusable prevention rule.

| Failure class | Detection and correction | Verification |
| --- | --- | --- |
| Wrong inherited style, story, or scenery | Compare with the current source throughout; remove unrelated prior-project designs and content. | Matched-time comparisons across the entire video. |
| Distorted proportions | Compare actor/prop ratios and silhouettes; correct shared scale or traced geometry. | Wide shots plus close contacts, all affected occurrences. |
| Bent, stretched, snapped, or detached limbs | Inspect arm/leg shapes through extreme poses and fast transitions; refine contours or a requested rig. | Source-aligned frame review; constant segment lengths only if using an articulated model. |
| Penetration, floating, or bad support | Review actor–floor, actor–furniture, hand–object, body–vehicle, and wheel–ground contacts. Respect intentional source stylization. | Entire contact interval and nearby cuts, using scale-aware clearances for geometry-based reconstruction. |
| Misaligned seat, desk, or support | Check orientation and the source's relative placement; adjust coherent transforms or traced shapes. | Feet/knees/supports and oblique views; no universal hardcoded offsets. |
| Sliding feet or wrong wheel motion | Compare world/image trajectories with actual travel. | Stance intervals, turns, stops, impacts, and wheel distance/radius if modeled. |
| Clothing folds lost, collapsing, or misrepresented | Compare silhouettes and deformation in bent/seated/raised-arm poses. Refine source-derived shapes or implement requested cloth behavior. | Review those intervals; do not label rigid shapes as simulated cloth. |
| Broken pickup/release or disappearing prop | Inspect before/at/after contact and visibility changes. | Continuous transform or source-frame correspondence, all relevant actors and props. |
| Ghosts, duplicate objects, stale visibility | Inspect active objects/layers and revisit frames out of order. | Expected instance counts and appearance/disappearance boundaries. |
| Camera jump, clipping, wrong zoom, or framing | Compare subject bounds and backgrounds; review candidates affected by parallax or foreground movement. | Shot boundaries and camera trajectories; estimates remain labeled as estimates. |
| Missing frame, repeated segment, wrong cut, or altered action | Check global frame indices and source timestamps, especially at part boundaries. | Complete coverage with no duplicates/gaps; compare both sides of joins. |
| Flow mislabeled as exact joints or identities | Review algorithm output and ambiguity of color regions/occlusions. | Document inference limits, grid resolution and units; do not assert unsupported hidden motion. |
| Jagged outlines, thin-line loss, fragmented regions, altered colors or text | Compare source/reconstruction metrics and inspect fine details; refine tracing settings locally. | Worst-error frames, text close-ups, and motion playback. |
| Temporal shimmer or inconsistent contours | Inspect consecutive reconstructed frames, not just isolated stills. | Slow playback and source-relative temporal comparisons at fast motion and static regions. |
| Raster source hidden inside supposed vector output | Inspect SVG elements and external/embedded image references. | No raster `<image>`, base64 source textures, or video overlays in the traced representation. |
| Upscaled preview presented as native final rendering | Inspect actual renderer buffer and encoded stream. | Both dimensions verified; original source-detail limits stated. |
| Missing, shifted, repeated, or falsely described audio | Inspect source/final streams and matched-time samples; assemble the full original track once when authorized. | Complete decode and alignment at start/middle/end and joins. |
| Preview too short or inaccessible | Check actual duration and the requested host. | Correct-length file and verified remote link, separate from the full movie. |
| Partial export reported as complete | Propagate all process failures and inspect frame counts and ending. | Complete decode, exact coverage, real final file, no active-writer claim of completion. |
| Old cache reused after source/settings changed | Check source/configuration hashes and affected intervals. | Invalidated parts rerendered; report belongs to current inputs. |
| Incorrect output folder or missing project/skill assets | Compare deliverables with the current request. | Complete project under the requested skill folder; final-only video folder contains the intended complete movie. |
| Local commit mistaken for publication | Check remote branch/file state. | Remote SHA equals delivered commit; actual links and paths confirmed. |

For each applicable issue record: source time/frame range, expected versus observed behavior, root cause, correction, verification method/results, evidence paths, and remaining limitations. Use pending/failed/passed/not-applicable with reasons. A related function in the template does not make a new film pass automatically.

When fixing shared code, revisit all affected shots and regenerate stale output. Do not add redundant trivial tests; use meaningful invariants or targeted regressions for observed defects and keep explicit visual evidence for artistic judgments.
