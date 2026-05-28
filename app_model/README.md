# App model (gallery classifier)

This folder holds the **ViT checkpoint SkySpotter uses in the app** for aircraft labels, gallery indexing, and Magic Wand.

- Ships with the default military-aircraft model.
- After training your own classes, copy your checkpoint here from `customized_model/` (see README → Customizing the Classifier).

Required files: `config.json`, `model.safetensors`, `preprocessor_config.json`, `labels.txt`.

Override location: `SkySpotter_APP_MODEL_DIR` (legacy: `SkySpotter_AIRCRAFT_CHECKPOINT_DIR`).
