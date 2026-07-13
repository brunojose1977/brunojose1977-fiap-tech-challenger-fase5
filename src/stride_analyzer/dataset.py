"""Download e preparação do dataset Kaggle."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import zipfile
from pathlib import Path

from stride_analyzer.config import Settings
from stride_analyzer.paths import dataset_local_disponivel

logger = logging.getLogger(__name__)


def remover_arquivos_xml(diretorio: Path) -> int:
    """Remove recursivamente todos os arquivos .xml do diretório."""
    removidos = 0
    for file in Path(diretorio).rglob("*.xml"):
        if file.is_file():
            file.unlink()
            removidos += 1
    return removidos


def _extrair_zips_existentes(diretorio: Path) -> None:
    """Extrai o maior arquivo .zip válido presente na pasta do dataset."""
    zips = sorted(diretorio.glob("*.zip"), key=lambda p: p.stat().st_size, reverse=True)
    for zip_path in zips:
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                if zf.testzip() is not None:
                    logger.warning("Zip incompleto ou corrompido: %s — ignorado", zip_path.name)
                    continue
                logger.info(
                    "Extraindo %s em %s (pode levar vários minutos)...",
                    zip_path.name,
                    diretorio,
                )
                zf.extractall(diretorio)
            logger.info("Extração concluída: %s", zip_path.name)
            return
        except zipfile.BadZipFile:
            logger.warning("Arquivo zip inválido: %s — ignorado", zip_path.name)


def _download_via_kaggle_cli(settings: Settings) -> None:
    settings.validate_kaggle_credentials()
    os.environ["KAGGLE_USERNAME"] = settings.kaggle_username  # type: ignore[arg-type]
    os.environ["KAGGLE_KEY"] = settings.kaggle_key  # type: ignore[arg-type]

    settings.dataset_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "kaggle",
        "datasets",
        "download",
        "-d",
        settings.kaggle_dataset,
        "--unzip",
        "-p",
        str(settings.dataset_dir),
    ]
    logger.info("Baixando dataset %s para %s", settings.kaggle_dataset, settings.dataset_dir)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("Kaggle CLI stderr: %s", result.stderr)
        raise subprocess.CalledProcessError(
            result.returncode, cmd, output=result.stdout, stderr=result.stderr
        )


def garantir_dataset(settings: Settings) -> Path:
    """
    Garante que o dataset exista localmente.
    Baixa do Kaggle apenas se não houver imagens na pasta dataset/.
    """
    settings.ensure_directories()

    if dataset_local_disponivel(settings.dataset_dir):
        logger.info("Dataset já disponível em: %s", settings.dataset_dir)
        return settings.dataset_dir

    zips_locais = list(settings.dataset_dir.glob("*.zip"))
    if zips_locais:
        _extrair_zips_existentes(settings.dataset_dir)
        if dataset_local_disponivel(settings.dataset_dir):
            removidos = remover_arquivos_xml(settings.dataset_dir)
            logger.info("%d arquivo(s) .xml removido(s)", removidos)
            return settings.dataset_dir

    _download_via_kaggle_cli(settings)

    if not dataset_local_disponivel(settings.dataset_dir):
        raise FileNotFoundError(
            f"Download concluído, mas nenhuma imagem encontrada em {settings.dataset_dir}."
        )

    removidos = remover_arquivos_xml(settings.dataset_dir)
    logger.info("%d arquivo(s) .xml removido(s)", removidos)
    return settings.dataset_dir


def extrair_zip_local(zip_path: Path, destino: Path) -> None:
    """Extrai um arquivo zip para o destino (útil em testes)."""
    destino.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(destino)
