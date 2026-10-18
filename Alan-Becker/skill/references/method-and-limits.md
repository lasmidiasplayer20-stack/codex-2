# Method, portability, and limits

## What this skill provides

A workflow for image-derived 2D reconstruction that follows the supplied reference's own visual language. The accompanying project demonstrates complete frame coverage, SVG path generation, native-size rasterization, per-frame shape/motion observations, original AAC retention, and full export validation.

The example source is approximately 170 seconds at 24000/1001 FPS and 640×360. Those are properties of that file, not defaults for future videos. Its campaign scenery and characters are examples, not reusable content requirements.

## Definitions

| Claim | Required evidence |
| --- | --- |
| Every visible frame reconstructed | Every source frame index has a corresponding drawing representation, with complete ordered coverage. |
| Complete transition coverage | Every adjacent frame pair has an observation; processing boundaries do not omit transitions. |
| Motion estimate | Algorithm, resolution, units, confidence/limitations, and reference-coordinate mapping documented. |
| Exact skeletal motion | Validated joint identities and trajectories; contours or optical flow alone are insufficient. |
| Native 1080p render | Drawing renderer actually emits a 1920×1080 buffer; source-detail limitations disclosed. |
| Exact visual clone | Explicit matching criterion verified over the complete output. Similar style, low average error, and metadata checks alone do not establish this. |
| Original audio retained | Source stream/provenance, unchanged timing, full decode, and matching samples or payload evidence. |
| Complete delivery | Full duration/frame count, completed validation, and verified file at the authorized remote destination. |

## Reuse with another source

Probe the new input before changing code. Review the case-study script's fixed dimensions, FPS, expected count, flow grid, source path, output path, and validator. Replace these with measured parameters in the new project; do not run its case-specific assertions against an unrelated video or disable them to make it pass.

Record `input_sha256`, frame/timestamp coverage, trace configuration, target dimensions, dependencies, and per-part provenance. Rebuild any part whose provenance no longer matches. Keep source raster frames as analysis inputs only; editable traced output must not disguise raster embedding as vector geometry.

The original pixels encode compression and limited resolution. Tracing may create contour drift, fragmentation, lost thin lines, altered text, color bands, or temporal flicker. Measure these, review them in motion, and refine the affected intervals. No algorithm here recovers occluded limbs, authoring layers, original vector control points, hidden intent, or physical forces with certainty.

## Sharing

The supplied project contains the reference provided for this task so the exact case can be reproduced. Do not assume that permission covers publishing other users' private reference files. Ask only if required publication rights or private-asset scope is unresolved; use existing explicit authorization when available. Do not bundle credentials, installed dependencies, caches, or temporary frames.
