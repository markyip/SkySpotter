import torch
import os
import sys
import json
import numpy as np
import evaluate
from pathlib import Path
from PIL import Image
from tqdm import tqdm

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from classifier_preprocess import build_processed_dataset  # noqa: E402
from datasets import Dataset, Features, ClassLabel, Image as DatasetImage
from transformers import (
    ViTForImageClassification, 
    ViTImageProcessor, 
    TrainingArguments, 
    Trainer,
    DefaultDataCollator,
    EarlyStoppingCallback
)
from torchvision.transforms import (
    CenterCrop,
    Compose,
    Normalize,
    RandomHorizontalFlip,
    RandomResizedCrop,
    Resize,
    ToTensor,
    ColorJitter
)

# --- CONFIGURATION ---
DATA_PATH = os.environ.get("SkySpotter_TRAIN_DATA_PATH", r"./training_data/classified_images")
PROCESSED_PATH = os.environ.get(
    "SkySpotter_TRAIN_PROCESSED_PATH", r"./training_data/processed_images"
)
# We use the high-resolution 384px ViT as our foundation
MODEL_ID = "google/vit-base-patch16-384"
OUTPUT_DIR = os.environ.get("SkySpotter_TRAIN_OUTPUT_DIR", r"./customized_model")

# --- GLOBAL TRANSFORMS (Required for Windows Multiprocessing) ---
# Hardcode 384px for high-resolution refinement
processor = ViTImageProcessor.from_pretrained(MODEL_ID)
RESOLUTION = 384
normalize = Normalize(mean=processor.image_mean, std=processor.image_std)

_train_transforms = Compose([
    RandomResizedCrop(RESOLUTION),
    RandomHorizontalFlip(),
    ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    ToTensor(),
    normalize,
])

_val_transforms = Compose([
    Resize(RESOLUTION),
    CenterCrop(RESOLUTION),
    ToTensor(),
    normalize,
])

def preprocess_train(examples):
    # This function must be at the global scope for Windows workers to pickle it
    examples["pixel_values"] = [_train_transforms(img.convert("RGB")) for img in examples["image"]]
    if "image" in examples:
        del examples["image"]
    return examples

def preprocess_val(examples):
    # This function must be at the global scope for Windows workers to pickle it
    examples["pixel_values"] = [_val_transforms(img.convert("RGB")) for img in examples["image"]]
    if "image" in examples:
        del examples["image"]
    return examples

def _load_training_image(path: Path) -> Image.Image:
    return Image.open(path)


def train():
    if not os.path.exists(DATA_PATH):
        print(f"ERROR: DATA_PATH not found at {DATA_PATH}")
        return

    source_root = Path(DATA_PATH)
    processed_root = Path(PROCESSED_PATH)
    print(f"--- Preprocessing training images (background removal + crop) ---")
    print(f"  Source:   {source_root}")
    print(f"  Processed: {processed_root}")

    def _progress(src_path: Path, status: str):
        tqdm.write(f"  {src_path.name}: {status}")

    saved, skipped = build_processed_dataset(
        source_root,
        processed_root,
        load_image=_load_training_image,
        progress_callback=_progress,
    )
    print(f"Preprocessing complete: {saved} saved, {skipped} skipped.")

    train_data_path = str(processed_root)
    if saved == 0 and not any(processed_root.rglob("*.png")):
        print("ERROR: No processed training images. Check source folders and rembg/pixi environment.")
        return

    print(f"--- Scanning Dataset: {train_data_path} ---")

    class_names = sorted(
        [
            d
            for d in os.listdir(train_data_path)
            if os.path.isdir(os.path.join(train_data_path, d))
        ]
    )
    
    if not class_names:
        print("ERROR: No subdirectories found in DATA_PATH!")
        return

    image_paths = []
    labels = []
    for label_idx, class_name in enumerate(class_names):
        class_dir = os.path.join(train_data_path, class_name)
        count = 0
        for f in os.listdir(class_dir):
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                image_paths.append(os.path.join(class_dir, f))
                labels.append(label_idx)
                count += 1
        if count > 0:
            print(f"  [+] Found {count} images for: {class_name}")

    if not image_paths:
        print("ERROR: No images found! Check if they are valid image formats (.jpg, .jpeg, .png).")
        return

    print(f"\nTotal images: {len(image_paths)} | Classes: {len(class_names)}")

    # 2. Create Dataset
    features = Features({"image": DatasetImage(), "label": ClassLabel(names=class_names)})
    raw_dataset = Dataset.from_dict({"image": image_paths, "label": labels}, features=features)
    dataset = raw_dataset.train_test_split(test_size=0.15, seed=42) # Increased val size
    
    id2label = {str(i): label for i, label in enumerate(class_names)}
    label2id = {label: str(i) for i, label in enumerate(class_names)}

    # Use with_transform for on-the-fly processing (Fixes RAM issues on Windows)
    train_ds = dataset["train"].with_transform(preprocess_train)
    val_ds = dataset["test"].with_transform(preprocess_val)

    # 4. Load Model
    print(f"\n--- Initializing Model from Foundation: {MODEL_ID} ---")
    model = ViTForImageClassification.from_pretrained(
        MODEL_ID,
        num_labels=len(class_names),
        id2label=id2label,
        label2id=label2id,
        ignore_mismatched_sizes=True 
    )
    if torch.cuda.is_available():
        accel = f"CUDA ({torch.cuda.get_device_name(0)})"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        accel = "MPS (Apple Metal)"
    else:
        accel = "CPU"
    print(f"--- Training accelerator: {accel} ---")

    # 5. Training Arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        remove_unused_columns=False, 
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=3e-5,
        per_device_train_batch_size=16, # lowered to 16 to be safer on typical GPUs
        gradient_accumulation_steps=2,  # effective batch size remains 32
        num_train_epochs=15,
        weight_decay=0.05,
        lr_scheduler_type="cosine",
        warmup_steps=500,
        logging_steps=10,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        save_total_limit=1,
        fp16=torch.cuda.is_available(),
        bf16=(not torch.cuda.is_available() and hasattr(torch.backends, "mps") and torch.backends.mps.is_available()),
        dataloader_num_workers=4,
        dataloader_pin_memory=True,
        dataloader_persistent_workers=True,
        tf32=True if torch.cuda.is_available() else False,
    )

    # 6. Metrics
    metric = evaluate.load("accuracy")
    def compute_metrics(p):
        return metric.compute(predictions=np.argmax(p.predictions, axis=1), references=p.label_ids)

    # 7. Run Training
    print("\n--- Starting Fine-Tuning (Combining Dataset + Base Knowledge) ---")
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=DefaultDataCollator(),
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )

    trainer.train()
    
    print("\n--- Evaluating Best Model ---")
    eval_results = trainer.evaluate()
    print(f"Final Accuracy: {eval_results.get('eval_accuracy', 0):.4f}")
    
    trainer.save_model()
    trainer.save_state() # Save trainer_state.json
    processor.save_pretrained(OUTPUT_DIR)
    
    # Save metrics to a file
    with open(os.path.join(OUTPUT_DIR, "all_results.json"), "w") as f:
        json.dump(eval_results, f, indent=4)
        
    with open(os.path.join(OUTPUT_DIR, "labels.txt"), "w") as f:
        f.write("\n".join(class_names))
        
    print(f"\nSUCCESS! Model saved to {OUTPUT_DIR}")
    print("Next steps:")
    print("  1. pixi run batch-test-classifier   # test on testing_data/test_images/")
    print("  2. When satisfied, copy checkpoint files to app_model/ for gallery use.")
    print("You can run 'python scripts/plot_training_history.py --model-dir customized_model' for training curves.")

if __name__ == "__main__":
    train()
