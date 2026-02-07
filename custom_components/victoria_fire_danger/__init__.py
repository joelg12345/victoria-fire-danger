"""The Victoria Fire Danger Ratings integration."""
from __future__ import annotations
import os
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOVELACE_KEY = f"{DOMAIN}_lovelace_registered"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Victoria Fire Danger component."""
    # Register static path for custom card
    www_path = os.path.join(os.path.dirname(__file__), "www")
    await hass.http.async_register_static_paths([
        StaticPathConfig(
            url_path=f"/{DOMAIN}_ui",
            path=www_path,
            cache_headers=True,
        )
    ])

    # Register Lovelace resource ONCE per HA start
    if not hass.data.get(_LOVELACE_KEY):
        hass.data[_LOVELACE_KEY] = True

        async def register_card(event=None):
            """Register JS card after Home Assistant starts."""
            resource_url = f"/{DOMAIN}_ui/vic-fire-danger-card.js?v=1.1.1"
            if "lovelace" not in hass.data:
                return
            ll_data = hass.data["lovelace"]
            resources = getattr(ll_data, "resources", None) or ll_data.get("resources", None)
            if not resources:
                return
            if any(getattr(res, "url", None) == resource_url for res in resources.async_items()):
                return
            await resources.async_create_item({"res_type": "module", "url": resource_url})

        hass.bus.async_listen_once("homeassistant_start", register_card)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Victoria Fire Danger from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload integration when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
