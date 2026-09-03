"""Re-raised errors keep (or deliberately drop) their cause — ruff B904, #22."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from parliament import cli
import parliament.providers as providers_module
from parliament.providers import create_provider


def test_a_missing_sdk_keeps_the_import_error_that_names_it(monkeypatch):
    """`from err` here is the difference between two different problems.

    "The SDK is not installed" and "the SDK is installed and one of its own
    imports is broken" produce the same friendly message, and only the cause
    tells them apart.
    """
    catalogue = dict(providers_module._CLOUD_PROVIDERS)
    catalogue["anthropic"] = ("parliament.providers._not_a_real_module", "X")
    monkeypatch.setattr(providers_module, "_CLOUD_PROVIDERS", catalogue)

    with pytest.raises(ImportError) as excinfo:
        create_provider("anthropic", model="m")

    assert "requires its SDK" in str(excinfo.value)
    assert excinfo.value.__cause__ is not None
    assert "_not_a_real_module" in str(excinfo.value.__cause__)


def test_a_friendly_cli_failure_does_not_drag_a_traceback_along(tmp_path, monkeypatch):
    """A missing config file is explained in full by the message above it.

    The config path has to survive Click's own ``exists=True`` check first --
    asserting on a nonexistent path only proves Click rejects it, and would
    pass with every ``from None`` in this change reverted. So a real file is
    handed in and the ``FileNotFoundError`` is raised downstream, where the
    ``except`` block under test actually sees it.
    """
    config = tmp_path / "parliament.yaml"
    config.write_text("members: []\n", encoding="utf-8")

    def _missing(*args, **kwargs):
        raise FileNotFoundError("hansard.json not found")

    monkeypatch.setattr(cli, "load_config", _missing)

    result = CliRunner().invoke(cli.main, ["ask", "--config", str(config), "q"])

    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert result.exception.__cause__ is None
    assert result.exception.__suppress_context__ is True


def test_an_unexpected_cli_failure_keeps_the_error_that_caused_it(tmp_path, monkeypatch):
    """The other half of the split: a catch-all keeps its cause."""
    config = tmp_path / "parliament.yaml"
    config.write_text("members: []\n", encoding="utf-8")

    boom = RuntimeError("something three frames down")

    def _explode(*args, **kwargs):
        raise boom

    monkeypatch.setattr(cli, "load_config", _explode)

    result = CliRunner().invoke(cli.main, ["ask", "--config", str(config), "q"])

    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert result.exception.__cause__ is boom
