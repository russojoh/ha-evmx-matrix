"""Config flow for the EVMX HDMI matrix."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers import config_validation as cv

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
from .protocol import EvmxCannotConnect, async_command

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_INPUTS, default=DEFAULT_INPUTS): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=16)
        ),
        vol.Optional(CONF_OUTPUTS, default=DEFAULT_OUTPUTS): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=16)
        ),
    }
)


class EvmxConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle adding a matrix."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for the address, then check the matrix answers."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            try:
                version = await async_command(host, port, "/^Version;")
            except EvmxCannotConnect:
                errors["base"] = "cannot_connect"
            else:
                if version.strip():
                    await self.async_set_unique_id(f"{host}:{port}")
                    self._abort_if_unique_id_configured()
                    title = f"HDMI Matrix {host}"
                    return self.async_create_entry(title=title, data=user_input)
                errors["base"] = "not_a_matrix"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors
        )
