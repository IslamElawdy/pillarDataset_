# Asset and tagging workflow

## Why this workflow exists

The project intentionally does not include third-party vehicle CAD or 3D models. Vehicle models can be license-restricted and often contain manufacturer marks. Therefore, the repository provides a safe workflow:

1. Run the procedural fallback generator to test the full COCO pipeline.
2. Add legally usable raw models to `assets/vehicles_raw/`.
3. Prepare each model once in Blender.
4. Store prepared models and metadata in `assets/vehicles_tagged/`.
5. Use the prepared models for large-scale rendering.

## Target classes

| id | name |
|---:|---|
| 1 | pillar |
| 2 | windshield |
| 3 | side_window |
| 4 | rear_window |
| 5 | quarter_glass |
| 6 | exterior_mirror |
| 7 | headlight |
| 8 | taillight |
| 9 | wheel |

## Manual preparation rules

### Pillars

Pillars are the most important and usually the hardest part. They are often not separate objects in downloaded models. If they are part of the body mesh, select the relevant faces in Blender and separate them into distinct objects.

Recommended object names:

```text
pillar_A_left
pillar_B_left
pillar_C_left
pillar_D_left
pillar_A_right
pillar_B_right
pillar_C_right
pillar_D_right
```

For training, all of them keep the same class id: `1 pillar`. The A/B/C/D names are only metadata for later topology validation.

### Glass

Separate or tag:

```text
windshield
side_window_front_left
side_window_rear_left
rear_window
quarter_glass_left
```

### Wheels, lights, mirrors

These are usually easier because they are often separate objects or materials. If needed, split them manually.

## Metadata format

Each prepared vehicle should contain a file similar to:

```json
{
  "vehicle_id": "vehicle_001",
  "source": "manual",
  "license_status": "to_be_checked",
  "objects": [
    {"object_name": "pillar_A_left", "class_id": 1, "class_name": "pillar", "instance_id": 1001, "semantic_hint": "A_pillar_left"},
    {"object_name": "windshield", "class_id": 2, "class_name": "windshield", "instance_id": 2001}
  ]
}
```

## First milestone without external models

Before preparing real vehicle assets, run:

```bash
autowert-synthcars render-demo --images 20 --output output/coco_dataset
```

This verifies that Blender, rendering, COCO export, and validation work on your machine.
