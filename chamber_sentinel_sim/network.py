"""Network isolation enforcement — blocks all non-localhost network access."""

from __future__ import annotations

import socket
from unittest.mock import patch

_original_connect = socket.socket.connect
_original_connect_ex = socket.socket.connect_ex
_isolation_active = False


class NetworkIsolationError(RuntimeError):
    pass


def _guarded_connect(self: socket.socket, address: tuple) -> None:
    if _isolation_active:
        host = address[0] if isinstance(address, tuple) else str(address)
        if host not in ("127.0.0.1", "localhost", "::1", "0.0.0.0"):
            raise NetworkIsolationError(
                f"Network isolation violation: attempted connection to {host}. "
                "The simulation must run fully locally with zero external network calls."
            )
    return _original_connect(self, address)


def _guarded_connect_ex(self: socket.socket, address: tuple) -> int:
    if _isolation_active:
        host = address[0] if isinstance(address, tuple) else str(address)
        if host not in ("127.0.0.1", "localhost", "::1", "0.0.0.0"):
            raise NetworkIsolationError(
                f"Network isolation violation: attempted connection to {host}."
            )
    return _original_connect_ex(self, address)


def enable_network_isolation() -> None:
    global _isolation_active
    socket.socket.connect = _guarded_connect  # type: ignore[assignment]
    socket.socket.connect_ex = _guarded_connect_ex  # type: ignore[assignment]
    _isolation_active = True


def disable_network_isolation() -> None:
    global _isolation_active
    socket.socket.connect = _original_connect  # type: ignore[assignment]
    socket.socket.connect_ex = _original_connect_ex  # type: ignore[assignment]
    _isolation_active = False
