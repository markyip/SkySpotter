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


def torch_gpu_available() -> bool:
    """True when PyTorch can run on CUDA or Apple MPS."""
    try:
        import torch
    except ImportError:
        return False
    if torch.cuda.is_available():
        return True
    return bool(getattr(torch.backends, "mps", None) and torch.backends.mps.is_available())


def onnxruntime_providers_for_rembg() -> List[str]:
    """
    Provider order for rembg / U2-Net background removal.

    Defaults to DirectML/CUDA when available. Set ``SkySpotter_REMBG_CPU=1`` for CPU-only.
    """
    force_cpu = os.environ.get("SkySpotter_REMBG_CPU", "").strip().lower()
    if force_cpu in ("1", "true", "yes", "on"):
        return ["CPUExecutionProvider"]
    return onnxruntime_providers_prefer_dml()


def rembg_uses_directml() -> bool:
    """True when rembg/U2-Net is configured to use DirectML."""
    try:
        return "DmlExecutionProvider" in onnxruntime_providers_for_rembg()
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
    """
    Whether to run the ViT aircraft model via ONNX + DirectML instead of PyTorch.

    Default: PyTorch on CUDA/MPS (better accuracy, matches training preprocessing).
    DirectML ONNX is used only as a fallback when no PyTorch GPU is available, or when
    ``SkySpotter_PREFER_DIRECTML=1`` / ``SkySpotter_CLASSIFIER_DEVICE=dml`` is set.
    """
    override = os.environ.get("SkySpotter_CLASSIFIER_DEVICE", "").strip().lower()
    if override in ("dml", "directml", "ort-dml"):
        return dml_available()
    if override in ("cuda", "cpu", "mps", "torch"):
        return False

    flag = os.environ.get("SkySpotter_PREFER_DIRECTML", "").strip().lower()
    if flag in ("1", "true", "yes", "on"):
        return dml_available()
    if flag in ("0", "false", "no", "off"):
        return False

    if torch_gpu_available():
        return False

    # No working PyTorch GPU: prefer DirectML on Windows (AMD/Intel/iGPU or CPU-only).
    if sys.platform == "win32" and dml_available():
        return True
    return False


def classifier_backend_name() -> str:
    """Human-readable active aircraft classifier backend."""
    if prefer_directml_classifier():
        return "directml-onnx"
    try:
        import torch

        device = _resolve_classifier_torch_device_name()
        if device == "cuda":
            return f"pytorch-cuda ({torch.cuda.get_device_name(0)})"
        if device == "mps":
            return "pytorch-mps"
        return "pytorch-cpu"
    except ImportError:
        return "unavailable"


def _resolve_classifier_torch_device_name() -> str:
    import torch

    override = os.environ.get("SkySpotter_CLASSIFIER_DEVICE", "").strip().lower()
    if override == "cpu":
        return "cpu"
    if override == "cuda":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if override == "mps":
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def gpu_vram_gib() -> Optional[float]:
    """CUDA device memory in GiB, or None when unavailable."""
    try:
        import torch

        if torch.cuda.is_available():
            return float(torch.cuda.get_device_properties(0).total_memory) / (1024**3)
    except Exception:
        pass
    return None


def suggested_aircraft_classify_workers() -> int:
    """
    Parallel index workers from GPU VRAM and rembg backend.

    ViT (PyTorch CUDA) + rembg (DirectML) share the GPU; default **2 workers** on
    11+ GiB cards. rembg on CPU allows higher parallelism. Override with
    ``SkySpotter_AIRCRAFT_CLASSIFY_WORKERS``.
    """
    raw = os.environ.get("SkySpotter_AIRCRAFT_CLASSIFY_WORKERS", "").strip()
    if raw:
        try:
            return max(1, min(8, int(raw)))
        except ValueError:
            pass

    dml_rembg = rembg_uses_directml()
    try:
        import torch

        if torch.cuda.is_available():
            gib = float(torch.cuda.get_device_properties(0).total_memory) / (1024**3)
            if dml_rembg and not prefer_directml_classifier():
                # CUDA ViT + DirectML rembg: conservative (ORT DML is not re-entrant).
                if gib >= 11:
                    return 2
                return 1
            if gib >= 20:
                return 6
            if gib >= 11:
                return 4
            if gib >= 8:
                return 3
            if gib >= 6:
                return 2
            return 1
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return 2 if dml_rembg else 2
    except Exception:
        pass
    return 2 if dml_rembg else min(4, max(2, (os.cpu_count() or 4) - 1))
