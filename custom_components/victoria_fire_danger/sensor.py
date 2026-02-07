"""Sensor platform for Victoria Fire Danger."""
import logging
import time
import xml.etree.ElementTree as ET
from datetime import timedelta, datetime

from bs4 import BeautifulSoup
import async_timeout
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CFA_FEED_URL,
    SCAN_INTERVAL_MINUTES,
    VICTORIA_DISTRICTS,
    RATING_ICONS,
)

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = [
    "rating_today",
    "rating_tomorrow",
    "rating_day_3",
    "rating_day_4",
    "total_fire_ban_today",
    "total_fire_ban_tomorrow",
    "total_fire_ban_day_3",
    "total_fire_ban_day_4",
]


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Victoria Fire Danger sensors from a config entry."""
    selected_districts = entry.options.get(
        "districts", entry.data.get("districts", VICTORIA_DISTRICTS)
    )

    coordinator = VictoriaFireDangerCoordinator(hass, selected_districts)
    await coordinator.async_config_entry_first_refresh()

    _LOGGER.debug("Setting up Victoria Fire Danger sensors. Districts: %s", selected_districts)

    ent_reg = async_get_entity_registry(hass)
    valid_unique_ids: set[str] = set()
    entities = []

    for district in selected_districts:
        for sensor_type in SENSOR_TYPES:
            unique_id = f"{DOMAIN}_{district.lower().replace(' ', '_')}_{sensor_type}"
            valid_unique_ids.add(unique_id)

            entities.append(
                VicFireSensor(
                    coordinator=coordinator,
                    district=district,
                    sensor_type=sensor_type,
                    entry_id=entry.entry_id,
                )
            )

    # Remove stale entities safely
    for entity_entry in list(ent_reg.entities.values()):
        if (
            entity_entry.platform == DOMAIN
            and entity_entry.config_entry_id == entry.entry_id
            and entity_entry.unique_id not in valid_unique_ids
        ):
            _LOGGER.info("Removing stale Victoria Fire Danger entity: %s", entity_entry.entity_id)
            ent_reg.async_remove(entity_entry.entity_id)

    async_add_entities(entities)


class VicFireSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Victoria Fire Danger sensor."""

    def __init__(self, coordinator, district, sensor_type, entry_id):
        super().__init__(coordinator)
        self._district = district
        self._type = sensor_type

        self._attr_name = f"{district} {sensor_type.replace('_', ' ').title()}"
        self._attr_unique_id = f"{DOMAIN}_{district.lower().replace(' ', '_')}_{sensor_type}"
        self._attr_has_entity_name = True
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Victoria Fire Danger",
            "manufacturer": "CFA Victoria",
        }

    @property
    def icon(self):
        state_val = str(self.state).upper()
        if "total_fire_ban" in self._type:
            return "mdi:fire-alert" if state_val == "YES" else "mdi:fire-off"
        return RATING_ICONS.get(state_val, "mdi:shield-check")

    @property
    def state(self):
        if not self.coordinator.data:
            return "UNKNOWN"
        day_map = {"today": "0", "tomorrow": "1", "day_3": "2", "day_4": "3"}
        day_idx = next((v for k, v in day_map.items() if k in self._type), "0")
        prefix = "ban_" if "total_fire_ban" in self._type else "rate_"
        return self.coordinator.data.get(self._district, {}).get(
            f"{prefix}{day_idx}", "No" if prefix == "ban_" else "NO RATING"
        )

    @property
    def extra_state_attributes(self):
        """
        ⚠️ DO NOT RENAME `area_name`
        This attribute is REQUIRED by vic-fire-danger-card.js
        """
        return {
            "area_name": self._district,  # <-- REQUIRED BY CARD
            "district": self._district,
            "sensor_type": self._type,
            "last_updated": (
                self.coordinator.last_update_time.isoformat()
                if self.coordinator.last_update_time
                else None
            ),
        }


class VictoriaFireDangerCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch Victoria Fire Danger data periodically."""

    def __init__(self, hass, districts):
        super().__init__(
            hass,
            _LOGGER,
            name="Victoria Fire Danger",
            update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES),
        )
        self.districts = districts
        self.last_update_time = None

    async def _async_update_data(self):
        start = time.perf_counter()
        try:
            session = async_get_clientsession(self.hass)
            async with async_timeout.timeout(15):
                async with session.get(CFA_FEED_URL) as resp:
                    text = await resp.text()

            root = ET.fromstring(text)
            items = root.findall(".//item")
            data = {d: {} for d in self.districts}
            today = dt_util.now().date()

            for item in items:
                title = item.find("title").text
                try:
                    date_part = title.split(",")[-1].strip()
                    item_date = datetime.strptime(date_part, "%d %B %Y").date()
                    diff = (item_date - today).days
                    if diff < 0 or diff > 3:
                        continue
                except Exception:
                    continue

                soup = BeautifulSoup(item.find("description").text, "html.parser")
                text = soup.get_text(separator="\n")
                ban_text, *rate_parts = text.split("Fire Danger Ratings")
                rate_text = rate_parts[0] if rate_parts else ""

                for district in self.districts:
                    search = "West and South Gippsland" if district == "West Gippsland" else district

                    data[district][f"ban_{diff}"] = (
                        "Yes" if any(search.lower() in l.lower() and "YES" in l.upper() for l in ban_text.splitlines())
                        else "No"
                    )

                    data[district][f"rate_{diff}"] = "NO RATING"
                    for line in rate_text.splitlines():
                        if search.lower() in line.lower() and ":" in line:
                            data[district][f"rate_{diff}"] = line.split(":")[-1].strip().upper().split("-")[0]
                            break

            self.last_update_time = dt_util.now()
            _LOGGER.debug("CFA update completed in %.2f ms", (time.perf_counter() - start) * 1000)
            return data

        except Exception as err:
            raise UpdateFailed(f"CFA Error: {err}")
