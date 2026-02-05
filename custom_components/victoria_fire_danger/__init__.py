"""The Victoria Fire Danger Ratings integration."""
from __future__ import annotations

import os
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Victoria Fire Danger component."""

    # 1. Register the virtual path for the custom card
    www_path = os.path.join(os.path.dirname(__file__), "www")
    await hass.http.async_register_static_paths([
        StaticPathConfig(
            url_path=f"/{DOMAIN}_ui",
            path=www_path,
            cache_headers=True,
        )
    ])

    # 2. Automatically register the Lovelace resource (silent if Lovelace not ready)
    hass.async_create_task(_async_register_lovelace_resource(hass))

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Victoria Fire Danger from a config entry."""

    # Just forward the platform setup (coordinator is created in sensor.py)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_register_lovelace_resource(hass: HomeAssistant) -> None:
    """Register Lovelace resource for the custom card."""

    resource_url = f"/{DOMAIN}_ui/vic-fire-danger-card.js?v=1.0.7"

    if "lovelace" not in hass.data:
        # Lovelace not initialized yet; skip silently
        return

    resources = hass.data["lovelace"].get("resources")
    if resources:
        # Skip if already registered
        if any(res.get("url") == resource_url for res in resources.async_items()):
            return

        if hasattr(resources, "async_create_item"):
            await resources.async_create_item({
                "res_type": "module",
                "url": resource_url
            })


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
