# Classified Image Dataset Template

Put your training images here using one subfolder per class label.

Example:

- `training_data/classified_images/F35/`
- `training_data/classified_images/F16/`
- `training_data/classified_images/AH64/`

Notes:

- Folder names become the output class labels.
- Use image files such as `.jpg`, `.jpeg`, `.png` (and `.arw` if needed).
- Keep labels stable between runs to avoid changing class index mapping unexpectedly.

Start training:

- Windows: `train_model.bat`
- macOS/Linux: `./train_model.sh`
