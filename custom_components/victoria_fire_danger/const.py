"""Constants for Victoria Fire Danger."""
DOMAIN = "victoria_fire_danger"
CFA_FEED_URL = "https://www.cfa.vic.gov.au/cfa/rssfeed/tfbfdrforecast_rss.xml"
SCAN_INTERVAL_MINUTES = 30

VICTORIA_DISTRICTS = [
    "Central",
    "North Central",
    "Northern Country",
    "North East",
    "East Gippsland",
    "West Gippsland",
    "Wimmera",
    "South West",
    "Mallee"
]

RATING_ICONS = {
    "NO RATING": "mdi:shield-check",
    "MODERATE": "mdi:fire",
    "HIGH": "mdi:fire-alert",
    "EXTREME": "mdi:fire-truck",
    "CATASTROPHIC": "mdi:skull-crossbones",
}

