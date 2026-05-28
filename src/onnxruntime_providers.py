"""Shared ONNX Runtime provider selection (DirectML on Windows, etc.)."""

from __future__ import annotations

import os
import sys
from typing import List, Optional


def dml_available() -> bool:
    try:
        import onnxruntime as ort

        return "DmlExecutionProvider" in ort.get_available_providers()
    except Exception:
        return False


def onnxruntime_providers_prefer_dml() -> List[str]:
    """
    Provider order for inference sessions.

    Override with SkySpotter_ORT_PROVIDERS=DmlExecutionProvider,CPUExecutionProvider
  """
    import onnxruntime as ort

    available = set(ort.get_available_providers())
    custom = os.environ.get("SkySpotter_ORT_PROVIDERS", "").strip()
    if custom:
        picked = [p.strip() for p in custom.split(",") if p.strip() in available]
        if picked:
            return picked

    if sys.platform == "darwin":
        order = [
            "CoreMLExecutionProvider",
            "CUDAExecutionProvider",
            "DmlExecutionProvider",
            "CPUExecutionProvider",
        ]
    elif sys.platform == "win32":
        order = [
            "CUDAExecutionProvider",
            "DmlExecutionProvider",
            "CPUExecutionProvider",
        ]
    else:
        order = ["CUDAExecutionProvider", "CPUExecutionProvider"]

    selected = [p for p in order if p in available]
    return selected or ["CPUExecutionProvider"]


def create_onnxruntime_session(model_path: str, providers: Optional[List[str]] = None):
    """Create an InferenceSession with options suited for DirectML when used."""
    import onnxruntime as ort

    providers = providers or onnxruntime_providers_prefer_dml()
    so = ort.SessionOptions()
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    if "DmlExecutionProvider" in providers:
        so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        so.enable_mem_pattern = False
    return ort.InferenceSession(model_path, sess_options=so, providers=providers)


def prefer_directml_classifier() -> bool:
    """Whether to run the ViT aircraft model via ONNX + DirectML instead of PyTorch."""
    override = os.environ.get("SkySpotter_CLASSIFIER_DEVICE", "").strip().lower()
    if override in ("dml", "directml", "ort-dml"):
        return dml_available()
    if override in ("cuda", "cpu", "mps", "torch"):
        return False
    if sys.platform != "win32":
        return False
    flag = os.environ.get("SkySpotter_PREFER_DIRECTML", "1").strip().lower()
    if flag in ("0", "false", "no", "off"):
        return False
    return dml_available()
