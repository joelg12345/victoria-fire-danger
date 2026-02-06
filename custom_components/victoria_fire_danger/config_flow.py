"""Config flow for Victoria Fire Danger."""
from __future__ import annotations

import voluptuous as vol
from homeassistant.core import callback
from homeassistant import config_entries
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import DOMAIN, VICTORIA_DISTRICTS

# Define options for the selector
DISTRICT_OPTIONS = ["All Districts"] + VICTORIA_DISTRICTS


class VictoriaFireDangerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Victoria Fire Danger."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Prevent multiple instances
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            # Process "All Districts"
            selected = user_input.get("districts", ["All Districts"])
            if "All Districts" in selected:
                user_input["districts"] = VICTORIA_DISTRICTS

            return self.async_create_entry(
                title="Victoria Fire Danger",
                data={"districts": user_input["districts"]}
            )

        # Show the form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("districts", default=["All Districts"]): SelectSelector(
                    SelectSelectorConfig(
                        options=DISTRICT_OPTIONS,
                        multiple=True,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow for editing integration settings."""
        return VictoriaFireDangerOptionsFlow(config_entry)


class VictoriaFireDangerOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Victoria Fire Danger."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Handle "All Districts"
            selected = user_input.get("districts", ["All Districts"])
            if "All Districts" in selected:
                user_input["districts"] = VICTORIA_DISTRICTS

            # Update options and reload
            return self.async_create_entry(
                title="Victoria Fire Danger Options",
                data={"districts": user_input["districts"]}
            )

        # Show the options form
        current_districts = self._config_entry.options.get(
            "districts", self._config_entry.data.get("districts", ["All Districts"])
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("districts", default=current_districts): SelectSelector(
                    SelectSelectorConfig(
                        options=DISTRICT_OPTIONS,
                        multiple=True,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }),
        )
