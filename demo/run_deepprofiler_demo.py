"""DeepProfiler v0.5.1 optimized demo — extract features from synthetic images."""
import time, sys, os, tempfile, json, subprocess
import numpy as np
import pandas as pd
from pathlib import Path
from PIL import Image

tmp = Path(tempfile.mkdtemp(prefix="dp_optimized_"))
print(f"Project root: {tmp}")

# --- Create project structure ---
for d in ["inputs/config", "inputs/metadata", "inputs/locations", "inputs/images",
          "outputs/demo/features", "outputs/demo/checkpoint", "outputs/demo/logs"]:
    (tmp / d).mkdir(parents=True)

# --- Config ---
config = {
    "dataset": {
        "metadata": {"label_field": "Class", "control_value": "DMSO"},
        "images": {"channels": ["DNA", "RNA", "ER", "AGP", "Mito"],
                   "file_format": "tif", "bits": 16, "width": 64, "height": 64},
        "locations": {"mode": "single_cells", "box_size": 32, "mask_objects": False},
    },
    "prepare": {"compression": {"implement": False, "scaling_factor": 1.0}},
    "profile": {"feature_layer": "block6a_activation", "checkpoint": "None", "batch_size": 64},
    "train": {
        "partition": {"targets": ["Class"]},
        "model": {
            "name": "efficientnet", "crop_generator": "crop_generator",
            "initialization": "random",
            "params": {"conv_blocks": 0, "learning_rate": 0.0001,
                       "batch_size": 64, "label_smoothing": 0.0},
        },
        "validation": {"batch_size": 64},
        "sampling": {"factor": 1.0, "cache_size": 64, "workers": 1, "alpha": 0.2},
    },
}
with open(tmp / "inputs/config/demo_config.json", "w") as f:
    json.dump(config, f, indent=2)

# --- Metadata ---
metadata = pd.DataFrame({
    "Metadata_Plate": ["Plate1", "Plate1"],
    "Metadata_Well": ["A01", "A01"],
    "Metadata_Site": ["1", "1"],
    "DNA": ["fake_DNA.tif", "fake_DNA.tif"],
    "RNA": ["fake_RNA.tif", "fake_RNA.tif"],
    "ER": ["fake_ER.tif", "fake_ER.tif"],
    "AGP": ["fake_AGP.tif", "fake_AGP.tif"],
    "Mito": ["fake_Mito.tif", "fake_Mito.tif"],
    "Class": ["DMSO", "DMSO"],
})
metadata.to_csv(tmp / "inputs/metadata/index.csv", index=False)

# --- Locations ---
loc_dir = tmp / "inputs/locations/Plate1"
loc_dir.mkdir(parents=True, exist_ok=True)
locations = pd.DataFrame({
    "Nuclei_Location_Center_X": [32, 48],
    "Nuclei_Location_Center_Y": [32, 48],
})
locations.to_csv(loc_dir / "A01-1-Nuclei.csv", index=False)

# --- Synthetic images ---
img_dir = tmp / "inputs/images/Plate1"
img_dir.mkdir(parents=True, exist_ok=True)
for ch in ["DNA", "RNA", "ER", "AGP", "Mito"]:
    arr = np.random.randint(0, 65535, (64, 64), dtype=np.uint16)
    Image.fromarray(arr).save(img_dir / f"fake_{ch}.tif")

print(f"Setup: {len(metadata)} images, {len(locations)} cells, 5 channels, 64x64 uint16")
print()

# --- Run DeepProfiler profile ---
dp_exe = "D:/MINICONDA/envs/cellpainting-claw/Scripts/deepprofiler.exe"
cmd = [dp_exe, f"--root={tmp}", "--config=demo_config.json",
       "--exp=demo", "--metadata=index.csv", "--gpu=-1", "profile"]

print("Running: " + " ".join(cmd))
print()
t0 = time.perf_counter()
env = {**os.environ, "CUDA_VISIBLE_DEVICES": "", "TF_CPP_MIN_LOG_LEVEL": "2"}
result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env)
elapsed = time.perf_counter() - t0

# --- Results ---
feat_dir = tmp / "outputs/demo/features"
if result.returncode == 0 and feat_dir.exists():
    print(f"=== DeepProfiler v0.5.1 (OPTIMIZED) ===")
    print(f"Status: SUCCESS (exit {result.returncode})")
    print(f"Time: {elapsed:.1f}s")
    print()
    for f in sorted(feat_dir.iterdir()):
        if f.suffix == ".npz":
            data = np.load(f)
            print(f"Output: {f.name} ({f.stat().st_size:,} bytes)")
            print(f"  Features: {data['features'].shape} (1280-dim embeddings)")
            print(f"  Locations: {data['locations'].shape}")
    print()
    print("Optimizations applied: np.savez (#2), np.stack (#3), skip-concat (#10), prefetch (#1)")
else:
    print(f"FAILED: exit {result.returncode}")
    print("STDERR:", result.stderr[-1000:])

# Cleanup
import shutil
shutil.rmtree(tmp, ignore_errors=True)
print()
print("DONE")
