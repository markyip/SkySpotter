# Customized classifier (your trained model)

After training, SkySpotter writes the checkpoint here by default:

- `config.json`
- `model.safetensors`
- `preprocessor_config.json`
- `labels.txt`

## Try before promoting to the gallery

1. Train with `scripts\launchers\train_model.bat` (Windows) or `./scripts/launchers/train_model.sh` (macOS).
2. Batch-test against `testing_data/test_images/`:
   ```bash
   pixi run batch-test-classifier
   ```
3. When results look good, **copy** (do not move until you are sure) these files into `models/gallery-classifier/skyspotter-military-aircraft-vit/` (or legacy `app_model/`) to use the model in the gallery.

The default weights live in `models/gallery-classifier/skyspotter-military-aircraft-vit/` on GitHub (Git LFS). Your customized checkpoint does not replace them until you copy files there yourself.
