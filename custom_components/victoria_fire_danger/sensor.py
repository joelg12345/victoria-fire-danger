"""Sensor platform for Victoria Fire Danger."""
import logging
import time
import xml.etree.ElementTree as ET
from datetime import timedelta, datetime

from bs4 import BeautifulSoup
import async_timeout
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CFA_FEED_URL, SCAN_INTERVAL_MINUTES, VICTORIA_DISTRICTS, RATING_ICONS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Victoria Fire Danger sensors from a config entry."""

    # 1. Check if coordinator already exists for this entry
    if not hass.data.get(DOMAIN):
        hass.data.setdefault(DOMAIN, {})

    if entry.entry_id not in hass.data[DOMAIN]:
        # Create the coordinator and store it
        coordinator = VictoriaFireDangerCoordinator(hass)
        await coordinator.async_config_entry_first_refresh()
        hass.data[DOMAIN][entry.entry_id] = coordinator
    else:
        coordinator = hass.data[DOMAIN][entry.entry_id]

    # 2. Get districts from options, fallback to initial config data
    districts = entry.options.get("districts", entry.data.get("districts", VICTORIA_DISTRICTS))
    entities = []

    # 3. Build sensors for the selected districts
    for district in districts:
        types = [
            "rating_today", "rating_tomorrow", "rating_day_3", "rating_day_4",
            "total_fire_ban_today", "total_fire_ban_tomorrow", "total_fire_ban_day_3", "total_fire_ban_day_4"
        ]
        for s_type in types:
            entities.append(VicFireSensor(coordinator, district, s_type))

    # 4. Add sensors to HA
    async_add_entities(entities, True)



class VicFireSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Victoria Fire Danger sensor."""

    def __init__(self, coordinator, district, sensor_type):
        super().__init__(coordinator)
        self._district = district
        self._type = sensor_type

        # Let HA assign the entity_id automatically
        self._attr_name = f"{district} {sensor_type.replace('_', ' ').title()}"
        self._attr_unique_id = f"{DOMAIN}_{district.lower().replace(' ', '_')}_{sensor_type}"

    @property
    def icon(self):
        """Return the icon to use in the frontend based on the state."""
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
        return self.coordinator.data.get(self._district, {}).get(f"{prefix}{day_idx}", "No" if "ban" in prefix else "NO RATING")

    @property
    def extra_state_attributes(self):
        return {
            "area_name": self._district,
            "last_updated": self.coordinator.last_update_time.isoformat() if self.coordinator.last_update_time else None
        }


class VictoriaFireDangerCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch Victoria Fire Danger data periodically."""

    def __init__(self, hass):
        super().__init__(
            hass,
            _LOGGER,
            name="Victoria Fire Danger",
            update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES)
        )
        self.last_update_time = None

    async def _async_update_data(self):
        """Fetch and parse CFA data efficiently."""
        start_time = time.perf_counter()

        try:
            session = async_get_clientsession(self.hass)
            async with async_timeout.timeout(15):
                async with session.get(CFA_FEED_URL) as resp:
                    text = await resp.text()

            root = ET.fromstring(text)
            items = root.findall(".//item")
            data = {d: {} for d in VICTORIA_DISTRICTS}
            today = dt_util.now().date()

            for item in items:
                title_str = item.find("title").text
                try:
                    date_part = title_str.split(",")[-1].strip()
                    item_date = datetime.strptime(date_part, "%d %B %Y").date()
                    diff = (item_date - today).days
                    if diff < 0 or diff > 3:
                        continue
                    day_key = str(diff)
                except Exception:
                    continue

                desc_html = item.find("description").text
                soup = BeautifulSoup(desc_html, "html.parser")
                full_text = soup.get_text(separator="\n")

                # Split ban vs rating sections
                parts = full_text.split("Fire Danger Ratings")
                ban_text = parts[0]
                rate_text = parts[1] if len(parts) > 1 else ""

                for d in VICTORIA_DISTRICTS:
                    search_name = "West and South Gippsland" if d == "West Gippsland" else d

                    # Parse Total Fire Ban
                    data[d][f"ban_{day_key}"] = "No"
                    for line in ban_text.split("\n"):
                        if search_name.lower() in line.lower() and "YES" in line.upper():
                            data[d][f"ban_{day_key}"] = "Yes"
                            break

                    # Parse Fire Danger Ratings
                    data[d][f"rate_{day_key}"] = "NO RATING"
                    for line in rate_text.split("\n"):
                        if search_name.lower() in line.lower() and ":" in line:
                            val = line.split(":")[-1].strip().upper().split("-")[0].strip()
                            data[d][f"rate_{day_key}"] = val
                            break

            elapsed = (time.perf_counter() - start_time) * 1000
            _LOGGER.debug("CFA Update parsed %s districts in %.2fms", len(VICTORIA_DISTRICTS), elapsed)

            self.last_update_time = dt_util.now()
            return data

        except Exception as err:
            raise UpdateFailed(f"CFA Error: {err}")
