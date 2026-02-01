# Victoria Fire Danger Ratings for Home Assistant

An unofficial Home Assistant integration and custom frontend card that fetches official fire danger ratings and total fire ban data directly from the Victoria CFA RSS feeds. 

This package provides high-accuracy sensors for all 9 Victorian districts and a specialized "roadside-style" gauge card for your dashboard.

## Features
- **Real-time Data:** Polled from CFA every 30 minutes.
- **4-Day Forecast:** Dedicated sensors for Today, Tomorrow, Day 3, and Day 4.
- **District Support:** Monitor any or all fire districts in Victoria.
- **Custom Gauge Card:** A high-visibility Lovelace card matching the official Australian Fire Danger Rating (AFDRS) signage.
- **Dynamic Icons:** Theme-aware icons that change based on the severity of the rating.

---

## Monitored Districts
The integration provides data for the following CFA districts:

| District | Sensor Prefix |
| :--- | :--- |
| Central | `sensor.central_` |
| North Central | `sensor.north_central_` |
| Northern Country | `sensor.northern_country_` |
| North East | `sensor.north_east_` |
| East Gippsland | `sensor.east_gippsland_` |
| West Gippsland | `sensor.west_gippsland_` |
| Wimmera | `sensor.wimmera_` |
| South West | `sensor.south_west_` |
| Mallee | `sensor.mallee_` |

---

## Installation

### 1. Integration (The Sensors)
1. Copy the `custom_components/victoria_fire_danger` folder into your Home Assistant `custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings > Devices & Services > Add Integration**.
4. Search for **Victoria Fire Danger Ratings** and follow the prompts.

### 2. Frontend (The Card)
1. Download `vic-fire-danger-card.js` from the `dist/` folder of this repository.
2. Upload the file to your Home Assistant `www/` folder.
3. Add the resource to your Dashboard:
   - Go to **Settings > Dashboards**.
   - Click the **three dots** (top right) > **Resources**.
   - Click **Add Resource**.
   - Enter `/local/vic-fire-danger-card.js` and select **JavaScript Module**.

---

## Dashboard Usage

Add a **Manual** card to your dashboard and use the following configuration:

```yaml
type: custom:vic-fire-danger-card
entity: sensor.central_rating_today

### Card Behavior
* **Dynamic Needle:** The needle moves automatically to match the rating (**MODERATE**, **HIGH**, **EXTREME**, **CATASTROPHIC**).
* **Fire Ban Alerts:** Displays a prominent "Total Fire Ban" warning icon and text when a ban is declared.
* **Forecast Grid:** View the next three days of ratings at a glance at the bottom of the card.
* **No Rating Mode:** During the off-season, the card displays a clean white "No Rating" state that remains high-contrast in both Light and Dark modes.

---

### Credits & Attribution
* **Original Logic:** This integration is based on and inspired by the work of [@vwylaw](https://github.com/vwylaw).
* **Data Sourced From:** [Country Fire Authority (CFA) Victoria](https://www.cfa.vic.gov.au/).
* **Design:** Modernized Australian Fire Danger Rating (AFDRS) gauge card.

> [!IMPORTANT]
> **Disclaimer:** This integration is not affiliated with, or endorsed by, the CFA. Always refer to official sources for life-safety information.
