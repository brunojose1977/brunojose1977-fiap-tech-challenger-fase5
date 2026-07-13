"""Testes da CLI."""

from unittest.mock import patch

from stride_analyzer.cli import build_parser, main


def test_parser_setup():
    parser = build_parser()
    args = parser.parse_args(["setup"])
    assert args.command == "setup"


def test_main_setup(settings, capsys):
    with patch("stride_analyzer.cli.Settings.from_env", return_value=settings):
        code = main(["setup"])
    assert code == 0
    captured = capsys.readouterr()
    assert "Dataset" in captured.out


def test_main_analyze_sem_diagramas(settings, capsys):
    with patch("stride_analyzer.cli.Settings.from_env", return_value=settings):
        code = main(["analyze"])
    assert code == 1
    assert "Nenhum .png" in capsys.readouterr().err
