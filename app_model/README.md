# Legacy path: `app_model/`

Gallery classifier weights now live in the repository at:

**`models/gallery-classifier/skyspotter-military-aircraft-vit/`**

SkySpotter still checks this folder for backward compatibility. After training, copy your four checkpoint files here **or** into the `models/gallery-classifier/<your-id>/` layout and set `SkySpotter_GALLERY_CLASSIFIER_DIR`.

See [models/gallery-classifier/README.md](../models/gallery-classifier/README.md) for Git LFS pull instructions.
