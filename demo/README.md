# Demo Backend

This directory contains a **sanitized minimal demo backend** for CellPainting-Claw.

It is intentionally small and self-contained. The demo bundle includes:

- synthetic CPJUMP-style raw TIFF images
- minimal profiling metadata and CellProfiler-style tables
- CellProfiler `.cppipe` files copied into a repo-local demo backend
- a minimal segmentation backend with precomputed label masks and measurement tables
- a repo-local project config at `configs/project_config.demo.json`

The demo bundle is designed for **public validation of the toolkit surface**. It does not represent a biological dataset and is not intended for scientific interpretation.

Recommended public demo entry points from the repository root:

```bash
CONFIG=configs/project_config.demo.json
DATA_ROOT=demo/workspace/outputs/quick_start_data
RUN_ROOT=demo/workspace/outputs/quick_start_classical

cellpainting-skills run \
  --config "$CONFIG" \
  --skill data-inspect-availability \
  --output-dir "$DATA_ROOT/01_inspect"

cellpainting-skills run \
  --config "$CONFIG" \
  --skill cp-extract-measurements \
  --output-dir "$RUN_ROOT/01_measurements"
```

The public documentation now uses this demo backend in two ways:

- data-access skills for Gallery inspection, planning, and bounded downloads
- classical profiling skills for CellProfiler tables, single-cell export, and pycytominer outputs

The profiling demo backend currently packages a minimal validated measurement result set directly in the repository. In the public demo checkout, `cp-extract-measurements` therefore reuses these bundled tables when the original backend script is not present.
