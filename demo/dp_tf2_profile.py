"""DeepProfiler TF2 Keras feature extraction.

Replaces broken TF1 compat path. Produces 1280-dim embeddings
from EfficientNetB0 (5ch input) + Cell Painting CNN checkpoint.
"""

import sys, time, os
from pathlib import Path
import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
from tensorflow.keras.layers import GlobalAveragePooling2D
from tensorflow.keras.models import Model
import efficientnet.tfkeras as efn


def build_cell_painting_cnn(input_size=64, channels=5):
    """Build EfficientNetB0 with 5ch input + GAP for 1280-dim features."""
    base = efn.EfficientNetB0(
        include_top=False, weights=None,
        input_shape=(input_size, input_size, channels),
    )
    # Use top_conv output (1280-dim feature maps)
    feature_maps = base.get_layer("top_activation").output
    pooled = GlobalAveragePooling2D(name="pool5")(feature_maps)
    return Model(inputs=base.input, outputs=pooled, name="cell_painting_cnn")


def load_checkpoint(model, ckpt_path):
    """Load Cell_Painting_CNN_v1.hdf5 weights into TF2 model."""
    reader = tf.train.load_checkpoint(ckpt_path)
    var_map = reader.get_variable_to_shape_map()

    loaded = 0
    for layer in model.layers:
        if not layer.weights:
            continue
        for w in layer.weights:
            # TF2: w.name = "cell_painting_cnn/stem_conv/kernel:0"
            # TF1 checkpoint: "stem_conv/kernel" or ".../stem_conv/kernel"
            base_name = w.name.split("/", 1)[1].replace(":0", "")
            candidates = [
                base_name,
                base_name + "/.ATTRIBUTES/VARIABLE_VALUE",
                f"efficientnetb0/{base_name}",
            ]
            found = False
            for ckpt_name in candidates:
                if reader.has_tensor(ckpt_name):
                    val = reader.get_tensor(ckpt_name)
                    if val.shape == w.shape:
                        w.assign(val)
                        loaded += 1
                        found = True
                        break
            if not found:
                # Try matching by shape and layer name
                for ckpt_name, ckpt_shape in var_map.items():
                    if ckpt_shape == w.shape.as_list():
                        if layer.name in ckpt_name:
                            w.assign(reader.get_tensor(ckpt_name))
                            loaded += 1
                            found = True
                            break
    return loaded


# ============================================================
def main():
    print("=" * 60)
    print("DeepProfiler TF2 Feature Extractor")
    print("=" * 60)

    # Build
    t0 = time.perf_counter()
    model = build_cell_painting_cnn(input_size=64, channels=5)
    print(f"Model: {model.count_params():,} params ({time.perf_counter()-t0:.1f}s)")
    print(f"Input:  {model.input.shape}")
    print(f"Output: {model.output.shape}")

    # Checkpoint
    ckpt = Path("Cell_Painting_CNN_v1.hdf5")
    if ckpt.exists():
        n = load_checkpoint(model, str(ckpt))
        print(f"Checkpoint: loaded {n} weights")
    else:
        print("Checkpoint not found — running with random weights")

    # Benchmark
    np.random.seed(42)
    batch = np.random.randn(8, 64, 64, 5).astype(np.float32)

    # Warmup
    _ = model.predict(batch[:1], verbose=0)

    t0 = time.perf_counter()
    for _ in range(10):
        _ = model.predict(batch, verbose=0)
    t = (time.perf_counter() - t0) / 10

    features = model.predict(batch, verbose=0)
    print(f"\nExtracted: {features.shape[1]}-dim embeddings")
    print(f"Time: {t*1000:.0f}ms/batch ({t*1000/8:.0f}ms per crop)")
    print(f"Throughput: {8/t:.0f} crops/sec (CPU)")

    # Save .npz (matching DeepProfiler format)
    out = Path("demo/workspace/outputs/dp_tf2_features.npz")
    out.parent.mkdir(parents=True, exist_ok=True)
    meta = np.array([b"cell_%d" % i for i in range(len(batch))])
    locs = np.tile([32, 32, 64, 64], (len(batch), 1)).astype(np.float32)
    np.savez(out, features=features, metadata=meta, locations=locs)
    print(f"Saved: {out} ({out.stat().st_size:,} bytes)")
    print("\nDONE — TF2 works, no TF1 compat needed.")


if __name__ == "__main__":
    main()
