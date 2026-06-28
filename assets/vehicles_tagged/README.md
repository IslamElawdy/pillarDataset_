# Tagged vehicle models

Prepared Blender files and metadata will be stored here.

Expected structure per vehicle:

```text
vehicles_tagged/
└── vehicle_001/
    ├── vehicle_001_tagged.blend
    └── model_meta.json
```

`model_meta.json` maps Blender objects to dataset classes and instance IDs.

The initial implementation also supports a procedural fallback, so this folder may remain empty while testing the pipeline.
