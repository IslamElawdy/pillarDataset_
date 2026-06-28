import numpy as np


def bbox_from_pixels(arr):
    rows, cols = np.nonzero(arr)
    if rows.size == 0 or cols.size == 0:
        return None
    x0 = float(cols.min())
    y0 = float(rows.min())
    x1 = float(cols.max())
    y1 = float(rows.max())
    return [x0, y0, x1 - x0 + 1.0, y1 - y0 + 1.0]


def area_from_pixels(arr):
    return float(np.count_nonzero(arr))


def rectangle_polygon_from_bbox(bbox):
    x, y, w, h = bbox
    return [x, y, x + w, y, x + w, y + h, x, y + h]
