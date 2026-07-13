"""Testes de configuração."""

from pathlib import Path

from stride_analyzer.config import Settings


def test_settings_from_env(project_root: Path, monkeypatch):
    monkeypatch.setenv("PROJECT_ROOT", str(project_root))
    monkeypatch.setenv("MAX_IMAGENS", "5")
    settings = Settings.from_env()

    assert settings.project_root == project_root
    assert settings.dataset_dir == project_root / "dataset"
    assert settings.diagramas_dir == project_root / "diagramas_selecionados"
    assert settings.relatorio_dir == project_root / "relatorio"
    assert settings.max_imagens == 5


def test_ensure_directories(settings: Settings):
    settings.ensure_directories()
    assert settings.dataset_dir.exists()
    assert settings.diagramas_dir.exists()
    assert settings.relatorio_dir.exists()


def test_validate_kaggle_credentials_raises(settings: Settings, monkeypatch):
    monkeypatch.delenv("KAGGLE_USERNAME", raising=False)
    monkeypatch.delenv("KAGGLE_KEY", raising=False)
    s = Settings.from_env()
    try:
        s.validate_kaggle_credentials()
        assert False, "Deveria lançar ValueError"
    except ValueError as e:
        assert "Kaggle" in str(e)


def test_validate_openai_credentials_raises(project_root: Path, monkeypatch):
    monkeypatch.setenv("PROJECT_ROOT", str(project_root))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    s = Settings.from_env()
    try:
        s.validate_openai_credentials()
        assert False, "Deveria lançar ValueError"
    except ValueError as e:
        assert "OpenAI" in str(e)
