# 🔥 Victoria Fire Danger Ratings for Home Assistant

[![GitHub Stars](https://img.shields.io/github/stars/joelg12345/victoria-fire-danger?style=social)](https://github.com/joelg12345/victoria-fire-danger)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/joelg12345/victoria-fire-danger.svg)](https://github.com/joelg12345/victoria-fire-danger/releases)
[![License](https://img.shields.io/github/license/joelg12345/victoria-fire-danger.svg)](LICENSE)

A custom Home Assistant integration and custom frontend card that fetches official fire danger ratings and total fire ban data directly from the Victoria CFA. Features a specialized "roadside-style" gauge card matching the official Australian Fire Danger Rating (AFDRS) signage!

![Victoria Fire Danger Card](https://raw.githubusercontent.com/joelg12345/victoria-fire-danger/main/card-preview.png)

---

## ✨ Features

- 🎨 **Beautiful Custom Card**: A high-visibility Lovelace card matching official CFA roadside signage.
- 🎯 **Dynamic Needle**: The gauge needle moves automatically to match the rating (MODERATE → HIGH → EXTREME → CATASTROPHIC).
- 🚫 **Total Fire Ban Alerts**: Displays prominent warnings when a ban is declared for your district.
- 📅 **4-Day Forecast**: Dedicated sensors for Today, Tomorrow, Day 3, and Day 4.
- 🌏 **All 9 Victorian Districts**: Full support for all CFA fire weather areas.
- ⚙️ **Easy Configuration**: User-friendly dropdown UI for district selection.
- 🔄 **Auto-Updates**: Data polled from CFA every 30 minutes.

---

## 🚀 Quick Start Guide

### 1. Installation

#### HACS (Recommended)
1. Open **HACS** in Home Assistant.
2. Go to **Integrations**.
3. Click the three dots (top right) → **Custom repositories**.
4. Add `https://github.com/joelg12345/victoria-fire-danger` as an **Integration**.
5. Search for "**Victoria Fire Danger Ratings**" and click **Download**.
6. **🛑 IMPORTANT: Restart Home Assistant required after installation.**

#### Manual Installation
1. Download the latest release.
2. Extract the `victoria_fire_danger` folder to your `/config/custom_components/` directory.
3. **🛑 IMPORTANT: Restart Home Assistant required after installation.**

### 2. Configuration

1. After restarting, go to **Settings** → **Devices & Services**.
2. Click **+ Add Integration**.
3. Search for "**Victoria Fire Danger Ratings**".
4. Select your **Fire District** from the dropdown.
5. Click **Submit**.

### 3. Setup Custom Card

**The custom card is automatically registered for you!** Once the integration is configured, you can add the card to your dashboard immediately. No manual resource management is required.

---

## 🎨 Using the Custom Card

Add a **Manual** card to your dashboard and use the following YAML:

```yaml
type: custom:vic-fire-danger-card
entity: sensor.central_fire_danger_rating
```

---

## 📊 Monitored Districts

The integration supports all 9 Victorian fire districts:

| District | Sensor Prefix (Example) |
| :--- | :--- |
| **Central** | `sensor.central_` |
| **North Central** | `sensor.north_central_` |
| **Northern Country** | `sensor.northern_country_` |
| **North East** | `sensor.north_east_` |
| **East Gippsland** | `sensor.east_gippsland_` |
| **West Gippsland** | `sensor.west_gippsland_` |
| **Wimmera** | `sensor.wimmera_` |
| **South West** | `sensor.south_west_` |
| **Mallee** | `sensor.mallee_` |

---

## 🔔 Automation Example

Get a notification on your phone when fire danger reaches EXTREME:

```yaml
automation:
  - alias: "Fire Danger EXTREME Alert"
    trigger:
      - platform: state
        entity_id: sensor.central_fire_danger_rating
        to: "EXTREME"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ EXTREME Fire Danger"
          message: "Fire danger is EXTREME for the Central District. Take action now!"
```

---

## 🛠️ Troubleshooting

### Card Not Appearing?
1. The integration registers the card at `victoria_fire_danger_ui/vic-fire-danger-card.js`.
2. Perform a **hard refresh** in your browser (**Ctrl+Shift+R** or **Cmd+Shift+R**).
3. Check **Settings** → **Dashboards** → **Resources** to ensure the entry exists.

---

## 📜 Credits & Attribution

* **Original Logic:** This integration is based on and inspired by the NSW RFS work of [@vwylaw](https://github.com/vwylaw).
* **Data Sourced From:** [Country Fire Authority (CFA) Victoria](https://www.cfa.vic.gov.au/).
* **License:** MIT License.

> **Disclaimer:** This integration is not affiliated with, or endorsed by, the CFA. Always refer to official sources and the VicEmergency app for life-safety information.
