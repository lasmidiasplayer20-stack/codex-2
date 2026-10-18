# Frame-aligned 2D recreation — TeamWater reference

A new project based exclusively on the video supplied for this task. The earlier `Alan-Becker/UM-PIXEL.mp4` project and its files are preserved. The previous repository's 3D/Cozy Snow Plow visual reference is not used here.

Every one of the **4,078 source frames** is reconstructed as filled SVG paths and rendered at **1920×1080**, retaining **24000/1001 FPS** and source order. The original AAC soundtrack is copied once during final assembly. The input is 640×360: drawing the reconstructed paths in Full HD does not recover details absent from that file.

**This is image-derived, frame-by-frame vector reconstruction.** It is not a newly authored articulated rig, physical simulation, motion-capture system, or recovery of the author's original animation files. Paths approximate compressed raster artwork; pixel identity is not claimed. SVG drawings contain no embedded raster image or video texture, and no replacement story or gestures are invented.

## Files

- `../../video/teamwater-recriado-1080p.mp4`: complete film with original audio, delivered after validation.
- `assets/reference.mp4`: supplied input, required to reproduce this specific mapping.
- `src/run_all.py`: complete baseline → refinement → validation workflow.
- `src/recreate.py`: extraction, reconstruction, mapping, and multipart export.
- `src/refine.py`: higher-precision primary colored silhouettes and presentation panels, retained only when source-relative MSE improves.
- `vectors/part-*.zip`: editable SVG drawings, one per frame, using global indices.
- `analysis/reference.json`: metadata, hash, settings, and method limitations.
- `analysis/parts.json`: exact, nonoverlapping processing frame intervals.
- `analysis/part-*.json`: per-frame correspondence, color components, image changes, flow summaries, and camera/cut candidates.
- `analysis/flow-*.npz`: an 80×45 flow grid sampled every eight pixels from flow estimated at 640×360. Values use source pixels per frame. This is an observational estimate, not exact joint positions.
- `analysis/sequence-notes.json`: whole-source narrative overview with approximate time ranges.
- `analysis/reconstruction.json`: coverage and source-relative error measurements.
- `analysis/visual-comparison.jpg`: matched-time source/reconstruction samples spanning the source.
- `src/validate.py` and `analysis/validation.json`: complete MP4, coverage, vector archive, flow, and audio checks.

The mapping covers all frames and all 4,077 adjacent transitions. Color components are not guaranteed persistent character identities; affine camera estimates can be confounded by independent movement or parallax. Processing boundaries are not necessarily shot cuts. Each timestamp's SVG directly records the visible pose and framing of that source frame.

## Reproduce this case study

Requires Python 3.12, FFmpeg/FFprobe, and the system Cairo library. Install pinned dependencies in a virtual environment:

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/run_all.py
```

Paths resolve from the project directory. `.work/`, ignored by Git, stores extracted frames and temporary video parts. Match concurrency to the actual CPU/RAM quota. Completed parts may be resumed only with identical input/settings. Use a fresh workspace when changing the reference or tracing configuration; do not reuse incompatible caches.

This concrete example intentionally checks its input dimensions, FPS, and expected count. Before adapting it to another video, derive all dimensions, rational timing, flow-grid bounds, validation expectations, and output paths from that new input. Do not disable assertions and call the result validated.

The workflow requires no API key or AI service. Source artwork, names, marks, and audio remain those of the supplied reference; their inclusion does not attribute the original animation to this project.
