"""Análise de segurança STRIDE via OpenAI Vision."""

from __future__ import annotations

import base64
import logging
from pathlib import Path

from openai import OpenAI

from stride_analyzer.config import Settings

logger = logging.getLogger(__name__)

PROMPT_SEGURANCA = """\
Você é um Arquiteto de Cloud e Especialista em Segurança da Informação.
Analise o diagrama de arquitetura de sistemas fornecido na imagem.

Aplique a metodologia STRIDE e forneça um relatório estruturado avaliando \
as potenciais vulnerabilidades. Para cada letra do STRIDE, forneça:
1. Ameaça/Vulnerabilidade potencial identificada \
(baseada nos componentes visíveis ou na ausência deles).
2. Contramedidas de Hardening recomendadas.

As categorias são:
- S: Spoofing (Falsificação de Identidade)
- T: Tampering (Modificação de Dados)
- R: Repudiation (Repúdio)
- I: Information Disclosure (Divulgação de Informação)
- D: Denial of Service (Negação de Serviço)
- E: Elevation of Privilege (Elevação de Privilégio)

Seja técnico, direto e foque em práticas modernas de segurança em nuvem \
(Zero Trust, IAM, Criptografia, WAF, etc.).
"""


def encode_image_to_base64(image_path: Path | str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def analisar_arquitetura_stride(
    image_path: Path | str,
    client: OpenAI,
    model: str = "gpt-4o",
) -> str:
    """Envia diagrama para OpenAI e retorna análise STRIDE."""
    base64_image = encode_image_to_base64(image_path)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT_SEGURANCA},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            max_tokens=1500,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        logger.exception("Erro ao analisar %s", image_path)
        return f"Erro ao processar a imagem: {exc}"


def executar_analise_stride(
    settings: Settings,
    diagramas: list[Path],
    client: OpenAI | None = None,
) -> list[dict]:
    """Executa STRIDE para cada diagrama e retorna lista de resultados."""
    if client is None:
        settings.validate_openai_credentials()
        client = OpenAI(api_key=settings.openai_api_key)

    resultados: list[dict] = []
    for img_path in diagramas:
        logger.info("Analisando: %s", img_path.name)
        analise = analisar_arquitetura_stride(
            img_path, client=client, model=settings.openai_model
        )
        resultados.append(
            {
                "arquivo": img_path.name,
                "caminho": str(img_path),
                "analise": analise,
            }
        )
    return resultados
