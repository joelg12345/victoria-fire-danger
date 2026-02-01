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
        # 1. Prevent multiple instances of the integration
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            # 2. Process the "All Districts" selection
            selected = user_input.get("districts", ["All Districts"])
            if "All Districts" in selected:
                user_input["districts"] = VICTORIA_DISTRICTS
            
            return self.async_create_entry(
                title="Victoria Fire Danger", 
                data={"districts": user_input["districts"]}
            )

        # 3. Show the form with the multi-select dropdown
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
