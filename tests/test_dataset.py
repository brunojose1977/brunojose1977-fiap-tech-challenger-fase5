"""Testes de dataset."""

from pathlib import Path
from unittest.mock import patch

import pytest

from stride_analyzer.config import Settings
from stride_analyzer.dataset import garantir_dataset, remover_arquivos_xml
from stride_analyzer.paths import dataset_local_disponivel


def test_remover_arquivos_xml(settings: Settings):
    xml_file = settings.dataset_dir / "anotacao.xml"
    xml_file.write_text("<root/>", encoding="utf-8")
    sub = settings.dataset_dir / "sub"
    sub.mkdir()
    (sub / "outro.xml").write_text("<root/>", encoding="utf-8")

    removidos = remover_arquivos_xml(settings.dataset_dir)
    assert removidos == 2
    assert not xml_file.exists()


def test_garantir_dataset_ja_existe(settings: Settings, sharp_image: Path):
    with patch("stride_analyzer.dataset._download_via_kaggle_cli") as mock_dl:
        path = garantir_dataset(settings)
        mock_dl.assert_not_called()
        assert path == settings.dataset_dir


def test_garantir_dataset_baixa_quando_vazio(settings: Settings):
    with patch("stride_analyzer.dataset._download_via_kaggle_cli") as mock_dl:
        def _simulate_download(s):
            img_path = s.dataset_dir / "downloaded.png"
            import cv2
            import numpy as np

            img = np.zeros((50, 50, 3), dtype=np.uint8)
            cv2.imwrite(str(img_path), img)

        mock_dl.side_effect = _simulate_download
        path = garantir_dataset(settings)
        mock_dl.assert_called_once()
        assert dataset_local_disponivel(path)


def test_garantir_dataset_falha_sem_imagens(settings: Settings):
    with patch("stride_analyzer.dataset._download_via_kaggle_cli"):
        with pytest.raises(FileNotFoundError):
            garantir_dataset(settings)
