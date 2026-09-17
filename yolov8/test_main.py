import pytest
from pathlib import Path

from main import parse_args, evaluate_image


def test_parse_args_defaults():
    args = parse_args(["--mode", "camera"])
    assert args.mode == "camera"


def test_evaluate_image_file_not_found():
    with pytest.raises(FileNotFoundError):
        evaluate_image(None, "does_not_exist.png")
