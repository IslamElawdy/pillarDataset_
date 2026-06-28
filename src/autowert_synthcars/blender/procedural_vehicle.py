import math
import random

import bpy
from mathutils import Vector


CLASS_IDS = {
    "pillar": 1,
    "windshield": 2,
    "side_window": 3,
    "rear_window": 4,
    "quarter_glass": 5,
    "exterior_mirror": 6,
    "headlight": 7,
    "taillight": 8,
    "wheel": 9,
}


COLOR_BY_CLASS = {
    1: (1.0, 0.0, 0.45, 1.0),
    2: (0.0, 0.8, 0.8, 1.0),
    3: (0.0, 0.35, 1.0, 1.0),
    4: (0.6, 0.25, 0.9, 1.0),
    5: (0.2, 0.8, 0.2, 1.0),
    6: (1.0, 0.75, 0.0, 1.0),
    7: (1.0, 0.35, 0.0, 1.0),
    8: (1.0, 0.0, 0.0, 1.0),
    9: (0.0, 0.2, 1.0, 1.0),
}


def make_material(name, color, roughness=0.45, metallic=0.0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = color[3]
    material.diffuse_color = color
    return material


def cube_object(name, location, scale, material, class_name=None, instance_id=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    if class_name is not None:
        class_id = CLASS_IDS[class_name]
        obj["class_name"] = class_name
        obj["class_id"] = class_id
        obj["instance_id"] = instance_id if instance_id is not None else class_id * 1000
    return obj


def wheel_object(name, location, radius, width, material, instance_id):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=width, location=location, rotation=(math.pi / 2, 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    obj["class_name"] = "wheel"
    obj["class_id"] = CLASS_IDS["wheel"]
    obj["instance_id"] = instance_id
    return obj


def create_procedural_vehicle(seed=0):
    rng = random.Random(seed)
    body_color = rng.choice([
        (0.95, 0.95, 0.92, 1.0),
        (0.02, 0.02, 0.02, 1.0),
        (0.55, 0.58, 0.62, 1.0),
        (0.75, 0.04, 0.03, 1.0),
        (0.03, 0.12, 0.45, 1.0),
    ])

    body = make_material("body_random", body_color, roughness=rng.uniform(0.2, 0.65), metallic=rng.uniform(0.0, 0.45))
    dark = make_material("dark_trim", (0.02, 0.02, 0.025, 1.0))
    glass_front = make_material("glass_front", (0.0, 0.75, 0.80, 0.55))
    glass_side = make_material("glass_side", (0.0, 0.25, 0.95, 0.55))
    glass_rear = make_material("glass_rear", (0.45, 0.20, 0.80, 0.55))
    glass_quarter = make_material("glass_quarter", (0.1, 0.65, 0.15, 0.55))
    pillar_mat = make_material("pillar_label_body", body_color)
    mirror_mat = make_material("mirror", (0.95, 0.72, 0.0, 1.0))
    head_mat = make_material("headlight", (1.0, 0.45, 0.02, 1.0))
    tail_mat = make_material("taillight", (1.0, 0.02, 0.02, 1.0))
    wheel_mat = make_material("wheel", (0.03, 0.03, 0.035, 1.0))

    objects = []
    length = rng.uniform(4.4, 5.2)
    height = rng.uniform(1.35, 1.75)
    width = rng.uniform(1.7, 2.05)

    objects.append(cube_object("body_lower", (0, 0, 0.65), (length / 2, width / 2, 0.42), body))
    objects.append(cube_object("body_upper", (-0.15, 0, 1.18), (length * 0.34, width * 0.44, 0.34), body))

    # Windows and glass regions on visible side and center roof line.
    side_y = -width / 2 - 0.012
    objects.append(cube_object("windshield", (-1.55, side_y, 1.34), (0.38, 0.015, 0.32), glass_front, "windshield", 2001))
    objects.append(cube_object("side_window_front", (-0.70, side_y, 1.36), (0.42, 0.015, 0.30), glass_side, "side_window", 3001))
    objects.append(cube_object("side_window_rear", (0.25, side_y, 1.36), (0.48, 0.015, 0.30), glass_side, "side_window", 3002))
    objects.append(cube_object("quarter_glass", (1.05, side_y, 1.34), (0.22, 0.015, 0.28), glass_quarter, "quarter_glass", 5001))
    objects.append(cube_object("rear_window", (1.55, side_y, 1.30), (0.22, 0.015, 0.31), glass_rear, "rear_window", 4001))

    # Pillars as separate labelable geometry.
    pillar_xs = [-1.10, -0.25, 0.80, 1.30]
    for index, px in enumerate(pillar_xs, start=1):
        objects.append(cube_object(f"pillar_{index}", (px, side_y - 0.01, 1.32), (0.055, 0.025, 0.43), pillar_mat, "pillar", 1000 + index))

    # Mirror, lights, wheels.
    objects.append(cube_object("left_mirror", (-1.23, side_y - 0.18, 1.18), (0.16, 0.08, 0.07), mirror_mat, "exterior_mirror", 6001))
    objects.append(cube_object("headlight_left", (-length / 2 - 0.02, side_y - 0.02, 0.86), (0.08, 0.10, 0.07), head_mat, "headlight", 7001))
    objects.append(cube_object("taillight_left", (length / 2 + 0.02, side_y - 0.02, 0.88), (0.08, 0.10, 0.08), tail_mat, "taillight", 8001))

    wheel_positions = [(-1.55, -width / 2, 0.38), (1.55, -width / 2, 0.38), (-1.55, width / 2, 0.38), (1.55, width / 2, 0.38)]
    for idx, position in enumerate(wheel_positions, start=1):
        objects.append(wheel_object(f"wheel_{idx}", position, 0.36, 0.18, wheel_mat, 9000 + idx))

    return objects
