"""The package ships what PEP 561 needs to expose its annotations."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _package_root() -> Path:
    spec = importlib.util.find_spec("parliament")
    assert spec is not None and spec.origin is not None
    return Path(spec.origin).parent


def test_py_typed_marker_exists() -> None:
    """Without it, mypy and pyright treat `import parliament` as untyped."""
    assert (_package_root() / "py.typed").is_file()


def test_py_typed_marker_is_empty() -> None:
    """PEP 561 gives the file no contents; anything in it would be a mistake."""
    assert (_package_root() / "py.typed").read_bytes() == b""


def test_py_typed_ships_beside_the_code_it_describes() -> None:
    """It has to sit inside the installed package, not next to it.

    A marker in the project root, or in `src/`, is not on the import path and a
    type checker never sees it -- which looks identical to not having one.
    """
    root = _package_root()

    assert (root / "__init__.py").is_file()
    assert (root / "py.typed").parent == root
