"""Testes de utilitários de paths."""

from pathlib import Path

import pytest

from stride_analyzer.config import Settings
from stride_analyzer.paths import (
    dataset_local_disponivel,
    listar_png_diagramas,
    verificar_pastas_locais,
)


def test_dataset_local_disponivel_com_imagem(sharp_image: Path, settings):
    assert dataset_local_disponivel(settings.dataset_dir) is True


def test_dataset_local_disponivel_vazio(project_root: Path):
    assert dataset_local_disponivel(project_root / "dataset") is False


def test_dataset_local_disponivel_inexistente(project_root: Path):
    assert dataset_local_disponivel(project_root / "inexistente") is False


def test_verificar_pastas_locais(settings: Settings, sharp_image: Path):
    pastas = {
        "Dataset": settings.dataset_dir,
        "Diagramas": settings.diagramas_dir,
    }
    resumo = verificar_pastas_locais(pastas)
    assert resumo["Dataset"]["existe"] is True
    assert resumo["Dataset"]["imagens"] >= 1
    assert resumo["Diagramas"]["existe"] is True


def test_listar_png_diagramas(settings: Settings, sharp_image: Path):
    dest = settings.diagramas_dir / "test.png"
    dest.write_bytes(sharp_image.read_bytes())
    pngs = listar_png_diagramas(settings.diagramas_dir)
    assert len(pngs) == 1
    assert pngs[0].name == "test.png"


def test_listar_png_pasta_inexistente(project_root: Path):
    with pytest.raises(FileNotFoundError):
        listar_png_diagramas(project_root / "inexistente")
