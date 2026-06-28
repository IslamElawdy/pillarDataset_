import json
from pathlib import Path

from PIL import Image, ImageDraw


COLORS = {
    1: (255, 0, 128),
    2: (0, 200, 200),
    3: (0, 120, 255),
    4: (150, 80, 220),
    5: (80, 180, 40),
    6: (245, 180, 0),
    7: (255, 120, 0),
    8: (255, 0, 0),
    9: (0, 80, 255),
}


def visualize(coco_json, image_dir, output_dir, limit=50):
    coco_json = Path(coco_json)
    image_dir = Path(image_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with coco_json.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    images = {item["id"]: item for item in data.get("images", [])}
    by_image = {}
    for item in data.get("annotations", []):
        by_image.setdefault(item["image_id"], []).append(item)

    written = 0
    for image_id, img in images.items():
        if written >= limit:
            break
        path = image_dir / img["file_name"]
        if not path.exists():
            continue
        image = Image.open(path).convert("RGBA")
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for ann in by_image.get(image_id, []):
            color = COLORS.get(int(ann["category_id"]), (255, 255, 0))
            rgba = (color[0], color[1], color[2], 90)
            for poly in ann.get("segmentation", []):
                pts = [(poly[i], poly[i + 1]) for i in range(0, len(poly), 2)]
                if len(pts) >= 3:
                    draw.polygon(pts, fill=rgba, outline=(color[0], color[1], color[2], 255))
            x, y, w, h = ann.get("bbox", [0, 0, 0, 0])
            draw.rectangle([x, y, x + w, y + h], outline=(color[0], color[1], color[2], 255), width=2)
        result = Image.alpha_composite(image, overlay).convert("RGB")
        result.save(output_dir / img["file_name"])
        written += 1
    return written
