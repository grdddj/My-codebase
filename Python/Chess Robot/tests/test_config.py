import pytest

from src.config import Config


def test_invalid_values():
    with pytest.raises(ValueError, match="Unknown website"):
        Config(website="unknown")
    with pytest.raises(ValueError, match="Invalid mode"):
        Config(mode="unknown")
