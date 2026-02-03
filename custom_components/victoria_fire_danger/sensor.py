"""Sensor platform for Victoria Fire Danger - Synced with NSW Logic."""
import logging
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
    coordinator = hass.data[DOMAIN][entry.entry_id]
    districts = entry.data.get("districts", VICTORIA_DISTRICTS)
    entities = []
    for district in districts:
        # These suffixes are now perfectly aligned with the NSW JS card logic
        types = [
            "rating_today", "rating_tomorrow", "rating_day_3", "rating_day_4",
            "total_fire_ban_today", "total_fire_ban_tomorrow", "total_fire_ban_day_3", "total_fire_ban_day_4"
        ]
        for s_type in types:
            entities.append(VicFireSensor(coordinator, district, s_type))
    async_add_entities(entities)

class VicFireSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, district, sensor_type):
        super().__init__(coordinator)
        self._district = district
        self._type = sensor_type
        slug = district.lower().replace(" ", "_")
        self.entity_id = f"sensor.{slug}_{sensor_type}"
        self._attr_name = f"{district} {sensor_type.replace('_', ' ').title()}"
        self._attr_unique_id = f"{DOMAIN}_{slug}_{sensor_type}"

    @property
    def icon(self):
        """Return the icon to use in the frontend based on the state."""
        state_val = str(self.state).upper()
        
        # Logic for Total Fire Ban sensors
        if "total_fire_ban" in self._type:
            return "mdi:fire-alert" if state_val == "YES" else "mdi:fire-off"
        
        # Logic for Fire Danger Rating sensors using RATING_ICONS from const.py
        return RATING_ICONS.get(state_val, "mdi:shield-check")

    @property
    def state(self):
        if not self.coordinator.data: return "UNKNOWN"
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
    def __init__(self, hass):
        super().__init__(hass, _LOGGER, name="Victoria Fire Danger", update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES))
        self.last_update_time = None

    async def _async_update_data(self):
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
                    if diff < 0 or diff > 3: continue
                    day_key = str(diff)
                except: continue

                desc = item.find("description").text
                parts = desc.split("Fire Danger Ratings")
                ban_section = parts[0]
                rate_section = parts[1] if len(parts) > 1 else ""

                for d in VICTORIA_DISTRICTS:
                    search_name = "West and South Gippsland" if d == "West Gippsland" else d
                    
                    # Ban Parsing (Improved for "YES" anywhere in line)
                    ban_soup = BeautifulSoup(ban_section, "html.parser")
                    data[d][f"ban_{day_key}"] = "No"
                    for line in ban_soup.get_text(separator="\n").split("\n"):
                        if search_name.lower() in line.lower() and "YES" in line.upper():
                            data[d][f"ban_{day_key}"] = "Yes"

                    # Rating Parsing
                    rate_soup = BeautifulSoup(rate_section, "html.parser")
                    data[d][f"rate_{day_key}"] = "NO RATING"
                    for line in rate_soup.get_text(separator="\n").split("\n"):
                        if search_name.lower() in line.lower() and ":" in line:
                            val = line.split(":")[-1].strip().upper().split("-")[0].strip()
                            data[d][f"rate_{day_key}"] = val
            
            self.last_update_time = dt_util.now()
            return data
        except Exception as err:
            raise UpdateFailed(f"CFA Error: {err}")
