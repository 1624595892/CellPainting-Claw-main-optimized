# Changelog

## 0.1.0 - 2026-03-24

### Added

- Stable release helper scripts:
  - `scripts/run_release_smoke_test.sh`
  - `scripts/build_release_bundle.sh`
- Release documentation:
  - `docs/release_quickstart.md`
  - `docs/first_run_guide.md`
  - `RELEASE_NOTES.md`
- Portable distribution config template:
  - `configs/project_config.portable.example.json`
- Env-driven OpenClaw provider setup for AutoDL and Docker tracks.

### Changed

- Rewrote release-facing documentation in English.
- Standardized OpenClaw guidance around TUI-first usage.
- Updated Docker integration to use generic OpenAI-compatible provider environment variables instead of provider-specific hardcoding.
- Updated release packaging to exclude local runtime state and secret-bearing files.

### Removed

- Secret-bearing OpenClaw backup configs from the repository-managed tree.
- Local temporary build artifacts, caches, and leftover agent runtime state.

### Validated

- Release smoke test passes on the current validated environment.
- Source release bundle generation completes successfully.
