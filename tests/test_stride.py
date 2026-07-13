"""Testes de análise STRIDE."""

from unittest.mock import MagicMock

from stride_analyzer.stride import (
    analisar_arquitetura_stride,
    encode_image_to_base64,
    executar_analise_stride,
)


def test_encode_image_to_base64(sharp_image):
    encoded = encode_image_to_base64(sharp_image)
    assert isinstance(encoded, str)
    assert len(encoded) > 0


def test_analisar_arquitetura_stride_mock(sharp_image):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Análise STRIDE mock"))]
    mock_client.chat.completions.create.return_value = mock_response

    resultado = analisar_arquitetura_stride(sharp_image, client=mock_client)
    assert "STRIDE" in resultado
    mock_client.chat.completions.create.assert_called_once()


def test_executar_analise_stride(settings, sharp_image):
    dest = settings.diagramas_dir / sharp_image.name
    dest.write_bytes(sharp_image.read_bytes())

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Relatório completo"))]
    mock_client.chat.completions.create.return_value = mock_response

    resultados = executar_analise_stride(settings, [dest], client=mock_client)
    assert len(resultados) == 1
    assert resultados[0]["arquivo"] == dest.name
    assert "Relatório" in resultados[0]["analise"]
