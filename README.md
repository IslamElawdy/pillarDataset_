# AutoWert Pillar Synthetic Dataset Generator

Synthetic Blender-based dataset generator for AutoWert vehicle-pillar instance segmentation.

The project creates RGB images and COCO Instance Segmentation annotations for training RF-DETR-Seg / RT-DETR-style instance-segmentation models for vehicle structural-part detection.

## Target classes

| id | class | purpose |
|---:|---|---|
| 1 | `pillar` | generic A/B/C/D pillar regions; A/B/C/D are assigned later by topology |
| 2 | `windshield` | front windshield |
| 3 | `side_window` | side windows |
| 4 | `rear_window` | rear window |
| 5 | `quarter_glass` | small triangular/quarter glass |
| 6 | `exterior_mirror` | side mirrors |
| 7 | `headlight` | front lights |
| 8 | `taillight` | rear lights |
| 9 | `wheel` | wheels |

Optional class, disabled by default:

| id | class |
|---:|---|
| 10 | `door_handle` |

## Important design decision

This repository does **not** ship third-party vehicle CAD/3D models. Instead, it provides two workflows:

1. **Procedural fallback vehicles** for immediate pipeline tests without external assets.
2. **Vehicle asset tagging workflow** for imported `.blend`, `.glb`, `.gltf`, `.fbx`, or `.obj` models once legally usable models are available.

The procedural fallback exists so the full COCO pipeline can be tested today, even when no real vehicle model is available.

## Output format

The generator writes RF-DETR-compatible COCO folders:

```text
output/coco_dataset/
├── train/
│   ├── _annotations.coco.json
│   └── *.jpg
├── valid/
│   ├── _annotations.coco.json
│   └── *.jpg
└── test/
    ├── _annotations.coco.json
    └── *.jpg
```

## Quick start

### 1. Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Linux
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt
pip install -e .
```

### 2. Install Blender

Install Blender 4.2 LTS or newer and ensure the `blender` executable is available on PATH.

### 3. Start the HTML UI

```bash
python scripts/run_ui.py
```

Open:

```text
http://127.0.0.1:8080
```

### 4. Generate a small demo dataset without vehicle models

```bash
autowert-synthcars render-demo --images 20 --output output/coco_dataset
```

If `blender` is not on PATH:

```bash
autowert-synthcars render-demo --images 20 --output output/coco_dataset --blender "C:/Program Files/Blender Foundation/Blender 4.2/blender.exe"
```

### 5. Validate COCO annotations

```bash
autowert-synthcars validate output/coco_dataset/train/_annotations.coco.json
```

### 6. Create preview overlays

```bash
autowert-synthcars visualize output/coco_dataset/train/_annotations.coco.json output/coco_dataset/train output/previews/train
```

## Current implementation status

Implemented in this initial version:

- Project structure
- COCO class mapping
- Blender headless orchestration
- Procedural vehicle fallback with labeled parts
- RGB rendering in Eevee, Cycles, or mixed mode
- COCO instance annotation writer
- Train/valid/test split
- COCO validator
- Overlay visualization tool
- FastAPI + plain HTML/CSS/JavaScript UI
- Windows/Linux launch scripts

Current technical limitation:

- The procedural fallback currently exports rectangle-style projected polygons from object bounds. This is enough to validate the complete pipeline and start experiments, but the next implementation step should replace this with real per-pixel object-color/Cryptomatte masks for production-quality instance segmentation.

Not included:

- Real vehicle 3D models
- Vendor model download automation
- Guaranteed production realism

## Why no CAD or 3D models are included?

Vehicle models are often license-restricted and may contain manufacturer IP, trademarks, or editorial-only license terms. This project therefore keeps asset acquisition separate and documented. Add legally usable models to:

```text
assets/vehicles_raw/
```

Then prepare/tag them into:

```text
assets/vehicles_tagged/
```

See `docs/ANNOTATION_AND_ASSET_WORKFLOW.md` for the planned tagging workflow.
