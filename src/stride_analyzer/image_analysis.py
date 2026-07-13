"""Critérios de qualidade e classificação de diagramas de arquitetura."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Protocol

import cv2
import numpy as np
from PIL import Image


class ImageClassifier(Protocol):
    def __call__(self, image: Image.Image, candidate_labels: list[str]) -> list[dict]: ...


def is_sharp(image_cv: np.ndarray, threshold: float = 100.0) -> bool:
    """Verifica nitidez via variância do Laplaciano."""
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance > threshold


def is_aligned(image_cv: np.ndarray) -> bool:
    """Verifica alinhamento via Transformada de Hough."""
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    if lines is None:
        return True

    skewed_lines = 0
    for line in lines:
        _, theta = line[0]
        angle = np.degrees(theta)
        if not ((angle < 5 or angle > 175) or (85 < angle < 95)):
            skewed_lines += 1

    return skewed_lines < 5


ARCHITECTURE_LABELS = [
    "a complete software architecture diagram",
    "a cropped or incomplete image",
    "a random photo",
    "a text document",
]


def is_architecture_diagram(
    image_path: Path | str,
    classifier: ImageClassifier | None = None,
) -> bool:
    """Usa IA zero-shot para validar se a imagem é um diagrama de arquitetura completo."""
    if classifier is None:
        return False

    try:
        image = Image.open(image_path)
        results = classifier(image, candidate_labels=ARCHITECTURE_LABELS)
        return results[0]["label"] == ARCHITECTURE_LABELS[0]
    except Exception:
        return False


def avaliar_imagem(
    file_path: Path,
    sharpness_threshold: float,
    classifier: ImageClassifier | None = None,
) -> bool:
    """Aplica todos os critérios de filtragem em uma imagem."""
    img_cv = cv2.imread(str(file_path))
    if img_cv is None:
        return False
    if not is_sharp(img_cv, threshold=sharpness_threshold):
        return False
    if not is_aligned(img_cv):
        return False
    if not is_architecture_diagram(file_path, classifier):
        return False
    return True


def criar_classificador_clip(model_name: str = "openai/clip-vit-base-patch32") -> Callable:
    """Carrega pipeline CLIP para classificação zero-shot."""
    from transformers import pipeline

    return pipeline("zero-shot-image-classification", model=model_name)
