from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from autowert_synthcars.coco.validate_coco import print_report, validate_coco_file
from autowert_synthcars.coco.visualize_coco import visualize


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BLENDER_ENTRY = PROJECT_ROOT / "src" / "autowert_synthcars" / "blender" / "blender_entry.py"


def run_render_demo(args):
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    blender = args.blender or "blender"
    command = [
        blender,
        "--background",
        "--python",
        str(BLENDER_ENTRY),
        "--",
        "--output",
        str(output),
        "--images",
        str(args.images),
        "--width",
        str(args.width),
        "--height",
        str(args.height),
        "--engine",
        str(args.engine),
    ]
    print("Running Blender command:")
    print(" ".join(command))
    subprocess.run(command, check=True)


def run_validate(args):
    report = validate_coco_file(args.coco_json)
    print_report(report)
    if not report["ok"]:
        raise SystemExit(1)


def run_visualize(args):
    written = visualize(args.coco_json, args.image_dir, args.output_dir, args.limit)
    print(f"Wrote {written} preview images to {args.output_dir}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="AutoWert synthetic COCO dataset generator")
    sub = parser.add_subparsers(dest="command", required=True)

    render = sub.add_parser("render-demo", help="Generate a procedural Blender demo dataset without external 3D models")
    render.add_argument("--output", default="output/coco_dataset")
    render.add_argument("--images", type=int, default=20)
    render.add_argument("--width", type=int, default=1920)
    render.add_argument("--height", type=int, default=1080)
    render.add_argument("--engine", choices=["eevee", "cycles", "mixed"], default="eevee")
    render.add_argument("--blender", default=None, help="Path to Blender executable")
    render.set_defaults(func=run_render_demo)

    validate = sub.add_parser("validate", help="Validate a COCO JSON file")
    validate.add_argument("coco_json")
    validate.set_defaults(func=run_validate)

    preview = sub.add_parser("visualize", help="Create overlay preview images from COCO annotations")
    preview.add_argument("coco_json")
    preview.add_argument("image_dir")
    preview.add_argument("output_dir")
    preview.add_argument("--limit", type=int, default=50)
    preview.set_defaults(func=run_visualize)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
