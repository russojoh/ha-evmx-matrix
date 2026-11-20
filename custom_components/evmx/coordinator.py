"""Coordinator for the EVMX HDMI matrix."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .protocol import EvmxCannotConnect, async_command, parse_routing, route_command

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=15)


@dataclass
class EvmxData:
    """State read from the matrix."""

    routes: dict[int, int] = field(default_factory=dict)
    model: str | None = None
    firmware: str | None = None


class EvmxCoordinator(DataUpdateCoordinator[EvmxData]):
    """Poll the routing table and push changes to the matrix."""

    def __init__(self, hass: HomeAssistant, host: str, port: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} {host}",
            update_interval=SCAN_INTERVAL,
        )
        self.host = host
        self.port = port
        self._model: str | None = None
        self._firmware: str | None = None
        self._lock = asyncio.Lock()

    async def _async_update_data(self) -> EvmxData:
        async with self._lock:
            try:
                raw = await async_command(self.host, self.port, "%9975.")
            except EvmxCannotConnect as err:
                raise UpdateFailed(str(err)) from err

            routes = parse_routing(raw)
            if not routes:
                raise UpdateFailed(f"unparsable routing reply: {raw!r}")

            if self._firmware is None:
                try:
                    self._firmware = (
                        await async_command(self.host, self.port, "/^Version;")
                    ).strip() or None
                    self._model = (
                        await async_command(self.host, self.port, "/*Type;")
                    ).strip() or None
                except EvmxCannotConnect:
                    _LOGGER.debug("Could not read model/firmware from %s", self.host)

            return EvmxData(routes=routes, model=self._model, firmware=self._firmware)

    async def async_set_route(self, output: int, source: int) -> None:
        """Switch one output to an input, then refresh."""
        async with self._lock:
            await async_command(self.host, self.port, route_command(source, output))
            raw = await async_command(self.host, self.port, "%9975.")
        routes = parse_routing(raw)
        if routes:
            self.async_set_updated_data(
                EvmxData(
                    routes=routes, model=self._model, firmware=self._firmware
                )
            )
