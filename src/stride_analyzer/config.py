"""Configuração centralizada (Twelve-Factor App — III. Config)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _project_root() -> Path:
    env_root = os.getenv("PROJECT_ROOT")
    if env_root:
        return Path(env_root).resolve()
    # Em contêiner Docker o código fica em /app/src/stride_analyzer/
    container_root = Path(__file__).resolve().parents[1]
    if container_root.name == "src" and (container_root.parent / "pyproject.toml").exists():
        return container_root.parent
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    """Configurações imutáveis carregadas do ambiente."""

    project_root: Path
    dataset_dir: Path
    diagramas_dir: Path
    relatorio_dir: Path
    kaggle_username: str | None
    kaggle_key: str | None
    openai_api_key: str | None
    max_imagens: int
    sharpness_threshold: float
    kaggle_dataset: str
    openai_model: str

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> Settings:
        root = _project_root()
        if env_file is None:
            env_file = root / ".env"
        if env_file.exists():
            load_dotenv(env_file)

        return cls(
            project_root=root,
            dataset_dir=root / "dataset",
            diagramas_dir=root / "diagramas_selecionados",
            relatorio_dir=root / "relatorio",
            kaggle_username=os.getenv("KAGGLE_USERNAME"),
            kaggle_key=os.getenv("KAGGLE_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            max_imagens=int(os.getenv("MAX_IMAGENS", "10")),
            sharpness_threshold=float(os.getenv("SHARPNESS_THRESHOLD", "150.0")),
            kaggle_dataset=os.getenv(
                "KAGGLE_DATASET", "carlosrian/software-architecture-dataset"
            ),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        )

    def ensure_directories(self) -> None:
        for folder in (self.dataset_dir, self.diagramas_dir, self.relatorio_dir):
            folder.mkdir(parents=True, exist_ok=True)

    def validate_kaggle_credentials(self) -> None:
        if not self.kaggle_username or not self.kaggle_key:
            raise ValueError(
                "Credenciais Kaggle ausentes. Defina KAGGLE_USERNAME e KAGGLE_KEY no .env"
            )

    def validate_openai_credentials(self) -> None:
        if not self.openai_api_key:
            raise ValueError(
                "Chave OpenAI ausente. Defina OPENAI_API_KEY no .env"
            )
