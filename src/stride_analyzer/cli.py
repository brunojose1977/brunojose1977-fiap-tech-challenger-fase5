"""Interface de linha de comando (Twelve-Factor: processes / disposability)."""

from __future__ import annotations

import argparse
import logging
import sys

from stride_analyzer.config import Settings
from stride_analyzer.dataset import garantir_dataset
from stride_analyzer.filter import filtrar_e_salvar_diagramas
from stride_analyzer.image_analysis import criar_classificador_clip
from stride_analyzer.paths import listar_png_diagramas, verificar_pastas_locais
from stride_analyzer.reports import salvar_relatorios
from stride_analyzer.stride import executar_analise_stride


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )


def cmd_setup(args: argparse.Namespace) -> int:
    settings = Settings.from_env()
    settings.ensure_directories()
    pastas = {
        "Dataset": settings.dataset_dir,
        "Diagramas selecionados": settings.diagramas_dir,
        "Relatórios": settings.relatorio_dir,
    }
    resumo = verificar_pastas_locais(pastas)
    for nome, info in resumo.items():
        status = "OK" if info["existe"] else "AUSENTE"
        print(f"  [{status}] {nome}: arquivos={info['arquivos']} imagens={info['imagens']}")
    return 0


def cmd_download(args: argparse.Namespace) -> int:
    settings = Settings.from_env()
    garantir_dataset(settings)
    print(f"Dataset disponível em: {settings.dataset_dir}")
    return 0


def cmd_filter(args: argparse.Namespace) -> int:
    settings = Settings.from_env()
    garantir_dataset(settings)

    classifier = None
    if not args.skip_clip:
        logging.getLogger(__name__).info("Carregando modelo CLIP...")
        classifier = criar_classificador_clip()

    aprovadas = filtrar_e_salvar_diagramas(settings, classifier=classifier)
    print(f"{len(aprovadas)} diagramas salvos em {settings.diagramas_dir}")
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    settings = Settings.from_env()
    diagramas = listar_png_diagramas(settings.diagramas_dir)

    if not diagramas:
        print(
            f"Nenhum .png em {settings.diagramas_dir}. "
            "Execute 'filter' ou adicione diagramas manualmente.",
            file=sys.stderr,
        )
        return 1

    print(f"Analisando {len(diagramas)} diagrama(s)...")
    resultados = executar_analise_stride(settings, diagramas)
    paths = salvar_relatorios(resultados, settings.relatorio_dir)

    print("Análise concluída!")
    print(f"  JSON : {paths['json']}")
    print(f"  PDF  : {paths['pdf']}")
    print(f"  DOCX : {paths['docx']}")
    return 0


def cmd_run_all(args: argparse.Namespace) -> int:
    if cmd_download(args) != 0:
        return 1
    if cmd_filter(args) != 0:
        return 1
    return cmd_analyze(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Carga de diagramas Kaggle e análise STRIDE",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Log detalhado")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("setup", help="Cria pastas locais e exibe status").set_defaults(
        func=cmd_setup
    )
    sub.add_parser(
        "download",
        help="Baixa dataset do Kaggle se não existir localmente",
    ).set_defaults(func=cmd_download)
    p_filter = sub.add_parser("filter", help="Filtra e seleciona diagramas do dataset")
    p_filter.add_argument(
        "--skip-clip",
        action="store_true",
        help="Pula classificação CLIP (apenas nitidez e alinhamento)",
    )
    p_filter.set_defaults(func=cmd_filter)

    sub.add_parser(
        "analyze",
        help="Executa análise STRIDE nos diagramas selecionados",
    ).set_defaults(func=cmd_analyze)
    p_all = sub.add_parser("run-all", help="Download + filter + analyze")
    p_all.add_argument("--skip-clip", action="store_true")
    p_all.set_defaults(func=cmd_run_all)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(getattr(args, "verbose", False))
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
