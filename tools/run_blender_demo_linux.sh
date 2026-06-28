#!/usr/bin/env bash
set -e
python -m autowert_synthcars.cli render-demo --images 20 --output output/coco_dataset --engine eevee
