import argparse
import json
import math
import os
import random
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

THIS_FILE = Path(__file__).resolve()
SRC_ROOT = THIS_FILE.parents[2]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from autowert_synthcars.blender.procedural_vehicle import CLASS_IDS, create_procedural_vehicle

CATEGORIES = [
    {"id": 1, "name": "pillar", "supercategory": "structure"},
    {"id": 2, "name": "windshield", "supercategory": "glass"},
    {"id": 3, "name": "side_window", "supercategory": "glass"},
    {"id": 4, "name": "rear_window", "supercategory": "glass"},
    {"id": 5, "name": "quarter_glass", "supercategory": "glass"},
    {"id": 6, "name": "exterior_mirror", "supercategory": "vehicle_part"},
    {"id": 7, "name": "headlight", "supercategory": "light"},
    {"id": 8, "name": "taillight", "supercategory": "light"},
    {"id": 9, "name": "wheel", "supercategory": "vehicle_part"},
]


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def setup_render(width, height, engine):
    scene = bpy.context.scene
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.film_transparent = False
    if engine.lower() == "cycles":
        scene.render.engine = "CYCLES"
        scene.cycles.samples = 64
        scene.cycles.use_denoising = True
        try:
            scene.cycles.device = "GPU"
        except Exception:
            pass
    else:
        scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_camera(seed):
    rng = random.Random(seed)
    az = math.radians(rng.choice([rng.uniform(-135, -35), rng.uniform(35, 135)]))
    el = math.radians(rng.uniform(8, 24))
    dist = rng.uniform(7.0, 12.0)
    x = math.cos(az) * math.cos(el) * dist
    y = math.sin(az) * math.cos(el) * dist
    z = math.sin(el) * dist + 0.8
    bpy.ops.object.camera_add(location=(x, y, z))
    cam = bpy.context.object
    cam.name = "camera"
    cam.data.lens = rng.uniform(30, 50)
    look_at(cam, (0, 0, 0.9))
    bpy.context.scene.camera = cam
    return cam


def setup_lighting(seed):
    rng = random.Random(seed)
    bpy.context.scene.world.color = (rng.uniform(0.55, 0.95), rng.uniform(0.55, 0.95), rng.uniform(0.55, 0.95))
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 8))
    sun = bpy.context.object
    sun.name = "sun"
    sun.data.energy = rng.uniform(1.0, 4.5)
    sun.rotation_euler = (math.radians(rng.uniform(25, 65)), 0, math.radians(rng.uniform(0, 360)))
    if rng.random() < 0.4:
        bpy.ops.object.light_add(type="AREA", location=(rng.uniform(-3, 3), rng.uniform(-4, 4), rng.uniform(3, 5)))
        area = bpy.context.object
        area.name = "area_fill"
        area.data.energy = rng.uniform(150, 450)
        area.data.size = rng.uniform(3, 6)


def setup_ground(seed):
    rng = random.Random(seed)
    material = bpy.data.materials.new("ground_random")
    material.diffuse_color = rng.choice([(0.35, 0.35, 0.35, 1), (0.18, 0.18, 0.18, 1), (0.45, 0.42, 0.38, 1)])
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
    ground = bpy.context.object
    ground.name = "ground"
    ground.data.materials.append(material)


def object_bbox_polygon(obj, camera, width, height):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    coords = []
    for corner in obj_eval.bound_box:
        world = obj_eval.matrix_world @ Vector(corner)
        ndc = world_to_camera_view(bpy.context.scene, camera, world)
        if ndc.z < 0:
            continue
        x = ndc.x * width
        y = (1.0 - ndc.y) * height
        coords.append((x, y))
    if not coords:
        return None
    xs = [max(0.0, min(width - 1.0, p[0])) for p in coords]
    ys = [max(0.0, min(height - 1.0, p[1])) for p in coords]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    if x1 - x0 < 2 or y1 - y0 < 2:
        return None
    bbox = [x0, y0, x1 - x0, y1 - y0]
    polygon = [x0, y0, x1, y0, x1, y1, x0, y1]
    area = (x1 - x0) * (y1 - y0)
    return bbox, polygon, area


def choose_split(index):
    r = index % 10
    if r == 8:
        return "valid"
    if r == 9:
        return "test"
    return "train"


def render_one(index, output_root, width, height, engine):
    seed = 100000 + index
    clear_scene()
    setup_render(width, height, engine)
    setup_ground(seed)
    objects = create_procedural_vehicle(seed=seed)
    cam = setup_camera(seed)
    setup_lighting(seed)

    split = choose_split(index)
    split_dir = output_root / split
    split_dir.mkdir(parents=True, exist_ok=True)
    file_name = f"synthetic_{index:06d}.jpg"
    bpy.context.scene.render.filepath = str(split_dir / file_name)
    bpy.ops.render.render(write_still=True)

    image_item = {"id": index + 1, "file_name": file_name, "width": width, "height": height}
    annotations = []
    ann_base = (index + 1) * 1000
    ann_offset = 1
    for obj in objects:
        if "class_id" not in obj:
            continue
        result = object_bbox_polygon(obj, cam, width, height)
        if result is None:
            continue
        bbox, polygon, area = result
        if area < 100:
            continue
        annotations.append({
            "id": ann_base + ann_offset,
            "image_id": image_item["id"],
            "category_id": int(obj["class_id"]),
            "bbox": bbox,
            "segmentation": [polygon],
            "area": area,
            "iscrowd": 0,
        })
        ann_offset += 1
    return split, image_item, annotations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--images", type=int, default=20)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--engine", choices=["eevee", "cycles", "mixed"], default="eevee")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None)

    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)
    data = {split: {"info": {"description": "AutoWert procedural synthetic dataset"}, "licenses": [], "images": [], "annotations": [], "categories": CATEGORIES} for split in ["train", "valid", "test"]}

    for i in range(args.images):
        if args.engine == "mixed":
            engine = "cycles" if i % 5 == 0 else "eevee"
        else:
            engine = args.engine
        split, image_item, annotations = render_one(i, output_root, args.width, args.height, engine)
        data[split]["images"].append(image_item)
        data[split]["annotations"].extend(annotations)

    for split, payload in data.items():
        split_dir = output_root / split
        split_dir.mkdir(parents=True, exist_ok=True)
        with (split_dir / "_annotations.coco.json").open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)


if __name__ == "__main__":
    main()
