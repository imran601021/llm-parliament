"""LLM Parliament — multi-agent debate for better AI decisions."""

from importlib.metadata import PackageNotFoundError, version

from parliament.core.parliament import Parliament
from parliament.core.types import Bill, Hansard, Member, Response, Synthesis

try:
    __version__ = version("llm-parliament")
except PackageNotFoundError:  # running from a source tree without install
    __version__ = "0.0.0.dev0"

__all__ = [
    "Bill",
    "Hansard",
    "Member",
    "Parliament",
    "Response",
    "Synthesis",
    "__version__",
]
