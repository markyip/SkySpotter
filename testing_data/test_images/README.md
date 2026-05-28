# Test images for model verification

Place **held-out** sample photos here (ideally photos **not** used in `training_data/classified_images/`).

**Run** (from project root): `scripts\launchers\verify_model.bat` (Windows) or `./scripts/launchers/verify_model.sh` (macOS)

**Review**

1. `../test_output/pipeline_images/` — subject crop looks right
2. `../test_output/top3_detection_scores.csv` — `top1_label` and `top1_score` look reasonable

See README → **Customizing the Classifier → 3. Test your model** for full steps.
