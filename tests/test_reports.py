"""Testes de geração de relatórios."""

from stride_analyzer.reports import gerar_docx_relatorio, gerar_pdf_relatorio, salvar_relatorios


def _resultados_exemplo(caminho: str) -> list[dict]:
    return [
        {
            "arquivo": "diagrama.png",
            "caminho": caminho,
            "analise": "S: Spoofing - risco identificado.\n\nT: Tampering - controle ausente.",
        }
    ]


def test_gerar_pdf_relatorio(settings, sharp_image):
    pdf_path = settings.relatorio_dir / "test.pdf"
    gerar_pdf_relatorio(_resultados_exemplo(str(sharp_image)), pdf_path)
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0


def test_gerar_docx_relatorio(settings, sharp_image):
    docx_path = settings.relatorio_dir / "test.docx"
    gerar_docx_relatorio(_resultados_exemplo(str(sharp_image)), docx_path)
    assert docx_path.exists()
    assert docx_path.stat().st_size > 0


def test_salvar_relatorios(settings, sharp_image):
    paths = salvar_relatorios(
        _resultados_exemplo(str(sharp_image)),
        settings.relatorio_dir,
        timestamp="20260101_120000",
    )
    assert paths["json"].exists()
    assert paths["pdf"].exists()
    assert paths["docx"].exists()
    assert "20260101_120000" in paths["json"].name
