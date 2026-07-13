"""Utilitários para pastas e arquivos locais do projeto."""

from __future__ import annotations

from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def verificar_pastas_locais(pastas: dict[str, Path]) -> dict[str, dict]:
    """Resume existência e contagem de arquivos em cada pasta."""
    resumo: dict[str, dict] = {}

    for nome, pasta in pastas.items():
        pasta = Path(pasta)
        if not pasta.exists():
            resumo[nome] = {"existe": False, "arquivos": 0, "imagens": 0}
            continue

        arquivos = [f for f in pasta.rglob("*") if f.is_file()]
        imagens = [f for f in arquivos if f.suffix.lower() in IMAGE_EXTENSIONS]
        resumo[nome] = {
            "existe": True,
            "arquivos": len(arquivos),
            "imagens": len(imagens),
        }

    return resumo


def dataset_local_disponivel(diretorio: Path) -> bool:
    """Retorna True se existirem imagens no diretório."""
    path = Path(diretorio)
    if not path.exists():
        return False

    for file in path.rglob("*"):
        if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS:
            return True
    return False


def listar_png_diagramas(diretorio: Path) -> list[Path]:
    """Lista arquivos .png na pasta de diagramas selecionados."""
    pasta = Path(diretorio)
    if not pasta.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {pasta}")

    return sorted(
        p for p in pasta.iterdir() if p.is_file() and p.suffix.lower() == ".png"
    )
