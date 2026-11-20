"""Select entities - one per matrix output, value is the routed input."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import entry_options
from .const import CONF_HOST, DOMAIN, MANUFACTURER
from .coordinator import EvmxCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create one select per output."""
    coordinator: EvmxCoordinator = hass.data[DOMAIN][entry.entry_id]
    inputs, outputs = entry_options(entry)
    async_add_entities(
        EvmxOutputSelect(coordinator, entry, output, inputs)
        for output in range(1, outputs + 1)
    )


class EvmxOutputSelect(CoordinatorEntity[EvmxCoordinator], SelectEntity):
    """Choose which input feeds one output."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:video-input-hdmi"

    def __init__(
        self,
        coordinator: EvmxCoordinator,
        entry: ConfigEntry,
        output: int,
        inputs: int,
    ) -> None:
        super().__init__(coordinator)
        self._output = output
        self._attr_unique_id = f"{entry.entry_id}_output_{output}"
        self._attr_name = f"Output {output}"
        self._attr_options = [str(number) for number in range(1, inputs + 1)]
        data = coordinator.data
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            model=data.model if data and data.model else "HDMI Matrix",
            sw_version=data.firmware if data and data.firmware else None,
            configuration_url=f"http://{entry.data[CONF_HOST]}/",
        )

    @property
    def current_option(self) -> str | None:
        """The input currently routed to this output."""
        if not self.coordinator.data:
            return None
        source = self.coordinator.data.routes.get(self._output)
        return str(source) if source else None

    async def async_select_option(self, option: str) -> None:
        """Route `option` (an input) to this output."""
        await self.coordinator.async_set_route(self._output, int(option))
