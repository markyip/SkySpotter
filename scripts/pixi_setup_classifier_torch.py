#!/usr/bin/env python3
"""Install CPU or CUDA PyTorch based on hardware; DirectML used when GPU torch unavailable."""

from __future__ import annotations

import importlib.metadata as md
import re
import shutil
import subprocess
import sys

CUDA_INDEX = "https://download.pytorch.org/whl/cu124"
CPU_INDEX = "https://download.pytorch.org/whl/cpu"


def _pip(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pip", *args],
        text=True,
        capture_output=True,
    )


def _torch_version() -> str | None:
    try:
        return md.version("torch")
    except md.PackageNotFoundError:
        return None


def _torch_build_tag() -> str:
    ver = _torch_version() or ""
    if "+cu" in ver:
        return "cuda"
    if "+cpu" in ver:
        return "cpu"
    return "unknown"


def nvidia_gpu_detected() -> bool:
    """Best-effort NVIDIA GPU detection without importing torch."""
    if shutil.which("nvidia-smi") is None:
        return False
    try:
        result = subprocess.run(
            ["nvidia-smi", "-L"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    if result.returncode != 0:
        return False
    return bool(re.search(r"GPU\s+\d+", result.stdout or "", re.IGNORECASE))


def _clear_torch_modules() -> None:
    for name in list(sys.modules):
        if name == "torch" or name.startswith("torch.") or name.startswith("torchvision"):
            sys.modules.pop(name, None)


def torch_cuda_works(*, subprocess_check: bool = False) -> bool:
    """Return True when CUDA PyTorch can see a GPU."""
    if subprocess_check:
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import torch; raise SystemExit(0 if torch.cuda.is_available() else 1)",
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        return result.returncode == 0

    _clear_torch_modules()
    try:
        import torch
    except Exception:
        return False
    return bool(torch.cuda.is_available())


def _reinstall_torch_packages(index_url: str, *, quiet: bool = False) -> bool:
    if not quiet:
        print(f"Reinstalling torch + torchvision from {index_url} …", flush=True)
    _pip("uninstall", "-y", "torch", "torchvision")
    result = _pip(
        "install",
        "--upgrade",
        "torch",
        "torchvision",
        "--index-url",
        index_url,
    )
    if result.returncode != 0:
        if not quiet:
            print(result.stderr or result.stdout, file=sys.stderr)
        return False
    if result.stdout.strip() and not quiet:
        print(result.stdout.strip(), flush=True)
    return True


def install_cuda_torch(*, quiet: bool = False) -> bool:
    if not quiet:
        print("Configuring PyTorch CUDA build for GPU aircraft classification …", flush=True)
    if not _reinstall_torch_packages(CUDA_INDEX, quiet=quiet):
        return False
    if not torch_cuda_works(subprocess_check=True):
        if not quiet:
            ver = _torch_version()
            print(
                f"CUDA PyTorch install finished but torch.cuda.is_available() is False "
                f"(torch {ver}).",
                file=sys.stderr,
                flush=True,
            )
        return False
    return True


def install_cpu_torch(*, quiet: bool = False) -> bool:
    if not quiet:
        print("Configuring PyTorch CPU build …", flush=True)
    if not _reinstall_torch_packages(CPU_INDEX, quiet=quiet):
        return False
    return _torch_version() is not None


def configure_classifier_torch(*, quiet: bool = False) -> str:
    """
    Pick and install a suitable PyTorch build.

    Returns one of: ``cuda``, ``cpu``, ``directml_fallback``.
    """
    has_nvidia = nvidia_gpu_detected()

    if has_nvidia:
        if _torch_build_tag() == "cuda" and torch_cuda_works(subprocess_check=True):
            if not quiet:
                result = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        "import torch; print(torch.__version__); "
                        "print(torch.cuda.get_device_name(0))",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False,
                )
                lines = [ln.strip() for ln in (result.stdout or "").splitlines() if ln.strip()]
                ver = lines[0] if lines else _torch_version()
                gpu = lines[1] if len(lines) > 1 else "CUDA"
                print(
                    f"PyTorch GPU ready: {ver} on {gpu} "
                    "(aircraft classifier will use CUDA)",
                    flush=True,
                )
            return "cuda"
        if install_cuda_torch(quiet=quiet):
            if not quiet:
                result = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        "import torch; print(torch.__version__); "
                        "print(torch.cuda.get_device_name(0))",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False,
                )
                lines = [ln.strip() for ln in (result.stdout or "").splitlines() if ln.strip()]
                ver = lines[0] if lines else _torch_version()
                gpu = lines[1] if len(lines) > 1 else "CUDA"
                print(
                    f"PyTorch GPU ready: {ver} on {gpu}",
                    flush=True,
                )
            return "cuda"
        if not quiet:
            print(
                "NVIDIA GPU detected but CUDA PyTorch could not be enabled. "
                "Falling back to DirectML ONNX for aircraft classification.",
                file=sys.stderr,
                flush=True,
            )
        install_cpu_torch(quiet=quiet)
        return "directml_fallback"

    if _torch_build_tag() != "cpu":
        install_cpu_torch(quiet=quiet)

    if not quiet:
        print(
            "No compatible GPU for PyTorch CUDA. "
            "Aircraft classifier will use DirectML ONNX when indexing.",
            flush=True,
        )
    return "directml_fallback"


def main() -> int:
    configure_classifier_torch()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
