# Classified image dataset

Put training images here using **one subfolder per class label** (any subject: birds, animals, aircraft, etc.).

Examples:

- `training_data/classified_images/robin/`
- `training_data/classified_images/sparrow/`
- `training_data/classified_images/F35/` (military aircraft)

Notes:

- Folder names become class labels in the trained model.
- Use `.jpg`, `.jpeg`, or `.png` in source folders (training will auto-remove backgrounds and write processed PNGs under `training_data/processed_images/`).
- Keep label folder names stable between runs.

Start training (pixi installs dependencies including `rembg`):

- **Windows:** `scripts\launchers\train_model.bat`
- **macOS:** `./scripts/launchers/train_model.sh`

Output checkpoint defaults to `customized_model/`. Copy to `app_model/` when you want the gallery to use it.
