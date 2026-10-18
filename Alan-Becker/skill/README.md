# Reference-faithful 2D video clone

An English-language skill with its executable reference project included in `project/`.

- [Skill instructions](SKILL.md)
- [Method and limitations](references/method-and-limits.md)
- [Generalized failure-prevention guide](references/failure-prevention.md)
- [Project and reproduction commands](project/README.md)
- [Complete video](../video/teamwater-recriado-1080p.mp4)

Keep this entire folder together when sharing it. Compatible assistants load `SKILL.md` and its relative resources. For Codex, copy the folder into `$CODEX_HOME/skills/reference-faithful-2d-video-clone` (normally `~/.codex/skills/reference-faithful-2d-video-clone`), then restart the session if necessary. Invoke `$reference-faithful-2d-video-clone` with a new reference and the desired outputs.

The project is a case study, not a universal parameter-free cloner. Its source, frame rate, dimensions, and validation assumptions belong to that example. Adapt them from a new input before reuse. The workflow retains the current reference's drawing style; it does not apply the earlier 3D aesthetic.

No API key is required. Installed dependencies, caches, temporary parts, and extracted raster frames are excluded. The supplied video and its artwork/audio remain the original material, not newly authored content attributed to this project. See `project/analysis/reference.json` for its SHA-256 and technical provenance.
