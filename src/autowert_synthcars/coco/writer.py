from .json_io import write_json


class CocoWriter:
    def __init__(self, categories):
        self.images = []
        self.items = []
        self.categories = []
        for item in categories:
            if item.get("enabled", True):
                self.categories.append({"id": int(item["id"]), "name": str(item["name"]), "supercategory": str(item.get("supercategory", "vehicle"))})
        self.next_image_id = 1
        self.next_item_id = 1

    def add_image(self, file_name, width, height):
        image_id = self.next_image_id
        self.next_image_id = self.next_image_id + 1
        self.images.append({"id": image_id, "file_name": file_name, "width": width, "height": height})
        return image_id

    def add_item(self, image_id, category_id, bbox, polygon, area):
        item_id = self.next_item_id
        self.next_item_id = self.next_item_id + 1
        self.items.append({"id": item_id, "image_id": image_id, "category_id": int(category_id), "bbox": bbox, "segmentation": [polygon], "area": float(area), "iscrowd": 0})
        return item_id

    def to_dict(self):
        return {"info": {"description": "AutoWert synthetic dataset", "version": "0.1.0"}, "licenses": [], "images": self.images, "annotations": self.items, "categories": self.categories}

    def save(self, path):
        write_json(self.to_dict(), path)
