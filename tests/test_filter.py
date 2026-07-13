"""Testes de filtragem de diagramas."""

from stride_analyzer.filter import filtrar_e_salvar_diagramas


def test_filtrar_e_salvar_respeita_max_imagens(
    settings, sharp_image, blur_image, mock_classifier, monkeypatch
):
    monkeypatch.setenv("MAX_IMAGENS", "1")
    from stride_analyzer.config import Settings

    s = Settings.from_env()
    aprovadas = filtrar_e_salvar_diagramas(s, classifier=mock_classifier)
    assert len(aprovadas) <= 1
    for p in aprovadas:
        assert p.parent == s.diagramas_dir
        assert p.exists()


def test_filtrar_rejeita_borrada(settings, blur_image, mock_classifier):
    aprovadas = filtrar_e_salvar_diagramas(settings, classifier=mock_classifier)
    nomes = [p.name for p in aprovadas]
    assert "blur.png" not in nomes
