import json
from pathlib import Path


def validate_coco_file(path):
    path = Path(path)
    errors = []
    warnings = []
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    for key in ["images", "annotations", "categories"]:
        if key not in data:
            errors.append(f"Missing key: {key}")

    images = data.get("images", [])
    anns = data.get("annotations", [])
    cats = data.get("categories", [])

    image_ids = {item.get("id") for item in images}
    category_ids = {item.get("id") for item in cats}

    for img in images:
        if not img.get("file_name"):
            errors.append(f"Image has no file_name: {img}")
        if int(img.get("width", 0)) <= 0 or int(img.get("height", 0)) <= 0:
            errors.append(f"Image has invalid size: {img}")

    for ann in anns:
        if ann.get("image_id") not in image_ids:
            errors.append(f"Annotation references missing image_id: {ann.get('id')}")
        if ann.get("category_id") not in category_ids:
            errors.append(f"Annotation references missing category_id: {ann.get('id')}")
        if float(ann.get("area", 0)) <= 0:
            errors.append(f"Annotation has invalid area: {ann.get('id')}")
        bbox = ann.get("bbox", [])
        if len(bbox) != 4:
            errors.append(f"Annotation has invalid bbox: {ann.get('id')}")
        seg = ann.get("segmentation", [])
        if not seg:
            warnings.append(f"Annotation has no segmentation: {ann.get('id')}")

    return {"path": str(path), "images": len(images), "annotations": len(anns), "categories": len(cats), "errors": errors, "warnings": warnings, "ok": not errors}


def print_report(report):
    print(f"COCO file: {report['path']}")
    print(f"Images: {report['images']}")
    print(f"Annotations: {report['annotations']}")
    print(f"Categories: {report['categories']}")
    print(f"OK: {report['ok']}")
    if report["errors"]:
        print("Errors:")
        for item in report["errors"]:
            print(f"  - {item}")
    if report["warnings"]:
        print("Warnings:")
        for item in report["warnings"]:
            print(f"  - {item}")
