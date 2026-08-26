import pytest


from server import validate_terraform_path


def test_valid_terraform_path() -> None:
    path = validate_terraform_path("terraform")

    assert path.is_dir()
    assert list(path.glob("*.tf"))


def test_invalid_terraform_path() -> None:
    with pytest.raises(ValueError):
        validate_terraform_path("missing-directory")