"""Config flow for Victoria Fire Danger."""
from __future__ import annotations

import voluptuous as vol
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
        # Prevent multiple instances of the integration
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            # Process the "All Districts" selection
            selected = user_input.get("districts", ["All Districts"])
            if "All Districts" in selected:
                user_input["districts"] = VICTORIA_DISTRICTS

            return self.async_create_entry(
                title="Victoria Fire Danger",
                data={"districts": user_input["districts"]},
            )

        # Show the form with the multi-select dropdown
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "districts",
                        default=["All Districts"],
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=DISTRICT_OPTIONS,
                            multiple=True,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return VictoriaFireDangerOptionsFlow()


class VictoriaFireDangerOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Victoria Fire Danger."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            selected = user_input.get("districts", [])

            # Preserve existing "All Districts" behavior
            if "All Districts" in selected:
                selected = VICTORIA_DISTRICTS

            return self.async_create_entry(
                title="",
                data={"districts": selected},
            )

        # Default comes from options first, then original config
        current_districts = (
            self.config_entry.options.get("districts")
            or self.config_entry.data.get("districts", [])
        )

        # If all districts are selected, show "All Districts" in UI
        if set(current_districts) == set(VICTORIA_DISTRICTS):
            current_districts = ["All Districts"]

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "districts",
                        default=current_districts,
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=DISTRICT_OPTIONS,
                            multiple=True,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )
