"""Testes de análise de imagens."""

import numpy as np

from stride_analyzer.image_analysis import (
    ARCHITECTURE_LABELS,
    avaliar_imagem,
    is_aligned,
    is_architecture_diagram,
    is_sharp,
)


def test_is_sharp_detecta_imagem_nitida(sharp_image):
    import cv2

    img = cv2.imread(str(sharp_image))
    assert is_sharp(img, threshold=50.0)


def test_is_sharp_rejeita_imagem_borrada(blur_image):
    import cv2

    img = cv2.imread(str(blur_image))
    assert not is_sharp(img, threshold=150.0)


def test_is_aligned_com_imagem_uniforme():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    assert is_aligned(img) is True


def test_is_architecture_diagram_com_mock(sharp_image, mock_classifier):
    assert is_architecture_diagram(sharp_image, mock_classifier) is True


def test_is_architecture_diagram_sem_classificador(sharp_image):
    assert is_architecture_diagram(sharp_image, None) is False


def test_avaliar_imagem_aprovada(sharp_image, mock_classifier):
    assert (
        avaliar_imagem(sharp_image, sharpness_threshold=50.0, classifier=mock_classifier)
        is True
    )


def test_avaliar_imagem_rejeita_borrada(blur_image, mock_classifier):
    assert (
        avaliar_imagem(blur_image, sharpness_threshold=150.0, classifier=mock_classifier)
        is False
    )


def test_architecture_labels_contem_diagrama():
    assert "a complete software architecture diagram" in ARCHITECTURE_LABELS
