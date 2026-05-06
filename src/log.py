"""Centralized logging setup.

Stdlib `logging` only. Each module does ``logger = logging.getLogger(__name__)``
and goes through here for configuration.

Format: ``[HH:MM:SS LVL module] msg``. Module name is shortened to the leaf
component (``mc.scan`` instead of ``src.scanner``-style noise).

Level can be overridden via the ``MC_LOG_LEVEL`` env var (e.g. ``DEBUG``).
"""

import logging
import os
import sys


class _LeafModuleFormatter(logging.Formatter):
    """Formatter that shows only the leaf module name (after the last dot)."""

    def format(self, record: logging.LogRecord) -> str:
        record.leaf = record.name.rsplit(".", 1)[-1]
        return super().format(record)


def setup(level: str | int | None = None) -> None:
    """Configure the root logger. Idempotent — safe to call more than once."""
    resolved = level or os.environ.get("MC_LOG_LEVEL", "INFO")
    if isinstance(resolved, str):
        resolved = getattr(logging, resolved.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(resolved)

    # Replace handlers on re-setup so tests / repeated calls don't duplicate output.
    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        _LeafModuleFormatter(
            fmt="[%(asctime)s %(levelname)s %(leaf)s] %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    root.addHandler(handler)
