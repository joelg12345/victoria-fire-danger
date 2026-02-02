"""The Victoria Fire Danger Ratings integration."""
from __future__ import annotations

import os

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .sensor import VictoriaFireDangerCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

# This tells Home Assistant that this integration is only configured via the UI
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Victoria Fire Danger component."""
    # 1. Register the virtual path for the card
    # This maps /victoria_fire_danger_ui/ to custom_components/victoria_fire_danger/www/
    www_path = os.path.join(os.path.dirname(__file__), "www")
    
    await hass.http.async_register_static_paths([
        StaticPathConfig(
            url_path=f"/{DOMAIN}_ui",
            path=www_path,
            cache_headers=True,
        )
    ])

    # 2. Automatically register the Lovelace resource
    hass.async_create_task(_async_register_lovelace_resource(hass))
    
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Victoria Fire Danger from a config entry."""
    coordinator = VictoriaFireDangerCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def _async_register_lovelace_resource(hass: HomeAssistant) -> None:
    """Register Lovelace resource for the custom card."""
    # Using v=1.0.4 to clear browser cache for the new location
    resource_url = f"/{DOMAIN}_ui/vic-fire-danger-card.js?v=1.0.7"
    
    if "lovelace" not in hass.data:
        return

    resources = hass.data["lovelace"].get("resources")
    if resources:
        # Check if already registered
        if any(res.get("url") == resource_url for res in resources.async_items()):
            return
            
        # Add the resource to the dashboard
        if hasattr(resources, "async_create_item"):
            await resources.async_create_item({
                "res_type": "module",
                "url": resource_url
            })

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
