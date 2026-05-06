"""Base ``SessionSource`` interface.

A source is responsible for one thing: walking its own transcript directory
and yielding fully-populated ``Session`` records. The pipeline downstream
(canonical project resolution, feature derivation, DB upsert, sync-delete)
is identical regardless of source.
"""

from abc import ABC, abstractmethod
from typing import Iterator

from src.scanner import Session


class SessionSource(ABC):
    """Abstract source — one implementation per tool."""

    #: Short stable identifier used in logs and (eventually) DB rows.
    name: str = ""

    @abstractmethod
    def discover(self, cfg: dict) -> Iterator[Session]:
        """Walk the source's transcript directory and yield ``Session`` records.

        Implementations must:
          - return early if their root directory does not exist
          - tolerate per-file parse failures (log a warning, skip the file)
          - leave ``Session.project`` as the raw mangled name from the source;
            canonicalization happens upstream in :func:`cli.scan_all`.
        """
        raise NotImplementedError
