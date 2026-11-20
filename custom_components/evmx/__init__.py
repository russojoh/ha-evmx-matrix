"""The EVMX HDMI matrix integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_HOST,
    CONF_INPUTS,
    CONF_OUTPUTS,
    CONF_PORT,
    DEFAULT_INPUTS,
    DEFAULT_OUTPUTS,
    DEFAULT_PORT,
    DOMAIN,
)
from .coordinator import EvmxCoordinator

PLATFORMS: list[Platform] = [Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up an EVMX matrix from a config entry."""
    coordinator = EvmxCoordinator(
        hass,
        entry.data[CONF_HOST],
        entry.data.get(CONF_PORT, DEFAULT_PORT),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an EVMX matrix."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok


def entry_options(entry: ConfigEntry) -> tuple[int, int]:
    """Return (inputs, outputs) for an entry."""
    return (
        int(entry.data.get(CONF_INPUTS, DEFAULT_INPUTS)),
        int(entry.data.get(CONF_OUTPUTS, DEFAULT_OUTPUTS)),
    )
