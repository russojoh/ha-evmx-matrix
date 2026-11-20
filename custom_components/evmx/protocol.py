"""Async transport for the EVMX matrix ASCII protocol.

The matrix listens on TCP 4001 and speaks plain ASCII, one command per line,
terminated with CR+LF. Replies are one or more lines and there is no prompt
that reliably marks the end, so a reply is read until the socket goes quiet.
"""

from __future__ import annotations

import asyncio
import logging
import re

from .const import DEFAULT_TIMEOUT, READ_QUIET_PERIOD

_LOGGER = logging.getLogger(__name__)

_AV_ROUTE = re.compile(r"AV:\s*(\d+)\s*->\s*(\d+)")
_IN_LINE = re.compile(r"^in\b", re.I)


class EvmxError(Exception):
    """Base error for the matrix transport."""


class EvmxCannotConnect(EvmxError):
    """Raised when the matrix cannot be reached."""


async def _read_until_quiet(reader: asyncio.StreamReader) -> str:
    """Read until the device stops talking."""
    chunks: list[bytes] = []
    while True:
        try:
            chunk = await asyncio.wait_for(reader.read(4096), READ_QUIET_PERIOD)
        except asyncio.TimeoutError:
            break
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks).decode("ascii", errors="replace")


async def async_command(host: str, port: int, command: str) -> str:
    """Send one command, return the raw reply text."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), DEFAULT_TIMEOUT
        )
    except (OSError, asyncio.TimeoutError) as err:
        raise EvmxCannotConnect(f"{host}:{port} unreachable: {err}") from err

    try:
        # The device greets with "Please Input Your Command :" - clear it so the
        # caller's reply is not mixed with the banner.
        await _read_until_quiet(reader)
        writer.write(f"{command}\r\n".encode("ascii"))
        await writer.drain()
        return await _read_until_quiet(reader)
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except (OSError, asyncio.TimeoutError):
            pass


def parse_routing(raw: str) -> dict[int, int]:
    """Parse `%9975.` (or `Status.`) into {output: input}."""
    routes: dict[int, int] = {}

    for line in raw.splitlines():
        match = _AV_ROUTE.search(line)
        if match:
            source, output = int(match.group(1)), int(match.group(2))
            routes[output] = source

    if routes:
        return routes

    values: list[int] | None = None
    for line in raw.splitlines():
        if _IN_LINE.match(line.strip()):
            numbers = [int(n) for n in re.findall(r"\d+", line)]
            # The header line "In 01 02 03 04" is the output numbering; the last
            # line is the payload. Keep whichever came last.
            if numbers:
                values = numbers
    if values:
        for index, source in enumerate(values, start=1):
            routes[index] = source
    return routes


def route_command(source: int, output: int) -> str:
    """`4B1.` = send input 4 to output 1."""
    return f"{source}B{output}."
