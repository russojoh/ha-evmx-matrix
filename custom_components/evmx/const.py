"""Constants for the EVMX HDMI matrix integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "evmx"

CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_INPUTS: Final = "inputs"
CONF_OUTPUTS: Final = "outputs"

DEFAULT_PORT: Final = 4001
DEFAULT_INPUTS: Final = 4
DEFAULT_OUTPUTS: Final = 4

DEFAULT_TIMEOUT: Final = 6.0
READ_QUIET_PERIOD: Final = 0.6

MANUFACTURER: Final = "Vanco / Evolution"

CMD_PROMPT: Final = "*"
