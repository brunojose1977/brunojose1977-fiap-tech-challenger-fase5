"""Fixtures compartilhadas para testes."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from stride_analyzer.config import Settings


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    (tmp_path / "dataset").mkdir()
    (tmp_path / "diagramas_selecionados").mkdir()
    (tmp_path / "relatorio").mkdir()
    return tmp_path


@pytest.fixture
def settings(project_root: Path, monkeypatch: pytest.MonkeyPatch) -> Settings:
    monkeypatch.setenv("PROJECT_ROOT", str(project_root))
    monkeypatch.setenv("KAGGLE_USERNAME", "test_user")
    monkeypatch.setenv("KAGGLE_KEY", "test_key")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("MAX_IMAGENS", "3")
    return Settings.from_env()


@pytest.fixture
def sharp_image(project_root: Path) -> Path:
    """Imagem sintética com bordas definidas (alta nitidez)."""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    img[50:150, 50:150] = (255, 255, 255)
    path = project_root / "dataset" / "sharp.png"
    cv2.imwrite(str(path), img)
    return path


@pytest.fixture
def blur_image(project_root: Path) -> Path:
    """Imagem borrada (baixa nitidez)."""
    img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    img = cv2.GaussianBlur(img, (51, 51), 0)
    path = project_root / "dataset" / "blur.png"
    cv2.imwrite(str(path), img)
    return path


@pytest.fixture
def mock_classifier():
    """Classificador que sempre retorna diagrama de arquitetura."""

    def _classifier(image, candidate_labels):
        return [{"label": candidate_labels[0], "score": 0.99}]

    return _classifier
