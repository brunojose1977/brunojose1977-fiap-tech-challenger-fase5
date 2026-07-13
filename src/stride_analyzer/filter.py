"""Filtragem e seleção de diagramas aprovados."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from stride_analyzer.config import Settings
from stride_analyzer.image_analysis import avaliar_imagem

logger = logging.getLogger(__name__)


def filtrar_e_salvar_diagramas(
    settings: Settings,
    classifier=None,
) -> list[Path]:
    """
    Percorre o dataset, aplica critérios de qualidade e copia
    até max_imagens diagramas aprovados para diagramas_selecionados/.
    """
    settings.ensure_directories()
    aprovadas: list[Path] = []

    for file_path in settings.dataset_dir.rglob("*"):
        if len(aprovadas) >= settings.max_imagens:
            break

        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            continue

        if not avaliar_imagem(
            file_path,
            sharpness_threshold=settings.sharpness_threshold,
            classifier=classifier,
        ):
            continue

        dest_path = settings.diagramas_dir / file_path.name
        shutil.copy(file_path, dest_path)
        aprovadas.append(dest_path)
        logger.info("Aprovada: %s", dest_path.name)

    logger.info("%d imagens salvas em %s", len(aprovadas), settings.diagramas_dir)
    return aprovadas
